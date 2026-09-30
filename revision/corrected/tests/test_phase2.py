"""Phase 2 information-set and result-shape contracts."""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
import pandas as pd

from revision.corrected.code.protocol import load_calendar, split_position
from revision.corrected.code.phase2_models import Fitted, forecast
from revision.corrected.code.phase2_runner import weekly_rows, load_tasks
from revision.corrected.code.phase2_status import check_saved_stream


class Phase2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.grid=load_calendar()
        cls.position=split_position(cls.grid)

    def test_validation_grid_has_all_bounded_candidates(self):
        tasks=load_tasks('validate')
        self.assertEqual(len(tasks),8)
        self.assertEqual({t['family'] for t in tasks}, {'sarimax','prophet','neuralprophet'})
        self.assertTrue(all(t['regime']=='frozen' and t['seed']==42 for t in tasks))

    def test_neural_origin_uses_scaled_history_and_future_without_future_y(self):
        features=['no']
        mean=float(self.grid.iloc[:self.position].no.mean())
        scale=float(self.grid.iloc[:self.position].no.std(ddof=0))
        scaler=SimpleNamespace(transform=lambda x:(x-mean)/scale)
        fitted=Fitted('neuralprophet',SimpleNamespace(),features,scaler,None,self.position,{},'episode_000')
        captured={}
        def future_builder(model,context,future):
            captured['context']=context.copy(); captured['future']=future.copy()
            self.assertNotIn('y',future)
            return pd.concat([context,future.assign(y=np.nan,ID='episode_000')],ignore_index=True)
        def prediction(model,frame,raw):
            return pd.DataFrame({'ds':[self.grid.index[self.position]],
                                 **{f'step{i}':[float(i)] for i in range(168)}})
        with patch('revision.corrected.code.phase2_models.np_future',future_builder),patch('revision.corrected.code.phase2_models.np_predict',prediction):
            values,_,_=forecast(fitted,self.grid,self.position)
        np.testing.assert_allclose(values,np.arange(168))
        expected=(self.grid.iloc[self.position-168:self.position].no.to_numpy()-mean)/scale
        np.testing.assert_allclose(captured['context'].no.to_numpy(),expected)
        expected_future=(self.grid.iloc[self.position:self.position+168].no.to_numpy()-mean)/scale
        np.testing.assert_allclose(captured['future'].no.to_numpy(),expected_future)
        self.assertTrue(captured['context'].y.notna().all())
        self.assertEqual(captured['context'].ds.max()+pd.Timedelta(hours=1),captured['future'].ds.min())

    def test_weekly_rows_rejects_missing_score_target(self):
        grid=self.grid.copy(); grid.loc[grid.index[self.position],'pm2_5']=np.nan
        row=SimpleNamespace(position=self.position,window=1)
        task=dict(id='test',family='prophet',regime='frozen',clip_inputs=False,seed=42)
        with self.assertRaises(ValueError):
            weekly_rows(task,grid,row,np.zeros(168),0,0)

    def test_saved_stream_rejects_wrong_week_and_false_observation_mask(self):
        row=SimpleNamespace(position=self.position,window=1)
        task=dict(id='test',stage='core',family='prophet',regime='walk',week=1,clip_inputs=False,seed=42)
        frame=weekly_rows(task,self.grid,row,np.zeros(168),0,0)
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'forecast.csv'
            frame.to_csv(file,index=False)
            self.assertEqual(check_saved_stream(file,task,self.grid),'')
            frame.loc[0,'window']=2
            frame.to_csv(file,index=False)
            self.assertIn('locked eligibility',check_saved_stream(file,task,self.grid))
            frame.loc[0,'window']=1
            frame.loc[0,'observed']=False
            frame.to_csv(file,index=False)
            self.assertIn('mask is false',check_saved_stream(file,task,self.grid))


if __name__=='__main__':unittest.main()
