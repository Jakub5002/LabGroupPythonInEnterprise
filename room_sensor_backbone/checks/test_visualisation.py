"""Small checks for V1–V4 and the new snapshot interface (standard library only).

A skip means a student placeholder was reached. All previous exercises remain
solved in this iteration. No browser or Streamlit installation is required here.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from functools import wraps
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from analysis import extended_summary
from dashboard_support import chart_columns, freshness, read_snapshot, validate_snapshot
from file_workflow import run_files
from recording import write_snapshot
from run_configuration import load_run_config
from trend_analysis import add_trends, linear_trend, moving_average
from visualisation_config import extract_visualisation, file_snapshot_path

ROOT = Path(__file__).resolve().parents[1]
T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def points():
    """An irregularly spaced straight line: 10 units at t=0; slope 2 units/min."""
    return [{"time": (T0 + timedelta(seconds=s)).isoformat(), "value": y}
            for s, y in [(0, 10.0), (60, 12.0), (180, 16.0)]]


def snapshot():
    """A small valid document, independent of the new numerical task functions."""
    return {
        "series": {"room": "lab", "sensor_id": "s1", "metric": "temperature", "unit": "C"},
        "points": points(), "summary": extended_summary([10.0, 12.0, 16.0]),
        "status": "running", "source_mode": "simulation",
        "expected_interval_seconds": 5.0, "started_at": T0.isoformat(),
        "published_at": (T0 + timedelta(seconds=180)).isoformat(),
    }


def exercise(function):
    @wraps(function)
    def checked(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except NotImplementedError as error:
            self.skipTest(str(error))
    return checked


class VisualisationTasks(unittest.TestCase):
    @exercise
    def test_V1_trailing_means_and_warmup(self):
        self.assertEqual(moving_average([10, 20, 30, 40], 3), [10, 15, 20, 30])

    @exercise
    def test_V1_empty_identity_and_long_window(self):
        self.assertEqual(moving_average([], 3), [])
        self.assertEqual(moving_average([1, 5], 1), [1, 5])
        self.assertEqual(moving_average([1, 5], 100), [1, 3])

    @exercise
    def test_V1_does_not_modify_input(self):
        values = [1, 4, 8]; before = values.copy()
        moving_average(values, 2)
        self.assertEqual(values, before)

    @exercise
    def test_V1_rejects_bad_capacity_and_nonfinite_values(self):
        moving_average([], 1)  # Probe outside subTest so a TODO becomes one skip.
        for size in (0, -1, True, 1.2):
            with self.subTest(size=size), self.assertRaises(ValueError):
                moving_average([1], size)
        for value in (True, "3", float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                moving_average([value], 2)

    @exercise
    def test_V2_irregular_spacing_is_not_an_index_fit(self):
        result = linear_trend(points())
        self.assertAlmostEqual(result["slope_per_minute"], 2.0)
        self.assertAlmostEqual(result["value_at_start"], 10.0)
        self.assertEqual(result["fitted_values"], [10.0, 12.0, 16.0])

    @exercise
    def test_V2_empty_singleton_and_repeated_instant(self):
        self.assertIsNone(linear_trend([])["slope_per_minute"])
        self.assertEqual(linear_trend(points()[:1])["fitted_values"], [None])
        same = [points()[0], {**points()[0], "value": 30}]
        self.assertIsNone(linear_trend(same)["slope_per_minute"])

    @exercise
    def test_V2_constant_series_is_zero_not_undefined(self):
        result = linear_trend([{**p, "value": 9} for p in points()])
        self.assertEqual(result["slope_per_minute"], 0)
        self.assertEqual(result["fitted_values"], [9, 9, 9])

    @exercise
    def test_V2_timezone_offsets_and_nonmutation(self):
        data = points(); data[0]["time"] = "2026-01-01T01:00:00+01:00"
        before = deepcopy(data)
        self.assertAlmostEqual(linear_trend(data)["slope_per_minute"], 2)
        self.assertEqual(data, before)

    @exercise
    def test_V2_rejects_naive_times_and_bad_values(self):
        linear_trend([])
        with self.assertRaises(ValueError):
            linear_trend([{"time": "2026-01-01T00:00:00", "value": 2}])
        with self.assertRaises(ValueError):
            linear_trend([{**points()[0], "value": float("nan")}])

    @exercise
    def test_V3_reads_without_changing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "latest.json"
            text = json.dumps(snapshot()); path.write_text(text, encoding="utf-8")
            self.assertEqual(read_snapshot(path), snapshot())
            self.assertEqual(path.read_text(encoding="utf-8"), text)

    @exercise
    def test_V3_reopens_file_instead_of_caching_previous_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "latest.json"
            write_snapshot(path, snapshot()); first = read_snapshot(path)
            second = snapshot(); second["status"] = "completed"
            write_snapshot(path, second)
            self.assertEqual(read_snapshot(path)["status"], "completed")
            self.assertEqual(first["status"], "running")

    @exercise
    def test_V3_missing_invalid_and_oversized_files_raise(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "latest.json"
            path.write_text(json.dumps(snapshot()), encoding="utf-8")
            read_snapshot(path)
            path.unlink()
            with self.assertRaises(OSError): read_snapshot(path)
            path.write_text("{invalid", encoding="utf-8")
            with self.assertRaises(ValueError): read_snapshot(path)
            path.write_text(json.dumps(snapshot()), encoding="utf-8")
            with patch("dashboard_support.MAX_SNAPSHOT_BYTES", 4):
                with self.assertRaisesRegex(ValueError, "too large"): read_snapshot(path)

    @exercise
    def test_V3_calls_schema_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "latest.json"
            path.write_text(json.dumps(snapshot()), encoding="utf-8"); read_snapshot(path)
            bad = snapshot(); bad["summary"]["count"] = 999
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError): read_snapshot(path)

    @exercise
    def test_V4_raw_columns_have_real_datetimes(self):
        result = chart_columns(snapshot())
        self.assertEqual(list(result), ["Time (UTC)", "Measurement"])
        self.assertEqual(result["Measurement"], [10, 12, 16])
        self.assertEqual(result["Time (UTC)"][0], T0)
        self.assertEqual((result["Time (UTC)"][2] - result["Time (UTC)"][1]).total_seconds(), 120)

    @exercise
    def test_V4_copies_published_curves_without_recalculating(self):
        data = snapshot()
        data["analysis"] = {"moving_average": [1, 2, 3],
                            "trend": {"fitted_values": [4, 5, 6]}}
        before = deepcopy(data)
        result = chart_columns(data)
        self.assertEqual(result["Moving average"], [1, 2, 3])
        result["Moving average"][0] = 999
        self.assertEqual(data, before)

    @exercise
    def test_V4_empty_input_produces_empty_columns(self):
        data = snapshot(); data["points"] = []
        self.assertEqual(chart_columns(data), {"Time (UTC)": [], "Measurement": []})


class BoundaryChecks(unittest.TestCase):
    def test_valid_snapshot_and_empty_warmup(self):
        self.assertEqual(validate_snapshot(snapshot()), snapshot())
        empty = snapshot(); empty.update(points=[], summary=extended_summary([]))
        validate_snapshot(empty)

    def test_bad_json_shapes_and_counts_are_rejected(self):
        for bad in ([], {}, None, {**snapshot(), "points": {}},
                    {**snapshot(), "summary": {"count": True}},
                    {**snapshot(), "status": "invented"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError): validate_snapshot(bad)

    def test_unsorted_points_and_nonfinite_values_are_rejected(self):
        for data in (snapshot(), snapshot()):
            data["points"] = list(reversed(data["points"]))
            with self.assertRaises(ValueError): validate_snapshot(data)
        bad = snapshot(); bad["points"][0]["value"] = float("nan")
        with self.assertRaises(ValueError): validate_snapshot(bad)

    def test_wrong_curve_length_is_rejected(self):
        data = snapshot()
        data["analysis"] = {"moving_average_samples": 2, "moving_average": [10],
                            "trend": {"fitted_values": [10, 12, 16],
                                      "slope_per_minute": 2, "value_at_start": 10}}
        with self.assertRaisesRegex(ValueError, "align"): validate_snapshot(data)

    def test_fresh_stale_and_clock_skew(self):
        self.assertEqual(freshness(snapshot(), T0 + timedelta(seconds=181))[0], "success")
        self.assertEqual(freshness(snapshot(), T0 + timedelta(seconds=196))[0], "warning")
        self.assertIn("future", freshness(snapshot(), T0)[1])

    def test_offline_and_finished_runs_are_not_live_outages(self):
        for mode, status in (("files", "completed"), ("simulation", "interrupted"), ("demo", "completed")):
            data = snapshot(); data.update(source_mode=mode, status=status)
            self.assertEqual(freshness(data, T0 + timedelta(days=100))[0], "info")
        failed = snapshot(); failed["status"] = "failed"
        self.assertEqual(freshness(failed, T0)[0], "error")

    def test_empty_live_window_can_be_waiting_or_stale(self):
        data = snapshot(); data.update(points=[], summary=extended_summary([]))
        self.assertIn("Waiting", freshness(data, T0 + timedelta(seconds=2))[1])
        self.assertIn("Stale", freshness(data, T0 + timedelta(seconds=20))[1])

    def test_unfinished_numerical_tasks_are_explicit_not_fabricated(self):
        with patch("trend_analysis.moving_average", side_effect=NotImplementedError("V1")):
            result = add_trends(snapshot(), 5)
        self.assertIsNone(result["analysis"])
        self.assertEqual(result["analysis_note"], "V1")
        self.assertEqual(result["points"], snapshot()["points"])

    def test_real_numerical_errors_are_not_hidden(self):
        with patch("trend_analysis.moving_average", side_effect=ValueError("bad data")):
            with self.assertRaisesRegex(ValueError, "bad data"): add_trends(snapshot(), 5)

    def test_config_defaults_partial_override_and_nonmutation(self):
        raw = {"mode": "files", "visualisation": {"moving_average_samples": 3}}
        before = deepcopy(raw)
        legacy, settings = extract_visualisation(raw)
        self.assertEqual(legacy, {"mode": "files"})
        self.assertEqual(settings, {"moving_average_samples": 3, "file_window_size": 300})
        self.assertEqual(raw, before)

    def test_config_rejects_misspellings_and_bad_sizes(self):
        for supplied in (None, [], {"average": 3}, {"file_window_size": True},
                         {"moving_average_samples": 0}, {"file_window_size": 10001}):
            with self.subTest(supplied=supplied), self.assertRaises(ValueError):
                extract_visualisation({"visualisation": supplied})

    def test_file_snapshot_path_collisions_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            config = json.loads((ROOT / "config/example.json").read_text())
            config["output"] = {"readings_path": "processed.csv", "summary_path": "summary.json"}
            config["logging"]["path"] = None
            for name in ("summary.latest.json", "summary.latest.json.tmp"):
                config["input"]["path"] = name
                path.write_text(json.dumps(config), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "collision"): load_run_config(path)
                self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_finite_snapshot_is_sorted_bounded_and_matches_its_points(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            config = json.loads((ROOT / "config/example.json").read_text())
            config["input"]["path"] = str(ROOT / "data/readings.csv")
            config["output"] = {"readings_path": "calibrated.csv", "summary_path": "summary.json"}
            config["logging"]["path"] = None
            config["visualisation"] = {"file_window_size": 3}
            path.write_text(json.dumps(config), encoding="utf-8")
            loaded = load_run_config(path)
            with patch("sys.stdout", new_callable=io.StringIO): run_files(loaded)
            view = validate_snapshot(json.loads(file_snapshot_path(loaded).read_text()))
            report = json.loads((path.parent / "summary.json").read_text())
            self.assertEqual(report["summary"]["count"], 6)
            self.assertEqual(view["summary"]["count"], 3)
            self.assertEqual(view["selected_records"], 6)
            self.assertEqual(view["source_mode"], "files")
            self.assertEqual(view["summary"], extended_summary([p["value"] for p in view["points"]]))


if __name__ == "__main__":
    unittest.main()
