"""Revision forecasters for the same three families in the submitted study.

Forecast routines never accept future PM2.5. Fitted instances live only within
one isolated process; numeric predictions and diagnostics are checkpointed.
"""
from dataclasses import dataclass
import json
import time
import warnings
import numpy as np
import pandas as pd
from .protocol import (REVISION, configuration, origin_inputs, fit_input_scaler,
    transform_inputs, prophet_frame, neural_training_segments,
    extract_raw_forecast, advance_sarimax_state)
from .model_checks import np_future, np_predict


@dataclass
class Fitted:
    family: str
    model: object
    features: list
    scaler: object
    bounds: object
    fit_end: int
    metadata: dict
    first_episode_id: str | None = None


def _config_label(family, candidate):
    if family == "sarimax":
        return {"order": tuple(candidate["order"]), "seasonal_order": tuple(candidate["seasonal_order"])}
    if family == "prophet":
        return {"seasonality_mode": candidate["seasonality_mode"]}
    return {"epochs": int(candidate["epochs"]), "n_lags": 168, "n_forecasts": 168}


def fit_model(grid, position, family, candidate, features, clip_inputs, seed, run_dir):
    cfg = configuration()
    start = time.perf_counter()
    raw_history = grid.iloc[:position][[cfg["target"]] + features].copy()
    scaler, bounds = fit_input_scaler(raw_history, features, clip=clip_inputs)
    history = transform_inputs(raw_history, features, scaler, bounds)
    prep_seconds = time.perf_counter()-start
    meta = {"family": family, "candidate": _config_label(family, candidate),
            "features": features, "clip_inputs": clip_inputs, "seed": seed,
            "fit_end_exclusive": str(grid.index[position]), "training_calendar_hours": len(history),
            "observed_training_targets": int(history[cfg["target"]].notna().sum()),
            "preparation_seconds": prep_seconds, "scaler": None if scaler is None else {
                "mean": {f: float(v) for f, v in zip(features, scaler.mean_)},
                "scale": {f: float(v) for f, v in zip(features, scaler.scale_)}},
            "input_clip_bounds": None if bounds is None else {
                "lower": bounds[0].to_dict(), "upper": bounds[1].to_dict()},
            "target_clipped": False, "target_imputed": False, "device": "cpu", "cpu_threads": cfg["cpu_threads"]}
    first_episode_id = None
    begin = time.perf_counter()
    if family == "prophet":
        from prophet import Prophet
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True,
                        daily_seasonality=True, seasonality_mode=candidate["seasonality_mode"],
                        uncertainty_samples=0)
        for feature in features:
            # Input standardization is explicit and train-only above.
            model.add_regressor(feature, standardize=False)
        frame = prophet_frame(history).dropna(subset=["y"] + features)
        model.fit(frame, seed=seed)
        meta["observed_training_rows_used"] = len(frame)
        if features:
            from prophet.utilities import regressor_coefficients
            meta["prophet_regressor_coefficients"] = regressor_coefficients(model).to_dict("records")
    elif family == "sarimax":
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        exog = history[features].ffill() if features else None
        if exog is not None and exog.isna().any().any():
            raise ValueError("SARIMAX historical exogenous inputs cannot start missing")
        model = SARIMAX(history[cfg["target"]], exog=exog,
                        order=tuple(candidate["order"]), seasonal_order=tuple(candidate["seasonal_order"]),
                        enforce_stationarity=False, enforce_invertibility=False)
        policy = cfg["sarimax_optimizer_policy"]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fitted = model.fit(disp=False, maxiter=policy["initial_maxiter"],
                               low_memory=True, cov_type="none")
            first_iterations = int(fitted.mle_retvals.get("iterations", 0))
            retried = not bool(fitted.mle_retvals.get("converged", False))
            if retried:
                fitted = model.fit(start_params=fitted.params, disp=False,
                                   maxiter=policy["retry_additional_maxiter"],
                                   low_memory=True, cov_type="none")
        meta["optimizer"] = {"initial_iterations": first_iterations,
                             "retry_performed": retried,
                             "last_iterations": int(fitted.mle_retvals.get("iterations", 0)),
                             "converged": bool(fitted.mle_retvals.get("converged", False)),
                             "warnings": [str(w.message) for w in caught[-6:]]}
        meta["parameter_estimates"] = {str(k): float(v) for k,v in zip(fitted.param_names, fitted.params)}
        model = fitted
    elif family == "neuralprophet":
        import torch
        from neuralprophet import NeuralProphet, set_random_seed, set_log_level
        torch.set_num_threads(cfg["cpu_threads"])
        set_log_level("ERROR")
        set_random_seed(seed)
        model = NeuralProphet(n_lags=168, n_forecasts=168, epochs=candidate["epochs"],
                 batch_size=128, learning_rate=.001, yearly_seasonality=True,
                 weekly_seasonality=True, daily_seasonality=True,
                 impute_missing=False, drop_missing=True,
                 global_normalization=True, global_time_normalization=True,
                 accelerator="cpu", trainer_config={"default_root_dir": str(run_dir / "training_logs"),
                                                    "enable_model_summary": False})
        for feature in features:
            model.add_future_regressor(feature, normalize="off")
        segmented, episodes = neural_training_segments(history, features)
        first_episode_id = segmented.ID.iloc[0]
        (run_dir / "training_episodes.json").write_text(json.dumps(episodes, indent=2))
        trace = model.fit(segmented, freq="h", progress=None, num_workers=0, checkpointing=False)
        trace.to_csv(run_dir / "training_trace.csv", index=False)
        if not np.isfinite(trace["Loss"]).all():
            raise ValueError("Nonfinite NeuralProphet training loss")
        meta["training_episodes_retained"] = sum(x["retained"] for x in episodes)
        meta["training_samples"] = sum(x["training_samples"] for x in episodes)
        meta["training_loss_first"] = float(trace.Loss.iloc[0])
        meta["training_loss_last"] = float(trace.Loss.iloc[-1])
        meta["training_loss_min"] = float(trace.Loss.min())
        meta["epochs_completed"] = len(trace)
        meta["target_normalization"] = {
            "shift": float(model.config_normalization.global_data_params["y"].shift),
            "scale": float(model.config_normalization.global_data_params["y"].scale)}
    else:
        raise ValueError(family)
    meta["fit_seconds"] = time.perf_counter()-begin
    return Fitted(family, model, features, scaler, bounds, position, meta, first_episode_id)


def forecast(fitted, grid, position, horizon=168):
    cfg = configuration()
    history, future_x = origin_inputs(grid, position, features=fitted.features, horizon=horizon)
    future_x = transform_inputs(future_x, fitted.features, fitted.scaler, fitted.bounds)
    begin = time.perf_counter()
    components = None
    if fitted.family == "sarimax":
        exog = future_x[fitted.features] if fitted.features else None
        result = fitted.model.forecast(steps=horizon, exog=exog)
        predicted = result.to_numpy()
        if not result.index.equals(future_x.index):
            raise ValueError("SARIMAX target timestamps differ from the calendar")
    elif fitted.family == "prophet":
        future = future_x.reset_index().rename(columns={"datetime": "ds"})
        result = fitted.model.predict(future)
        if not pd.DatetimeIndex(result.ds).equals(future_x.index):
            raise ValueError("Prophet target timestamps differ from the calendar")
        predicted = result.yhat.to_numpy()
        cols = [c for c in ["trend", "daily", "weekly", "yearly"] + fitted.features if c in result]
        components = result[["ds"] + cols]
    else:
        context = transform_inputs(history.iloc[-168:], fitted.features, fitted.scaler, fitted.bounds)
        frame = prophet_frame(context)
        frame["ID"] = fitted.first_episode_id
        future = future_x.reset_index().rename(columns={"datetime": "ds"})
        input_frame = np_future(fitted.model, frame, future if fitted.features else None)
        result = np_predict(fitted.model, input_frame, raw=True)
        predicted = extract_raw_forecast(result, future_x.index[0], horizon).to_numpy()
    if len(predicted) != horizon or not np.isfinite(predicted).all():
        raise ValueError("Forecast contains a missing/nonfinite or misaligned lead")
    return predicted, time.perf_counter()-begin, components


def advance_frozen_sarimax(fitted, grid, start, stop):
    if fitted.family != "sarimax":
        return 0.0
    history = grid.iloc[:stop][["pm2_5"] + fitted.features]
    interval = history.iloc[start:stop].copy()
    if fitted.features:
        # Transform only previously revealed values and causal history fills.
        values = transform_inputs(history, fitted.features, fitted.scaler, fitted.bounds)
        interval = values.iloc[start:stop]
        exog = values[fitted.features].ffill().iloc[start:stop]
    else:
        exog = None
    begin = time.perf_counter()
    fitted.model = advance_sarimax_state(fitted.model, interval.pm2_5, exog)
    return time.perf_counter()-begin
