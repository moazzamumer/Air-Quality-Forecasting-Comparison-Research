#!/usr/bin/env bash
set -euo pipefail
PM_RESPONSE_NOTES=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PM_TEX_TREE=${PM_REVISION_TEXMF:-/tmp/pm-revision-texmf}
PM_TEX_CACHE=${PM_REVISION_TEXVAR:-/tmp/pm-revision-texvar}
PM_PDFLATEX=${PM_REVISION_PDFLATEX:-/home/moazzam/.local/bin/pdflatex}
# Compile existing source by default; --regenerate refreshes from authored prose.
if [[ ${1:-} == --regenerate ]]; then
    python3 "$PM_RESPONSE_NOTES/build_response.py"
fi
cd -- "$PM_RESPONSE_NOTES/../revised_v1"
TEXMFHOME="$PM_TEX_TREE" TEXMFVAR="$PM_TEX_CACHE" "$PM_PDFLATEX" -interaction=nonstopmode -halt-on-error response_to_reviewers.tex > "$PM_RESPONSE_NOTES/first_pass.log" 2>&1
TEXMFHOME="$PM_TEX_TREE" TEXMFVAR="$PM_TEX_CACHE" "$PM_PDFLATEX" -interaction=nonstopmode -halt-on-error response_to_reviewers.tex > "$PM_RESPONSE_NOTES/final_build.log" 2>&1
python3 - <<'PY'
from pathlib import Path
log=Path('response_to_reviewers.log').read_text()
assert 'Output written on response_to_reviewers.pdf' in log
for problem in ['LaTeX Error:', 'There were undefined', 'Overfull \\hbox', 'Overfull \\vbox']:
    assert problem not in log, problem
print('Response PDF compiled without errors, undefined references or overfull boxes.')
PY
