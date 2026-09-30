"""Installed-library checks on tiny synthetic data; no research scores."""
import json
import time
import warnings
import numpy as np
import pandas as pd
from .protocol import REVISION, prophet_frame, extract_raw_forecast, neural_training_segments, advance_sarimax_state


def np_future(model, history, future_inputs):
    """Build a NaN-target future frame using observed context and PP inputs only."""
    future = model.make_future_dataframe(history, regressors_df=future_inputs,
                                          periods=model.n_forecasts, n_historic_predictions=False)
    first_future = (future_inputs.ds.min() if future_inputs is not None
                    else history.ds.max() + pd.Timedelta(hours=1))
    assert future.loc[future.ds >= first_future, "y"].isna().all()
    return future


def np_predict(model, future, raw):
    """Work around 0.9.0's uninitialized conditional_cols for NaN future targets.

    Enable its preprocessing branch ONLY at prediction, with complete observed
    context and complete future X. There are no internal missing values to fill;
    the unknown future target is dropped/restored by library code. Training
    retains impute_missing=False. Never modify the installed library.
    """
    original = model.config_missing.impute_missing
    cfg = model.config_regressors.regressors
    cols = ["y"] + (list(cfg) if cfg else [])
    context = future.iloc[:model.n_lags]
    if len(future) != model.n_lags + model.n_forecasts:
        raise ValueError("Expected precisely one complete forecast-origin input frame")
    if context[cols].isna().any().any():
        raise ValueError("Prediction compatibility path requires complete observed context")
    tail = future.iloc[model.n_lags:]
    if not tail["y"].isna().all():
        raise ValueError("Future target values must be unavailable")
    if cfg and future[list(cfg)].isna().any().any():
        raise ValueError("Missing PP covariates may not be auto-imputed")
    model.config_missing.impute_missing = True
    try:
        return model.predict(future.copy(), raw=raw, decompose=False)
    finally:
        model.config_missing.impute_missing = original


def neural_check(directory):
    from neuralprophet import NeuralProphet, set_random_seed, set_log_level
    set_log_level("ERROR")
    set_random_seed(42)
    n, lag, horizon = 160, 8, 4
    dates = pd.date_range("2024-01-01", periods=n+horizon, freq="h")
    x = np.sin(np.arange(n+horizon)/10)
    frame = pd.DataFrame({"pm2_5": 20+3*x[:n], "x": x[:n]}, index=dates[:n])
    frame.index.name = "datetime"
    frame.iloc[30:34] = np.nan
    history, segments = neural_training_segments(frame, ["x"], lag, horizon)
    model = NeuralProphet(n_lags=lag, n_forecasts=horizon, epochs=2, batch_size=32,
        learning_rate=.001, yearly_seasonality=False, weekly_seasonality=False,
        daily_seasonality=True, impute_missing=False, drop_missing=True,
        global_normalization=True, global_time_normalization=True,
        accelerator="cpu", trainer_config={"default_root_dir": str(directory), "enable_model_summary": False})
    model.add_future_regressor("x", normalize="off")
    trace = model.fit(history, freq="h", progress=None, num_workers=0, checkpointing=False)
    trace.to_csv(directory / "neural_synthetic_training.csv", index=False)
    print("Synthetic training trace:", trace.to_dict("records"), flush=True)
    assert not model.config_missing.impute_missing
    assert np.isfinite(trace["Loss"]).all(), "Missing-data training produced invalid losses"
    future_x = pd.DataFrame({"ds": dates[n:], "x": x[n:]})
    context = history.iloc[-lag:].copy()
    future = np_future(model, context, future_x)
    original_error = None
    try:
        model.predict(future.copy(), raw=True, decompose=False)
    except Exception as exc:
        original_error = f"{type(exc).__name__}: {exc}"
    raw = np_predict(model, future, raw=True)
    by_target = np_predict(model, future, raw=False)
    extracted = extract_raw_forecast(raw, dates[n], horizon)
    diagonal = np.array([by_target.loc[by_target.ds==dates[n+i], f"yhat{i+1}"].iloc[0] for i in range(horizon)])
    np.testing.assert_allclose(extracted.values, diagonal, rtol=1e-6)
    # With one origin, yhat1 has exactly one valid future prediction.
    last_yhat1 = by_target.loc[by_target.ds>=dates[n], "yhat1"]
    assert last_yhat1.notna().sum() == 1
    assert not model.config_missing.impute_missing, "Compatibility path changed training policy"
    params = model.config_normalization.global_data_params["y"]
    np.testing.assert_allclose(params.shift, history.y.min())
    np.testing.assert_allclose(params.scale, history.y.quantile(.95)-history.y.min())
    # Translating only the training target must translate physical-unit forecasts
    # by the same amount. This checks inverse normalization, not predictive skill.
    translated = history.copy()
    translated["y"] += 1000
    set_random_seed(42)
    shifted_model = NeuralProphet(n_lags=lag, n_forecasts=horizon, epochs=2, batch_size=32,
        learning_rate=.001, yearly_seasonality=False, weekly_seasonality=False,
        daily_seasonality=True, impute_missing=False, drop_missing=True,
        global_normalization=True, global_time_normalization=True, accelerator="cpu",
        trainer_config={"default_root_dir": str(directory / "normalization_check"), "enable_model_summary": False})
    shifted_model.add_future_regressor("x", normalize="off")
    shifted_model.fit(translated, freq="h", progress=None, num_workers=0, checkpointing=False)
    shifted_future = np_future(shifted_model, translated.iloc[-lag:], future_x)
    shifted_raw = np_predict(shifted_model, shifted_future, raw=True)
    shifted_values = extract_raw_forecast(shifted_raw, dates[n], horizon).values
    np.testing.assert_allclose(shifted_values, extracted.values+1000, rtol=0, atol=.0002)
    trace.to_csv(directory / "neural_synthetic_training.csv", index=False)
    raw.to_csv(directory / "neural_synthetic_raw.csv", index=False)
    return {"missing_source_values": 4, "finite_training_loss": True,
            "training_episodes": segments, "gap_crossing_training_samples": 0,
            "raw_vs_target_diagonal_equal": True, "valid_future_yhat1": 1,
            "normalization_training_only_parameters_checked": True,
            "physical_unit_translation_check_passed": True,
            "original_no_imputation_prediction_error": original_error,
            "prediction_only_compatibility_path_passed": True,
            "fit_target_imputation_disabled": True}


def sarimax_check():
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    dates = pd.date_range("2024-01-01", periods=104, freq="h")
    rng = np.random.default_rng(42)
    y = pd.Series(10+np.cumsum(rng.normal(size=104)), index=dates)
    x = pd.DataFrame({"x": np.cos(np.arange(104)/10)}, index=dates)
    y.iloc[20:22] = np.nan
    y.iloc[85:87] = np.nan
    fit = SARIMAX(y.iloc[:80], exog=x.iloc[:80], order=(1,0,0), trend="c").fit(disp=False)
    before = fit.params.copy()
    updated = advance_sarimax_state(fit, y.iloc[80:100], exog=x.iloc[80:100])
    pd.testing.assert_series_equal(before, updated.params)
    forecast = updated.forecast(steps=4, exog=x.iloc[100:])
    assert forecast.index.equals(dates[100:])
    assert np.isfinite(forecast).all()
    low = SARIMAX(y.iloc[:80], exog=x.iloc[:80], order=(1,0,0), trend="c").filter(fit.params, low_memory=True)
    low_updated = advance_sarimax_state(low, y.iloc[80:100], exog=x.iloc[80:100])
    low_forecast = low_updated.forecast(steps=4, exog=x.iloc[100:])
    np.testing.assert_allclose(low_forecast, forecast, rtol=1e-10)
    return {"missing_endog_accepted": True, "parameters_unchanged_after_extend": True,
            "forecast_index_after_state_update_correct": True,
            "low_memory_state_refresh_matches_standard_extend": True}


def main():
    directory = REVISION / "artifacts/phase1/model_checks"
    directory.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    results = {"sarimax": sarimax_check(), "neuralprophet": neural_check(directory)}
    results["elapsed_seconds_including_imports"] = time.perf_counter()-start
    (directory / "results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        warnings.filterwarnings("ignore", message="Protobuf gencode version.*")
        main()
