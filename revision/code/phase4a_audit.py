"""Read-only scientific review of saved runs; writes review evidence only.

This does not repair data, fit a model, change a selection, or regenerate scores.
"""
import hashlib
import json
import subprocess

import numpy as np
import pandas as pd

from .protocol import ROOT, REVISION, original_path, neural_training_segments

OUT = REVISION / 'artifacts/phase4a'
SOURCE = REVISION / 'artifacts/coverage_reconsideration'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(ROOT/'data/beijing.csv')
    raw.index = pd.DatetimeIndex(pd.to_datetime(raw[['year','month','day','hour']]), name='datetime')
    raw = raw.sort_index()
    assert not raw.index.has_duplicates
    grid = raw.reindex(pd.date_range(raw.index.min(), raw.index.max(), freq='h', name='datetime'))
    cfg = json.loads((REVISION/'config/protocol.json').read_text())
    cutoff = int(.9*len(grid))
    selected = cfg['selected_features']; broad = cfg['broad_features']
    pollutants = ['pm2_5','pm10','no','no2','co','so2','o3','nh3']
    bad_cells = []
    for feature in pollutants:
        for ts, value in grid.loc[grid[feature].lt(0), feature].items():
            bad_cells.append(dict(timestamp=str(ts), feature=feature, value=float(value),
                                  partition='training' if ts < grid.index[cutoff] else 'test',
                                  selected_input=feature in selected))
    pd.DataFrame(bad_cells).to_csv(OUT/'invalid_pollutant_cells.csv', index=False)
    # Counterfactual audit only: invalidate the identified -9999 input cells in memory.
    # Legitimate negative temperature/dew point values are not changed.
    candidate = grid.copy()
    for feature in broad:
        if feature in pollutants: candidate[feature] = candidate[feature].mask(candidate[feature].eq(-9999))
    scales = []
    samples = []
    validation = pd.read_csv(REVISION/'artifacts/phase1/validation_windows.csv')
    for boundary, end in [('validation_fit', int(validation.position.iloc[0])), ('initial_test_fit', cutoff)]:
        for variant, features in [('selected', selected), ('broad', broad), ('no_inputs', [])]:
            old = grid.iloc[:end][features].dropna()
            new = candidate.iloc[:end][features].dropna()
            for f in features:
                scales.append(dict(boundary=boundary, variant=variant, feature=f,
                    current_mean=old[f].mean(), current_scale=old[f].std(ddof=0),
                    candidate_mean=new[f].mean(), candidate_scale=new[f].std(ddof=0),
                    current_complete_rows=len(old), candidate_complete_rows=len(new)))
            _, episodes_old = neural_training_segments(grid.iloc[:end], features)
            _, episodes_new = neural_training_segments(candidate.iloc[:end], features)
            before = sum(e['training_samples'] for e in episodes_old)
            after = sum(e['training_samples'] for e in episodes_new)
            samples.append(dict(boundary=boundary, variant=variant,
                current_samples=before, candidate_samples=after, difference=after-before,
                current_retained_episodes=sum(e['retained'] for e in episodes_old),
                candidate_retained_episodes=sum(e['retained'] for e in episodes_new)))
    pd.DataFrame(scales).to_csv(OUT/'input_scaling_sensitivity.csv', index=False)
    pd.DataFrame(samples).to_csv(OUT/'neural_training_sample_impact.csv', index=False)
    cols = ['pm2_5']+broad
    mask = grid.iloc[cutoff:cutoff+3864][cols].notna().all(axis=1)
    candidate_mask = candidate.iloc[cutoff:cutoff+3864][cols].notna().all(axis=1)
    assert mask.equals(candidate_mask)
    runs = [json.loads(p.read_text()) for p in sorted((SOURCE/'runs').glob('*/metadata.json'))]
    all_completed = all(m['status']=='completed' for m in runs)
    assert len(runs)==129 and all_completed
    assert all(m['fit']['fit_end_exclusive']==m['fit_origin'] for m in runs)
    for m in runs:
        path = SOURCE/'runs'/m['task']['id']/'forecasts.csv'
        d = pd.read_csv(path, parse_dates=['target_timestamp','forecast_origin'])
        assert pd.Timestamp(m['fit_origin']) <= d.forecast_origin.min()
        np.testing.assert_array_equal(d.target_timestamp-d.forecast_origin,
                                      pd.to_timedelta(d.lead_hour-1,unit='h'))
        source = grid.loc[d.target_timestamp]
        np.testing.assert_allclose(d.original_target, source.pm2_5, atol=0, rtol=0, equal_nan=True)
        np.testing.assert_array_equal(d.score_eligible, source[cols].notna().all(axis=1))
        assert np.isfinite(d.loc[d.score_eligible,'base_prediction']).all()
    correction_paths = sorted((SOURCE/'corrections').glob('*_alpha_*.csv'))
    assert len(correction_paths) == 35
    for p in correction_paths:
        d=pd.read_csv(p);bias=0.;alpha=float(d.alpha.iloc[0])
        for _,w in d.groupby('window',sort=True):
            np.testing.assert_allclose(w.applied_bias,bias,atol=1e-9,rtol=0)
            np.testing.assert_allclose(w.corrected_prediction,w.base_prediction+bias,
                                       atol=1e-9,rtol=0,equal_nan=True)
            obs=w[w.score_eligible]
            bias=alpha*(obs.original_target-obs.base_prediction).mean()+(1-alpha)*bias
    baseline = pd.read_csv(SOURCE/'baselines/persistence.csv')
    for w,d in baseline.groupby('window'):
        origin = pd.Timestamp(d.forecast_origin.iloc[0])
        prior = grid.loc[grid.index < origin, 'pm2_5'].dropna()
        np.testing.assert_allclose(d.base_prediction,prior.iloc[-1],atol=1e-9,rtol=0)
    component = pd.read_csv(REVISION/'artifacts/phase3/prophet_components.csv')
    weighting=[]
    for name,d in component.groupby('component'):
        weighting.append(dict(component=name, equal_week_mean_absolute=d.mean_absolute.mean(),
            hourly_mean_absolute=np.average(d.mean_absolute,weights=d.hours)))
    pd.DataFrame(weighting).to_csv(OUT/'component_weighting_audit.csv',index=False)
    from .coverage_protocol import seasonal_past_fill
    week12 = baseline[baseline.window==12];origin=pd.Timestamp(week12.forecast_origin.iloc[0])
    past=grid.loc[grid.index < origin,['pm2_5']]
    provisional_last=float(seasonal_past_fill(past).pm2_5.iloc[-1])
    genuine_last=float(past.pm2_5.dropna().iloc[-1])
    example=json.loads((SOURCE/'runs/core_prophet_walk_w02_s42/metadata.json').read_text())
    source=json.loads((ROOT/example['reused_from']/'metadata.json').read_text())
    hashes=json.loads((REVISION/'artifacts/phase1/original_manifest.json').read_text())['files']
    for name,expected in hashes.items():
        assert hashlib.sha256(original_path(name).read_bytes()).hexdigest()==expected['sha256'],name
    reviewed_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    audit_inputs=[ROOT/'data/beijing.csv',REVISION/'config/protocol.json',
                  REVISION/'config/coverage_reconsideration.json',REVISION/'code/protocol.py',
                  REVISION/'code/coverage_runner.py',REVISION/'code/phase3_analysis.py',
                  REVISION/'artifacts/phase2/selection.json',SOURCE/'verification.json',
                  SOURCE/'baselines/definitions.json']
    findings=dict(reviewed_commit=reviewed_commit,mode='read-only audit; proposed cleaning is in-memory only',
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in audit_inputs},
        invalid_pollutant_cells=bad_cells,invalid_cells=len(bad_cells),
        no_invalid_test_cells=all(x['partition']=='training' for x in bad_cells),
        candidate_test_mask_unchanged=mask.equals(candidate_mask),scored_hours=int(mask.sum()),
        completed_run_tasks=len(runs),same_calendar_target_mask_and_fit_cutoffs_checked=True,
        causal_correction_streams_checked=len(correction_paths),last_genuine_observation_baseline_checked=True,
        original_hashes_checked=len(hashes),
        training_validation_provisional=True,manuscript_numbers_provisional=True,
        baseline_finalization=dict(week=12,standalone_finish_value=provisional_last,
                                   saved_checked_value=genuine_last),
        reused_forecast_timing_example=dict(run='core_prophet_walk_w02_s42',
            broader_forecast_seconds=example['completed_weeks'][0]['forecast_seconds'],
            original_forecast_seconds=source['completed_weeks'][0]['forecast_seconds']),
        verdict='Hold Phase 4B scientific claims: correct invalid training inputs and assess/refit affected models first.')
    (OUT/'review_evidence.json').write_text(json.dumps(findings,indent=2)+'\n')
    print(json.dumps(findings,indent=2))


if __name__ == '__main__': main()
