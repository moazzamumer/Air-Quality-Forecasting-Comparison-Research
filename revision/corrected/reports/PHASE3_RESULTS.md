# Corrected-input Phase 3 analysis

**Campaign status: 128 successful tasks, one declared failed broad-input SARIMAX control. All 120 main experiment tasks succeeded. The failed control exhausted both bounded solver attempts; its nonconverged estimates are preserved, and no forecasts or performance claims from that control enter these tables.**

Generated from the verified pollutant-invalid-input-v2 run streams. All model settings were selected on corrected training-only validation. This is retrospective Perfect Prognosis evaluation, with actual future gas inputs supplied to each core model. The source PM2.5 targets, 23 weekly origins, 3,624 scored hours and common mask are unchanged.

## Main results

| stream | hours | pooled_mae | pooled_rmse | mean_weekly_mae | weekly_mae_sd |
| --- | --- | --- | --- | --- | --- |
| sarimax_frozen_s42 | 3624 | 30.4841 | 46.9642 | 30.6584 | 14.9911 |
| sarimax_walk_s42 | 3624 | 30.4296 | 46.8778 | 30.5969 | 14.9156 |
| prophet_frozen_s42 | 3624 | 43.9288 | 57.5603 | 44.2017 | 15.3791 |
| prophet_walk_s42 | 3624 | 38.7203 | 51.1347 | 39.0121 | 11.8019 |
| neuralprophet_frozen_s42 | 3624 | 53.3920 | 70.1690 | 53.1214 | 27.6774 |
| neuralprophet_walk_s42 | 3624 | 41.9490 | 56.5118 | 42.3830 | 17.8048 |
| sarimax_frozen_s42_ewma03 | 3624 | 29.9385 | 43.8022 | 30.1664 | 13.1277 |
| prophet_frozen_s42_ewma03 | 3624 | 37.6869 | 49.9687 | 38.0683 | 10.8419 |
| neuralprophet_frozen_s42_ewma03 | 3624 | 37.6182 | 50.9084 | 38.2899 | 12.5658 |
| persistence | 3624 | 125.7377 | 198.3266 | 127.7769 | 106.3919 |
| daily_persistence | 3624 | 121.5214 | 202.3411 | 119.5283 | 102.2088 |
| weekly_persistence | 3624 | 152.9031 | 248.6467 | 149.8121 | 119.2930 |

Pooled errors weight scored hours equally; weekly means weight the 23 calendar origins equally. Four weeks have partial target coverage. A table value alone does not establish a universal ordering.

## Matched weekly comparisons

| contrast | mean_weekly_mae_difference | weekly_difference_sd | ci95_block3_low | ci95_block3_high | ci95_block2_low | ci95_block2_high | ci95_block4_low | ci95_block4_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sarimax: EWMA 0.3 − base | -0.4920 | 6.2597 | -3.9119 | 2.2516 | -3.6041 | 2.2211 | -3.9591 | 2.0979 |
| prophet: EWMA 0.3 − base | -6.1334 | 12.5882 | -14.0112 | -0.9913 | -12.9361 | -1.2191 | -14.5572 | -0.3749 |
| neuralprophet: EWMA 0.3 − base | -9.2545 | 14.1831 | -18.9765 | -0.2511 | -17.0219 | -2.0587 | -20.1134 | 0.3313 |
| EWMA(0.3) frozen SARIMAX − EWMA(0.3) frozen Prophet | -7.9019 | 9.0106 | -11.3327 | -3.6261 | -11.2307 | -3.8499 | -11.5932 | -4.1070 |
| EWMA(0.3) frozen Prophet − weekly-refit Prophet | -0.9438 | 3.5088 | -1.8950 | 0.7273 | -2.1682 | 0.5629 | -1.8627 | 0.7388 |
| sarimax frozen − weekly persistence | -119.1537 | 122.6219 | -195.3827 | -43.8665 | -182.5803 | -57.1578 | -203.9436 | -31.9345 |
| sarimax walk − weekly persistence | -119.2151 | 122.5660 | -195.4323 | -43.9708 | -182.6115 | -57.2234 | -203.9878 | -32.0056 |
| prophet frozen − weekly persistence | -105.6103 | 125.8105 | -184.1033 | -28.5285 | -170.3400 | -41.4138 | -193.8384 | -14.6088 |
| prophet walk − weekly persistence | -110.7999 | 124.0113 | -188.7317 | -35.6099 | -175.6054 | -49.4773 | -197.6719 | -23.8670 |
| neuralprophet frozen − weekly persistence | -102.7539 | 132.4209 | -186.4550 | -22.6444 | -171.2718 | -36.0896 | -195.9782 | -7.0154 |
| neuralprophet walk − weekly persistence | -109.6320 | 126.2644 | -188.1631 | -31.0799 | -174.6387 | -45.8459 | -197.5552 | -18.2349 |

A negative A−B difference favors A. Intervals come from 2,000 moving-block bootstrap replicates with a 3-week primary block and 2/4-week sensitivity. The sample contains only 23 dependent weeks; the intervals are descriptive and not multiplicity-adjusted. NeuralProphet paired losses average the three seed-level losses by week.

## Seed variability

| stream | pooled_mae | pooled_rmse | mean_weekly_mae |
| --- | --- | --- | --- |
| neuralprophet_frozen_s42 | 53.3920 | 70.1690 | 53.1214 |
| neuralprophet_walk_s42 | 41.9490 | 56.5118 | 42.3830 |
| neuralprophet_frozen_s123 | 52.3670 | 67.9626 | 52.2581 |
| neuralprophet_walk_s123 | 42.2525 | 56.5751 | 42.6796 |
| neuralprophet_frozen_s2026 | 34.8914 | 46.7738 | 35.7950 |
| neuralprophet_walk_s2026 | 34.6136 | 46.4417 | 35.4776 |

| regime | seed_count | pooled_mae_mean | pooled_mae_sd | weekly_mae_mean | weekly_mae_sd_across_seeds |
| --- | --- | --- | --- | --- | --- |
| frozen | 3 | 46.8835 | 10.3981 | 47.0581 | 9.7637 |
| walk | 3 | 39.6050 | 4.3253 | 40.1801 | 4.0752 |

The sample SD above is variability across three training seeds, distinct from weekly error SD and from a forecast ensemble.

## EWMA and predictor controls

Alpha 0.3 was predefined. The alpha grid below is a sensitivity analysis; no alpha is selected from test performance. Bias is applied before each week and updated only from its completed scored-hour base residuals.

| family | seed | alpha | mean_weekly_mae | mean_weekly_improvement | beneficial_weeks |
| --- | --- | --- | --- | --- | --- |
| neuralprophet | 42 | 0.0000 | 53.1214 | -0.0000 | 0 |
| neuralprophet | 42 | 0.1000 | 44.2750 | 8.8464 | 14 |
| neuralprophet | 42 | 0.2000 | 40.3141 | 12.8073 | 14 |
| neuralprophet | 42 | 0.3000 | 38.2899 | 14.8315 | 13 |
| neuralprophet | 42 | 0.5000 | 36.3181 | 16.8033 | 14 |
| neuralprophet | 42 | 0.7000 | 35.3600 | 17.7613 | 14 |
| neuralprophet | 42 | 1.0000 | 34.7105 | 18.4109 | 16 |
| neuralprophet | 123 | 0.0000 | 52.2581 | -0.0000 | 0 |
| neuralprophet | 123 | 0.1000 | 43.6055 | 8.6525 | 13 |
| neuralprophet | 123 | 0.2000 | 40.2692 | 11.9888 | 13 |
| neuralprophet | 123 | 0.3000 | 38.7319 | 13.5262 | 14 |
| neuralprophet | 123 | 0.5000 | 37.1676 | 15.0905 | 14 |
| neuralprophet | 123 | 0.7000 | 36.3185 | 15.9396 | 14 |
| neuralprophet | 123 | 1.0000 | 35.6698 | 16.5882 | 15 |
| neuralprophet | 2026 | 0.0000 | 35.7950 | 0.0000 | 0 |
| neuralprophet | 2026 | 0.1000 | 36.0921 | -0.2971 | 12 |
| neuralprophet | 2026 | 0.2000 | 36.2897 | -0.4947 | 10 |
| neuralprophet | 2026 | 0.3000 | 36.3891 | -0.5941 | 10 |
| neuralprophet | 2026 | 0.5000 | 36.5879 | -0.7929 | 10 |
| neuralprophet | 2026 | 0.7000 | 36.8355 | -1.0405 | 9 |
| neuralprophet | 2026 | 1.0000 | 37.6695 | -1.8745 | 6 |
| prophet | 42 | 0.0000 | 44.2017 | -0.0000 | 0 |
| prophet | 42 | 0.1000 | 41.5790 | 2.6227 | 16 |
| prophet | 42 | 0.2000 | 39.3345 | 4.8673 | 17 |
| prophet | 42 | 0.3000 | 38.0683 | 6.1334 | 17 |
| prophet | 42 | 0.5000 | 36.9783 | 7.2235 | 18 |
| prophet | 42 | 0.7000 | 36.6679 | 7.5338 | 17 |
| prophet | 42 | 1.0000 | 36.7678 | 7.4340 | 17 |
| sarimax | 42 | 0.0000 | 30.6584 | -0.0000 | 0 |
| sarimax | 42 | 0.1000 | 29.4959 | 1.1625 | 14 |
| sarimax | 42 | 0.2000 | 29.9209 | 0.7374 | 14 |
| sarimax | 42 | 0.3000 | 30.1664 | 0.4920 | 14 |
| sarimax | 42 | 0.5000 | 30.3823 | 0.2760 | 10 |
| sarimax | 42 | 0.7000 | 30.5990 | 0.0594 | 10 |
| sarimax | 42 | 1.0000 | 31.3302 | -0.6719 | 10 |

| stream | pooled_mae | pooled_rmse | mean_weekly_mae |
| --- | --- | --- | --- |
| sarimax_frozen_no_inputs | 115.2377 | 173.5350 | 113.0628 |
| sarimax_frozen_clip | 33.1674 | 51.5463 | 33.2549 |
| prophet_frozen_no_inputs | 134.0666 | 190.3955 | 130.9544 |
| prophet_frozen_broad | 15.8687 | 27.5719 | 15.5593 |
| prophet_frozen_clip | 47.6791 | 62.7614 | 47.8034 |
| neuralprophet_frozen_no_inputs | 119.4993 | 177.0235 | 117.1411 |
| neuralprophet_frozen_broad | 22.3452 | 33.2919 | 23.3875 |
| neuralprophet_frozen_clip | 58.2802 | 75.9513 | 57.8862 |

Broad-input controls include future PM10 under Perfect Prognosis. No-input controls retain the selected settings, so these are input ablations rather than newly tuned univariate competitors. Predictor clipping is a training-quantile sensitivity only; the target is never clipped.

## High concentrations and lead time

The high-event threshold is the training target 95th percentile (691.335 PM2.5 units). The same scored target hours define every model comparison.

| stream | hours | mae | rmse |
| --- | --- | --- | --- |
| sarimax_frozen_s42 | 158 | 51.0233 | 67.6887 |
| sarimax_walk_s42 | 158 | 50.9902 | 67.6335 |
| sarimax_frozen_s42_ewma03 | 158 | 47.6734 | 63.9926 |
| prophet_frozen_s42 | 158 | 50.6003 | 61.7567 |
| prophet_walk_s42 | 158 | 49.9507 | 60.5918 |
| prophet_frozen_s42_ewma03 | 158 | 49.9371 | 60.7731 |
| neuralprophet_frozen_s42 | 158 | 32.3232 | 41.3469 |
| neuralprophet_walk_s42 | 158 | 32.1465 | 40.8800 |
| neuralprophet_frozen_s42_ewma03 | 158 | 32.6730 | 41.8389 |
| persistence | 158 | 320.6741 | 367.6844 |
| daily_persistence | 158 | 556.2925 | 601.7356 |
| weekly_persistence | 158 | 536.7977 | 612.3323 |

High-event hours in the primary selected SARIMAX stream occur in 6 weeks; the subset is small and clustered. Full timestamp, hourly-lead and day-lead records are saved in the phase3 artifacts.

[Lead-hour figure](../artifacts/phase3/figures/lead_hour_mae.pdf) · [Lead-day figure](../artifacts/phase3/figures/lead_day_mae.pdf) · [Weekly chronology](../artifacts/phase3/figures/weekly_mae_chronology.pdf) · [Weekly distribution](../artifacts/phase3/figures/weekly_mae_distribution.pdf) · [Correction diagnostic](../artifacts/phase3/figures/correction_diagnostics.pdf) · [Regime comparison](../artifacts/phase3/figures/regime_comparison.pdf)

## Model interpretation

SARIMAX and Prophet fitted coefficients are saved per run in `../artifacts/phase3/coefficients.csv`. These are conditional associations of scaled predictors; they do not establish causal pollutant effects. The Prophet component means below weight each scored hour equally. Large positive and negative components can cancel.

| component | hours | hour_weighted_mean_signed | hour_weighted_mean_absolute |
| --- | --- | --- | --- |
| co | 3624.0000 | -79.0426 | 237.5345 |
| daily | 3624.0000 | -0.0000 | 19.1752 |
| no | 3624.0000 | 17.3425 | 38.4479 |
| no2 | 3624.0000 | -20.2087 | 43.5495 |
| so2 | 3624.0000 | 7.3084 | 25.0211 |
| trend | 3624.0000 | 221.4793 | 221.4793 |
| weekly | 3624.0000 | 0.0157 | 4.0505 |
| yearly | 3624.0000 | -0.3946 | 10.1196 |

## Runtime and resources

The next table includes only newly fitted walk origins 2–23. Original fitting timers include import/model setup in some runs; numerical SARIMAX recovery timers cover optimization only. They are separated by timer boundary, and cannot be used as a single controlled speed ratio. Source forecast time for a reused first-origin prediction is preserved in `core_timing.csv`; reuse overhead does not mean zero model forecast cost.

| family | fit_timer_boundary | fits | median_fit_seconds | minimum_fit_seconds | maximum_fit_seconds |
| --- | --- | --- | --- | --- | --- |
| neuralprophet | fit_including_initialization | 66 | 182.0163 | 170.6299 | 202.5884 |
| prophet | fit_including_initialization | 22 | 23.9141 | 16.2201 | 33.7392 |
| sarimax | optimization_only | 22 | 110.1251 | 51.1785 | 215.0583 |

| phase | events | failed | recorded_attempt_wall_hours | largest_sampled_peak_rss_mib |
| --- | --- | --- | --- | --- |
| broader | 132 | 3 | 6.6260 | 1845.3164 |
| validation | 8 | 1 | 0.9233 | 1639.7148 |

Recorded supervisor attempt wall hours include startup, failures and superseded completions. Interrupted attempts and standalone diagnostic fits without finalized supervisor records are excluded; this is not total project time or a controlled speed comparison. Peak RSS is sampled; a short-lived peak may be missed. All revised fits used local CPU with two configured model threads. EWMA arithmetic timings exclude model fitting, CSV I/O and plotting.

## Complete-context sensitivity

The 16 complete-context weeks are selected from these corrected 23-week base streams. For alpha 0.3, the strict skip/carry policy updates bias only after those 16 completed weeks, while the primary policy updates after every partially observed week. The table reports both policies without mixing old uncorrected model forecasts.

| stream | strict_pooled_mae | broader_subset_pooled_mae | strict_minus_broader_subset_mae |
| --- | --- | --- | --- |
| sarimax_frozen_s42 | 29.6184 | 29.6184 | 0.0000 |
| sarimax_walk_s42 | 29.5783 | 29.5783 | 0.0000 |
| sarimax_frozen_s42_ewma03 | 29.0942 | 29.1530 | -0.0587 |
| prophet_frozen_s42 | 44.1489 | 44.1489 | 0.0000 |
| prophet_walk_s42 | 36.6942 | 36.6942 | 0.0000 |
| prophet_frozen_s42_ewma03 | 39.1569 | 35.7754 | 3.3815 |
| neuralprophet_frozen_s42 | 55.2941 | 55.2941 | 0.0000 |
| neuralprophet_walk_s42 | 39.8646 | 39.8646 | 0.0000 |
| neuralprophet_frozen_s42_ewma03 | 38.6660 | 34.2564 | 4.4096 |
| neuralprophet_frozen_s123 | 53.6372 | 53.6372 | 0.0000 |
| neuralprophet_walk_s123 | 40.3871 | 40.3871 | 0.0000 |
| neuralprophet_frozen_s123_ewma03 | 38.5141 | 34.8048 | 3.7093 |
| neuralprophet_frozen_s2026 | 32.7797 | 32.7797 | 0.0000 |
| neuralprophet_walk_s2026 | 32.6228 | 32.6228 | 0.0000 |
| neuralprophet_frozen_s2026_ewma03 | 32.9952 | 33.1497 | -0.1545 |
| persistence | 125.3727 | 125.3727 | 0.0000 |
| daily_persistence | 131.1845 | 131.1845 | 0.0000 |
| weekly_persistence | 164.5865 | 164.5865 | 0.0000 |
| sarimax_frozen_no_inputs | 124.3825 | 124.3825 | 0.0000 |
| sarimax_frozen_clip | 32.6415 | 32.6415 | 0.0000 |
| prophet_frozen_no_inputs | 146.8411 | 146.8411 | 0.0000 |
| prophet_frozen_broad | 14.3936 | 14.3936 | 0.0000 |
| prophet_frozen_clip | 48.7812 | 48.7812 | 0.0000 |
| neuralprophet_frozen_no_inputs | 127.4624 | 127.4624 | 0.0000 |
| neuralprophet_frozen_broad | 20.9312 | 20.9312 | 0.0000 |
| neuralprophet_frozen_clip | 60.8459 | 60.8459 | 0.0000 |

## Scope and limitations

Input invalid codes have been marked missing only in the versioned working calendar. Historical inference filling, including a 120-hour gap, remains an assumption; its reconstruction errors are documented. Baselines lack future gases. The source series comprises API-derived estimates rather than independently authenticated station readings, and original API response archives are unavailable. The test period was examined during the earlier study and revision, so these results are a transparent revised retrospective analysis rather than a previously untouched confirmatory evaluation. The short test season cannot establish year-round or geographic generalization.

These results are evidence for author review. Manuscript wording and the point-by-point response remain separate tasks.
