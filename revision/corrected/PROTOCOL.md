# Corrected pollutant-input protocol (v2)

Decision recorded 2026-09-30, before inspecting corrected validation or test scores. The scientific target remains Beijing PM2.5 over 168 hours. The primary evaluation retains all 23 complete weekly calendar origins and the existing common observed-hour scoring mask. The old `revision/artifacts/` directory is the preserved pre-correction reference.

## Invalid-input rule

The raw CSV is immutable. The loader creates a working hourly view in memory. It treats `-9999` as missing **only** in pollutant predictor columns `NO`, `NO2`, `CO`, `SO2`, `O3`, `NH3`, and `PM10`. The four known affected cells are one O3, one PM10 and two NO2 values, all before validation fitting. The loader rejects any other negative pollutant concentration or unexpected count/code. It never changes PM2.5 values. Negative temperatures and dew points remain valid. [The rule is machine-readable](config/protocol.json) and enforced by [the versioned loader](code/protocol.py).

This rule responds to chemically impossible negative concentrations and is independent of which candidate or model wins. It does not claim the upstream provider explicitly defined `-9999` as its missing-value marker; the source response archive is unavailable. No high positive concentration is automatically clipped or deleted in the primary experiment.

After conversion to missing, the established model policies apply: SARIMAX causally forward-fills historical exogenous values; Prophet fits observed complete rows; NeuralProphet forms complete contiguous episodes. Future missing inputs are excluded from scoring and computational placeholders are tested for no effect at scored hours. Training and scoring targets are never imputed. Input scaling, any ablation clipping bounds and NeuralProphet target normalization are estimated only from data before each fit origin.

## Validation and experiments

Repeat the existing four chronological training-only validation weeks and bounded candidate grid. Select by mean weekly MAE, then pooled RMSE, without reference to test performance. Use the resulting settings for both frozen and weekly expanding refit regimes. Run the same core families, seeds, predictor/no-input/broad/clipping controls, and 23-week schedule. Repeat the descriptive feature analysis using the corrected training view; retain the four gases as a predefined set rather than recasting them as a validated mRMR selection.

The corrected run directory is `revision/corrected/artifacts/`. The old run directory is never an automatic source of fitted parameters or model forecasts. The **only** planned shared model computation within this version is the identical first-origin frozen fit/forecast for the corresponding week-1 walk task, conditional on exact task/configuration/signature checks. Target-only baseline definitions may reuse concepts from v1 but are regenerated and checked here. A 16-week complete-context sensitivity can be calculated from the corrected 23-week streams; it is secondary.

Existing model recovery is a numerical issue. The selected forecasting orders and data cutoff must stay fixed. The default bounded solver failed at the corrected first test origin and its failed attempt is preserved. The corrected test-origin SARIMAX fits now initialize from the selected, converged training-only validation fit at the first origin and from that corrected first-origin fit later. The fixed recovery method is complex-step L-BFGS-B (200 iterations, 100 line searches); accept only finite converged fits with nondecreasing training likelihood. This recovery was judged on training fit convergence and likelihood, never test error. No model is declared complete merely because the supervisor exited successfully.

## Predeclared reporting rules

- Recompute all correction streams after base forecasts. Main EWMA alpha remains 0.3, with the recorded alpha grid reported as sensitivity, never selected by test score.
- Report both pooled hourly and equally weighted weekly errors, matched comparisons, partial-week counts, lead times, high-pollution performance and NeuralProphet seed variability.
- Separate actual supervisor wall time from model fit/preparation/prediction timers. State timer boundaries and reused first-origin work. Do not assign zero prediction cost to a reused forecast or claim a controlled runtime ratio from incompatible timer boundaries.
- Use a single last-genuine-observation persistence definition at baseline creation and verification. Label Prophet component weighting explicitly; report across-seed mean and sample SD.
- Treat all numerical claims as pending until saved-run integrity checks and a fresh evidence review pass. The author decision checkpoint precedes any working manuscript copy.

The protocol intentionally preserves the original research question, known Perfect Prognosis future-gas assumption, source-provenance limitations and prior test-period exposure. These are reported limits rather than parameters tuned to the corrected results.
