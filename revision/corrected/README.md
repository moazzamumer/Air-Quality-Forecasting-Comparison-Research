# Corrected-input revision runs

This is the versioned continuation of the existing revision experiments. The original source CSV, `main.ipynb`, submitted manuscript, and `revision/artifacts/` remain the pre-correction record. Start with [the locked protocol](PROTOCOL.md) and [the input audit](artifacts/phase1/input_audit.json).

The corrected working calendar masks four invalid pollutant input cells during loading. The target, 23 forecast origins, 3,624 scored hours, three model families, two updating regimes, validation rule, seeds, controls and EWMA grid remain the intended study design. Model settings must be selected again from the corrected training-only validation before the 23-week matrix runs.

`code/` contains the versioned implementation. `artifacts/phase1/` contains the source/input audit and corrected training-only feature analysis; `artifacts/phase2/` is corrected validation; `artifacts/coverage_reconsideration/` is the corrected two-regime experiment matrix; `artifacts/phase3/` is the downstream analysis. Results in these directories are not manuscript-ready until the full integrity check and author review are complete.

The resumable command after successful validation is `bash revision/corrected/run_after_validation.sh`. It executes the 23-origin matrix, baseline and correction finalization, full checks, analysis and an independent saved-evidence audit. Each command must exit successfully before the next starts. A process exit alone is not accepted as evidence of model completion; `postfit_audit.json` is the final technical gate. Moazzam does not need to run this script.
