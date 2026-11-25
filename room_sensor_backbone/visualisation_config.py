"""Two optional settings, kept separate from the previous configuration exercise."""
from copy import deepcopy

DEFAULTS = {"moving_average_samples": 5, "file_window_size": 300}


def extract_visualisation(raw: dict) -> tuple[dict, dict]:
    """WORKED: remove our optional section before validating the old schemas.

Old configuration files still work. Partial overrides are allowed; spelling
mistakes and impractically large display settings are rejected before I/O.
"""
    legacy = deepcopy(raw)
    supplied = legacy.pop("visualisation", {})
    if not isinstance(supplied, dict) or set(supplied) - set(DEFAULTS):
        raise ValueError("visualisation accepts moving_average_samples and file_window_size.")
    settings = {**DEFAULTS, **supplied}
    for key, value in settings.items():
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 10000:
            raise ValueError(f"visualisation.{key} must be an integer from 1 to 10000.")
    return legacy, settings


def file_snapshot_path(config: dict):
    """WORKED: a summary named summary.json has a neighbour summary.latest.json."""
    summary = config["output"]["summary_path"]
    return summary.with_name(summary.stem + ".latest.json")
