"""Reuse the identical initial fit/forecast shared by both core regimes.

At the first test origin, data, settings, seed and preprocessing are identical.
Later walk-forward origins must still fit independently. Reused measurements
are marked explicitly so resource analysis does not count them as extra fits.
"""
import json
from copy import deepcopy
import pandas as pd
from .phase2_runner import OUT, load_tasks, paths, signature


def main():
    sources={t['family']+str(t['seed']):t for t in load_tasks('core') if t['regime']=='frozen'}
    for task in load_tasks('core'):
        if task['regime']!='walk' or task['week']!=1:continue
        source=sources[task['family']+str(task['seed'])]
        source_folder,source_meta,source_csv=paths(source)
        if not source_meta.exists() or not source_csv.exists():continue
        original=json.loads(source_meta.read_text())
        if original.get('status')!='completed' or original['protocol_signature']!=signature():continue
        folder,meta,csv=paths(task)
        if meta.exists():
            existing=json.loads(meta.read_text())
            if existing.get('status')=='running':continue
            if existing.get('status')=='completed' and existing.get('protocol_signature')==signature():continue
        values=pd.read_csv(source_csv)
        values=values[values.window==1].copy()
        if len(values)!=168:raise ValueError('Initial shared forecast must have 168 hours')
        if values.forecast_origin.nunique()!=1 or values.forecast_origin.iloc[0]!=original['fit_origin']:
            raise ValueError('Only the forecast at the identical fit origin may be reused')
        values['run_id']=task['id'];values['regime']='walk'
        folder.mkdir(parents=True,exist_ok=True)
        values.to_csv(csv,index=False);values.to_csv(folder/'week_01.csv',index=False)
        record=deepcopy(original)
        record['task']=task
        record['reused_from_run']=source['id']
        record['fit_executed_for_this_task']=False
        record['reuse_reason']='Identical first test origin, complete training history, candidate settings, features, preprocessing and seed across the two regimes'
        record['completed_weeks']=original['completed_weeks'][:1]
        record['scored_hours']=168
        record['mean_weekly_mae']=record['completed_weeks'][0]['mae']
        record['pooled_rmse']=record['completed_weeks'][0]['rmse']
        meta.write_text(json.dumps(record,indent=2))
        component=source_folder/'components_w01.csv'
        if component.exists():(folder/'components_w01.csv').write_bytes(component.read_bytes())
        print('Reused identical initial fit/forecast:',source['id'],'->',task['id'],flush=True)


if __name__=='__main__':main()
