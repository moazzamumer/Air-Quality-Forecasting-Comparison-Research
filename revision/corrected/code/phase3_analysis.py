"""Rebuild Phase 3 publication evidence from verified, saved forecast streams.

No model fit or test-informed configuration choice occurs here. Run from the
project root with ``venv/bin/python -m revision.code.phase3_analysis``.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .protocol import ROOT, REVISION, load_calendar, split_position

SOURCE = REVISION / 'artifacts/coverage_reconsideration'
OUT = REVISION / 'artifacts/phase3'
FIG = OUT / 'figures'
SEEDS = (42, 123, 2026)
FAMILIES = ('sarimax', 'prophet', 'neuralprophet')
DAY_COLORS = {'sarimax': '#277da1', 'prophet': '#e67e22',
              'neuralprophet': '#7b3fa0', 'weekly_persistence': '#777777'}


def verified_source():
    v = json.loads((SOURCE / 'verification.json').read_text())
    assert v['ready'] and v['additional_checks_passed']
    assert v['complete_tasks'] == v['expected_tasks'] == 129
    assert not v['pending_tasks'] and not v['integrity_errors']
    assert v['observed_scoring_hours'] == 3624 and v['scheduled_weeks'] == 23
    return v


def stream(path: Path | pd.DataFrame, name: str, prediction: str = 'base_prediction'):
    d = (pd.read_csv(path, parse_dates=['forecast_origin', 'target_timestamp'])
         if isinstance(path, Path) else path.copy())
    for column in ('forecast_origin', 'target_timestamp'):
        d[column] = pd.to_datetime(d[column])
    assert len(d) == 3864 and d.window.nunique() == 23, (path, len(d))
    assert not d[['target_timestamp', 'window']].duplicated().any(), path
    d = d.sort_values(['window', 'lead_hour']).reset_index(drop=True)
    assert d.score_eligible.sum() == 3624 and d[prediction][d.score_eligible].notna().all(), path
    return pd.DataFrame({'stream': name, 'window': d.window, 'forecast_origin': d.forecast_origin,
                         'target_timestamp': d.target_timestamp, 'lead_hour': d.lead_hour,
                         'target': d.original_target, 'score': d.score_eligible,
                         'prediction': d[prediction]})


def load_streams():
    streams = {}
    for family in FAMILIES:
        seeds = SEEDS if family == 'neuralprophet' else (42,)
        for seed in seeds:
            for regime in ('frozen', 'walk'):
                name = f'{family}_{regime}_s{seed}'
                if regime == 'frozen':
                    p = SOURCE / 'runs' / f'core_{name}' / 'forecasts.csv'
                    d = stream(p, name)
                else:
                    parts = [pd.read_csv(SOURCE / 'runs' / f'core_{family}_walk_w{w:02d}_s{seed}' / 'forecasts.csv')
                             for w in range(1, 24)]
                    d = stream(pd.concat(parts, ignore_index=True), name)
                streams[name] = d
            name = f'{family}_frozen_s{seed}_ewma03'
            streams[name] = stream(SOURCE / 'corrections' /
                                   f'core_{family}_frozen_s{seed}_alpha_0p3.csv',
                                   name, 'corrected_prediction')
    for name in ('persistence', 'daily_persistence', 'weekly_persistence'):
        streams[name] = stream(SOURCE / 'baselines' / f'{name}.csv', name)
    for family in FAMILIES:
        for variant in ('no_inputs', 'broad', 'clip'):
            name = f'{family}_frozen_{variant}'
            streams[name] = stream(SOURCE / 'runs' / f'ablate_{family}_{variant}' / 'forecasts.csv', name)
    ref = next(iter(streams.values()))
    for name, d in streams.items():
        assert d[['window', 'forecast_origin', 'target_timestamp', 'lead_hour', 'score']].equals(
            ref[['window', 'forecast_origin', 'target_timestamp', 'lead_hour', 'score']]), name
        np.testing.assert_allclose(d.target, ref.target, rtol=0, atol=0, equal_nan=True)
    return streams


def losses(d):
    a = d.loc[d.score].copy()
    a['error'] = a.prediction - a.target
    a['absolute_error'] = a.error.abs()
    a['squared_error'] = a.error.pow(2)
    a['forecast_day'] = (a.lead_hour.sub(1) // 24 + 1).astype(int)
    return a


def summarize(a):
    week = a.groupby('window', sort=True).agg(hours=('absolute_error', 'size'),
        mae=('absolute_error', 'mean'), mse=('squared_error', 'mean'),
        bias=('error', 'mean'), origin=('forecast_origin', 'first')).reset_index()
    week['rmse'] = np.sqrt(week.mse)
    return week, {'windows': len(week), 'hours': len(a),
        'pooled_mae': a.absolute_error.mean(), 'pooled_rmse': np.sqrt(a.squared_error.mean()),
        'mean_weekly_mae': week.mae.mean(), 'weekly_mae_sd': week.mae.std(ddof=1),
        'mean_weekly_rmse': week.rmse.mean(), 'weekly_rmse_sd': week.rmse.std(ddof=1)}


def bootstrap_difference(d, seed=42, repetitions=2000, blocks=(2, 3, 4)):
    """Moving blocks of adjacent calendar weeks; negative differences favor A."""
    d = np.asarray(d, dtype=float)
    assert len(d) == 23 and np.isfinite(d).all()
    result = {}
    for block in blocks:
        rng = np.random.default_rng(seed + block)
        starts = rng.integers(0, len(d)-block+1,
                              size=(repetitions, int(np.ceil(len(d)/block))))
        indices = (starts[:, :, None] + np.arange(block)).reshape(repetitions, -1)[:, :len(d)]
        samples = d[indices].mean(axis=1)
        result[block] = tuple(np.percentile(samples, [2.5, 97.5]))
    return result


def paired_table(week_metrics):
    weekly = {name: table.set_index('window').mae for name, table in week_metrics.items()}
    def vec(family, regime, correction=False):
        suffix = '_ewma03' if correction else ''
        seeds = SEEDS if family == 'neuralprophet' else (42,)
        return np.mean([weekly[f'{family}_{regime}_s{s}{suffix}'].to_numpy()
                        for s in seeds], axis=0)
    contrasts = []
    for family in FAMILIES:
        contrasts.append((f'{family}: EWMA 0.3 − base',
                          vec(family, 'frozen', True), vec(family, 'frozen')))
    contrasts.extend([
        ('corrected frozen SARIMAX − corrected frozen Prophet',
         vec('sarimax', 'frozen', True), vec('prophet', 'frozen', True)),
        ('corrected frozen Prophet − weekly-refit Prophet',
         vec('prophet', 'frozen', True), vec('prophet', 'walk'))])
    baseline = weekly['weekly_persistence'].to_numpy()
    for family in FAMILIES:
        for regime in ('frozen', 'walk'):
            contrasts.append((f'{family} {regime} − weekly persistence',
                              vec(family, regime), baseline))
    records = []
    differences = []
    for label, left, right in contrasts:
        delta = left-right
        bands = bootstrap_difference(delta)
        records.append(dict(contrast=label, weeks=len(delta), mean_weekly_mae_difference=delta.mean(),
            weekly_difference_sd=delta.std(ddof=1), ci95_block2_low=bands[2][0],
            ci95_block2_high=bands[2][1], ci95_block3_low=bands[3][0],
            ci95_block3_high=bands[3][1], ci95_block4_low=bands[4][0],
            ci95_block4_high=bands[4][1]))
        differences.extend(dict(contrast=label, window=w, difference=float(value))
                           for w, value in enumerate(delta, 1))
    return pd.DataFrame(records), pd.DataFrame(differences)


def correction_analysis(streams, week_metrics):
    rows = []
    for family in FAMILIES:
        for seed in (SEEDS if family == 'neuralprophet' else (42,)):
            base_name = f'{family}_frozen_s{seed}'
            base_week = week_metrics[base_name].set_index('window')
            for alpha in (0., .1, .2, .3, .5, .7, 1.):
                token = str(alpha).replace('.', 'p')
                path = SOURCE / 'corrections' / f'core_{base_name}_alpha_{token}.csv'
                raw = pd.read_csv(path)
                corrected = raw[raw.score_eligible].copy()
                assert len(corrected) == 3624
                a = losses(streams[base_name])
                np.testing.assert_allclose(corrected.original_target, a.target, rtol=0, atol=0)
                current = corrected.groupby('window').apply(
                    lambda x: np.mean(np.abs(x.corrected_prediction-x.original_target)),
                    include_groups=False)
                for w in range(1, 24):
                    part = corrected[corrected.window == w]
                    source = a[a.window == w]
                    rows.append(dict(family=family, seed=seed, alpha=alpha, window=w,
                        hours=len(part), base_mae=base_week.loc[w, 'mae'], corrected_mae=current.loc[w],
                        mae_improvement=base_week.loc[w, 'mae']-current.loc[w],
                        mean_base_residual=float((source.target-source.prediction).mean()),
                        applied_bias=float(part.applied_bias.iloc[0])))
    detail = pd.DataFrame(rows)
    assert detail.groupby(['family', 'seed', 'alpha']).window.nunique().eq(23).all()
    summary = detail.groupby(['family', 'seed', 'alpha']).agg(
        mean_weekly_mae=('corrected_mae', 'mean'),
        mean_weekly_improvement=('mae_improvement', 'mean'),
        beneficial_weeks=('mae_improvement', lambda x: int((x > 1e-9).sum()))).reset_index()
    return detail, summary


def strict_sensitivity(streams):
    """Compute the corrected 16-week complete-context subset without old fitted outputs."""
    from .coverage_protocol import windows
    _, grid = load_calendar()
    eligible = windows(grid)
    strict_weeks = eligible.loc[eligible.strict_eligible, 'window'].to_list()
    assert len(strict_weeks) == 16
    rows = []
    for name, broad in streams.items():
        subset = broad[broad.window.isin(strict_weeks)].sort_values(['window', 'lead_hour'])
        assert len(subset) == 2688 and subset.window.nunique() == 16
        broad_mae = np.abs(subset.prediction-subset.target).mean()
        if name.endswith('_ewma03'):
            base = streams[name.removesuffix('_ewma03')]
            bias = 0.; predictions = []
            for week in strict_weeks:
                part = base[(base.window == week) & base.score]
                predictions.extend((part.prediction+bias).to_numpy())
                residual = (part.target-part.prediction).mean()
                bias = .3*residual+.7*bias
            strict_predictions = np.asarray(predictions)
        else:
            strict_predictions = subset.prediction.to_numpy()
        differences = strict_predictions-subset.target.to_numpy()
        rows.append(dict(stream=name, weeks=16, hours=2688,
                         strict_pooled_mae=np.abs(differences).mean(),
                         broader_subset_pooled_mae=broad_mae,
                         strict_minus_broader_subset_mae=np.abs(differences).mean()-broad_mae,
                         maximum_prediction_difference=np.max(np.abs(strict_predictions-subset.prediction.to_numpy()))))
    return pd.DataFrame(rows)


def interpretation():
    coefficients = []
    timing = []
    for p in sorted((SOURCE / 'runs').glob('*/metadata.json')):
        m = json.loads(p.read_text())
        task = m['task']; fit = m['fit']; rid = task['id']
        if task['stage'] != 'core': continue
        scale = fit['scaler']['scale']
        if task['family'] == 'sarimax':
            for feature in task['features']:
                beta = fit['parameter_estimates'][feature]
                coefficients.append(dict(run_id=rid, family='sarimax', regime=task['regime'],
                    window=task.get('week', 1), feature=feature, coefficient_scaled_input=beta,
                    coefficient_per_raw_unit=beta/scale[feature], input_scale=scale[feature]))
        if task['family'] == 'prophet':
            for x in fit['prophet_regressor_coefficients']:
                feature = x['regressor']; beta = x['coef']
                coefficients.append(dict(run_id=rid, family='prophet', regime=task['regime'],
                    window=task.get('week', 1), feature=feature, coefficient_scaled_input=beta,
                    coefficient_per_raw_unit=beta/scale[feature], input_scale=scale[feature]))
        diags = m['completed_weeks']
        source_meta = (json.loads((ROOT/m['reused_from']/'metadata.json').read_text())
                       if m.get('reused_from') else None)
        boundary = ('reused_source' if source_meta else
                    'optimization_only' if fit.get('optimizer',{}).get('method') else
                    'fit_including_initialization')
        original_forecast_seconds = (sum(float(x.get('forecast_seconds',0))
                                         for x in source_meta['completed_weeks'][:len(diags)])
                                     if source_meta else sum(float(x.get('forecast_seconds',0)) for x in diags))
        timing.append(dict(run_id=rid, family=task['family'], regime=task['regime'], seed=task['seed'],
            windows=len(diags), fit_executed=bool(m.get('fit_executed')),
            source_fit_seconds=float(fit.get('fit_seconds', 0)),
            fit_timer_boundary=boundary,
            source_run=m.get('reused_from') or m.get('restored_parameters_from') or '',
            state_reconstruction_seconds=float(fit.get('state_reconstruction_seconds', 0)),
            state_update_seconds=sum(float(x.get('state_update_seconds', 0)) for x in diags),
            forecast_seconds=sum(float(x.get('forecast_seconds', 0)) for x in diags),
            source_forecast_seconds=original_forecast_seconds,
            placeholder_check_seconds=sum(float(x.get('invariance_check_seconds', 0)) for x in diags),
            sampled_self_peak_rss_mib=m.get('sampled_self_peak_rss_mib')))
    coeff = pd.DataFrame(coefficients)
    comp = []
    pdir = SOURCE / 'runs/core_prophet_frozen_s42'
    for w in range(1, 24):
        p = pdir / f'components_w{w:02d}.csv'
        c = pd.read_csv(p, parse_dates=['ds'])
        f = pd.read_csv(pdir / f'week_{w:02d}.csv', parse_dates=['target_timestamp'])
        assert len(c) == len(f) == 168 and c.ds.equals(f.target_timestamp)
        for column in ('trend', 'daily', 'weekly', 'yearly', 'no', 'no2', 'co', 'so2'):
            values = c.loc[f.score_eligible, column]
            comp.append(dict(window=w, component=column, hours=len(values),
                             mean_signed=float(values.mean()), mean_absolute=float(values.abs().mean())))
    return coeff, pd.DataFrame(comp), pd.DataFrame(timing)


def resource_events():
    rows = []
    for label, p in [('validation', REVISION/'artifacts/phase2/supervisor.jsonl'),
                     ('broader', SOURCE/'supervisor.jsonl')]:
        if not p.exists():continue
        with p.open() as f:
            for line in f:
                e = json.loads(line)
                rows.append(dict(phase=label, task_id=e.get('task_id', e.get('original_id')),
                    returncode=e['returncode'], elapsed_seconds=e['elapsed_seconds'],
                    sampled_peak_rss_mib=e.get('sampled_peak_rss_mib'),
                    guard_reason=e.get('guard_reason')))
    return pd.DataFrame(rows)


def save_figure(fig, name):
    fig.savefig(FIG/f'{name}.pdf', bbox_inches='tight')
    fig.savefig(FIG/f'{name}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)


def figures(streams, week_metrics, lead_hour, lead_day, correction):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for family in FAMILIES:
        name = f'{family}_frozen_s42'
        d = lead_hour[lead_hour.stream == name]
        ax.plot(d.lead_hour, d.mae, linewidth=1.4, label=family, color=DAY_COLORS[family])
    ax.set(xlabel='Lead hour (1–168)', ylabel='MAE (PM2.5 units)', xlim=(1, 168))
    ax.legend(frameon=False, ncol=3);ax.grid(alpha=.2);fig.tight_layout();save_figure(fig, 'lead_hour_mae')

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for family in FAMILIES:
        name = f'{family}_frozen_s42'
        d = lead_day[lead_day.stream == name]
        ax.plot(d.forecast_day, d.mae, marker='o', label=family, color=DAY_COLORS[family])
    d = lead_day[lead_day.stream == 'weekly_persistence']
    ax.plot(d.forecast_day, d.mae, marker='o', label='Weekly persistence', color='#777777')
    ax.set(xlabel='Forecast day', ylabel='MAE (PM2.5 units)', xticks=range(1, 8))
    ax.legend(frameon=False, ncol=2);ax.grid(alpha=.2);fig.tight_layout();save_figure(fig, 'lead_day_mae')

    fig, ax = plt.subplots(figsize=(11, 4.4))
    for family in FAMILIES:
        name = f'{family}_frozen_s42'
        d = week_metrics[name]
        ax.plot(d.window, d.mae, marker='o', markersize=3, label=family,
                color=DAY_COLORS[family])
    ax.set(xlabel='Consecutive test week', ylabel='Weekly MAE (observed hours)', xticks=range(1, 24, 2))
    ax.legend(frameon=False, ncol=3);ax.grid(alpha=.2);fig.tight_layout();save_figure(fig, 'weekly_mae_chronology')

    fig, ax = plt.subplots(figsize=(9, 4.4))
    names = [f'{f}_frozen_s42' for f in FAMILIES] + ['weekly_persistence']
    ax.boxplot([week_metrics[n].mae for n in names], tick_labels=['SARIMAX', 'Prophet', 'NeuralProphet', 'Weekly persistence'], showfliers=True)
    ax.set(ylabel='Weekly MAE (observed hours)');ax.grid(axis='y', alpha=.2)
    fig.tight_layout();save_figure(fig, 'weekly_mae_distribution')

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for ax, family in zip(axes, FAMILIES):
        d = correction[(correction.family == family) & (correction.seed == 42) &
                       (correction.alpha == .3)].sort_values('window')
        ax.plot(d.window, d.mean_base_residual, label='Observed base residual mean', color='#277da1')
        ax.plot(d.window, d.applied_bias, label='Bias known at origin', color='#e67e22')
        ax.bar(d.window, d.mae_improvement, alpha=.4, label='MAE improvement', color='#3a9b60')
        ax.axhline(0, color='black', linewidth=.5)
        ax.set(ylabel=family);ax.grid(alpha=.15)
    axes[0].legend(frameon=False, ncol=3, fontsize=8)
    axes[-1].set(xlabel='Consecutive test week', xticks=range(1, 24, 2))
    fig.tight_layout();save_figure(fig, 'correction_diagnostics')

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    for ax, family in zip(axes, FAMILIES):
        for regime, color in [('frozen','#277da1'),('walk','#e67e22')]:
            d=week_metrics[f'{family}_{regime}_s42']
            ax.plot(d.window,d.mae,marker='o',markersize=2.5,label=regime,color=color)
        ax.set(ylabel=f'{family} MAE');ax.grid(alpha=.15)
    axes[0].legend(frameon=False,ncol=2)
    axes[-1].set(xlabel='Consecutive test week',xticks=range(1,24,2))
    fig.tight_layout();save_figure(fig,'regime_comparison')


def benchmark_correction(streams):
    """Measure correction arithmetic alone; exclude CSV I/O and plotting."""
    rows = []
    for family in FAMILIES:
        seeds = SEEDS if family == 'neuralprophet' else (42,)
        for seed in seeds:
            name = f'{family}_frozen_s{seed}'
            base = streams[name]
            stored = streams[name+'_ewma03']
            runs = []
            for _ in range(20):
                start = time.perf_counter()
                bias = 0.;replayed = np.empty(len(base), dtype=float)
                for w in range(1, 24):
                    section = base.window.eq(w).to_numpy()
                    valid = section & base.score.to_numpy()
                    replayed[section] = base.prediction.to_numpy()[section]+bias
                    residual = (base.target.to_numpy()[valid]-base.prediction.to_numpy()[valid]).mean()
                    bias = .3*residual+.7*bias
                runs.append(time.perf_counter()-start)
            np.testing.assert_allclose(replayed[base.score], stored.prediction[base.score],
                                       atol=1e-9, rtol=0)
            rows.append(dict(stream=name, iterations=20,
                             correction_arithmetic_seconds_median=float(np.median(runs))))
    return pd.DataFrame(rows)


def main():
    v = verified_source()
    OUT.mkdir(parents=True, exist_ok=True);FIG.mkdir(exist_ok=True)
    streams = load_streams()
    metrics = []; week_metrics = {}; hourly = []; daily = []
    for name, d in streams.items():
        a = losses(d); week, m = summarize(a); week_metrics[name] = week
        metrics.append(dict(stream=name, **m))
        week.assign(stream=name).to_csv(OUT/f'weekly_{name}.csv', index=False)
        for col, rows in [('lead_hour', hourly), ('forecast_day', daily)]:
            group = a.groupby(col).agg(hours=('absolute_error', 'size'),
                mae=('absolute_error', 'mean'), mse=('squared_error', 'mean')).reset_index()
            group['rmse'] = np.sqrt(group.mse);group['stream'] = name
            rows.append(group.drop(columns='mse'))
    metric_table = pd.DataFrame(metrics)
    assert metric_table.hours.eq(3624).all() and metric_table.windows.eq(23).all()
    metric_table.to_csv(OUT/'performance.csv', index=False)
    lead_hour = pd.concat(hourly, ignore_index=True)
    lead_hour.to_csv(OUT/'lead_hour.csv', index=False)
    lead_day = pd.concat(daily, ignore_index=True)
    lead_day.to_csv(OUT/'forecast_day.csv', index=False)
    paired, differences = paired_table(week_metrics)
    paired.to_csv(OUT/'paired_contrasts.csv', index=False)
    differences.to_csv(OUT/'paired_weekly_differences.csv', index=False)
    correction, alpha = correction_analysis(streams, week_metrics)
    correction.to_csv(OUT/'correction_weekly.csv', index=False)
    alpha.to_csv(OUT/'correction_alpha_summary.csv', index=False)
    coefficients, components, timings = interpretation()
    coefficients.to_csv(OUT/'coefficients.csv', index=False)
    components.to_csv(OUT/'prophet_components.csv', index=False)
    timings.to_csv(OUT/'core_timing.csv', index=False)
    events = resource_events();events.to_csv(OUT/'resource_events.csv', index=False)
    _, grid = load_calendar(); cutoff = split_position(grid)
    train = grid.iloc[:cutoff].pm2_5.dropna();test = grid.iloc[cutoff:].pm2_5.dropna()
    threshold = float(train.quantile(.95))
    descriptive = pd.DataFrame([dict(partition=label, n=len(x), mean=x.mean(), sd=x.std(ddof=1),
        median=x.median(), q25=x.quantile(.25), q75=x.quantile(.75), iqr=x.quantile(.75)-x.quantile(.25),
        minimum=x.min(), maximum=x.max()) for label, x in [('training', train), ('test', test)]])
    descriptive.to_csv(OUT/'target_descriptive.csv', index=False)
    high = []
    for name, d in streams.items():
        a = losses(d);h = a[a.target > threshold]
        high.append(dict(stream=name, training_q95_threshold=threshold, hours=len(h),
            mae=h.absolute_error.mean(), rmse=np.sqrt(h.squared_error.mean()),
            share_of_scored_hours=len(h)/len(a)))
    high = pd.DataFrame(high);high.to_csv(OUT/'high_concentration.csv', index=False)
    high_week = []
    for name, d in streams.items():
        a = losses(d); h = a[a.target > threshold]
        for w, part in h.groupby('window'):
            high_week.append(dict(stream=name, window=w, hours=len(part),
                                  mae=part.absolute_error.mean(), rmse=np.sqrt(part.squared_error.mean())))
    high_week = pd.DataFrame(high_week)
    high_week.to_csv(OUT/'high_concentration_by_week.csv', index=False)
    strict = strict_sensitivity(streams)
    strict.to_csv(OUT/'strict_sensitivity.csv', index=False)
    correction_time = benchmark_correction(streams)
    correction_time.to_csv(OUT/'correction_timing.csv', index=False)
    figures(streams, week_metrics, lead_hour, lead_day, correction)
    from .corrected_report import write_report as write_corrected_report
    write_corrected_report(metric_table, paired, alpha, high, high_week, descriptive,
                           coefficients, components, timings, events, strict, threshold)
    summary = dict(source_protocol_signature=v['protocol_signature'], streams=len(streams),
        paired_contrasts=len(paired), training_q95_threshold=threshold,
        high_hours=int(high.loc[high.stream=='sarimax_frozen_s42','hours'].iloc[0]),
        figure_stems=['lead_hour_mae','lead_day_mae','weekly_mae_chronology',
                      'weekly_mae_distribution','correction_diagnostics','regime_comparison'])
    (OUT/'manifest.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
