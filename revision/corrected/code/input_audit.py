"""Compare the immutable source with the corrected working calendar."""
import hashlib
import json

import numpy as np
import pandas as pd

from .protocol import ROOT, REVISION, configuration, load_calendar, split_position, fit_input_scaler, neural_training_segments
from .coverage_protocol import windows


def main():
    cfg=configuration(); source=ROOT/cfg['source']; raw=pd.read_csv(source)
    raw.index=pd.DatetimeIndex(pd.to_datetime(raw[['year','month','day','hour']]),name='datetime')
    original=raw.sort_index().reindex(pd.date_range(raw.index.min(),raw.index.max(),freq='h',name='datetime'))
    _,corrected=load_calendar();cutoff=split_position(corrected)
    columns=[cfg['target']]+cfg['broad_features']
    changes=[]
    for name in columns:
        before=original[name];after=corrected[name]
        changed=before.notna()&after.isna()
        for timestamp,value in before[changed].items():
            changes.append(dict(timestamp=str(timestamp),input=name,original=float(value),corrected='NaN',
                                partition='training' if timestamp<corrected.index[cutoff] else 'test'))
        np.testing.assert_allclose(before[~changed],after[~changed],rtol=0,atol=0,equal_nan=True)
    assert len(changes)==4 and all(x['partition']=='training' and x['original']==-9999 for x in changes)
    assert original[cfg['target']].equals(corrected[cfg['target']])
    scale=[];samples=[]
    boundaries=[('validation',int(pd.read_csv(REVISION/'artifacts/phase1/validation_windows.csv').position.iloc[0])),
                ('initial_test',cutoff)]
    for label,end in boundaries:
        for group,features in [('selected',cfg['selected_features']),('broad',cfg['broad_features']),('no_inputs',[])]:
            old=original.iloc[:end];new=corrected.iloc[:end]
            if features:
                old_scaler,_=fit_input_scaler(old,features)
                new_scaler,_=fit_input_scaler(new,features)
                for i,name in enumerate(features):
                    scale.append(dict(boundary=label,group=group,input=name,
                                      original_mean=float(old_scaler.mean_[i]),corrected_mean=float(new_scaler.mean_[i]),
                                      original_std=float(old_scaler.scale_[i]),corrected_std=float(new_scaler.scale_[i]),
                                      original_complete_rows=len(old[features].dropna()),
                                      corrected_complete_rows=len(new[features].dropna())))
            _,old_episodes=neural_training_segments(old,features)
            _,new_episodes=neural_training_segments(new,features)
            samples.append(dict(boundary=label,group=group,
                                original_samples=sum(x['training_samples'] for x in old_episodes),
                                corrected_samples=sum(x['training_samples'] for x in new_episodes),
                                original_episodes=sum(x['retained'] for x in old_episodes),
                                corrected_episodes=sum(x['retained'] for x in new_episodes)))
    before=windows(original);after=windows(corrected)
    pd.testing.assert_series_equal(before.scored_hours,after.scored_hours)
    assert len(after[after.full_week])==23 and int(after[after.full_week].scored_hours.sum())==3624
    output=REVISION/'artifacts/phase1'
    pd.DataFrame(changes).to_csv(output/'invalid_input_changes.csv',index=False)
    pd.DataFrame(scale).to_csv(output/'scaling_comparison.csv',index=False)
    pd.DataFrame(samples).to_csv(output/'neural_sample_comparison.csv',index=False)
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()
    preserved=json.loads((output/'original_manifest.json').read_text())['files'][cfg['source']]['sha256']
    earlier=json.loads((ROOT/'revision/artifacts/phase1/original_manifest.json').read_text())['files'][cfg['source']]['sha256']
    assert source_sha256==preserved==earlier
    evidence=dict(version=cfg['version'],source_sha256=source_sha256,
                  corrected_cells=4,training_target_unchanged=True,test_scored_hours_unchanged=3624,
                  test_origins_unchanged=23,source_csv_preserved=True,
                  input_changes_file='invalid_input_changes.csv',
                  scaling_file='scaling_comparison.csv',sample_file='neural_sample_comparison.csv')
    (output/'input_audit.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
