#!/usr/bin/env bash
# Resume the computational matrix after training-only selection is complete.
set -euo pipefail
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
export MPLCONFIGDIR=/tmp/weather-revision-matplotlib CUDA_VISIBLE_DEVICES="" TF_CPP_MIN_LOG_LEVEL=3
python_bin=venv/bin/python
"$python_bin" - <<'PY'
import json
from revision.code.phase2_runner import OUT,signature
p=OUT/'selection.json'
if not p.exists():raise SystemExit('Training-only selection has not completed')
selection=json.loads(p.read_text())
if selection['protocol_signature']!=signature():raise SystemExit('Selection signature differs from current protocol/code')
print('Selected configurations:',json.dumps(selection['selected'],sort_keys=True),flush=True)
PY
"$python_bin" -m revision.code.phase2_runner core
"$python_bin" -m revision.code.phase2_status
"$python_bin" -m revision.code.phase2_runner ablate
"$python_bin" -m revision.code.phase2_status
"$python_bin" -m revision.code.phase2_runner correct
"$python_bin" -m revision.code.phase2_status
