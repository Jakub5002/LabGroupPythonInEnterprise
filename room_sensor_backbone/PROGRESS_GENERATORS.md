# Your generator-extension notes

Name / team: Jakub Wołczyński, Oleksandra Utkina, Hubert Zagała, Paweł Wdowik, Łukasz Szymańczyk 

Python version used:

## Task progress

| Task | Implemented? | Evidence / test or observation |
|---|---|---|
| G1: infinite numerical source | YES | `sensor_values` uses a private `random.Random(seed)`, yields Gaussian values forever, checks `isfinite` before clipping, and stores no history. Same seed gives the same sequence; zero noise gives exactly the mean. Tests: *(paste the G1 test names and results)* |
| G2: pacing | YES | `wait_until` computes `deadline - clock()`, sleeps while the remainder is positive, and rechecks the clock. It never busy-waits or requests a negative sleep. Tests: `test_first_measurement_is_at_5_not_0`, `test_independent_intervals_and_stable_ties`, `test_no_unused_eleventh_measurement` and `test_slow_consumer_does_not_create_synthetic_backlog` were skipped before the fix. Rerun and record that they pass. |
| G3: lazy recording reader | |  |
| G4: lazy selection/calibration | | |
| G5: bounded windows | YES | `rolling_windows` validates a positive integer `size` (rejecting booleans), uses `collections.deque(maxlen=size)` to bound memory, enforces a single `(room, sensor_id, metric, unit)` series, and yields fresh copies of both the window list and each record on every step. |
| G6: continuous recording | YES | Relevant tests: `test_archive_includes_unselected_series_and_limit_is_total`, `test_ctrl_c_flushes_recording_and_final_metadata`, `test_limit_can_end_before_first_selected_record`, `test_storage_failure_is_not_a_success`. Record that they pass once G2 is fixed. |

## Explain in your own words

**What starts and advances a generator?**
Calling the generator function only creates the generator object and runs no code. The body starts on the first `next()` call, for example from a `for` loop. It runs until the next `yield` and pauses there. Every later `next()` resumes it from that point. So the consumer drives it.

**Why do ten readings at a five-second period require fifty seconds here?**
The first reading is due after one interval, not at startup. The readings are due at 5, 10, 15, ... 50 seconds, and `wait_until` really sleeps until each deadline. The tenth reading is at 10 × 5 = 50 s. There is no fast-forward mode.

**Which values does the live mean describe? Which does the offline mean describe?**
The live mean describes only the selected series and only the points currently in the bounded window, at most `window_capacity` of them. The offline mean describes the full raw archive, so it can include more points, and its count can be larger.

**Where is the first side effect in the stream pipeline?**
(*) Generating values and waiting have no lasting effect. The first real side effect is writing a record to storage, which means appending to `raw.jsonl`. In `simulation.py` the closest thing is `parse_record` with the wall-clock timestamp.

**Which data is saved when your live view selects only temperature?**
(*) The raw archive still saves every acquired record, including the unselected series. The selection only decides what goes into `latest.json` and its statistics.

**How do you stop early without leaving the raw file open?**
I stop through the limit or Ctrl+C and let `finally` blocks or a `with` statement run. They close the child generators, flush and close the raw file, and write the final metadata with status `interrupted` or `completed`.

**What can still grow without bound even though the live memory is bounded?**
The raw archive file. The window is capped, but `raw.jsonl` keeps every record, so it grows for as long as the program runs, and faster with more channels.

**What should the future plot do before the first measurement arrives?**
It should handle the empty `points` list as a normal state. It shows empty axes with the title and unit labels, and draws no points, no mean line and no error bars. `null` statistics stay unavailable and are not treated as 0. It also shouldn't crash if the file is missing, and it never asks the generator for a new measurement.


