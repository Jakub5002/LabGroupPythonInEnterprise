# Start here — your sensor data in a browser

**Handout 1 of 2 · Keep VISUALISATION_SOLUTIONS.md beside this guide.**

## 1. Follow the boundary

You are adding a **reader of results**, not another sensor collector:

```text
collector → raw.jsonl + latest.json → dashboard → browser
```

The collector records every raw measurement, then selects and calibrates one
series. It calculates statistics and trends from a bounded window and publishes
one complete JSON snapshot. The dashboard only reads that snapshot. Never start
a generator inside dashboard code: interface reruns must not acquire new data.

All earlier tasks are solved. In the student folder, only V1–V4 are unfinished.
The reference folder contains the completed versions of the same four functions.

## 2. Your four functions

| Task | File / function | Required result |
|---|---|---|
| V1 | `trend_analysis.py`: `moving_average` | One trailing mean per value; use partial windows during warm-up. |
| V2 | `trend_analysis.py`: `linear_trend` | Slope in units/minute and fitted values, using recorded times. |
| V3 | `dashboard_support.py`: `read_snapshot` | Read one JSON file and call the supplied validator. |
| V4 | `dashboard_support.py`: `chart_columns` | Convert timestamps and arrange published curves into equal-length columns. |

For the quickest visible result, complete **V3 and V4** and view the demo first.
Then complete V1 and V2 to add your own analysis to new collector snapshots.
The supplied layout, snapshot writer, validation and status handling are not
additional exercises. Numerical placeholders are reported explicitly; raw
recording still works. A slope is not a prediction or a significance claim.

## 3. Open the browser

Use a Python 3.11+ environment. From the project folder:

```bash
python -m pip install -r requirements-dashboard.txt
python -m streamlit run dashboard.py --server.address=127.0.0.1
```

Open the local address printed in the terminal. The default source is an
**offline synthetic demo**, so its old dates are intentional. The student page
identifies an unfinished V3/V4 instead of showing a long traceback.

Now start collection in a second terminal:

```bash
python run.py config/dashboard_live.json
```

Click **Rescan session folders** and select the new session's `latest.json`.
A one-second browser refresh does not create a measurement. Pause display
updates, then resume: the archive should have continued growing. Close the
browser and reopen it; the collector should still be running. Stop it with Ctrl+C.

## 4. Adjust the right setting

Sensor timing remains `simulation.sensors[*].interval_seconds`; retained live
history remains `stream.window_size`. Add this optional section to a config:

```json
"visualisation": {"moving_average_samples": 5, "file_window_size": 300}
```

Five means **samples**, not seconds. File-window size limits offline display,
not the full saved analysis. The displayed moving average is recalculated within
the visible window, with warm-up again at its left edge. Change these settings
in the collector config and restart it; browser checkboxes only hide/show curves.

## 5. Check your work

```bash
python -m unittest discover -s checks -p "test_visualisation.py" -v
```

Append `-k V3` to focus on one task. **Skipped means unfinished**, not passed.
Aim for zero skips after V1–V4. Run all checks with `-p "*.py"`.

To view finite file results, run `python run.py` and select
`output/summary.latest.json`. For a finished recording, run its printed offline
command and paste the resulting snapshot path. The live window and whole-file
summary can differ because they describe different samples.

**Done when:** timestamps are on the x-axis, plotted points and statistics agree,
empty data does not crash the page, and stopping collection is distinguishable
from merely pausing the display.
