"""The browser boundary: read a snapshot, check its shape, prepare display data.

This module has no Streamlit dependency and NEVER starts sensor acquisition.
V3 and V4 are the small reader/presentation exercises. Other helpers are supplied.
"""
from datetime import datetime, timezone
import json
from pathlib import Path

from records import UNITS
from trend_analysis import finite_number, instant

MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024


def validate_snapshot(document: dict) -> dict:
    """WORKED: check the fields used by the page; allow additional metadata.

Reject inconsistent counts or curve lengths rather than drawing a misleading
plot. This checks the interface, not whether the publisher's arithmetic is right.
"""
    try:
        series, points, summary = (document[k] for k in ("series", "points", "summary"))
        if not all(isinstance(series[k], str) and series[k].strip()
                   for k in ("room", "sensor_id", "metric", "unit")):
            raise ValueError("The series identity must contain non-empty text.")
        if UNITS.get(series["metric"]) != series["unit"]:
            raise ValueError("Unsupported metric/unit pair.")
        if not isinstance(points, list):
            raise ValueError("points must be an array.")
        times = []
        for point in points:
            times.append(instant(point["time"]))
            if not finite_number(point["value"]):
                raise ValueError("Point values must be finite numbers.")
        if times != sorted(times):
            raise ValueError("Snapshot points must be ordered by time.")
        count = summary["count"]
        if isinstance(count, bool) or not isinstance(count, int) or count != len(points):
            raise ValueError("Summary count must equal the number of displayed points.")
        for name in ("mean", "minimum", "maximum", "median", "sample_sd"):
            value = summary[name]
            if value is not None and not finite_number(value):
                raise ValueError(f"Invalid summary field: {name}.")
        if document.get("status") not in {"running", "completed", "interrupted", "failed"}:
            raise ValueError("Unrecognised recorded run status.")
        if document.get("source_mode", "simulation") not in {"files", "simulation", "demo"}:
            raise ValueError("Unrecognised source mode.")
        for name in ("published_at", "started_at"):
            if document.get(name) is not None:
                instant(document[name])
        interval = document.get("expected_interval_seconds")
        if interval is not None and (not finite_number(interval) or interval <= 0):
            raise ValueError("The expected interval must be positive.")
        analysis = document.get("analysis")
        if analysis is not None:
            size = analysis["moving_average_samples"]
            if isinstance(size, bool) or not isinstance(size, int) or size < 1:
                raise ValueError("Invalid moving-average sample count.")
            for curve in (analysis["moving_average"], analysis["trend"]["fitted_values"]):
                if not isinstance(curve, list) or len(curve) != len(points):
                    raise ValueError("Analysis curves must align with displayed points.")
                if not all(v is None or finite_number(v) for v in curve):
                    raise ValueError("Analysis curves must contain finite values or null.")
            for name in ("slope_per_minute", "value_at_start"):
                v = analysis["trend"][name]
                if v is not None and not finite_number(v):
                    raise ValueError("Invalid linear-trend result.")
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Not a dashboard snapshot: required fields are missing or malformed.") from error
    return document


def read_snapshot(path: Path) -> dict:
    """SOLUTION V3: read ONE JSON document, then validate it. Do not cache the file.

Read at most MAX_SNAPSHOT_BYTES + 1 bytes; reject an oversized file. The caller
handles missing/invalid files and retains the last good view. Do not return {} on
failure: that would hide an error. Do not modify or write the source file.
"""
    with Path(path).open("rb") as stream:
        content = stream.read(MAX_SNAPSHOT_BYTES + 1)
    if len(content) > MAX_SNAPSHOT_BYTES:
        raise ValueError("Snapshot too large. Select latest.json, not raw.jsonl.")
    return validate_snapshot(json.loads(content.decode("utf-8")))


def chart_columns(snapshot: dict) -> dict:
    """SOLUTION V4: arrange existing results into equal-length plotting columns.

Convert timestamp strings to aware UTC datetimes. Always include the measured
values. Add moving-average and fitted-trend columns only when analysis exists.
Do not calculate statistics again, change the snapshot, or invent timestamps.
"""
    points = snapshot["points"]
    columns = {"Time (UTC)": [instant(p["time"]) for p in points],
               "Measurement": [p["value"] for p in points]}
    analysis = snapshot.get("analysis")
    if analysis is not None:
        columns["Moving average"] = list(analysis["moving_average"])
        columns["Linear trend"] = list(analysis["trend"]["fitted_values"])
    return columns


def freshness(snapshot: dict, now: datetime) -> tuple[str, str]:
    """WORKED: describe measurement age, not an invented collector heartbeat.

Completed file results are historical, not broken live feeds. A saved 'running'
status alone is never proof that the collector is still alive.
"""
    status = snapshot["status"]
    if status == "failed":
        return "error", "Collector reported a failure. These are the last saved results."
    if snapshot.get("source_mode") in {"files", "demo"}:
        return "info", "Offline result: historical timestamps are expected."
    if status != "running":
        return "info", f"Acquisition {status}. This is the final saved window."
    points = snapshot["points"]
    stamp = points[-1]["time"] if points else snapshot.get("started_at", snapshot.get("published_at"))
    if stamp is None:
        return "warning", "Running is the last saved status; data age is unavailable."
    age = (now.astimezone(timezone.utc) - instant(stamp)).total_seconds()
    if age < -2:
        return "warning", "Timestamp is in the future. Check the computer clocks."
    threshold = max(5.0, 3.0 * (snapshot.get("expected_interval_seconds") or 5.0))
    if age > threshold:
        return "warning", f"Stale data: no selected measurement for {age:.1f} s (limit {threshold:g} s)."
    if not points:
        return "info", "Waiting for the first selected measurement."
    return "success", f"Recent measurement: {max(age, 0):.1f} s old. Saved status: running."
