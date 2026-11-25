"""A read-only Streamlit page. Start it with `python -m streamlit run dashboard.py`.

Never import or call simulate_sensors here: UI reruns must not own acquisition.
The only retained data is one bounded, last-good snapshot per browser session.
"""
from datetime import datetime, timezone
from pathlib import Path
import sys

import streamlit as st

from dashboard_support import chart_columns, freshness, read_snapshot

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Room sensors", layout="wide")
st.title("Room sensor monitor")
st.caption("Read-only dashboard · one selected measurement series · calculations supplied by the collector")

# A new session appears after a full rerun. Do not silently switch the chosen run.
with st.sidebar:
    st.header("Data and display")
    st.button("Rescan session folders")
    candidates = [ROOT / "data" / "dashboard_demo.json"]
    candidates += sorted((ROOT / "output" / "sessions").glob("*/latest.json"), reverse=True)
    candidates += sorted((ROOT / "output").glob("*.latest.json"))
    supplied_path = sys.argv[1] if len(sys.argv) == 2 else ""
    choice = st.selectbox("Snapshot source", ["Custom path"] + [str(p.relative_to(ROOT)) for p in candidates],
                          index=0 if supplied_path else 1, key="snapshot_choice")
    if choice == "Custom path":
        text = st.text_input("Snapshot path", value=supplied_path, key="snapshot_path")
        path = (ROOT / Path(text).expanduser()).resolve() if text.strip() else None
    else:
        path = (ROOT / choice).resolve()
    st.caption("Relative paths start beside dashboard.py. Custom paths can be absolute.")
    paused = st.checkbox("Pause display updates", key="paused")
    interval = st.selectbox("Refresh interval (seconds)", [1, 2, 5], key="refresh_seconds")
    refresh_once = st.button("Read once now")
    show_average = st.checkbox("Show moving average", value=True, key="show_average")
    show_trend = st.checkbox("Show linear trend", value=True, key="show_trend")
    st.caption("Pause affects this browser only. It does not stop the collector.")

# Changing the source must never show cached data from a different session.
if st.session_state.get("active_path") != str(path):
    st.session_state.active_path = str(path)
    st.session_state.last_good = None
    st.session_state.read_problem = None
if refresh_once:
    st.session_state.read_once = True


def number_text(value, digits=3):
    """Display undefined statistics as a dash, not as a numerical zero."""
    return "—" if value is None else f"{value:.{digits}f}"


@st.fragment(run_every=None if paused else interval)
def display_snapshot():
    """Refresh only the view. Failed reads keep an explicitly labelled old plot."""
    if path is None:
        st.info("Choose a snapshot or paste the path printed by the collector.")
        return
    forced = st.session_state.pop("read_once", False)
    if not paused or forced:
        try:
            st.session_state.last_good = read_snapshot(path)
            st.session_state.read_problem = None
        except NotImplementedError as error:
            st.info(f"Student task: {error}")
            return
        except (OSError, ValueError) as error:
            st.session_state.read_problem = str(error)

    snapshot = st.session_state.last_good
    if paused:
        st.info("Display paused. The collector continues independently. Use 'Read once now' for a single refresh.")
    if st.session_state.read_problem:
        st.warning("Snapshot unavailable; keeping the last valid view. " + st.session_state.read_problem)
    if snapshot is None:
        st.info("No snapshot loaded yet. Start the collector, or select the offline demo.")
        return

    series = snapshot["series"]
    st.subheader(f'{series["room"]} / {series["sensor_id"]} / {series["metric"]}')
    level, message = freshness(snapshot, datetime.now(timezone.utc))
    getattr(st, level)(message)
    st.caption(f"Source: {path}")
    if snapshot.get("analysis_note"):
        st.warning("Trend analysis is unfinished: " + snapshot["analysis_note"])
    if not snapshot["points"]:
        st.info("This snapshot contains no selected measurements yet.")
        return

    summary, unit = snapshot["summary"], series["unit"]
    analysis = snapshot.get("analysis")
    slope = analysis["trend"]["slope_per_minute"] if analysis else None
    cards = st.columns(4)
    cards[0].metric(f"Latest [{unit}]", number_text(snapshot["points"][-1]["value"]))
    cards[1].metric(f"Window mean [{unit}]", number_text(summary["mean"]))
    cards[2].metric("Points in window", str(summary["count"]))
    cards[3].metric(f"Trend [{unit}/min]", number_text(slope, 4))
    st.caption("The slope describes this window; it is not a forecast or a significance test.")

    try:
        columns = chart_columns(snapshot)
    except NotImplementedError as error:
        st.info(f"Student task: {error}")
        return
    curves = ["Measurement"]
    if show_average and "Moving average" in columns:
        curves.append("Moving average")
    if show_trend and "Linear trend" in columns:
        curves.append("Linear trend")
    st.line_chart(columns, x="Time (UTC)", y=curves,
                  x_label="Recorded time", y_label=f'{series["metric"]} [{unit}]', height=370)
    st.caption("Recorded timestamps determine spacing. Hover for exact values; chart timezone display can depend on your browser.")
    st.write(f'Median: {number_text(summary["median"])} {unit} · '
             f'Min–max: {number_text(summary["minimum"])}–{number_text(summary["maximum"])} {unit} · '
             f'Sample SD: {number_text(summary["sample_sd"])} {unit}')
    st.caption(f'Last measurement: {snapshot["points"][-1]["time"]} | '
               f'Raw records at publication: {snapshot.get("records_saved", "unknown")} | '
               f'Selected records: {snapshot.get("selected_records", "unknown")}')
    with st.expander("Window data and snapshot metadata"):
        st.dataframe(columns)
        st.json({key: value for key, value in snapshot.items() if key not in {"points", "analysis"}})


display_snapshot()
