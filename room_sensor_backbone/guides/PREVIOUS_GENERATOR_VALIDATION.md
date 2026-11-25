# Release validation — generator extension (solved)

Verified on 9 November 2026 using **Python 3.13.5 on Linux**, with only the
standard library. This report describes the generator extension; the historical
finite-solution report is retained separately as PREVIOUS_STAGE_VALIDATION.md.

## Clean-extraction check

The archive was extracted into a fresh directory and the complete suite was run:

```bash
python -B -m unittest discover -s checks -p "*.py" -v
```

**118 tests passed, zero skipped.** The complete output is in `validation/test_output.txt`.
The 76 earlier checks remain unchanged. The extension adds 42 checks. A student
placeholder is counted as skipped, not as a correct implementation. The completed
reference has no task-related skips. Both editions' default file entry point,
`run_finite.py`, and explicit `config/files.json` were also run successfully from
`/tmp`, outside the project directory.

A direct attempt to run simulation in the untouched student scaffold exits with
a visible task error, writes no fabricated measurements, and marks its created
session as failed. Because the stream is pulled by its final consumer, G5 is the
first placeholder reached in that full-run experiment.

## Real 10 x 5-second experiment

The completed reference was copied into a separate working directory and run with
`config/simulation_10_readings.json`, from outside that directory. It used actual
sleeping and the actual monotonic clock, not a test substitute.

- Raw records saved: **10**.
- Configured period: **5.0 seconds**; first reading delayed by one full period.
- Measured acquisition elapsed: **50.001688 seconds**.
- Total subprocess wall time, including Python startup and setup: **50.726431 seconds**.
- Exit status: **0**; session status: **completed**.

Machine-readable values are in `validation/real_timing.json`. This is an observation
from this environment, not a performance guarantee for every OS or storage device.
Most unit checks instead use a fake clock so repeated tests do not require a real
fifty-second wait. A short integration check also uses actual sleeping.

## What the new checks cover

The checks exercise private seeded random state, value bounds, delayed first
measurement, independent intervals and stable ties, no eleventh read after a
finite prefix, and the documented slow-consumer policy. They check lazy JSONL
reading, file closure, errors with line numbers, one-pass selection, no raw-input
mutation, warm-up windows, and window bounds over 3,000 records.

They also check incremental visibility before a recording handle closes, optional
fsync invocation, invalid serialisation, snapshot replacement, strict configuration,
path collisions, distinct session directories, and the generated offline config.
Integration tests verify that unselected channels are still recorded, the count
limit applies to all raw readings, an empty selected view is valid, and offline
calibration is applied once. A simulated write failure stops the run and preserves
the earlier completed record. A POSIX SIGINT test checks Ctrl+C-style shutdown,
closed recordings, parseable saved rows, and final interrupted metadata.

## Source preservation and compatibility

All 12 original Python source/test files other than run.py, all five original data
files, and the original config/example.json were compared byte-for-byte with the
latest supplied room_sensor_solved archive and are unchanged. run.py is now the
mode dispatcher; its earlier finite calculation is in file_workflow.py. There are
no packaging manifests, dependency installations, or web/plotting components.

All 20 Python files in each edition were parsed with the Python 3.9 grammar setting.
This does not constitute execution on Python 3.9. Runtime type-hint compatibility
is maintained by avoiding the newer `Path | None` spelling. The final source files
were compared with the clean-extraction tested sources before packaging.

## Explicit limits

Windows and macOS execution, real hardware, GUI interaction, network file systems,
long-duration acquisition, and power-failure recovery were not tested. The SIGINT
integration check is POSIX-specific and is skipped on Windows. Normal application
shutdown uses KeyboardInterrupt; no cross-platform automated signal claim is made.

The source is consumer-driven, not autonomous hardware. Slow processing can delay
measurements; missed slots are not backfilled with invented history. The bounded
memory claim is about fixed configured sources and a bounded selected-series
window, not an exhaustive heap-leak proof. Disk/log growth is unbounded. Ordinary
flush is not a power-loss guarantee, and abrupt termination can leave stale
metadata or an incomplete final JSONL line. The finite offline workflow still
loads its input dataset into memory; the new lazy reader offers a separate bounded
replay route for window-based analysis.
