# Solutions — G1–G6

**Handout 2 of 2 · Your companion to Start Here**

Compare each explanation with the matching function in the solved project.
The snippets show the central idea, not replacements for the complete functions:
retain their validation and error handling. Try the check below each explanation.

## G1 · Generate values, not timestamps

**`simulation.py` → `sensor_values`**

Create one private random-number generator **before** the infinite loop:

```python
rng = random.Random(sensor["seed"])
while True:
    value = rng.gauss(sensor["mean"], sensor["noise_std"])
    # Check finiteness and apply the metric's limits here.
    yield value
```

Reject nonfinite values; clip humidity to 0–100 and pressure to at least zero.
The generator pauses at `yield` until its consumer requests another value.
It neither sleeps nor retains earlier values. Recreating `rng` inside the loop
would restart its sequence every time.

**Check:** zero noise gives a constant; equal seeds give equal value sequences.

## G2 · Wait for an absolute deadline

**`simulation.py` → `wait_until`**

```python
remaining = deadline - clock()
while remaining > 0:
    sleep(remaining)
    remaining = deadline - clock()
```

`clock` defaults to `time.monotonic`, measuring elapsed time without depending on
wall-clock adjustments. Rechecking handles early wake-ups; an expired deadline
needs no sleep. The supplied scheduler combines this wait with G1. It uses UTC
wall-clock time separately for each stored measurement.

**Check:** one 5-second channel emits near 5, 10, …, 50 seconds. The first-to-last
timestamp gap is about 45 seconds, although acquisition takes about 50 seconds.

## G3 · Yield one file record at a time

**`streaming.py` → `iter_jsonl`**

Open the finished file inside a `with` block. Iterate over numbered lines, skip
blank lines, decode with `json.loads`, validate with `parse_record`, then `yield`.
Include the filename and line number in errors. Exhaust or explicitly close the
generator to release the file.

Do not accumulate a list or add delays: this is offline replay, not live tailing.

**Check:** a valid first line is returned before an invalid third line raises an
error. Validation happens as you consume the file.

## G4 · Filter first; calibrate a copy

**`streaming.py` → `select_calibrated`**

Compare the full `(room, sensor_id, metric)` identity. Skip other series. For a
match, yield the existing `calibrate_reading` result; when calibration is disabled,
yield `reading.copy()` instead. Raw input must remain unchanged in both cases.

This transformation performs no file access, logging, or printing. To find one
match it may consume several rejected records, but it stops at that match.

**Check:** selecting temperature excludes humidity without changing either input.

## G5 · Bound memory and protect snapshots

**`streaming.py` → `rolling_windows`**

Use a positive integer capacity, rejecting booleans and mixed series/units:

```python
window = deque(maxlen=size)
# Inside the loop, after validation:
window.append(reading.copy())
yield [record.copy() for record in window]
```

Yield partial windows during warm-up. The deque drops the oldest entry when full.
Copies prevent an edited result from changing later windows. The supplied
`build_snapshot` calculates statistics from exactly the points being returned.

**Check:** capacity 3 produces window lengths 1, 2, 3, 3, …, not an expanding list.

## G6 · Record incrementally

**`recording.py` → `append_reading`**

```python
line = json.dumps(reading, ensure_ascii=False, allow_nan=False) + "\n"
stream.write(line)
stream.flush()
```

Serialise before writing so invalid values cannot leave a partial JSON object.
When requested, call `os.fsync(stream.fileno())` after flushing. Let write errors
propagate. The caller owns the open file; this function must not close it.
Flushing improves visibility, but is not a power-failure guarantee.

**Check:** two calls produce two readable lines before the writer is closed.

## Follow one record through the application

`run_stream.py` limits **total raw records**, saves each one, then applies G4 and
G5. A humidity record is therefore archived even when you monitor temperature.
The consumer advances the generators: they are not background sensor threads,
and slow processing can delay acquisition. Memory stays bounded; the archive grows.

The generated offline configuration uses the existing finite file workflow,
which loads the recording into memory. G3 provides a separate lazy replay route.
For the next visualisation step, use `latest.json` or a finished recording—do not
start another sensor generator whenever a plot refreshes.
