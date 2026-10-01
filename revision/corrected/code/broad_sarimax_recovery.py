"""Explicitly signed numerical supplement for one failed broad-input control."""
import hashlib
import json
import resource
import shutil
import time
import traceback
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from .protocol import REVISION, load_calendar, fit_input_scaler, transform_inputs
from .coverage_protocol import OUT, signature as base_signature, windows, forecast, rows, metrics
from .coverage_runner import tasks
from .phase2_models import Fitted, advance_frozen_sarimax
from .phase2_runner import signature as validation_signature

POLICY=REVISION/'config/broad_sarimax_recovery.json'


def signature():
    h=hashlib.sha256()
    h.update(Path(__file__).read_bytes());h.update(POLICY.read_bytes())
    h.update(base_signature().encode())
    return h.hexdigest()


def verify_metadata(meta):
    recovery=meta.get('numerical_recovery')
    if not recovery:return
    policy=json.loads(POLICY.read_text())
    assert meta['task']['id']==policy['task_id']
    assert meta['protocol_signature']==policy['base_signature']==base_signature()
    assert recovery['signature']==signature() and recovery['version']==policy['version']
    opt=meta['fit']['optimizer']
    assert opt['converged'] and opt['iterations']<=policy['maxiter']
    assert opt['final_log_likelihood']>=opt['initial_log_likelihood']-1e-5
    assert opt['initialization_source_cutoff']==meta['fit_origin']


def main():
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    policy=json.loads(POLICY.read_text());assert base_signature()==policy['base_signature']
    task=next(t for t in tasks() if t['id']==policy['task_id'])
    folder=OUT/'runs'/task['id'];mp=folder/'metadata.json'
    old=json.loads(mp.read_text())
    if old['status']=='completed':verify_metadata(old);return
    assert old['status']=='failed' and old['task']==task
    archive=OUT/'failed_attempts'/task['id'];archive.mkdir(parents=True,exist_ok=True)
    for name in ('metadata.json','run.log'):
        if not (archive/name).exists():shutil.copy2(folder/name,archive/name)
    _,grid=load_calendar();table=windows(grid);selected=table[table.full_week]
    pos=int(selected.iloc[0].position);features=task['features'];started=time.perf_counter()
    meta=dict(task=task,status='running',protocol_signature=base_signature(),
        strict_protocol_signature=validation_signature(),fit_origin=str(grid.index[pos]),
        started_utc=pd.Timestamp.now(tz='UTC').isoformat(),fit_executed=True,
        restored_parameters_from=None,
        numerical_recovery=dict(version=policy['version'],signature=signature(),policy=str(POLICY.relative_to(REVISION))))
    mp.write_text(json.dumps(meta,indent=2))
    try:
        began=time.perf_counter();history=grid.iloc[:pos][['pm2_5']+features]
        scaler,bounds=fit_input_scaler(history,features,False)
        scaled=transform_inputs(history,features,scaler,bounds)
        model=SARIMAX(scaled.pm2_5,exog=scaled[features].ffill(),
            order=tuple(task['candidate']['order']),seasonal_order=tuple(task['candidate']['seasonal_order']),
            enforce_stationarity=False,enforce_invertibility=False)
        initial=model.start_params;initial_llf=float(model.loglike(initial))
        assert np.isfinite(initial).all() and np.isfinite(initial_llf)
        prep=time.perf_counter()-began;began=time.perf_counter();iteration=0
        def checkpoint(params):
            nonlocal iteration
            iteration+=1
            if iteration%10==0:
                record=dict(iteration=iteration,parameters=list(map(float,params)),
                    elapsed_seconds=time.perf_counter()-began,parameter_coordinate='optimizer untransformed')
                (folder/'recovery_optimizer_checkpoint.json').write_text(json.dumps(record,indent=2))
                print('training optimizer iteration',iteration,flush=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            fitted=model.fit(start_params=initial,method='minimize',min_method='L-BFGS-B',
                maxiter=policy['maxiter'],maxls=policy['maxls'],optim_score='approx',
                optim_complex_step=True,disp=False,low_memory=True,cov_type='none',callback=checkpoint)
        fit=dict(family='sarimax',candidate=task['candidate'],features=features,clip_inputs=False,seed=42,
            fit_end_exclusive=str(grid.index[pos]),training_calendar_hours=pos,
            observed_training_targets=int(history.pm2_5.notna().sum()),target_imputed=False,target_clipped=False,
            scaler={'mean':dict(zip(features,map(float,scaler.mean_))),
                    'scale':dict(zip(features,map(float,scaler.scale_)))},input_clip_bounds=None,
            preparation_seconds=prep,fit_seconds=time.perf_counter()-began,device='cpu',cpu_threads=2,
            parameter_estimates=dict(zip(fitted.param_names,map(float,fitted.params))),
            optimizer=dict(converged=bool(fitted.mle_retvals.get('converged')),
                iterations=int(fitted.mle_retvals.get('iterations',0)),initial_log_likelihood=initial_llf,
                final_log_likelihood=float(fitted.llf),initialization_source='corrected_training_conditional_sum_of_squares',
                initialization_source_cutoff=str(grid.index[pos]),method='complex-step L-BFGS-B, maxiter400/maxls100, default tolerances',
                warnings=[str(w.message) for w in caught[-6:]]))
        meta['fit']=fit;mp.write_text(json.dumps(meta,indent=2))
        verify_metadata(meta)
        assert np.isfinite(fitted.params).all() and np.isfinite(fitted.llf)
        print('Training convergence accepted; generating forecasts',flush=True)
        f=Fitted('sarimax',fitted,features,scaler,bounds,pos,fit)
        parts=[];diags=[];previous=pos
        for row in selected.itertuples():
            state_seconds=advance_frozen_sarimax(f,grid,previous,int(row.position)) if row.position>previous else 0.
            previous=int(row.position);prediction,score,diag,_=forecast(f,grid,previous)
            diag['state_update_seconds']=state_seconds
            frame=rows(task,grid,row,prediction,score,diag)
            frame.to_csv(folder/f'week_{int(row.window):02d}.csv',index=False);parts.append(frame)
            diags.append(dict(window=int(row.window),**diag))
        combined=pd.concat(parts,ignore_index=True);combined.to_csv(folder/'forecasts.csv',index=False)
        meta.update(status='completed',completed_weeks=diags,completed_utc=pd.Timestamp.now(tz='UTC').isoformat(),
            sampled_self_peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,**metrics(combined))
        mp.write_text(json.dumps(meta,indent=2));verify_metadata(meta)
    except Exception:
        meta.update(status='failed',error=traceback.format_exc());mp.write_text(json.dumps(meta,indent=2));raise
    finally:
        event=dict(task_id=task['id'],returncode=0 if meta['status']=='completed' else 1,
            elapsed_seconds=time.perf_counter()-started,sampled_peak_rss_mib=None,guard_reason=None,
            numerical_recovery_signature=signature())
        with (OUT/'supervisor.jsonl').open('a') as log:log.write(json.dumps(event)+'\n')


if __name__=='__main__':main()
