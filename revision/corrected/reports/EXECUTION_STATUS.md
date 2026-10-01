# Corrected experiment execution checkpoint

**Final update, 1 October 2026:** all 120 main tasks and eight controls completed successfully. Broad-input SARIMAX failed both bounded fits and is explicitly unavailable. Final analyses, six figure pairs, the independent saved-evidence audit and 25 contract tests passed for the accepted evidence. See [the fresh review](PHASE4A_REVIEW.md) and [author decision checkpoint](../AUTHOR_DECISION.md). The snapshot below is the earlier execution checkpoint.

Snapshot on 1 October 2026 (Karachi time), while the complete 129-task campaign is running. This document is not a completion certificate. The timestamp and signed completed-task list are saved in `../artifacts/coverage_reconsideration/execution_checkpoint.json`.

Completed and checked at this checkpoint:

- Corrected input/source audit and training-only feature analysis.
- All eight validation candidates attempted; seven succeeded. Selection remains SARIMAX `(1,0,1) × (1,0,1,24)`, additive Prophet and NeuralProphet 50 epochs.
- All five frozen core runs, each with 23 origins and 3,624 scored hours, carrying the current corrected experiment signature.
- SARIMAX walk origins 1–3; the first shares the identical corrected frozen computation, while origins 2–3 are actual new fits.
- The initial SARIMAX convergence failure is preserved and excluded. Its fixed training-only recovery is documented in `SARIMAX_NUMERICAL_RECOVERY.md`.

The running command is `bash revision/corrected/run_after_validation.sh`; it resumes compatible completed tasks and then executes finalization, coverage checks, analysis and the independent saved-evidence audit. Progress is recorded in `../artifacts/full_pipeline.log`. No notebook execution is required from Moazzam.

Before accepting final results, require all 129 tasks to be complete and the final technical gate `../artifacts/phase3/postfit_audit.json` to pass under the current signature. Then review the numerical effects, limitations and reviewer coverage and record Moazzam's decision in `../AUTHOR_DECISION.md`. The manuscript-copy gate remains closed until that decision.
