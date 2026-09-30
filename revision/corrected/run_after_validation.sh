#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
export MPLCONFIGDIR=/tmp/weather-revision-matplotlib

venv/bin/python -m revision.corrected.code.coverage_runner audit
venv/bin/python -m revision.corrected.code.coverage_runner run
venv/bin/python -m revision.corrected.code.coverage_runner finish
venv/bin/python -m revision.corrected.code.coverage_checks
venv/bin/python -m revision.corrected.code.phase3_analysis
venv/bin/python -m revision.corrected.code.postfit_audit
