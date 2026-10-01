# The experiment pipeline, explained for Moazzam

**Current pipeline amendment, 1 October 2026:** use `corrected/` for the completed corrected-input experiments. Mask four invalid pollutant predictor cells in memory → repeat training-only feature analysis/validation → fit the same two-regime, 23-origin matrix → generate common-mask scores/corrections → run `bash revision/corrected/run_analysis.sh` → author evidence review. All 120 main tasks and eight controls passed; one bounded control fit failed and is explicitly unavailable. [Current protocol](corrected/PROTOCOL.md), [notebook](corrected/main_revision.ipynb) and [review](corrected/reports/PHASE4A_REVIEW.md) supersede the numerical-readiness statements in the earlier pipeline account below.

**Read this first:** this describes what the saved revision experiments actually did. The critical author review found four invalid `-9999` pollutant input values in training. The existing numbers are now provisional, pending correction and rerunning affected work. The raw dataset and the saved experiments have not been changed. See [the review](reports/PHASE4A_CRITICAL_REVIEW.md) and [decisions](decisions.md).

The overall flow is: **raw data → hourly calendar → training/test split → training-only validation → frozen and weekly-refit forecasts → residual correction → matched scoring → tables and figures.** The notebook displays this work; scripts carry out fitting and analysis.

## 1. What are we predicting?

We predict the next 168 hourly PM2.5 values in Beijing. PM2.5 is the **target**. NO, NO₂, CO and SO₂ are the four primary **inputs**, also called covariates or regressors. The data are API-derived estimates, rather than an identified set of station measurements. Future gas values are supplied from the held-out data under **Perfect Prognosis (PP)**. Future PM2.5 values are withheld from prediction and used afterwards to measure error.

This is the original study's general comparison: SARIMAX, Prophet and NeuralProphet, with weekly refitting versus fixed parameters and residual correction. The implementation and some selected settings have changed to address correctness and reviewer requests.

## 2. Which data enter the revision?

| Item | Actual revision procedure |
| --- | --- |
| Source | `data/beijing.csv`; the source CSV remains unchanged. |
| Recorded interval | 2020-11-25 01:00 through 2025-06-29 19:00. |
| Raw rows | 39,523, with 744 absent hourly timestamps. |
| Calendar | Reindex to 40,267 consecutive hourly positions; insert missing positions as NaN, without inventing measurements. |
| Old preprocessing | The original notebook's full-dataset upper-tail z-score row filter is not used. It removed 2,693 rows and broke hourly continuity. |
| Target cleaning | Preserve recorded PM2.5 values, including high pollution levels. No target winsorization, replacement or synthetic scoring labels. |
| Detected gap in this procedure | NaN checks did not catch numeric `-9999` entries in NO₂, O₃ and PM10. They were treated as data. Correction is proposed, not yet implemented. |

Negative temperatures and dew points are legitimate values and must not be removed by a general “negative value” rule. Pollutant inputs require their own validity checks. Original-source uncertainties, including unrecorded retrieval dates and response-field mapping, are listed in `artifacts/phase1/provenance.json`.

**Code:** `code/protocol.py` (`load_calendar`); `code/audit.py`. **Evidence:** `reports/PHASE1_DATA_AUDIT.md`; `artifacts/phase4a/invalid_pollutant_cells.csv`.

## 3. Where is the training/test boundary?

The split is chronological, using 90% of the complete hourly calendar for training. There is no random row shuffle between training and test.

| Partition | Calendar hours | Originally present target values | Dates |
| --- | --- | --- | --- |
| Training | 36,240 | 35,736 | 2020-11-25 01:00 through 2025-01-13 00:00 |
| Test | 4,027 | 3,787 | 2025-01-13 01:00 through 2025-06-29 19:00 |

The test interval contains **23 full calendar forecast weeks plus a 163-hour tail**. The main revised evaluation retains all 23 forecast origins. It scores 3,624 hours: 19 fully observed weeks and four partial weeks. The 163-hour tail is described but excluded from the full-week experiment. The earlier 16-week result is a strict-availability sensitivity, not the main result.

At every origin, all methods use exactly the same scored target timestamps. An hour is scored only if its original PM2.5 and all nine broad-set covariates are present. This common rule also applies to baselines and selected-gas models to keep comparisons matched.

The newly found invalid cells are all in training. In-memory replacement of those cells with NaN leaves this 23-origin / 3,624-hour test mask unchanged.

## 4. What preprocessing happens before a fit?

Input scaling uses `StandardScaler`: subtract the fitting-history mean and divide by its standard deviation. Statistics are estimated only from complete input rows available before the fit's cutoff. They are frozen in the frozen regime and recalculated from expanded history in the weekly-refit regime. No test-wide scaler is used.

In the primary experiment neither inputs nor target are clipped. A separate frozen-model sensitivity clips **input values only**, at 1st/99th percentiles learned from fitting history, before scaling. The target stays original. There is no additional post-forecast clipping to force predictions above zero.

Missing training data are handled by model:

| Model | Treatment during fitting |
| --- | --- |
| SARIMAX | Keep the hourly calendar and missing targets as NaN. Causally forward-fill historical exogenous gaps for state propagation. Missing PM2.5 is not invented. |
| Prophet | Fit complete observed rows containing the target and required inputs, retaining their actual dates. |
| NeuralProphet | Form contiguous fully observed episodes of at least 336 hours, sufficient for a 168-hour input history plus 168-hour forecast target. No training window crosses a gap. Episodes share global model parameters and target/time normalization. |

Prophet's extra regressor scaling is disabled because external scaling is already applied. NeuralProphet's future-regressor normalization is disabled; its target normalization is learned during fitting. None of these checks currently rejects the numeric `-9999` values; that is the outstanding preprocessing correction.

**Code:** `code/protocol.py` (`fit_input_scaler`, `neural_training_segments`); `code/phase2_models.py` (`fit_model`).

## 5. How were settings chosen?

Four chronological validation weeks lie entirely inside training, from 2024-12-16 01:00 to 2025-01-13 00:00. Candidate models were fitted before the first validation origin and their history/state refreshed at subsequent origins. Mean weekly MAE selected the configuration, with pooled RMSE as a tie-breaker. This is a bounded fixed-parameter validation proxy used for both regimes, not an exhaustive search or separate optimization for each regime.

| Model | Candidates | Existing selected setting, now provisional |
| --- | --- | --- |
| SARIMAX | Four combinations of `(1,0,1)`/`(1,1,1)` with seasonal `(1,0,1,24)`/`(1,1,1,24)` | `(1,0,1) × (1,0,1,24)`; one candidate did not converge and was not selected |
| Prophet | Additive or multiplicative seasonality | Additive |
| NeuralProphet | 30 or 50 epochs, seed 42 for screening | 50 epochs; 168 lags, 168 forecasts, batch size 128, learning rate 0.001 |

The four gases remain a **predefined subset**. The corrected descriptive mRMR run did not establish that this exact subset was selected. Rankings, selection scores and chosen settings require review after the invalid training inputs are corrected, because those values precede even the validation fitting cutoff.

**Code:** `code/phase2_runner.py`. **Evidence:** `artifacts/phase2/selection.json`, `validation_summary.csv` and `artifacts/phase1/feature_rankings_training_only.csv`.

## 6. What happens in the two regimes?

| At each weekly origin | Frozen parameters | Weekly expanding refit |
| --- | --- | --- |
| Fit model parameters | Once on initial training history | Fit on all available history before that week's origin |
| Fit preprocessing | Once; keep transformations fixed | Refit transformations on that expanded history |
| SARIMAX history | Update the filtered state using newly revealed targets without estimating new parameters | Fit on the expanded historical series |
| Prophet dates | Forecast the actual current week's timestamps | Forecast that week's timestamps using the new fit |
| NeuralProphet context | Supply the latest 168-hour history to the fixed model | Supply latest history to the newly fitted model |
| Future target information | No future PM2.5 supplied | No future PM2.5 supplied |
| Future gas information | Actual future gases under PP | Same PP assumption |

For example, week 2's refit may use week 1 observations because they have already occurred. It cannot use week 2 PM2.5 to make week 2 forecasts. The first origin is the same fitting problem in both regimes, so its fit/forecast can be shared rather than counted twice.

## 7. How does the 23-week version deal with gaps at prediction time?

For NeuralProphet's dense historical context and the seasonal baselines, missing history is filled from 168 hours earlier, recursively using past values; where no seasonal antecedent exists, the last prior value is used. Actual historical observations are preserved. This is **inference-context filling**, not target filling for model fitting or scoring. SARIMAX uses its missing-target filter; Prophet does not consume a target-lag context.

A future input can be unavailable inside a partial week. The computational model input uses a placeholder so a forecast array can be formed; the affected hour is not scored. A second prediction perturbs those placeholders and checks that predictions at scored hours are unchanged. Saved affected forecasts are masked. This test does not prove that historical filling is accurate. Training-only masked-history checks showed large reconstruction errors, especially for long gaps; the assumption must remain visible.

**Code:** `code/coverage_protocol.py`. **Evidence:** `artifacts/coverage_reconsideration/windows.csv`, `history_fill_validation.csv`, and per-run metadata.

## 8. Which experiments were executed?

| Experiment | Coverage |
| --- | --- |
| Core four-gas comparison | All three families, frozen and weekly refit; NeuralProphet seeds 42, 123 and 2026 |
| Simple baselines | Last-observation persistence, daily persistence and weekly persistence |
| Predictor controls | Frozen seed-42 models with no inputs, four selected gases, or broad inputs including future PM10 |
| Clipping sensitivity | Frozen seed-42 selected-gas models with training-derived predictor clipping |
| Residual correction | Each frozen core stream, α in 0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0 |

The broader runner completed 129 tasks: five frozen core tasks, 115 model/seed/week refit tasks, and nine extra frozen controls. Its execution comprised 45 new fits, 80 reused forecasts from actual earlier fits, and four frozen SARIMAX state reconstructions. These are not 129 newly trained models. Preserved source paths identify reuse. Experiments genuinely ran; the newly identified invalid-input issue means their final numerical conclusions still need re-evaluation.

Fitting used the local CPU, two configured model threads, sequential child processes and saved per-origin outputs. SARIMAX failures were retained and eligible final-comparison fits were recovered with a documented numerical solver policy; recovery uses training likelihood/convergence, not favorable test errors.

## 9. How does residual correction work?

Start with bias zero. Add the bias known at the start of the current week to every base forecast. After that week finishes, calculate its mean **original target minus base prediction** over scored hours. Update the bias for the next week:

`next_bias = alpha × current_week_base_residual_mean + (1 − alpha) × current_bias`

The predefined main alpha is 0.3. Alpha 1 uses only the previous completed week's mean residual; alpha 0 supplies no correction. The current week's outcomes never correct that same week's forecasts. The broader experiment updates after each of 23 weeks; the strict 16-week experiment skips unavailable weeks and carries its bias. Their corrected predictions need not match even on overlapping weeks.

## 10. How are outputs turned into paper results?

`forecasts.csv` saves timestamp, origin, lead hour, original target, scoring mask and prediction. `metadata.json` records settings, training cutoff, fitting status/timing and source reuse. NeuralProphet also has training traces; Prophet has component CSVs. The analysis reloads these files to produce pooled MAE/RMSE, weekly means and sample SD, matched weekly differences, lead-hour/day errors and pollution-extreme results.

Paired comparisons resample chronological weekly differences using 2,000 moving-block replicates, with blocks of 3 weeks and sensitivity to 2/4 weeks. NeuralProphet seed-level weekly losses are averaged before that comparison; seed runs do not count as extra independent weeks. High-concentration analysis uses the training target's 95th percentile. These analyses cannot repair invalid training inputs after the fact.

PDF/PNG figures and CSV tables are in `artifacts/phase3/`. More presentation figures can be generated from saved forecasts and components after the corrected evidence is accepted. Models are not generally saved as reloadable full checkpoints; a new question requiring unsaved internals could require another fit.

## 11. Which files should I open?

| Question | Entry point |
| --- | --- |
| What happens and why? | This file and [decisions.md](decisions.md) |
| Is the evidence ready? | [Critical review](reports/PHASE4A_CRITICAL_REVIEW.md) |
| What is each reviewer asking? | [Reviewer tracker](REVIEWER_TRACKER.md) |
| What are the current results? | [Phase 3 report](reports/PHASE3_RESULTS.md), now provisional |
| Where do I see notebook output? | [main_revision.ipynb](main_revision.ipynb), also provisional |
| Where is training implemented? | `code/phase2_models.py`; schedules in `phase2_runner.py` and `coverage_runner.py` |
| Where is gap handling implemented? | `code/protocol.py` and `coverage_protocol.py` |
| Where are tables/figures calculated? | `code/phase3_analysis.py` |

The base `config/protocol.json` is a historical signed strict-protocol record; `config/coverage_reconsideration.json` overrides its test eligibility/context rules for the primary 23-origin experiment. Some old status text in the signed files is historical. Neither file currently includes the proposed sentinel correction.

The current finalization order is `coverage_runner finish` **followed by** `coverage_checks`, before `phase3_analysis`. The final checker enforces the correct last-genuine-observation persistence baseline. The review found that `finish` alone uses a different value when the last historical hour is missing. This reproduction dependency must be made unambiguous before release; Moazzam does not need to execute these commands for the review.
