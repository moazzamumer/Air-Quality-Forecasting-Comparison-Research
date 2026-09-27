# Notebook/manuscript reconciliation

Source of experimental code: unchanged `main.ipynb`. Cell indices below are
zero-based and refer to the original preservation manifest. Existing `.py`
scripts have unconfirmed usage and are not authoritative result evidence.

| Topic | Submitted description | Local evidence | Revision action / reviewer coverage |
|---|---|---|---|
| Sampling calendar | Continuous hourly grid, no missing timestamps | Raw CSV has 744 absent hours; old preprocessing deletes another 2,693 rows | Restore calendar and observation masks; report exclusions and exact coverage (R2.M2–M3) |
| Date range | December 2020–June 2025 | Actual source starts November 25, 2020 at 01:00 and ends June 29, 2025 at 19:00 | Report exact bounds; distinguish requested dates from returned data (R2.M2) |
| Outliers | Training-only percentile winsorization | Cell 17 computes full-dataset z-scores and keeps rows where every z-score is <3; no absolute-value threshold | Start from raw data, do not delete pollution extremes; raw-target evaluation and input-clipping sensitivity (R2.M3) |
| Old preprocessed file | Implied output of stated preprocessing | Its timestamps/values reproduce the cell 17 z-score filter | Record verified source provenance; never call this file winsorized data (R2.M3) |
| EDA correlation | Feature selection training-only | Cell 12's correlation analysis precedes splitting and uses full data | Recompute training-only ranks (R2.M7) |
| Mutual information | Training-only MI and fixed feature set | Cell 24 uses an earlier training slice; the experimental regime later uses a different split | Recompute on the revised training partition and publish exact ranks (R2.M7) |
| mRMR | Valid relevance/redundancy selection | Cell 26 leaves the target last, supplies continuous values without discretization; saved output selects `target` and reflects a different call state | Correct descriptive rerun, disclose original invalid evidence; define four gases as predefined subset (R2.M7) |
| Evaluation coverage | 23 weekly windows | Cell 132 uses 36,830 preprocessed rows and yields 21 complete 168-row chunks with a remainder; chunks are not necessarily calendar weeks | Use 168 calendar hours, record incomplete tail and shared eligible origins (R1.1; R2.M2, M4) |
| NeuralProphet inputs | Future-known selected regressors under PP | Cells 134/148 use lagged regressors and do not provide the current week's future regressors | Use common PP information set with explicitly supplied future regressors (R2.M1, M5–M6) |
| NeuralProphet training | 30 epochs | Adaptive regime source specifies 50 epochs | Training-only bounded 30/50-epoch validation; document revised configuration (R2.M5) |
| NeuralProphet extraction | One complete 168-step forecast | Cells 134/148 take the last 168 values from `yhat1` and drop NaNs; this column does not contain all leads from one origin | Verify raw `step0`–`step167` extraction and original units; reject nonfinite predictions explicitly (R1.4; R2.M5) |
| Prophet seasonality | Additive seasonal/regressor formulation | Cells 137/151 specify multiplicative seasonality; default added regressors inherit model mode | Validate additive/multiplicative options and describe the chosen model accurately (R2.M5, M10) |
| Frozen Prophet origin | Current forecast week advances | Cell 151 calls the frozen model's future-date generator against its original fitted history each week | Predict current target timestamps directly; key regressors by timestamp (R2.M6) |
| Frozen SARIMAX state | Weekly origins with frozen model | Cell 154 repeats `model_fit.forecast` from the original end state, without advancing observed state/history | Extend filtered state with revealed observations and missing-endog handling, keeping fitted parameters fixed (R2.M6) |
| Metrics | Mean window MAE/RMSE | Adaptive source concatenates predictions and computes pooled errors; mean weekly RMSE differs from pooled RMSE | Save and label both definitions, report weekly SD and paired uncertainty (R1.8; R2.M9) |
| Saved primary results | Prophet walk-forward MAE 37.61 / RMSE 50.10 | Cell 137 saved output: 21 windows, MAE 40.21 / RMSE 55.98 | Mark manuscript numbers unreproduced; regenerate with revised protocol, without matching numbers by tuning |
| Frozen-regime results | Complete numerical comparison | Cells 145–158 have no saved outputs | Existing code is a starting point, not independently verified evidence for reported values |
| Environment | Python 3.12 / Colab / T4 | Available local environment: Python 3.11.2, CPU; CUDA-built PyTorch does not establish actual GPU use | Record actual local execution, versions and timing boundaries; no direct old-versus-new hardware speedup claims (R1.6; R2.M10) |
| Original SARIMAX memory failure | Runtime/memory conclusion | Local notebook has an incomplete walk-forward attempt; submitted failure details cannot be reconstructed from saved artifacts | Measure revised implementation and document implementation-specific failures, if any (R1.1; R2.M10) |

These discrepancies do not establish the causes of the submitted NeuralProphet
errors. They justify correctness checks and new experiments before attributing
results to any model family's inherent strengths or weaknesses.

Retrieval dates and original raw API responses are not present in the available
files. Do not infer retrieval dates from file modification times. Extraction
source supports UTC interpretation but does not authenticate historic execution
or the ordered mapping of response component values. Record these limits in
the provenance report and eventual response to R2.M2.
