# Corrected evidence review before Phase 4B

Reviewed on 1 October 2026. This is the assistant's self-audit of the revision it helped implement, not independent peer review or a decision on Moazzam's behalf.

## Assessment

**The corrected primary experiments and reporting package are ready for author review. I recommend proceeding to manuscript writing after Moazzam records his decision, with the limitations below carried into the manuscript and response.** All 120 main tasks completed: five frozen fits/streams and 115 weekly-origin tasks across the same three families, two regimes and three NeuralProphet seeds. Eight of nine controls completed. The broad-input SARIMAX control failed both bounded optimizer attempts and is unavailable; it has no accepted predictions or error estimates. This limits the broad-feature comparison but does not invalidate the completed primary experiments.

The [independent saved-evidence audit](../artifacts/phase3/postfit_audit.json) passed for the 128 successful tasks and separately checked the declared failed control. The all-task success flag remains false. The analysis gate explicitly requires all main tasks and the eight other controls, rather than silently dropping any unsuccessful main model. All 25 scientific-contract tests passed; [the log is saved](../artifacts/phase3/contracts.log).

## Corrected findings

Every value below is pooled hourly MAE on the same 23 origins and 3,624 observed scoring hours. NeuralProphet entries in this table use seed 42; the next paragraph summarizes all seeds.

| Family | Frozen base | Weekly refit base | Frozen + EWMA α=0.3 |
| --- | ---: | ---: | ---: |
| SARIMAX | 30.484 | 30.430 | 29.938 |
| Prophet | 43.929 | 38.720 | 37.687 |
| NeuralProphet, seed 42 | 53.392 | 41.949 | 37.618 |

Across three NeuralProphet seeds, frozen MAE is 46.883 ± 10.398 and weekly-refit MAE is 39.605 ± 4.325 (mean ± sample SD across seeds). Seed 2026 performs substantially better than seeds 42/123. EWMA improves the latter two but slightly worsens seed 2026. Do not state that the correction always helps or that one architecture is inherently inferior. The matched weekly bootstrap interval for SARIMAX's small correction benefit includes zero; Prophet's and the seed-averaged NeuralProphet improvement intervals exclude zero under the primary block length, subject to the short dependent weekly sample and sensitivity limitations.

The corrected input rule has a meaningful effect: seed-42 frozen Prophet MAE changes from 38.648 to 43.929 and NeuralProphet from 38.462 to 53.392 relative to the preserved pre-correction revision. SARIMAX changes only slightly. These are a transparent corrected rerun, not an attempt to preserve earlier rankings. All target-only baselines reproduce the pre-correction values.

Broad-input Prophet and NeuralProphet controls have MAE 15.869 and 22.345, respectively, with actual future PM10 included. Their informational advantage must be stated. The failed broad-input SARIMAX control prevents a complete three-family broad-input ranking. The four gases remain a predefined study subset; the corrected descriptive mRMR ranking does not establish that they are optimal.

The 158 high-concentration hours are clustered in six weeks. On that subset seed-42 NeuralProphet has lower MAE than SARIMAX/Prophet despite its worse aggregate performance. This supports reporting concentration and seed dependence rather than a universal ordering.

## Earlier review findings

| Finding | Resolution and evidence |
| --- | --- |
| A1: invalid input values | Exactly four `-9999` predictor cells become missing in memory. The raw source and targets are unchanged. Validation, descriptive feature analysis and affected fits were repeated. [Input audit](../artifacts/phase1/input_audit.json); [selection](../artifacts/phase2/selection.json). |
| Fitting/scaling/episodes | Independent checks reproduce preprocessing from history before each origin and NeuralProphet episode sample counts. No fitting or scoring targets are imputed. All accepted model outputs use the corrected signature. |
| Calendar and target isolation | All main streams retain 23 origins / 3,624 scored hours; four weeks have partial coverage. Timestamp alignment, shared masks, causal history handling, and unavailable-input placeholder invariance pass. The 16-week sensitivity uses the corrected forecasts. |
| A2: timing | Fit timer boundaries and first-origin source forecast cost are explicit. Recorded supervisor attempts include failures but exclude unrecorded diagnostic/interrupted work; these are not total project time or a controlled speed ratio. |
| A3: baselines | Production and verification share the last-genuine-observation helper. Week 12 persistence is 257.0. Three baseline definitions/checksums are saved; running finalization alone produces the correct persistence value. |
| A4: summaries and figures | Prophet components are weighted by scored hours. An explicit three-seed mean/SD table and six PDF/PNG figure pairs are saved, including both-regime comparisons. Final manuscript captions still need selection and wording. |
| Bounded control failure | Training-only recovery exhausted 400 iterations without convergence. Estimates/attempts are retained, and no failed-fit forecasts enter the analysis. [Failure declaration](../config/analysis_completion.json). |

## Interpretation limits and writing obligations

Actual future gases make this retrospective Perfect Prognosis evaluation. Target-only baselines have a different information set. The API-derived source estimates are not independently authenticated station measurements; missing original responses, positional pollutant mapping and a source-date discrepancy remain provenance limitations. Causal historical inference filling is an assumption, especially across the 120-hour gap. Four winter validation weeks, 23 test origins, three seeds and the small clustered high-event subset limit generalization. Coefficients/components describe conditional model associations, not causal pollutant effects. Solver convergence does not prove a global optimum.

No definite future-target leakage or train/test scaling violation was found in the reviewed implementation and saved evidence. This audit checks those concrete contracts; it cannot certify every possible scientific defect or authenticate upstream data. The already examined test period must be described as a revised retrospective evaluation.

The [corrected reviewer evidence ledger](REVIEWER_EVIDENCE.md) maps every point to its current evidence and remaining writing task. Literature assessment, manuscript equations/terminology, claim narrowing, clean-environment reproduction, DOI release and the response PDF remain Phase 4B/5 tasks. No comment is closed until its manuscript and response treatment is checked.

## Author decision

Moazzam should decide whether to proceed with the verified primary package while disclosing the unavailable broad-input SARIMAX control, or require further work on that control or another named concern. Record the decision in [AUTHOR_DECISION.md](../AUTHOR_DECISION.md). No working manuscript copy has been created.
