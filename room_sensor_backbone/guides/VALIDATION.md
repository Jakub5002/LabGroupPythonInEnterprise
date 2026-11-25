# Validation — visualisation iteration

Reference: **147 passed; zero skipped.**

## Executed

Python **3.13.5 on Linux**. The standard-library suite has **147 tests**: all 118
previous checks plus 29 new checks. Cases were run in eight isolated batches to
fit the execution environment; the supplied ordinary unittest command runs the
same cases sequentially. Per-case output and totals are in
`validation/visualisation/`.

The reference passed all 147 cases. The student scaffold passed 131 and skipped
16 tests only because explicit V1–V4 placeholders were reached. A skip is not a
completed exercise. In the parallel student run, the original Ctrl+C check hit its
five-second startup deadline once under load. The affected 18-test batch passed
when rerun alone; neither the test nor application code was changed. The initial
log is retained in the student archive.

New checks cover moving-average warm-up, irregular-time slopes, undefined trends,
non-mutation, JSON reading/reloading, invalid/oversized snapshots, aligned plot
columns, stale/finished/offline status, optional configuration, path collisions,
and bounded finite-file publication. The original checks cover timed acquisition,
raw recording of unselected channels, storage failure, Ctrl+C and offline replay.

A separate reference end-to-end run used the supplied real-wait quick configuration:
**10 raw measurements, 5 points in the final live window, and 10 points in the
offline snapshot**. Stored analysis exactly matched recalculation from its points.
Offline reanalysis left the raw archive byte-for-byte unchanged.

All Python files parsed under Python 3.9 grammar. This is a syntax check, not an
older-interpreter runtime test. Other operating systems were not executed here.

## Browser-runtime boundary — not verified here

**Streamlit was not installed in this environment.** Package installation failed
because the environment could not retrieve dependencies. Consequently, genuine
Streamlit rendering, websocket delivery, automatic fragment reruns, and interaction
in a real browser were **not executed**. No browser screenshot or successful
Streamlit-version claim is supplied.

The page's Python control flow was exercised with a lightweight API stand-in:
offline metrics, read-only loading, pause, one-shot refresh, retention after corrupt
JSON, clearing a previous source, and curve toggles. This is not a substitute for
a Streamlit/browser test. The source also passed compilation and uses the official
fragment/line-chart APIs linked in CHANGES_VISUALISATION.md.

Four optional **real AppTest** checks are included in `browser_checks/`; all four
correctly skipped here because Streamlit was unavailable. After installing
`requirements-dashboard.txt`, run:

```bash
python -m unittest discover -s browser_checks -p "test_*.py" -v
```

AppTest itself is not a live browser. Follow the compact handouts for the final
manual live check: start collection, open the page, pause/resume the display,
stop collection, and confirm the final window remains visible.

Earlier `PREVIOUS_*` documents and the old `validation/test_output.txt` concern
previous iterations, not additional tests of this dashboard.
