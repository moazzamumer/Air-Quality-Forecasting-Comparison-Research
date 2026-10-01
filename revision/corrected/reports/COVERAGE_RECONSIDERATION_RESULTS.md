# Broader coverage reconsideration results

Verified ready: **False**; accepted tasks: 128/129.

The schedule retains 23 full calendar weeks / 3,864 hours. The shared observed-only mask scores 3,624 hours: 19 complete weeks and four partially observed weeks. The final 163-hour remainder is reported separately and not included.

Four invalid training pollutant input cells are treated as missing in the corrected working calendar. The chronological split, seed design, and target missingness policies are unchanged. Dense historical inference context uses causal weekly seasonal filling only where observations are absent; filling counts are recorded. Training and scoring targets are never filled.

Unavailable future-input hours are not scored and their predictions are masked. Each affected fitted-model/origin passes a perturbation check proving its scored predictions are unchanged by computational placeholders at unavailable-input timestamps. This guarantee is implementation-specific, not a general property of other models.

## Core descriptive results

| family | regime | variant | seed | windows | hours | pooled_mae | pooled_rmse | mean_weekly_mae | weekly_mae_sd | mean_weekly_rmse | weekly_rmse_sd | strict_subset_pooled_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| neuralprophet | frozen | selected | 42 | 23 | 3624 | 53.392 | 70.169 | 53.1214 | 27.6774 | 63.2349 | 29.6546 | 55.2941 |
| neuralprophet | frozen | selected | 123 | 23 | 3624 | 52.367 | 67.9626 | 52.2581 | 24.3657 | 62.4457 | 26.2552 | 53.6372 |
| neuralprophet | frozen | selected | 2026 | 23 | 3624 | 34.8914 | 46.7738 | 35.795 | 12.8728 | 45.0542 | 15.8667 | 32.7797 |
| neuralprophet | walk | selected | 42 | 23 | 3624 | 41.949 | 56.5118 | 42.383 | 17.8048 | 52.5364 | 21.7874 | 39.8646 |
| neuralprophet | walk | selected | 123 | 23 | 3624 | 42.2525 | 56.5751 | 42.6796 | 16.8244 | 53.0244 | 20.5748 | 40.3871 |
| neuralprophet | walk | selected | 2026 | 23 | 3624 | 34.6136 | 46.4417 | 35.4776 | 12.6596 | 44.6977 | 15.7374 | 32.6228 |
| prophet | frozen | selected | 42 | 23 | 3624 | 43.9288 | 57.5603 | 44.2017 | 15.3791 | 54.7047 | 18.5085 | 44.1489 |
| prophet | walk | selected | 42 | 23 | 3624 | 38.7203 | 51.1347 | 39.0121 | 11.8019 | 49.1524 | 14.892 | 36.6942 |
| sarimax | frozen | selected | 42 | 23 | 3624 | 30.4841 | 46.9642 | 30.6584 | 14.9911 | 41.7411 | 21.8499 | 29.6184 |
| sarimax | walk | selected | 42 | 23 | 3624 | 30.4296 | 46.8778 | 30.5969 | 14.9156 | 41.6585 | 21.7817 | 29.5783 |

Pooled MAE weights observed hours equally; mean weekly MAE weights weeks equally and differs when coverage varies. Report both, weekly SD and coverage. No full-week accuracy claim is supported by a partially scored week.

## Frozen controls

| family | regime | variant | seed | windows | hours | pooled_mae | pooled_rmse | mean_weekly_mae | weekly_mae_sd | mean_weekly_rmse | weekly_rmse_sd | strict_subset_pooled_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| neuralprophet | frozen | broad | 42 | 23 | 3624 | 22.3452 | 33.2919 | 23.3875 | 9.7005 | 31.932 | 13.3578 | 20.9312 |
| neuralprophet | frozen | clip | 42 | 23 | 3624 | 58.2802 | 75.9513 | 57.8862 | 28.0614 | 69.8855 | 28.4666 | 60.8459 |
| neuralprophet | frozen | no_inputs | 42 | 23 | 3624 | 119.4993 | 177.0235 | 117.1411 | 87.6031 | 140.1736 | 104.1902 | 127.4624 |
| neuralprophet | frozen | selected | 42 | 23 | 3624 | 53.392 | 70.169 | 53.1214 | 27.6774 | 63.2349 | 29.6546 | 55.2941 |
| prophet | frozen | broad | 42 | 23 | 3624 | 15.8687 | 27.5719 | 15.5593 | 7.1099 | 23.5255 | 13.4924 | 14.3936 |
| prophet | frozen | clip | 42 | 23 | 3624 | 47.6791 | 62.7614 | 47.8034 | 15.5782 | 59.956 | 18.7141 | 48.7812 |
| prophet | frozen | no_inputs | 42 | 23 | 3624 | 134.0666 | 190.3955 | 130.9544 | 86.8094 | 156.937 | 102.3784 | 146.8411 |
| prophet | frozen | selected | 42 | 23 | 3624 | 43.9288 | 57.5603 | 44.2017 | 15.3791 | 54.7047 | 18.5085 | 44.1489 |
| sarimax | frozen | clip | 42 | 23 | 3624 | 33.1674 | 51.5463 | 33.2549 | 14.3852 | 46.5007 | 22.0315 | 32.6415 |
| sarimax | frozen | no_inputs | 42 | 23 | 3624 | 115.2377 | 173.535 | 113.0628 | 89.9039 | 134.9151 | 105.8064 | 124.3825 |
| sarimax | frozen | selected | 42 | 23 | 3624 | 30.4841 | 46.9642 | 30.6584 | 14.9911 | 41.7411 | 21.8499 | 29.6184 |

## Baselines

| run | windows | hours | pooled_mae | pooled_rmse | mean_weekly_mae | weekly_mae_sd | mean_weekly_rmse | weekly_rmse_sd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| persistence | 23 | 3624 | 125.7377 | 198.3266 | 127.7769 | 106.3919 | 157.2341 | 123.9935 |
| daily_persistence | 23 | 3624 | 121.5214 | 202.3411 | 119.5283 | 102.2088 | 153.6187 | 127.9374 |
| weekly_persistence | 23 | 3624 | 152.9031 | 248.6467 | 149.8121 | 119.293 | 193.4921 | 151.1543 |

## Limitations and continuity

The original raw data and notebook are preserved. This retains the 23-week calendar schedule and supports a corrected 16-week sensitivity; it does not recreate irregular row chunks in the old notebook. Only the identical first-origin corrected frozen fit/forecast is reused for the corresponding weekly-refit task. Historical filling is a substantive inference assumption, particularly for 120 missing context hours. Fixed-rule reconstruction errors on training-only masked histories are saved without using test performance to choose a fill method.

The broader correction streams update on observed-hour residual means after each of the 23 weeks. The strict sensitivity keeps its original skip/carry policy. On the 16-week subset, correction values can therefore differ between policies even when base forecasts agree; disclose this rather than claiming identical correction experiments.

New fits and first-origin source reuse are identified in run metadata. Resource accounting must distinguish the source forecast cost from the overhead of reuse.

Phase 3 remains pending. Statistical comparisons, residual/lead-time diagnostics and figures will use this documented corrected-input protocol.

## Final evidence checks

The final checker accepted 128/129 tasks, all three baselines and 35 correction streams with no integrity errors. The input audit verified all 21 original file fingerprints.

Among the 128 accepted tasks, 123 execute new fits and 5 reuse an identical first-origin frozen forecast. The broad-input SARIMAX control failed convergence and has no accepted forecasts. The largest scored-forecast change under unavailable-input placeholder perturbation is 0.

Week 12 persistence repeats the last genuinely observed target, 257.0 at 2025-03-30 00:00, rather than a filled last hour. Source timestamps and all baseline definitions/checksums are in `artifacts/coverage_reconsideration/baselines/definitions.json`.

All 120 main experiment tasks and eight controls pass saved-evidence checks. The declared failed control is excluded transparently; the all-task success flag remains false. Phase 3 uses these accepted streams.
