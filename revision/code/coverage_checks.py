"""Additional evidence checks, independent of fitting-code signatures."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .protocol import ROOT,REVISION,configuration,load_calendar
from .coverage_protocol import OUT,windows,seasonal_past_fill,metrics,signature
from .coverage_runner import tasks,verify_and_report


def check_frame(frame,grid,expected_windows):
    frame=frame.copy()
    for column in ['target_timestamp','forecast_origin']:frame[column]=pd.to_datetime(frame[column])
    assert set(frame.window)==set(expected_windows),'Wrong calendar origins'
    assert len(frame)==168*len(expected_windows),'Incomplete scheduled stream'
    assert not frame[['forecast_origin','target_timestamp']].duplicated().any(),'Duplicate targets'
    np.testing.assert_array_equal(frame.target_timestamp-frame.forecast_origin,pd.to_timedelta(frame.lead_hour-1,unit='h'))
    raw=grid.loc[frame.target_timestamp]
    mask=raw[['pm2_5']+configuration()['broad_features']].notna().all(axis=1).to_numpy()
    np.testing.assert_array_equal(frame.score_eligible,mask)
    np.testing.assert_array_equal(frame.observed,raw.pm2_5.notna().to_numpy())
    np.testing.assert_allclose(frame.original_target,raw.pm2_5.to_numpy(),rtol=0,atol=0,equal_nan=True)
    assert np.isfinite(frame.loc[mask,'base_prediction']).all(),'Missing scored predictions'
    return frame


def main():
    verify_and_report()
    info=json.loads((OUT/'verification.json').read_text())
    if not info['ready']:raise RuntimeError('Broader evidence not ready')
    _,grid=load_calendar();table=windows(grid);full=table[table.full_week]
    for task in tasks():
        folder=OUT/'runs'/task['id'];meta=json.loads((folder/'metadata.json').read_text())
        assert meta['task']==task,'Run task/configuration changed'
        frame=check_frame(pd.read_csv(folder/'forecasts.csv'),grid,[task['week']] if task['regime']=='walk' else range(1,24))
        if task['regime']=='frozen':
            assert meta['strict_reproduction_max_difference']>=0
            assert frame.score_eligible.sum()==3624
        for diag in meta['completed_weeks']:
            row=full[full.window==diag['window']].iloc[0]
            observed=frame[frame.window==diag['window']]
            assert int(observed.score_eligible.sum())==int(row.scored_hours)==diag['scored_hours']
            if task['family']=='neuralprophet':
                assert diag['history_target_filled_hours']==int(row.missing_context_target_hours)
            else:assert diag['history_target_filled_hours']==0
            if not diag.get('reused_strict_forecast'):
                h=grid.iloc[int(row.position)-168:int(row.position)][task['features']]
                assert diag['history_input_filled_cells']==int(h.isna().sum().sum()) if task['family']=='neuralprophet' else diag['history_input_filled_cells']==0
                assert diag['future_placeholder_cells']==int(grid.iloc[int(row.position):int(row.position)+168][task['features']].isna().sum().sum())
                assert diag['placeholder_max_scored_prediction_difference']<=0.0001+0.000001*float(np.abs(observed.loc[observed.score_eligible,'base_prediction']).max())
        if task['family']=='sarimax':
            assert np.isfinite(list(meta['fit']['parameter_estimates'].values())).all()
            opt=meta['fit']['optimizer']
            if meta['fit_executed']:
                assert pd.Timestamp(opt['initialization_source_cutoff'])<=pd.Timestamp(meta['fit_origin'])
                assert opt['final_log_likelihood']>=opt['initial_log_likelihood']-1e-5
        if task['family']=='neuralprophet':
            trace_folder=ROOT/meta['reused_from'] if meta.get('reused_from') else folder
            if not (trace_folder/'training_trace.csv').exists():
                source_meta=json.loads((trace_folder/'metadata.json').read_text())
                trace_folder=trace_folder.parent/source_meta['reused_from_run']
            trace=pd.read_csv(trace_folder/'training_trace.csv')
            assert len(trace)==50 and np.isfinite(trace.Loss).all()
    for name,cycle in [('persistence',1),('daily_persistence',24),('weekly_persistence',168)]:
        frame=check_frame(pd.read_csv(OUT/'baselines'/f'{name}.csv'),grid,range(1,24))
        for row in full.itertuples():
            p=int(row.position);history=seasonal_past_fill(grid.iloc[:p][['pm2_5']])
            predicted=np.resize(history.pm2_5.iloc[-cycle:].to_numpy(),168)
            np.testing.assert_allclose(frame.loc[frame.window==row.window,'base_prediction'],predicted,rtol=0,atol=1e-10)
    files=list((OUT/'corrections').glob('*_alpha_*.csv'))
    expected={f"{t['id']}_alpha_{str(a).replace('.','p')}.csv" for t in tasks() if t['stage']=='core' and t['regime']=='frozen'
              for a in [0.]+configuration()['ewma_alpha_sensitivity']}
    assert {f.name for f in files}==expected
    for file in files:
        frame=check_frame(pd.read_csv(file),grid,range(1,24));alpha=float(frame.alpha.iloc[0])
        assert frame.alpha.eq(alpha).all()
        assert np.isfinite(frame.loc[frame.score_eligible,'corrected_prediction']).all()
    info.update(additional_checks_passed=True,checks_source='revision/code/coverage_checks.py')
    (OUT/'verification.json').write_text(json.dumps(info,indent=2))
    print('Broader checks passed: 129 tasks, 23 origins, 3,624 observed hours; baseline causality, missingness and training diagnostics verified.')


if __name__=='__main__':main()
