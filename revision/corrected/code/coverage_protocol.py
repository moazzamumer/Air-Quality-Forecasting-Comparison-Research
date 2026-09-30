"""Broader coverage contracts; leave the verified strict protocol unchanged."""
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from .protocol import REVISION, configuration, load_calendar, split_position, transform_inputs, prophet_frame, extract_raw_forecast
from .model_checks import np_future, np_predict
from .phase2_runner import signature as strict_signature

OUT=REVISION/'artifacts/coverage_reconsideration'
POLICY=REVISION/'config/coverage_reconsideration.json'


def policy():return json.loads(POLICY.read_text())


def signature():
    h=hashlib.sha256(strict_signature().encode())
    for file in [configuration_source(),POLICY,Path(__file__),REVISION/'code/coverage_runner.py']:
        h.update(file.read_bytes())
    return h.hexdigest()


def configuration_source():
    """Bind corrected forecasts to the exact immutable raw CSV bytes."""
    return REVISION.parents[1]/configuration()['source']


def seasonal_past_fill(history,period=168):
    """Fill missing historical values only, without changing observed values."""
    result=history.copy()
    for column in history:
        values=result[column].to_numpy(dtype=float,copy=True)
        for i in np.flatnonzero(~np.isfinite(values)):
            if i>=period and np.isfinite(values[i-period]):values[i]=values[i-period]
            elif i>0 and np.isfinite(values[i-1]):values[i]=values[i-1]
            else:raise ValueError('No prior value for causal history fill')
        result[column]=values
    return result


def windows(grid):
    cfg=configuration();start=split_position(grid);records=[]
    broad=[cfg['target']]+cfg['broad_features']
    for w,p in enumerate(range(start,len(grid),168),1):
        future=grid.iloc[p:p+168];context=grid.iloc[p-168:p]
        mask=future[broad].notna().all(axis=1)
        records.append(dict(window=w,position=p,origin=str(future.index[0]),last_target=str(future.index[-1]),
             calendar_hours=len(future),scored_hours=int(mask.sum()),
             missing_context_target_hours=int(context[cfg['target']].isna().sum()),
             missing_context_input_hours=int(context[cfg['broad_features']].isna().any(axis=1).sum()),
             full_week=len(future)==168,full_observed_week=len(future)==168 and bool(mask.all()),
             strict_eligible=len(future)==168 and bool(mask.all()) and not context[broad].isna().any().any()))
    return pd.DataFrame(records)


def dense_prediction(fitted,context,future_x):
    """Predict from an already complete computational frame, without future y."""
    h=len(future_x)
    if fitted.family=='sarimax':
        result=fitted.model.forecast(steps=h,exog=future_x[fitted.features] if fitted.features else None)
        if not result.index.equals(future_x.index):raise ValueError('SARIMAX timestamp mismatch')
        return result.to_numpy(),None
    if fitted.family=='prophet':
        result=fitted.model.predict(future_x.reset_index().rename(columns={'datetime':'ds'}))
        if not pd.DatetimeIndex(result.ds).equals(future_x.index):raise ValueError('Prophet timestamp mismatch')
        cols=[c for c in ['trend','daily','weekly','yearly']+fitted.features if c in result]
        return result.yhat.to_numpy(),result[['ds']+cols]
    frame=prophet_frame(context.iloc[-fitted.model.n_lags:]);frame['ID']=fitted.first_episode_id
    future=future_x.reset_index().rename(columns={'datetime':'ds'})
    inputs=np_future(fitted.model,frame,future if fitted.features else None)
    raw=np_predict(fitted.model,inputs,raw=True)
    return extract_raw_forecast(raw,future_x.index[0],h).to_numpy(),None


def forecast(fitted,grid,position):
    cfg=configuration();h=168;cols=[cfg['target']]+fitted.features
    # Slice the past before filling, including when the caller supplied future y.
    history=grid.iloc[:position][cols].copy()
    missing=history.iloc[-h:][cols].isna()
    filled=seasonal_past_fill(history)
    context=transform_inputs(filled.iloc[-h:],fitted.features,fitted.scaler,fitted.bounds)
    future=grid.iloc[position:position+h][fitted.features].copy()
    raw_missing=future.isna()
    for i,feature in enumerate(fitted.features):future[feature]=future[feature].fillna(float(fitted.scaler.mean_[i]))
    dense=transform_inputs(future,fitted.features,fitted.scaler,fitted.bounds)
    started=time.perf_counter();prediction,components=dense_prediction(fitted,context,dense)
    base_seconds=time.perf_counter()-started
    if len(prediction)!=h or not np.isfinite(prediction).all():raise ValueError('Nonfinite full computational forecast')
    score=grid.iloc[position:position+h][[cfg['target']]+cfg['broad_features']].notna().all(axis=1).to_numpy()
    invariant_seconds=0.;max_difference=0.
    if raw_missing.any().any():
        alternate=dense.copy()
        # Perturb AFTER clipping/scaling so even clipped-input controls get a real perturbation.
        alternate[fitted.features]=alternate[fitted.features].mask(raw_missing,10.)
        started=time.perf_counter();perturbed,_=dense_prediction(fitted,context,alternate)
        invariant_seconds=time.perf_counter()-started
        tolerance=policy()['placeholder_tolerance']
        np.testing.assert_allclose(prediction[score],perturbed[score],**tolerance)
        max_difference=float(np.max(np.abs(prediction[score]-perturbed[score])))
    uses_dense_context=fitted.family=='neuralprophet'
    metadata=dict(history_context_consumed=uses_dense_context,
        history_context_missing_target_hours=int(missing[cfg['target']].sum()),
        history_target_filled_hours=int(missing[cfg['target']].sum()) if uses_dense_context else 0,
        history_input_filled_cells=int(missing[fitted.features].sum().sum()) if uses_dense_context else 0,
        future_placeholder_cells=int(raw_missing.sum().sum()),scored_hours=int(score.sum()),
        placeholder_max_scored_prediction_difference=max_difference,
        placeholder_invariance_passed=True,forecast_seconds=base_seconds,invariance_check_seconds=invariant_seconds)
    # Never present unavailable-input conditional forecasts as observed PP predictions.
    unavailable=grid.iloc[position:position+h][cfg['broad_features']].isna().any(axis=1).to_numpy()
    prediction[unavailable]=np.nan
    if components is not None:components.loc[unavailable,components.columns!='ds']=np.nan
    return prediction,score,metadata,components


def rows(task,grid,row,prediction,score,diagnostics):
    p=int(row.position);target=grid.iloc[p:p+168].pm2_5.to_numpy(dtype=float)
    return pd.DataFrame(dict(run_id=task['id'],family=task['family'],regime=task['regime'],
        variant=task.get('variant','selected'),seed=task['seed'],window=int(row.window),
        forecast_origin=str(grid.index[p]),target_timestamp=grid.index[p:p+168],lead_hour=np.arange(1,169),
        original_target=target,observed=np.isfinite(target),score_eligible=score,
        base_prediction=prediction,applied_bias=0.,corrected_prediction=prediction,
        history_target_filled_hours=diagnostics['history_target_filled_hours'],
        history_input_filled_cells=diagnostics['history_input_filled_cells']))


def metrics(frame,column='base_prediction'):
    observed=frame[frame.score_eligible];weekly=observed.groupby('window')
    maes=weekly.apply(lambda w:np.mean(np.abs(w.original_target-w[column])),include_groups=False)
    rmses=weekly.apply(lambda w:np.sqrt(np.mean((w.original_target-w[column])**2)),include_groups=False)
    error=observed.original_target-observed[column]
    return dict(windows=maes.size,hours=len(observed),pooled_mae=float(np.abs(error).mean()),
        pooled_rmse=float(np.sqrt((error**2).mean())),mean_weekly_mae=float(maes.mean()),
        weekly_mae_sd=float(maes.std(ddof=1)),mean_weekly_rmse=float(rmses.mean()),weekly_rmse_sd=float(rmses.std(ddof=1)))


def audit():
    OUT.mkdir(parents=True,exist_ok=True);_,grid=load_calendar();table=windows(grid)
    table.to_csv(OUT/'windows.csv',index=False)
    primary=table[table.full_week]
    if len(primary)!=23 or primary.scored_hours.sum()!=3624:raise ValueError('Unexpected broader coverage')
    # Fixed seasonal rule evaluated on synthetic historical gaps within training, without tuning.
    records=[]
    validation=pd.read_csv(REVISION/'artifacts/phase1/validation_windows.csv')
    for row in validation.itertuples():
        p=int(row.position);original=grid.iloc[:p][['pm2_5']].copy()
        for length in [24,48,120]:
            masked=original.copy();masked.iloc[-length:]=np.nan
            reconstructed=seasonal_past_fill(masked)
            truth=original.iloc[-length:].pm2_5.to_numpy();estimate=reconstructed.iloc[-length:].pm2_5.to_numpy()
            records.append(dict(validation_origin=row.origin,masked_history_hours=length,
                                reconstruction_mae=float(np.mean(np.abs(truth-estimate))),
                                reconstruction_rmse=float(np.sqrt(np.mean((truth-estimate)**2))),
                                used_for_method_selection=False))
    pd.DataFrame(records).to_csv(OUT/'history_fill_validation.csv',index=False)
    print('Coverage: 23 full origins, 3,864 scheduled hours, 3,624 observed scoring hours; 19 full and 4 partial weeks',flush=True)
