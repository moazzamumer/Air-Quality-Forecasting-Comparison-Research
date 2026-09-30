"""Read-only audit of saved preprocessing, selection and evaluation boundaries."""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from .protocol import ROOT, REVISION, load_calendar, split_position, neural_training_segments


def main():
    _, grid = load_calendar()
    cutoff = split_position(grid)
    source = REVISION / 'artifacts/coverage_reconsideration'
    strict = REVISION / 'artifacts/phase2'
    files = sorted((source / 'runs').glob('*/metadata.json'))
    validation_files = sorted((strict / 'runs').glob('validate_*/metadata.json'))
    assert len(files) == 129 and len(validation_files) == 8
    scalers = normalizations = warm_starts = 0
    cache = {}
    for path in files + validation_files:
        meta = json.loads(path.read_text())
        task, fit = meta['task'], meta['fit']
        origin = pd.Timestamp(meta['fit_origin'])
        history = grid.loc[grid.index < origin]
        assert len(history) == fit['training_calendar_hours']
        assert fit['fit_end_exclusive'] == meta['fit_origin']
        assert not fit['target_imputed'] and not fit['target_clipped']
        features = task['features']
        if features:
            values = history[features].dropna()
            if task['clip_inputs']:
                lower, upper = values.quantile(.01), values.quantile(.99)
                for f in features:
                    np.testing.assert_allclose(fit['input_clip_bounds']['lower'][f], lower[f])
                    np.testing.assert_allclose(fit['input_clip_bounds']['upper'][f], upper[f])
                values = values.clip(lower, upper, axis=1)
            np.testing.assert_allclose([fit['scaler']['mean'][f] for f in features], values.mean(), rtol=1e-10)
            np.testing.assert_allclose([fit['scaler']['scale'][f] for f in features], values.std(ddof=0), rtol=1e-10)
            scalers += 1
        if task['family'] == 'neuralprophet':
            key = (origin, tuple(features))
            if key not in cache:
                segmented, episodes = neural_training_segments(history, features)
                assert pd.to_datetime(segmented.ds).max() < origin
                cache[key] = (float(segmented.y.min()), float(segmented.y.quantile(.95)-segmented.y.min()),
                              sum(e['training_samples'] for e in episodes))
            shift, scale, samples = cache[key]
            np.testing.assert_allclose([fit['target_normalization']['shift'], fit['target_normalization']['scale']],
                                       [shift, scale], rtol=1e-10)
            assert samples == fit['training_samples']
            normalizations += 1
        for record in (meta, fit.get('optimizer', {})):
            if 'initialization_source_cutoff' in record:
                assert pd.Timestamp(record['initialization_source_cutoff']) <= origin
                warm_starts += 1
    # Independently recompute successful validation scores and selected candidates.
    candidates = {}
    for path in validation_files:
        meta = json.loads(path.read_text())
        if meta['status'] != 'completed':
            continue
        d = pd.read_csv(path.parent/'forecasts.csv', parse_dates=['target_timestamp'])
        assert d.target_timestamp.max() < grid.index[cutoff]
        assert pd.Timestamp(meta['fit_origin']) == grid.index[cutoff-4*168]
        error = d.original_target-d.base_prediction
        mae = error.abs().groupby(d.window).mean().mean()
        rmse = np.sqrt((error**2).mean())
        np.testing.assert_allclose([mae, rmse], [meta['mean_weekly_mae'], meta['pooled_rmse']])
        task = meta['task']
        candidates.setdefault(task['family'], []).append((mae, rmse, task['id'], task['candidate']))
    selection = json.loads((strict/'selection.json').read_text())['selected']
    for family, scores in candidates.items():
        assert sorted(scores)[0][3] == selection[family]
    for path in files:
        task = json.loads(path.read_text())['task']
        assert task['candidate'] == selection[task['family']]
    # Recalculate saved aggregate errors without rewriting any scientific outputs.
    from .phase3_analysis import load_streams, losses, summarize
    streams = load_streams()
    saved = pd.read_csv(REVISION/'artifacts/phase3/performance.csv').set_index('stream')
    for name, frame in streams.items():
        _, numbers = summarize(losses(frame))
        for key, value in numbers.items():
            np.testing.assert_allclose(saved.loc[name, key], value, rtol=1e-10)
    evidence = dict(reviewed_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        raw_data_sha256=hashlib.sha256((ROOT/'data/beijing.csv').read_bytes()).hexdigest(),
        audit_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        fitted_metadata_records_checked=len(files)+len(validation_files),
        input_scalers_recomputed_from_pre_origin_history=scalers,
        neural_target_normalizations_and_sample_counts_checked=normalizations,
        recorded_warm_start_cutoffs_checked=warm_starts,
        successful_validation_candidates_recomputed=sum(map(len,candidates.values())),
        selection_matches_training_only_validation=True, all_final_tasks_match_selection=True,
        performance_streams_recomputed=len(streams),
        conclusion='No new leakage defect found in checked paths; invalid-input blocker and PP/provenance limitations remain.',
        scope='Saved evidence and source audit; no new research model fits or independent upstream-data authentication.')
    output = REVISION/'artifacts/phase4a/lifecycle_evidence.json'
    output.write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
