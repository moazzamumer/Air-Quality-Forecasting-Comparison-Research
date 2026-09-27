# Adaptive PM2.5 forecasting — research and journal revision

This project compares SARIMAX, Prophet and NeuralProphet for Beijing PM2.5 under
Perfect Prognosis, using weekly walk-forward refitting and frozen parameters
with residual correction. The Scientific Reports revision builds on this study
with implementation corrections and the additional analyses requested in review.

## Start here

- **Original experiments:** [main.ipynb](main.ipynb), preserved unchanged.
- **Revision experiments:** [revision/main_revision.ipynb](revision/main_revision.ipynb), the main notebook entry point for revised work.
- **Current findings:** [Phase 1 summary](revision/reports/PHASE1_SUMMARY.md).
- **Revision tracking:** [plan](revision/REVISION_PLAN.md), [reviewer tracker](revision/REVIEWER_TRACKER.md), and [response draft](revision/RESPONSE_TO_REVIEWERS.md).

## Repository layout

```text
main.ipynb                 Original experimental notebook
data/                      Original local datasets
PM_Forecasting_Environmental_Modeling_Assessment_Submission/
                           Preserved submitted manuscript and figures
revision/
    main_revision.ipynb    Main revision notebook
    code/                  Supporting reusable code
    config/                Recorded experimental protocol
    tests/                 Scientific correctness checks
    reports/               Audit findings and protocol decisions
    artifacts/             Generated evidence and results
legacy/
    scripts/               Earlier standalone forecasting scripts
    notebooks/             Earlier extraction notebook
    outputs/               Original figures and weekly plots
    exploratory/           Other older experimental notebooks
    logs/                  Historical training logs
```

Run the original notebook from the project root so its `./data/` paths continue
to work. Its historical plots are archived; rerunning its original plotting cells
will recreate `regime1_weekly_plots/` at the root. No original notebook cells were
rewritten for this organization change.

See [revision instructions](revision/README.md) for reproducible audit/check
commands and [archive notes](legacy/README.md) for old-file locations. Local
datasets, environments and training logs remain excluded by the existing ignore
policy; this organization does not stage or commit files.
