"""Require complete main experiments and one explicitly declared control failure."""
import hashlib
import json
import numpy as np
from .protocol import REVISION
from .coverage_protocol import OUT, signature


def declared_failure(info):
    from .coverage_runner import tasks
    from .broad_sarimax_recovery import signature as recovery_signature
    policy=json.loads((REVISION/'config/analysis_completion.json').read_text())
    task_id=policy['failed_task'];p=OUT/'runs'/task_id/'metadata.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==policy['failed_metadata_sha256']
    m=json.loads(p.read_text())
    assert m['task']==next(t for t in tasks() if t['id']==task_id)
    assert m['status']=='failed' and m['protocol_signature']==signature()
    assert m['numerical_recovery']['signature']==recovery_signature()
    opt=m['fit']['optimizer']
    assert not opt['converged'] and opt['iterations']==400
    assert np.isfinite(list(m['fit']['parameter_estimates'].values())).all()
    assert not (p.parent/'forecasts.csv').exists()
    assert info['protocol_signature']==signature() and not info['integrity_errors']
    assert info['complete_tasks']==policy['successful_tasks']==128
    assert info['expected_tasks']==policy['attempted_tasks']==129
    assert info['pending_tasks']==[task_id] and not info['ready']
    return task_id
