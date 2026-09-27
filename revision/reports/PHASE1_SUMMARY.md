# Phase 1 summary

Technical checks: passed. Full research experiments have not started.

## Workspace and preservation

Revision code, configuration, notebook, reports, tests and generated artifacts are isolated below `revision/`. All 21 fingerprinted originals remain unchanged, including `main.ipynb` and the submitted manuscript.

## Established findings

- Raw data: 39,523 rows, 40,267 calendar hours, 744 missing hours in 21 intervals. The raw file has no empty values, which does not establish continuous sampling.
- Old preprocessing is verified whole-dataset upper z-score row removal: 2,693 rows deleted. It is not the winsorization described in the paper.
- The revised calendar split starts testing at 2025-01-13 01:00. There are 23 full weeks plus a 163-hour terminal window.
- Shared strict availability retains 16 weeks / 2,688 original observed target hours. Availability exclusions and exact dates are saved; this reduces generalizability and must be disclosed.
- Corrected training-only correlation, MI and mRMR results are saved. The original mRMR call is invalid evidence for selecting four gases; the revision labels them predefined and plans an ablation.
- Source code supports UTC interpretation and establishes endpoint/coordinate evidence. Exact retrieval dates and archived response metadata remain unavailable; a provider-availability/start-date discrepancy is also documented.

## Correctness evidence

- 10 recorded protocol tests: passed. They check calendar/value preservation, target isolation, training-only transformations, coverage, episode boundaries, forecast extraction and correction timing.
- Synthetic installed-library checks verify a complete raw NeuralProphet horizon against the target-indexed diagonal; `yhat1` alone has only one valid future lead in that example.
- NeuralProphet training uses complete episodes with shared global components/normalization; no gap-crossing windows or synthetic target labels. Its 0.9.0 prediction preprocessing requires a narrowly scoped compatibility path when seasons and unknown future targets are present. Training imputation stays disabled.
- SARIMAX low-memory results need terminal-filter-state initialization for the first state refresh. The wrapper matches normal state updating on the synthetic check, including missing revealed targets, and does not re-estimate parameters.

## Bounded pilot results

| Model | Fit time | Forecast time | Peak group RSS | Qualification |
|---|---|---|---|---|
| prophet | 16.15 s | 0.013 s | 401.2 MiB | additive configuration; validation selection pending |
| statsmodels | 168.57 s | 0.014 s | 239.8 MiB | 10 optimization iterations; convergence not established |
| neuralprophet | 11.37 s | 0.119 s | 1636.0 MiB | 2 feasibility epochs; not validated accuracy |

Pilots use 35,568 historical calendar hours before the first training-only validation origin (2024-12-16 01:00), and forecast 168 hours without future target inputs. CPU threads are fixed at two. No pilot MAE/ranking is presented as a research result.

## Compute estimate

These are rough linear projections from the recorded pilots, not reserved runtime or measured complete experiments. Budget includes full proposed model-fit counts before any reuse of identical initial fits. Predictions, preprocessing, imports and analysis add overhead; allow for expanding histories and convergence retries.

- Prophet: 22 fits, approximately 0.10 fit-hours at the pilot rate.
- SARIMAX: 24 fits, approximately 5.62–22.48 fit-hours projecting 50–200 iterations. Different orders can differ substantially; the short pilot is not convergence evidence.
- NeuralProphet: 54 core/sensitivity fits plus two validation candidates, approximately 2.68–4.39 fit-hours projecting 30–50 epochs. Three seeds remain in the proposed core matrix.

The full matrix remains conditional on these estimates and training-only validation. Use sequential resumable runs, a bounded optimizer with explicit convergence reporting, and checkpointed forecasts. A failed/nonconverged final fit must be recorded and addressed; do not silently relax comparability or count it as a successful convergence check.

## Phase 2 boundary

The next work is training-only candidate validation, then the main comparison/baselines/ablations/sensitivities using the documented calendar and information sets. No manuscript or final response claim has been marked complete from this audit alone.

Metadata that cannot be recovered is a documented limitation, not a reason to invent provenance. Phase 4 must explain it and the reduced evaluation coverage explicitly. Review the compute estimates before committing the machine to full experiments.
