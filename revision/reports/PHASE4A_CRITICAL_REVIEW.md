# Phase 4A critical review — before manuscript editing

Reviewed 2026-09-30 against local commit `39799dd` and the saved run evidence. This is an author-perspective self-audit by the assistant that helped implement the revision. It is not independent external peer review, journal approval, or approval on Moazzam's behalf.

## Verdict

**Hold Phase 4B. The work is concrete, but the current model results are not yet cleared for manuscript use.** The main problem is four invalid `-9999` pollutant input cells in training, including two NO₂ values used by the primary models. Earlier checks verified execution, calendar alignment, absence of future-target leakage and matched scoring, but did not catch these numeric invalid codes. My earlier statements that the evidence was ready for manuscript revision were too broad.

The raw data, original notebook, submitted manuscript, model fits and reported results have not been modified during this review. The 129 run tasks really completed; these are real model outputs. Completing a run is distinct from validating all its input values. Correcting the input handling requires assessing/repeating affected training and validation, not merely changing table labels or rescoring the same predictions.

This does not call for replacing the study. The proposed correction preserves the three model families, two regimes, target, 23-origin test schedule and its 3,624 scored hours. The numerical impact and revised rankings remain unknown until affected fits are rerun.

## What I checked

- Read preprocessing, training/validation scheduling, frozen-state/history updates, broader missingness handling, correction code and Phase 3 aggregation.
- Independently inspected numeric pollutant values in the raw CSV, including finite negative codes that `isna()` does not detect.
- Rechecked all 129 saved runs against the original calendar, target values, common scored-hour mask, horizon timestamps and recorded fitting cutoffs.
- Replayed the timing of all 35 correction streams, verifying that each week uses the previously available bias and only then updates it from that week's base residuals.
- Checked the saved persistence stream against the last genuinely observed target at each origin, all 21 preserved original-file hashes, the source-reuse timing example and component aggregation weighting.
- Reran the existing 26 tests: they pass. None currently rejects the discovered invalid training codes. Passing these tests is therefore necessary but not sufficient for input validity.

The reproducible read-only audit command is `venv/bin/python -m revision.code.phase4a_audit`. It writes only `artifacts/phase4a/` evidence, not training data or model outputs. [Review evidence](../artifacts/phase4a/review_evidence.json) and [test log](../artifacts/phase4a/existing_tests.log) accompany this report. The audit does not independently authenticate the upstream API responses or prove that every possible scientific defect has been excluded.

## Finding A1 — Invalid pollutant inputs require corrected model fitting

**Priority: blocking for quantitative manuscript claims.**

| Timestamp | Input | Value | Used by |
| --- | --- | --- | --- |
| 2023-07-26 07:00 | O₃ | -9999 | Broad-input controls |
| 2024-02-07 23:00 | PM10 | -9999 | Broad-input controls |
| 2024-08-05 03:00 | NO₂ | -9999 | Primary selected-gas models and broad-input controls |
| 2024-08-11 00:00 | NO₂ | -9999 | Primary selected-gas models and broad-input controls |

All are before the first validation fit cutoff (2024-12-16 01:00). No such code was found in PM2.5 or in the test partition. `protocol.load_calendar` preserves these values as finite numbers; scaler fitting and model fitting therefore consume them. Their precise upstream origin or provider missing-value convention has not been authenticated, but they are not valid pollutant concentrations under the recorded units. They must not be confused with valid negative temperature/dew point values or with genuine high PM2.5 extremes.

An **in-memory diagnostic only**, replacing those four input cells with NaN under the existing complete-input-row/episode policies, gives:

| Quantity at initial test fit | Current | After proposed input invalidation |
| --- | --- | --- |
| Selected-input NO₂ standardization scale | 93.3192 | 54.8353 |
| Selected-input complete scaler rows | 35,736 | 35,734 |
| NeuralProphet selected-input training samples | 30,423 | 29,991 |
| NeuralProphet broad-input training samples | 30,423 | 29,504 |
| Primary test scored hours | 3,624 | 3,624 |

Changing a few input cells can affect fitted transformations and many overlapping NeuralProphet windows. This is why I cannot dismiss the problem as only four observations. The diagnostic does not predict how MAE or model rankings will change.

**Required follow-up:** preserve the raw file; add pollutant-specific validity handling in a versioned working view; retain original PM2.5 targets and legitimate negative weather values; add a check for this failure case; repeat affected training-only feature analysis and validation; fit/recover affected models under the corrected version; regenerate metrics, correction streams, uncertainty, coefficients and figures. Retain the previous evidence with its pre-correction identity. Reuse unaffected outputs only after checking their inputs, settings and provenance. Do not choose corrective settings by favorable test outcomes.

**Reviewer relevance:** R1.3–R1.8; R2.M3–M5; R2.M7–M10; E1. It also limits readiness of every result-dependent response.

## Finding A2 — Runtime output is not yet a consistent model-speed comparison

**Priority: fix before citing runtime advantages; no new fitting necessarily required for an honest accounting.**

`phase3_analysis.interpretation` carries fit durations from source metadata, but original fitting timers include initialization/import work whereas numerical recovery timers measure optimization only. Broader reused tasks contain zero newly executed prediction seconds and lightweight process RSS; those values are not the source model's prediction cost or memory. For example, broader `core_prophet_walk_w02_s42` records zero prediction seconds while its source run records about 0.01226 seconds.

The saved campaign wall-time logs correctly preserve actual attempts, including failures, but combining strict and broader campaign costs is not the same as a controlled frozen-versus-refit benchmark. The existing Phase 3 table also includes first-origin fits in a median labeled for weekly-refit sources, rather than isolating only subsequent refits.

**Required follow-up:** distinguish actual campaign work, source fit costs and forecast reuse; recover original timing/RSS for reused predictions where reporting model computation; split incompatible timer boundaries instead of implying direct speed ratios; define whether initial shared fits and recovery attempts enter each total. If a common-boundary comparison cannot be reconstructed, narrow the runtime claim. Do not treat zero reuse time as zero prediction cost. Relevant: R1.6; R2.M10.

## Finding A3 — Baseline regeneration depends on the final checker

**Priority: make reproduction safe before release. The currently saved persistence baseline passed this audit.**

`coverage_runner finish` generates a generic filled-history persistence value. `coverage_checks` subsequently enforces last-genuine-observation persistence. At week 12 these are **14.75 versus 257.0**. The final saved stream uses the correct 257.0. Running `finish` alone can overwrite that corrected stream and its summary. The later Phase 3 additional-check gate helps catch incomplete finalization, but this is an avoidable command-order trap.

**Required follow-up:** make the intended baseline definition authoritative in the finalization entry point, or supply one clearly documented guarded wrapper. Avoid changing signed fitting code or triggering wholesale refits merely to repair output assembly. Until then the required sequence is `finish` → `coverage_checks` → analysis. Relevant: R2.M4; R2.m6.

## Finding A4 — Some analysis summaries need completion or clearer labels

**Priority: reporting repair after A1; saved forecasts contain the information needed.**

- The Prophet component table in `write_report` averages 23 weekly means equally. Its prose does not clearly identify that weighting. CO's mean absolute contribution is 254.11 with equal-week weighting versus 258.44 with equal-hour weighting. State the definition or compute the desired pooled value; do not silently mix them.
- Individual NeuralProphet seeds and seed-averaged paired losses exist, but the planned explicit across-seed mean/SD summary is absent. Produce it from corrected results and distinguish variability across seeds from variability across weeks.
- Five analysis figures are saved, but the current line/distribution plots mostly show seed-42 frozen base models. They are not yet a finished figure set covering both regimes and corrected comparisons. Final figure selection and captions must state regime, seed, mask and units; further plots can be generated from saved forecasts.
- Several historical reports/configuration fields still say earlier phases are pending. Signed experiment records should be preserved, but readers need a clear current index and amendment hierarchy. The new `flow.md` and this review provide that distinction.

Relevant: R1.3–R1.4; R1.8; R2.M5; R2.M9–M10; R2.m4–m6.

## Scientific limits that must remain visible after the repair

These are not reasons to invent a different study or to claim the experiments never ran. They constrain the interpretation:

1. **Provenance:** original API responses/retrieval dates are absent. The historical extraction uses positional `components.values()` mapping and the earliest date has an unresolved source-documentation discrepancy. We cannot independently authenticate that upstream mapping from the surviving CSV. Report source-estimate targets rather than station ground truth. Any recovered original response archive could strengthen this evidence.
2. **Information advantage:** actual future gases make this a PP experiment. Baselines have no such future inputs. Broad-input controls also have future PM10. Lower error than these baselines or between input sets cannot establish operational readiness or pure architecture superiority.
3. **History reconstruction:** causal filling avoids future-target leakage, but does not guarantee accurate history. For the 120-hour synthetic training gaps, saved target-reconstruction MAE ranges from about 214 to 360. State the assumption and retain the strict sensitivity; do not present filled context as measurement.
4. **Small validation/test scope:** four winter validation weeks and 23 test origins are limited. Partial-week losses are based on unequal counts. Block-bootstrap intervals remain descriptive and sensitive to serial dependence/seasonality. The 158 high-concentration hours are clustered in six weeks.
5. **Selection and convergence:** the four gases are predefined, not justified retrospectively by mRMR. A bounded candidate grid, three NeuralProphet seeds and finite training loss do not establish globally optimal models. SARIMAX recoveries and warm starts need disclosure; convergence flags are not proof of a global optimum.
6. **Interpretability:** coefficients/components show how the fitted models use correlated inputs. They do not identify causal effects of pollutants. Coefficient stability is conditional on input validity and the selected fitting protocol.

## Coverage of all reviewer points at this checkpoint

“Recheck numbers” means the requested work exists but affected training/results must be regenerated after A1. “Method ready” means the implementation/protocol can be explained; it does not close the response. All rows still require final manuscript/response treatment.

| ID | Critical review assessment |
| --- | --- |
| R1.1 | Completion/common-calendar evidence exists; repeat affected fits before quoting final 23-origin accuracy. |
| R1.2 | PP-only scope is clear; Abstract/Conclusion qualifications still unwritten. |
| R1.3 | Effects/components saved; recheck after A1 and label aggregation (A4). |
| R1.4 | Alignment/seed checks exist; diagnosis must use corrected results, not presumed architecture weakness. |
| R1.5 | Bounded validation executed; must repeat with valid inputs. |
| R1.6 | Hardware evidence exists; timing comparison needs A2. |
| R1.7 | Alpha grid and causal replay exist; regenerate from corrected base forecasts. |
| R1.8 | Matched metrics/paired intervals exist; regenerate and retain aggregation labels. |
| R1.9 | Concision/readability revision remains a writing task. |
| R1.10 | Original target description is unaffected by these input codes; text insertion pending. |
| R2.M1 | Scope agreed, but deployment wording must still be narrowed. |
| R2.M2 | Calendar/coverage audit exists; address invalid input codes and unrecoverable source metadata explicitly. |
| R2.M3 | Target remains original; recompute predictor-clipping/high-event comparisons after A1. |
| R2.M4 | Current baseline and matched schedule verified; address A3 and rerun affected models. |
| R2.M5 | Training-only selection/alignment procedures exist; input correction requires revised validation and seed results. |
| R2.M6 | Frozen/refit information sets are implemented; pseudocode and explicit inference-filling wording pending. |
| R2.M7 | Four-gas/mRMR distinction is documented; repeat affected rankings and ablations. |
| R2.M8 | Correction is causal and sensitivity executed; corrected residual streams will be needed. |
| R2.M9 | Metrics/uncertainty/lead-time implementation exists; recompute results and explain limited weekly sample. |
| R2.M10 | Interpretation/resource evidence exists; A1/A2/A4 qualify readiness. |
| R2.M11 | Suggested-study relevance assessment and critical literature positioning still pending. |
| R2.m1 | SARIMAX equation must follow the final validated configuration; writing pending. |
| R2.m2 | Horizon-specific residual wording remains a text correction. |
| R2.m3 | Unsupported Kalman implementation statement still needs removal. |
| R2.m4 | All-week figures exist; regenerate after corrected training and label scope. |
| R2.m5 | Arithmetic generation exists; use final corrected values in manuscript/response. |
| R2.m6 | Code/results/provenance are saved; data-validity check, A3, clean-environment reproduction and release remain pending. |

E1–E5 likewise remain open: factual/claim consistency must include A1, every point needs a response, prose needs revision, the DOI-linked release is not complete, and the final manuscript/response PDFs are not yet prepared.

## Recommended order before Phase 4B

1. Agree and record the pollutant-specific invalid-input rule in a new protocol version; preserve the existing raw file and pre-correction evidence.
2. Add a check for the discovered case; re-audit fitting rows, scaling, NeuralProphet episodes and unchanged test coverage.
3. Repeat affected feature analysis/validation, then execute the existing two-regime matrix with the corrected inputs and validated settings. Reuse only demonstrably unaffected work.
4. Regenerate correction/analysis outputs; resolve timing definitions, component weighting, seed summary and baseline finalization.
5. Review the new evidence and record Moazzam's decision before making a working manuscript copy.

No repair fits or manuscript edits were performed as part of this review. The proposal and rationale are recorded in [decisions.md](../decisions.md), and the complete current pipeline is described in [flow.md](../flow.md).
