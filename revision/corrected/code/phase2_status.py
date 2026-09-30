"""Read-only progress and coverage report for the long Phase 2 run."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .protocol import REVISION, configuration, load_calendar
from .phase2_runner import OUT, CANDIDATES, FAMILIES, load_tasks, signature


def markdown_table(frame):
    frame=frame.fillna('')
    columns=list(frame.columns)
    lines=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    for row in frame.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(str(value).replace('|','\\|') for value in row)+' |')
    return '\n'.join(lines)


def baseline_table():
    records=[]
    for file in sorted((OUT/'baselines').glob('*.csv')):
        frame=pd.read_csv(file)
        weekly=frame.groupby('window').apply(lambda w:float(np.mean(np.abs(w.original_target-w.base_prediction))),include_groups=False)
        records.append(dict(run=file.stem,windows=weekly.size,hours=len(frame),
                            mean_weekly_mae=weekly.mean(),weekly_mae_sd=weekly.std(ddof=1),
                            pooled_rmse=np.sqrt(np.mean((frame.original_target-frame.base_prediction)**2))))
    return pd.DataFrame(records)


def check_saved_stream(file, task, grid):
    frame=pd.read_csv(file,parse_dates=['forecast_origin','target_timestamp'])
    expected=672 if task['stage']=='validate' else (168 if task['regime']=='walk' else 2688)
    if len(frame)!=expected:
        return f'Expected {expected} rows, found {len(frame)}'
    if frame[['forecast_origin','target_timestamp']].duplicated().any():
        return 'Duplicate forecast/target timestamp'
    if not (frame.target_timestamp-frame.forecast_origin==pd.to_timedelta(frame.lead_hour-1,unit='h')).all():
        return 'Lead-time alignment failed'
    if not np.isfinite(frame.base_prediction).all():
        return 'Nonfinite base prediction'
    windows=pd.read_csv(REVISION/'artifacts/phase1'/
                        ('validation_windows.csv' if task['stage']=='validate' else 'test_windows.csv'))
    windows=windows[windows.eligible]
    if task['regime']=='walk':windows=windows[windows.window==task['week']]
    expected_pairs=pd.DataFrame([
        dict(window=int(row.window),forecast_origin=pd.Timestamp(row.origin),lead_hour=lead)
        for row in windows.itertuples() for lead in range(1,169)])
    columns=['window','forecast_origin','lead_hour']
    actual=frame[columns].sort_values(columns).reset_index(drop=True)
    expected_pairs=expected_pairs.sort_values(columns).reset_index(drop=True)
    if not actual.equals(expected_pairs):
        return 'Forecast windows or lead hours differ from locked eligibility'
    if not frame.observed.eq(True).all() or not frame.eligible.eq(True).all():
        return 'Scored observation or eligibility mask is false'
    try:
        np.testing.assert_array_equal(frame.original_target.to_numpy(),grid.loc[frame.target_timestamp,'pm2_5'].to_numpy())
    except (AssertionError,KeyError):
        return 'Original target differs from raw calendar'
    return ''


def run_table():
    _,grid=load_calendar()
    records=[]
    for file in sorted((OUT/'runs').glob('*/metadata.json')):
        info=json.loads(file.read_text());task=info['task']
        forecasts=file.parent/'forecasts.csv'
        stream_error=check_saved_stream(forecasts,task,grid) if forecasts.exists() else 'No complete forecast file'
        current=info.get('protocol_signature')==signature()
        status=info.get('status')
        if status=='completed' and not current:status='stale_signature'
        elif status=='completed' and stream_error:status='invalid_stream'
        records.append(dict(run_id=task['id'],stage=task['stage'],family=task['family'],
                            regime=task['regime'],variant=task.get('variant','selected'),
                            status=status,signature_match=current,
                            complete_forecasts=forecasts.exists() and not stream_error,
                            stream_error=stream_error,scored_hours=info.get('scored_hours',0),
                            mean_weekly_mae=info.get('mean_weekly_mae'),pooled_rmse=info.get('pooled_rmse'),
                            error=(info.get('error') or '').splitlines()[-1] if info.get('error') else ''))
    return pd.DataFrame(records)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    baselines=baseline_table();runs=run_table()
    if not baselines.empty:baselines.to_csv(OUT/'baseline_summary.csv',index=False)
    if not runs.empty:runs.to_csv(OUT/'run_status.csv',index=False)
    lines=['# Phase 2 progress','',
           'The trained-model matrix is computationally long and runs sequentially. This file reports observed state, not promised results.','',
           '## Baselines','']
    lines.append(markdown_table(baselines.round(3)) if not baselines.empty else 'Pending.')
    lines.extend(['','## Trained runs',''])
    if not runs.empty:
        grouped=runs.groupby(['stage','status']).size().reset_index(name='count')
        lines.append(markdown_table(grouped))
        failed=runs[runs.status=='failed']
        if not failed.empty:
            lines.extend(['','### Failures','',markdown_table(failed[['run_id','error']])])
    else:lines.append('No completed trained-model runs yet.')
    if (OUT/'selection.json').exists():
        selected=json.loads((OUT/'selection.json').read_text())
        lines.extend(['','## Training-only selected settings','',
                      '```json',json.dumps(selected['selected'],indent=2),'```'])
        expected=load_tasks('core')+load_tasks('ablate')
        complete_ids=set(runs.loc[(runs.status=='completed') & runs.complete_forecasts,'run_id']) if not runs.empty else set()
        finished=sum(t['id'] in complete_ids for t in expected)
        lines.extend(['',f'Complete original-policy core/ablation tasks: {finished} of {len(expected)}. Shared initial forecasts are included and explicitly marked as reused in metadata.'])
        verification_file=OUT/'verification.json'
        if verification_file.exists():
            verified=json.loads(verification_file.read_text())
            if verified.get('protocol_signature')==signature():
                lines.extend(['','## Verified coverage including numerical recoveries','',
                              f"Verified tasks: {verified['complete_tasks']}/{len(expected)}; accepted recoveries: {verified['recovered_tasks']}; unresolved failures: {verified['unresolved_failed_tasks']}; integrity errors: {len(verified['integrity_errors'])}.",
                              '', 'Original failures above remain in the audit trail. `verified_coverage.csv` maps each task to its accepted original or recovery forecast. This section reflects the latest verifier run; rerun verification after additional fitting.'])
    correction_file=OUT/'corrections/summary.csv'
    if correction_file.exists():
        correction=pd.read_csv(correction_file)
        lines.extend(['','## Frozen correction replay','',
                      f'Saved correction streams: {len(correction)} (no correction plus six predefined alpha settings per complete frozen run).',
                      '',markdown_table(correction[correction.alpha==configuration()['ewma_alpha']].round(4)),
                      '', 'These are point estimates at the predefined alpha. Paired uncertainty and interpretation belong to Phase 3; no test-optimal alpha is selected.'])
    lines.extend(['','Complete comparison requires the selected validation settings, all eligible core runs, and all planned ablations. Results may change from the submitted paper.'])
    (REVISION/'reports/PHASE2_PROGRESS.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__=='__main__':main()
