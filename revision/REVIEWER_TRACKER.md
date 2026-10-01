# Reviewer revision tracker

**Phase 4B draft update, 1 October 2026:** Moazzam explicitly approved Phase 4A and manuscript writing. A separate highlighted revised v1 is prepared with corrected 23-week results and four author-supplied literature additions. See [the draft manuscript](manuscript/revised_v1/manuscript.pdf), [the point-by-point change ledger](manuscript/revised_v1_notes/CHANGE_LOG.md), and [pending author input](manuscript/revised_v1_notes/AUTHOR_INPUTS.md). Scientific text is drafted; data/code archive statements, the DOI release, response PDF and final verification remain pending. This update supersedes historical decision-pending/writing-hold statements below without deleting their audit history. No comment is closed merely because draft prose exists.

**Current corrected evidence, 1 October 2026:** all 120 main tasks and eight controls passed. One broad-input SARIMAX control failed both bounded fits and is declared unavailable; no failed-fit forecasts enter results. Corrected analyses, six figure pairs and the independent saved-evidence audit passed; 25 contract tests passed. [Fresh review](corrected/reports/PHASE4A_REVIEW.md), [individual evidence ledger](corrected/reports/REVIEWER_EVIDENCE.md), and [author decision](corrected/AUTHOR_DECISION.md). Moazzam’s decision is pending. Numerical statements and artifact links below refer to the preserved pre-correction history unless specifically marked as corrected.

**Critical review update, 2026-09-30: numerical clearance withdrawn; Phase 4B on hold.** Four invalid `-9999` pollutant input cells were found in training, including two in primary NO₂. Experiments genuinely completed, but affected validation, model fitting and downstream results need correction/re-evaluation. The original 23-origin / 3,624-hour test mask is unchanged by the proposed cleaning. Historical “Evidence ready” and completed-phase notes below record execution, not final scientific clearance. See [the critical review](reports/PHASE4A_CRITICAL_REVIEW.md), [pipeline](flow.md), and [decision record](decisions.md). No training or manuscript changes were made during the review.

| Review finding | Required follow-up | Main linked comments |
| --- | --- | --- |
| A1: invalid training inputs | Version the input-validity correction; repeat affected rankings/validation/fits/analysis; preserve previous evidence. | R1.3–R1.8; R2.M2–M5, M7–M10; all result-dependent claims; E1 |
| A2: mixed timing boundaries and reuse fields | Distinguish source computation, recovery and reuse; avoid unsupported runtime ratios. | R1.6; R2.M10 |
| A3: baseline finalization depends on checker | Make finalization unambiguous; the current saved last-observation baseline is correct. | R2.M4; R2.m6 |
| A4: component weighting, seed summary, figure scope | Label or recompute aggregation; add across-seed summary and select figures after corrected results. | R1.3–R1.4, R1.8; R2.M5, M9–M10; R2.m4–m6 |

Status: Phase 3 publication analysis is complete from the verified broader primary evaluation: 23 weekly origins / 3,624 observed hours (19 complete weeks and four partial weeks). The 16-week strict experiment remains a sensitivity reference. All 129 broader tasks, three baselines and 35 correction streams pass verification. Phase 3 tables, five PDF/PNG figures, paired intervals, model interpretation and resource accounting are in `reports/PHASE3_RESULTS.md` and `artifacts/phase3/`; 26 scientific-contract tests pass. Phase 4A author review is prepared in `PHASE4A_AUTHOR_REVIEW.md`. The submitted manuscript and point-by-point response remain unedited.

The [Phase 3 findings ledger](reports/PHASE3_FINDINGS_LEDGER.md) maps the new analysis evidence to individual reviewer points. Evidence alone does not close a comment.

## Broader coverage amendment before Phase 3

| Reviewer points | Action and result | Evidence |
|---|---|---|
| R1.1; R2.M2; R2.M4 | Retain 23 weekly calendar origins, score the same 3,624 original observed hours for all methods; label 19 complete/four partial weeks and the separate 163-hour remainder. | `artifacts/coverage_reconsideration/windows.csv`; `coverage.png`; `verification.json` |
| R1.4; R2.M5–M6 | Keep selected settings/fitting targets unchanged; handle dense inference history with a documented causal seasonal fill; verify actual model placeholder invariance and strict-week reproduction. All 129 tasks and 22 tests pass. | `config/coverage_reconsideration.json`; `runs/*/`; `preflight_checks.json`; `history_fill_validation.csv` |
| R2.M3; R2.M7 | Extend all frozen clipping and predictor controls to the same wider mask; preserve the strict reference. | `experimental_summary.csv`; `runs/ablate_*/` |
| R1.7; R2.M8 | Recompute 35 correction streams using each week's observed residual mean after outcomes; retain the old strict skip/carry policy as a separate sensitivity. | `corrections/`; `artifacts/phase2/corrections/` |
| R1.6; R1.8; R2.M9–M10; R2.m6 | Save pooled versus weekly metrics, 80 exact weekly-forecast reuses, 45 new fits/four SARIMAX reconstructions, resources and executed notebook/chart. The subsequent Phase 3 analysis is recorded below; writing remains pending. | `supervisor.jsonl`; `main_revision.ipynb`; `reports/COVERAGE_RECONSIDERATION_RESULTS.md` |

## Phase 3 evidence log

| Reviewer points | Analysis performed | Evidence |
| --- | --- | --- |
| R1.1; R1.8; R2.M4; R2.M9; R2.m4 | Matched 23-origin metrics, pooled versus weekly aggregation, all-week variation, strict sensitivity and 11 predefined paired weekly contrasts with 2/3/4-week block intervals. | `artifacts/phase3/performance.csv`; `paired_contrasts.csv`; `strict_sensitivity.csv`; `figures/weekly_mae_chronology.pdf` |
| R1.7; R2.M8 | All predefined α alternatives, weekwise residual/bias/MAE changes, and correction timing isolated from fits. | `correction_alpha_summary.csv`; `correction_weekly.csv`; `correction_timing.csv`; `figures/correction_diagnostics.pdf` |
| R1.4; R1.10; R2.M3; R2.M5; R2.M7; R2.M9 | Three-seed NeuralProphet outcomes, original-target distributions, high-concentration subset, controlled ablations and exact lead-hour/day errors. | `target_descriptive.csv`; `high_concentration.csv`; `performance.csv`; `lead_hour.csv`; `forecast_day.csv` |
| R1.3; R1.6; R2.M10 | Fit-specific scaled/raw-input coefficients, Prophet contributions, local CPU/resource and attempted-run accounting. | `coefficients.csv`; `prophet_components.csv`; `core_timing.csv`; `resource_events.csv` |

## Strict Phase 2 evidence log

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
| R2.m4 | Forecast reuse + figures | 3–5 | X8 | Evidence ready |
| R2.m5 | Generated arithmetic + writing | 3–5 | X8 | Evidence ready |
| R2.m6 | Reproducibility + packaging | 1–5 | X1–X8 | In progress |
| E1 | Evidence-based writing and consistency audit | 3–5 | — | In progress |
| E2 | Comment coverage | 1–5 | — | In progress |
| E3 | Writing | 4–5 | — | Planned |
| E4 | Versioned DOI release | 4–5 | — | Planned |
| E5 | Submission package | 4–5 | — | Planned |

## Reviewer comments and closure records

### R1.1

**Corrected evidence update (1 October 2026): Evidence ready.** All 23 SARIMAX refit origins completed; all models use the common 3,624-hour mask. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Replace incomplete-run claims and report partial weeks.

> The SARIMAX walk-forward run stops at week 21 of 23 because increasing memory usage prevented completion in the available computing environment, yet the abstract, Results and Discussion often present it alongside the two fully completed models (Prophet, NeuralProphet) without flagging this difference. Please state explicitly, wherever SARIMAX walk-forward performance is mentioned, that the reported MAE/RMSE are cumulative over 21 of 23 weeks, and avoid phrasing that implies a like-for-like comparison with the complete runs. This is not a fatal flaw, but as written it could mislead readers about the comparability of the three models under this regime.

- **Type / phase:** Experiment + reporting; 2–5.
- **Shared work:** X2.
- **Dependencies / overlap:** R2.M4; matched coverage before rankings.
- **Planned action / closure evidence:** Complete-run or failure log, matched-period comparison, coverage labels in every relevant passage.
- **Status:** Evidence ready
- **Changes performed:** The broader primary comparison now retains all 23 calendar origins and uses the same 3,624 observed scoring hours for every family/regime/seed: 19 complete and four partial weeks. All SARIMAX refits are valid; five strict-run numerical recoveries and the additional-origin solver policy remain explicit. The original 16-week strict subset is preserved as sensitivity evidence. Partial weeks are labeled, and their missing hours are not scored.
- **Evidence/artifacts:** reports/COVERAGE_RECONSIDERATION_RESULTS.md; artifacts/coverage_reconsideration/windows.csv; artifacts/coverage_reconsideration/verification.json; artifacts/coverage_reconsideration/experimental_summary.csv; reports/PHASE2_VERIFICATION.md.
- **Critical review (2026-09-30):** A1: the 23-origin schedule/completed tasks are verified, but affected model fitting and final accuracy must be regenerated. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** 23-origin matched metrics and preserved 16-week sensitivity: artifacts/phase3/performance.csv; artifacts/phase3/strict_sensitivity.csv. Original manuscript 21/23 limitation is corrected in the revised experiment; writing remains pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R1.2

**Corrected evidence update (1 October 2026): Writing pending.** Perfect Prognosis scope and unavailable operational future gases are documented. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Qualify Abstract/Conclusion and deployment statements.

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
- **Limitations or deviation:** PP-only route agreed; manuscript/response claim boundaries remain to be written.

### R1.3

**Corrected evidence update (1 October 2026): Evidence ready.** SARIMAX and Prophet effects saved per fit; Prophet components weight scored hours. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Identify fit/aggregation; interpret correlated associations cautiously.

> Interpretability claims. The manuscript repeatedly calls Prophet and SARIMAX "interpretable," but does not show what the exogenous drivers (NO, NO₂, CO, SO₂) actually contribute inside the fitted models. If available from the fitted models, please report, even briefly, the SARIMAX β coefficients and/or Prophet regressor effect sizes; otherwise, please moderate the interpretability claim. If estimates are reported, specify the relevant fitted model or aggregation procedure.

- **Type / phase:** Analysis + writing; 2–4.
- **Shared work:** X2, X8.
- **Dependencies / overlap:** R2.M10; valid fitted models.
- **Planned action / closure evidence:** Identified-fit coefficients/components, units/scaling, stability discussion and noncausal caveats.
- **Status:** In progress
- **Changes performed:** SARIMAX parameters and train-only input scaling, Prophet gas coefficients and all-week trend/seasonality/regressor components have been saved for frozen and refitted models. Interpretation, stability analysis and manuscript claims remain Phase 3/4 work.
- **Evidence/artifacts:** artifacts/phase2/runs/core_*/metadata.json; artifacts/phase2/runs/core_prophet_*/components_w*.csv.
- **Critical review (2026-09-30):** A1/A4: refit affected models and qualify component weighting before citing effects or refit stability. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Frozen and 23-refit SARIMAX/Prophet coefficient scales and frozen Prophet components: artifacts/phase3/coefficients.csv; artifacts/phase3/prophet_components.csv. Interpretation remains conditional/noncausal.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R1.4

**Corrected evidence update (1 October 2026): Evidence ready.** Corrected episodes, timestamp contracts, raw forecast extraction and three seeds audited. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Explain seed-dependent outcomes without asserting inherent model weakness.

> NeuralProphet's performance deserves a fuller explanation. Please expand this briefly with a diagnosis of possible causes, clearly distinguishing documented results from tentative explanations.

- **Type / phase:** Experiment + diagnosis + writing; 1–4.
- **Shared work:** X1, X2, X7, X8.
- **Dependencies / overlap:** R2.M5; alignment and convergence checks first.
- **Planned action / closure evidence:** Horizon-extraction check, convergence/normalization records, seeded results and evidence-based diagnosis.
- **Status:** In progress
- **Changes performed:** Corrected 168-step NeuralProphet forecasts now cover all 23 origins for seeds 42, 123 and 2026 in both regimes, using 3,624 original observed scoring hours. Fifty epochs remain training-validation-selected; fitting targets are never filled. Missing inference history is filled with an explicit causal seasonal rule, with counts and training-only reconstruction limitations recorded. Frozen strict-week forecasts reproduce their preserved reference. Diagnostics and manuscript interpretation remain Phase 3/4 work.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/runs/core_neuralprophet_*/; artifacts/coverage_reconsideration/history_fill_validation.csv; artifacts/coverage_reconsideration/verification.json; reports/COVERAGE_RECONSIDERATION_RESULTS.md.
- **Critical review (2026-09-30):** A1/A4: invalid inputs affect NeuralProphet training windows; regenerate seed results and add the planned across-seed summary. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** NeuralProphet three-seed weekly/pooled results and lead patterns: artifacts/phase3/performance.csv; artifacts/phase3/lead_hour.csv. Seed-specific high-concentration result weakens blanket rankings.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R1.5

**Corrected evidence update (1 October 2026): Evidence ready.** Eight bounded validation candidates attempted; seven succeeded; selection unchanged. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Report selected settings and failed candidate; acknowledge limited search.

> SARIMAX order selection. The order (1,1,1) and seasonal order (1,1,1,24) are stated in 4.3.1 but the manuscript does not indicate how they were chosen criterion search or fixed a priori from the known 24-hour cycle. Please clarify the selection procedure, since this affects how the SARIMAX–Prophet comparison should be read.

- **Type / phase:** Experiment + writing; 1–4.
- **Shared work:** X1.
- **Dependencies / overlap:** R2.M5 strengthens a selection-method clarification.
- **Planned action / closure evidence:** Training-only validation results and explicit original-versus-revised SARIMAX order-selection account.
- **Status:** Evidence ready
- **Changes performed:** The bounded training-only search has completed: four SARIMAX orders, additive/multiplicative Prophet and 30/50 NeuralProphet epochs. Settings were locked before held-out evaluation: SARIMAX (1,0,1)x(1,0,1,24), additive Prophet and 50 epochs. One nonconverged SARIMAX validation candidate was excluded without scoring; final-comparison numerical recoveries do not reopen selection. This is a four-week fixed-parameter validation proxy rather than exhaustive tuning.
- **Evidence/artifacts:** artifacts/phase2/selection.json; artifacts/phase2/validation_summary.csv; artifacts/phase2/runs/validate_*/; reports/PHASE2_SUMMARY.md.
- **Critical review (2026-09-30):** A1: invalid inputs occur before validation fitting; repeat training-only selection before presenting final orders. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Protocol/experiment evidence is available; manuscript/response wording remains pending.

### R1.6

**Corrected evidence update (1 October 2026): Evidence ready.** Hardware/software, timer boundaries, actual attempts and source prediction costs saved. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Narrow speed claims; distinguish optimization, initialization and reuse.

> It is not stated whether SARIMAX (statsmodels) and Prophet also ran with any hardware acceleration. Since these are typically CPU-bound implementations, please confirm the computing setup used for each model, so that the reported execution-time differences (Tables 2–3) can be attributed to the models themselves rather than partly to the hardware.

- **Type / phase:** Measurement + writing; 1–4.
- **Shared work:** X2.
- **Dependencies / overlap:** R2.M10; controlled machine and timing scope.
- **Planned action / closure evidence:** Per-model actual acceleration, CPU/RAM/software inventory, timing definitions and measured breakdown.
- **Status:** In progress
- **Changes performed:** Strict and broader resource records distinguish original fitting, failed/recovered attempts, new weekly fitting, frozen-state reconstruction, same-configuration frozen refitting, exact forecast reuse and placeholder checks. Eighty strict walk-forward forecasts are reused with source provenance; the broader matrix has 45 newly executed fits and four frozen SARIMAX reconstructions. Phase 3 must aggregate these costs without double-counting source fits and explain fit-timer boundaries.
- **Evidence/artifacts:** artifacts/phase2/supervisor.jsonl; artifacts/phase2/recovery_supervisor.jsonl; artifacts/coverage_reconsideration/supervisor.jsonl; artifacts/coverage_reconsideration/runs/*/metadata.json.
- **Critical review (2026-09-30):** A2: source-fit/recovery timer boundaries differ; source prediction cost and memory must not be replaced by reuse-task zeros. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** CPU-only local fit/forecast/state-update and supervisor resource evidence: artifacts/phase3/core_timing.csv; artifacts/phase3/resource_events.csv; artifacts/phase3/correction_timing.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R1.7

**Corrected evidence update (1 October 2026): Evidence ready.** Predefined alpha grid replayed causally; seed-dependent correction benefits quantified. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Explain why alpha remains 0.3; report sensitivity rather than test-optimal tuning.

> Sensitivity of the residual-correction mechanism. The EWMA bias correction uses a fixed smoothing factor (α = 0.3) throughout the manuscript. Please state whether nearby values of α were tried and, if so, whether they produced qualitatively similar conclusions. If not, acknowledge the absence of this sensitivity analysis as a limitation.

- **Type / phase:** Forecast reuse + analysis; 2–4.
- **Shared work:** X6.
- **Dependencies / overlap:** R2.M8 requires more than acknowledging missing sensitivity.
- **Planned action / closure evidence:** All predefined alpha results, fixed primary alpha justification, and previous-week residual comparator.
- **Status:** In progress
- **Changes performed:** Five broader frozen core streams have no correction plus the predefined alpha grid, giving 35 verified streams across all 23 origins. Bias is applied before current outcomes; each week updates from its observed-hour base residual mean after the forecast horizon. Alpha 0.3 stays predefined. The preserved strict sensitivity retains its original skip/carry policy, so subset correction values can differ even when base forecasts agree. Paired/residual diagnostics and writing remain pending.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/corrections/*.csv; artifacts/coverage_reconsideration/corrections/summary.csv; artifacts/phase2/corrections/; reports/COVERAGE_RECONSIDERATION_RESULTS.md.
- **Critical review (2026-09-30):** A1: regenerate causal alpha replays from corrected base forecasts; the fixed alpha policy remains unchanged. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Predefined alpha grid, previous-week residual comparator, weekwise diagnostics and paired differences: artifacts/phase3/correction_alpha_summary.csv; artifacts/phase3/correction_weekly.csv; artifacts/phase3/paired_contrasts.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R1.8

**Corrected evidence update (1 October 2026): Evidence ready.** Matched weekly errors, descriptive block intervals and all-week figures regenerated. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Define pooled versus weekly aggregation and uncertainty limits.

> Figure 1 lists "MAE, RMSE (Mean ± Std)" as part of the evaluation protocol, but Tables 2 and 3 report only the mean MAE/RMSE, with no accompanying measure of dispersion across the 23 weekly windows. Given that week-level MAE varies considerably for every model, please report the standard deviation or interquartile range of the weekly errors alongside each mean, so that comparisons between models — such as the corrected SARIMAX vs. Prophet result in Table 3 — can be assessed against this variability rather than as single point estimates. A paired comparison across the matched weekly windows would also help support the model ranking.

- **Type / phase:** Forecast reuse + statistics + figures; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R2.M9; R2.m4; aligned saved predictions.
- **Planned action / closure evidence:** Mean weekly metrics with dispersion, separately labeled pooled errors, and dependence-aware paired intervals.
- **Status:** In progress
- **Changes performed:** Strict and broader descriptive summaries include weekly MAE/RMSE means/sample SD and pooled hourly metrics. In the broader 23-origin evaluation, partial-week counts differ, so mean weekly MAE and pooled MAE must not be equated. Publication tables/plots and paired uncertainty remain Phase 3 work.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/experimental_summary.csv; artifacts/coverage_reconsideration/baseline_summary.csv; artifacts/phase2/experimental_summary.csv.
- **Critical review (2026-09-30):** A1/A4: recompute matched errors/intervals after corrected fitting, keeping weekly and pooled weighting explicit. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Pooled versus weekly mean/SD and 2/3/4-week paired-block intervals: artifacts/phase3/performance.csv; artifacts/phase3/paired_contrasts.csv; artifacts/phase3/figures/weekly_mae_distribution.pdf.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R1.9

**Corrected evidence update (1 October 2026): Writing pending.** Experimental package supports a shorter focused narrative. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Condense literature and remove repetitive claims.

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
- **Limitations or deviation:** Writing action remains pending; do not mark this reviewer point closed before the manuscript and response are checked.

### R1.10

**Corrected evidence update (1 October 2026): Evidence ready.** Original-target train/test distributions and high-event subsets are saved. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Add concise descriptive statistics with units and source limitations.

> Descriptive information on the PM2.5 series: Consider adding a brief descriptive summary of the PM2.5 series, including the mean and a clearly defined measure of range or variability, so that readers unfamiliar with Beijing's pollution levels can judge the practical magnitude of the reported MAE/RMSE values.

- **Type / phase:** Data analysis + writing; 1, 3–4.
- **Shared work:** X8.
- **Dependencies / overlap:** R2.M2–M3; original observed target.
- **Planned action / closure evidence:** Training/test descriptive table with counts, mean, SD, quantiles and original-scale range.
- **Status:** Evidence ready.
- **Changes performed:** Original-target descriptive statistics saved separately for training/test; manuscript insertion remains pending.
- **Evidence/artifacts:** artifacts/phase1/data_audit.json.
- **Phase 3 evidence:** Original observed training/test distributions: artifacts/phase3/target_descriptive.csv. Manuscript insertion pending.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M1

**Corrected evidence update (1 October 2026): Writing pending.** The information set is retrospective Perfect Prognosis. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Distinguish conditional forecasting from deployment.

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
- **Limitations or deviation:** PP-only route agreed; manuscript/response claim boundaries remain to be written.

### R2.M2

**Corrected evidence update (1 October 2026): Evidence with provenance limits.** Calendar gaps, invalid-input correction, source bytes and extraction limitations documented. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Disclose API estimates and missing original response/retrieval metadata.

> Dataset provenance and evaluation coverage
> Please report the geographic coordinates, specific API endpoints, retrieval dates, time zone, exact date boundaries, and total observation counts. Provide the training and test dates, the number of evaluated hours, and the handling of any incomplete final weekly window. Because the target comprises model-based gridded estimates rather than direct station measurements, this distinction and its implications for validation should be emphasized. The approximately 23-week test period also limits conclusions about year-round performance.

- **Type / phase:** Data audit + reporting; 1, 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** Precedes all experiments; R1.10.
- **Planned action / closure evidence:** Provenance/coverage report, exact split and evaluated hours, incomplete-window handling, gridded-target and seasonal-coverage limitations.
- **Status:** In progress
- **Changes performed:** The raw source, provenance limitations and reconstructed calendar remain documented. The wider evaluation retains 23 full calendar origins with 3,624 of 3,864 hours scored, including four partial weeks; the final 163-hour remainder is separately reported. Exact original observation masks, gap/context counts and a coverage plot are saved. No missing scoring targets are invented. Source retrieval/date/measurement limitations remain unresolved where historical evidence is absent.
- **Evidence/artifacts:** reports/PHASE1_DATA_AUDIT.md; artifacts/phase1/provenance.json; artifacts/coverage_reconsideration/windows.csv; artifacts/coverage_reconsideration/coverage.png; reports/COVERAGE_RECONSIDERATION_RESULTS.md.
- **Critical review (2026-09-30):** A1: document invalid numeric input codes in addition to absent timestamps; proposed correction leaves test coverage unchanged. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** 23-origin/3,624-hour matched primary evidence, strict 16-week sensitivity and original-target descriptions: artifacts/phase3/performance.csv; artifacts/phase3/strict_sensitivity.csv; artifacts/phase3/target_descriptive.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Historical retrieval dates and raw API responses are unavailable; report this honestly. Manuscript/response pending.

### R2.M3

**Corrected evidence update (1 October 2026): Evidence ready.** Original targets retained; train-only input clipping and high-event comparisons repeated. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Correct outlier-processing description and discuss extremes.

> Winsorization and evaluation of pollution extremes
> Sections 3.1 and 4.1 describe percentile-based clipping, but it is unclear whether the held-out PM2.5 target was also clipped. Please specify which variables and data partitions were transformed. Performance should be reported against the original, unclipped test target, since high pollution concentrations may represent genuine events rather than measurement errors. A sensitivity analysis without winsorization would help establish whether the conclusions depend on suppressing extremes.

- **Type / phase:** Experiment + data audit + reporting; 1–4.
- **Shared work:** X5, X8.
- **Dependencies / overlap:** Original targets and gap policy before all scoring.
- **Planned action / closure evidence:** Raw-target primary metrics, explicit transformation table, predictor-clipping sensitivity and high-concentration analysis.
- **Status:** In progress
- **Changes performed:** All three frozen predictor-clipping controls now cover the broader 23-origin schedule and identical 3,624 original observed targets. Training-derived predictor bounds remain fixed; fitting/scoring targets are unclipped and unfilled. The strict 16-week sensitivity is preserved and reproduced. Inference context filling is separately identified; distribution/extreme-event analysis and writing remain pending.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/runs/ablate_*_clip/; artifacts/coverage_reconsideration/experimental_summary.csv; artifacts/phase2/runs/; reports/COVERAGE_RECONSIDERATION_RESULTS.md.
- **Critical review (2026-09-30):** A1: correct invalid predictors, not valid target extremes; repeat affected clipping and high-concentration comparisons. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Training 95th-percentile threshold 691.335, 158 high hours in six weeks, and unclipped-target sensitivity: artifacts/phase3/high_concentration.csv; artifacts/phase3/high_concentration_by_week.csv; artifacts/phase3/performance.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M4

**Corrected evidence update (1 October 2026): Evidence ready.** Three baselines finalized; both regimes cover matching 23 origins and observed hours. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Disclose baseline information disadvantage and historical filling.

> Benchmark adequacy and fair comparison
> Include persistence and seasonal-persistence baselines to demonstrate forecasting skill beyond simple reference methods. Claims of competitiveness against more advanced approaches should either be supported by an appropriate additional comparator under the same protocol or narrowed to the three evaluated model families. Furthermore, Table 2 compares SARIMAX over 21 weeks with the other models over 23 weeks. Please provide a common-period comparison for all models and, if possible, complete the SARIMAX evaluation.

- **Type / phase:** Experiment + scope + reporting; 1–4.
- **Shared work:** X2, X3.
- **Dependencies / overlap:** R1.1; scope excludes unsupported advanced-model superiority.
- **Planned action / closure evidence:** Three persistence references, shared-period table, full SARIMAX attempt or documented failure, narrowed competitiveness claims.
- **Status:** Evidence ready
- **Changes performed:** All core methods/regimes/seeds and three persistence baselines share the broader 23-origin schedule and the exact 3,624-hour observed-only scoring mask. Nineteen weeks are fully observed; four have 120, 120, 48 and 144 scored hours. The original strict 16-week comparison remains a sensitivity reference. Missing history is handled explicitly for methods requiring dense context; partial weeks do not support full-week accuracy claims. Publication/PP-scope wording remains pending.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/baselines/*.csv; artifacts/coverage_reconsideration/experimental_summary.csv; artifacts/coverage_reconsideration/windows.csv; reports/COVERAGE_RECONSIDERATION_RESULTS.md.
- **Critical review (2026-09-30):** A1/A3: rerun affected models; preserve the verified saved persistence definition and make its finalization unambiguous. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** All three model families and persistence/daily/weekly persistence baselines share 23 origins and 3,624 scored hours: artifacts/phase3/performance.csv; artifacts/phase3/paired_contrasts.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M5

**Corrected evidence update (1 October 2026): Evidence ready.** Training-only validation, preprocessing, episodes, epochs and seed evidence checked. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Document bounded tuning and training choices; avoid optimality claims.

> Model selection and NeuralProphet performance
> Please justify the SARIMAX orders, Prophet configuration, and NeuralProphet training settings using a time-ordered validation procedure within the training data. The unusually large NeuralProphet errors warrant checks of training convergence, normalization, forecast–target alignment, and the extraction of its 168-step predictions. Report repeated runs with different seeds where relevant. The present results should not be interpreted as demonstrating an inherent weakness of NeuralProphet without these checks.

- **Type / phase:** Validation + correctness + repeated experiments; 1–4.
- **Shared work:** X1, X2, X7.
- **Dependencies / overlap:** R1.4–R1.5; must precede interpretation.
- **Planned action / closure evidence:** Chronological candidate-selection table, validity checks, convergence records, and repeated-seed results.
- **Status:** In progress
- **Changes performed:** Training-only configuration selection remains locked, and all 129 broader tasks have accepted evidence, including all three NeuralProphet seeds in both regimes. Same-configuration frozen refits reproduce their strict-week forecasts; additional SARIMAX fits use the recorded training-only numerical initialization policy. Twenty-two scientific-contract tests and complete broader evidence checks pass. Epoch traces, context-fill counts and seed analysis inputs are saved; diagnosis/writing remain pending.
- **Evidence/artifacts:** artifacts/phase2/selection.json; tests/test_coverage.py; artifacts/coverage_reconsideration/preflight_checks.json; artifacts/coverage_reconsideration/verification.json; artifacts/coverage_reconsideration/runs/*/training_trace.csv.
- **Critical review (2026-09-30):** A1/A4: revalidate and refit affected models; current finite-loss/alignment checks did not validate sentinel inputs. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Three NeuralProphet seeds and the selected SARIMAX/Prophet configurations evaluated with lead-time, weekly and high-event checks: artifacts/phase3/performance.csv; artifacts/phase3/forecast_day.csv; artifacts/phase3/high_concentration.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M6

**Corrected evidence update (1 October 2026): Method ready; writing pending.** Frozen state/context refresh and expanding refits are explicit and audited. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Add pipeline/pseudocode, horizons and causal missing-context policy.

> Frozen-model forecasting protocol
> Clarify whether “frozen” means fixed parameters only or also a fixed internal model state. For each weekly forecast origin, specify whether SARIMAX incorporates newly observed target values through state updating and whether NeuralProphet receives the latest 168 observed target values. Provide concise pseudocode showing the information available to each model and when residual correction is applied. This distinction is essential for reproducibility and fair comparison.

- **Type / phase:** Protocol + implementation checks + writing; 1–4.
- **Shared work:** X2.
- **Dependencies / overlap:** R2.M5; state and context behavior precedes core runs.
- **Planned action / closure evidence:** Per-model fixed-parameter/refreshed-history definition, pseudocode and checks that current-week targets are unavailable.
- **Status:** Evidence ready
- **Changes performed:** The broader protocol preserves selected configurations and fitting policies while retaining all 23 origins. SARIMAX refreshes native filtered state through observed/missing calendar history; Prophet predicts current timestamps; NeuralProphet receives only pre-origin history with explicit missing-context filling. Future targets never enter inference. Scored PP inputs are original observations; unavailable-input timestamps are unscored, and actual fitted-model perturbation checks confirm their computational placeholders do not affect scored predictions. Manuscript pseudocode remains pending.
- **Evidence/artifacts:** config/coverage_reconsideration.json; code/coverage_protocol.py; code/coverage_checks.py; tests/test_coverage.py; artifacts/coverage_reconsideration/verification.json.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Protocol/experiment evidence is available; manuscript/response wording remains pending.

### R2.M7

**Corrected evidence update (1 October 2026): Evidence partial; failure disclosed.** Corrected rankings/mRMR and eight controls exist; broad SARIMAX is unavailable. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Explain predefined four gases, future PM10 advantage and failed control; no optimal-subset claim.

> Feature-selection procedure
> Report the correlation and mutual-information rankings, mRMR configuration, any discretization, and the rule used to select four predictors. The exclusion of PM10 because it is strongly associated with the target requires clearer justification: relevance to the target is not the same as redundancy among predictors. An ablation comparing the selected subset with a broader predictor set and a model without exogenous inputs would clarify the value of feature selection.

- **Type / phase:** Feature audit + ablation + writing; 1–4.
- **Shared work:** X4.
- **Dependencies / overlap:** R2.M2; mRMR target/configuration checks.
- **Planned action / closure evidence:** Training-only rankings and selection account, mRMR details or explicit correction of unsupported claims, no/selected/broad-input ablation.
- **Status:** In progress
- **Changes performed:** No-input, four-gas and broad-input frozen comparisons now share all 23 origins and the common 3,624-hour mask. Settings stay fixed across controlled ablations. Broad PP inputs include PM10; their information advantage must be explicit. Strict-week forecasts reproduce preserved references. Feature interpretation and manuscript edits remain pending.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/runs/ablate_*_no_inputs/; artifacts/coverage_reconsideration/runs/ablate_*_broad/; artifacts/coverage_reconsideration/experimental_summary.csv.
- **Critical review (2026-09-30):** A1: repeat affected feature rankings and ablations; keep the four gases predefined. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Frozen no-input, selected-gas, broader-input and clipped-input comparisons: artifacts/phase3/performance.csv. Broad inputs include future PM10 and have an information advantage.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M8

**Corrected evidence update (1 October 2026): Evidence ready.** Correction residuals, alpha alternatives and timing are saved. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: State apply-before-observe/update-after-week mechanics and mixed benefits.

> Residual correction and sensitivity analysis
> The fixed EWMA smoothing parameter, α = 0.3, requires justification. Please provide a sensitivity analysis or select this parameter using historical validation data only. Comparison with a simple previous-week mean-residual correction would help establish the benefit of exponential smoothing. The authors should also explain why correction improves Prophet and SARIMAX but worsens NeuralProphet, using residual-bias patterns rather than speculation. EWMA correction should be positioned as an established technique applied within this evaluation, unless a distinct methodological innovation is demonstrated.

- **Type / phase:** Forecast reuse + diagnostics + writing; 2–4.
- **Shared work:** X6, X8.
- **Dependencies / overlap:** R1.7; residuals from valid base predictions.
- **Planned action / closure evidence:** Alpha sensitivity, alpha=1 comparator, residual-bias plots and established-method positioning.
- **Status:** In progress
- **Changes performed:** Five broader frozen core streams have no correction plus the predefined alpha grid, giving 35 verified streams across all 23 origins. Bias is applied before current outcomes; each week updates from its observed-hour base residual mean after the forecast horizon. Alpha 0.3 stays predefined. The preserved strict sensitivity retains its original skip/carry policy, so subset correction values can differ even when base forecasts agree. Paired/residual diagnostics and writing remain pending.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/corrections/*.csv; artifacts/coverage_reconsideration/corrections/summary.csv; artifacts/phase2/corrections/; reports/COVERAGE_RECONSIDERATION_RESULTS.md.
- **Critical review (2026-09-30):** A1: residual diagnostics must be regenerated after corrected base fitting; current correction timing itself passed review. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Alpha grid and residual/bias plots show model- and seed-dependent correction effects: artifacts/phase3/correction_alpha_summary.csv; artifacts/phase3/figures/correction_diagnostics.pdf; artifacts/phase3/paired_contrasts.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M9

**Corrected evidence update (1 October 2026): Evidence ready.** All-week variability, matched intervals, hourly/day lead and seed summaries saved. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Present results with coverage, dependence and small-sample qualifications.

> Performance aggregation and uncertainty
> Sections 3.5–3.6 describe averaging weekly metrics, whereas the tables label them as overall MAE and RMSE. Please distinguish mean weekly RMSE from pooled RMSE across all forecasted hours, as these are not equivalent. Report weekly error distributions and uncertainty around paired performance differences using an approach that respects temporal dependence. Also provide performance by forecast lead time, because an aggregate 168-hour score can conceal deterioration at longer horizons.

- **Type / phase:** Forecast reuse + statistics + reporting; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R1.8; exact timestamps and matched coverage.
- **Planned action / closure evidence:** Pooled versus weekly metric definitions, weekly distributions, paired block-bootstrap intervals and lead-time results.
- **Status:** In progress
- **Changes performed:** The wider summary distinguishes equally weighted weekly metrics from pooled observed-hour metrics because four weeks are partial. Weekly SD, window/hour counts and the strict-subset reference are saved. Full timestamped streams support uncertainty and lead-time analysis; those publication analyses remain Phase 3 work.
- **Evidence/artifacts:** artifacts/coverage_reconsideration/experimental_summary.csv; artifacts/coverage_reconsideration/windows.csv; artifacts/coverage_reconsideration/runs/*/forecasts.csv.
- **Critical review (2026-09-30):** A1/A4: metric/interval implementation is available but current model-derived numbers are provisional. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Pooled/weekly MAE/RMSE, all-week spread, paired 2/3/4-week intervals and exact lead-hour/day summaries: artifacts/phase3/performance.csv; artifacts/phase3/paired_contrasts.csv; artifacts/phase3/lead_hour.csv; artifacts/phase3/forecast_day.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M10

**Corrected evidence update (1 October 2026): Evidence ready.** Fit-specific effects, hourly components, resource attempts and timer boundaries saved. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Show model interpretation; qualify causality, stability and implementation-specific memory.

> Interpretability and computational claims
> Interpretability is central to the title but is not demonstrated sufficiently through the reported results. Please present relevant model components, regressor effects, or other interpretable outputs and discuss their stability and limitations without treating associations as causal effects. For runtime comparisons, report CPU, system RAM, software versions, actual GPU use, and whether training, preprocessing, and prediction are included. The SARIMAX memory failure should be described as an observation in the specific implementation and environment rather than a general property of the model.

- **Type / phase:** Model analysis + resource measurement + writing; 1–4.
- **Shared work:** X2, X8.
- **Dependencies / overlap:** R1.3, R1.6; valid fits and comparable timing.
- **Planned action / closure evidence:** Model outputs with stability/noncausal limitations, complete hardware/software/timing description and implementation-specific failure report.
- **Status:** In progress
- **Changes performed:** SARIMAX coefficients/scaling and Prophet components/regressor effects have been saved across primary frozen fits and refits. Local hardware/software, actual CPU/no-GPU use, fitting/prediction/state-update timings and sampled RSS are recorded, including failed/recovered attempts. Stability, noncausal interpretation and fair computational aggregation remain Phase 3 work.
- **Evidence/artifacts:** artifacts/phase1/hardware.json; artifacts/phase1/environment.json; artifacts/phase2/runs/*/metadata.json; artifacts/phase2/runs/core_prophet_*/components_w*.csv; artifacts/phase2/supervisor.jsonl; artifacts/phase2/recovery_supervisor.jsonl.
- **Critical review (2026-09-30):** A1/A2/A4: coefficients require corrected fits; runtime boundaries and component aggregation need explicit treatment. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Frozen/refit SARIMAX and Prophet effects and auditable local timing/CPU/no-GPU resource accounting: artifacts/phase3/coefficients.csv; artifacts/phase3/prophet_components.csv; artifacts/phase3/core_timing.csv; artifacts/phase3/resource_events.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.M11

**Corrected evidence update (1 October 2026): Writing/research pending.** No suggested-study citation has been marked accepted solely because requested. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Verify suggested sources and assess substantive relevance in Phase 4B.

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
- **Limitations or deviation:** Suggested-study source assessment and critical positioning remain pending in Phase 4B.

### R2.m1

**Corrected evidence update (1 October 2026): Writing pending.** Final SARIMAX order is (1,0,1) x (1,0,1,24). See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Rewrite equation to match actual multiplicative structure and differencing.

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
- **Limitations or deviation:** Writing action remains pending; do not mark this reviewer point closed before the manuscript and response are checked.

### R2.m2

**Corrected evidence update (1 October 2026): Writing pending.** Forecasts contain 168 origin-specific leads. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Replace one-step residual terminology.

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
- **Limitations or deviation:** Writing action remains pending; do not mark this reviewer point closed before the manuscript and response are checked.

### R2.m3

**Corrected evidence update (1 October 2026): Writing pending.** No separate Kalman bias-correction alternative was implemented. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Remove its unsupported implementation promise.

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
- **Limitations or deviation:** Writing action remains pending; do not mark this reviewer point closed before the manuscript and response are checked.

### R2.m4

**Corrected evidence update (1 October 2026): Evidence ready.** All-week chronology/distribution and both-regime figure pairs generated. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Select figures and label regime, seed, coverage and units.

> Supplement the best- and worst-week figures with a summary covering all evaluation weeks; these selected examples alone do not establish stability.

- **Type / phase:** Forecast reuse + figures; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R1.8; R2.M9.
- **Planned action / closure evidence:** All-week chronological error plot/distribution and appropriately labeled illustrative weeks.
- **Status:** Evidence ready; manuscript and response pending.
- **Changes performed:** Generated chronological weekly error and distribution figures covering all 23 matched origins; selected examples will be labeled illustrative in the revised manuscript.
- **Evidence/artifacts:** artifacts/phase3/figures/weekly_mae_chronology.pdf; artifacts/phase3/figures/weekly_mae_distribution.pdf; artifacts/phase3/weekly_*.csv.
- **Critical review (2026-09-30):** A1/A4: regenerate figures from corrected forecasts and state the displayed regime/seed. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** All 23 weeks included in chronological and distribution figures: artifacts/phase3/figures/weekly_mae_chronology.pdf; artifacts/phase3/figures/weekly_mae_distribution.pdf.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.m5

**Corrected evidence update (1 October 2026): Evidence ready.** Differences derive from full-precision revised forecasts. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Replace old rounding claims and use consistent displayed precision.

> Reconcile the reported Prophet MAE reduction of 7.93 with the displayed values, 45.61 − 37.67 = 7.94, or explain rounding from unrounded results.

- **Type / phase:** Generated arithmetic + writing; 3–5.
- **Shared work:** X8.
- **Dependencies / overlap:** R2.M9; revised metric values.
- **Planned action / closure evidence:** All differences generated from full precision, with consistent rounding and a note where rounded subtraction differs.
- **Status:** Evidence ready; manuscript and response pending.
- **Changes performed:** Computed revised differences from unrounded saved forecasts and stored them alongside their paired weekly uncertainties. The old 7.93/7.94 assertion is superseded and must be replaced in the manuscript.
- **Evidence/artifacts:** artifacts/phase3/performance.csv; artifacts/phase3/paired_contrasts.csv; reports/PHASE3_RESULTS.md.
- **Critical review (2026-09-30):** A1: use corrected-model differences rather than carrying over current provisional numbers. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Phase 3 evidence:** Phase 3 tables/contrasts derive differences from unrounded saved predictions; the manuscript’s original 7.93/7.94 statement must be replaced by revised values: artifacts/phase3/performance.csv; artifacts/phase3/paired_contrasts.csv.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Phase 3 analysis is available; manuscript/response wording and final claim limits remain pending.

### R2.m6

**Corrected evidence update (1 October 2026): Reproduction/release pending.** Versioned code, saved forecasts, seeds, dependencies, notebook and analysis command exist. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Complete clean-environment reproduction, redistribution review and versioned release.

> Provide a versioned code release, dependency specifications, seeds, data-processing instructions, and scripts reproducing each table and figure.

- **Type / phase:** Reproducibility + packaging; 1–5.
- **Shared work:** X1–X8.
- **Dependencies / overlap:** E4; final executable artifacts.
- **Planned action / closure evidence:** Versioned source, dependencies, seeds, data instructions, reproduction commands, smoke check and DOI-linked release.
- **Status:** In progress
- **Changes performed:** Separate locked strict/broader configurations, signatures, seeds, source-fit reuse records, model traces, forecasts, resource logs and verification commands are available. The revision notebook has saved executed audits, checks, results and coverage chart. Original fingerprints remain unchanged. Local Git milestones preserve the work; GitHub publication status is recorded separately. Clean-environment reproduction, final publication-output scripts and DOI release remain pending.
- **Evidence/artifacts:** README.md; main_revision.ipynb; requirements-observed.txt; artifacts/coverage_reconsideration/verification.json; code/coverage_checks.py; reports/COVERAGE_RECONSIDERATION_RESULTS.md.
- **Critical review (2026-09-30):** A1/A3: add input-validity checks and safe baseline finalization before clean-environment reproduction and release. See reports/PHASE4A_CRITICAL_REVIEW.md.
- **Manuscript location:** Pending.
- **Response status:** Scaffold only.
- **Limitations or deviation:** Clean-environment reproduction, data redistribution decision and versioned DOI release remain pending in Phases 4B–5.

## Editorial obligations

### E1

**Corrected evidence update (1 October 2026): Writing pending.** Verified corrected numbers and a restrained fresh review are available. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Align every manuscript claim with corrected evidence and limits.

> Please ensure the results are accurately reported, any overstated conclusions are rewritten and the limitations of the work fully explained.

- **Type / phase:** Evidence-based writing and consistency audit; 3–5.
- **Closure evidence:** Generated artifacts support all numbers; scope, coverage, limitations and changed findings are explicit.
- **Status:** In progress.
- **Changes performed:** Source/report discrepancies and unreproduced original claims documented. Final numerical results and evidence-based manuscript revision remain pending.
- **Evidence/artifacts:** reports/NOTEBOOK_MANUSCRIPT_DISCREPANCIES.md.
- **Manuscript location:** Pending.

### E2

**Corrected evidence update (1 October 2026): Response pending.** All 27 reviewer points remain individually tracked. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Write and verify every response; add final page/line references.

> Revise the manuscript thoroughly, addressing each reviewer comment.

- **Type / phase:** Comment coverage; 1–5.
- **Closure evidence:** All 27 reviewer entries have individual responses and evidence or an explicit reasoned limitation.
- **Status:** In progress.
- **Changes performed:** All reviewer IDs retained; Phase 1 actions linked individually without marking experimental or manuscript requests prematurely complete.
- **Evidence/artifacts:** REVIEWER_TRACKER.md.
- **Manuscript location:** Pending.

### E3

**Corrected evidence update (1 October 2026): Writing pending.** No manuscript copy has yet been made. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Edit clarity, structure and language after author decision.

> Improve clarity, structure, and language where necessary.

- **Type / phase:** Writing; 4–5.
- **Closure evidence:** Readability edit, compressed repetition and consistent terminology.
- **Status:** Planned.
- **Changes performed / evidence / manuscript location:** Pending.

### E4

**Corrected evidence update (1 October 2026): Release pending.** Local versioned checkpoints exist; DOI publication is outstanding. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Create reviewed DOI-linked code release and availability statement.

> Please note that if your manuscript uses any custom or bespoke computational tool or code, or reports a new algorithm, tool, software, or a pipeline (even if individual components are not new), the underlying code must be deposited in a recognised DOI-assigning repository (e.g. zenodo) and linked either from Methods or a dedicated Code Availability section.

- **Type / phase:** Versioned DOI release; 4–5.
- **Closure evidence:** Published version-specific DOI linked from the manuscript and response, with reviewed reproducibility contents.
- **Status:** Planned.
- **Changes performed / evidence / manuscript location:** Pending.

### E5

**Corrected evidence update (1 October 2026): Submission pending.** Manuscript/response PDFs are not yet prepared; deadline is October 6. See corrected/reports/REVIEWER_EVIDENCE.md. Remaining: Check final PDFs and supplementary material; submission remains an author action.

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
