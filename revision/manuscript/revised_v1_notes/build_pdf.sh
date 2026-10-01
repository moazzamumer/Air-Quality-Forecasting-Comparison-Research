#!/usr/bin/env bash
set -euo pipefail
PM_NOTES_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PM_ROOT=$(cd -- "$PM_NOTES_DIR/../../.." && pwd)
PM_TEX_TREE=${PM_REVISION_TEXMF:-/tmp/pm-revision-texmf}
PM_TEX_CACHE=${PM_REVISION_TEXVAR:-/tmp/pm-revision-texvar}
PM_PDFLATEX=${PM_REVISION_PDFLATEX:-/home/moazzam/.local/bin/pdflatex}
PM_BIBTEX=${PM_REVISION_BIBTEX:-/home/moazzam/.local/bin/bibtex}
# Standard journal packages must be installed in the local TeX setup or PM_TEX_TREE.
# Compile existing source by default so later manual author edits are preserved.
# --regenerate intentionally replaces v1 text/figures from the generation scripts.
if [[ ${1:-} == --regenerate ]]; then
    python3 "$PM_NOTES_DIR/build_manuscript.py"
    MPLCONFIGDIR=/tmp/pm-revision-mpl "$PM_ROOT/venv/bin/python" "$PM_NOTES_DIR/build_figures.py"
fi
cd -- "$PM_NOTES_DIR/../revised_v1"
TEXMFHOME="$PM_TEX_TREE" TEXMFVAR="$PM_TEX_CACHE" "$PM_PDFLATEX" -interaction=nonstopmode -halt-on-error manuscript.tex > "$PM_NOTES_DIR/first_pass.log" 2>&1
TEXMFHOME="$PM_TEX_TREE" "$PM_BIBTEX" manuscript > "$PM_NOTES_DIR/bibtex_build.log" 2>&1
python3 "$PM_NOTES_DIR/highlight_bibliography.py"
TEXMFHOME="$PM_TEX_TREE" TEXMFVAR="$PM_TEX_CACHE" "$PM_PDFLATEX" -interaction=nonstopmode -halt-on-error manuscript.tex > "$PM_NOTES_DIR/reference_pass.log" 2>&1
TEXMFHOME="$PM_TEX_TREE" TEXMFVAR="$PM_TEX_CACHE" "$PM_PDFLATEX" -interaction=nonstopmode -halt-on-error manuscript.tex > "$PM_NOTES_DIR/final_build.log" 2>&1
python3 - <<'PY'
from pathlib import Path
log=Path('manuscript.log').read_text()
assert 'Output written on manuscript.pdf' in log
for problem in ['There were undefined','LaTeX Error:', 'Package soul Error:', 'Overfull \\hbox', 'Overfull \\vbox']:
    assert problem not in log,problem
print('PDF compiled with resolved references and no overfull boxes.')
PY
