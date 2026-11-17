from contextlib import closing
from pathlib import Path
from run_configuration import load_run_config
from streaming import iter_jsonl, select_calibrated, rolling_windows, build_snapshot

# Replace YOUR_SESSION with the actual directory printed by your simulation.
settings = Path("output/sessions/YOUR_SESSION/offline_config.json")
config = load_run_config(settings)
last = None
with closing(iter_jsonl(config["input"]["path"])) as raw:
    selected = select_calibrated(raw, config["selection"], config["calibration"])
    for window in rolling_windows(selected, 5):
        last = build_snapshot(window, config["selection"], config["calibration"], 5)
print(last)
