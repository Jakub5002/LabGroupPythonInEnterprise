# Room sensors — a read-only browser dashboard

**Solved reference · visualisation iteration**

Your collector is still an ordinary Python program. A second program displays
its saved results in a browser. Closing, refreshing or pausing the browser does
not stop collection or change the sensor sampling interval.

```text
sensors → raw archive → select/calibrate → bounded window → statistics/trends
                                                        ↓
                                                   latest.json
                                                        ↓
                                              Streamlit → browser
```

## Read these two handouts first

**VISUALISATION_START_HERE.md** and **VISUALISATION_SOLUTIONS.md** are matching,
short guides for the same meeting. Earlier guides are retained as optional
reference; they describe their original stages.

This is still a folder, not an installable package: no pyproject.toml, manifest,
Git setup, database, JavaScript, API server or background worker framework.

## 1. Try the offline example

Use a **Python 3.11+ environment** for the dashboard. The collector has no new
third-party dependencies. Check which interpreter your terminal uses:

```bash
python --version
python -m pip install -r requirements-dashboard.txt
python -m streamlit run dashboard.py --server.address=127.0.0.1
```

Open the local URL printed by Streamlit (normally http://127.0.0.1:8501).
The default is a labelled, bundled **offline demo**, not a running simulation.
No sensor process is needed to inspect it.

## 2. Watch a live recording

In another terminal, inside the same project folder:

```bash
python run.py config/dashboard_live.json
```

The selected temperature channel samples once per second; other channels retain
their own intervals. In the dashboard, click **Rescan session folders** and choose
the new `output/sessions/.../latest.json` entry. The collector also prints a
complete dashboard command with an explicit path. Stop collection with Ctrl+C.

The existing five-second example remains unchanged:

```bash
python run.py config/simulation_10_readings.json
```

## 3. View the finite file workflow

```bash
python run.py
```

Select `output/summary.latest.json` after rescanning. The CSV and full summary are
still produced as before; the new snapshot holds a bounded display window.
Recordings can also be reanalysed with their generated `offline_config.json`.
Paste the printed snapshot path using **Custom path** to view that offline result.

## Where to look

| File | Role |
|---|---|
| `trend_analysis.py` | V1 moving average and V2 timestamp-based linear trend. |
| `dashboard_support.py` | V3 snapshot reader and V4 plotting columns; supplied validation/status helpers. |
| `dashboard.py` | Supplied Streamlit layout, controls, refresh and last-good-view handling. |
| `visualisation_config.py` | Optional settings; old configuration files still work. |
| `run_stream.py`, `file_workflow.py` | Existing collectors now publish analysis and view metadata. |

Use `CHECKS_VISUALISATION.md` for test commands and `VALIDATION.md` for what was
actually executed. Use a virtual environment if you do not want to add Streamlit
to your existing one. Separate collector/dashboard environments may share files.

**Scope:** one selected series, two local processes, one writer per session.
The dashboard is not an operating-system service and has no authentication.
Keep it bound to localhost. Raw archives grow; display history is bounded.
