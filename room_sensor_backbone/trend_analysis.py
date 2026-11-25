"""Pure calculations for a finite display window; no files, clocks or UI imports.

V1 and V2 are the new numerical exercises. They receive already calibrated data.
You can test them without a sensor, a browser, or Streamlit.
"""
from collections import deque
from datetime import datetime, timezone
from math import fsum, isfinite
from statistics import fmean


def instant(text: str) -> datetime:
    """WORKED: parse an explicit timezone and normalise it to UTC (also accept Z)."""
    if not isinstance(text, str):
        raise ValueError("A timestamp must be text.")
    value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.utcoffset() is None:
        raise ValueError("A timestamp must include a timezone.")
    return value.astimezone(timezone.utc)


def finite_number(value) -> bool:
    """WORKED: reject booleans, non-numbers, NaN and infinity at a data boundary."""
    try:
        return not isinstance(value, bool) and isinstance(value, (int, float)) and isfinite(value)
    except OverflowError:
        return False


def moving_average(values: list[float], samples: int) -> list[float]:
    """SOLUTION V1: one trailing mean per input, using partial windows at the start.

For [10, 20, 30, 40] and samples=3, return [10, 15, 20, 30]. Do not change
values. The input is the finite DISPLAY window, not the unlimited raw stream.
"""
    if isinstance(samples, bool) or not isinstance(samples, int) or samples < 1:
        raise ValueError("Moving-average samples must be a positive integer.")
    recent = deque(maxlen=samples)
    result = []
    for value in values:
        if not finite_number(value):
            raise ValueError("Moving-average input must contain finite numbers.")
        recent.append(value)
        result.append(fmean(recent))
    return result


def linear_trend(points: list[dict]) -> dict:
    """SOLUTION V2: ordinary least-squares slope in measurement units per minute.

Use actual elapsed time, NOT the point index. The fitted values correspond to
the input points. With fewer than two distinct times the slope is undefined:
return None and an equally long list of None, not a fabricated zero slope.
"""
    undefined = {"slope_per_minute": None, "value_at_start": None,
                 "fitted_values": [None] * len(points)}
    if not points:
        return undefined
    times = [instant(point["time"]) for point in points]
    values = [point["value"] for point in points]
    if not all(finite_number(value) for value in values):
        raise ValueError("Trend input must contain finite numbers.")
    minutes = [(time - times[0]).total_seconds() / 60.0 for time in times]
    x_mean, y_mean = fmean(minutes), fmean(values)
    denominator = fsum((x - x_mean) ** 2 for x in minutes)
    if denominator == 0:
        return undefined
    slope = fsum((x - x_mean) * (y - y_mean)
                 for x, y in zip(minutes, values)) / denominator
    intercept = y_mean - slope * x_mean
    fitted = [intercept + slope * x for x in minutes]
    if not all(isfinite(value) for value in [slope, intercept] + fitted):
        raise ValueError("Trend calculation exceeded the finite numerical range.")
    return {"slope_per_minute": slope, "value_at_start": intercept,
            "fitted_values": fitted}


def add_trends(snapshot: dict, samples: int) -> dict:
    """WORKED: attach calculations to the SAME points used for window statistics.

The only caught exception denotes an explicit student placeholder. Numerical
errors still fail the collector. Nothing is silently replaced by invented data.
"""
    result = snapshot.copy()
    try:
        average = moving_average([p["value"] for p in snapshot["points"]], samples)
        trend = linear_trend(snapshot["points"])
    except NotImplementedError as error:
        result.update(analysis=None, analysis_note=str(error))
    else:
        result["analysis"] = {"moving_average_samples": samples,
                              "moving_average": average, "trend": trend}
    return result
