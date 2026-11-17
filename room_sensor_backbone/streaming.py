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
    """TASK G3: yield one parsed row at a time from a FINISHED JSONL recording.

Ignore blank lines; report the line number on invalid input. Exhaust or close
this generator to close its file. This is a replay reader, not a file-tail service.
"""
    with path.open('r') as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            if len(line) == 0:
                continue
            try:
                record = json.loads(line)
            except ValueError as err:
                raise ValueError(f"{path.name}: line {line_num}: {err}") from err
            yield record
            


def select_calibrated(readings: Iterable[dict], selection: dict,
                      calibration: dict) -> Iterator[dict]:
    """TASK G4: lazily filter ONE series, then yield a fresh corrected copy.

Do not use the older select_series: it builds a complete list. Never apply this
series' calibration coefficients to another metric or station.
"""
    # TODO G4: your implementation begins here.
    # Filter lazily using the complete room/sensor_id/metric identity.
    # For matching records, yield a calibrated new record or an unchanged copy.
    # Reuse calibrate_reading; never materialise the incoming iterable.
    keys = ("room", "sensor_id", "metric")
    wanted = tuple(selection[k] for k in keys)

    calibration = calibration or {}
    scale = calibration.get("scale", 1.0)
    offset = calibration.get("offset", 0.0)
    is_enabled = calibration.get("enabled", True)

    for record in readings:
        if tuple(record.get(k) for k in keys) != wanted:
            continue  # inne serie są odrzucane
        if is_enabled:
            yield calibrate_reading(record, scale=scale, offset=offset)
        else:
            yield record.copy()

def rolling_windows(readings: Iterable[dict], size: int) -> Iterator[list[dict]]:
    """TASK G5: yield a separate snapshot after each selected observation.

Yield partial windows during warm-up. One sample permits a mean but not sample
standard deviation. Do not mix series; do not leak mutable window state.
"""
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("window size must be a positive integer.")

    window: deque[dict] = deque(maxlen=size)
    series_identity: tuple[str, str, str, str] | None = None

    for row in readings:
        current_identity = (
            row["room"],
            row["sensor_id"],
            row["metric"],
            row["unit"],
        )
        if series_identity is None:
            series_identity = current_identity
        elif current_identity != series_identity:
            raise ValueError("rolling_windows accepts records from one series only.")

        window.append(row.copy())
        yield [item.copy() for item in window]


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
