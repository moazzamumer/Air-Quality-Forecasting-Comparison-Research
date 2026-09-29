# Phase 2 experimental evidence

Verification exit evidence ready: **True**. Valid completed tasks: 94/94; numerical recoveries: 6; unresolved failed tasks: 0.

## Training-only settings

Four complete validation weeks were entirely within the training partition. Candidate fits ended before the first validation origin; later origins refreshed history without refitting. Selection used mean weekly MAE, then pooled RMSE. This is a fixed-parameter validation proxy for both core regimes, not exhaustive tuning.

```json
{
  "sarimax": {
    "order": [
      1,
      0,
      1
    ],
    "seasonal_order": [
      1,
      0,
      1,
      24
    ]
  },
  "prophet": {
    "seasonality_mode": "additive"
  },
  "neuralprophet": {
    "epochs": 50
  }
}
```

One of four SARIMAX validation candidates did not converge under the bounded screening policy. Its failure is retained; it was not scored or selected. The subsequent numerical recovery policy applies to final-comparison fits with the selected settings and does not reopen candidate selection.

## Core point estimates and available coverage

| family | regime | seed | windows | hours | recovered_windows | mean_weekly_mae | pooled_rmse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| neuralprophet | frozen | 42 | 16 | 2688 | 0 | 38.4425 | 54.157 |
| neuralprophet | frozen | 123 | 16 | 2688 | 0 | 40.7011 | 55.7874 |
| neuralprophet | frozen | 2026 | 16 | 2688 | 0 | 34.4563 | 47.3575 |
| neuralprophet | walk | 42 | 16 | 2688 | 0 | 34.2246 | 48.9294 |
| neuralprophet | walk | 123 | 16 | 2688 | 0 | 36.0393 | 50.4888 |
| neuralprophet | walk | 2026 | 16 | 2688 | 0 | 34.2501 | 47.3004 |
| prophet | frozen | 42 | 16 | 2688 | 0 | 36.9634 | 49.2811 |
| prophet | walk | 42 | 16 | 2688 | 0 | 35.4976 | 48.5941 |
| sarimax | frozen | 42 | 16 | 2688 | 0 | 29.9143 | 47.5415 |
| sarimax | walk | 42 | 16 | 2688 | 5 | 29.8776 | 47.5056 |

The primary MAE column is mean weekly MAE. Weekly windows all contain 168 hours, so pooled MAE is identical; pooled RMSE differs from mean weekly RMSE. The CSV saves both definitions and sample weekly standard deviations. Each row uses that run’s available complete weeks. If coverage differs, these rows are not a matched ranking. Phase 3 must report matched comparisons, paired uncertainty, lead-time errors, residuals and seed variability. No seed-averaged forecast is substituted for the seed-42 primary run.

## Frozen predictor and clipping controls (seed 42)

| family | variant | windows | hours | recovered_windows | mean_weekly_mae | pooled_rmse |
| --- | --- | --- | --- | --- | --- | --- |
| neuralprophet | broad | 16 | 2688 | 0 | 20.8682 | 28.7808 |
| neuralprophet | clip | 16 | 2688 | 0 | 60.0122 | 78.6622 |
| neuralprophet | no_inputs | 16 | 2688 | 0 | 127.4624 | 192.9712 |
| neuralprophet | selected | 16 | 2688 | 0 | 38.4425 | 54.157 |
| prophet | broad | 16 | 2688 | 0 | 19.9231 | 26.6482 |
| prophet | clip | 16 | 2688 | 0 | 48.2797 | 64.6323 |
| prophet | no_inputs | 16 | 2688 | 0 | 146.8411 | 208.3171 |
| prophet | selected | 16 | 2688 | 0 | 36.9634 | 49.2811 |
| sarimax | broad | 16 | 2688 | 0 | 17.5727 | 24.4265 |
| sarimax | clip | 16 | 2688 | 16 | 32.6548 | 52.1682 |
| sarimax | no_inputs | 16 | 2688 | 0 | 124.3805 | 189.3001 |
| sarimax | selected | 16 | 2688 | 0 | 29.9143 | 47.5415 |

No-input, selected four-gas, broad-input and clipped-input runs retain the selected model settings. Broad inputs include contemporaneous future PM10 under Perfect Prognosis and therefore provide additional target-related information. Clipping affects predictors at training-derived 1st/99th percentiles; fitting/scoring targets remain original. These controls were tested in the frozen regime only.

## Forecast reuse and correction

Three baselines cover 16 weeks / 2,688 hours. All five frozen core streams have no-correction plus six predefined alpha replays, giving 35 saved streams. Alpha 0.3 remains the primary predefined setting. Bias is applied before the current week’s outcomes update it; skipped windows carry the bias unchanged. Corrections use base residual means.

## Numerical fitting and resources

Original nonconverged attempts remain in their own folders and have no scored stream. A recovery, where present, changes numerical initialization, derivative precision and line-search allowance while retaining orders, data cutoff, features and preprocessing; it requires convergence, finite likelihood/parameters, and training likelihood no worse than the original failed point. Verification names the exact recovery evidence used for every task. Runtime analysis must include failed attempts and every recovery effort, including rejected attempts.

The two regimes share the identical initial fit/forecast, explicitly marked by `reused_from_run`; later refits are independent expanding-history fits. All processes use the same local CPU, two configured threads, and no GPU. Original-run `fit_seconds` includes model import/initialization and optimization, excluding earlier calendar/scaler preparation; recovery `fit_seconds` measures optimization only. Recovery preprocessing metadata inherits the original fit description. Supervisor elapsed time includes full child-process setup and is the consistent measure for total effort. Peak group RSS is sampled every 0.5 seconds. Phase 3 must label these timing boundaries and shared/recovered work explicitly.

## Evidence locations

- `artifacts/phase2/verification.json` and `verified_coverage.csv`: completeness, integrity and exact forecast evidence mapping.
- `artifacts/phase2/runs/*/`: timestamped forecasts, training traces/episodes, fit metadata, coefficients/components and logs.
- `artifacts/phase2/baselines/`, `corrections/`, `experimental_summary.csv`, `validation_summary.csv`: reloadable outputs.
- `config/protocol.json` and `config/sarimax_numerical_recovery.json`: locked study protocol and recorded numerical amendment.

All 21 fingerprinted originals remain unchanged. The original `main.ipynb` and submitted manuscript have not been replaced. Phase 2 supplies experimental evidence; manuscript and point-by-point response writing remain pending.
