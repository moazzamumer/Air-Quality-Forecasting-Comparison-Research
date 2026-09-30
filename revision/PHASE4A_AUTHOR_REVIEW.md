# Phase 4A — Moazzam's review before manuscript editing

**Critical review update, 2026-09-30: hold Phase 4B.** The assistant's [critical review](reports/PHASE4A_CRITICAL_REVIEW.md) found four invalid `-9999` pollutant input cells in training, including two in the primary NO₂ input. Existing accuracy/selection results are provisional pending input correction and affected refitting. The 23-origin / 3,624-hour test mask is unchanged by the proposed correction. “Evidence ready” in the historical map below means work was executed; it no longer clears the affected numerical results for manuscript use. Start with [flow.md](flow.md) and [decisions.md](decisions.md) to understand the pipeline and proposed repair.

**Purpose.** Review the revised study at a high level and check that every reviewer request has a concrete answer path. This is an author decision checkpoint. The submitted `PM_Forecasting_Environmental_Modeling_Assessment_Submission/manuscript.tex` and PDF remain untouched; no working manuscript copy is created in Phase 4A.

**Lifecycle follow-up.** The [forecasting-methodology review](reports/PHASE4A_LIFECYCLE_REVIEW.md) checked preprocessing, validation, information boundaries and saved metrics. No additional definite leakage violation was found in the inspected paths. It retains the input-validity blocker and explicitly qualifies PP, prior test-period exposure, source provenance and inferential claims.

**Current evidence.** The primary comparison is 23 consecutive weekly origins with 3,624 observed scoring hours (19 complete and four partial weeks). The original 16-week / 2,688-hour strict-availability experiment is a secondary sensitivity. All three families were evaluated in frozen and weekly-refit regimes. [The Phase 3 results](reports/PHASE3_RESULTS.md), [executed notebook](main_revision.ipynb), [Phase 3 findings ledger](reports/PHASE3_FINDINGS_LEDGER.md), and [full reviewer tracker](REVIEWER_TRACKER.md) are the review sources. The notebook presents results; model fits and provenance live in `artifacts/coverage_reconsideration/runs/` and `artifacts/phase2/runs/`.

## What to review first

1. **Study identity and scope.** Confirm that the same Beijing PM2.5, three-family, two-regime Perfect Prognosis comparison remains the paper's subject. The corrected 23-week schedule, original targets, four-gas primary inputs, and 16-week sensitivity are acceptable. Four partially scored weeks and a separate 163-hour remainder must be visible.
2. **What the data support.** The pre-correction matched performance and paired intervals are preserved in `reports/PHASE3_RESULTS.md`; their rankings and effect sizes require re-evaluation after invalid-input repair. Once corrected results are available, inspect model/seed-dependent correction effects, high-concentration performance and paired uncertainty without assuming the old findings must survive. The broader-input control includes future PM10 and should remain a qualified ablation.
3. **Figures and readability.** Inspect `artifacts/phase3/figures/` (five PDF/PNG pairs) and `artifacts/coverage_reconsideration/coverage.pdf`. These are evidence plots, not a fixed final manuscript layout; Phase 4B can combine, restyle or add plots from saved forecasts and components without retraining.
4. **Known limits.** Accept or flag the Perfect Prognosis future-gas assumption, model-estimate rather than station target, unavailable historical retrieval-date/raw-response metadata, causal filling of missing inference history (including a 120-hour gap), four partially observed weeks, and the short test season. These must be stated plainly in the paper.
5. **Response scope.** Check the point-by-point map below. An experiment may be complete while its manuscript explanation and reviewer response remain unwritten. Approval to proceed means the evidence and planned treatment are acceptable, not that all 27 comments are already closed.

## All 27 reviewer points

“Evidence ready” means the requested experiment, diagnostic, table or audit is available. “Writing pending” means the actual manuscript and response text still need to be made and checked. Links are in the [tracker](REVIEWER_TRACKER.md) and [findings ledger](reports/PHASE3_FINDINGS_LEDGER.md).

| ID | High-level treatment to review | Current gate |
| --- | --- | --- |
| R1.1 | All three weekly-refit families now have matched 23-origin results; disclose the original incomplete SARIMAX run as corrected. | Evidence ready; writing pending |
| R1.2 | Explain when future gases may be known and when Perfect Prognosis is only an idealization. | Scope decided; writing pending |
| R1.3 | Report identified-fit SARIMAX/Prophet effects, scaling, refit ranges and noncausal limits. | Evidence ready; writing pending |
| R1.4 | Explain NeuralProphet checks, three-seed variation and tentative causes without claiming inherent weakness. | Evidence ready; writing pending |
| R1.5 | Explain training-only candidate validation and revised SARIMAX order selection. | Evidence ready; writing pending |
| R1.6 | Give CPU-only hardware, software, fit/forecast/state-update timing and RAM caveats. | Evidence ready; writing pending |
| R1.7 | Report the predefined EWMA alpha grid and previous-week comparator; do not tune on test errors. | Evidence ready; writing pending |
| R1.8 | Show pooled and weekly errors, weekly spread and matched paired intervals. | Evidence ready; writing pending |
| R1.9 | Shorten Related Work and remove repeated Discussion/Conclusion prose. | Writing task pending |
| R1.10 | Include original-scale training/test PM2.5 descriptive statistics. | Evidence ready; writing pending |
| R2.M1 | Restrict Abstract/Conclusion deployment claims to Perfect Prognosis. | Scope decided; writing pending |
| R2.M2 | Give exact provenance, counts, dates, 23-origin coverage and model-estimate target caveat; do not invent retrieval dates. | Audit ready; unrecoverable metadata must be acknowledged |
| R2.M3 | State unclipped targets, input-clipping sensitivity and high-concentration performance. | Evidence ready; writing pending |
| R2.M4 | Report three persistence baselines and matched 23-origin comparison; narrow claims about untested advanced models. | Evidence ready; writing pending |
| R2.M5 | Give chronological validation, alignment/convergence checks and NeuralProphet seeds. | Evidence ready; writing pending |
| R2.M6 | Define frozen parameters versus refreshed history/state and provide information-set pseudocode. | Implementation checked; pseudocode pending |
| R2.M7 | Correct mRMR/feature-selection account and show fixed-setting no/selected/broad-input ablations. | Audit and ablations ready; writing pending |
| R2.M8 | Explain alpha=0.3 as predefined, show residual patterns and alpha=1, call EWMA an established method. | Evidence ready; positioning text pending |
| R2.M9 | Distinguish pooled/weekly RMSE, show all-week spread, paired intervals and lead-time performance. | Evidence ready; writing pending |
| R2.M10 | Show effects/components and stability; report resource boundaries and implementation-specific failures. | Evidence ready; writing pending |
| R2.M11 | Critically assess suggested recent studies and position this narrower single-city PP study. | Source assessment and writing pending |
| R2.m1 | Correct the SARIMAX equation to the implemented orders and regression treatment. | Formula edit pending |
| R2.m2 | Replace “one-step residual” with the actual horizon-specific weekly forecast error. | Terminology edit pending |
| R2.m3 | Remove the unsupported Kalman-implementation claim. | Text edit pending |
| R2.m4 | Show chronological and distribution summaries for all 23 weeks; label selected examples illustrative. | Figures ready; writing pending |
| R2.m5 | Replace the old 7.93/7.94 arithmetic with revised unrounded-generated values. | Evidence ready; text edit pending |
| R2.m6 | Assemble versioned source, dependency/data instructions and table/figure regeneration; later verify a clean environment and DOI deposit. | Reproduction scripts present; release/package pending |

## Editorial items and acceptance gate

The decision letter also requires accurate and proportionate conclusions (E1), a response to every reviewer item (E2), improved clarity (E3), a versioned DOI-linked release (E4), and a complete submission package (E5). These are Phase 4B/5 deliverables, not completed by this review sheet.

Phase 4A is complete when the blocking invalid-input issue and identified reporting/reproduction follow-ups have been resolved, then Moazzam has reviewed the five items above and accepted the updated 27-point treatment map as the basis for writing. A concern can be logged in `REVIEWER_TRACKER.md` before manuscript work. **Do not mark a reviewer point resolved merely because its analysis exists.** The assistant's critical review does not substitute for Moazzam's acceptance.

Only then begin **Phase 4B**: create a separate working copy of the submitted LaTeX manuscript, preserve the original and its checksum, revise the manuscript and `RESPONSE_TO_REVIEWERS.md` together, and update each tracker entry with the actual section/table/figure and remaining limitation. Final PDF compilation, page/line references and release checks remain Phase 5.
