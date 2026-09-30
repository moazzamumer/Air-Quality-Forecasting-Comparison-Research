# Forecasting lifecycle and leakage review

Reviewed 2026-09-30 against commit `8edeb86` and saved evidence, at Moazzam's request. This is a focused source/evidence audit, not a new experiment or a guarantee of journal acceptance.

## Verdict

**No additional definite future-target leakage or chronological-split violation was found in the inspected revision paths. The core design is defensible as a retrospective, Perfect Prognosis comparison. Numerical readiness remains blocked by the invalid training inputs found in the earlier review.**

Do not interpret this as “all standards certified” or “rejection is impossible.” In particular, upstream data authenticity cannot be established from code alone, and using actual future gases would invalidate an operational forecast interpretation. The previously documented input, runtime, baseline-finalization and reporting issues remain open: [critical review A1–A4](PHASE4A_CRITICAL_REVIEW.md).

## Lifecycle checks

| Area | Finding and evidence |
| --- | --- |
| Data integrity | Calendar reconstructed before splitting; duplicate timestamps rejected; observed targets retained. Four invalid pollutant inputs are a definite unresolved validity defect, not a discovered future-target leak. Original-file hashes were checked in the preceding audit. |
| Chronological separation | Fit history uses rows strictly before the forecast origin. Four validation weeks end before the initial test origin. No shuffled train/test split. Overlapping NeuralProphet training windows stay wholly within their training episodes. |
| Preprocessing | Recomputed all 134 input scalers across 137 final/validation metadata records directly from pre-origin history, including training-derived clipping bounds. All matched. This verifies their temporal boundary, not the validity of the uncorrected input values. |
| Target normalization | Recomputed 77 NeuralProphet target-normalization and training-sample records from retained pre-origin episodes; all matched. No target clipping or fitting-label imputation is recorded. |
| Model selection | Recomputed the seven successful candidates' validation scores and the selection rule. All three selected configurations match, and all 129 final tasks use their corresponding selected configuration. The eighth candidate failed. Validation is a limited four-week frozen-parameter proxy, not separate exhaustive tuning for both regimes. |
| Feature selection | Descriptive mRMR uses the full initial training partition, including its validation interval. It does **not** drive the current candidate search: the four gases are an inherited predefined set. If feature selection becomes part of tuning during repair, fit it inside the pre-validation history; the existing full-training ranking must not select features and then be evaluated on those same validation weeks. |
| Forecast information | SARIMAX/Prophet receive future regressors but no future target; NeuralProphet constructs a future frame with NaN targets and extracts all leads from one origin. Existing mutation tests verify input isolation and the library-specific extraction path. Saved horizon timestamps are aligned. |
| Frozen versus refit | Frozen parameters/scalers remain fixed while state/context refresh uses observations before each origin. Weekly refits may use completed earlier test weeks; this is valid sequential evaluation, not permission to train on the week being predicted. Recovery code prohibits later-cutoff initialization; seven explicit warm-start cutoff fields in the newly audited metadata also passed. |
| Missing history/future inputs | Historical filling is forward-causal. Computational future-input placeholders are masked from scoring and checked for cross-lead effects. Existing actual-model perturbation evidence shows zero effect on scored predictions. Filling can still be inaccurate; a 120-hour historical gap is a material limitation. |
| Residual correction | Prior bias is applied before updating from the completed week's base residuals. The previous audit replayed all 35 streams. Main alpha remains fixed at 0.3; sensitivity results must not be used to retrospectively select a favorable test alpha. |
| Evaluation | All methods use the same 23-origin / 3,624-hour observed mask. Independently recalculated all 27 saved performance summaries; they match. Missing targets are not synthetic labels. Pooled hourly and equally weighted weekly errors have distinct denominators. |
| Uncertainty | Matched weekly losses, blocked resampling and seed averaging avoid treating every hour or seed as an independent replicate. Intervals are limited descriptive comparisons, not forecast prediction intervals or proof of universal superiority. Eleven contrasts are not a multiplicity-adjusted confirmatory hypothesis family. |
| Reproduction | Saved settings, versions, forecasts, traces and provenance support an audit. Original raw-response authentication, clean-environment reproduction, baseline finalization and consistent timing remain unfinished. Existing run signatures alone are not full data/environment fingerprints; corrected runs must bind their new input version, selection and code to their artifacts before any reuse. |

The executable follow-up audit is `venv/bin/python -m revision.code.lifecycle_audit`. It writes only [lifecycle_evidence.json](../artifacts/phase4a/lifecycle_evidence.json). It does not refit a research model, modify data, regenerate model forecasts or rewrite existing metrics. Source inspection supplemented the numeric checks; the existing 26-test passing result is from the preceding review, not a new full-suite run here.

## Boundaries that the paper must state accurately

1. **Perfect Prognosis defines the information set.** Actual future gases are legitimate inputs for the declared conditional retrospective experiment. They are unavailable future information for an ordinary operational forecast. These results therefore do not measure deployable next-week accuracy. Historical weather estimates in the broad ablation also do not establish information availability in real time. Baselines receive less information; beating them does not by itself establish architecture superiority.
2. **Sequential observations are allowed, future observations are not.** Week 1 targets may update week 2's state, refit or correction once week 1 has ended. No extra 168-hour embargo is inherently required here: fitting labels already stop before each origin, and past context is deliberately available. This is not a set of 23 forecasts all issued at the first test date. It assumes past values are available without an unmodeled reporting delay.
3. **The test interval is already examined.** The old study and revision have exposed these outcomes. The 16-to-23-week change was motivated by coverage and continuity, but still occurred after earlier results existed. Document the amendment; do not portray the revised period as an untouched holdout or the whole revision as prospectively preregistered. No test-score optimization was found in the inspected selection code, but code cannot prove absence of every informal research decision. Lock the invalid-input rule and rerun plan before evaluating repaired results; do not restore old rankings by tuning. This does not automatically require replacing the 23-week primary study.
4. **Source provenance remains a substantial scientific uncertainty.** The targets are API-derived estimates, not authenticated station observations. Original response JSONs are absent, the extraction used positional field mapping, and an earliest-date discrepancy remains. The CSV does not prove a wrong mapping, but neither can this audit certify it. Describe those limits precisely; disclosure alone cannot guarantee a reviewer will consider the source evidence sufficient.
5. **The sampled period limits inference.** Four validation weeks, 23 test weeks, partial coverage, clustered extremes and three NeuralProphet seeds support a bounded case study. Missingness may be informative. Do not generalize to all seasons/cities, claim causal pollutant effects, or promise guaranteed model rankings. Training loss/convergence flags alone do not establish optimal model specification; report residual/lead-time diagnostics and bounded search choices.

## What is required before clearing Phase 4B?

The earlier repair sequence still applies: version the pollutant-specific invalid-input correction; repeat affected training-only analysis and validation; rerun affected models; regenerate downstream analysis; resolve A2–A4; then review the corrected evidence. Keep the 23-week primary schedule and preserve pre-correction artifacts. Add input-validity checks and bind corrected data/code/settings to run provenance. Any newly introduced learned feature selection must respect the validation boundary described above.

This pass found no reason to redesign the entire forecasting study. It also does not clear the current numerical results or close the source-provenance questions. No manuscript, fitting code, configuration or existing experiment output was changed by this pass.

## Methodological references used for this review

- [Scikit-learn: common pitfalls and data leakage](https://scikit-learn.org/stable/common_pitfalls.html): fit learned transformations and feature selection on training data, without test-driven model choices.
- [Hyndman and Athanasopoulos: time-series cross-validation](https://otexts.com/fpp3/tscv.html): rolling origins use only prior observations and can assess multi-step forecasts.
- [Hyndman and Athanasopoulos: forecasting with regression](https://otexts.com/fpp3/forecasting-regression.html): ex-post evaluation may use realized predictors while withholding future target values; ex-ante forecasting requires future predictor values to be available or forecast.

These support the criteria above. Conclusions about this repository come from its code and saved evidence, not from the external references.
