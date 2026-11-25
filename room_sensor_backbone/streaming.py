"""Lazy finite/infinite processing, followed by bounded snapshots for future plots.

Selection/calibration and snapshot calculations do not open files or consult
clocks. A rolling window is stateful, but it retains only a fixed number of rows.
"""
from collections import deque
import json
from pathlib import Path
from typing import Iterable, Iterator

from analysis import extended_summary
from calibration import calibrate_reading
from records import UNITS, parse_record


def iter_jsonl(path: Path) -> Iterator[dict]:
    """SOLUTION G3: yield one parsed row at a time from a FINISHED JSONL recording.

Ignore blank lines; report the line number on invalid input. Exhaust or close
this generator to close its file. This is a replay reader, not a file-tail service.
"""
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                record = parse_record(json.loads(line))
            except ValueError as error:
                raise ValueError(f"{path}: JSON Lines line {number}: {error}") from error
            yield record


def select_calibrated(readings: Iterable[dict], selection: dict,
                      calibration: dict) -> Iterator[dict]:
    """SOLUTION G4: lazily filter ONE series, then yield a fresh corrected copy.

Do not use the older select_series: it builds a complete list. Never apply this
series' calibration coefficients to another metric or station.
"""
    key = tuple(selection[name] for name in ("room", "sensor_id", "metric"))
    for reading in readings:
        if tuple(reading[name] for name in ("room", "sensor_id", "metric")) != key:
            continue
        if calibration["enabled"]:
            yield calibrate_reading(reading, calibration["scale"], calibration["offset"])
        else:
            yield reading.copy()


def rolling_windows(readings: Iterable[dict], size: int) -> Iterator[list[dict]]:
    """SOLUTION G5: yield a separate snapshot after each selected observation.

Yield partial windows during warm-up. One sample permits a mean but not sample
standard deviation. Do not mix series; do not leak mutable window state.
"""
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("Window size must be a positive integer.")
    window = deque(maxlen=size)
    key = None
    for reading in readings:
        this_key = tuple(reading[name] for name in ("room", "sensor_id", "metric", "unit"))
        if key is not None and this_key != key:
            raise ValueError("A rolling window must contain exactly one series/unit.")
        key = this_key
        window.append(reading.copy())
        # Copies are bounded by size. A consumer cannot corrupt the next snapshot.
        yield [record.copy() for record in window]


def build_snapshot(window: list[dict], selection: dict, calibration: dict,
                   capacity: int) -> dict:
    """WORKED EXAMPLE: give a future plot points and matching statistics together.

Timestamps are preserved exactly; irregular spacing must remain visible. This
function does no plotting or I/O. All statistics describe this window only.
"""
    return {
        "series": {**selection, "unit": UNITS[selection["metric"]]},
        "points": [{"time": row["time"], "value": row["value"]} for row in window],
        "summary": extended_summary([row["value"] for row in window]),
        "window_capacity": capacity,
        "calibration_applied": calibration["enabled"],
        "calibration": calibration.copy(),
    }
