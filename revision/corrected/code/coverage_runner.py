"""Execute and verify the broader hourly-mask evaluation before Phase 3."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import warnings
import numpy as np
import pandas as pd
import psutil
from .protocol import ROOT,REVISION,configuration,load_calendar,split_position,fit_input_scaler,transform_inputs
from .phase2_models import Fitted,fit_model,advance_frozen_sarimax
from .phase2_runner import OUT as STRICT,signature as strict_signature
from .coverage_protocol import OUT,policy,signature,seasonal_past_fill,latest_observed_persistence,windows,forecast,rows,metrics,audit
from .phase2_status import markdown_table


def tasks():
    cfg=configuration();record=json.loads((STRICT/'selection.json').read_text())
    if record['protocol_signature']!=strict_signature():
        raise ValueError('Corrected validation selection has a stale protocol signature')
    selection=record['selected']
    core=[dict(id=f'core_{f}_frozen_s{s}',stage='core',family=f,regime='frozen',seed=s,
               features=cfg['selected_features'],clip_inputs=False,variant='selected',candidate=selection[f])
          for f in selection for s in (cfg['seeds'] if f=='neuralprophet' else [42])]
    core += [dict(id=f'core_{f}_walk_w{w:02d}_s{s}',stage='core',family=f,regime='walk',seed=s,week=w,
               features=cfg['selected_features'],clip_inputs=False,variant='selected',candidate=selection[f])
          for f in selection for s in (cfg['seeds'] if f=='neuralprophet' else [42]) for w in range(1,24)]
    ablation=[dict(id=f'ablate_{f}_{v}',stage='ablate',family=f,regime='frozen',seed=42,
                  features=[] if v=='no_inputs' else cfg['broad_features'] if v=='broad' else cfg['selected_features'],
                  clip_inputs=v=='clip',variant=v,candidate=selection[f])
              for f in selection for v in ['no_inputs','broad','clip']]
    return core+ablation


def strict_source(task):
    """Only the first walk forecast can share its identical corrected frozen fit."""
    if task['regime']!='walk' or task['week']!=1 or task['variant']!='selected':return None
    frozen=OUT/'runs'/f"core_{task['family']}_frozen_s{task['seed']}"
    if not (frozen/'metadata.json').exists():return None
    meta=json.loads((frozen/'metadata.json').read_text())
    expected=dict(task, id=f"core_{task['family']}_frozen_s{task['seed']}",regime='frozen')
    expected.pop('week',None)
    if meta['status']!='completed' or meta['protocol_signature']!=signature() or meta['task']!=expected:
        raise ValueError('Incompatible corrected frozen source for first walk origin')
    return frozen,meta


def sarimax_model(grid,position,task,source=None):
    """Restore a frozen fit exactly, or estimate additional refits with fixed policy."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    began=time.perf_counter();features=task['features']
    history=grid.iloc[:position][['pm2_5']+features]
    scaler,bounds=fit_input_scaler(history,features,task['clip_inputs'])
    scaled=transform_inputs(history,features,scaler,bounds)
    model=SARIMAX(scaled.pm2_5,exog=scaled[features].ffill() if features else None,
        order=tuple(task['candidate']['order']),seasonal_order=tuple(task['candidate']['seasonal_order']),
        enforce_stationarity=False,enforce_invertibility=False)
    if source is not None:
        folder,reference=source
        if reference['fit_origin']!=str(grid.index[position]):raise ValueError('Restore cutoff differs')
        if features:
            np.testing.assert_allclose(scaler.mean_,[reference['fit']['scaler']['mean'][f] for f in features],rtol=0,atol=1e-10)
            np.testing.assert_allclose(scaler.scale_,[reference['fit']['scaler']['scale'][f] for f in features],rtol=0,atol=1e-10)
        params=np.array([reference['fit']['parameter_estimates'][name] for name in model.param_names])
        fitted=model.filter(params,low_memory=True,cov_type='none')
        meta=reference['fit'].copy();meta['state_reconstruction_seconds']=time.perf_counter()-began
        return Fitted('sarimax',fitted,features,scaler,bounds,position,meta),False,str(folder.relative_to(ROOT))
    reference=json.loads((OUT/'runs/core_sarimax_frozen_s42/metadata.json').read_text())
    if pd.Timestamp(reference['fit_origin'])>grid.index[position]:raise ValueError('Future initialization cutoff')
    initial=[]
    for name in model.param_names:
        value=reference['fit']['parameter_estimates'][name]
        if name in features:value*=scaler.scale_[features.index(name)]/reference['fit']['scaler']['scale'][name]
        initial.append(value)
    initial_llf=float(model.loglike(np.asarray(initial)))
    preparation=time.perf_counter()-began;began=time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        fitted=model.fit(start_params=np.asarray(initial),method='minimize',min_method='L-BFGS-B',
            maxiter=200,maxls=100,optim_score='approx',optim_complex_step=True,disp=False,low_memory=True,cov_type='none')
    meta=dict(family='sarimax',candidate=task['candidate'],features=features,clip_inputs=task['clip_inputs'],seed=task['seed'],
        fit_end_exclusive=str(grid.index[position]),training_calendar_hours=position,
        observed_training_targets=int(history.pm2_5.notna().sum()),target_imputed=False,target_clipped=False,
        scaler={'mean':dict(zip(features,map(float,scaler.mean_))),'scale':dict(zip(features,map(float,scaler.scale_)))},
        input_clip_bounds=None,device='cpu',cpu_threads=2,preparation_seconds=preparation,
        fit_seconds=time.perf_counter()-began,
        parameter_estimates=dict(zip(fitted.param_names,map(float,fitted.params))),
        optimizer=dict(converged=bool(fitted.mle_retvals.get('converged')),iterations=int(fitted.mle_retvals.get('iterations',0)),
            initial_log_likelihood=initial_llf,final_log_likelihood=float(fitted.llf),
            initialization_source='corrected_core_sarimax_frozen_s42',initialization_source_cutoff=reference['fit_origin'],
            method='complex-step L-BFGS-B, maxiter200/maxls100, default tolerances',warnings=[str(w.message) for w in caught[-6:]]))
    if not meta['optimizer']['converged'] or not np.isfinite(fitted.params).all() or not np.isfinite(fitted.llf):
        raise RuntimeError('Additional SARIMAX refit did not converge')
    if fitted.llf<initial_llf-1e-5:raise RuntimeError('Refit reduced training likelihood')
    return Fitted('sarimax',fitted,features,scaler,bounds,position,meta),True,None


def execute(task):
    folder=OUT/'runs'/task['id'];folder.mkdir(parents=True,exist_ok=True)
    _,grid=load_calendar();table=windows(grid);table=table[table.full_week]
    selected=table[table.window==task['week']] if task['regime']=='walk' else table
    position=int(selected.iloc[0].position);source=strict_source(task)
    meta=dict(task=task,status='running',protocol_signature=signature(),strict_protocol_signature=strict_signature(),
        fit_origin=str(grid.index[position]),started_utc=pd.Timestamp.now(tz='UTC').isoformat())
    mp=folder/'metadata.json';mp.write_text(json.dumps(meta,indent=2))
    try:
        if task['regime']=='walk' and source is not None:
            src,old=source;frame=pd.read_csv(src/'forecasts.csv',parse_dates=['target_timestamp'])
            frame=frame[frame.window==1].sort_values('lead_hour')
            if len(frame)!=168 or frame.target_timestamp.min()!=pd.Timestamp(meta['fit_origin']):
                raise ValueError('First-origin reuse source is not the identical corrected week')
            diag=dict(history_target_filled_hours=0,history_input_filled_cells=0,
                future_placeholder_cells=0,scored_hours=168,placeholder_invariance_passed=True,
                placeholder_max_scored_prediction_difference=0.,forecast_seconds=0.,invariance_check_seconds=0.,
                reused_strict_forecast=True)
            row=selected.iloc[0];scores=np.ones(168,dtype=bool)
            combined=rows(task,grid,row,frame.base_prediction.to_numpy(),scores,diag)
            meta.update(fit=old['fit'],fit_executed=False,reused_from=str(src.relative_to(ROOT)),
                        original_source_metadata_sha256=hashlib.sha256((src/'metadata.json').read_bytes()).hexdigest(),
                        completed_weeks=[dict(window=int(row.window),**diag)])
        else:
            if task['family']=='sarimax' and task['regime']=='frozen' and task['variant']=='selected':
                fitted=fit_model(grid,position,task['family'],task['candidate'],task['features'],
                                 task['clip_inputs'],task['seed'],folder)
                fit_executed=True;restored=None
            elif task['family']=='sarimax':fitted,fit_executed,restored=sarimax_model(grid,position,task,source)
            else:
                fitted=fit_model(grid,position,task['family'],task['candidate'],task['features'],task['clip_inputs'],task['seed'],folder)
                fit_executed=True;restored=None
            meta.update(fit=fitted.metadata,fit_executed=fit_executed,restored_parameters_from=restored)
            if task['family']=='sarimax' and not fitted.metadata['optimizer']['converged']:
                raise RuntimeError('Corrected SARIMAX fit did not converge under the fixed numerical policy')
            if source is not None:
                meta.update(strict_reference=str(source[0].relative_to(ROOT)),
                    strict_reference_metadata_sha256=hashlib.sha256((source[0]/'metadata.json').read_bytes()).hexdigest())
            parts=[];previous=position;week_meta=[];maximum_reproduction_difference=0.
            strict_forecasts=pd.read_csv(source[0]/'forecasts.csv') if source is not None else None
            for row in selected.itertuples():
                p=int(row.position);state_seconds=0.
                if task['family']=='sarimax' and p>previous:
                    state_seconds=advance_frozen_sarimax(fitted,grid,previous,p);previous=p
                prediction,score,diag,components=forecast(fitted,grid,p)
                diag['state_update_seconds']=state_seconds
                if strict_forecasts is not None:
                    original=strict_forecasts[strict_forecasts.window==int(row.window)]
                    if not original.empty:
                        np.testing.assert_allclose(prediction,original.base_prediction.to_numpy(),
                                                   **policy()['strict_forecast_reproduction_tolerance'])
                        difference=float(np.max(np.abs(prediction-original.base_prediction.to_numpy())))
                        maximum_reproduction_difference=max(maximum_reproduction_difference,difference)
                        diag['strict_reproduction_max_difference']=difference
                frame=rows(task,grid,row,prediction,score,diag);parts.append(frame)
                frame.to_csv(folder/f'week_{int(row.window):02d}.csv',index=False)
                if components is not None:components.to_csv(folder/f'components_w{int(row.window):02d}.csv',index=False)
                week_meta.append(dict(window=int(row.window),**diag))
                meta.update(completed_weeks=week_meta,strict_reproduction_max_difference=maximum_reproduction_difference)
                mp.write_text(json.dumps(meta,indent=2))
                print(task['id'],'week',row.window,'scored',diag['scored_hours'],flush=True)
            combined=pd.concat(parts,ignore_index=True)
        combined.to_csv(folder/'forecasts.csv',index=False)
        meta.update(status='completed',completed_utc=pd.Timestamp.now(tz='UTC').isoformat(),**metrics(combined),
                    sampled_self_peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
        mp.write_text(json.dumps(meta,indent=2))
    except Exception:
        meta.update(status='failed',error=traceback.format_exc());mp.write_text(json.dumps(meta,indent=2));raise


def supervise(only=None):
    audit()
    for task in tasks():
        if only and task['id'] not in only:continue
        folder=OUT/'runs'/task['id'];mp=folder/'metadata.json';csv=folder/'forecasts.csv'
        if mp.exists() and csv.exists():
            old=json.loads(mp.read_text())
            if old['status']=='completed' and old['protocol_signature']==signature():continue
        folder.mkdir(parents=True,exist_ok=True);env=os.environ.copy()
        for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','TF_NUM_INTRAOP_THREADS','TF_NUM_INTEROP_THREADS']:env[key]='2'
        env.update(MPLCONFIGDIR='/tmp/weather-revision-matplotlib',CUDA_VISIBLE_DEVICES='',TF_CPP_MIN_LOG_LEVEL='3')
        started=time.perf_counter();peak=0;guard=None;limit=min(6*1024**3,int(psutil.virtual_memory().available*.75))
        print('START',task['id'],flush=True)
        with (folder/'run.log').open('w') as log:
            proc=subprocess.Popen([sys.executable,'-u','-m','revision.corrected.code.coverage_runner','child',json.dumps(task)],
                cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            while proc.poll() is None:
                try:
                    root=psutil.Process(proc.pid);rss=sum(p.memory_info().rss for p in [root]+root.children(recursive=True) if p.is_running());peak=max(peak,rss)
                    if rss>limit:guard='memory_guard'
                    elif time.perf_counter()-started>5400:guard='90_minute_guard'
                    if guard:
                        for child in root.children(recursive=True):child.terminate()
                        proc.terminate()
                        try:proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:proc.kill()
                except psutil.NoSuchProcess:pass
                time.sleep(.5)
        measurement=dict(task_id=task['id'],returncode=proc.returncode,elapsed_seconds=time.perf_counter()-started,
                         sampled_peak_rss_mib=peak/1024**2,guard_reason=guard)
        with (OUT/'supervisor.jsonl').open('a') as log:log.write(json.dumps(measurement)+'\n')
        print('END',json.dumps(measurement),flush=True)
        if not mp.exists():
            raise RuntimeError(f'Worker did not write to corrected workspace: {task["id"]}')
        actual=json.loads(mp.read_text())
        if actual.get('protocol_signature')!=signature() or actual.get('task')!=task:
            raise RuntimeError(f'Worker wrote incompatible corrected task: {task["id"]}')


def baselines_and_corrections():
    _,grid=load_calendar();table=windows(grid);cfg=configuration()
    folder=OUT/'baselines';folder.mkdir(parents=True,exist_ok=True)
    for name,cycle in [('persistence',1),('daily_persistence',24),('weekly_persistence',168)]:
        parts=[]
        for row in table[table.full_week].itertuples():
            p=int(row.position);history=seasonal_past_fill(grid.iloc[:p][['pm2_5']])
            values=(latest_observed_persistence(grid.iloc[:p][['pm2_5']]) if cycle==1
                    else np.resize(history.pm2_5.iloc[-cycle:].to_numpy(),168))
            mask=grid.iloc[p:p+168][['pm2_5']+cfg['broad_features']].notna().all(axis=1).to_numpy()
            task=dict(id=name,family=name,regime='baseline',seed=0)
            diag=dict(history_target_filled_hours=int(grid.iloc[p-cycle:p].pm2_5.isna().sum()),history_input_filled_cells=0)
            parts.append(rows(task,grid,row,values,mask,diag))
        pd.concat(parts,ignore_index=True).to_csv(folder/f'{name}.csv',index=False)
    folder=OUT/'corrections';folder.mkdir(parents=True,exist_ok=True);summaries=[]
    for task in tasks():
        if task['stage']!='core' or task['regime']!='frozen':continue
        source=OUT/'runs'/task['id'];meta=json.loads((source/'metadata.json').read_text())
        if meta['status']!='completed' or meta['protocol_signature']!=signature():raise ValueError('Incomplete frozen stream')
        base=pd.read_csv(source/'forecasts.csv')
        for alpha in [0.]+cfg['ewma_alpha_sensitivity']:
            bias=0.;parts=[]
            for _,week in base.groupby('window',sort=True):
                piece=week.copy();piece['applied_bias']=bias;piece['corrected_prediction']=piece.base_prediction+bias
                piece['alpha']=alpha;parts.append(piece)
                observed=week[week.score_eligible]
                if alpha:bias=alpha*float((observed.original_target-observed.base_prediction).mean())+(1-alpha)*bias
            frame=pd.concat(parts,ignore_index=True);frame.to_csv(folder/f"{task['id']}_alpha_{str(alpha).replace('.','p')}.csv",index=False)
            summaries.append(dict(run_id=task['id'],alpha=alpha,**metrics(frame,'corrected_prediction')))
    pd.DataFrame(summaries).to_csv(folder/'summary.csv',index=False)


def verify_and_report():
    _,grid=load_calendar();table=windows(grid);expected=table[table.full_week];errors=[];pending=[];records=[]
    for task in tasks():
        folder=OUT/'runs'/task['id'];mp=folder/'metadata.json';csv=folder/'forecasts.csv'
        if not mp.exists():pending.append(task['id']);continue
        meta=json.loads(mp.read_text())
        if meta['status']!='completed':pending.append(task['id']);continue
        if meta['protocol_signature']!=signature():errors.append(task['id']+': signature differs')
        frame=pd.read_csv(csv,parse_dates=['forecast_origin','target_timestamp'])
        exp=expected[expected.window==task['week']] if task['regime']=='walk' else expected
        expected_rows=pd.DataFrame([dict(window=int(r.window),forecast_origin=pd.Timestamp(r.origin),lead_hour=i) for r in exp.itertuples() for i in range(1,169)])
        columns=['window','forecast_origin','lead_hour']
        pd.testing.assert_frame_equal(frame[columns].sort_values(columns).reset_index(drop=True),expected_rows.sort_values(columns).reset_index(drop=True))
        if frame[['forecast_origin','target_timestamp']].duplicated().any():errors.append(task['id']+': duplicate timestamp')
        np.testing.assert_array_equal(frame.target_timestamp-frame.forecast_origin,pd.to_timedelta(frame.lead_hour-1,unit='h'))
        raw=grid.loc[frame.target_timestamp];mask=raw[['pm2_5']+configuration()['broad_features']].notna().all(axis=1).to_numpy()
        np.testing.assert_array_equal(frame.score_eligible,mask)
        np.testing.assert_allclose(frame.original_target,raw.pm2_5.to_numpy(),rtol=0,atol=0,equal_nan=True)
        if not np.isfinite(frame.loc[frame.score_eligible,'base_prediction']).all():errors.append(task['id']+': nonfinite scored forecast')
        if meta['fit_origin']!=str(frame.forecast_origin.min()):errors.append(task['id']+': training cutoff differs')
        if task['family']=='sarimax' and not meta['fit']['optimizer']['converged']:errors.append(task['id']+': unconverged fit')
        if task['family']=='neuralprophet' and meta['fit']['epochs_completed']!=50:errors.append(task['id']+': epochs differ')
        for week in meta['completed_weeks']:
            if not week['placeholder_invariance_passed']:errors.append(task['id']+': failed placeholder invariance')
        if meta.get('reused_from'):
            original=pd.read_csv(ROOT/meta['reused_from']/'forecasts.csv')
            original=original[original.window.isin(frame.window)].sort_values(['window','lead_hour'])
            np.testing.assert_allclose(frame.base_prediction,original.base_prediction,rtol=0,atol=1e-10)
            digest=hashlib.sha256((ROOT/meta['reused_from']/'metadata.json').read_bytes()).hexdigest()
            if digest!=meta['original_source_metadata_sha256']:errors.append(task['id']+': reused source changed')
        if meta.get('strict_reference'):
            original=pd.read_csv(ROOT/meta['strict_reference']/'forecasts.csv')
            current=frame[frame.window.isin(original.window)].sort_values(['window','lead_hour'])
            np.testing.assert_allclose(current.base_prediction,original.base_prediction,**policy()['strict_forecast_reproduction_tolerance'])
        records.append(dict(run_id=task['id'],family=task['family'],regime=task['regime'],variant=task['variant'],seed=task['seed'],
                            fit_executed=meta['fit_executed'],**metrics(frame)))
    baselines=list((OUT/'baselines').glob('*.csv'));corrections=list((OUT/'corrections').glob('*_alpha_*.csv'))
    if len(baselines)!=3:errors.append('Three baselines required')
    if len(corrections)!=35:errors.append('35 correction streams required')
    for file in corrections:
        frame=pd.read_csv(file);alpha=float(frame.alpha.iloc[0]);bias=0.
        source=pd.read_csv(OUT/'runs'/file.name.split('_alpha_')[0]/'forecasts.csv')
        for col in ['original_target','base_prediction','score_eligible','window']:
            np.testing.assert_allclose(frame[col],source[col],rtol=0,atol=1e-10,equal_nan=True)
        for _,week in frame.groupby('window',sort=True):
            np.testing.assert_allclose(week.applied_bias,bias,rtol=0,atol=1e-10)
            np.testing.assert_allclose(week.corrected_prediction,week.base_prediction+bias,rtol=0,atol=1e-10,equal_nan=True)
            observed=week[week.score_eligible]
            if alpha:bias=alpha*(observed.original_target-observed.base_prediction).mean()+(1-alpha)*bias
    info=dict(protocol_signature=signature(),expected_tasks=len(tasks()),complete_tasks=len(records),pending_tasks=pending,
        integrity_errors=errors,ready=not pending and not errors,scheduled_weeks=23,scheduled_hours=3864,
        observed_scoring_hours=3624,full_observed_weeks=19,partially_observed_weeks=4,
        original_files_verified=len(json.loads((REVISION/'artifacts/phase1/original_manifest.json').read_text())['files']))
    (OUT/'verification.json').write_text(json.dumps(info,indent=2))
    if not records:print(json.dumps(info));return
    summary=[]
    for keys,group in pd.DataFrame(records).groupby(['family','regime','variant','seed']):
        frames=[pd.read_csv(OUT/'runs'/r.run_id/'forecasts.csv') for r in group.itertuples()]
        pooled=pd.concat(frames,ignore_index=True)
        if pooled[['forecast_origin','target_timestamp']].duplicated().any():raise ValueError('Duplicate pooled forecast')
        strict_subset=pooled[pooled.window.isin(table.loc[table.strict_eligible,'window'])]
        summary.append(dict(family=keys[0],regime=keys[1],variant=keys[2],seed=keys[3],
                            **metrics(pooled),strict_subset_pooled_mae=metrics(strict_subset)['pooled_mae'] if len(strict_subset) else np.nan))
    summary=pd.DataFrame(summary);summary.to_csv(OUT/'experimental_summary.csv',index=False)
    baseline=pd.DataFrame([dict(run=f.stem,**metrics(pd.read_csv(f))) for f in baselines]);baseline.to_csv(OUT/'baseline_summary.csv',index=False)
    lines=['# Broader coverage reconsideration results','',f"Verified ready: **{info['ready']}**; accepted tasks: {len(records)}/{len(tasks())}.",
        '', 'The schedule retains 23 full calendar weeks / 3,864 hours. The shared observed-only mask scores 3,624 hours: 19 complete weeks and four partially observed weeks. The final 163-hour remainder is reported separately and not included.',
        '', 'Four invalid training pollutant input cells are treated as missing in the corrected working calendar. The chronological split, seed design, and target missingness policies are unchanged. Dense historical inference context uses causal weekly seasonal filling only where observations are absent; filling counts are recorded. Training and scoring targets are never filled.',
        '', 'Unavailable future-input hours are not scored and their predictions are masked. Each affected fitted-model/origin passes a perturbation check proving its scored predictions are unchanged by computational placeholders at unavailable-input timestamps. This guarantee is implementation-specific, not a general property of other models.',
        '', '## Core descriptive results','',markdown_table(summary[summary.variant=='selected'].round(4)),
        '', 'Pooled MAE weights observed hours equally; mean weekly MAE weights weeks equally and differs when coverage varies. Report both, weekly SD and coverage. No full-week accuracy claim is supported by a partially scored week.',
        '', '## Frozen controls','',markdown_table(summary[(summary.regime=='frozen') & (summary.seed==42)].round(4)),
        '', '## Baselines','',markdown_table(baseline.round(4)),
        '', '## Limitations and continuity','',
        'The original raw data and notebook are preserved. This retains the 23-week calendar schedule and supports a corrected 16-week sensitivity; it does not recreate irregular row chunks in the old notebook. Only the identical first-origin corrected frozen fit/forecast is reused for the corresponding weekly-refit task. Historical filling is a substantive inference assumption, particularly for 120 missing context hours. Fixed-rule reconstruction errors on training-only masked histories are saved without using test performance to choose a fill method.',
        '', 'The broader correction streams update on observed-hour residual means after each of the 23 weeks. The strict sensitivity keeps its original skip/carry policy. On the 16-week subset, correction values can therefore differ between policies even when base forecasts agree; disclose this rather than claiming identical correction experiments.',
        '', 'New fits and first-origin source reuse are identified in run metadata. Resource accounting must distinguish the source forecast cost from the overhead of reuse.',
        '', 'Phase 3 remains pending. Statistical comparisons, residual/lead-time diagnostics and figures will use this documented corrected-input protocol.']
    (REVISION/'reports/COVERAGE_RECONSIDERATION_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(info,indent=2))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['audit','run','child','finish','verify']);parser.add_argument('task',nargs='?');parser.add_argument('--only',nargs='*');args=parser.parse_args()
    if args.stage=='audit':audit()
    elif args.stage=='run':supervise(args.only)
    elif args.stage=='child':execute(json.loads(args.task))
    elif args.stage=='finish':baselines_and_corrections();verify_and_report()
    else:verify_and_report()


if __name__=='__main__':main()
