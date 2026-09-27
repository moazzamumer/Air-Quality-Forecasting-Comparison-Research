# Phase 1 protocol decisions

Machine-readable source: `../config/protocol.json`. Full comparison settings
remain subject to training-only validation and the measured compute budget.

## Data and coverage

Use the raw Beijing CSV, reconstruct its hourly calendar, and preserve original
values and observation masks. Calendar labels run from 2020-11-25 01:00 through
2025-06-29 19:00. UTC interpretation is supported by source/provider conventions;
retrieval logs and archived response metadata are unavailable.

Split the 40,267-hour calendar at position 36,240. Training ends 2025-01-13 00:00;
testing starts 2025-01-13 01:00. Test origins advance every 168 hours. The last
163-hour window starts 2025-06-23 01:00 and is excluded from primary comparisons.

Eligible weeks must have complete original targets and all broad-set PP inputs
throughout the future 168 hours, and complete targets/inputs throughout the
previous 168 hours. This predeclared availability rule is shared by all models
and ablations. It retains weeks 1–7, 10, 16–23 (16 weeks; 2,688 hours). Weeks
8, 9, 11–15 are excluded for missing future data and/or context; exact reasons
are exported in the coverage table. Neither concentrations nor errors determine
eligibility. This reduced and discontinuous coverage limits seasonal claims and
must remain visible in all tables and paired analyses.

Missing target values are never interpolated or treated as observed outcomes.
Training uses model-appropriate missing-data handling: Prophet fits complete
observed rows; SARIMAX retains missing endog on the calendar and forward-fills
missing historical exogenous inputs using past values only for state propagation;
NeuralProphet trains on complete contiguous observed episodes of at least 336
hours with global shared parameters, target normalization and time normalization.
No NeuralProphet training lag/horizon window crosses a gap. Training episode
counts and sample exclusions are saved per fit.

The primary targets and inputs remain unclipped. The planned clipping sensitivity
clips exogenous inputs only using training-derived 1st/99th percentiles. Input
scalers use observed training input rows only. Four gases are predefined; the
corrected descriptive mRMR rerun does not retroactively justify their selection.

## Information and state at each origin

An origin is the timestamp of the first forecasted hour; lead 1 targets that
timestamp and lead 168 targets origin +167 hours. Historical information ends
at origin −1 hour. All three models receive the true future selected inputs
under PP; no future PM2.5 is supplied to prediction routines.

```text
fit preprocessing and model on the initial training partition
bias = 0
for every calendar forecast origin:
    reveal observations strictly before the origin
    advance SARIMAX filtered state through all intervening hours without refitting
    if origin is ineligible:
        record reason; carry correction bias unchanged; continue
    if walk-forward:
        refit preprocessing and model on revealed history only
    forecast the actual next 168 timestamps with future PP inputs
    for NeuralProphet use latest 168 observed targets, shared frozen parameters
        and one raw forecast-origin vector step0 ... step167
    corrected forecast = base forecast + bias available at the origin
    after all 168 outcomes are revealed:
        residual_mean = mean(original target - base forecast)
        bias = alpha * residual_mean + (1 - alpha) * bias
    save timestamps, inputs/configuration identity, predictions and coverage
```

No model forecasts are generated for excluded weeks under the strict protocol,
so no residual correction update is invented for them. Newly observed history
still advances through these weeks for subsequent eligible origins. With gaps
in evaluated weeks, bootstrap blocks may not bridge nonadjacent origins.

NeuralProphet episode IDs are bookkeeping for contiguous training samples, not
stations or separate local models. All components/normalization are shared.
At inference an existing bookkeeping ID is used solely to access the global
model; the supplied observed context and actual timestamps determine forecasts.

## Validation and bounded pilots

Four complete validation origins occur at 2024-12-16, 2024-12-23, 2024-12-30 and
2025-01-06, each at 01:00. Fit candidates before the first origin and evaluate
these four windows entirely within the training partition, refreshing observed
history without parameter refits. Selection uses mean weekly MAE, then pooled
RMSE. No test errors choose hyperparameters or alpha.

Phase 1 pilots use the first validation origin and original full history before
it. NeuralProphet pilots use two epochs, and SARIMAX pilots cap optimization at
ten iterations. Their purpose is to check prediction alignment and estimate
resources; they cannot establish accuracy, convergence or final rankings.

Use CPU execution with two numerical/PyTorch threads, sequential isolated fits
and checkpoints. Import/setup time is separate from model fit/prediction time.
Pilot timing is an estimate only; the revised paper needs controlled Phase 2
measurements at validated configurations, including actual convergence.
