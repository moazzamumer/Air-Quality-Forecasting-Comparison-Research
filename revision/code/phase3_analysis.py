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

from .protocol import REVISION, load_calendar, split_position

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
    """Audit the preserved 16-week results against the same broader-week slice.

    Correction streams legitimately differ because strict policy skips unavailable
    weeks while the broader policy updates from every partially observed week.
    """
    root = REVISION / 'artifacts/phase2'
    map_table = pd.read_csv(root/'verified_coverage.csv')
    strict_weeks = pd.read_csv(SOURCE/'windows.csv')
    strict_weeks = strict_weeks.loc[strict_weeks.strict_eligible, 'window'].to_list()
    assert len(strict_weeks) == 16
    rows = []
    for name, broad in streams.items():
        if name.endswith('ewma03'):
            run = 'core_' + name.removesuffix('_ewma03')
            path = root/'corrections'/f'{run}_alpha_0p3.csv'
            field = 'corrected_prediction'
        elif name in ('persistence', 'daily_persistence', 'weekly_persistence'):
            path = root/'baselines'/f'{name}.csv';field = 'base_prediction'
        else:
            parts = name.split('_')
            field = 'base_prediction'
            if '_walk_s' in name:
                family, _, seed_text = parts
                old_parts = []
                for w in strict_weeks:
                    run = f'core_{family}_walk_w{w:02d}_{seed_text}'
                    mapping = map_table[map_table.run_id == run]
                    assert len(mapping) == 1, run
                    path = root/'runs'/mapping.iloc[0].evidence_run_id/'forecasts.csv'
                    old_parts.append(pd.read_csv(path))
                old = pd.concat(old_parts, ignore_index=True)
            else:
                run = (f'ablate_{parts[0]}_{"_".join(parts[2:])}' if not parts[2].startswith('s')
                       else 'core_'+name)
                mapping = map_table[map_table.run_id == run]
                assert len(mapping) == 1, run
                path = root/'runs'/mapping.iloc[0].evidence_run_id/'forecasts.csv'
                old = pd.read_csv(path)
        if name.endswith('ewma03') or name in ('persistence', 'daily_persistence', 'weekly_persistence'):
            assert path.exists(), path
            old = pd.read_csv(path)
        old = old[old.window.isin(strict_weeks)]
        subset = broad[broad.window.isin(strict_weeks)]
        assert len(old) == len(subset) == 2688 and old.window.nunique() == 16, name
        old = old.sort_values(['window', 'lead_hour']);subset = subset.sort_values(['window', 'lead_hour'])
        np.testing.assert_array_equal(old.window, subset.window)
        np.testing.assert_array_equal(old.lead_hour, subset.lead_hour)
        np.testing.assert_allclose(old.original_target, subset.target, atol=0, rtol=0)
        old_error = old[field].to_numpy()-old.original_target.to_numpy()
        broader_error = subset.prediction.to_numpy()-subset.target.to_numpy()
        rows.append(dict(stream=name, weeks=16, hours=2688,
            strict_pooled_mae=np.abs(old_error).mean(),
            broader_subset_pooled_mae=np.abs(broader_error).mean(),
            strict_minus_broader_subset_mae=np.abs(old_error).mean()-np.abs(broader_error).mean(),
            maximum_prediction_difference=np.max(np.abs(old[field].to_numpy()-subset.prediction.to_numpy()))))
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
        timing.append(dict(run_id=rid, family=task['family'], regime=task['regime'], seed=task['seed'],
            windows=len(diags), fit_executed=bool(m.get('fit_executed')),
            source_fit_seconds=float(fit.get('fit_seconds', 0)),
            source_run=m.get('reused_from') or m.get('restored_parameters_from') or '',
            state_reconstruction_seconds=float(fit.get('state_reconstruction_seconds', 0)),
            state_update_seconds=sum(float(x.get('state_update_seconds', 0)) for x in diags),
            forecast_seconds=sum(float(x.get('forecast_seconds', 0)) for x in diags),
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
    for label, p in [('strict', REVISION/'artifacts/phase2/supervisor.jsonl'),
                     ('strict_recovery', REVISION/'artifacts/phase2/recovery_supervisor.jsonl'),
                     ('broader', SOURCE/'supervisor.jsonl')]:
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


def markdown_table(frame, decimals=2):
    labels = list(frame.columns)
    def cell(x):
        if isinstance(x, (float, np.floating)): return f'{x:.{decimals}f}'
        return str(x)
    rows = ['| '+' | '.join(labels)+' |', '| '+' | '.join('---' for _ in labels)+' |']
    rows.extend('| '+' | '.join(cell(x) for x in values)+' |' for values in frame.itertuples(index=False, name=None))
    return '\n'.join(rows)


def write_report(metrics, paired, alpha, high, high_week, descriptive,
                 coefficients, components, timing, events, strict, threshold):
    selected = [f'{family}_{regime}_s42' for family in FAMILIES for regime in ('frozen', 'walk')]
    selected += [f'{family}_frozen_s42_ewma03' for family in FAMILIES]
    selected += ['persistence', 'daily_persistence', 'weekly_persistence']
    shown = metrics.set_index('stream').loc[selected].reset_index()
    compare = shown[['stream','windows','hours','pooled_mae','pooled_rmse',
                      'mean_weekly_mae','weekly_mae_sd','mean_weekly_rmse','weekly_rmse_sd']]
    coeff_summary = coefficients[coefficients.regime == 'walk'].groupby(['family','feature']).agg(
        minimum_raw_unit=('coefficient_per_raw_unit','min'),
        maximum_raw_unit=('coefficient_per_raw_unit','max')).reset_index()
    frozen_coeff = coefficients[coefficients.regime == 'frozen'].groupby(['family','feature']).agg(
        frozen_raw_unit=('coefficient_per_raw_unit','first'),
        source_input_scale=('input_scale','first')).reset_index()
    coeff_summary = frozen_coeff.merge(coeff_summary, on=['family','feature'])
    week_high = high_week[high_week.stream == 'sarimax_frozen_s42']
    timing_summary = timing[timing.regime == 'walk'].groupby('family').source_fit_seconds.median().reset_index(
        name='median_source_fit_seconds')
    first = timing[(timing.regime == 'frozen') & (timing.seed == 42)][['family','source_fit_seconds',
        'state_update_seconds','forecast_seconds']].rename(columns={'source_fit_seconds':'initial_source_fit_seconds',
        'state_update_seconds':'frozen_state_update_seconds_23w',
        'forecast_seconds':'frozen_forecast_seconds_23w'})
    timing_summary = first.merge(timing_summary, on='family')
    event_summary = events.groupby('phase').agg(events=('returncode','size'),
        failed=('returncode', lambda x: int((x != 0).sum())),
        wall_hours=('elapsed_seconds', lambda x: x.sum()/3600),
        largest_sampled_peak_rss_mib=('sampled_peak_rss_mib','max')).reset_index()
    correction = alpha[alpha.alpha == .3][['family','seed','mean_weekly_mae',
        'mean_weekly_improvement','beneficial_weeks']]
    extremes = high.set_index('stream').loc[[f'{f}_frozen_s42' for f in FAMILIES]+
                                               ['weekly_persistence']].reset_index()
    broad = metrics[metrics.stream.str.endswith('_frozen_broad')][['stream','pooled_mae','pooled_rmse']]
    clip = metrics[metrics.stream.str.endswith('_frozen_clip')][['stream','pooled_mae','pooled_rmse']]
    no_inputs = metrics[metrics.stream.str.endswith('_frozen_no_inputs')][['stream','pooled_mae','pooled_rmse']]
    seed_metrics = metrics[metrics.stream.str.match('neuralprophet_(frozen|walk)_s(42|123|2026)$')][
        ['stream','pooled_mae','mean_weekly_mae']]
    no_correction = strict[~strict.stream.str.endswith('ewma03')]
    assert no_correction.maximum_prediction_difference.max() < 1e-8
    lines = [
        '# Phase 3 — Publication analysis from verified forecasts','',
        'Generated by `venv/bin/python -m revision.code.phase3_analysis`. All numerical results are computed from the verified broader forecast artifacts. This is the analysis record for manuscript revision; the submitted manuscript and original notebook have not been altered.','',
        '## Scope and methods','',
        'The primary evaluation has 23 consecutive 168-hour forecast origins (3,864 scheduled hours) and scores 3,624 original observed target hours on one shared mask. Nineteen weeks are complete and four are partial. The trailing 163-hour calendar segment is outside this full-week comparison. All models use the Perfect Prognosis information set with actual future gases; these results do not establish deployed forecast performance. The strict 16-week, 2,688-hour reference is retained below.','',
        'Pooled MAE/RMSE weight every scored hour equally; mean weekly MAE/RMSE weight each calendar week equally. Their denominators differ because partial weeks contain 120, 120, 48 and 144 scored hours. Weekly SD is sample SD over 23 weeks. All contrasts use unrounded weekly MAE on the same calendar weeks. NeuralProphet paired contrasts average the three seed-level weekly losses; they do not average predictions or treat seeds as independent weeks.','',
        'The predeclared uncertainty procedure uses 2,000 moving-block bootstrap replicates of adjacent weekly loss differences, random seed 42 with separate deterministic streams for block lengths 2, 3 and 4; the primary displayed interval uses 3-week blocks. A draw samples overlapping block starts within the 23-week series and truncates the concatenation to 23 weeks. No block crosses a discontinuous calendar boundary; four weeks have reduced within-week target coverage. These percentile intervals are descriptive sensitivity analyses of a short, dependent series, not evidence of universal model superiority.','',
        '## Matched model performance','',markdown_table(compare),'',
        f'The frozen and weekly-refit selected-gas SARIMAX point estimates are close (pooled MAE {metrics.set_index("stream").loc["sarimax_frozen_s42","pooled_mae"]:.2f} and {metrics.set_index("stream").loc["sarimax_walk_s42","pooled_mae"]:.2f}). The predefined α=0.3 correction yields pooled MAE {metrics.set_index("stream").loc["sarimax_frozen_s42_ewma03","pooled_mae"]:.2f} for frozen SARIMAX, {metrics.set_index("stream").loc["prophet_frozen_s42_ewma03","pooled_mae"]:.2f} for frozen Prophet and {metrics.set_index("stream").loc["neuralprophet_frozen_s42_ewma03","pooled_mae"]:.2f} for NeuralProphet seed 42. These are same-mask comparisons, and the week-level paired estimates below govern uncertainty claims. The seasonal baselines are much less accurate under this particular Perfect Prognosis protocol.','',
        '## Paired weekly uncertainty (A − B; negative favors A)','',
        markdown_table(paired[['contrast','weeks','mean_weekly_mae_difference','weekly_difference_sd',
                              'ci95_block3_low','ci95_block3_high','ci95_block2_low','ci95_block2_high',
                              'ci95_block4_low','ci95_block4_high']]),'',
        'The corrected frozen SARIMAX–Prophet difference is negative under each stated block length. For SARIMAX, the α=0.3 correction has a small average weekly benefit and each interval spans zero. Corrected frozen Prophet and weekly-refit Prophet have similar week-level errors with intervals spanning zero. The Prophet correction is more consistently favorable in this sample; NeuralProphet correction varies by seed. Week-level dependence, partial coverage and the 23-week horizon limit inferential strength.','',
        '## Lead time, week variation and high concentrations','',
        'Exact 1–168-hour and day 1–7 MAE/RMSE with counts are in `../artifacts/phase3/lead_hour.csv` and `../artifacts/phase3/forecast_day.csv`. The lead-time curves do not support a simple monotonic deterioration for every model. Chronological and distribution plots include all 23 weeks; selected best or worst weeks are not substituted for the full series.','',
        '[Lead-hour MAE](../artifacts/phase3/figures/lead_hour_mae.pdf) · [Forecast-day MAE](../artifacts/phase3/figures/lead_day_mae.pdf) · [Chronological weekly MAE](../artifacts/phase3/figures/weekly_mae_chronology.pdf) · [Weekly error distribution](../artifacts/phase3/figures/weekly_mae_distribution.pdf)','',
        'Training/test descriptions use original observed PM2.5, including observations in the 163-hour terminal test remainder.','',
        markdown_table(descriptive),'',
        f'The original-target high-concentration threshold is the training 95th percentile, {threshold:.3f} PM2.5 units. Exactly {int(week_high.hours.sum())} of the 3,624 scored hours exceed it, concentrated in {len(week_high)} of the 23 weeks. The same target hours are used for all model comparisons.','',
        markdown_table(extremes[['stream','hours','mae','rmse']]),'',
        'NeuralProphet seed 42 has lower MAE than selected-gas SARIMAX on this small high-concentration subset, although its overall MAE is higher. This limits any claim of uniform SARIMAX advantage. The subset is clustered and this is descriptive, not an independently powered comparison.','',
        '## Correction and sensitivity findings','',
        'α=0.3 was predefined before held-out evaluation. The full α grid and previous-week residual comparator (α=1) are reported without choosing the test-best value. Bias is applied using only earlier completed-week residuals, then updated from the current week after its target hours become available.','',
        markdown_table(correction),'',
        'The week-by-week base residual, applied bias and MAE change are saved in `../artifacts/phase3/correction_weekly.csv` and [plotted together](../artifacts/phase3/figures/correction_diagnostics.pdf). The direction and size of a subsequent benefit vary with residual persistence. That observation is diagnostic; a mechanism for the residual shifts has not been established.','',
        'The frozen selected-gas ablations are controlled input-set comparisons at the same model settings. Broader inputs include future PM10 and therefore provide additional companion-particulate information; their lower errors must not be presented as an operational improvement or a fair replacement for the predefined four-gas comparison.','',
        'Removing all future covariates from the fixed selected-gas configurations produces the following errors. This is an ablation, not an independently selected univariate model.','',
        markdown_table(no_inputs),'',
        'The broader-input frozen control has the following errors:','',
        markdown_table(broad),'',
        'Training-percentile clipping of selected predictors worsens all three frozen models here. Fitting and scoring PM2.5 targets remain original and unclipped.','',
        markdown_table(clip),'',
        'NeuralProphet seed-level outcomes vary; the seed 42 ranking must not be described as an intrinsic property of the architecture. All runs have checked 168-step alignment and finite 50-epoch training traces.','',
        markdown_table(seed_metrics),'',
        '## Model interpretation','',
        'The following selected-input SARIMAX and Prophet coefficients are from the frozen fit at the first test origin, with ranges across 23 saved weekly-refit fits. `source_input_scale` is the training-only standard deviation used to scale each API-derived input. Dividing the stored coefficient per scaled input by that value yields the displayed coefficient per raw input unit. The Prophet coefficient comes from `prophet.utilities.regressor_coefficients` on the externally standardized input. Coefficients are conditional model associations, not pollutant causal effects; correlated inputs and model parameterization can change signs and magnitudes.','',
        markdown_table(coeff_summary, decimals=4),'',
        'Frozen Prophet additive component values for the 3,624 scored timestamps include trend and daily/weekly/yearly seasonal contributions as well as the four regressors. The mean absolute component sizes below describe model contributions, not independent feature importance; large opposing signed terms can cancel.','',
        markdown_table(components.groupby('component').agg(mean_signed=('mean_signed','mean'),
            mean_absolute=('mean_absolute','mean')).reset_index()),'',
        '## Computation and accounting','',
        'All revised model runs used the same local AMD Ryzen 5 5500U machine, CPU only, with two configured model threads. Time boundaries separate fit, frozen SARIMAX state update and forecasting in run metadata. Initial fits shown here may originate in the preserved strict run; reused fit times are reference measurements and must not be summed again as new Phase 3 work. Weekly-refit median source-fit durations include recovered source fits where applicable.','',
        markdown_table(timing_summary),'',
        'Process supervisor wall times include child startup, fitting, state updates, forecast calculation and integrity checks. The strict and recovery logs include failed attempts; the broader log also includes 80 reused forecasts and four SARIMAX state reconstructions. These phases overlap in evidence but the event wall hours are actual sequential work performed, not a per-model speed ratio. The sampled peak group RSS is interval-sampled and may miss short peaks. No GPU was used. Original Colab timings are not directly comparable.','',
        markdown_table(event_summary),'',
        'Saved `../artifacts/phase3/core_timing.csv` and `../artifacts/phase3/resource_events.csv` retain run-level accounting. The in-memory α=0.3 correction replay was timed separately over 20 repeats per frozen stream (`../artifacts/phase3/correction_timing.csv`); it excludes CSV I/O, fitting and plotting and is too small to serve as a whole-pipeline runtime estimate.','',
        '## Preserved strict-availability sensitivity','',
        f'Across the original 16 strictly eligible weeks, uncorrected broader forecasts reproduce the preserved reference to at most {no_correction.maximum_prediction_difference.max():.2g} PM2.5 units. The full [strict sensitivity table](../artifacts/phase3/strict_sensitivity.csv) includes every base and corrected stream. Broader EWMA values on those same weeks can differ because the broader rule updates after partially observed intervening weeks, while the strict rule skips and carries bias; they are distinct correction policies.','',
        '## Boundaries for manuscript claims','',
        'The broader protocol causally fills missing historical inference context, including a gap of 120 hours. Missing targets are never filled for fitting or scoring, and computational future-input placeholders at unscored hours were tested for zero effect on scored predictions. The four partial weeks contain less evidence than complete weeks. API-derived gridded/model-estimate PM2.5 is not direct station validation; original retrieval dates and raw API responses are unavailable. The limited roughly 23-week test season does not establish year-round or geographic generalization. The Perfect Prognosis covariates are unavailable as future observations in ordinary deployment.','',
        'All generated tables and figures trace to `../artifacts/phase3/manifest.json`, the source files under `../artifacts/coverage_reconsideration/`, and the checked phase-2 strict reference. These findings support Phase 4 manuscript and point-by-point response editing; they do not assert acceptance or a completed journal submission.',''
    ]
    (REVISION/'reports/PHASE3_RESULTS.md').write_text('\n'.join(lines))


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
    write_report(metric_table, paired, alpha, high, high_week, descriptive,
                 coefficients, components, timings, events, strict, threshold)
    summary = dict(source_protocol_signature=v['protocol_signature'], streams=len(streams),
        paired_contrasts=len(paired), training_q95_threshold=threshold,
        high_hours=int(high.loc[high.stream=='sarimax_frozen_s42','hours'].iloc[0]),
        figure_stems=['lead_hour_mae','lead_day_mae','weekly_mae_chronology',
                      'weekly_mae_distribution','correction_diagnostics'])
    (OUT/'manifest.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
