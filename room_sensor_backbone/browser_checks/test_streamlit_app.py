"""Optional real Streamlit AppTest checks. These do not replace a browser test.

Install requirements-dashboard.txt first. Run from the project folder with:
python -m unittest discover -s browser_checks -p 'test_*.py' -v
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None


@unittest.skipUnless(HAS_STREAMLIT, "Streamlit is not installed; dashboard-runtime checks were not run.")
class DashboardAppTests(unittest.TestCase):
    def setUp(self):
        from dashboard_support import chart_columns, read_snapshot
        try:
            chart_columns(read_snapshot(ROOT / "data/dashboard_demo.json"))
        except NotImplementedError as error:
            self.skipTest(str(error))
        from streamlit.testing.v1 import AppTest
        self.app = AppTest.from_file(str(ROOT / "dashboard.py"), default_timeout=15)

    def test_demo_draws_metrics_without_an_exception(self):
        app = self.app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.metric), 4)
        self.assertEqual(app.metric[2].value, "60")

    def test_pause_keeps_loaded_view(self):
        app = self.app.run()
        values = [m.value for m in app.metric]
        app.checkbox(key="paused").check().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([m.value for m in app.metric], values)
        self.assertTrue(any("paused" in text.value.lower() for text in app.info))

    def test_display_options_do_not_change_statistical_values(self):
        app = self.app.run()
        values = [m.value for m in app.metric]
        app.checkbox(key="show_average").uncheck().run()
        app.checkbox(key="show_trend").uncheck().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([m.value for m in app.metric], values)

    def test_missing_file_is_a_warning_not_a_crash(self):
        app = self.app.run()
        app.selectbox(key="snapshot_choice").select("Custom path").run()
        with tempfile.TemporaryDirectory() as directory:
            app.text_input(key="snapshot_path").input(str(Path(directory) / "absent.json")).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(len(app.warning))


if __name__ == "__main__":
    unittest.main()
