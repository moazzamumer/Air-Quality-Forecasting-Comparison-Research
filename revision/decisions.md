# Critical experiment decisions and their reasoning

This is an author-readable decision record, not a list of every implementation detail. “Applied” means the saved experiments use that choice. It does not mean Moazzam has approved the manuscript wording. “Proposed” means no experiment has yet been changed. Dates refer to the revision work, not the dataset retrieval date.

**2026-09-30 review status:** hold Phase 4B scientific claims pending the invalid-input correction described in D10. The earlier run-completeness and leakage checks did not detect four `-9999` pollutant values in training. Existing results are real computed results but provisional. See [flow](flow.md) and [critical review](reports/PHASE4A_CRITICAL_REVIEW.md).

## D01 — Retain the original scientific question

**Applied; scope agreed with Moazzam.** Keep Beijing PM2.5, SARIMAX/Prophet/NeuralProphet, a 168-hour horizon, frozen parameters versus weekly expanding refit, and EWMA residual correction. The primary inputs remain NO, NO₂, CO and SO₂. No new city or operational covariate-forecasting experiment was added.

**Reason:** answer the reviewers within the existing paper's question and feasible compute budget. These are corrections and extensions to the study, not evidence that every original implementation choice or numerical claim is retained. In particular, the old irregular row chunks, target/input preprocessing, future-regressor supply and forecast extraction had to change.

**Consequence:** describe the evaluated scope accurately; do not claim superiority to unevaluated advanced models or geographic generalization. Evidence: `REVISION_PLAN.md`, `reports/NOTEBOOK_MANUSCRIPT_DISCREPANCIES.md`.

## D02 — Rebuild the hourly calendar and retain real pollution extremes

**Applied; correctness decision.** Start from the raw CSV, preserve its values and restore absent calendar positions as NaN. Replace the original full-dataset upper-tail z-score row deletion. Use chronological 90/10 calendar splitting and compare against original PM2.5 targets. Test target extremes are not clipped.

**Reason:** a 168-row slice after row deletion is not necessarily a 168-hour forecast; full-series filtering also uses information beyond the training period. Reviewers requested original-scale target evaluation and transparent missingness.

**Consequence:** the corrected schedule and results need not numerically reproduce the submitted paper. Historical source values should be preserved for audit, but invalid input codes must not be treated as genuine concentrations—an omission discovered in D10. Evidence: `reports/PHASE1_DATA_AUDIT.md`.

## D03 — Use 23 weekly origins as primary, keep the 16-week result secondary

**Applied at Moazzam's request after the strict comparison.** Keep all 23 full calendar origins and use a common observed-hour mask. Score 3,624 hours across 19 complete and four partial weeks. Report the separate 163-hour tail. Preserve the completed strict 16-week / 2,688-hour experiment as a sensitivity.

**Reason:** removing every week with any missing future/context value discarded available observations and weakened continuity with the intended test period.

**Tradeoff:** dense historical context is causally filled where necessary; that is a substantive assumption, including a 120-hour missing context. Training-only reconstruction checks have large errors. No missing target is invented for fitting or scoring. Computational future-input placeholders are checked for no effect at scored hours. Partial weeks cannot support a full-week accuracy claim, and missingness may be informative. Evidence: `config/coverage_reconsideration.json`, `artifacts/coverage_reconsideration/history_fill_validation.csv`.

## D04 — Keep Perfect Prognosis explicit and the four gases predefined

**Applied; PP-only route agreed with Moazzam.** All three core families receive the actual future selected-gas values. Baselines use only past targets. The four-gas subset is described as predefined, not as proven optimal by the original mRMR output.

**Reason:** the original NeuralProphet implementation did not supply the same future-input information; the feature-selection record was not sufficient to establish the claimed four-gas selection. The corrected training-only descriptive mRMR result differs from that subset.

**Tradeoff:** this measures performance conditional on unavailable-in-practice future observations. Better errors than persistence do not isolate architecture skill because inputs differ. The broad frozen ablation adds future PM10 and other inputs; its lower errors cannot establish that the four-gas subset is optimal or that operational performance improved. Evidence: `reports/NOTEBOOK_MANUSCRIPT_DISCREPANCIES.md`, `artifacts/phase1/mrmr_training_only.json`.

## D05 — Select settings using a bounded chronological validation search

**Applied; current selected settings provisional under D10.** Compare four SARIMAX order combinations, two Prophet seasonality modes, and NeuralProphet 30/50 epochs on four training-only validation weeks. Select mean weekly MAE, then pooled RMSE. Use the same chosen configuration in both regimes. NeuralProphet has three core seeds; extra controls use seed 42.

**Reason:** provide a documented training-only selection method without an unbounded search. No settings are chosen to recover submitted rankings. The existing choices are SARIMAX `(1,0,1) × (1,0,1,24)`, additive Prophet and 50 NeuralProphet epochs.

**Tradeoff:** four winter validation weeks and a fixed-parameter proxy are limited. This is not separately optimized tuning for each regime or ablation. One SARIMAX candidate failed bounded convergence and was excluded. Finite NeuralProphet training loss does not prove optimal training or an inherent architecture ranking. Invalid input correction must precede repeating selection, because all four bad cells occur before validation fitting. Evidence: `artifacts/phase2/selection.json`.

## D06 — Define frozen as fixed parameters with current historical information

**Applied; reviewer-requested clarification/correction.** Refresh SARIMAX's filtered state, give NeuralProphet the latest 168-hour historical context, and make Prophet predict actual current-week dates. Freeze fitted parameters and preprocessing. In weekly refit, re-estimate preprocessing and parameters using all available earlier history.

**Reason:** repeatedly forecasting from the original end state or dates does not implement advancing weekly origins. NeuralProphet now extracts one origin's `step0`–`step167`, with future target values absent.

**Consequence:** refreshed state/history and EWMA are distinct. The first-origin fit is shareable across regimes; later refits are real expanding-history estimation. Evidence: `code/protocol.py`, `code/model_checks.py`, `code/phase2_models.py`.

## D07 — Keep EWMA alpha predefined and evaluate alternatives transparently

**Applied.** Main alpha remains 0.3. Also report no correction, 0.1/0.2/0.5/0.7 and previous-week residual correction (alpha 1). Apply only bias known at the forecast origin, then update after the week using base residuals. Do not select a test-optimal alpha.

**Reason:** answer both reviewers' sensitivity requests without optimizing on held-out errors. EWMA is an established technique whose usefulness is evaluated here, not a new algorithmic contribution.

**Tradeoff:** the broader correction updates on partial-week observed residual means; the strict result carries bias over excluded weeks. Corrected values can differ on shared weeks. The current model/seed-dependent benefits are provisional under D10. Evidence: `artifacts/coverage_reconsideration/corrections/`, `artifacts/phase3/correction_weekly.csv`.

## D08 — Use matched errors and restrained uncertainty claims

**Applied.** Report pooled MAE/RMSE separately from mean weekly metrics and their sample SD. Compare matched weekly losses with 2,000 moving-block replicates (3-week blocks plus 2/4-week sensitivity). Average NeuralProphet losses across seeds for its paired comparison; also retain individual-seed outcomes. Define high pollution using the training target's 95th percentile.

**Reason:** partial weeks have unequal hours, weekly errors are dependent, and seed runs do not create independent test weeks. These distinctions answer the reviewers' aggregation/uncertainty concerns.

**Tradeoff:** 23 seasonal weeks and four partial weeks provide limited inferential evidence. The high-concentration subset has 158 hours in six weeks. Three seeds provide limited repeatability evidence. Do not equate nonzero bootstrap intervals with universal superiority. An explicit across-seed mean/SD summary still needs to be produced from corrected results. Evidence: `code/phase3_analysis.py`, `artifacts/phase3/paired_contrasts.csv`.

## D09 — Save actual run evidence, reuse only checked compatible forecasts

**Applied; implementation decision.** Run memory-heavy fits sequentially on the local CPU with two configured threads. Save forecasts, settings, timing, traces and source provenance. Reuse compatible earlier forecasts; reconstruct frozen SARIMAX from saved fitted parameters. Record numerical recoveries rather than conceal failed attempts.

**Reason:** reproducibility and feasible resource use. A notebook rerun should be able to show/recalculate outputs without repeating all fits. Solver recovery is accepted by convergence, finite parameters and training likelihood, not a favorable test score.

**Tradeoff:** runtime fields do not all have identical measurement boundaries. A reused task's zero prediction time is reuse overhead, not the original model's forecast cost. Recovery fitting timers differ from original fitting timers. Campaign wall-time totals do not establish algorithm speed ratios. Full model objects were not generally archived; a novel analysis requiring unsaved internals may require refitting. Evidence: `artifacts/phase2/recovery_supervisor.jsonl`, `artifacts/phase3/core_timing.csv`, `artifacts/phase3/resource_events.csv`.

## D10 — Correct invalid pollutant input codes before accepting final results

**Proposed on 2026-09-30; NOT applied.** Replace only the four identified `-9999` pollutant input cells with missing values in a new working data view, preserving the raw CSV bytes and observed PM2.5. Retain legitimate negative weather values. Follow the existing model-specific missing-input policies, repeat training-only feature analysis and validation, then rerun affected models and downstream analyses under a new version/signature.

**Reason:** two invalid NO₂ values enter every primary input-based model and validation candidate. Two more invalid values affect broad-input work. They are not ordinary high-pollution outliers. A diagnostic in-memory correction changes initial selected NO₂ scale from 93.3192 to 54.8353 and changes NeuralProphet's training-window construction. We cannot infer harmlessness from the small number of cells or merely rescore existing predictions.

**Consequence:** preserve existing results as pre-correction evidence; do not silently overwrite them or tune to restore their rankings. The 23-origin test schedule and 3,624-hour scored mask remain unchanged under this proposed cleaning. Baseline predictions and target-only controls may be reusable, but controls tied to selected model settings must be reconsidered if validation choices change. Final effect sizes/rankings are unknown until corrected fitting is complete. Evidence: `artifacts/phase4a/review_evidence.json`, `input_scaling_sensitivity.csv`, `neural_training_sample_impact.csv`.

## D11 — Keep review findings separate from author approval and manuscript edits

**Applied at Moazzam's request.** Phase 4A reviews evidence and decisions; Phase 4B creates a separate manuscript copy and writes the response only after the review concerns are resolved. This assistant review is a self-audit of work it helped produce, not independent external peer review or approval on Moazzam's behalf.

**Reason:** the authors need a clear, reviewable scientific basis before changing the manuscript. Every reviewer comment still needs its own response, even where the same experiment addresses multiple points.

**Current gate:** hold Phase 4B pending D10 and the reporting/reproduction follow-ups in [the critical review](reports/PHASE4A_CRITICAL_REVIEW.md). Literature assessment, manuscript equations/wording, final reproduction/DOI release and submission packaging remain explicit later tasks. No manuscript copy has been created by this review.
