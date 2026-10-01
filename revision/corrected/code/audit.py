"""Reproducible Phase 1 audit; writes exclusively beneath revision/."""
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import platform
import re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression
from .protocol import ROOT, REVISION, configuration, load_calendar, split_position, window_table, original_path

ARTIFACTS = REVISION / "artifacts/phase1"
REPORTS = REVISION / "reports"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def original_paths():
    names = ["main.ipynb", "weather_data_extraction.ipynb", "data/beijing.csv",
             "data/beijing_preprocessed_unscaled.csv", "regime1_all_models.py", "regime1_enhanced.py"]
    submission = ROOT / "PM_Forecasting_Environmental_Modeling_Assessment_Submission"
    names += [str(p.relative_to(ROOT)) for p in sorted(submission.iterdir()) if p.is_file()]
    return {name: original_path(name) for name in names}


def manifest():
    path = ARTIFACTS / "original_manifest.json"
    now = {name: {"sha256": digest(p), "bytes": p.stat().st_size} for name, p in original_paths().items()}
    if path.exists():
        original = json.loads(path.read_text())
        if original["files"] != now:
            raise RuntimeError("Original input checksums changed since the preservation baseline")
    else:
        path.write_text(json.dumps({"created_utc": datetime.now(timezone.utc).isoformat(), "files": now}, indent=2))
    return now


def statistics(series):
    s = series.dropna()
    return {"observed_n": int(len(s)), "mean": float(s.mean()), "sd": float(s.std(ddof=1)),
            "median": float(s.median()), "q25": float(s.quantile(.25)), "q75": float(s.quantile(.75)),
            "iqr": float(s.quantile(.75)-s.quantile(.25)), "min": float(s.min()), "max": float(s.max())}


def gap_table(grid):
    missing = ~grid["row_observed"]
    groups = missing.ne(missing.shift()).cumsum()
    return pd.DataFrame([dict(start=str(x.index.min()), end=str(x.index.max()), hours=len(x))
                         for _, x in grid[missing].groupby(groups[missing])])


def feature_analysis(train, cfg):
    features = cfg["broad_features"]
    complete = train[[cfg["target"]] + features].dropna()
    correlations = complete[features].corrwith(complete[cfg["target"]])
    mi = mutual_info_regression(complete[features], complete[cfg["target"]], random_state=42)
    ranks = pd.DataFrame({"feature": features, "pearson_r": correlations.reindex(features).values,
                          "mutual_information": mi})
    ranks["absolute_correlation_rank"] = ranks.pearson_r.abs().rank(method="min", ascending=False).astype(int)
    ranks["MI_rank"] = ranks.mutual_information.rank(method="min", ascending=False).astype(int)
    ranks.to_csv(ARTIFACTS / "feature_rankings_training_only.csv", index=False)
    edges, discrete = {}, pd.DataFrame(index=complete.index)
    for col in complete.columns:
        bins = np.unique(complete[col].quantile(np.linspace(0, 1, 6)).to_numpy())
        if len(bins) < 2:
            discrete[col] = 0
        else:
            discrete[col] = pd.cut(complete[col], bins=bins, labels=False, include_lowest=True).astype(int)
        edges[col] = bins.tolist()
    # pymrmr requires target FIRST and already-discretized integer columns.
    discrete = discrete.rename(columns={cfg["target"]: "target"})
    assert discrete.columns[0] == "target"
    import pymrmr
    chosen = pymrmr.mRMR(discrete.reset_index(drop=True), "MIQ", 5)
    if "target" in chosen or not set(chosen) <= set(features):
        raise RuntimeError("Invalid mRMR output")
    record = {"training_rows": len(complete), "criterion": "MIQ", "requested_features": 5,
              "target_position": 0, "discretization": "training-only quintiles, duplicate edges removed",
              "edges": edges, "selected": chosen,
              "role": "descriptive corrected rerun; does not retrospectively select the predefined four gases"}
    (ARTIFACTS / "mrmr_training_only.json").write_text(json.dumps(record, indent=2))
    return ranks, record


def main():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    original = manifest()
    cfg = configuration()
    raw, grid = load_calendar()
    source_raw = pd.read_csv(ROOT / cfg['source'])
    source_raw.index = pd.DatetimeIndex(pd.to_datetime(source_raw[['year','month','day','hour']]), name='datetime')
    source_raw = source_raw.sort_index()
    split = split_position(grid)
    test_windows = window_table(grid, split)
    validation = window_table(grid, split-4*168, split)
    assert validation.eligible.all(), "Validation origins require explicit revision of protocol"
    test_windows.to_csv(ARTIFACTS / "test_windows.csv", index=False)
    validation.to_csv(ARTIFACTS / "validation_windows.csv", index=False)
    gaps = gap_table(grid)
    gaps.to_csv(ARTIFACTS / "missing_hour_intervals.csv", index=False)
    pd.DataFrame({"datetime": grid.index, "row_observed": grid.row_observed.values,
                  "target_observed": grid.pm2_5.notna().values}).to_csv(ARTIFACTS / "calendar_observation_mask.csv", index=False)
    pre = pd.read_csv(ROOT / "data/beijing_preprocessed_unscaled.csv", parse_dates=["datetime"])
    removed = source_raw.loc[~source_raw.index.isin(pre.datetime)]
    from scipy.stats import zscore
    numeric = source_raw[["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3", "temperature", "dewpt"]]
    expected = numeric[(numeric.apply(zscore) < 3).all(axis=1)]
    pre_indexed = pre.set_index("datetime").sort_index()
    matches = expected.index.equals(pre_indexed.index) and np.allclose(expected.to_numpy(), pre_indexed[expected.columns].to_numpy())
    counts = dict(raw_rows=len(source_raw), raw_missing_values=int(source_raw.isna().sum().sum()),
                  corrected_input_missing_values=int(raw.isna().sum().sum()), calendar_hours=len(grid),
                  missing_hours=int((~grid.row_observed).sum()), gap_intervals=len(gaps),
                  training_calendar_hours=split, training_observed_targets=int(grid.iloc[:split].pm2_5.notna().sum()),
                  test_calendar_hours=len(grid)-split, test_observed_targets=int(grid.iloc[split:].pm2_5.notna().sum()),
                  full_test_windows=int((test_windows.calendar_hours==168).sum()),
                  eligible_test_windows=int(test_windows.eligible.sum()),
                  evaluated_hours=int(test_windows.loc[test_windows.eligible, "calendar_hours"].sum()),
                  tail_hours=int(test_windows.loc[test_windows.calendar_hours<168, "calendar_hours"].sum()),
                  preprocessed_rows=len(pre), removed_original_rows=len(removed),
                  preprocessed_matches_notebook_global_zscore_filter=bool(matches))
    (ARTIFACTS / "data_audit.json").write_text(json.dumps({"counts": counts, "first_timestamp": str(grid.index[0]),
                  "last_timestamp": str(grid.index[-1]), "train_start": str(grid.index[0]),
                  "train_end": str(grid.index[split-1]), "test_start": str(grid.index[split]),
                  "test_end": str(grid.index[-1]), "coordinates_csv": raw[["latitude", "longitude"]].drop_duplicates().to_dict("records"),
                  "duplicates": int(raw.index.duplicated().sum()), "descriptive": {
                      "all_observed": statistics(raw.pm2_5), "training": statistics(grid.iloc[:split].pm2_5),
                      "test": statistics(grid.iloc[split:].pm2_5), "removed_by_original_filter": statistics(removed.pm2_5)}}, indent=2))
    cells = json.loads((ROOT / "main.ipynb").read_text())["cells"]
    inventory = []
    for i, c in enumerate(cells):
        source = "".join(c["source"])
        inventory.append(dict(cell_index_zero_based=i, type=c["cell_type"], lines=len(source.splitlines()),
                              execution_count=c.get("execution_count"), outputs=len(c.get("outputs", [])),
                              first_line=source.splitlines()[0] if source.splitlines() else ""))
    pd.DataFrame(inventory).to_csv(ARTIFACTS / "notebook_inventory.csv", index=False)
    source = json.loads(original_path("weather_data_extraction.ipynb").read_text())
    extraction = "\n".join("".join(c["source"]) for c in source["cells"])
    endpoints = sorted(set(re.findall(r'https?://[^\s"?]+', extraction)))
    provenance = {"endpoints_in_source": [x for x in endpoints if "api." in x or "archive-api" in x],
                  "requested_coordinates_source": {"latitude": 39.906217, "longitude": 116.3912757},
                  "retrieval_date": "not recorded in available artifacts; filesystem dates are not retrieval evidence",
                  "timestamp_evidence": "pandas conversion from UNIX seconds without timezone localization; Open-Meteo request omits timezone (provider default GMT); UTC interpretation supported, original raw JSON/execution logs unavailable",
                  "requested_bounds_in_source": ["2019-01-01", "2025-06-30"],
                  "actual_bounds": [str(grid.index[0]), str(grid.index[-1])],
                  "pollutant_units": "micrograms per cubic metre, per provider documentation",
                  "weather_units": "degrees Celsius under provider defaults; archived response metadata unavailable",
                  "source_kind": "API-derived gridded/model estimates; not identified station observations",
                  "recovery_limitations": ["Extraction deletes temporary response JSONs", "merge is inner join followed by dropna",
                     "AQI copies first response value to every row; AQI is excluded from this study",
                     "components.values() uses JSON key order rather than named field lookup; archived responses cannot independently authenticate the mapping",
                     "Current OpenWeather documentation says history starts 2020-11-27, while CSV begins 2020-11-25; source-date discrepancy unresolved"],
                  "documentation": ["https://openweathermap.org/api/air-pollution", "https://open-meteo.com/en/docs/historical-weather-api"]}
    (ARTIFACTS / "provenance.json").write_text(json.dumps(provenance, indent=2))
    ranks, mrmr = feature_analysis(grid.iloc[:split], cfg)
    versions = {}
    for name in ["numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "prophet", "neuralprophet", "torch", "pymrmr", "psutil", "pytorch-lightning"]:
        try: versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name] = None
    (ARTIFACTS / "environment.json").write_text(json.dumps({"python": platform.python_version(), "platform": platform.platform(), "versions": versions}, indent=2))
    (REVISION / "requirements-observed.txt").write_text("# Observed local environment; not yet a clean-environment lockfile\n" + "\n".join(f"{n}=={v}" for n,v in versions.items() if v) + "\n")
    eligible = test_windows.loc[test_windows.eligible, "window"].tolist()
    report = f'''# Phase 1 data and source audit

Generated by `python -m revision.corrected.code.audit`; original SHA-256 checksums preserved in `artifacts/phase1/original_manifest.json`. The corrected loader masks the four recorded `-9999` pollutant input cells in memory; see `input_audit.json` and `invalid_input_changes.csv`.

## Coverage

- Raw CSV: {len(raw):,} rows, {grid.index[0]} to {grid.index[-1]}; {counts['raw_missing_values']} empty numeric/data values but **{counts['missing_hours']} absent hourly timestamps**, across {len(gaps)} intervals.
- Complete calendar: {len(grid):,} hours. Chronological 90/10 split: {split:,} training hours ({grid.index[0]}–{grid.index[split-1]}), {len(grid)-split:,} test hours ({grid.index[split]}–{grid.index[-1]}).
- Test: {counts['full_test_windows']} complete calendar weeks plus {counts['tail_hours']} terminal hours. The main corrected experiment retains **23 full calendar origins / 3,624 observed scoring hours** with a common hour-level mask. Under the older strict complete-context rule, **{len(eligible)} eligible weeks / {counts['evaluated_hours']:,} scored observed hours** remain for secondary sensitivity analysis.
- Eligible window numbers: {eligible}. Exclusions and exact dates are in `test_windows.csv`. Eligibility uses availability alone, never target magnitudes or model errors.
- The main experiment fills historical inference context causally where needed but never fills fitting or scoring targets. Missing future inputs are computational placeholders, and their hours are excluded from the shared score mask. The strict sensitivity excludes weeks with missing future inputs or context.

## Original preprocessing

- The preprocessed CSV contains {len(pre):,} rows, deleting {len(removed):,} raw observations. Exact timestamp/value reproduction of notebook cell 17's whole-dataset `(zscore < 3)` filter: **{matches}**.
- This is upper-tail row removal, not 1st/99th-percentile winsorization. It uses full-series statistics and destroys the regular hourly sampling grid. The revision starts from the raw CSV and scores original targets.
- Raw PM2.5 mean {raw.pm2_5.mean():.3f}, sample SD {raw.pm2_5.std():.3f}, min {raw.pm2_5.min():.2f}, max {raw.pm2_5.max():.2f} micrograms/m³. Partition-specific statistics are in `data_audit.json`; no physical observation validation is inferred from these estimates.

## Source provenance

CSV coordinates: {raw[['latitude','longitude']].drop_duplicates().to_dict('records')}. Extraction request coordinates: 39.906217°N, 116.3912757°E. Historical endpoints are recorded without credentials in `provenance.json`.

UTC is supported by UNIX-second conversion and the weather API's omitted-timezone default; it is an evidence-based interpretation, not independently authenticated historic execution. Retrieval dates and original response metadata are unavailable. Source requested bounds differ from actual CSV coverage. Current provider documentation and the earliest CSV date also differ; do not hide that discrepancy or invent retrieval information.

The source merges on calendar fields with an inner join and drops incomplete rows. It does not establish that missing hours were absent from both providers, or that the meteorological and pollutant estimates are direct station measurements.

## Feature analysis

Original cell 26 uses `pymrmr` with a target in the last column and no explicit discretization. The library requires an already-discretized target in the first column. Its saved outputs include the target as a selected feature, and do not match the currently stored call. Those outputs cannot establish the claimed selection procedure.

Corrected descriptive analysis uses {mrmr['training_rows']:,} observed training rows, fixed seed 42 for MI, training-derived quintile bins and MIQ with five selected predictors. mRMR result: {mrmr['selected']}. Full rankings and bin edges are saved. The four gases remain a predefined experimental subset; this corrected rerun does not retrospectively prove their original selection.

## Original-file preservation

{len(original)} original files were fingerprinted. Re-running this audit refuses to proceed if any fingerprint has changed. Neither notebook, raw CSV nor manuscript is edited by the audit.

## Documentation

- [OpenWeather Air Pollution API](https://openweathermap.org/api/air-pollution): response units/time semantics and current historical-availability statement.
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): default time/temperature conventions; the exact older ERA5 endpoint is established from local source.
- [pymrmr maintainer documentation](https://github.com/fbrundu/pymrmr): target-first input, discretization and MIQ interface.
'''
    (REPORTS / "PHASE1_DATA_AUDIT.md").write_text(report)
    print(json.dumps(counts, indent=2))
    print("Eligible test windows:", eligible)


if __name__ == "__main__":
    main()
