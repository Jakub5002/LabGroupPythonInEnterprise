"""Pure calibration: coefficients and measurements in, new values out.

No function here opens a file, reads configuration, prints, or configures logging.
The coefficients correct values within one unit; this is not unit conversion.
"""
from math import isfinite


def calibrate_value(value: float, scale: float = 1.0, offset: float = 0.0) -> float:
    """Apply y = scale * x + offset using supplied, not fitted, coefficients."""
    result = scale * value + offset
    if not isfinite(result):
        raise ValueError("Calibration produced a non-finite value.")
    return result


def calibrate_reading(reading: dict, scale: float, offset: float) -> dict:
    """YOUR TASK C1: return a new record with only its value changed.

    Call calibrate_value. Keep time, room, sensor_id, metric, and unit unchanged.
    The original dictionary must remain untouched; never calibrate it in place.
    """
    # Copy the record, calculate the new value, and return your copy.
    new_record = reading.copy()
    new_record["value"] = calibrate_value(reading["value"], scale=scale, offset=offset)
    return new_record
    raise NotImplementedError("C1: implement record calibration in calibration.py")
