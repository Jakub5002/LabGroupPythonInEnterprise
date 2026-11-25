# Checks for this iteration

Run the existing and new standard-library checks:

```bash
python -m unittest discover -s checks -p "*.py" -v
```

Limit the run to the new tasks:

```bash
python -m unittest discover -s checks -p "test_visualisation.py" -v
```

Append `-k V1`, `-k V2`, `-k V3`, or `-k V4` to focus on one exercise.
A skipped test means a labelled placeholder is unfinished, not that it passed.
The optional browser checks require the dashboard dependencies:

```bash
python -m unittest discover -s browser_checks -p "test_*.py" -v
```
