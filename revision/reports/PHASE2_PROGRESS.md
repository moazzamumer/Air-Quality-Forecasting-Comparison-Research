# Phase 2 progress

The trained-model matrix is computationally long and runs sequentially. This file reports observed state, not promised results.

## Baselines

| run | windows | hours | mean_weekly_mae | weekly_mae_sd | pooled_rmse |
| --- | --- | --- | --- | --- | --- |
| daily_persistence | 16 | 2688 | 131.184 | 117.026 | 222.425 |
| persistence | 16 | 2688 | 125.373 | 108.134 | 203.8 |
| weekly_persistence | 16 | 2688 | 164.586 | 132.046 | 268.421 |

## Trained runs

| stage | status | count |
| --- | --- | --- |
| ablate | completed | 8 |
| ablate | failed | 1 |
| core | completed | 80 |
| core | failed | 5 |
| recovery | completed | 6 |
| validate | completed | 7 |
| validate | failed | 1 |

### Failures

| run_id | error |
| --- | --- |
| ablate_sarimax_clip | RuntimeError: SARIMAX did not converge under bounded optimizer policy |
| core_sarimax_walk_w02_s42 | RuntimeError: SARIMAX did not converge under bounded optimizer policy |
| core_sarimax_walk_w17_s42 | RuntimeError: SARIMAX did not converge under bounded optimizer policy |
| core_sarimax_walk_w18_s42 | RuntimeError: SARIMAX did not converge under bounded optimizer policy |
| core_sarimax_walk_w20_s42 | RuntimeError: SARIMAX did not converge under bounded optimizer policy |
| core_sarimax_walk_w21_s42 | RuntimeError: SARIMAX did not converge under bounded optimizer policy |
| validate_sarimax_1 | RuntimeError: SARIMAX did not converge under bounded optimizer policy |

## Training-only selected settings

```json
{
  "sarimax": {
    "order": [
      1,
      0,
      1
    ],
    "seasonal_order": [
      1,
      0,
      1,
      24
    ]
  },
  "prophet": {
    "seasonality_mode": "additive"
  },
  "neuralprophet": {
    "epochs": 50
  }
}
```

Complete original-policy core/ablation tasks: 88 of 94. Shared initial forecasts are included and explicitly marked as reused in metadata.

## Verified coverage including numerical recoveries

Verified tasks: 94/94; accepted recoveries: 6; unresolved failures: 0; integrity errors: 0.

Original failures above remain in the audit trail. `verified_coverage.csv` maps each task to its accepted original or recovery forecast. This section reflects the latest verifier run; rerun verification after additional fitting.

## Frozen correction replay

Saved correction streams: 35 (no correction plus six predefined alpha settings per complete frozen run).

| run_id | alpha | mean_weekly_mae | pooled_rmse |
| --- | --- | --- | --- |
| core_sarimax_frozen_s42 | 0.3 | 29.4787 | 45.2745 |
| core_prophet_frozen_s42 | 0.3 | 35.7438 | 48.7719 |
| core_neuralprophet_frozen_s42 | 0.3 | 33.303 | 48.0548 |
| core_neuralprophet_frozen_s123 | 0.3 | 35.2739 | 48.946 |
| core_neuralprophet_frozen_s2026 | 0.3 | 34.6829 | 48.0475 |

These are point estimates at the predefined alpha. Paired uncertainty and interpretation belong to Phase 3; no test-optimal alpha is selected.

Complete comparison requires the selected validation settings, all eligible core runs, and all planned ablations. Results may change from the submitted paper.
