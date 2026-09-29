# Phase 3 findings linked to reviewer points

Status: Analysis complete; Phase 4 manuscript text and point-by-point responses pending. Numerical details and limitations are in [the generated results report](PHASE3_RESULTS.md). CSV/PDF evidence is under `../artifacts/phase3/`. The primary result uses the same 23 calendar origins and 3,624 observed target hours for every model; the strict 16-week analysis remains a separate sensitivity.

| Reviewer point | Evidence now available | Implication for manuscript/response |
| --- | --- | --- |
| R1.1; R2.M4 | `performance.csv`, `strict_sensitivity.csv`, `resource_events.csv` | Revised SARIMAX weekly refit completes all 23 origins. State original 21/23 manuscript limitation as corrected, not as if it never existed; use matched 23-origin tables. Report baselines and restrict competitiveness claims to evaluated families. |
| R1.3; R2.M10 | `coefficients.csv`, `prophet_components.csv` | Give fit-specific coefficients, raw-input scaling and Prophet component magnitudes. Do not infer causal pollutant effects. |
| R1.4; R2.M5 | `performance.csv`, `weekly_neuralprophet_*`, preserved training traces | Explain corrected alignment/convergence/normalization checks, seed variation and lead-time patterns. Do not call NeuralProphet inherently weak. |
| R1.6; R2.M10 | `core_timing.csv`, `resource_events.csv`, `correction_timing.csv` | Describe local CPU/two-thread environment, source-fit versus reused costs, wall-time boundaries, attempted recoveries and RSS limitations. Do not compare revised local timings with original Colab as speedups. |
| R1.7; R2.M8 | `correction_alpha_summary.csv`, `correction_weekly.csv`, `figures/correction_diagnostics.pdf`, `paired_contrasts.csv` | Report all predefined α values. α=0.3 helps Prophet in weekly MAE, is small/uncertain for SARIMAX, and varies by NeuralProphet seed. Keep α=0.3 predefined; do not choose the test-best α. |
| R1.8; R2.M9; R2.m4 | `performance.csv`, `paired_contrasts.csv`, `paired_weekly_differences.csv`, `figures/weekly_mae_distribution.pdf` | Separate pooled errors from mean±SD of weekly errors. Present paired 2/3/4-week moving-block intervals and avoid categorical significance claims with 23 weeks. |
| R1.10; R2.M2 | `target_descriptive.csv`, `strict_sensitivity.csv`, prior `phase1/data_audit.json`, `figures/weekly_mae_chronology.pdf` | State original observed PM2.5 range, counts and split. Explain four partially scored weeks, 163-hour remainder, gridded-estimate target, and limited season. |
| R2.M3 | `high_concentration.csv`, `high_concentration_by_week.csv`, `performance.csv` | State original targets are never clipped; predictors alone are clipped in the sensitivity. The 158 high-threshold scored hours occur in six weeks. Seed-42 NeuralProphet is better than selected-gas SARIMAX on this subset, so avoid uniform-ranking claims. |
| R2.M7 | `performance.csv` rows for `*_frozen_no_inputs`, `*_frozen_broad`, `*_frozen_clip` | All three families have the fixed-setting frozen ablations. The broad-input control contains future PM10, a different information advantage under Perfect Prognosis. |
| R2.M9 | `lead_hour.csv`, `forecast_day.csv`, `figures/lead_hour_mae.pdf`, `figures/lead_day_mae.pdf` | Report counts and errors by exact lead and days 1–7. Lead-error curves are nonmonotonic; explain patterns descriptively. |
| R2.m5 | `performance.csv`, `paired_contrasts.csv` | Replace the manuscript's original 7.93/7.94 Prophet difference with revised, generated values computed before rounding; state metric definitions. |

Writing-only or protocol-focused points remain in `../REVIEWER_TRACKER.md`. This ledger records analysis evidence and a writing implication; it does not close any comment before the manuscript and response have been revised.
