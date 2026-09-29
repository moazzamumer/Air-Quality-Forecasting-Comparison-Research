"""Verify saved Phase 2 evidence; never infer completion from a process exit alone."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .protocol import REVISION, load_calendar, original_path, configuration
from .phase2_runner import OUT, load_tasks, paths, signature
from .phase2_status import check_saved_stream, markdown_table


def main():
    cfg=configuration();_,grid=load_calendar();errors=[];exceptions=[];records=[]
    selected=json.loads((OUT/'selection.json').read_text())
    if selected['protocol_signature']!=signature():errors.append('Selection signature does not match')
    validation_candidates={family:[] for family in selected['selected']}
    validation_completed=0;validation_failures=[]
    for task in load_tasks('validate'):
        _,meta,csv=paths(task)
        if not meta.exists():errors.append(task['id']+': missing validation attempt');continue
        record=json.loads(meta.read_text())
        if record.get('protocol_signature')!=signature():errors.append(task['id']+': stale validation signature')
        if record.get('status')=='failed':validation_failures.append(task['id']);continue
        if record.get('status')!='completed' or not csv.exists():
            errors.append(task['id']+': incomplete validation');continue
        issue=check_saved_stream(csv,task,grid)
        if issue:errors.append(task['id']+': '+issue)
        frame=pd.read_csv(csv,parse_dates=['forecast_origin','target_timestamp'])
        test_start=pd.Timestamp(pd.read_csv(REVISION/'artifacts/phase1/test_windows.csv').iloc[0].origin)
        if frame.target_timestamp.max()>=test_start or pd.Timestamp(record['fit_origin'])!=frame.forecast_origin.min():
            errors.append(task['id']+': validation boundary differs')
        if task['family']=='sarimax' and not record['fit']['optimizer']['converged']:
            errors.append(task['id']+': scored unconverged validation')
        weekly=frame.groupby('window').apply(lambda w:np.mean(np.abs(w.original_target-w.base_prediction)),include_groups=False)
        mae=float(weekly.mean());rmse=float(np.sqrt(np.mean((frame.original_target-frame.base_prediction)**2)))
        np.testing.assert_allclose([mae,rmse],[record['mean_weekly_mae'],record['pooled_rmse']],rtol=0,atol=1e-9)
        validation_candidates[task['family']].append((mae,rmse,task['id'],task['candidate']))
        validation_completed+=1
    for family,candidates in validation_candidates.items():
        if not candidates or sorted(candidates)[0][3]!=selected['selected'][family]:
            errors.append(family+': selected setting differs from training-only validation')
    tasks=load_tasks('core')+load_tasks('ablate')
    pending=[]
    for task in tasks:
        folder,meta,csv=paths(task)
        if not meta.exists():pending.append(task['id']);continue
        record=json.loads(meta.read_text())
        status=record.get('status')
        if status not in ['completed','failed']:pending.append(task['id']);continue
        if record.get('protocol_signature')!=signature():
            errors.append(task['id']+': stale signature');continue
        recovered=False
        if status=='failed':
            exception=dict(run_id=task['id'],family=task['family'],regime=task['regime'],
                variant=task.get('variant','selected'),seed=task['seed'],week=task.get('week'),
                reason=record.get('error','Missing failure reason').splitlines()[-1],resolved=False)
            exceptions.append(exception)
            recovery_folder=OUT/'runs'/('recover_'+task['id'])
            recovery_meta=recovery_folder/'metadata.json'
            if not recovery_meta.exists():continue
            recovery=json.loads(recovery_meta.read_text())
            if recovery.get('status')!='completed':continue
            if recovery.get('protocol_signature')!=signature():
                errors.append(task['id']+': recovery signature differs');continue
            for key in ['family','regime','candidate','features','clip_inputs','seed']:
                if recovery['task'][key]!=task[key]:errors.append(task['id']+': recovery changed '+key)
            if recovery.get('recovered_from_failed_run')!=task['id']:
                errors.append(task['id']+': recovery provenance differs')
            if recovery.get('fit_origin')!=record['fit_origin']:
                errors.append(task['id']+': recovery training cutoff differs')
            optimizer=recovery['fit']['optimizer']
            if pd.Timestamp(recovery['initialization_source_cutoff'])>pd.Timestamp(record['fit_origin']):
                errors.append(task['id']+': recovery initialization used later history')
            if not np.isfinite([optimizer['final_log_likelihood'],optimizer['initial_log_likelihood']]).all():
                errors.append(task['id']+': recovery likelihood is nonfinite')
            if optimizer['final_log_likelihood']<optimizer['initial_log_likelihood']-1e-5:
                errors.append(task['id']+': recovery reduced training likelihood')
            policy_path=REVISION/'config/sarimax_numerical_recovery.json'
            code_path=REVISION/'code/phase2_recover.py'
            if recovery['numerical_policy_sha256']!=hashlib.sha256(policy_path.read_bytes()).hexdigest():
                errors.append(task['id']+': recovery policy checksum differs')
            if recovery['recovery_code_sha256']!=hashlib.sha256(code_path.read_bytes()).hexdigest():
                errors.append(task['id']+': recovery code checksum differs')
            record=recovery;folder=recovery_folder;csv=folder/'forecasts.csv';recovered=True
            exception.update(resolved=True,recovery_run=recovery['task']['id'])
        if not csv.exists():errors.append(task['id']+': no forecast CSV');continue
        issue=check_saved_stream(csv,task,grid)
        if issue:errors.append(task['id']+': '+issue)
        if task['family']=='sarimax' and not record.get('fit',{}).get('optimizer',{}).get('converged'):
            errors.append(task['id']+': scored nonconverged SARIMAX')
        if task['family']=='neuralprophet':
            if record.get('fit',{}).get('epochs_completed')!=task['candidate']['epochs']:
                errors.append(task['id']+': epoch count differs from configuration')
        if record.get('reused_from_run'):
            source=pd.read_csv(OUT/'runs'/record['reused_from_run']/'forecasts.csv')
            reused=pd.read_csv(csv)
            source=source[source.window==1]
            for column in ['forecast_origin','target_timestamp','lead_hour','original_target','base_prediction']:
                if column=='base_prediction':
                    # CSV round trips may change the final floating-point bit.
                    np.testing.assert_allclose(source[column].to_numpy(),reused[column].to_numpy(),rtol=0,atol=1e-10)
                else:
                    np.testing.assert_array_equal(source[column].to_numpy(),reused[column].to_numpy())
            if task.get('week')!=1:errors.append(task['id']+': reused a later refit')
        frame=pd.read_csv(csv)
        records.append(dict(run_id=task['id'],evidence_run_id=record['task']['id'],family=task['family'],regime=task['regime'],
                            variant=task.get('variant','selected'),seed=task['seed'],
                            windows=frame.window.nunique(),hours=len(frame),
                            reused_initial_fit=bool(record.get('reused_from_run')),
                            numerical_recovery=recovered,recovered_windows=frame.window.nunique() if recovered else 0))
    baseline_files=list((OUT/'baselines').glob('*.csv'))
    if {p.stem for p in baseline_files}!={'persistence','daily_persistence','weekly_persistence'}:
        errors.append('Expected the three specified baseline files')
    for file in baseline_files:
        dummy=dict(stage='core',regime='frozen')
        issue=check_saved_stream(file,dummy,grid)
        if issue:errors.append(file.name+': '+issue)
    correction_files=list((OUT/'corrections').glob('*_alpha_*.csv'))
    if len(correction_files)!=35:errors.append(f'Expected 35 correction streams, found {len(correction_files)}')
    for file in correction_files:
        frame=pd.read_csv(file);alpha=float(frame.alpha.iloc[0]);bias=0.
        issue=check_saved_stream(file,dict(stage='core',regime='frozen'),grid)
        if issue:errors.append(file.name+': '+issue)
        if not frame.alpha.eq(alpha).all() or alpha not in [0.,.1,.2,.3,.5,.7,1.]:
            errors.append(file.name+': correction alpha differs from predefined grid')
        source_id=file.name.split('_alpha_')[0]
        source=pd.read_csv(OUT/'runs'/source_id/'forecasts.csv')
        for column in ['window','forecast_origin','target_timestamp','lead_hour','original_target','base_prediction']:
            if column=='base_prediction':
                np.testing.assert_allclose(frame[column],source[column],rtol=0,atol=1e-10)
            else:np.testing.assert_array_equal(frame[column],source[column])
        if len(frame)!=2688:errors.append(file.name+': incomplete correction stream')
        for _,week in frame.groupby('window',sort=True):
            np.testing.assert_allclose(week.applied_bias,bias,rtol=0,atol=1e-10)
            np.testing.assert_allclose(week.corrected_prediction,week.base_prediction+bias,rtol=0,atol=1e-10)
            if alpha!=0:bias=alpha*(week.original_target-week.base_prediction).mean()+(1-alpha)*bias
    manifest=json.loads((REVISION/'artifacts/phase1/original_manifest.json').read_text())['files']
    for name,record in manifest.items():
        if hashlib.sha256(original_path(name).read_bytes()).hexdigest()!=record['sha256']:
            errors.append('Original file changed: '+name)
    info=dict(protocol_signature=signature(),all_tasks_attempted=not pending,
              phase2_exit_evidence_ready=not pending and not errors,
              expected_core_ablation_tasks=len(tasks),complete_tasks=len(records),
              failure_exceptions=exceptions,pending_tasks=pending,integrity_errors=errors,
              recovered_tasks=sum(x['numerical_recovery'] for x in records),
              unresolved_failed_tasks=sum(not x['resolved'] for x in exceptions),
              baselines=len(baseline_files),correction_streams=len(correction_files),
              validation_completed=validation_completed,validation_failures=validation_failures,
              original_files_verified=len(manifest),checked_utc=pd.Timestamp.now(tz='UTC').isoformat())
    (OUT/'verification.json').write_text(json.dumps(info,indent=2))
    completed=pd.DataFrame(records)
    if not completed.empty:completed.to_csv(OUT/'verified_coverage.csv',index=False)
    summary=['# Phase 2 verification','',
             f"Exit evidence ready: **{info['phase2_exit_evidence_ready']}**. Completed tasks: {len(records)}/{len(tasks)}; original failed attempts: {len(exceptions)}; recovered: {info['recovered_tasks']}; unresolved: {info['unresolved_failed_tasks']}; pending: {len(pending)}.",
             '',f'All {len(manifest)} original fingerprinted files checked. Baselines: {len(baseline_files)}. Correction streams: {len(correction_files)}.',
             '', 'Integrity errors: '+(', '.join(errors) if errors else 'none.'),
             '', '## Coverage exceptions','']
    summary.append(markdown_table(pd.DataFrame(exceptions)) if exceptions else 'None recorded.')
    if not completed.empty:
        pooled=completed.groupby(['family','regime','variant','seed'])[['windows','hours','recovered_windows']].sum().reset_index()
        summary.extend(['','## Completed forecast coverage','',markdown_table(pooled)])
    summary.extend(['','Unconverged fits have no scored forecast stream. Valid numerical recoveries are separately identified and retain the selected settings and training cutoff. Phase 3 must compare methods on matching successful windows and report available coverage, recovery effort, and any unresolved failure. A verified completed matrix can still contain explicitly documented failed-fit exceptions.'])
    (REVISION/'reports/PHASE2_VERIFICATION.md').write_text('\n'.join(summary)+'\n')
    print(json.dumps(info,indent=2))


if __name__=='__main__':main()
