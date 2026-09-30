"""Scientific contracts for broader scoring and explicit inference assumptions."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
import pandas as pd
from revision.corrected.code.protocol import load_calendar,split_position
from revision.corrected.code.phase2_models import Fitted
from revision.corrected.code.coverage_protocol import seasonal_past_fill,windows,forecast,metrics,dense_prediction
from revision.corrected.code.coverage_checks import latest_observed_persistence


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.grid=load_calendar();cls.position=split_position(cls.grid)

    def test_schedule_retains_23_origins_and_observed_hours(self):
        table=windows(self.grid);full=table[table.full_week]
        self.assertEqual(len(full),23);self.assertEqual(full.scored_hours.sum(),3624)
        self.assertEqual(full.full_observed_week.sum(),19)
        self.assertEqual(set(full.loc[~full.full_observed_week,'window']),{8,11,12,14})
        self.assertEqual(int(table.iloc[-1].calendar_hours),163)

    def test_fill_preserves_observations_and_is_prefix_causal(self):
        values=pd.DataFrame({'pm2_5':np.arange(600,dtype=float)})
        values.iloc[300:420]=np.nan
        filled=seasonal_past_fill(values)
        np.testing.assert_array_equal(filled.iloc[300:420].pm2_5,np.arange(132,252))
        observed=values.pm2_5.notna();np.testing.assert_array_equal(filled.loc[observed].pm2_5,values.loc[observed].pm2_5)
        pd.testing.assert_frame_equal(seasonal_past_fill(values.iloc[:450]),filled.iloc[:450])
        changed=values.copy();changed.iloc[450:]=1e9
        pd.testing.assert_frame_equal(seasonal_past_fill(changed).iloc[:450],filled.iloc[:450])

    def test_missing_initial_history_rejected(self):
        with self.assertRaises(ValueError):seasonal_past_fill(pd.DataFrame({'pm2_5':[np.nan,1.]}))

    def test_persistence_uses_last_genuine_observation_despite_trailing_gap(self):
        history=pd.DataFrame({'pm2_5':[12.,42.,np.nan,np.nan]})
        np.testing.assert_array_equal(latest_observed_persistence(history,4),[42.]*4)
        with self.assertRaises(ValueError):latest_observed_persistence(pd.DataFrame({'pm2_5':[np.nan]}))

    def test_masks_and_target_isolation_at_partially_observed_origin(self):
        p=self.position+7*168;fitted=Fitted('prophet',None,['no'],SimpleNamespace(mean_=np.array([10.]),scale_=np.array([2.]),transform=lambda x:(x-10)/2),None,p,{})
        calls=[]
        def dense(model,context,future):
            self.assertNotIn('pm2_5',future);calls.append(context.copy())
            return future.no.to_numpy()+100,None
        with patch('revision.corrected.code.coverage_protocol.dense_prediction',dense):
            prediction,score,meta,_=forecast(fitted,self.grid,p)
            changed=self.grid.copy();changed.iloc[p:p+168,changed.columns.get_loc('pm2_5')]=1e8
            prediction2,_,_,_=forecast(fitted,changed,p)
        self.assertEqual(score.sum(),120);self.assertEqual(meta['future_placeholder_cells'],48)
        self.assertTrue(np.isnan(prediction[~score]).all())
        np.testing.assert_allclose(prediction,prediction2,equal_nan=True)
        self.assertTrue(meta['placeholder_invariance_passed'])
        self.assertTrue(all(context.index.max()<self.grid.index[p] for context in calls))

    def test_cross_horizon_placeholder_effect_is_rejected(self):
        p=self.position+7*168;fitted=Fitted('prophet',None,['no'],SimpleNamespace(mean_=np.array([10.]),scale_=np.array([2.]),transform=lambda x:(x-10)/2),None,p,{})
        with patch('revision.corrected.code.coverage_protocol.dense_prediction',lambda m,c,f:(f.no.to_numpy()+f.no.sum(),None)):
            with self.assertRaises(AssertionError):forecast(fitted,self.grid,p)

    def test_partial_week_pooled_and_weekly_means_differ(self):
        frame=pd.DataFrame({'window':[1,1,2,2],'score_eligible':[True,True,True,False],
                            'original_target':[0.,0.,0.,np.nan],'base_prediction':[2.,2.,10.,1e9]})
        result=metrics(frame)
        self.assertEqual(result['hours'],3);self.assertAlmostEqual(result['pooled_mae'],14/3)
        self.assertAlmostEqual(result['mean_weekly_mae'],6.)

    def test_installed_neural_future_placeholders_do_not_affect_other_leads(self):
        import torch
        from neuralprophet import NeuralProphet,set_random_seed,set_log_level
        torch.set_num_threads(2);set_random_seed(42);set_log_level('ERROR')
        dates=pd.date_range('2024-01-01',periods=164,freq='h')
        x=np.sin(np.arange(164)/10)
        history=pd.DataFrame({'ds':dates[:160],'y':20+3*x[:160],'x':x[:160],'ID':'episode_000'})
        model=NeuralProphet(n_lags=8,n_forecasts=4,epochs=2,batch_size=32,learning_rate=.001,
            yearly_seasonality=False,weekly_seasonality=False,daily_seasonality=True,
            impute_missing=False,drop_missing=True,global_normalization=True,global_time_normalization=True,
            accelerator='cpu',trainer_config={'default_root_dir':'/tmp/weather-coverage-neural-test','enable_model_summary':False})
        model.add_future_regressor('x',normalize='off')
        model.fit(history,freq='h',progress=None,num_workers=0,checkpointing=False)
        context=history.iloc[-8:].rename(columns={'y':'pm2_5'}).set_index('ds').drop(columns='ID')
        context.index.name='datetime'
        future=pd.DataFrame({'x':x[160:]},index=pd.DatetimeIndex(dates[160:],name='datetime'))
        fitted=Fitted('neuralprophet',model,['x'],None,None,160,{},'episode_000')
        low=future.copy();high=future.copy();low.iloc[1]=0.;high.iloc[1]=10.
        a,_=dense_prediction(fitted,context,low);b,_=dense_prediction(fitted,context,high)
        np.testing.assert_allclose(a[[0,2,3]],b[[0,2,3]],rtol=1e-6,atol=1e-4)
        self.assertGreater(abs(a[1]-b[1]),1e-4)


if __name__=='__main__':unittest.main()
