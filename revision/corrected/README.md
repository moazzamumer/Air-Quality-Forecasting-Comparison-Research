# Corrected-input revision runs

**Current status, 1 October 2026: analysis and saved-evidence checks complete for 128 successful tasks; one bounded broad-input SARIMAX control failed and is declared unavailable. All 120 main experiment tasks passed.** Start with [the fresh evidence review](reports/PHASE4A_REVIEW.md), [corrected notebook](main_revision.ipynb) and [author decision checkpoint](AUTHOR_DECISION.md).

This is the versioned continuation of the existing revision experiments. The original source CSV, `main.ipynb`, submitted manuscript, and `revision/artifacts/` remain the pre-correction record. Start with [the locked protocol](PROTOCOL.md) and [the input audit](artifacts/phase1/input_audit.json).

The corrected working calendar masks four invalid pollutant input cells during loading. The target, 23 forecast origins, 3,624 scored hours, three model families, two updating regimes, validation rule, seeds, controls and EWMA grid remain the intended study design. Corrected training-only validation selected the same settings before the 23-week matrix ran.

`code/` contains the versioned implementation. `artifacts/phase1/` contains the source/input audit and corrected training-only feature analysis; `artifacts/phase2/` is corrected validation; `artifacts/coverage_reconsideration/` is the corrected two-regime experiment matrix; `artifacts/phase3/` is the downstream analysis. Results in these directories are not manuscript-ready until the full integrity check and author review are complete.

The original training command is `bash revision/corrected/run_after_validation.sh`. With the signed declared control failure, regenerate final tables, figures and evidence checks using `bash revision/corrected/run_analysis.sh`; this performs no model fitting. Each stage must exit successfully before the next starts. `postfit_audit.json` records the technical gate, successful tasks and unavailable control separately. Moazzam does not need to run these scripts.
