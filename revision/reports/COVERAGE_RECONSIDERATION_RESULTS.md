# Broader coverage reconsideration results

Verified ready: **True**; accepted tasks: 129/129.

The schedule retains 23 full calendar weeks / 3,864 hours. The shared observed-only mask scores 3,624 hours: 19 complete weeks and four partially observed weeks. The final 163-hour remainder is reported separately and not included.

Training data, chronological split, selected settings, seeds and fitting-target missingness policies remain unchanged. Dense historical inference context uses causal weekly seasonal filling only where observations are absent; filling counts are recorded. Training and scoring targets are never filled.

Unavailable future-input hours are not scored and their predictions are masked. Each affected fitted-model/origin passes a perturbation check proving its scored predictions are unchanged by computational placeholders at unavailable-input timestamps. This guarantee is implementation-specific, not a general property of other models.

## Core descriptive results

| family | regime | variant | seed | windows | hours | pooled_mae | pooled_rmse | mean_weekly_mae | weekly_mae_sd | mean_weekly_rmse | weekly_rmse_sd | strict_subset_pooled_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| neuralprophet | frozen | selected | 42 | 23 | 3624 | 38.4622 | 52.7838 | 38.9168 | 16.073 | 48.9262 | 20.4623 | 38.4425 |
| neuralprophet | frozen | selected | 123 | 23 | 3624 | 39.9792 | 54.2716 | 40.3056 | 15.2776 | 50.8195 | 19.3787 | 40.7011 |
| neuralprophet | frozen | selected | 2026 | 23 | 3624 | 34.8038 | 47.0539 | 35.2997 | 12.9859 | 44.3832 | 16.7408 | 34.4563 |
| neuralprophet | walk | selected | 42 | 23 | 3624 | 35.2827 | 48.8805 | 35.8867 | 13.1816 | 45.6675 | 18.5721 | 34.2246 |
| neuralprophet | walk | selected | 123 | 23 | 3624 | 36.5832 | 50.3294 | 37.11 | 12.5518 | 47.4557 | 17.7491 | 36.0393 |
| neuralprophet | walk | selected | 2026 | 23 | 3624 | 34.5838 | 46.9584 | 35.075 | 13.2028 | 44.1747 | 17.0118 | 34.2501 |
| prophet | frozen | selected | 42 | 23 | 3624 | 38.6483 | 49.7287 | 39.4644 | 12.9389 | 48.1525 | 15.3127 | 36.9634 |
| prophet | walk | selected | 42 | 23 | 3624 | 36.163 | 48.6061 | 36.277 | 11.317 | 45.9949 | 15.384 | 35.4976 |
| sarimax | frozen | selected | 42 | 23 | 3624 | 30.5043 | 47.4289 | 30.6181 | 15.3583 | 41.9444 | 22.3325 | 29.9143 |
| sarimax | walk | selected | 42 | 23 | 3624 | 30.443 | 47.3486 | 30.5486 | 15.3054 | 41.8442 | 22.3027 | 29.8776 |

Pooled MAE weights observed hours equally; mean weekly MAE weights weeks equally and differs when coverage varies. Report both, weekly SD and coverage. No full-week accuracy claim is supported by a partially scored week.

## Frozen controls

| family | regime | variant | seed | windows | hours | pooled_mae | pooled_rmse | mean_weekly_mae | weekly_mae_sd | mean_weekly_rmse | weekly_rmse_sd | strict_subset_pooled_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| neuralprophet | frozen | broad | 42 | 23 | 3624 | 21.5631 | 30.7501 | 22.3623 | 7.6862 | 29.8172 | 10.74 | 20.8682 |
| neuralprophet | frozen | clip | 42 | 23 | 3624 | 57.5315 | 75.0244 | 57.1606 | 27.3897 | 69.148 | 27.8661 | 60.0122 |
| neuralprophet | frozen | no_inputs | 42 | 23 | 3624 | 119.4993 | 177.0235 | 117.1411 | 87.6031 | 140.1736 | 104.1902 | 127.4624 |
| neuralprophet | frozen | selected | 42 | 23 | 3624 | 38.4622 | 52.7838 | 38.9168 | 16.073 | 48.9262 | 20.4623 | 38.4425 |
| prophet | frozen | broad | 42 | 23 | 3624 | 19.8958 | 26.7045 | 19.6515 | 5.6249 | 25.3582 | 7.2947 | 19.9231 |
| prophet | frozen | clip | 42 | 23 | 3624 | 47.2668 | 62.2642 | 47.4247 | 15.324 | 59.5359 | 18.5228 | 48.2797 |
| prophet | frozen | no_inputs | 42 | 23 | 3624 | 134.0666 | 190.3955 | 130.9544 | 86.8094 | 156.937 | 102.3784 | 146.8411 |
| prophet | frozen | selected | 42 | 23 | 3624 | 38.6483 | 49.7287 | 39.4644 | 12.9389 | 48.1525 | 15.3127 | 36.9634 |
| sarimax | frozen | broad | 42 | 23 | 3624 | 17.591 | 24.5215 | 17.4515 | 5.1973 | 22.8964 | 8.0554 | 17.5727 |
| sarimax | frozen | clip | 42 | 23 | 3624 | 33.1689 | 51.572 | 33.2536 | 14.4093 | 46.5098 | 22.0666 | 32.6548 |
| sarimax | frozen | no_inputs | 42 | 23 | 3624 | 115.2365 | 173.533 | 113.0619 | 89.9027 | 134.914 | 105.8048 | 124.3805 |
| sarimax | frozen | selected | 42 | 23 | 3624 | 30.5043 | 47.4289 | 30.6181 | 15.3583 | 41.9444 | 22.3325 | 29.9143 |

## Baselines

| run | windows | hours | pooled_mae | pooled_rmse | mean_weekly_mae | weekly_mae_sd | mean_weekly_rmse | weekly_rmse_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| persistence | 23 | 3624 | 125.7377 | 198.3266 | 127.7769 | 106.3919 | 157.2341 | 123.9935 |
| daily_persistence | 23 | 3624 | 121.5214 | 202.3411 | 119.5283 | 102.2088 | 153.6187 | 127.9374 |
| weekly_persistence | 23 | 3624 | 152.9031 | 248.6467 | 149.8121 | 119.293 | 193.4921 | 151.1543 |

## Limitations and continuity

The original raw data and notebook are preserved. This retains the corrected 23-week calendar schedule and expands the strict 16-week comparison; it does not recreate irregular row chunks in the old notebook. Strict forecasts are reused or reproduced under explicit checks. Historical filling is a substantive inference assumption, particularly for 120 missing context hours. Fixed-rule reconstruction errors on training-only masked histories are saved without using test performance to choose a fill method.

The broader correction streams update on observed-hour residual means after each of the 23 weeks. The strict sensitivity keeps its original skip/carry policy. On the 16-week subset, correction values can therefore differ between policies even when base forecasts agree; disclose this rather than claiming identical correction experiments.

New fits and source-fit reuse are identified in run metadata. Total resource accounting must include the strict runs, failed/recovered attempts, reconstruction, new fitting and invariance checks without counting reused fitting twice.

Phase 3 remains pending. Statistical comparisons, residual/lead-time diagnostics, figures and manuscript/response edits will use this documented broader protocol and the strict sensitivity.

## Final evidence checks

The final checker accepted 129/129 tasks, all three baselines and 35 correction streams with no integrity errors. The preserved strict reference verified all 21 original file fingerprints.

Of the 129 tasks, 45 execute new fits, 80 reuse an earlier complete weekly forecast, and 4 reconstruct a frozen SARIMAX state from a previously fitted parameter vector. The largest difference when reproducing strict-week forecasts is 8.4e-12 in PM2.5 units. The largest scored-forecast change under unavailable-input placeholder perturbation is 0.

Week 12 persistence repeats the last genuinely observed target, 257.0 at 2025-03-30 00:00, rather than a filled last hour. Source timestamps and all baseline definitions/checksums are in `artifacts/coverage_reconsideration/baselines/definitions.json`.

The completed [coverage chart](../artifacts/coverage_reconsideration/coverage.png) separates the original 16 complete-context weeks from the additional observed hours and missing hours. The notebook contains the executed chart and result tables. Twenty-two scientific-contract tests pass. These checks establish the saved evidence and scope; Phase 3 paired inference and manuscript interpretation remain pending.
