# Scientific Reports revision plan

Status: Phase 3 analysis completed from the verified 23-origin / 3,624-observed-hour primary evaluation; 19 weeks are complete and four partial. The 16-week strict experiment remains a sensitivity reference. All 129 broader tasks, three baselines and 35 correction streams pass verification. Phase 3 regenerates matched tables, five publication PDF/PNG figures, paired block-bootstrap sensitivity, high-concentration/lead-time diagnostics, interpretability and resource accounting from saved forecasts. The result and reviewer-linked finding records are `reports/PHASE3_RESULTS.md` and `reports/PHASE3_FINDINGS_LEDGER.md`. Manuscript/response edits remain Phase 4 work.

First author: Moazzam Umer Gondal. Corresponding author: Asma Ahmad Farhan.
Decision: Major Revision. Submission deadline: October 6, 2026.

## Agreed boundaries

- Use `main.ipynb` as the primary experimental source. Usage of the existing `.py` scripts is unconfirmed; treat them as supporting references.
- Completely exclude SIVP. Do not expand into unrelated folders or earlier projects.
- Keep the study focused on Beijing PM2.5 under Perfect Prognosis (PP). Do not add an operational covariate-forecasting scenario, another city, PM10 forecasting, or an advanced-model benchmark. Narrow claims accordingly.
- Use the local machine. Observed hardware: AMD Ryzen 5 5500U, 12 logical CPUs, approximately 16 GB RAM; no available `nvidia-smi`. Verify usable acceleration and software before choosing the final execution configuration.
- Preserve the original notebook, raw data, and submitted manuscript. Implement later revisions in separate, versioned artifacts, with explicit links to the original experiments.
- Keep `main.ipynb` at the project root and use `revision/main_revision.ipynb` as the single revision notebook entry point. Supporting code implements reusable checks and experiment functions; the notebook presents the workflow and results. Old supporting files/outputs are archived under `legacy/`, with relocation paths/checksums recorded in `revision/archive_locations.json`.
- Treat all reported numerical results as subject to replacement by corrected experiments. Do not tune to recover the submitted rankings or error values.
- Acceptance is not guaranteed. The response must report evidence honestly, including findings that weaken the original claims.

## Coverage amendment adopted before Phase 3

At Moazzam's request, the strict whole-week exclusion rule was reconsidered.
The primary evaluation now retains all 23 full calendar origins and scores
3,624 original observed hours: 19 complete and four partial weeks. The original
16-week / 2,688-hour matrix is retained as a strict-availability sensitivity.
The 163-hour terminal remainder stays separate. Original fitting targets,
training split, model selection/settings and seeds are unchanged.

Dense inference histories use an explicit causal 168-hour seasonal fill only
where historical observations are missing. Missing future-input hours are not
scored; actual fitted-model placeholder perturbations leave scored forecasts
unchanged. Strict frozen forecasts are reproduced, and 80 compatible weekly
forecasts are reused with exact provenance. The 129-task broader matrix,
baselines and 35 recomputed corrections pass full verification. New work
includes 45 fits and four frozen SARIMAX state reconstructions.

Partial-week coverage, uncertain context filling (including a 120-hour gap),
observed-only scoring and altered correction-update coverage must remain visible
in Phase 3/4. Mean weekly MAE and pooled MAE now differ in weighting. Phase 3
should use the broader streams as primary and the strict streams as sensitivity;
no comparisons may silently mix their masks or correction histories. See
`reports/COVERAGE_RECONSIDERATION_RESULTS.md` and
`config/coverage_reconsideration.json`. Earlier strict rules below document the
preserved reference and are superseded only where this amendment says so.

## Phase 1 — Establish and check the experimental protocol

Purpose: resolve source-code discrepancies and lock a defensible protocol before expensive runs.

1. Record checksums of the original notebook, data, and manuscript. Map notebook cells to manuscript methods and results. Distinguish saved outputs from currently executable source and from unverified manuscript claims.
2. Build a data-provenance and coverage report from the raw Beijing file and extraction code: coordinates, endpoints, variables, units, timestamps, date boundaries, counts, duplicate records, missing values, missing hours, training/test boundaries, and incomplete final windows. Recover retrieval dates/time zone only from evidence; mark unrecoverable metadata explicitly instead of guessing.
3. Reconstruct a regular hourly calendar from the raw data. Preserve an observation mask. Never equate 168 surviving rows with 168 consecutive hours, score imputed target values as observations, or silently discard failed predictions.
4. Before fitting, document and lock the missing-data policy based on the gap audit: eligible forecast origins, minimum historical context, permissible history-only filling, handling of unavailable PP covariates, and a common scoring mask. Report coverage exclusions. This is an unresolved prerequisite, not an invitation to select favorable weeks.
5. Use a chronological 90/10 split defined on the regular calendar, then consecutive non-overlapping 168-hour origins anchored at the test boundary. Evaluate full eligible windows; exclude the incomplete terminal window from primary weekly comparisons and report its dates and size. Revised counts need not equal the original 23 windows.
6. Make the primary experiment use original, unclipped PM2.5 targets and no winsorization. Scale exogenous inputs using training-only statistics when appropriate; document model-native normalization. The winsorization sensitivity changes exogenous inputs only, using 1st/99th training percentiles, while retaining the original target for fitting and scoring. Explain that this evaluates predictor clipping rather than every conceivable clipping policy.
7. Define PP inputs consistently: selected contemporaneous future gases are available to all three model families; future target values are unavailable. Fix origin, target timestamp, and lead time explicitly in every saved forecast.
8. Define frozen as fixed fitted parameters and fixed preprocessing transformations, with history refreshed at each weekly origin. SARIMAX updates its filtered state with newly observed history without refitting; NeuralProphet receives the latest eligible 168 target observations; Prophet predicts the actual current-week timestamps. State refresh is distinct from parameter estimation and EWMA correction.
9. Check NeuralProphet's installed-version prediction semantics. Extract all 168 steps from one forecast origin, not the last 168 values of `yhat1`. Verify alignment using a short synthetic example and an actual data window. Future targets must not enter lag construction or inference.
10. Check the feature-selection implementation, including target position, discrete/continuous inputs, mRMR criterion, and any discretization. Recompute training-only correlation/MI rankings. Treat the four gases as the manuscript's predefined subset unless a valid, documented selection procedure supports stronger claims; do not reverse-engineer a selection rule to force them.
11. Run one-window feasibility pilots only after protocol checks. Record runtime and peak RAM, choose one controlled CPU configuration, and estimate the full matrix below. Plan resumable, sequential fitting with per-window checkpoints; do not parallelize memory-heavy fits on this machine.

Exit evidence: provenance/coverage report, discrepancy log, frozen protocol/configuration, passing alignment/leakage checks, and an estimated execution budget. Resolve the gap policy and any infeasible matrix items before Phase 2; do not silently weaken reviewer coverage.

### Proposed bounded validation and experiment matrix

The agreed matrix below has now been executed. Training-only validation selected the final configurations before held-out fitting. Saved evidence and numerical-recovery exceptions are described in the Phase 2 reports.

| ID | Experiment | Proposed configuration | New fitting? | Main reviewer coverage |
|---|---|---|---|---|
| X1 | Training-only model validation | Use the last four eligible weekly origins entirely inside the training partition. Fit candidates before the first validation origin and update history without refitting for those four origins. Select by mean weekly MAE, then pooled RMSE as a tie-breaker. Disclose this fixed-parameter validation proxy for both regimes. | Yes | R1.5; R2.M5 |
| X2 | Core comparison | SARIMAX, Prophet, NeuralProphet; selected four-gas subset; weekly expanding refit and fixed parameters with refreshed history; identical eligible test origins. | Yes | R1.1, R1.4; R2.M4–M6 |
| X3 | Reference baselines | Persistence: repeat the last observed target for 168 steps. Daily seasonal persistence: repeat the last 24 hours. Weekly seasonal persistence: repeat the last 168 hours. No observations inside the forecast window may enter predictions. Apply the shared context-eligibility policy. | No model training; new predictions | R2.M4 |
| X4 | Predictor ablation | Frozen-parameter runs for all three families: no exogenous variables, the four gases, and all available candidate covariates (gases plus O3, NH3, temperature, dew point, PM10). Reuse the four-gas core run. Use the same selected model settings; describe this as a controlled ablation, not separately optimized best performance. | Two extra fits per family | R2.M7 |
| X5 | Predictor-clipping sensitivity | Frozen-parameter runs for all three families with the selected gases clipped at training-only 1st/99th percentiles. Compare against primary unclipped-input runs on exactly the same original targets. Keep other settings fixed. | One extra fit per family | R2.M3 |
| X6 | Correction alternatives | Replay each core frozen forecast stream with no correction, previous-week mean residual (alpha=1), and EWMA alpha in {0.1, 0.2, 0.3, 0.5, 0.7}. Retain alpha=0.3 as the predefined primary choice; report the full sensitivity without selecting a test-optimal alpha. | No | R1.7; R2.M8 |
| X7 | NeuralProphet repeatability | Seeds 42, 123, 2026 for both core regimes. Report individual-seed and across-seed results; use seed 42 for additional ablations/sensitivities. Do not present seed-averaged predictions as the primary model. | Yes | R1.4; R2.M5 |
| X8 | Metrics, uncertainty, diagnostics | Reuse timestamped forecast streams for weekly/pooled errors, lead-time curves, residual analysis, paired uncertainty, and all-week summaries. | No | R1.8, R1.10; R2.M8–M10; R2.m4–m5 |

Candidate configurations for X1: SARIMAX orders (1,0,1)/(1,1,1), each with seasonal (1,0,1,24)/(1,1,1,24), giving four candidates; Prophet additive versus multiplicative seasonality with daily/weekly/yearly seasonalities and default changepoint settings; NeuralProphet 168 lags/168 forecasts, daily/weekly/yearly seasonalities, future covariates, batch size 128, learning rate 0.001, and 30 versus 50 epochs. Use seed 42 for candidate screening. This is bounded validation, not exhaustive optimization. Save convergence traces/warnings; if all candidates in a family fail validity checks, diagnose and amend the protocol before test evaluation rather than selecting a failed fit.

Exclude PM10 from the predefined four-gas subset as a deliberate companion-particulate input restriction, not because target relevance is predictor redundancy. Include it in the broad PP ablation and describe the resulting information advantage. Generalization beyond API-derived, single-city series remains untested.

## Phase 2 — Produce reproducible experimental evidence

Purpose: execute only the agreed matrix after Phase 1 passes.

- Freeze the validation-selected configurations before test evaluation. Fit primary and sensitivity preprocessing independently as specified; do not reuse test-informed bounds or scalers.
- Run baselines and core models on the shared calendar. Save each completed model/seed/origin immediately. Capture convergence status, actual information supplied, fitting time, prediction/state-update time, and peak process RAM.
- Attempt the full SARIMAX walk-forward evaluation with bounded memory and process cleanup. If it still fails, keep the failure log, report actual coverage, and compare all models on the same successfully evaluated origins. Also show each model's complete available coverage separately. Do not describe partial errors as full-period errors.
- Complete X4/X5 on frozen models to keep their cost bounded. Scope conclusions from these analyses to the frozen regime; do not imply every sensitivity was tested under refitting.
- For EWMA, initialize bias to zero, correct the current week with the bias available at its origin, then update from that week's base residual mean only after outcomes become available. Do not use corrected residuals in the update. Apply identical observation masks across correction variants and document behavior for unevaluable windows.
- Collect interpretable outputs from the primary frozen fits and coefficient/component snapshots from available weekly refits. Distinguish fitted coefficients from total time-varying contributions, especially for multiplicative Prophet models.
- If the feasibility estimate or actual failures make required work impractical, revise the matrix explicitly with Moazzam; prioritize forecast correctness and matched coverage. Do not substitute a reporting-only response for a requested experiment without documenting the limitation.

Minimum saved forecast fields: run/configuration ID, model, regime, feature set, preprocessing variant, seed, forecast origin, target timestamp, lead hour, original target, observation/eligibility mask, base prediction, applied bias, corrected prediction. Store training/validation boundaries, preprocessing parameters, versions, seeds, fit status and resource measurements in run metadata. These are new revision artifacts; no public software API change is required.

Exit evidence: reloadable prediction files and metadata for every planned run, or an explicitly documented failure/coverage exception. No final model ranking is fixed in advance.

## Phase 3 — Analyze results and generate publication outputs

Purpose: answer the reviewers using one consistent set of saved predictions.

- Report pooled MAE and pooled RMSE across scored hours separately from mean weekly MAE/RMSE and their sample standard deviations. Include evaluated hours and windows. Generate all displayed differences from unrounded values.
- Report performance by lead hour and by forecast day (1–7), using matched observations. Summarize all weeks with error distributions and a chronological error plot; keep best/worst examples only as illustrations.
- Predefine paired contrasts: EWMA versus its base model for each family; corrected frozen SARIMAX versus corrected frozen Prophet; corrected frozen Prophet versus walk-forward Prophet; and each core model versus weekly persistence. Report paired mean weekly MAE differences and uncertainty, rather than declaring rankings from isolated point estimates.
- Proposed uncertainty calculation: 2,000 paired moving-block bootstrap replicates of chronological weekly error differences, using blocks of three weeks and sensitivity to two/four weeks, seed 42, percentile 95% intervals. Resample both methods jointly; do not treat hours or NeuralProphet seeds as independent weekly samples. For NeuralProphet's primary paired summary use weekly losses averaged over the three seeds, and report seed variability separately. If coverage is discontinuous, do not join nonadjacent weeks into a block; document the effective runs and resulting limitations. With a short test series, report interval sensitivity and avoid definitive significance language.
- Plot weekly base residual means, lagged bias persistence, applied corrections, and changes in MAE. Use these to explain when correction helps or harms. Label unsupported explanations as hypotheses.
- Report PM2.5 counts, mean, standard deviation, median, IQR, minimum and maximum separately for training/test observed values. Report high-concentration performance above a training-derived 95th-percentile threshold, with the scored sample count; do not substitute a clipped target.
- Present SARIMAX exogenous coefficients with input scaling/units and relevant fit identified; present Prophet trend/seasonality and regressor contributions. Summarize sign/magnitude variation across available refits. Discuss collinearity, model dependence and noncausal interpretation.
- Benchmark runtime on the same machine and controlled thread configuration, with the same timing boundaries. Separate initial fitting, subsequent refitting/state updates, forecasting and correction; label plotting/export exclusions. State GPU use explicitly, report process RAM measurement limitations, and do not compare revised local timings directly with original Colab timings as model speedups.

Exit evidence: complete. `artifacts/phase3/` contains regenerable tables and figures, `reports/PHASE3_RESULTS.md` records the interpretation and limitations, and `reports/PHASE3_FINDINGS_LEDGER.md` maps findings to comments. Twenty-six scientific-contract tests pass. The manuscript and reviewer response have not yet been edited to cite these outputs.

## Phase 4 — Revise the manuscript and response together

Purpose: write to the completed evidence, while keeping each comment traceable.

- Revise Methods and add concise pseudocode specifying each model's information set, state/history updates, forecast horizon, and correction timing. Correct the multiplicative SARIMAX equation and describe horizon-specific forecast errors rather than one-step residuals. Remove the unevaluated Kalman alternative.
- Rewrite Abstract, Results, Discussion and Conclusion around revised results and PP scope. Avoid claims of superiority to untested advanced models or inherent NeuralProphet weakness. Describe original versus revised configurations transparently.
- Shorten Related Work and remove repeated conclusions. Evaluate the five optional reviewer-suggested papers for substantive relevance before citation; emphasize differences in data sources, multi-station versus single-city scope, forecast inputs, adaptation, and resource reporting. Never compare their numerical errors as directly comparable benchmarks.
- Document gridded model-estimate targets, uncertain source metadata, coverage gaps, less-than-year-round testing, limited validation search, and any unresolved computational constraints.
- Prepare versioned reproducibility material: pinned dependencies, seeds, data-processing instructions, configuration, experiment commands and table/figure reproduction commands. Prepare a DOI repository deposit; first check data redistribution terms, so code-only publication with acquisition instructions remains possible. Do not invent retrieval dates or claim a DOI exists before publication.
- Update each response entry with the actual action, evidence, changed manuscript section, and remaining limitations. Shared work may resolve multiple entries; every original comment still receives its own answer.

Exit evidence: revised manuscript, complete response draft, reproducibility package ready for release, and no unsupported completed-action claims.

## Phase 5 — Verify and package the submission

- Check that all 27 reviewer comments and editorial obligations are resolved or have a reasoned, evidence-backed response. A manuscript rewrite alone does not close an experimental request.
- Cross-check tables, figures, abstract numbers, equations, coverage counts and timing definitions against generated artifacts. Ensure partial results and PP limitations are consistently identified.
- Validate a clean-environment smoke reproduction and regeneration of every reported table/figure from saved outputs. Full expensive reruns are not required merely to check document assembly.
- Publish the reviewed versioned code deposit through the author's account when authorized; insert its actual DOI in Methods/Code Availability and the response. GitHub alone does not satisfy the editor's DOI requirement. Finalize the archive content before publication.
- Compile the manuscript and point-by-point response PDFs with LaTeX, check references and rendering, and add final page/line or table/figure locations to responses. Prepare a marked manuscript if required by the submission portal.
- Prepare the final submission files for the authors. Uploading/submitting to the journal is a separate author action unless explicitly delegated.

Exit evidence: final manuscript PDF/source, response PDF/source, required supplementary artifacts, working DOI link and a fully checked tracker.

## Tracking and dependencies

`REVIEWER_TRACKER.md` preserves each original comment and maps it to work, evidence, dependencies and status. `RESPONSE_TO_REVIEWERS.md` is a response scaffold, not a claim that revisions are complete.

Main dependency chain: provenance/calendar → forecast correctness and information sets → validation → core/ablation predictions → metrics and interpretation → evidence-based writing → DOI/PDF/submission checks.

Independent writing edits can proceed after the protocol is settled: terminology, removal of unevaluated alternatives, literature compression, and PP claim boundaries. Final result-dependent prose must wait for Phase 3. Reviewer 2's stronger requests extend Reviewer 1's requests; they do not erase the need to answer Reviewer 1 individually.

Phase 1 resolutions: strict availability retains 16 matched weeks (2,688 hours); targets are never imputed; NeuralProphet trains on contiguous observed episodes with globally shared components/normalization; CPU pilots pass with compatibility wrappers for installed versions. The full matrix remains retained on a rough 8–27 fit-hour estimate before overhead, expanding-history costs and convergence retries. Retrieval dates/raw API response metadata are unrecoverable from current files and remain explicit limitations. Final settings were selected by Phase 2 training-only validation; accepted test fits and numerical-recovery provenance are verified; publication permissions and portal requirements remain Phase 4/5 dependencies.

## Technical references consulted for planning

- NeuralProphet's documentation distinguishes predictions by target and by forecast origin; verify against the installed version: [Prediction collection](https://neuralprophet.com/how-to-guides/feature-guides/collect_predictions.html).
- Statsmodels documents state-space forecasting and updating fitted results without parameter refitting: [Forecasting in statsmodels](https://www.statsmodels.org/stable/examples/notebooks/generated/statespace_forecasting.html).
- Zenodo documents versioned software archiving through GitHub: [GitHub and software](https://help.zenodo.org/docs/github/).

Phase 1 feasibility checks, Phase 2 revised comparison experiments, the coverage reconsideration, and Phase 3 publication analysis are complete. All 21 fingerprinted original files remain unchanged. The new work is isolated below `revision/`. Phase 4 can now rewrite the manuscript and point-by-point response against the documented findings.
