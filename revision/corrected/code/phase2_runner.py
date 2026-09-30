"""Resumable, isolated Phase 2 experiments. Run from the project root.

Each task produces a complete forecast CSV and metadata or an explicit failure.
The supervisor runs one memory-heavy model process at a time.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback
import warnings

import numpy as np
import pandas as pd
import psutil

from .protocol import ROOT, REVISION, configuration, load_calendar, split_position, window_table, persistence, apply_bias
from .phase2_models import fit_model, forecast, advance_frozen_sarimax

OUT = REVISION / 'artifacts/phase2'
CANDIDATES = {
    'sarimax': [dict(order=o, seasonal_order=s) for o in [[1,0,1],[1,1,1]] for s in [[1,0,1,24],[1,1,1,24]]],
    'prophet': [dict(seasonality_mode=m) for m in ['additive','multiplicative']],
    'neuralprophet': [dict(epochs=e) for e in [30,50]],
}
FAMILIES = tuple(CANDIDATES)


def signature():
    paths = [REVISION/'config/protocol.json', REVISION/'code/protocol.py',
             REVISION/'code/model_checks.py', REVISION/'code/phase2_models.py',
             REVISION/'code/phase2_runner.py']
    h = hashlib.sha256()
    for p in paths:
        h.update(p.read_bytes())
    return h.hexdigest()


def paths(task):
    folder = OUT/'runs'/task['id']
    return folder, folder/'metadata.json', folder/'forecasts.csv'


def load_tasks(stage, selection=None):
    cfg = configuration()
    if stage == 'validate':
        return [dict(id=f'validate_{f}_{i}',stage=stage,family=f,candidate=c,seed=42,
                     features=cfg['selected_features'],clip_inputs=False,regime='frozen')
                for f, choices in CANDIDATES.items() for i,c in enumerate(choices)]
    if selection is None:
        selection = json.loads((OUT/'selection.json').read_text())['selected']
    if stage == 'core':
        return ([dict(id=f'core_{f}_frozen_s{seed}',stage=stage,family=f,candidate=selection[f],
                      seed=seed,features=cfg['selected_features'],clip_inputs=False,regime='frozen')
                 for f in FAMILIES for seed in (cfg['seeds'] if f=='neuralprophet' else [42])]
                + [dict(id=f'core_{f}_walk_w{int(w.window):02d}_s{seed}',stage=stage,family=f,
                        candidate=selection[f],seed=seed,features=cfg['selected_features'],
                        clip_inputs=False,regime='walk',week=int(w.window))
                   for f in FAMILIES for seed in (cfg['seeds'] if f=='neuralprophet' else [42])
                   for w in pd.read_csv(REVISION/'artifacts/phase1/test_windows.csv').itertuples() if w.eligible])
    if stage == 'ablate':
        return [dict(id=f'ablate_{f}_{variant}',stage=stage,family=f,candidate=selection[f],
                     seed=42,features=([] if variant=='no_inputs' else
                                       cfg['broad_features'] if variant=='broad' else cfg['selected_features']),
                     clip_inputs=(variant=='clip'),regime='frozen',variant=variant)
                for f in FAMILIES for variant in ['no_inputs','broad','clip']]
    raise ValueError(stage)


def weekly_rows(task, grid, row, predicted, seconds, fit_seconds, state_seconds=0, components=None):
    p = int(row.position); h=configuration()['horizon_hours']
    actual = grid.iloc[p:p+h][configuration()['target']].to_numpy(dtype=float)
    if len(actual)!=h or not np.isfinite(actual).all():
        raise ValueError('Scoring would include an absent target')
    result = pd.DataFrame(dict(run_id=task['id'],family=task['family'],regime=task['regime'],
        feature_set=task.get('variant','selected'),clip_inputs=task['clip_inputs'],seed=task['seed'],
        window=int(row.window),forecast_origin=str(grid.index[p]),
        target_timestamp=grid.index[p:p+h],lead_hour=np.arange(1,h+1),
        original_target=actual,observed=True,eligible=True,base_prediction=predicted,
        applied_bias=0.0,corrected_prediction=predicted,
        fit_seconds=fit_seconds,forecast_seconds=seconds,state_update_seconds=state_seconds))
    if components is not None:
        comp_path = paths(task)[0]/f'components_w{int(row.window):02d}.csv'
        components.to_csv(comp_path,index=False)
    return result


def execute(task):
    folder, meta_path, predictions_path = paths(task)
    folder.mkdir(parents=True,exist_ok=True)
    cfg = configuration(); _,grid = load_calendar()
    val = pd.read_csv(REVISION/'artifacts/phase1/validation_windows.csv')
    test = pd.read_csv(REVISION/'artifacts/phase1/test_windows.csv')
    if task['stage']=='validate':
        rows = val[val.eligible]
        fit_position = int(rows.iloc[0].position)
    elif task['regime']=='walk':
        rows = test[(test.window==task['week']) & test.eligible]
        fit_position = int(rows.iloc[0].position)
    else:
        rows = test[test.eligible]
        fit_position = split_position(grid)
    if len(rows)==0: raise ValueError('No eligible windows for task')
    metadata = dict(task=task,protocol_signature=signature(),status='running',
                    python=platform.python_version(),platform=platform.platform(),
                    package_versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','statsmodels','prophet','neuralprophet','scikit-learn']},
                    fit_origin=str(grid.index[fit_position]),started_utc=pd.Timestamp.now(tz='UTC').isoformat())
    meta_path.write_text(json.dumps(metadata,indent=2,default=str))
    try:
        fitted = fit_model(grid,fit_position,task['family'],task['candidate'],task['features'],
                           task['clip_inputs'],task['seed'],folder)
        metadata['fit'] = fitted.metadata
        if task['family']=='sarimax' and not fitted.metadata['optimizer']['converged']:
            raise RuntimeError('SARIMAX did not converge under bounded optimizer policy')
        all_rows=[]; previous_end=fit_position; week_meta=[]
        # State propagation spans skipped weeks because the entire calendar is used.
        for row in rows.itertuples():
            position=int(row.position)
            state_seconds=0.0
            if task['family']=='sarimax' and position>previous_end:
                state_seconds=advance_frozen_sarimax(fitted,grid,previous_end,position)
                previous_end=position
            if task['regime']=='walk' and position!=fit_position:
                raise AssertionError('Walk-forward task may score only its own fitted origin')
            predicted,forecast_seconds,components=forecast(fitted,grid,position)
            result=weekly_rows(task,grid,row,predicted,forecast_seconds,
                               fitted.metadata['fit_seconds'] if position==fit_position else 0.0,
                               state_seconds,components)
            all_rows.append(result)
            # Atomic per-origin checkpoint; a crash never masquerades as a complete run.
            checkpoint=folder/f'week_{int(row.window):02d}.csv'
            result.to_csv(checkpoint,index=False)
            week_meta.append(dict(window=int(row.window),origin=str(grid.index[position]),
                                  forecast_seconds=forecast_seconds,state_update_seconds=state_seconds,
                                  mae=float(np.mean(np.abs(result.original_target-result.base_prediction))),
                                  rmse=float(np.sqrt(np.mean((result.original_target-result.base_prediction)**2)))))
            metadata['completed_weeks']=week_meta
            meta_path.write_text(json.dumps(metadata,indent=2,default=str))
            print(f"{task['id']} week {int(row.window)} MAE {week_meta[-1]['mae']:.4f}",flush=True)
        combined=pd.concat(all_rows,ignore_index=True)
        combined.to_csv(predictions_path,index=False)
        metadata['status']='completed'
        metadata['completed_utc']=pd.Timestamp.now(tz='UTC').isoformat()
        metadata['scored_hours']=len(combined)
        metadata['mean_weekly_mae']=float(np.mean([w['mae'] for w in week_meta]))
        metadata['pooled_rmse']=float(np.sqrt(np.mean((combined.original_target-combined.base_prediction)**2)))
        metadata['peak_rss_mib_self']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        meta_path.write_text(json.dumps(metadata,indent=2,default=str))
    except Exception:
        metadata['status']='failed'
        metadata['error']=traceback.format_exc()
        metadata['peak_rss_mib_self']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        meta_path.write_text(json.dumps(metadata,indent=2,default=str))
        raise


def select_validation():
    result={}; evidence={}
    for family in FAMILIES:
        candidates=[]
        for task in load_tasks('validate'):
            if task['family']!=family:continue
            _,mp,fp=paths(task)
            if not mp.exists():continue
            record=json.loads(mp.read_text())
            if record.get('status')=='completed' and fp.exists() and record.get('protocol_signature')==signature():
                candidates.append((record['mean_weekly_mae'],record['pooled_rmse'],task['id'],task['candidate']))
        evidence[family]=[dict(mean_weekly_mae=x[0],pooled_rmse=x[1],run_id=x[2],candidate=x[3]) for x in sorted(candidates)]
        if not candidates:raise RuntimeError(f'No valid converged validation candidate for {family}')
        result[family]=sorted(candidates)[0][3]
    output=dict(status='selected_from_training_only_validation',selection_rule='mean weekly MAE, pooled RMSE tie break',
                selected=result,candidates=evidence,protocol_signature=signature())
    (OUT/'selection.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2),flush=True)


def run_baselines():
    _,grid=load_calendar(); test=pd.read_csv(REVISION/'artifacts/phase1/test_windows.csv')
    folder=OUT/'baselines';folder.mkdir(parents=True,exist_ok=True)
    for name,cycle in [('persistence',1),('daily_persistence',24),('weekly_persistence',168)]:
        rows=[]
        for row in test[test.eligible].itertuples():
            p=int(row.position); predicted=persistence(grid.iloc[:p],168,cycle)
            actual=grid.iloc[p:p+168].pm2_5.to_numpy(dtype=float)
            rows.append(pd.DataFrame(dict(run_id=name,family=name,regime='baseline',feature_set='none',clip_inputs=False,
                seed=0,window=int(row.window),forecast_origin=str(grid.index[p]),target_timestamp=grid.index[p:p+168],
                lead_hour=np.arange(1,169),original_target=actual,observed=True,eligible=True,
                base_prediction=predicted,applied_bias=0.,corrected_prediction=predicted)))
        pd.concat(rows,ignore_index=True).to_csv(folder/f'{name}.csv',index=False)
    print('Saved all three matched baselines',flush=True)


def run_corrections():
    cfg=configuration(); folder=OUT/'corrections';folder.mkdir(parents=True,exist_ok=True)
    summaries=[]
    for task in load_tasks('core'):
        if task['regime']!='frozen':continue
        _,mp,fp=paths(task)
        if not mp.exists() or not fp.exists():continue
        meta=json.loads(mp.read_text())
        if meta.get('status')!='completed':continue
        base=pd.read_csv(fp)
        for alpha in [0.0]+cfg['ewma_alpha_sensitivity']:
            bias=0.; corrected=[]
            for _,week in base.groupby('window',sort=True):
                values=week.base_prediction.to_numpy();actual=week.original_target.to_numpy()
                if alpha==0: pred=values;next_bias=0.
                else: pred,next_bias=apply_bias(values,actual,bias,alpha)
                section=week.copy();section['applied_bias']=bias;section['corrected_prediction']=pred
                section['alpha']=alpha;corrected.append(section);bias=next_bias
            output=pd.concat(corrected,ignore_index=True)
            tag=str(alpha).replace('.','p')
            output.to_csv(folder/f"{task['id']}_alpha_{tag}.csv",index=False)
            summaries.append(dict(run_id=task['id'],alpha=alpha,mean_weekly_mae=float(output.groupby('window').apply(
                lambda x:np.mean(np.abs(x.original_target-x.corrected_prediction)),include_groups=False).mean()),
                pooled_rmse=float(np.sqrt(np.mean((output.original_target-output.corrected_prediction)**2)))))
    pd.DataFrame(summaries).to_csv(folder/'summary.csv',index=False)
    print(f'Saved {len(summaries)} correction streams',flush=True)


def supervise(stage, only=None):
    OUT.mkdir(parents=True,exist_ok=True)
    tasks=load_tasks(stage)
    if only:tasks=[t for t in tasks if t['id'] in only]
    if not tasks:raise ValueError('No tasks matched')
    for task in tasks:
        folder,mp,fp=paths(task)
        if mp.exists() and fp.exists():
            old=json.loads(mp.read_text())
            if old.get('status')=='completed' and old.get('protocol_signature')==signature():
                print('SKIP completed',task['id'],flush=True);continue
        folder.mkdir(parents=True,exist_ok=True)
        environment=os.environ.copy()
        for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','TF_NUM_INTRAOP_THREADS','TF_NUM_INTEROP_THREADS']:
            environment[key]='2'
        environment.update(MPLCONFIGDIR='/tmp/weather-revision-matplotlib',CUDA_VISIBLE_DEVICES='',TF_CPP_MIN_LOG_LEVEL='3')
        command=[sys.executable,'-u','-m','revision.corrected.code.phase2_runner','child',json.dumps(task)]
        start=time.perf_counter();peak=0;reason=None
        available=psutil.virtual_memory().available
        limit=min(6*1024**3,max(1024**3,int(available*.75)))
        print('START',task['id'],'RSS limit GiB',round(limit/1024**3,2),flush=True)
        with (folder/'run.log').open('w') as log:
            proc=subprocess.Popen(command,cwd=ROOT,env=environment,stdout=log,stderr=subprocess.STDOUT)
            while proc.poll() is None:
                try:
                    root=psutil.Process(proc.pid)
                    rss=sum(p.memory_info().rss for p in [root]+root.children(recursive=True) if p.is_running())
                    peak=max(peak,rss)
                    if rss>limit:reason='memory_guard'
                    elif time.perf_counter()-start>10800:reason='three_hour_time_guard'
                    if reason:
                        for child in root.children(recursive=True):child.terminate()
                        proc.terminate()
                        try:proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:proc.kill()
                except psutil.NoSuchProcess:pass
                time.sleep(.5)
            proc.wait()
        summary=dict(task_id=task['id'],returncode=proc.returncode,elapsed_seconds=time.perf_counter()-start,
                     sampled_peak_rss_mib=peak/1024**2,guard_reason=reason)
        with (OUT/'supervisor.jsonl').open('a') as stream:stream.write(json.dumps(summary)+'\n')
        print('END',json.dumps(summary),flush=True)
        if stage=='validate' and proc.returncode!=0:
            print('Candidate failed; inspect',folder/'run.log',flush=True)
    if stage=='validate' and not only:select_validation()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['validate','core','ablate','baselines','correct','child'])
    parser.add_argument('task',nargs='?')
    parser.add_argument('--only',nargs='*')
    args=parser.parse_args()
    warnings.filterwarnings('ignore',category=FutureWarning)
    warnings.filterwarnings('ignore',message='Protobuf gencode version.*')
    if args.stage=='child':execute(json.loads(args.task))
    elif args.stage=='baselines':run_baselines()
    elif args.stage=='correct':run_corrections()
    else:supervise(args.stage,args.only)


if __name__=='__main__':main()
