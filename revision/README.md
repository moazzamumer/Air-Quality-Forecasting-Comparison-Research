# Revision workspace

All revision work belongs here. The original `main.ipynb`, raw/preprocessed CSVs,
extraction notebook, supporting scripts, and submitted manuscript are preserved.
Their SHA-256 baseline is in `artifacts/phase1/original_manifest.json`.

Open `main_revision.ipynb` as the single notebook entry point. Supporting modules
hold reusable preprocessing, model checks and reproducibility commands; the
notebook will present the experiment sequence and results as the revision grows.
The research question, model families and two updating regimes build on the
original study. Correctness fixes and reviewer-requested analyses can change
reported numbers and conclusions; they do not introduce a replacement study.

## Organization

- `code/`: reusable audit, protocol checks and bounded pilot tools.
- `config/`: explicit experimental protocol; version changes before reruns.
- `main_revision.ipynb`: main notebook for the revision workflow.
- `tests/`: checks for calendar preservation, leakage prevention and forecast alignment.
- `artifacts/phase1/`: machine-readable audit results, coverage masks, rankings, checks and pilot records.
- `reports/`: findings, discrepancies, protocol decisions and phase summaries.
- Root Markdown documents: revision plan, reviewer tracker and response draft.
- `archive_locations.json`: relocation paths and checksums for old supporting files.

Old supporting files and outputs are archived under `../legacy/`. The original
`../main.ipynb`, `../data/` and submission manuscript retain their root paths.
The preservation checks resolve moved originals through the relocation record
without replacing their original checksum baseline.

## Phase 1 commands

Run from the original project directory with its existing Python environment:

```bash
venv/bin/python -m revision.code.audit
venv/bin/python -m unittest discover -s revision/tests -v
venv/bin/python -m revision.code.checks
MPLCONFIGDIR=/tmp/weather-revision-matplotlib venv/bin/python -m revision.code.model_checks
MPLCONFIGDIR=/tmp/weather-revision-matplotlib venv/bin/python -m revision.code.pilots
venv/bin/python -m revision.code.phase1_summary
```

For controlled timing, explicitly set `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
`MKL_NUM_THREADS` and `NUMEXPR_NUM_THREADS` to 2. The pilot launcher does this for
each isolated child and runs models sequentially. Pilots have time/RSS guards.
Read their status, convergence and logs rather than assuming successful termination.

The observed dependency file describes the existing environment. It is not yet
a portable lockfile. No dependency installation or original-file editing is
performed by these commands. A later clean-environment check belongs to Phase 5.

Audit and check outputs are not revised research results. The one-window pilots
use the first validation origin inside the training partition, two NeuralProphet
epochs and a bounded SARIMAX optimization. Do not cite pilot errors or rankings.

## Next boundary

Read `reports/PHASE1_SUMMARY.md` for current evidence and the Phase 2 readiness
decision. Full comparison experiments belong to Phase 2, after the protocol and
compute budget have been resolved. The old reported numbers are not acceptance
targets for new experiments.
