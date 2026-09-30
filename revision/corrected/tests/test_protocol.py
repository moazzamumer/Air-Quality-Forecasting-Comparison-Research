"""Scientific correctness contracts, not regression tests for old results."""
import unittest
import numpy as np
import pandas as pd
from revision.corrected.code.protocol import (configuration, load_calendar, split_position, window_table,
    origin_inputs, fit_input_scaler, transform_inputs, extract_raw_forecast, persistence, apply_bias, neural_training_segments)


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.grid = load_calendar()
        cls.split = split_position(cls.grid)

    def test_hourly_calendar_preserves_all_original_values(self):
        self.assertTrue((self.grid.index.to_series().diff().dropna() == pd.Timedelta(hours=1)).all())
        pd.testing.assert_frame_equal(self.grid.loc[self.raw.index, self.raw.columns], self.raw, check_dtype=False, check_freq=False)
        self.assertEqual(int(self.grid.pm2_5.isna().sum()), 744)

    def test_strict_shared_coverage(self):
        windows = window_table(self.grid, self.split)
        self.assertEqual(int(windows.eligible.sum()), 16)
        self.assertEqual(int(windows.loc[windows.eligible, "calendar_hours"].sum()), 2688)
        self.assertFalse(bool(windows.iloc[-1].eligible))
        self.assertEqual(int(windows.iloc[-1].calendar_hours), 163)
        self.assertTrue(window_table(self.grid, self.split-4*168, self.split).eligible.all())

    def test_future_targets_never_enter_predictor_input(self):
        history, future = origin_inputs(self.grid, self.split)
        changed = self.grid.copy()
        changed.loc[changed.index[self.split:], "pm2_5"] = -1e9
        h2, f2 = origin_inputs(changed, self.split)
        pd.testing.assert_frame_equal(history, h2)
        pd.testing.assert_frame_equal(future, f2)
        self.assertNotIn("pm2_5", future.columns)
        self.assertLess(history.index.max(), future.index.min())

    def test_scaling_and_clipping_ignore_future_values(self):
        cfg = configuration()
        history, future = origin_inputs(self.grid, self.split)
        scaler, bounds = fit_input_scaler(history, cfg["selected_features"], clip=True)
        transformed = transform_inputs(history, cfg["selected_features"], scaler, bounds)
        np.testing.assert_array_equal(transformed.pm2_5.values, history.pm2_5.values)
        changed = self.grid.copy()
        changed.loc[changed.index[self.split:], cfg["selected_features"]] = 1e12
        h2, _ = origin_inputs(changed, self.split)
        s2, b2 = fit_input_scaler(h2, cfg["selected_features"], clip=True)
        np.testing.assert_array_equal(scaler.mean_, s2.mean_)
        pd.testing.assert_series_equal(bounds[0], b2[0])

    def test_raw_forecast_extracts_one_origin_and_all_leads(self):
        start = pd.Timestamp("2025-01-01")
        raw = pd.DataFrame({"ds": [start-pd.Timedelta(hours=1), start],
                            **{f"step{i}": [-99, i+1] for i in range(168)}})
        extracted = extract_raw_forecast(raw, start, 168)
        np.testing.assert_array_equal(extracted.values, np.arange(1, 169))
        self.assertEqual(extracted.index[-1], start+pd.Timedelta(hours=167))

    def test_duplicate_origins_and_nonfinite_predictions_are_errors(self):
        start = pd.Timestamp("2025-01-01")
        with self.assertRaises(ValueError):
            extract_raw_forecast(pd.DataFrame({"ds": [start, start], "step0": [1, 2]}), start, 1)
        with self.assertRaises(ValueError):
            extract_raw_forecast(pd.DataFrame({"ds": [start], "step0": [np.nan]}), start, 1)

    def test_unavailable_pp_covariates_cannot_be_silently_filled(self):
        changed = self.grid.copy()
        changed.loc[changed.index[self.split], "no"] = np.nan
        with self.assertRaises(ValueError):
            origin_inputs(changed, self.split)

    def test_bias_is_applied_before_current_outcomes_update_it(self):
        first, bias = apply_bias([10, 10], [30, 30], 0, .3)
        np.testing.assert_array_equal(first, [10, 10])
        self.assertEqual(bias, 6)
        second, _ = apply_bias([10, 10], [999, 999], bias, .3)
        np.testing.assert_array_equal(second, [16, 16])
        previous_week, _ = apply_bias([10], [11], 20, 1)
        np.testing.assert_array_equal(previous_week, [30])

    def test_persistence_repeats_history_only(self):
        history = pd.DataFrame({"pm2_5": np.arange(168)})
        np.testing.assert_array_equal(persistence(history, 168, 168), np.arange(168))
        np.testing.assert_array_equal(persistence(history, 168, 24), np.tile(np.arange(144, 168), 7))
        np.testing.assert_array_equal(persistence(history, 168, 1), np.repeat(167, 168))

    def test_neural_training_segments_never_bridge_or_fill_gaps(self):
        frame = pd.DataFrame({"pm2_5": np.arange(800, dtype=float), "no": np.arange(800, dtype=float)},
                             index=pd.date_range("2024-01-01", periods=800, freq="h", name="datetime"))
        frame.iloc[350:400] = np.nan
        episodes, records = neural_training_segments(frame, ["no"])
        self.assertEqual(episodes.ID.nunique(), 2)
        self.assertEqual(sum(r["training_samples"] for r in records), (350-335)+(400-335))
        self.assertFalse(episodes[["y", "no"]].isna().any().any())
        self.assertFalse(pd.to_datetime(episodes.ds).isin(frame.index[350:400]).any())
        for _, group in episodes.groupby("ID"):
            self.assertTrue((pd.to_datetime(group.ds).diff().dropna()==pd.Timedelta(hours=1)).all())


if __name__ == "__main__":
    unittest.main()
