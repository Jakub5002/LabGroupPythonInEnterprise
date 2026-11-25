# Changes relative to room_sensor_solved

The input is the actual latest `room_sensor_solved.zip` supplied in this conversation.
This is an extension of its finite solution, not a fresh unrelated example.

All original Python modules except `run.py`, original checks, datasets, and the
original config/example.json are retained byte-for-byte. The old run.py numerical
workflow is moved into `file_workflow.run_files`; the new entry point dispatches
on mode. Existing `run_finite.py` remains unchanged.

New source modules: `simulation.py`, `streaming.py`, `recording.py`,
`run_configuration.py`, `run_stream.py`, and the extracted `file_workflow.py`.
New config examples: files, quick simulation, ten five-second observations, and
continuous multi-channel simulation. No manifest or third-party requirement file
has been added.

The student and reference versions differ only in the six G-task function bodies,
edition-specific README/validation text, and the reference solution guide. Existing
finite tasks are solved in BOTH. Supplied scheduler, configuration, orchestration,
data, and checks are the same.

The previous README, validation report, and generator planning note are retained
with PREVIOUS-prefixed filenames. Other earlier guides still describe the previous
finite-data assignment; use the new docs/ guides for this iteration.

## Compact handouts

`docs/01_START_HERE.md` and `GENERATOR_SOLUTIONS.md` are now companion student-facing
handouts for a single meeting. Both editions include both handouts. The README
points to them first; longer guides remain optional reference. This update changes
only Markdown documentation: Python code, exercises, configuration, data, and
checks are unchanged from this edition's original generator archive.
