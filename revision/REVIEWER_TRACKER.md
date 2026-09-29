# Reviewer revision tracker

Status: Strict-availability Phases 1/2 evidence is preserved. At Moazzam's request, coverage is being reconsidered before Phase 3: retain all 23 calendar origins, score only observed hours, and test explicit historical-context handling. See `reports/COVERAGE_RECONSIDERATION.md`. Phase 3 and manuscript/response edits remain pending.

## Phase 2 evidence log

| Reviewer points | Phase 2 action | Evidence | Current state |
|---|---|---|---|
| R1.5; R2.M5 | Bounded candidate screening on four training-only weeks, before selecting test configurations. | `artifacts/phase2/selection.json`; `validation_summary.csv`; `runs/validate_*/` | Complete: selected SARIMAX (1,0,1)x(1,0,1,24), additive Prophet, 50-epoch NeuralProphet. One validation candidate failed and was excluded. |
| R1.1; R1.4; R2.M4–M6 | Matched frozen/refitted core models and three NeuralProphet seeds; three persistence baselines. | `artifacts/phase2/verified_coverage.csv`; `experimental_summary.csv`; `baselines/` | All core streams cover 16 identical weeks / 2,688 hours. Five SARIMAX refits needed verified numerical recovery. |
| R2.M3; R2.M7 | Frozen no-input/broad-input ablation and train-only predictor-clipping sensitivity. | `artifacts/phase2/runs/ablate_*/`; `runs/recover_ablate_sarimax_clip/` | All nine extra tasks complete on the common mask. Clipped SARIMAX required numerical recovery. No target clipping/imputation. |
| R1.7; R2.M8 | No correction, predefined EWMA grid and previous-week residual mean. | `artifacts/phase2/corrections/`; `verification.json` | 35 streams complete; timing and exact-base-forecast identity verified. Mixed seed-specific correction effects require Phase 3 analysis. |
| R1.3; R1.6; R2.M10 | Model coefficients/components, training traces and local resource records. | `artifacts/phase2/runs/*/`; `supervisor.jsonl`; `recovery_supervisor.jsonl` | Evidence collected; interpretation, stability and fair runtime aggregation pending. Failed and rejected recovery attempts retained. |
| R1.8; R2.M9; R2.m6 | Reloadable descriptive summaries, full stream verification and executed revision notebook. | `reports/PHASE2_SUMMARY.md`; `PHASE2_VERIFICATION.md`; `main_revision.ipynb` | 94/94 accepted tasks, no unresolved failures or integrity errors; 14 tests pass; 21 original hashes unchanged. Paired uncertainty/publication outputs remain Phase 3. |

This log records implementation and evidence as they occur. It does not mark a comment closed until the manuscript and point-by-point response cite the actual result and limitation.

IDs: R1.n = Reviewer 1; R2.Mn = Reviewer 2 major; R2.mn = Reviewer 2 minor; E.n-style E1–E5 = editorial obligations. Reviewer quotations below preserve wording from the supplied decision letter; only list numbering/whitespace are normalized.

Workflow: Planned → In progress → Evidence ready → Manuscript updated → Response drafted → Verified. Use Blocked only with a named dependency. Evidence ready alone does not close a comment. Log every material action under its entry with artifact/commit, result and location; final page/line references are added after typesetting.

## Overview

| ID | Type | Phases | Experiment IDs | Status |
|---|---|---|---|---|
| R1.1 | Experiment + reporting | 2–5 | X2 | Evidence ready |
| R1.2 | Writing | 1, 4–5 | — | In progress |
| R1.3 | Analysis + writing | 2–4 | X2, X8 | In progress |
| R1.4 | Experiment + diagnosis + writing | 1–4 | X1, X2, X7, X8 | In progress |
| R1.5 | Experiment + writing | 1–4 | X1 | Evidence ready |
| R1.6 | Measurement + writing | 1–4 | X2 | In progress |
| R1.7 | Forecast reuse + analysis | 2–4 | X6 | In progress |
| R1.8 | Forecast reuse + statistics + figures | 3–5 | X8 | In progress |
| R1.9 | Writing | 4–5 | — | Planned |
| R1.10 | Data analysis + writing | 1, 3–4 | X8 | Evidence ready |
| R2.M1 | Writing + protocol | 1, 4–5 | — | In progress |
| R2.M2 | Data audit + reporting | 1, 3–5 | X8 | In progress |
| R2.M3 | Experiment + data audit + reporting | 1–4 | X5, X8 | In progress |
| R2.M4 | Experiment + scope + reporting | 1–4 | X2, X3 | Evidence ready |
| R2.M5 | Validation + correctness + repeated experiments | 1–4 | X1, X2, X7 | In progress |
| R2.M6 | Protocol + implementation checks + writing | 1–4 | X2 | Evidence ready |
| R2.M7 | Feature audit + ablation + writing | 1–4 | X4 | In progress |
| R2.M8 | Forecast reuse + diagnostics + writing | 2–4 | X6, X8 | In progress |
| R2.M9 | Forecast reuse + statistics + reporting | 3–5 | X8 | In progress |
| R2.M10 | Model analysis + resource measurement + writing | 1–4 | X2, X8 | In progress |
| R2.M11 | Literature assessment + writing | 4–5 | — | Planned |
| R2.m1 | Writing + formula verification | 4–5 | — | Planned |
| R2.m2 | Writing | 4–5 | — | Planned |
| R2.m3 | Writing | 4–5 | — | Planned |
| R2.m4 | Forecast reuse + figures | 3–5 | X8 | Planned |
| R2.m5 | Generated arithmetic + writing | 3–5 | X8 | Planned |
| R2.m6 | Reproducibility + packaging | 1–5 | X1–X8 | In progress |
| E1 | Evidence-based writing and consistency audit | 3–5 | — | In progress |
| E2 | Comment coverage | 1–5 | — | In progress |
| E3 | Writing | 4–5 | — | Planned |
| E4 | Versioned DOI release | 4–5 | — | Planned |
| E5 | Submission package | 4–5 | — | Planned |

## Reviewer comments and closure records

### R1.1

> The SARIMAX walk-forward run stops at week 21 of 23 because increasing memory usage prevented completion in the available computing environment, yet the abstract, Results and Discussion often present it alongside the two fully completed models (Prophet, NeuralProphet) without flagging this difference. Please state explicitly, wherever SARIMAX walk-forward performance is mentioned, that the reported MAE/RMSE are cumulative over 21 of 23 weeks, and avoid phrasing that implies a like-for-like comparison with the complete runs. This is not a fatal flaw, but as written it could mislead readers about the comparability of the three models under this regime.

- **Type / phase:** Experiment + reporting; 2–5.
- **Shared work:** X2.
- **Dependencies / overlap:** R2.M4; matched coverage before rankings.
- **Planned action / closure evidence:** Complete-run or failure log, matched-period comparison, coverage labels in every relevant passage.
- **Status:** Evidence ready
- **Changes performed:** All three families and both updating regimes now cover the same 16 eligible calendar weeks / 2,688 observed hours. Five nonconverged SARIMAX weekly refits were recovered with the selected orders and original cutoffs; original failures, numerical amendment and recovery effort are retained. The revised mask excludes unavailable weeks and the incomplete terminal window; revised counts do not equal the submitted 23-week row-based evaluation.
- **Evidence/artifacts:** reports/PHASE2_VERIFICATION.md; artifacts/phase2/verified_coverage.csv; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.2

> The Perfect Prognosis setting is used as an experimental simplification, with future values of the exogenous gases (NO, NO₂, CO, SO₂) supplied from the held-out test segment. In real deployment, these values would not normally be available as "observations" at the time of forecasting. Please add a short paragraph clarifying when this assumption reasonably approximates practice and when it remains an idealisation, so readers can properly calibrate the operational claims in the abstract and conclusion.

- **Type / phase:** Writing; 1, 4–5.
- **Shared work:** —.
- **Dependencies / overlap:** R2.M1; agreed PP scope.
- **Planned action / closure evidence:** PP information-set paragraph and calibrated Abstract/Conclusion; no unsupported operational claims.
- **Status:** In progress.
- **Changes performed:** Perfect Prognosis scope and forecast information sets are documented; manuscript claim changes remain Phase 4 work.
- **Evidence/artifacts:** reports/EXPERIMENTAL_PROTOCOL.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.3

> Interpretability claims. The manuscript repeatedly calls Prophet and SARIMAX "interpretable," but does not show what the exogenous drivers (NO, NO₂, CO, SO₂) actually contribute inside the fitted models. If available from the fitted models, please report, even briefly, the SARIMAX β coefficients and/or Prophet regressor effect sizes; otherwise, please moderate the interpretability claim. If estimates are reported, specify the relevant fitted model or aggregation procedure.

- **Type / phase:** Analysis + writing; 2–4.
- **Shared work:** X2, X8.
- **Dependencies / overlap:** R2.M10; valid fitted models.
- **Planned action / closure evidence:** Identified-fit coefficients/components, units/scaling, stability discussion and noncausal caveats.
- **Status:** In progress
- **Changes performed:** SARIMAX parameters and train-only input scaling, Prophet gas coefficients and all-week trend/seasonality/regressor components have been saved for frozen and refitted models. Interpretation, stability analysis and manuscript claims remain Phase 3/4 work.
- **Evidence/artifacts:** artifacts/phase2/runs/core_*/metadata.json; artifacts/phase2/runs/core_prophet_*/components_w*.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.4

> NeuralProphet's performance deserves a fuller explanation. Please expand this briefly with a diagnosis of possible causes, clearly distinguishing documented results from tentative explanations.

- **Type / phase:** Experiment + diagnosis + writing; 1–4.
- **Shared work:** X1, X2, X7, X8.
- **Dependencies / overlap:** R2.M5; alignment and convergence checks first.
- **Planned action / closure evidence:** Horizon-extraction check, convergence/normalization records, seeded results and evidence-based diagnosis.
- **Status:** In progress
- **Changes performed:** Corrected single-origin 168-lead NeuralProphet forecasts completed both regimes for seeds 42, 123 and 2026 on 16 matched weeks. Fifty training epochs were selected using training-only validation. Training traces, continuous-episode boundaries and normalization are saved. Comparative diagnosis and interpretation remain pending; no claim of inherent weakness is retained from the old experiment.
- **Evidence/artifacts:** artifacts/phase2/runs/core_neuralprophet_*/; artifacts/phase2/experimental_summary.csv; artifacts/phase2/verification.json.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.5

> SARIMAX order selection. The order (1,1,1) and seasonal order (1,1,1,24) are stated in 4.3.1 but the manuscript does not indicate how they were chosen criterion search or fixed a priori from the known 24-hour cycle. Please clarify the selection procedure, since this affects how the SARIMAX–Prophet comparison should be read.

- **Type / phase:** Experiment + writing; 1–4.
- **Shared work:** X1.
- **Dependencies / overlap:** R2.M5 strengthens a selection-method clarification.
- **Planned action / closure evidence:** Training-only validation results and explicit original-versus-revised SARIMAX order-selection account.
- **Status:** Evidence ready
- **Changes performed:** The bounded training-only search has completed: four SARIMAX orders, additive/multiplicative Prophet and 30/50 NeuralProphet epochs. Settings were locked before held-out evaluation: SARIMAX (1,0,1)x(1,0,1,24), additive Prophet and 50 epochs. One nonconverged SARIMAX validation candidate was excluded without scoring; final-comparison numerical recoveries do not reopen selection. This is a four-week fixed-parameter validation proxy rather than exhaustive tuning.
- **Evidence/artifacts:** artifacts/phase2/selection.json; artifacts/phase2/validation_summary.csv; artifacts/phase2/runs/validate_*/; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.6

> It is not stated whether SARIMAX (statsmodels) and Prophet also ran with any hardware acceleration. Since these are typically CPU-bound implementations, please confirm the computing setup used for each model, so that the reported execution-time differences (Tables 2–3) can be attributed to the models themselves rather than partly to the hardware.

- **Type / phase:** Measurement + writing; 1–4.
- **Shared work:** X2.
- **Dependencies / overlap:** R2.M10; controlled machine and timing scope.
- **Planned action / closure evidence:** Per-model actual acceleration, CPU/RAM/software inventory, timing definitions and measured breakdown.
- **Status:** In progress
- **Changes performed:** Full local experiment and recovery supervisor records, per-fit timing, prediction/state-update timing, sampled peak RSS, software versions and two-thread CPU configuration have been saved. Shared initial fits, failed attempts, rejected recovery attempts and successful recoveries are explicitly identified. Phase 3 must produce comparable totals and explain differing fit-timer boundaries.
- **Evidence/artifacts:** artifacts/phase2/supervisor.jsonl; artifacts/phase2/recovery_supervisor.jsonl; artifacts/phase2/runs/*/metadata.json; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.7

> Sensitivity of the residual-correction mechanism. The EWMA bias correction uses a fixed smoothing factor (α = 0.3) throughout the manuscript. Please state whether nearby values of α were tried and, if so, whether they produced qualitatively similar conclusions. If not, acknowledge the absence of this sensitivity analysis as a limitation.

- **Type / phase:** Forecast reuse + analysis; 2–4.
- **Shared work:** X6.
- **Dependencies / overlap:** R2.M8 requires more than acknowledging missing sensitivity.
- **Planned action / closure evidence:** All predefined alpha results, fixed primary alpha justification, and previous-week residual comparator.
- **Status:** In progress
- **Changes performed:** All five frozen core forecast streams have no correction and alpha 0.1/0.2/0.3/0.5/0.7/1.0 replays, giving 35 complete matched streams. Verification confirms the bias is applied before current outcomes update it, and each replay retains its exact base forecasts. Alpha 0.3 stays predefined; no test-optimal alpha is selected. Descriptive benefits vary across NeuralProphet seeds. Residual-bias diagnostics and paired uncertainty remain Phase 3 work.
- **Evidence/artifacts:** artifacts/phase2/corrections/*.csv; artifacts/phase2/corrections/summary.csv; artifacts/phase2/verification.json; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.8

> Figure 1 lists "MAE, RMSE (Mean ± Std)" as part of the evaluation protocol, but Tables 2 and 3 report only the mean MAE/RMSE, with no accompanying measure of dispersion across the 23 weekly windows. Given that week-level MAE varies considerably for every model, please report the standard deviation or interquartile range of the weekly errors alongside each mean, so that comparisons between models — such as the corrected SARIMAX vs. Prophet result in Table 3 — can be assessed against this variability rather than as single point estimates. A paired comparison across the matched weekly windows would also help support the model ranking.

- **Type / phase:** Forecast reuse + statistics + figures; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R2.M9; R2.m4; aligned saved predictions.
- **Planned action / closure evidence:** Mean weekly metrics with dispersion, separately labeled pooled errors, and dependence-aware paired intervals.
- **Status:** In progress
- **Changes performed:** Reloadable descriptive summaries now include mean weekly MAE/RMSE, their sample standard deviations, pooled MAE/RMSE, coverage and seed. Publication tables/figures and uncertainty interpretation remain Phase 3 work.
- **Evidence/artifacts:** artifacts/phase2/experimental_summary.csv; artifacts/phase2/baseline_summary.csv; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.9

> Manuscript length and density. At its current length, the manuscript is considerably longer than the journal's suggested format, and this affects readability. The Related Work section in particular could be shortened substantially without losing its core message. Similarly, the Discussion, Limitations and Conclusion sections partly repeat the same points and could be consolidated into fewer, more tightly written paragraphs.

- **Type / phase:** Writing; 4–5.
- **Shared work:** —.
- **Dependencies / overlap:** R2.M11; concise critical positioning.
- **Planned action / closure evidence:** Shorter Related Work, reduced repetition, and checked final length without inventing a journal word limit.
- **Status:** Planned.
- **Changes performed:** None.
- **Evidence/artifacts:** Pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R1.10

> Descriptive information on the PM2.5 series: Consider adding a brief descriptive summary of the PM2.5 series, including the mean and a clearly defined measure of range or variability, so that readers unfamiliar with Beijing's pollution levels can judge the practical magnitude of the reported MAE/RMSE values.

- **Type / phase:** Data analysis + writing; 1, 3–4.
- **Shared work:** X8.
- **Dependencies / overlap:** R2.M2–M3; original observed target.
- **Planned action / closure evidence:** Training/test descriptive table with counts, mean, SD, quantiles and original-scale range.
- **Status:** Evidence ready.
- **Changes performed:** Original-target descriptive statistics saved separately for training/test; manuscript insertion remains pending.
- **Evidence/artifacts:** artifacts/phase1/data_audit.json.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M1

> Forecasting assumptions and operational relevance
> Sections 3–4 explicitly assume that the actual future values of NO, NO2, CO, and SO2 are available throughout each 168-hour forecast window. This is a legitimate Perfect Prognosis experiment, but it does not establish performance under realistic operational conditions. The authors should either add an experiment using predictors available at the forecast origin or consistently restrict their claims to the Perfect Prognosis setting. The Abstract and Conclusion currently overstate readiness for real-world deployment.

- **Type / phase:** Writing + protocol; 1, 4–5.
- **Shared work:** —.
- **Dependencies / overlap:** R1.2; PP-only route chosen by Moazzam.
- **Planned action / closure evidence:** Consistent PP framing, source of future covariates specified, deployment benefits framed as conditional.
- **Status:** In progress.
- **Changes performed:** Agreed PP-only revision route encoded consistently in protocol. No operational scenario added; final written claims remain pending.
- **Evidence/artifacts:** reports/EXPERIMENTAL_PROTOCOL.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M2

> Dataset provenance and evaluation coverage
> Please report the geographic coordinates, specific API endpoints, retrieval dates, time zone, exact date boundaries, and total observation counts. Provide the training and test dates, the number of evaluated hours, and the handling of any incomplete final weekly window. Because the target comprises model-based gridded estimates rather than direct station measurements, this distinction and its implications for validation should be emphasized. The approximately 23-week test period also limits conclusions about year-round performance.

- **Type / phase:** Data audit + reporting; 1, 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** Precedes all experiments; R1.10.
- **Planned action / closure evidence:** Provenance/coverage report, exact split and evaluated hours, incomplete-window handling, gridded-target and seasonal-coverage limitations.
- **Status:** In progress.
- **Changes performed:** Coordinates/endpoints, supported timestamp convention, exact calendar/split/coverage and provenance limits audited. Retrieval dates and archived response metadata unavailable; not invented.
- **Evidence/artifacts:** reports/PHASE1_DATA_AUDIT.md; artifacts/phase1/provenance.json; artifacts/phase1/data_audit.json.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M3

> Winsorization and evaluation of pollution extremes
> Sections 3.1 and 4.1 describe percentile-based clipping, but it is unclear whether the held-out PM2.5 target was also clipped. Please specify which variables and data partitions were transformed. Performance should be reported against the original, unclipped test target, since high pollution concentrations may represent genuine events rather than measurement errors. A sensitivity analysis without winsorization would help establish whether the conclusions depend on suppressing extremes.

- **Type / phase:** Experiment + data audit + reporting; 1–4.
- **Shared work:** X5, X8.
- **Dependencies / overlap:** Original targets and gap policy before all scoring.
- **Planned action / closure evidence:** Raw-target primary metrics, explicit transformation table, predictor-clipping sensitivity and high-concentration analysis.
- **Status:** In progress
- **Changes performed:** All three frozen families completed predictor-only clipping at training-derived 1st/99th percentiles, with the original target retained for fitting/scoring. The clipped SARIMAX fit required a separately documented numerical recovery. Each control covers the same 16 weeks / 2,688 hours as its unclipped reference. Distribution plots, extreme-episode diagnostics and manuscript interpretation remain pending.
- **Evidence/artifacts:** artifacts/phase2/runs/ablate_*_clip/; artifacts/phase2/runs/recover_ablate_sarimax_clip/; artifacts/phase2/experimental_summary.csv; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M4

> Benchmark adequacy and fair comparison
> Include persistence and seasonal-persistence baselines to demonstrate forecasting skill beyond simple reference methods. Claims of competitiveness against more advanced approaches should either be supported by an appropriate additional comparator under the same protocol or narrowed to the three evaluated model families. Furthermore, Table 2 compares SARIMAX over 21 weeks with the other models over 23 weeks. Please provide a common-period comparison for all models and, if possible, complete the SARIMAX evaluation.

- **Type / phase:** Experiment + scope + reporting; 1–4.
- **Shared work:** X2, X3.
- **Dependencies / overlap:** R1.1; scope excludes unsupported advanced-model superiority.
- **Planned action / closure evidence:** Three persistence references, shared-period table, full SARIMAX attempt or documented failure, narrowed competitiveness claims.
- **Status:** Evidence ready
- **Changes performed:** Persistence, daily seasonal persistence and weekly seasonal persistence, plus all core models/regimes, now cover the same 16 eligible weeks / 2,688 hours. Exact coverage, five weekly SARIMAX numerical recoveries and excluded calendar windows are recorded. Matched point estimates are saved; publication comparisons and PP scope wording remain pending.
- **Evidence/artifacts:** artifacts/phase2/baselines/*.csv; artifacts/phase2/experimental_summary.csv; artifacts/phase2/verified_coverage.csv; reports/PHASE2_VERIFICATION.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M5

> Model selection and NeuralProphet performance
> Please justify the SARIMAX orders, Prophet configuration, and NeuralProphet training settings using a time-ordered validation procedure within the training data. The unusually large NeuralProphet errors warrant checks of training convergence, normalization, forecast–target alignment, and the extraction of its 168-step predictions. Report repeated runs with different seeds where relevant. The present results should not be interpreted as demonstrating an inherent weakness of NeuralProphet without these checks.

- **Type / phase:** Validation + correctness + repeated experiments; 1–4.
- **Shared work:** X1, X2, X7.
- **Dependencies / overlap:** R1.4–R1.5; must precede interpretation.
- **Planned action / closure evidence:** Chronological candidate-selection table, validity checks, convergence records, and repeated-seed results.
- **Status:** In progress
- **Changes performed:** Bounded training-only selection, correctly scaled single-origin 168-step forecasting and three-seed NeuralProphet repeats have completed. All 94 core/ablation tasks have accepted evidence; six SARIMAX numerical recoveries preserve selected settings/cutoffs and original failure records. Fourteen scientific-contract tests and full saved-stream verification pass. Training diagnostics and seed analysis remain Phase 3 work.
- **Evidence/artifacts:** tests/test_phase2.py; artifacts/phase2/selection.json; artifacts/phase2/runs/*/training_trace.csv; artifacts/phase2/verification.json; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M6

> Frozen-model forecasting protocol
> Clarify whether “frozen” means fixed parameters only or also a fixed internal model state. For each weekly forecast origin, specify whether SARIMAX incorporates newly observed target values through state updating and whether NeuralProphet receives the latest 168 observed target values. Provide concise pseudocode showing the information available to each model and when residual correction is applied. This distinction is essential for reproducibility and fair comparison.

- **Type / phase:** Protocol + implementation checks + writing; 1–4.
- **Shared work:** X2.
- **Dependencies / overlap:** R2.M5; state and context behavior precedes core runs.
- **Planned action / closure evidence:** Per-model fixed-parameter/refreshed-history definition, pseudocode and checks that current-week targets are unavailable.
- **Status:** Evidence ready
- **Changes performed:** Both regimes now have complete matched forecast streams for every family/seed. Frozen SARIMAX states refresh through newly revealed calendar history without parameter refitting, Prophet uses current target timestamps, and NeuralProphet receives only the latest eligible observed context plus PP future covariates. Saved origins/leads/masks and tests verify information-set and alignment contracts. Manuscript pseudocode and explanation remain pending.
- **Evidence/artifacts:** code/phase2_models.py; code/protocol.py; tests/test_phase2.py; artifacts/phase2/verification.json; artifacts/phase2/runs/core_*/forecasts.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M7

> Feature-selection procedure
> Report the correlation and mutual-information rankings, mRMR configuration, any discretization, and the rule used to select four predictors. The exclusion of PM10 because it is strongly associated with the target requires clearer justification: relevance to the target is not the same as redundancy among predictors. An ablation comparing the selected subset with a broader predictor set and a model without exogenous inputs would clarify the value of feature selection.

- **Type / phase:** Feature audit + ablation + writing; 1–4.
- **Shared work:** X4.
- **Dependencies / overlap:** R2.M2; mRMR target/configuration checks.
- **Planned action / closure evidence:** Training-only rankings and selection account, mRMR details or explicit correction of unsupported claims, no/selected/broad-input ablation.
- **Status:** In progress
- **Changes performed:** All three families completed no-input, predefined four-gas and broad-input frozen comparisons using selected settings and the exact common mask. Broad PP inputs include PM10 and therefore supply companion-particulate information; they are not operational covariate forecasts. These are controlled fixed-setting ablations, not independently tuned configurations. Interpretation and manuscript edits remain pending.
- **Evidence/artifacts:** artifacts/phase2/runs/ablate_*_no_inputs/; artifacts/phase2/runs/ablate_*_broad/; artifacts/phase2/experimental_summary.csv; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M8

> Residual correction and sensitivity analysis
> The fixed EWMA smoothing parameter, α = 0.3, requires justification. Please provide a sensitivity analysis or select this parameter using historical validation data only. Comparison with a simple previous-week mean-residual correction would help establish the benefit of exponential smoothing. The authors should also explain why correction improves Prophet and SARIMAX but worsens NeuralProphet, using residual-bias patterns rather than speculation. EWMA correction should be positioned as an established technique applied within this evaluation, unless a distinct methodological innovation is demonstrated.

- **Type / phase:** Forecast reuse + diagnostics + writing; 2–4.
- **Shared work:** X6, X8.
- **Dependencies / overlap:** R1.7; residuals from valid base predictions.
- **Planned action / closure evidence:** Alpha sensitivity, alpha=1 comparator, residual-bias plots and established-method positioning.
- **Status:** In progress
- **Changes performed:** All five frozen core forecast streams have no correction and alpha 0.1/0.2/0.3/0.5/0.7/1.0 replays, giving 35 complete matched streams. Verification confirms the bias is applied before current outcomes update it, and each replay retains its exact base forecasts. Alpha 0.3 stays predefined; no test-optimal alpha is selected. Descriptive benefits vary across NeuralProphet seeds. Residual-bias diagnostics and paired uncertainty remain Phase 3 work.
- **Evidence/artifacts:** artifacts/phase2/corrections/*.csv; artifacts/phase2/corrections/summary.csv; artifacts/phase2/verification.json; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M9

> Performance aggregation and uncertainty
> Sections 3.5–3.6 describe averaging weekly metrics, whereas the tables label them as overall MAE and RMSE. Please distinguish mean weekly RMSE from pooled RMSE across all forecasted hours, as these are not equivalent. Report weekly error distributions and uncertainty around paired performance differences using an approach that respects temporal dependence. Also provide performance by forecast lead time, because an aggregate 168-hour score can conceal deterioration at longer horizons.

- **Type / phase:** Forecast reuse + statistics + reporting; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R1.8; exact timestamps and matched coverage.
- **Planned action / closure evidence:** Pooled versus weekly metric definitions, weekly distributions, paired block-bootstrap intervals and lead-time results.
- **Status:** In progress
- **Changes performed:** The summary CSV distinguishes pooled errors from means/sample standard deviations of weekly errors and includes exact windows/hours. Saved timestamped forecasts support paired comparisons and lead-time diagnostics; uncertainty and figures remain Phase 3 work.
- **Evidence/artifacts:** artifacts/phase2/experimental_summary.csv; artifacts/phase2/verified_coverage.csv; artifacts/phase2/runs/*/forecasts.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M10

> Interpretability and computational claims
> Interpretability is central to the title but is not demonstrated sufficiently through the reported results. Please present relevant model components, regressor effects, or other interpretable outputs and discuss their stability and limitations without treating associations as causal effects. For runtime comparisons, report CPU, system RAM, software versions, actual GPU use, and whether training, preprocessing, and prediction are included. The SARIMAX memory failure should be described as an observation in the specific implementation and environment rather than a general property of the model.

- **Type / phase:** Model analysis + resource measurement + writing; 1–4.
- **Shared work:** X2, X8.
- **Dependencies / overlap:** R1.3, R1.6; valid fits and comparable timing.
- **Planned action / closure evidence:** Model outputs with stability/noncausal limitations, complete hardware/software/timing description and implementation-specific failure report.
- **Status:** In progress
- **Changes performed:** SARIMAX coefficients/scaling and Prophet components/regressor effects have been saved across primary frozen fits and refits. Local hardware/software, actual CPU/no-GPU use, fitting/prediction/state-update timings and sampled RSS are recorded, including failed/recovered attempts. Stability, noncausal interpretation and fair computational aggregation remain Phase 3 work.
- **Evidence/artifacts:** artifacts/phase1/hardware.json; artifacts/phase1/environment.json; artifacts/phase2/runs/*/metadata.json; artifacts/phase2/runs/core_prophet_*/components_w*.csv; artifacts/phase2/supervisor.jsonl; artifacts/phase2/recovery_supervisor.jsonl.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.M11

> Recent literature and positioning
> The literature review should more clearly position this work against recent particulate-matter prediction research involving multi-station modelling, advanced temporal learning, attention mechanisms, feature optimization, interpretability, and distributed learning. Where directly relevant, the authors may consider the following suggested studies, or suitable alternatives: 10.1371/journal.pone.0330465, 10.1038/s41598-025-16664-4, 10.1109/ACCESS.2024.3509142, 10.1088/2631-8695/ae2826, and 10.1016/j.rineng.2026.111937.
> The purpose should be critical positioning, not merely expanding the reference list. Explain what the present comparison contributes regarding adaptation, computational cost, and interpretability, while distinguishing its single-city Perfect Prognosis setting from other forecasting protocols. Numerical results from different datasets should not be presented as directly comparable. These specific citations are optional and should be included only when substantively relevant.

- **Type / phase:** Literature assessment + writing; 4–5.
- **Shared work:** —.
- **Dependencies / overlap:** R1.9; preserve concision.
- **Planned action / closure evidence:** Verified relevant recent sources, contribution positioned against differing protocols, no cross-dataset numerical rankings.
- **Status:** Planned.
- **Changes performed:** None.
- **Evidence/artifacts:** Pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.m1

> Revise Equation (4) to accurately represent the implemented seasonal and non-seasonal differencing and multiplicative SARIMAX structure.

- **Type / phase:** Writing + formula verification; 4–5.
- **Shared work:** —.
- **Dependencies / overlap:** R2.M5; finalized SARIMAX specification.
- **Planned action / closure evidence:** Backshift equation matching actual differencing, seasonal/nonseasonal polynomials and regression treatment.
- **Status:** Planned.
- **Changes performed:** None.
- **Evidence/artifacts:** Pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.m2

> Equation (8) describes a “one-step residual,” although the evaluation uses 168-step forecasts. Please correct this terminology.

- **Type / phase:** Writing; 4–5.
- **Shared work:** —.
- **Dependencies / overlap:** R2.M6; finalized horizon notation.
- **Planned action / closure evidence:** Replace one-step wording with horizon-specific forecast residuals at the weekly origin.
- **Status:** Planned.
- **Changes performed:** None.
- **Evidence/artifacts:** Pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.m3

> Remove the statement that Kalman-filter implementation details are provided unless this alternative is actually described and evaluated.

- **Type / phase:** Writing; 4–5.
- **Shared work:** —.
- **Dependencies / overlap:** EWMA-only protocol.
- **Planned action / closure evidence:** Remove unimplemented Kalman alternative and its promised implementation details.
- **Status:** Planned.
- **Changes performed:** None.
- **Evidence/artifacts:** Pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.m4

> Supplement the best- and worst-week figures with a summary covering all evaluation weeks; these selected examples alone do not establish stability.

- **Type / phase:** Forecast reuse + figures; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R1.8; R2.M9.
- **Planned action / closure evidence:** All-week chronological error plot/distribution and appropriately labeled illustrative weeks.
- **Status:** Planned.
- **Changes performed:** None.
- **Evidence/artifacts:** Pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.m5

> Reconcile the reported Prophet MAE reduction of 7.93 with the displayed values, 45.61 − 37.67 = 7.94, or explain rounding from unrounded results.

- **Type / phase:** Generated arithmetic + writing; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R2.M9; revised metric values.
- **Planned action / closure evidence:** All differences generated from full precision, with consistent rounding and a note where rounded subtraction differs.
- **Status:** Planned.
- **Changes performed:** None.
- **Evidence/artifacts:** Pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

### R2.m6

> Provide a versioned code release, dependency specifications, seeds, data-processing instructions, and scripts reproducing each table and figure.

- **Type / phase:** Reproducibility + packaging; 1–5.
- **Shared work:** X1–X8.
- **Dependencies / overlap:** E4; final executable artifacts.
- **Planned action / closure evidence:** Versioned source, dependencies, seeds, data instructions, reproduction commands, smoke check and DOI-linked release.
- **Status:** In progress
- **Changes performed:** Isolated revision source, observed dependencies, configuration/seeds, checkpointed forecasts, training diagnostics, explicit numerical-recovery provenance and verification/summary commands are available. The revision notebook has saved executed audit/check/result outputs. Original hashes remain unchanged. Clean-environment reproduction, final table/figure scripts and the versioned DOI release remain pending.
- **Evidence/artifacts:** README.md; main_revision.ipynb; requirements-observed.txt; artifacts/phase2/verification.json; artifacts/phase2/verified_coverage.csv; reports/PHASE2_SUMMARY.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Pending results; do not assume the requested conclusion.

## Editorial obligations

### E1

> Please ensure the results are accurately reported, any overstated conclusions are rewritten and the limitations of the work fully explained.

- **Type / phase:** Evidence-based writing and consistency audit; 3–5.
- **Closure evidence:** Generated artifacts support all numbers; scope, coverage, limitations and changed findings are explicit.
- **Status:** In progress.
- **Changes performed:** Source/report discrepancies and unreproduced original claims documented. Final numerical results and evidence-based manuscript revision remain pending.
- **Evidence/artifacts:** reports/NOTEBOOK_MANUSCRIPT_DISCREPANCIES.md.
- **Manuscript location:** Pending.

### E2

> Revise the manuscript thoroughly, addressing each reviewer comment.

- **Type / phase:** Comment coverage; 1–5.
- **Closure evidence:** All 27 reviewer entries have individual responses and evidence or an explicit reasoned limitation.
- **Status:** In progress.
- **Changes performed:** All reviewer IDs retained; Phase 1 actions linked individually without marking experimental or manuscript requests prematurely complete.
- **Evidence/artifacts:** REVIEWER_TRACKER.md.
- **Manuscript location:** Pending.

### E3

> Improve clarity, structure, and language where necessary.

- **Type / phase:** Writing; 4–5.
- **Closure evidence:** Readability edit, compressed repetition and consistent terminology.
- **Status:** Planned.
- **Changes performed / evidence / manuscript location:** Pending.

### E4

> Please note that if your manuscript uses any custom or bespoke computational tool or code, or reports a new algorithm, tool, software, or a pipeline (even if individual components are not new), the underlying code must be deposited in a recognised DOI-assigning repository (e.g. zenodo) and linked either from Methods or a dedicated Code Availability section.

- **Type / phase:** Versioned DOI release; 4–5.
- **Closure evidence:** Published version-specific DOI linked from the manuscript and response, with reviewed reproducibility contents.
- **Status:** Planned.
- **Changes performed / evidence / manuscript location:** Pending.

### E5

> When your revision is ready, please submit the updated manuscript and a point-by-point response.

- **Type / phase:** Submission package; 4–5.
- **Closure evidence:** Checked manuscript and response PDFs; required supplementary files; October 6 deadline recorded. Submission remains an author action unless delegated.
- **Status:** Planned.
- **Changes performed / evidence / manuscript location:** Pending.

## Shared-work rules

- A shared experiment may close several comments, but retain an individual response for each.
- R2.M4 extends R1.1: incomplete-run labeling does not replace matched-period comparisons.
- R2.M8 extends R1.7: acknowledging missing sensitivity alone is insufficient for the stronger request.
- R2.M10 extends R1.3: moderating claims alone does not provide the model outputs requested by Reviewer 2.
- R2.M11 and R1.9 are compatible: critically position relevant recent work while shortening the review.
- All figures/tables must be regenerated from revised evidence before adding final response locations.
