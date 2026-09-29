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

- `code/`: reusable audit, protocol checks, bounded pilot tools, and the Phase 2 experiment runner.
- `config/`: explicit experimental protocol; version changes before reruns.
- `main_revision.ipynb`: main notebook for the revision workflow.
- `tests/`: checks for calendar preservation, leakage prevention and forecast alignment.
- `artifacts/phase1/`: machine-readable audit results, coverage masks, rankings, checks and pilot records.
- `artifacts/phase2/`: validation, forecast streams, correction replays, fitting/resource metadata, and verified coverage.
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

## Phase 2 execution

The revision runner fits models sequentially in isolated child processes and
checkpoints every eligible weekly forecast. Completed tasks with the same
protocol/code signature are skipped on rerun. Inspect each run's `metadata.json`
and `run.log`; a forecast is complete only when metadata says `completed` and
the corresponding `forecasts.csv` exists. A failed or nonconverged SARIMAX fit
is not treated as an evaluated window. The original notebook remains unchanged.

```bash
venv/bin/python -m revision.code.phase2_runner validate
venv/bin/python -m revision.code.phase2_runner baselines
venv/bin/python -m revision.code.phase2_runner core
venv/bin/python -m revision.code.phase2_runner ablate
venv/bin/python -m revision.code.phase2_runner correct
```

`validate` must produce `artifacts/phase2/selection.json` before core or
ablation work. `core` includes matched refits, frozen forecasts and three
NeuralProphet seeds. `ablate` covers no exogenous inputs, broad candidate
inputs, and clipped selected inputs in the frozen regime. `correct` replays
saved frozen base forecasts without model retraining. The managed experiment
matrix has been executed by the revision work; the author does not need to run the notebook.
After validation, `revision/run_phase2_after_validation.sh` runs the remaining
stages in order and refreshes `reports/PHASE2_PROGRESS.md` between stages.
Run `venv/bin/python -m revision.code.phase2_status` at any time to regenerate
the read-only task/coverage report; it also checks saved forecast timestamps,
lead hours and original targets against the raw calendar.
`revision.code.phase2_reuse` records reuse of the identical initial fit and
first-week forecast across the two core regimes. It never reuses a later
walk-forward fit. Metadata names the source run and marks that no additional
fit was executed, so timing analysis can avoid counting shared computation twice.

After the scheduled matrix, `venv/bin/python -m revision.code.phase2_recover`
attempts bounded numerical recovery of nonconverged SARIMAX core/sensitivity
fits under `config/sarimax_numerical_recovery.json`. It preserves the original
failed run and writes a separately identified recovery. Selected model settings
and data cutoffs remain fixed; acceptance uses convergence and training
likelihood rather than forecast errors. Validation selection is not reopened.
`venv/bin/python -m revision.code.phase2_verify` checks the complete evidence
and writes `artifacts/phase2/verification.json` and
`reports/PHASE2_VERIFICATION.md`, including any unresolved coverage exceptions.

## Read the results

`reports/PHASE2_SUMMARY.md` presents descriptive results and fitting limitations.
`artifacts/phase2/verified_coverage.csv` identifies the exact accepted forecast
folder for each core/ablation task, including numerical recoveries. Original
failure metadata remains preserved; its presence does not mean a task is still
unresolved when a verified recovery is listed.

The following commands reload saved evidence and execute the notebook's audit,
checks and results displays without replaying model fitting:

```bash
venv/bin/python -m revision.code.phase2_summary
venv/bin/python -m revision.code.phase2_status
venv/bin/python -m revision.code.execute_notebook
```

The notebook executor uses the existing IPython in one shared process because
kernel sockets are blocked in this sandbox. Saved rich table outputs are ordinary
notebook outputs. The original `../main.ipynb` is never executed or rewritten by
this command. Phase 3 will analyze paired uncertainty, lead times, residuals,
interpretability and resources; manuscript/response edits follow the evidence.

Timing analysis must include original failed fits and all recovery attempts.
`supervisor.jsonl` and `recovery_supervisor.jsonl` record full child-process
elapsed time and sampled peak group RSS; shared first-origin fits are marked as
reused. Rejected Powell recovery code/policy/logs are archived under
`recovery_attempts/powell_v1/`. Its supervisor entries also remain in the main
recovery log, so do not count the archived copy a second time.

## Coverage reconsideration before Phase 3

The completed 16-week matrix remains a strict-availability sensitivity reference.
Moazzam requested a broader evaluation preserving all 23 calendar origins.
`config/coverage_reconsideration.json` records the separate amendment; its
runner writes only to `artifacts/coverage_reconsideration/`. Original source,
training split/configuration selection and fitting-target policies are unchanged.
Observed-hour scoring, explicit causal historical inference filling and actual
model placeholder-invariance checks must pass before the broader protocol is
adopted. Read `reports/COVERAGE_RECONSIDERATION.md` for the assumptions.

```bash
venv/bin/python -m revision.code.coverage_runner audit
venv/bin/python -m revision.code.coverage_runner run
venv/bin/python -m revision.code.coverage_runner finish
```

The author does not need to execute these commands; the revision work runs and
verifies them. Broader and strict artifacts have separate signatures. Do not
rerun candidate selection or replace strict evidence when changing coverage.

Broader coverage has now passed full verification. Read
`reports/COVERAGE_RECONSIDERATION_RESULTS.md` and the executed notebook's
coverage-reconsideration section. `artifacts/coverage_reconsideration/` supplies
the primary 23-origin observed-hour streams; `artifacts/phase2/` preserves the
strict sensitivity. Reload and check without fitting:

```bash
venv/bin/python -m revision.code.coverage_runner finish
venv/bin/python -m revision.code.coverage_checks
venv/bin/python -m revision.code.execute_notebook
```

The coverage chart is generated by the notebook and saved as PNG/PDF. Broader
checks verify original targets/masks, calendar/lead alignment, strict forecast
reproduction, reused-source provenance, training traces, baseline causality and
correction timing. Phase 3 publication analysis remains pending.
