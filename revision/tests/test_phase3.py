"""Scientific guardrails for saved-prediction publication analysis."""
import unittest
import numpy as np
import pandas as pd

from revision.code.phase3_analysis import (OUT, SOURCE, bootstrap_difference,
                                           load_streams, losses, summarize,
                                           strict_sensitivity)


class Phase3AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.streams = load_streams()

    def test_bootstrap_preserves_constant_paired_difference(self):
        result = bootstrap_difference(np.repeat(-2.5, 23))
        for low, high in result.values():
            self.assertAlmostEqual(low, -2.5)
            self.assertAlmostEqual(high, -2.5)

    def test_same_observed_target_mask_and_direct_mae(self):
        a = losses(self.streams['sarimax_frozen_s42'])
        b = losses(self.streams['prophet_frozen_s42'])
        self.assertEqual(len(a), 3624)
        pd.testing.assert_series_equal(a.target, b.target)
        _, computed = summarize(a)
        saved = pd.read_csv(OUT/'performance.csv').set_index('stream').loc['sarimax_frozen_s42']
        self.assertAlmostEqual(computed['pooled_mae'], saved.pooled_mae, places=10)
        self.assertAlmostEqual(computed['mean_weekly_mae'], saved.mean_weekly_mae, places=10)

    def test_strict_base_forecasts_reproduce_original_reference(self):
        comparison = strict_sensitivity(self.streams)
        uncorrected = comparison[~comparison.stream.str.endswith('ewma03')]
        self.assertEqual(len(uncorrected), 22)
        self.assertLess(uncorrected.maximum_prediction_difference.max(), 1e-8)
        corrected = comparison[comparison.stream.str.endswith('ewma03')]
        self.assertTrue((corrected.maximum_prediction_difference > 1).any())

    def test_no_correction_is_identity_on_scored_hours(self):
        base = self.streams['prophet_frozen_s42']
        no = pd.read_csv(SOURCE/'corrections/core_prophet_frozen_s42_alpha_0p0.csv')
        np.testing.assert_allclose(no.loc[no.score_eligible, 'corrected_prediction'],
                                   base.loc[base.score, 'prediction'], atol=1e-10, rtol=0)


if __name__ == '__main__':
    unittest.main()
