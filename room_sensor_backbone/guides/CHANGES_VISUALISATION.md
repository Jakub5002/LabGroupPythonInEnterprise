# Changes from the solved compact generator folder

Both new versions start from **room_sensor_generators_solved_compact.zip**.
Previous generator tasks are solved in the student version too; the new exercises
are only V1–V4. The student and reference folders differ only in those function
bodies, task labels, and the README/version-specific validation notes.

## Added

- `dashboard.py`: one read-only Streamlit page, separately launched.
- `dashboard_support.py`: read/validate snapshots, prepare columns, describe age.
- `trend_analysis.py`: pure moving average and irregular-time least-squares trend.
- `visualisation_config.py`: two optional validated settings and a derived file path.
- Compact working/solution handouts, test commands, new tests, synthetic demo JSON,
  an optional dashboard requirements file, and `config/dashboard_live.json`.

## Small edits to the existing application

`run_configuration.py` removes/validates the optional visualisation section
before reusing the old schemas. It also guards the new finite snapshot path.
`run_stream.py` adds curves, timestamps and status metadata at publication.
`file_workflow.py` publishes a sorted, bounded snapshot alongside its existing
outputs. `recording.py` carries view settings into the offline configuration.

Other existing Python modules, original tests, and original configurations are
unchanged. Existing summary/calibrated outputs retain their previous meaning.
Old validation and README files are preserved under PREVIOUS_GENERATOR names.

## Snapshot contract

Existing `series`, `points`, `summary`, `calibration`, and `window_capacity` remain.
New `analysis` contains aligned moving-average and linear-trend arrays plus the
slope in units/minute. `source_mode`, `published_at`, `started_at` (live), and
`expected_interval_seconds` (live) support status display. Counters describe the
last publication, not a continuously updated heartbeat.

A file snapshot is named `<summary stem>.latest.json` beside the full summary.
A live session still uses `latest.json`. Each plot and its statistics use the same
selected calibrated points. The raw archive remains before filtering/calibration.

## Deliberate limits

One selected series, not a multi-sensor selector. One writer per session and a
shared local filesystem. No HTTP data API, authentication, service supervisor,
production hardening or automatic restart. The collector remains consumer-paced;
heavy processing can delay sampling. Archives grow; windows stay bounded.

The finite workflow still loads its file into memory. A dashboard snapshot is
limited to 8 MiB; do not select an archive. Live-window capacity is your existing
configuration choice. Snapshot replacement is not a power-loss durability promise
or a guarantee for all network filesystems. Browser polling is not a heartbeat.

## Official references

- Streamlit fragments: https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment
- Line charts: https://docs.streamlit.io/develop/api-reference/charts/st.line_chart
- Running a page: https://docs.streamlit.io/develop/api-reference/cli/run
- Python/environment setup: https://docs.streamlit.io/get-started/installation/command-line
- Optional AppTest: https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest
