"""Pure selection and finite-data analysis. There is no file or logging code here.

An Iterable can be a list or an iterator. These functions still produce finite
results: accepting an Iterable does NOT make whole-data analysis safe on infinity.
"""
from collections.abc import Iterable
from statistics import fmean, stdev, median


def select_series(readings: Iterable[dict], room: str, sensor_id: str,
                  metric: str) -> list[dict]:
    """WORKED EXAMPLE: select exactly one room/sensor/metric combination."""
    # We create a new list, but do not copy or modify the contained dictionaries.
    return [r for r in readings
            if (r["room"], r["sensor_id"], r["metric"]) == (room, sensor_id, metric)]


def basic_summary(values: list[float]) -> dict:
    """WORKED EXAMPLE: count, mean, minimum and maximum for one finite series."""
    # An empty selection is not a collection of zero-valued measurements.
    if not values:
        return {"count": 0, "mean": None, "minimum": None, "maximum": None}
    return {"count": len(values), "mean": fmean(values),
            "minimum": min(values), "maximum": max(values)}



def explore_data(readings: list[dict]) -> dict:
    """YOUR TASK E1: describe what is present, before interpreting the values.

    Return record_count, sorted rooms, sorted sensor_ids, sorted metrics,
    time_start/time_end (None if empty), and series: a list of dictionaries with
    room, sensor_id, metric, unit, count. Sort series by room/sensor_id/metric.
    Use actual times, not row positions; input records need not be time-sorted.
    """
    # Count each (room, sensor_id, metric) separately. Do not calculate a mixed-unit mean.
    rooms = set()
    sensor_ids = set()
    metrics = set()
    series = {}

    times = []

    for reading in readings:
        room = reading["room"]
        sensor_id = reading["sensor_id"]
        metric = reading["metric"]
        unit = reading["unit"]
        time = reading["time"]

        rooms.add(room)
        sensor_ids.add(sensor_id)
        metrics.add(metric)
        times.append(time)

        key = (room, sensor_id, metric)

        if key not in series:
            series[key] = {
                "room": room,
                "sensor_id": sensor_id,
                "metric": metric,
                "unit": unit,
                "count": 0
            }

        series[key]["count"] += 1

    result = {
        "record_count": len(readings),
        "rooms": sorted(rooms),
        "sensor_ids": sorted(sensor_ids),
        "metrics": sorted(metrics),
        "time_start": min(times) if times else None,
        "time_end": max(times) if times else None,
        "series": sorted(series.values(), key=lambda x: (x["room"], x["sensor_id"], x["metric"]))
    }

    return result

def extended_summary(values: list[float]) -> dict:
    """Create a summary basen pn basic_summary with an addition of median and standard deviation"""
    if values is None:
        return None
    if len(values) == 0:
        return {"count": 0, "mean": None, "minimum": None, "maximum": None, "median": None, "sample_sd": None}
    extended = basic_summary(values)
    extended.update({"median": median(values) if len(values)>=1 else None, "sample_sd": stdev(values) if len(values)>=2 else None})
    return extended

def summarise_by_series(readings: list[dict]) -> list[dict]:
    """YOUR TASK S2: return one independently calculated summary per series.

    Each output dictionary has room, sensor_id, metric, unit, and summary.
    summary is the result of extended_summary for that group's values.
    Sort the output by room/sensor_id/metric. Empty input returns [].
    """
    # Group by the complete three-part key, then analyse each group separately.
    if readings is None:
        return []

    temp_dict = {}

    for reading in readings:
        key = (reading["room"], reading["sensor_id"], reading["metric"])
        temp_dict.setdefault(key, {}).setdefault(reading["unit"],[]).append(reading["value"])

    summarised_readings = []

    for key in sorted(temp_dict):
        unit = list(temp_dict[key].keys())[0] # get first unit (others not supported)
        values = temp_dict[key][unit]
        summary = extended_summary(values)

        room, sensor_id, metric = key
        summarised_readings.append(
            {
                "room" : room,
                "sensor_id" : sensor_id,
                "metric" : metric,
                "unit" : unit,
                "summary" : summary
            }
        )

    return summarised_readings
    
