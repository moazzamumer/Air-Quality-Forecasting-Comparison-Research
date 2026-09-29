"""Bounded numerical recovery of failed SARIMAX comparison fits, with provenance."""
import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
import traceback
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import psutil
from .protocol import ROOT, REVISION, configuration, load_calendar, fit_input_scaler, transform_inputs
from .phase2_models import Fitted, forecast, advance_frozen_sarimax
from .phase2_runner import OUT, signature, weekly_rows

POLICY=REVISION/'config/sarimax_numerical_recovery.json'


def eligible_failures():
    records=[]
    files=list((OUT/'runs').glob('core_sarimax_*/metadata.json'))+list((OUT/'runs').glob('ablate_sarimax_*/metadata.json'))
    for file in sorted(files):
        record=json.loads(file.read_text())
        if (record.get('status')=='failed' and record.get('protocol_signature')==signature()
                and record.get('fit',{}).get('optimizer',{}).get('converged') is False):
            records.append(record['task']['id'])
    return records


def recover(original_id):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    source_path=OUT/'runs'/original_id/'metadata.json'
    source=json.loads(source_path.read_text());original=source['task']
    if original['family']!='sarimax' or original['stage'] not in ['core','ablate'] or source['status']!='failed':
        raise ValueError('Numerical recovery is restricted to failed final-comparison SARIMAX fits')
    if source['protocol_signature']!=signature():raise ValueError('Original failure uses a different protocol')
    task=dict(original,id='recover_'+original_id,stage='recovery',recovered_task_id=original_id)
    folder=OUT/'runs'/task['id'];folder.mkdir(parents=True,exist_ok=True)
    policy=json.loads(POLICY.read_text());_,grid=load_calendar()
    windows=pd.read_csv(REVISION/'artifacts/phase1/test_windows.csv')
    rows=(windows[(windows.window==task['week']) & windows.eligible]
          if task['regime']=='walk' else windows[windows.eligible])
    position=grid.index.get_loc(pd.Timestamp(source['fit_origin']));features=task['features']
    history=grid.iloc[:position][['pm2_5']+features].copy()
    scaler,bounds=fit_input_scaler(history,features,task['clip_inputs'])
    scaled=transform_inputs(history,features,scaler,bounds)
    if features:
        np.testing.assert_allclose(scaler.mean_,[source['fit']['scaler']['mean'][f] for f in features],rtol=0,atol=1e-10)
        np.testing.assert_allclose(scaler.scale_,[source['fit']['scaler']['scale'][f] for f in features],rtol=0,atol=1e-10)
    model=SARIMAX(scaled.pm2_5,exog=scaled[features].ffill() if features else None,order=tuple(task['candidate']['order']),
                  seasonal_order=tuple(task['candidate']['seasonal_order']),
                  enforce_stationarity=False,enforce_invertibility=False)
    estimates=source['fit']['parameter_estimates']
    start_params=np.array([estimates[name] for name in model.param_names])
    if not np.isfinite(start_params).all():raise ValueError('Failed-fit starting parameters are not finite')
    initial_llf=float(model.loglike(start_params))
    if not np.isfinite(initial_llf):raise ValueError('Failed-fit starting likelihood is not finite')
    reference=json.loads((OUT/'runs/core_sarimax_frozen_s42/metadata.json').read_text())
    if reference['status']!='completed' or reference['task']['candidate']!=task['candidate']:
        raise ValueError('Warm initialization must come from the converged selected model')
    if pd.Timestamp(reference['fit_origin'])>pd.Timestamp(source['fit_origin']):
        raise ValueError('Warm initialization cannot use a later data cutoff')
    reference_params=reference['fit']['parameter_estimates']
    warm_params=[]
    for name in model.param_names:
        value=reference_params.get(name,0.)
        if name in features and name in reference['fit']['features']:
            value*=float(scaler.scale_[features.index(name)])/reference['fit']['scaler']['scale'][name]
        warm_params.append(value)
    warm_params=np.asarray(warm_params)
    warm_llf=float(model.loglike(warm_params))
    if not np.isfinite(warm_llf):raise ValueError('Earlier converged parameter initialization has nonfinite likelihood')
    meta=dict(task=task,status='running',protocol_signature=signature(),
              numerical_policy=policy,numerical_policy_sha256=hashlib.sha256(POLICY.read_bytes()).hexdigest(),
              recovery_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              recovered_from_failed_run=original_id,fit_origin=source['fit_origin'],
              original_failed_fit_seconds=source['fit']['fit_seconds'],
              initialization_source_run=reference['task']['id'],initialization_source_cutoff=reference['fit_origin'],
              package_versions=source['package_versions'],python=source['python'],platform=source['platform'],
              started_utc=pd.Timestamp.now(tz='UTC').isoformat())
    meta_path=folder/'metadata.json';meta_path.write_text(json.dumps(meta,indent=2))
    start=time.perf_counter()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            stage=policy['final_stage']
            final=model.fit(start_params=warm_params,method=stage['method'],min_method=stage['min_method'],
                            maxiter=stage['maxiter'],maxls=stage['maxls'],optim_score=stage['optim_score'],
                            optim_complex_step=stage['optim_complex_step'],
                            disp=False,low_memory=True,cov_type='none')
        fit=source['fit'].copy()
        fit['fit_seconds']=time.perf_counter()-start
        fit['optimizer']=dict(converged=bool(final.mle_retvals.get('converged',False)),
             recovery=True,initial_log_likelihood=initial_llf,
             warm_start_log_likelihood=warm_llf,method=stage,
             final_iterations=int(final.mle_retvals.get('iterations',0)),final_log_likelihood=float(final.llf),
             warnings=[str(w.message) for w in caught[-6:]])
        fit['parameter_estimates']={str(k):float(v) for k,v in zip(final.param_names,final.params)}
        meta['fit']=fit
        if not fit['optimizer']['converged'] or not np.isfinite(final.llf) or not np.isfinite(final.params).all():
            raise RuntimeError('Numerical recovery did not reach a valid converged fit')
        if final.llf < initial_llf - 1e-5:
            raise RuntimeError('Numerical recovery reduced the training log likelihood')
        fitted=Fitted('sarimax',final,features,scaler,bounds,position,fit)
        pieces=[];previous=position;week_records=[]
        for row in rows.itertuples():
            current=int(row.position);state_seconds=0.
            if current>previous:
                state_seconds=advance_frozen_sarimax(fitted,grid,previous,current);previous=current
            values,seconds,components=forecast(fitted,grid,current)
            week=weekly_rows(task,grid,row,values,seconds,fit['fit_seconds'] if current==position else 0.,state_seconds)
            week.to_csv(folder/f'week_{int(row.window):02d}.csv',index=False);pieces.append(week)
            week_records.append(dict(window=int(row.window),origin=str(grid.index[current]),
                                     forecast_seconds=seconds,state_update_seconds=state_seconds,
                                     mae=float(np.mean(np.abs(week.original_target-week.base_prediction))),
                                     rmse=float(np.sqrt(np.mean((week.original_target-week.base_prediction)**2)))))
        frame=pd.concat(pieces,ignore_index=True);frame.to_csv(folder/'forecasts.csv',index=False)
        meta.update(status='completed',completed_utc=pd.Timestamp.now(tz='UTC').isoformat(),scored_hours=len(frame),
                    completed_weeks=week_records,mean_weekly_mae=float(np.mean([w['mae'] for w in week_records])),
                    pooled_rmse=float(np.sqrt(np.mean((frame.original_target-frame.base_prediction)**2))),
                    peak_rss_mib_self=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
        meta_path.write_text(json.dumps(meta,indent=2))
        print('Numerical recovery converged:',original_id,flush=True)
    except Exception:
        meta.update(status='failed',error=traceback.format_exc())
        meta_path.write_text(json.dumps(meta,indent=2));raise


def supervise(only=None):
    failures=eligible_failures()
    if only:failures=[x for x in failures if x in only]
    for original_id in failures:
        folder=OUT/'runs'/('recover_'+original_id);folder.mkdir(parents=True,exist_ok=True)
        meta=folder/'metadata.json'
        if meta.exists() and json.loads(meta.read_text()).get('status')=='completed':continue
        env=os.environ.copy()
        for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='2'
        env.update(MPLCONFIGDIR='/tmp/weather-revision-matplotlib',CUDA_VISIBLE_DEVICES='')
        start=time.perf_counter();peak=0;reason=None
        limit=min(6*1024**3,int(psutil.virtual_memory().available*.75))
        print('RECOVER',original_id,flush=True)
        with (folder/'run.log').open('w') as log:
            proc=subprocess.Popen([sys.executable,'-u','-m','revision.code.phase2_recover','--child',original_id],
                                  cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            while proc.poll() is None:
                try:
                    root=psutil.Process(proc.pid)
                    rss=sum(p.memory_info().rss for p in [root]+root.children(recursive=True) if p.is_running());peak=max(peak,rss)
                    if rss>limit:reason='memory_guard'
                    elif time.perf_counter()-start>5400:reason='90_minute_recovery_guard'
                    if reason:
                        for child in root.children(recursive=True):child.terminate()
                        proc.terminate()
                        try:proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:proc.kill()
                except psutil.NoSuchProcess:pass
                time.sleep(.5)
            proc.wait()
        measurement=dict(original_id=original_id,returncode=proc.returncode,elapsed_seconds=time.perf_counter()-start,
                         sampled_peak_rss_mib=peak/1024**2,guard_reason=reason)
        with (OUT/'recovery_supervisor.jsonl').open('a') as stream:stream.write(json.dumps(measurement)+'\n')
        print(json.dumps(measurement),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--child');parser.add_argument('--only',nargs='*');args=parser.parse_args()
    if args.child:recover(args.child)
    else:supervise(args.only)


if __name__=='__main__':main()
