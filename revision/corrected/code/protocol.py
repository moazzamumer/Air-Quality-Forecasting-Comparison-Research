"""Calendar, origin isolation, preprocessing and forecast extraction contracts."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
REVISION = ROOT / "revision/corrected"


def original_path(name):
    """Resolve preserved originals after repository-only archival moves."""
    relocation = REVISION / "archive_locations.json"
    if relocation.exists():
        for move in json.loads(relocation.read_text())["moves"]:
            source, target = move["from"], move["to"]
            if name == source or name.startswith(source + "/"):
                return ROOT / (target + name[len(source):])
    return ROOT / name


def configuration():
    return json.loads((REVISION / "config/protocol.json").read_text())


def load_calendar(path=None):
    cfg = configuration()
    raw = pd.read_csv(path or ROOT / cfg["source"])
    raw.index = pd.DatetimeIndex(pd.to_datetime(raw[["year", "month", "day", "hour"]]), name="datetime")
    if raw.index.has_duplicates:
        raise ValueError("Duplicate timestamps require an explicit resolution before modeling")
    raw = raw.sort_index()
    policy = cfg['invalid_pollutant_policy']
    pollutant_columns = [cfg['target']] + policy['affected_columns']
    bad = raw[pollutant_columns].lt(0)
    counts = bad.sum().to_dict()
    expected = {name: policy['expected_by_column'].get(name, 0) for name in pollutant_columns}
    if counts != expected or int(bad.sum().sum()) != policy['expected_invalid_cells']:
        raise ValueError(f'Unexpected negative pollutant values: {counts}; expected {expected}')
    for name in policy['affected_columns']:
        invalid = bad[name]
        if not raw.loc[invalid, name].eq(policy['invalid_value']).all():
            raise ValueError(f'Unexpected invalid pollutant code in {name}')
        raw.loc[invalid, name] = np.nan
    if not (raw.index == raw.index.floor("h")).all():
        raise ValueError("Non-hourly timestamp labels")
    grid = raw.reindex(pd.date_range(raw.index.min(), raw.index.max(), freq="h", name="datetime"))
    grid["row_observed"] = grid.index.isin(raw.index)
    return raw, grid


def split_position(grid):
    return int(configuration()["train_fraction"] * len(grid))


def window_table(grid, start, stop=None):
    cfg = configuration()
    stop = len(grid) if stop is None else stop
    h, lag = cfg["horizon_hours"], cfg["context_hours"]
    columns = [cfg["target"]] + cfg["broad_features"]
    records = []
    for number, position in enumerate(range(start, stop, h), 1):
        future = grid.iloc[position:min(position+h, stop)]
        context = grid.iloc[max(0, position-lag):position]
        reasons = []
        if len(future) != h:
            reasons.append("incomplete_terminal_window")
        if len(context) != lag or context[columns].isna().any().any():
            reasons.append("missing_context")
        if future[columns].isna().any().any():
            reasons.append("missing_future_target_or_PP_covariates")
        records.append(dict(window=number, position=position, origin=str(future.index[0]),
                            last_target=str(future.index[-1]), calendar_hours=len(future),
                            observed_target_hours=int(future[cfg["target"]].notna().sum()),
                            missing_context_hours=int(context[columns].isna().any(axis=1).sum()),
                            missing_future_hours=int(future[columns].isna().any(axis=1).sum()),
                            eligible=not reasons, exclusion=";".join(reasons)))
    return pd.DataFrame(records)


def origin_inputs(grid, position, features=None, horizon=None, context=None):
    cfg = configuration()
    features = cfg["selected_features"] if features is None else features
    horizon = cfg["horizon_hours"] if horizon is None else horizon
    context = cfg["context_hours"] if context is None else context
    history = grid.iloc[:position][[cfg["target"]] + features].copy()
    future_x = grid.iloc[position:position+horizon][features].copy()
    past = history.iloc[-context:]
    if len(future_x) != horizon or future_x.isna().any().any():
        raise ValueError("Incomplete future PP covariates")
    if len(past) != context or past.isna().any().any():
        raise ValueError("Incomplete observed context")
    # Deliberately do not return future targets: scoring has a separate path.
    return history, future_x


def fit_input_scaler(history, features, clip=False):
    observed = history[features].dropna()
    if not features:
        return None, None
    bounds = (observed.quantile(.01), observed.quantile(.99)) if clip else None
    values = observed.clip(bounds[0], bounds[1], axis=1) if clip else observed
    return StandardScaler().fit(values), bounds


def transform_inputs(frame, features, scaler, bounds=None):
    result = frame.copy()
    if not features:
        return result
    values = result[features]
    if bounds is not None:
        values = values.clip(bounds[0], bounds[1], axis=1)
    result[features] = scaler.transform(values)
    return result


def prophet_frame(frame):
    return frame.rename(columns={"pm2_5": "y"}).reset_index().rename(columns={"datetime": "ds"})


def neural_training_segments(frame, features, lag=168, horizon=168):
    """Complete contiguous episodes; shared parameters, no gap-crossing windows.

    All rows of a retained episode are observed. Episodes shorter than lag+horizon
    have no complete training sample and are excluded, with counts returned.
    """
    columns = ["pm2_5"] + features
    valid = frame[columns].notna().all(axis=1)
    starts = valid.ne(valid.shift()).cumsum()
    episodes, records = [], []
    for number, (_, episode) in enumerate(frame.loc[valid].groupby(starts.loc[valid])):
        keep = len(episode) >= lag+horizon
        identifier = f"episode_{number:03d}"
        records.append({"ID": identifier, "start": str(episode.index[0]), "end": str(episode.index[-1]),
                        "observed_hours": len(episode), "retained": keep,
                        "training_samples": max(0, len(episode)-lag-horizon+1)})
        if keep:
            data = prophet_frame(episode[columns])
            data["ID"] = identifier
            episodes.append(data)
    if not episodes:
        raise ValueError("No complete contiguous NeuralProphet training episode")
    combined = pd.concat(episodes, ignore_index=True)
    if combined[["y"]+features].isna().any().any():
        raise AssertionError("Synthetic/missing training labels entered a complete episode")
    return combined, records


def advance_sarimax_state(fitted, endog, exog):
    """Keep parameters fixed while refreshing the filter, including low-memory fits.

    statsmodels 0.14.5's extend assumes the public predicted_state arrays exist.
    A low-memory initial fit retains its terminal state in filter_results instead.
    Clone only the new interval, initialize from that terminal predicted state,
    and filter with the existing parameters. Subsequent short intervals can use
    extend normally. This avoids retaining full-history covariance trajectories.
    """
    if fitted.predicted_state is not None and fitted.predicted_state_cov is not None:
        refreshed = fitted.extend(endog, exog=exog)
    else:
        filt = fitted.filter_results
        state = np.array(filt.predicted_state[..., -1], copy=True)
        covariance = np.array(filt.predicted_state_cov[..., -1], copy=True)
        model = fitted.model.clone(endog, exog=exog)
        model.ssm.initialize_known(state, covariance)
        refreshed = model.filter(fitted.params, transformed=True, conserve_memory=0, cov_type="none")
    np.testing.assert_array_equal(fitted.params, refreshed.params)
    return refreshed


def extract_raw_forecast(raw, first_target, horizon):
    """NeuralProphet 0.9: raw ds is the first target, step0 is lead hour 1."""
    rows = raw.loc[pd.to_datetime(raw["ds"]) == pd.Timestamp(first_target)]
    if len(rows) != 1:
        raise ValueError(f"Expected one origin row at {first_target}, found {len(rows)}")
    columns = [f"step{i}" for i in range(horizon)]
    missing = set(columns) - set(rows.columns)
    if missing:
        raise ValueError(f"Missing horizon columns: {sorted(missing)}")
    values = rows[columns].iloc[0].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite forecast; do not silently change scoring coverage")
    return pd.Series(values, index=pd.date_range(first_target, periods=horizon, freq="h"), name="prediction")


def persistence(history, horizon=168, cycle=1):
    recent = history["pm2_5"].iloc[-cycle:].to_numpy()
    if len(recent) != cycle or not np.isfinite(recent).all():
        raise ValueError("Missing persistence context")
    return np.resize(recent, horizon)


def apply_bias(base, actual, bias, alpha):
    base, actual = np.asarray(base), np.asarray(actual)
    if base.shape != actual.shape or not np.isfinite(base).all() or not np.isfinite(actual).all():
        raise ValueError("Correction requires matched, complete observed arrays")
    corrected = base + bias
    next_bias = alpha * float(np.mean(actual-base)) + (1-alpha) * bias
    return corrected, next_bias
