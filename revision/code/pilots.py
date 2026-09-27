"""Bounded one-origin pilots on training-only validation data.

These are feasibility/correctness runs, not the revised research comparison.
Each model runs in a separate process with time/RSS guards.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import warnings
import numpy as np
import pandas as pd
import psutil
from .protocol import (ROOT, REVISION, configuration, load_calendar, split_position,
    origin_inputs, fit_input_scaler, transform_inputs, prophet_frame, extract_raw_forecast, neural_training_segments, advance_sarimax_state)

DIRECTORY = REVISION / "artifacts/phase1/pilots"


def run_model(name, epochs, iterations):
    start = time.perf_counter()
    cfg = configuration()
    _, grid = load_calendar()
    position = split_position(grid)-cfg["validation_windows"]*cfg["horizon_hours"]
    history, future_x = origin_inputs(grid, position)
    features = cfg["selected_features"]
    scaler, _ = fit_input_scaler(history, features)
    scaled = transform_inputs(history, features, scaler)
    future_x = transform_inputs(future_x, features, scaler)
    record = {"model": name, "status": "running", "pilot_only": True,
              "forecast_origin": str(future_x.index[0]), "history_calendar_hours": len(history),
              "history_observed_targets": int(history.pm2_5.notna().sum()), "forecast_hours": len(future_x),
              "future_target_supplied": False, "device": "cpu", "cpu_threads": 2,
              "fit_target_imputation": False, "history_target_gaps": int(history.pm2_5.isna().sum()),
              "validation_origin_entirely_inside_training": True,
              "python": sys.version.split()[0], "package_version": importlib.metadata.version(name)}
    phase = time.perf_counter()
    if name == "prophet":
        from prophet import Prophet
        record["import_seconds"] = time.perf_counter()-phase
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True,
                        seasonality_mode="additive", uncertainty_samples=0)
        for feature in features:
            model.add_regressor(feature, standardize=False)
        frame = prophet_frame(scaled).dropna()
        phase = time.perf_counter()
        model.fit(frame, seed=42)
        record["fit_seconds"] = time.perf_counter()-phase
        phase = time.perf_counter()
        forecast = model.predict(future_x.reset_index().rename(columns={"datetime":"ds"}))
        values = forecast.yhat.to_numpy()
        assert pd.DatetimeIndex(forecast.ds).equals(future_x.index)
        record["prediction_seconds"] = time.perf_counter()-phase
        record["observed_training_rows_used"] = len(frame)
        record["configuration"] = "additive; default changepoints; daily/weekly/yearly; externally scaled regressors"
    elif name == "statsmodels":
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        record["import_seconds"] = time.perf_counter()-phase
        model = SARIMAX(scaled.pm2_5, exog=scaled[features].ffill(), order=(1,1,1),
                        seasonal_order=(1,1,1,24), enforce_stationarity=False, enforce_invertibility=False)
        iteration_times = []
        phase = time.perf_counter()
        fit = model.fit(disp=False, maxiter=iterations, low_memory=True, cov_type="none",
                        callback=lambda _: iteration_times.append(time.perf_counter()-phase))
        record["fit_seconds"] = time.perf_counter()-phase
        record["optimizer_iterations_requested"] = iterations
        record["optimizer_iterations_completed"] = int(fit.mle_retvals.get("iterations",0))
        record["converged"] = bool(fit.mle_retvals.get("converged",False))
        record["iteration_elapsed_seconds"] = iteration_times
        phase = time.perf_counter()
        forecast = fit.forecast(steps=168, exog=future_x[features])
        values = forecast.to_numpy()
        assert forecast.index.equals(future_x.index)
        record["prediction_seconds"] = time.perf_counter()-phase
        # Refresh through one observed validation week without re-estimation.
        observed_week = transform_inputs(grid.iloc[position:position+168][["pm2_5"]+features], features, scaler)
        state_start = time.perf_counter()
        refreshed = advance_sarimax_state(fit, observed_week.pm2_5, observed_week[features])
        np.testing.assert_array_equal(fit.params, refreshed.params)
        record["state_update_seconds"] = time.perf_counter()-state_start
        record["fixed_parameters_state_update_passed"] = True
        record["low_memory"] = True
        record["configuration"] = "(1,1,1)x(1,1,1,24); low-memory filtering; no covariance estimation in feasibility pilot"
    else:
        import torch
        from neuralprophet import NeuralProphet, set_random_seed, set_log_level
        from .model_checks import np_future, np_predict
        record["import_seconds"] = time.perf_counter()-phase
        torch.set_num_threads(2)
        record["torch_threads"] = torch.get_num_threads()
        record["cuda_available"] = torch.cuda.is_available()
        record["torch_built_cuda_version"] = torch.version.cuda
        set_log_level("ERROR")
        set_random_seed(42)
        model = NeuralProphet(n_lags=168, n_forecasts=168, epochs=epochs, batch_size=128,
            learning_rate=.001, yearly_seasonality=True, weekly_seasonality=True,
            daily_seasonality=True, impute_missing=False, drop_missing=True,
            global_normalization=True, global_time_normalization=True,
            accelerator="cpu", trainer_config={"default_root_dir": str(DIRECTORY / "neural_training"),
                "enable_model_summary": False})
        for feature in features:
            model.add_future_regressor(feature, normalize="off")
        segmented, segment_records = neural_training_segments(scaled, features)
        (DIRECTORY / "neural_training_segments.json").write_text(json.dumps(segment_records, indent=2))
        phase = time.perf_counter()
        trace = model.fit(segmented, freq="h", progress=None, num_workers=0, checkpointing=False)
        record["fit_seconds"] = time.perf_counter()-phase
        trace.to_csv(DIRECTORY / "neural_training_trace.csv", index=False)
        record["epochs_completed"] = len(trace)
        record["finite_training_loss"] = bool(np.isfinite(trace["Loss"]).all())
        assert record["finite_training_loss"]
        frame = prophet_frame(scaled.iloc[-168:])
        # All parameters/target/time normalization are global. Use an existing
        # bookkeeping ID for inference; episode labels do not select local models.
        frame["ID"] = segmented.ID.iloc[0]
        future_df = future_x.reset_index().rename(columns={"datetime":"ds"})
        phase = time.perf_counter()
        future = np_future(model, frame, future_df)
        raw = np_predict(model, future, raw=True)
        values = extract_raw_forecast(raw, future_x.index[0], 168).to_numpy()
        record["prediction_seconds"] = time.perf_counter()-phase
        record["fit_target_imputation_disabled_after_prediction"] = not model.config_missing.impute_missing
        record["configuration"] = f"168 lags/168 leads; future regressors; {epochs} feasibility epochs; no training imputation"
        record["training_episodes"] = len([s for s in segment_records if s["retained"]])
        record["complete_training_samples"] = sum(s["training_samples"] for s in segment_records)
        record["30_epoch_fit_seconds_linear_projection"] = record["fit_seconds"]*30/max(len(trace),1)
        record["50_epoch_fit_seconds_linear_projection"] = record["fit_seconds"]*50/max(len(trace),1)
        record["projection_caveat"] = "Short-pilot extrapolation includes preparation overhead; full-run timing may differ"
    assert len(values)==168 and np.isfinite(values).all()
    record["all_168_predictions_finite"] = True
    record["forecast_timestamps_match_calendar"] = True
    pd.DataFrame({"forecast_origin":future_x.index[0], "target_timestamp":future_x.index,
                  "lead_hour":np.arange(1,169), "base_prediction":values}).to_csv(DIRECTORY / f"{name}_pilot_forecasts.csv",index=False)
    record["elapsed_seconds_excluding_launcher_imports"] = time.perf_counter()-start
    record["peak_rss_mib_self"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    record["status"] = "passed_feasibility_and_alignment"
    (DIRECTORY / f"{name}_pilot.json").write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))


def supervise(names, epochs, iterations):
    DIRECTORY.mkdir(parents=True,exist_ok=True)
    previous=DIRECTORY / "launcher_results.json"
    summaries=json.loads(previous.read_text()) if previous.exists() else []
    for name in names:
        available = psutil.virtual_memory().available
        limit = min(6*1024**3, max(1024**3, int(available*.75)))
        command=[sys.executable,"-u","-m","revision.code.pilots","--child",name,
                 "--epochs",str(epochs),"--iterations",str(iterations)]
        environment=os.environ.copy()
        for key in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","TF_NUM_INTRAOP_THREADS","TF_NUM_INTEROP_THREADS"]:
            environment[key]="2"
        environment.update(MPLCONFIGDIR="/tmp/weather-revision-matplotlib", CUDA_VISIBLE_DEVICES="",TF_CPP_MIN_LOG_LEVEL="3")
        start=time.perf_counter();peak=0;reason=None
        print(f"Starting {name}: time guard 900 s; process-group RSS guard {limit/1024**3:.2f} GiB",flush=True)
        with (DIRECTORY / f"{name}.log").open("w") as output:
            proc=subprocess.Popen(command,cwd=ROOT,env=environment,stdout=output,stderr=subprocess.STDOUT)
            while proc.poll() is None:
                try:
                    root=psutil.Process(proc.pid)
                    rss=sum(p.memory_info().rss for p in [root]+root.children(recursive=True) if p.is_running())
                    peak=max(peak,rss)
                    if rss>limit:reason="process_group_memory_guard"
                    elif time.perf_counter()-start>900:reason="900_second_time_guard"
                    if reason:
                        for child in root.children(recursive=True):
                            child.terminate()
                        proc.terminate()
                        try:proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:proc.kill()
                except psutil.NoSuchProcess:
                    pass
                time.sleep(.5)
            proc.wait()
        summary={"model":name,"returncode":proc.returncode,"elapsed_seconds_including_imports":time.perf_counter()-start,
                 "process_group_peak_rss_mib_sampled":peak/1024**2,"memory_guard_mib":limit/1024**2,
                 "guard_reason":reason,"memory_sampling_seconds":.5}
        summaries.append(summary)
        (DIRECTORY / "launcher_results.json").write_text(json.dumps(summaries,indent=2))
        print(json.dumps(summary),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--child",choices=["prophet","statsmodels","neuralprophet"])
    parser.add_argument("--models",nargs="+",default=["prophet","statsmodels","neuralprophet"],choices=["prophet","statsmodels","neuralprophet"])
    parser.add_argument("--epochs",type=int,default=2)
    parser.add_argument("--iterations",type=int,default=10)
    args=parser.parse_args()
    DIRECTORY.mkdir(parents=True,exist_ok=True)
    warnings.filterwarnings("ignore",category=FutureWarning)
    warnings.filterwarnings("ignore",message="Protobuf gencode version.*")
    if args.child:
        try:run_model(args.child,args.epochs,args.iterations)
        except Exception:
            (DIRECTORY / f"{args.child}_failure.txt").write_text(traceback.format_exc())
            raise
    else:supervise(args.models,args.epochs,args.iterations)


if __name__=="__main__":
    main()
