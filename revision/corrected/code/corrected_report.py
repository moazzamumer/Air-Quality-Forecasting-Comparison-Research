"""Neutral report of corrected experiment results; no assumed ranking text."""
import numpy as np
import pandas as pd

from .protocol import REVISION


def table(frame):
    fields=list(frame.columns)
    lines=['| '+' | '.join(fields)+' |','| '+' | '.join('---' for _ in fields)+' |']
    for row in frame.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(f'{value:.4f}' if isinstance(value,(float,np.floating)) else
                                  str(value).replace('|','\\|') for value in row)+' |')
    return '\n'.join(lines)


def write_report(metrics, paired, alpha, high, high_week, descriptive,
                 coefficients, components, timing, events, strict, threshold):
    selected = [f'{family}_{regime}_s42' for family in ('sarimax','prophet','neuralprophet')
                for regime in ('frozen','walk')]
    selected += [f'{family}_frozen_s42_ewma03' for family in ('sarimax','prophet','neuralprophet')]
    selected += ['persistence','daily_persistence','weekly_persistence']
    main = metrics.set_index('stream').loc[selected].reset_index()
    seeds = metrics[metrics.stream.str.match(r'neuralprophet_(frozen|walk)_s(42|123|2026)$')].copy()
    seeds['regime'] = seeds.stream.str.extract(r'neuralprophet_(frozen|walk)_')
    seed_summary = seeds.groupby('regime').agg(seed_count=('pooled_mae','size'),
        pooled_mae_mean=('pooled_mae','mean'),pooled_mae_sd=('pooled_mae','std'),
        weekly_mae_mean=('mean_weekly_mae','mean'),weekly_mae_sd_across_seeds=('mean_weekly_mae','std')).reset_index()
    seed_summary.to_csv(REVISION/'artifacts/phase3/neuralprophet_seed_summary.csv',index=False)
    # Hourly weighting is explicit because four weeks have fewer scored hours.
    component = components.groupby('component').apply(lambda d:pd.Series({
        'hours':int(d.hours.sum()),
        'hour_weighted_mean_signed':np.average(d.mean_signed,weights=d.hours),
        'hour_weighted_mean_absolute':np.average(d.mean_absolute,weights=d.hours)}),
        include_groups=False).reset_index()
    component.to_csv(REVISION/'artifacts/phase3/prophet_component_summary.csv',index=False)
    timing = timing.copy()
    timing['walk_week'] = pd.to_numeric(timing.run_id.str.extract(r'_w(\d+)_')[0],errors='coerce')
    timing_rows = timing[(timing.regime=='walk') & timing.fit_executed & (timing.walk_week>1)]
    timing_summary = timing_rows.groupby(['family','fit_timer_boundary']).agg(
        fits=('source_fit_seconds','size'),median_fit_seconds=('source_fit_seconds','median'),
        minimum_fit_seconds=('source_fit_seconds','min'),maximum_fit_seconds=('source_fit_seconds','max')).reset_index()
    timing_summary.to_csv(REVISION/'artifacts/phase3/timing_by_boundary.csv',index=False)
    event_summary = events.groupby('phase').agg(events=('returncode','size'),
        failed=('returncode',lambda x:int((x!=0).sum())),
        actual_wall_hours=('elapsed_seconds',lambda x:float(x.sum()/3600)),
        largest_sampled_peak_rss_mib=('sampled_peak_rss_mib','max')).reset_index()
    no_correction = strict[~strict.stream.str.endswith('ewma03')]
    assert no_correction.maximum_prediction_difference.max() < 1e-8
    lines = [
        '# Corrected-input Phase 3 analysis','',
        'Generated from the verified pollutant-invalid-input-v2 run streams. All model settings were selected on corrected training-only validation. This is retrospective Perfect Prognosis evaluation, with actual future gas inputs supplied to each core model. The source PM2.5 targets, 23 weekly origins, 3,624 scored hours and common mask are unchanged.','',
        '## Main results','',table(main[['stream','hours','pooled_mae','pooled_rmse','mean_weekly_mae','weekly_mae_sd']]),'',
        'Pooled errors weight scored hours equally; weekly means weight the 23 calendar origins equally. Four weeks have partial target coverage. A table value alone does not establish a universal ordering.','',
        '## Matched weekly comparisons','',table(paired[['contrast','mean_weekly_mae_difference','weekly_difference_sd',
            'ci95_block3_low','ci95_block3_high','ci95_block2_low','ci95_block2_high','ci95_block4_low','ci95_block4_high']]),'',
        'A negative A−B difference favors A. Intervals come from 2,000 moving-block bootstrap replicates with a 3-week primary block and 2/4-week sensitivity. The sample contains only 23 dependent weeks; the intervals are descriptive and not multiplicity-adjusted. NeuralProphet paired losses average the three seed-level losses by week.','',
        '## Seed variability','',table(seeds[['stream','pooled_mae','pooled_rmse','mean_weekly_mae']]),'',
        table(seed_summary),'',
        'The sample SD above is variability across three training seeds, distinct from weekly error SD and from a forecast ensemble.','',
        '## EWMA and predictor controls','',
        'Alpha 0.3 was predefined. The alpha grid below is a sensitivity analysis; no alpha is selected from test performance. Bias is applied before each week and updated only from its completed scored-hour base residuals.','',
        table(alpha[['family','seed','alpha','mean_weekly_mae','mean_weekly_improvement','beneficial_weeks']]),'',
        table(metrics[metrics.stream.str.endswith(('_frozen_no_inputs','_frozen_broad','_frozen_clip'))][
            ['stream','pooled_mae','pooled_rmse','mean_weekly_mae']]),'',
        'Broad-input controls include future PM10 under Perfect Prognosis. No-input controls retain the selected settings, so these are input ablations rather than newly tuned univariate competitors. Predictor clipping is a training-quantile sensitivity only; the target is never clipped.','',
        '## High concentrations and lead time','',
        f'The high-event threshold is the training target 95th percentile ({threshold:.3f} PM2.5 units). The same scored target hours define every model comparison.','',
        table(high[high.stream.isin(selected)][['stream','hours','mae','rmse']]),'',
        f'High-event hours in the primary selected SARIMAX stream occur in {high_week[high_week.stream=="sarimax_frozen_s42"].window.nunique()} weeks; the subset is small and clustered. Full timestamp, hourly-lead and day-lead records are saved in the phase3 artifacts.','',
        '[Lead-hour figure](../artifacts/phase3/figures/lead_hour_mae.pdf) · [Lead-day figure](../artifacts/phase3/figures/lead_day_mae.pdf) · [Weekly chronology](../artifacts/phase3/figures/weekly_mae_chronology.pdf) · [Weekly distribution](../artifacts/phase3/figures/weekly_mae_distribution.pdf) · [Correction diagnostic](../artifacts/phase3/figures/correction_diagnostics.pdf) · [Regime comparison](../artifacts/phase3/figures/regime_comparison.pdf)','',
        '## Model interpretation','',
        'SARIMAX and Prophet fitted coefficients are saved per run in `../artifacts/phase3/coefficients.csv`. These are conditional associations of scaled predictors; they do not establish causal pollutant effects. The Prophet component means below weight each scored hour equally. Large positive and negative components can cancel.','',
        table(component),'',
        '## Runtime and resources','',
        'The next table includes only newly fitted walk origins 2–23. Original fitting timers include import/model setup in some runs; numerical SARIMAX recovery timers cover optimization only. They are separated by timer boundary, and cannot be used as a single controlled speed ratio. Source forecast time for a reused first-origin prediction is preserved in `core_timing.csv`; reuse overhead does not mean zero model forecast cost.','',
        table(timing_summary),'',table(event_summary),'',
        'Supervisor wall hours count actual sequential attempts including startup and failures. Peak RSS is sampled; a short-lived peak may be missed. All revised fits used local CPU with two configured model threads. EWMA arithmetic timings exclude model fitting, CSV I/O and plotting.','',
        '## Complete-context sensitivity','',
        'The 16 complete-context weeks are selected from these corrected 23-week base streams. For alpha 0.3, the strict skip/carry policy updates bias only after those 16 completed weeks, while the primary policy updates after every partially observed week. The table reports both policies without mixing old uncorrected model forecasts.','',
        table(strict[['stream','strict_pooled_mae','broader_subset_pooled_mae','strict_minus_broader_subset_mae']]),'',
        '## Scope and limitations','',
        'Input invalid codes have been marked missing only in the versioned working calendar. Historical inference filling, including a 120-hour gap, remains an assumption; its reconstruction errors are documented. Baselines lack future gases. The source series comprises API-derived estimates rather than independently authenticated station readings, and original API response archives are unavailable. The test period was examined during the earlier study and revision, so these results are a transparent revised retrospective analysis rather than a previously untouched confirmatory evaluation. The short test season cannot establish year-round or geographic generalization.','',
        'These results are evidence for author review. Manuscript wording and the point-by-point response remain separate tasks.',''
    ]
    (REVISION/'reports/PHASE3_RESULTS.md').write_text('\n'.join(lines)+'\n')
