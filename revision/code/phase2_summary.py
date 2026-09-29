"""Summarize Phase 2 evidence without declaring rankings from point estimates."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .protocol import REVISION
from .phase2_runner import OUT
from .phase2_status import markdown_table
from .phase2_verify import main as verify


def metric_record(frame):
    weeks=frame.groupby('window',sort=True)
    weekly_mae=weeks.apply(lambda w:np.mean(np.abs(w.original_target-w.base_prediction)),include_groups=False)
    weekly_rmse=weeks.apply(lambda w:np.sqrt(np.mean((w.original_target-w.base_prediction)**2)),include_groups=False)
    return dict(windows=frame.window.nunique(),hours=len(frame),
                pooled_mae=float(np.mean(np.abs(frame.original_target-frame.base_prediction))),
                pooled_rmse=float(np.sqrt(np.mean((frame.original_target-frame.base_prediction)**2))),
                mean_weekly_mae=float(weekly_mae.mean()),weekly_mae_sd=float(weekly_mae.std(ddof=1)),
                mean_weekly_rmse=float(weekly_rmse.mean()),weekly_rmse_sd=float(weekly_rmse.std(ddof=1)))


def main():
    verify()
    verified=json.loads((OUT/'verification.json').read_text())
    if verified['integrity_errors'] or verified['pending_tasks']:
        raise RuntimeError('Cannot summarize unfinished or invalid Phase 2 evidence')
    coverage=pd.read_csv(OUT/'verified_coverage.csv')
    records=[]
    for keys,rows in coverage.groupby(['family','regime','variant','seed'],sort=True):
        frames=[pd.read_csv(OUT/'runs'/r.evidence_run_id/'forecasts.csv') for r in rows.itertuples()]
        frame=pd.concat(frames,ignore_index=True).sort_values(['window','lead_hour'])
        if frame[['forecast_origin','target_timestamp']].duplicated().any():raise ValueError('Duplicate pooled forecast')
        records.append(dict(family=keys[0],regime=keys[1],variant=keys[2],seed=keys[3],
                            recovered_windows=int(rows.recovered_windows.sum()),**metric_record(frame)))
    metrics=pd.DataFrame(records);metrics.to_csv(OUT/'experimental_summary.csv',index=False)
    candidates=[]
    for meta in sorted((OUT/'runs').glob('validate_*/metadata.json')):
        record=json.loads(meta.read_text());task=record['task']
        candidates.append(dict(run_id=task['id'],family=task['family'],candidate=json.dumps(task['candidate'],sort_keys=True),
                               status=record['status'],mean_weekly_mae=record.get('mean_weekly_mae'),
                               pooled_rmse=record.get('pooled_rmse')))
    pd.DataFrame(candidates).to_csv(OUT/'validation_summary.csv',index=False)
    core=metrics[(metrics.variant=='selected')]
    sensitivity=metrics[(metrics.regime=='frozen') & (metrics.seed==42)]
    lines=['# Phase 2 experimental evidence','',
           f"Verification exit evidence ready: **{verified['phase2_exit_evidence_ready']}**. Valid completed tasks: {verified['complete_tasks']}/94; numerical recoveries: {verified['recovered_tasks']}; unresolved failed tasks: {verified['unresolved_failed_tasks']}.",
           '', '## Training-only settings','',
           'Four complete validation weeks were entirely within the training partition. Candidate fits ended before the first validation origin; later origins refreshed history without refitting. Selection used mean weekly MAE, then pooled RMSE. This is a fixed-parameter validation proxy for both core regimes, not exhaustive tuning.',
           '', '```json',json.dumps(json.loads((OUT/'selection.json').read_text())['selected'],indent=2),'```',
           '', 'One of four SARIMAX validation candidates did not converge under the bounded screening policy. Its failure is retained; it was not scored or selected. The subsequent numerical recovery policy applies to final-comparison fits with the selected settings and does not reopen candidate selection.',
           '', '## Core point estimates and available coverage','',
           markdown_table(core[['family','regime','seed','windows','hours','recovered_windows','mean_weekly_mae','pooled_rmse']].round(4)),
           '', 'The primary MAE column is mean weekly MAE. Weekly windows all contain 168 hours, so pooled MAE is identical; pooled RMSE differs from mean weekly RMSE. The CSV saves both definitions and sample weekly standard deviations. Each row uses that run’s available complete weeks. If coverage differs, these rows are not a matched ranking. Phase 3 must report matched comparisons, paired uncertainty, lead-time errors, residuals and seed variability. No seed-averaged forecast is substituted for the seed-42 primary run.',
           '', '## Frozen predictor and clipping controls (seed 42)','',
           markdown_table(sensitivity[['family','variant','windows','hours','recovered_windows','mean_weekly_mae','pooled_rmse']].round(4)),
           '', 'No-input, selected four-gas, broad-input and clipped-input runs retain the selected model settings. Broad inputs include contemporaneous future PM10 under Perfect Prognosis and therefore provide additional target-related information. Clipping affects predictors at training-derived 1st/99th percentiles; fitting/scoring targets remain original. These controls were tested in the frozen regime only.',
           '', '## Forecast reuse and correction','',
           'Three baselines cover 16 weeks / 2,688 hours. All five frozen core streams have no-correction plus six predefined alpha replays, giving 35 saved streams. Alpha 0.3 remains the primary predefined setting. Bias is applied before the current week’s outcomes update it; skipped windows carry the bias unchanged. Corrections use base residual means.',
           '', '## Numerical fitting and resources','',
           'Original nonconverged attempts remain in their own folders and have no scored stream. A recovery, where present, changes numerical initialization, derivative precision and line-search allowance while retaining orders, data cutoff, features and preprocessing; it requires convergence, finite likelihood/parameters, and training likelihood no worse than the original failed point. Verification names the exact recovery evidence used for every task. Runtime analysis must include failed attempts and every recovery effort, including rejected attempts.',
           '', 'The two regimes share the identical initial fit/forecast, explicitly marked by `reused_from_run`; later refits are independent expanding-history fits. All processes use the same local CPU, two configured threads, and no GPU. Original-run `fit_seconds` includes model import/initialization and optimization, excluding earlier calendar/scaler preparation; recovery `fit_seconds` measures optimization only. Recovery preprocessing metadata inherits the original fit description. Supervisor elapsed time includes full child-process setup and is the consistent measure for total effort. Peak group RSS is sampled every 0.5 seconds. Phase 3 must label these timing boundaries and shared/recovered work explicitly.',
           '', '## Evidence locations','',
           '- `artifacts/phase2/verification.json` and `verified_coverage.csv`: completeness, integrity and exact forecast evidence mapping.',
           '- `artifacts/phase2/runs/*/`: timestamped forecasts, training traces/episodes, fit metadata, coefficients/components and logs.',
           '- `artifacts/phase2/baselines/`, `corrections/`, `experimental_summary.csv`, `validation_summary.csv`: reloadable outputs.',
           '- `config/protocol.json` and `config/sarimax_numerical_recovery.json`: locked study protocol and recorded numerical amendment.',
           '', f"All {verified['original_files_verified']} fingerprinted originals remain unchanged. The original `main.ipynb` and submitted manuscript have not been replaced. Phase 2 supplies experimental evidence; manuscript and point-by-point response writing remain pending."]
    (REVISION/'reports/PHASE2_SUMMARY.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__=='__main__':main()
