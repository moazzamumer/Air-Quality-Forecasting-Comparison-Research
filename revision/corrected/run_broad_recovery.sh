#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export MPLCONFIGDIR=/tmp/weather-revision-matplotlib
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
timeout 5400 venv/bin/python -u -m revision.corrected.code.broad_sarimax_recovery
venv/bin/python -m revision.corrected.code.coverage_runner finish
venv/bin/python -m revision.corrected.code.coverage_checks
venv/bin/python -m revision.corrected.code.phase3_analysis
venv/bin/python -m revision.corrected.code.postfit_audit
