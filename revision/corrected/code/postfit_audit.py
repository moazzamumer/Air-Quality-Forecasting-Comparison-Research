"""Independent saved-evidence checks after corrected fitting and analysis."""
import hashlib
import json

import numpy as np
import pandas as pd

from .protocol import ROOT, REVISION, configuration, load_calendar, split_position, neural_training_segments
from .coverage_protocol import windows, signature
from .coverage_runner import tasks
from .phase2_runner import load_tasks, signature as validation_signature


def main():
    cfg=configuration();_,grid=load_calendar();cutoff=split_position(grid)
    source_sha256=hashlib.sha256((ROOT/cfg['source']).read_bytes()).hexdigest()
    baseline_sha256=json.loads((ROOT/'revision/artifacts/phase1/original_manifest.json').read_text())['files'][cfg['source']]['sha256']
    input_sha256=json.loads((REVISION/'artifacts/phase1/input_audit.json').read_text())['source_sha256']
    assert source_sha256==baseline_sha256==input_sha256
    selection=json.loads((REVISION/'artifacts/phase2/selection.json').read_text())
    assert selection['protocol_signature']==validation_signature()
    validation=[]
    for task in load_tasks('validate'):
        p=REVISION/'artifacts/phase2/runs'/task['id']
        m=json.loads((p/'metadata.json').read_text())
        assert m['protocol_signature']==validation_signature() and m['task']==task
        if m['status']!='completed':continue
        d=pd.read_csv(p/'forecasts.csv',parse_dates=['target_timestamp'])
        assert d.target_timestamp.max()<grid.index[cutoff]
        score=float((d.original_target-d.base_prediction).abs().groupby(d.window).mean().mean())
        rmse=float(np.sqrt(((d.original_target-d.base_prediction)**2).mean()))
        np.testing.assert_allclose([score,rmse],[m['mean_weekly_mae'],m['pooled_rmse']])
        validation.append((task['family'],score,rmse,task['id'],task['candidate']))
    for family in selection['selected']:
        candidates=[x[1:] for x in validation if x[0]==family]
        assert sorted(candidates)[0][3]==selection['selected'][family]
    mask=grid[['pm2_5']+cfg['broad_features']].notna().all(axis=1)
    reviewed=[];scalers=0;neural_samples=0;reused=0;recoveries=0
    for task in tasks():
        folder=REVISION/'artifacts/coverage_reconsideration/runs'/task['id']
        m=json.loads((folder/'metadata.json').read_text());fit=m['fit']
        if m.get('numerical_recovery'):
            from .broad_sarimax_recovery import verify_metadata
            verify_metadata(m)
            recoveries+=1
        assert m['status']=='completed' and m['task']==task and m['protocol_signature']==signature()
        assert task['candidate']==selection['selected'][task['family']]
        origin=pd.Timestamp(m['fit_origin']);history=grid.loc[grid.index<origin]
        assert len(history)==fit['training_calendar_hours'] and str(origin)==fit['fit_end_exclusive']
        assert not fit['target_imputed'] and not fit['target_clipped']
        features=task['features']
        if features:
            values=history[features].dropna()
            if task['clip_inputs']:
                lower,upper=values.quantile(.01),values.quantile(.99)
                for f in features:
                    np.testing.assert_allclose(fit['input_clip_bounds']['lower'][f],lower[f])
                    np.testing.assert_allclose(fit['input_clip_bounds']['upper'][f],upper[f])
                values=values.clip(lower,upper,axis=1)
            np.testing.assert_allclose([fit['scaler']['mean'][f] for f in features],values.mean(),rtol=1e-10)
            np.testing.assert_allclose([fit['scaler']['scale'][f] for f in features],values.std(ddof=0),rtol=1e-10)
            scalers+=1
        if task['family']=='neuralprophet':
            _,episodes=neural_training_segments(history,features)
            assert fit['training_samples']==sum(x['training_samples'] for x in episodes)
            neural_samples+=1
        if m.get('reused_from'):
            reused+=1
            source=ROOT/m['reused_from']
            digest=hashlib.sha256((source/'metadata.json').read_bytes()).hexdigest()
            assert digest==m['original_source_metadata_sha256']
        d=pd.read_csv(folder/'forecasts.csv',parse_dates=['target_timestamp','forecast_origin'])
        assert d.target_timestamp.min()>=origin
        np.testing.assert_array_equal(d.score_eligible,mask.loc[d.target_timestamp])
        np.testing.assert_allclose(d.original_target,grid.loc[d.target_timestamp,'pm2_5'],atol=0,rtol=0,equal_nan=True)
        assert np.isfinite(d.loc[d.score_eligible,'base_prediction']).all()
        reviewed.append(task['id'])
    table=windows(grid);full=table[table.full_week]
    assert len(full)==23 and full.scored_hours.sum()==3624
    baseline=REVISION/'artifacts/coverage_reconsideration/baselines/persistence.csv'
    b=pd.read_csv(baseline)
    for _,d in b.groupby('window'):
        origin=pd.Timestamp(d.forecast_origin.iloc[0]);past=grid.loc[grid.index<origin,'pm2_5'].dropna()
        np.testing.assert_allclose(d.base_prediction,past.iloc[-1],rtol=0,atol=1e-10)
    v=json.loads((REVISION/'artifacts/coverage_reconsideration/verification.json').read_text())
    assert v['ready'] and v['additional_checks_passed'] and v['complete_tasks']==129
    results=pd.read_csv(REVISION/'artifacts/phase3/performance.csv')
    assert len(results)==27 and results.hours.eq(3624).all()
    seed_summary=pd.read_csv(REVISION/'artifacts/phase3/neuralprophet_seed_summary.csv').set_index('regime')
    for regime in ('frozen','walk'):
        names=[f'neuralprophet_{regime}_s{seed}' for seed in (42,123,2026)]
        values=results.set_index('stream').loc[names,'pooled_mae']
        assert int(seed_summary.loc[regime,'seed_count'])==3
        np.testing.assert_allclose([seed_summary.loc[regime,'pooled_mae_mean'],
                                    seed_summary.loc[regime,'pooled_mae_sd']],
                                   [values.mean(),values.std(ddof=1)])
    components=pd.read_csv(REVISION/'artifacts/phase3/prophet_components.csv')
    component_summary=pd.read_csv(REVISION/'artifacts/phase3/prophet_component_summary.csv').set_index('component')
    for name,part in components.groupby('component'):
        np.testing.assert_allclose(component_summary.loc[name,'hour_weighted_mean_absolute'],
                                   np.average(part.mean_absolute,weights=part.hours))
        assert int(component_summary.loc[name,'hours'])==3624
    timing=pd.read_csv(REVISION/'artifacts/phase3/core_timing.csv')
    for _,row in timing[timing.fit_timer_boundary=='reused_source'].iterrows():
        assert row.source_forecast_seconds>0 and row.forecast_seconds==0
    figures=REVISION/'artifacts/phase3/figures'
    for stem in ['lead_hour_mae','lead_day_mae','weekly_mae_chronology',
                 'weekly_mae_distribution','correction_diagnostics','regime_comparison']:
        assert (figures/(stem+'.pdf')).exists() and (figures/(stem+'.png')).exists()
    evidence=dict(source_sha256=source_sha256,
                  protocol_signature=signature(),validation_signature=validation_signature(),
                  successful_validation_candidates=len(validation),corrected_runs_checked=len(reviewed),
                  pre_origin_scalers_checked=scalers,neural_episode_sample_counts_checked=neural_samples,
                  identical_first_origin_reuses_checked=reused,performance_streams=len(results),
                  separately_signed_numerical_recoveries_checked=recoveries,
                  neuralprophet_seed_summary_checked=True,component_hour_weighting_checked=True,
                  reused_forecast_source_cost_checked=True,figure_pairs_checked=6,
                  primary_origins=23,scored_hours=3624,ready_for_author_evidence_review=True)
    output=REVISION/'artifacts/phase3/postfit_audit.json'
    output.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
