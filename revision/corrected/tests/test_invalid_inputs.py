"""Scientific contracts for the corrected working calendar."""
import unittest

import numpy as np
import pandas as pd

from revision.corrected.code.protocol import (
    ROOT, configuration, load_calendar, split_position, fit_input_scaler,
    neural_training_segments,
)
from revision.corrected.code.coverage_protocol import windows


class InvalidInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = pd.read_csv(ROOT/'data/beijing.csv')
        cls.raw, cls.grid = load_calendar()
        cls.cutoff = split_position(cls.grid)

    def test_only_four_named_pollutant_cells_become_missing(self):
        original = self.original.set_index(pd.to_datetime(self.original[['year','month','day','hour']]))
        expected = [('2023-07-26 07:00','o3'), ('2024-02-07 23:00','pm10'),
                    ('2024-08-05 03:00','no2'), ('2024-08-11 00:00','no2')]
        for timestamp, feature in expected:
            self.assertEqual(original.loc[pd.Timestamp(timestamp),feature], -9999)
            self.assertTrue(pd.isna(self.raw.loc[pd.Timestamp(timestamp),feature]))
        changed = self.raw[original.columns].compare(original.loc[self.raw.index], keep_equal=False)
        self.assertEqual(len(changed),4)
        self.assertTrue(self.raw.temperature.lt(0).any())
        pd.testing.assert_series_equal(self.raw.pm2_5,original.pm2_5,check_names=False)

    def test_scaling_episodes_and_test_coverage_change_as_expected(self):
        cfg=configuration();features=cfg['selected_features']
        _,old = __import__('revision.code.protocol',fromlist=['load_calendar']).load_calendar()
        old_history=old.iloc[:self.cutoff];new_history=self.grid.iloc[:self.cutoff]
        old_scale,_=fit_input_scaler(old_history,features)
        new_scale,_=fit_input_scaler(new_history,features)
        self.assertLess(new_scale.scale_[features.index('no2')],old_scale.scale_[features.index('no2')])
        _,old_episodes=neural_training_segments(old_history,features)
        _,new_episodes=neural_training_segments(new_history,features)
        self.assertEqual(sum(e['training_samples'] for e in old_episodes),30423)
        self.assertEqual(sum(e['training_samples'] for e in new_episodes),29991)
        original_mask=old.iloc[self.cutoff:][['pm2_5']+cfg['broad_features']].notna().all(axis=1)
        corrected_mask=self.grid.iloc[self.cutoff:][['pm2_5']+cfg['broad_features']].notna().all(axis=1)
        pd.testing.assert_series_equal(original_mask,corrected_mask)
        full=windows(self.grid);full=full[full.full_week]
        self.assertEqual((len(full),int(full.scored_hours.sum())),(23,3624))


if __name__ == '__main__':unittest.main()
