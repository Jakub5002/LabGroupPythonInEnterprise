# Visualisation environment note

Use a Python 3.11+ environment for the optional Streamlit dashboard. The collector
still uses only the standard library; it can run in a separate environment sharing
the same session folder. The earlier core-compatibility notes below are historical,
not evidence of a Streamlit runtime test. See VALIDATION.md for this iteration.

---

# Interpreter compatibility

This extension retains the original Python 3.9+ syntax target and the earlier
Optional/Union annotation fix. No `Path | None` type annotation is introduced.
Runtime verification uses Python 3.13.5 on Linux; see VALIDATION.md for exact tests.
Grammar checking with a Python 3.9 feature setting is not a Python 3.9 runtime test.

Use `python --version` and `python -c "import sys; print(sys.executable)"` to identify
the interpreter behind your command. No third-party dependencies are required.
A maintained Python version is preferable for a new environment; the syntax target
is not a recommendation to install an older interpreter.

The standard record uses explicit UTC offsets such as +00:00, preserving the
previous parser's cross-version timestamp convention. Actual GUI, Windows/macOS,
real hardware, power-loss recovery, and long-duration operation are not verified
by the Linux tests.
