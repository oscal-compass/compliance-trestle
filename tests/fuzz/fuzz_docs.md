# Fuzzing harness for compliance-trestle

This folder contains **structure-aware fuzzing** for trestle's OSCAL models,
starting with the `Catalog` model.

The primary goal is to find bugs in how trestle parses and round-trips OSCAL
JSON — especially silent data corruption and unexpected crashes that normal
unit tests miss because they only exercise known-good inputs.

## Why this fuzzer exists

- Improves the OpenSSF Scorecard Fuzzing metric (addresses issue #2018).
- Exercises deep nesting, missing fields, UUID edge cases, parameter
  resolution, and round-trip serialisation behaviour.
- Runs automatically on every pull request (10 minutes, non-blocking).
- Uses real NIST SP800-53 data so the fuzzer operates on production-like
  documents rather than synthetic test cases.

## What it does

On every iteration the fuzzer:

1. Takes a (mutated) OSCAL JSON document.
2. Parses it into a trestle `Catalog` Pydantic model.
3. Serialises the model back to JSON.
4. Re-parses that JSON into a second `Catalog` object.
5. Asserts the two objects are semantically identical after normalisation.

A divergence in step 5 indicates a silent data-corruption bug in trestle's
load-save cycle and is recorded as a crash.

The mutator deliberately deletes required keys, removes list items, and
corrupts strings and numbers to stress-test parsing and serialisation logic.

## Key files

| File | Purpose |
|------|---------|
| `fuzz_catalog.py` | Fuzzing harness for the Catalog model |
| `.clusterfuzzlite/build.sh` | Downloads the real NIST seed and compiles the fuzzer |
| `.clusterfuzzlite/project.yaml` | Configures ClusterFuzzLite for Python |
| `.github/workflows/fuzzing.yml` | GitHub Actions workflow — runs on every PR |

## Running locally

The NIST SP800-53 seed is **required**.  The harness exits immediately with a
clear error if it is not present.  A minimal hand-crafted catalog produces
near-zero useful coverage — the mutator's input space collapses to a single
shallow control family and the fuzzer spends all its cycles bouncing off the
Pydantic validation wall rather than exercising trestle's deep parsing logic.

In CI, `build.sh` downloads the seed automatically.  For local runs:

```bash
cd /path/to/compliance-trestle
pip install -e ".[test]"

mkdir -p tests/fuzz/fuzz_catalog_seed_corpus

curl -fsSL \
  "https://raw.githubusercontent.com/usnistgov/oscal-content/\
941c978d14c57379fbf6f7fb388f675067d5bff7/nist.gov/SP800-53/rev5/json/\
NIST_SP-800-53_rev5_catalog-min.json" \
  -o tests/fuzz/fuzz_catalog_seed_corpus/nist_sp800_53_rev5.json

python tests/fuzz/fuzz_catalog.py
```

Press `Ctrl+C` to stop.

## Data model compatibility

| Model | Round-trip fit | Seed availability | Status | Notes |
|-------|---------------|-------------------|--------|-------|
| Catalog | Excellent | NIST SP800-53 rev5 (public, pinned) | Done | Self-contained, deep nesting |
| Profile | Very good | NIST FISMA Low / Moderate / High profiles | Planned | Needs extra variant for resolution logic |
| Component Definition | Very good | trestle test fixtures | Planned | Similar structure to Catalog |
| SSP | Good | Generated from trestle test fixtures | Planned | Cross-document UUID refs need a stub resolver or workspace |
| SAP | Good | Generated from trestle test fixtures | Planned | Same challenge as SSP |
| SAR | Good | Generated from trestle test fixtures | Planned | Same challenge as SAP |
| POAM | Shallow | Low value | Not recommended | Better suited for property-based testing (Hypothesis) |

## Roadmap

- **Next**: Generalise the harness into a reusable factory; add
  `fuzz_profile.py` and `fuzz_component_def.py`.
- **Later**: Implement SSP, SAP, and SAR using document-local isolation
  (stub out cross-document resolution) to keep the harnesses self-contained.
- **Long-term**: Add a scheduled nightly long-run job; evaluate full
  workspace-based fuzzing for the cross-document models.

## Technical notes (for maintainers)

### Harness architecture and ClusterFuzzLite integration

The harness uses [Atheris](https://github.com/google/atheris) for
coverage-guided Python fuzzing and integrates with ClusterFuzzLite via
OSS-Fuzz base images (`Dockerfile`).

During CI builds (`build.sh`), the pinned NIST SP800-53 catalog is downloaded
into `$OUT/fuzz_catalog_seed_corpus/`.  libFuzzer loads every file in that
directory as an initial corpus entry, so the fuzzer starts with ~1,000
structurally sound real-world controls rather than random bytes.

### Structure-aware mutator design

The custom mutator (`_mut`) is designed to stress-test Pydantic validation
paths without immediately destroying the OSCAL structure:

- **Key deletion**: The mutator can *remove* required keys entirely, not just
  corrupt their values.  This exercises Pydantic's missing-field validation
  and any trestle code that assumes a field is always present.
- **Recursion-depth guard**: The mutator tracks nesting depth and stops
  recursing beyond `MAX_DEPTH = 32`, preventing false-positive
  `RecursionError` crashes on the deep nesting in the NIST catalog.  This
  value was validated against the full NIST seed in local testing.
- **Softened list mutation**: List elements are mutated, skipped, or removed
  with equal (3-way) probability, preserving more document structure per
  iteration than an aggressive mutate-or-remove approach.
- **Entropy source**: The custom mutator passes the full corpus entry (`data`)
  to `FuzzedDataProvider`.  An earlier version used the 8-byte `seed` integer
  instead, which was exhausted after ~8 `ConsumeIntInRange` calls and silently
  returned `0` for all subsequent calls, making mutations nearly deterministic.
  Using `data` gives the FDP varied, abundant entropy on every libFuzzer
  iteration.

### Why no fallback seed

A minimal hand-crafted catalog — one group, one control, no params — produces
near-zero useful coverage.  The mutator walks a shallow tree, runs out of
meaningful structure almost immediately, and the fuzzer spends all its time
bouncing off Pydantic's validation wall without ever reaching trestle's deeper
parsing and serialisation logic.  Running with such a seed gives a false sense
of progress while finding nothing.

The NIST SP800-53 catalog is a hard requirement.  If it is not present, the
harness raises `FileNotFoundError` immediately rather than running silently at
negligible effectiveness.

### How normalisation works

The round-trip assertion compares `obj1` and `obj2` using `_normalise()` rather
than Pydantic v1's built-in `__eq__`.  Here is exactly what `_normalise()` does
to a parsed catalog before comparing:

**Step 1 — serialise both objects to plain dicts**

```python
dict1 = json.loads(obj1.json(by_alias=True, exclude_none=True))
dict2 = json.loads(obj2.json(by_alias=True, exclude_none=True))
```

Both objects are serialised with `exclude_none=True` so that optional fields
that were absent in the input are not present in the dict.  This mirrors what
Pydantic v1 does on every serialisation and ensures the two dicts start from
the same baseline.

**Step 2 — strip None and empty containers recursively**

```python
cleaned = {
    k: _normalise(v)
    for k, v in obj.items()
    if v is not None and v != [] and v != {}
}
```

Even after `exclude_none=True`, Pydantic v1 can produce fields set to `None`,
`[]`, or `{}` depending on how default values are defined in the model.
Stripping these prevents false positives where one side of the comparison has
`"params": null` and the other simply omits `"params"`.

**Step 3 — sort dict keys**

```python
return dict(sorted(cleaned.items()))
```

Pydantic v1 does not guarantee the order in which fields are serialised.  Two
semantically identical `Catalog` objects can produce dicts with keys in
different orders.  Sorting removes this as a source of false positives.

**Step 4 — sort list elements by JSON representation**

```python
return sorted(normalised_items, key=lambda x: json.dumps(x, sort_keys=True))
```

Pydantic v1's serialiser does not guarantee list element order.  A list of
`props` on a control may come out in a different order on the second parse.
Sorting by JSON representation makes element-order differences invisible to the
comparison.

This is intentionally lossy for one class of bug: if OSCAL semantics require a
specific list order (e.g. `parts` must appear in document order) and trestle
violates that order on round-trip, the normalisation will hide it.  This
trade-off is accepted because false positives from ordering noise are more
damaging to the harness's usefulness than missing that single class of bug.

**Why not just use `obj1 == obj2`?**

Pydantic v1's `__eq__` compares field by field, including the order of elements
in lists.  On the NIST catalog — which has hundreds of controls each with
multiple `props`, `parts`, and `params` — the serialiser produces list orderings
that differ between the first and second parse.  Using `__eq__` directly
produces a crash on almost every valid input that clears Stage 1, making the
idempotency assertion useless.

### Exception handling

The same exception class means completely different things depending on which
object raised it.  The harness uses a two-stage try block to keep these cases
separate.

**Stage 1 — parsing external input into `obj1`** (`Catalog.parse_raw(data)`):

| Exception | Raised by | Meaning | Handling |
|-----------|-----------|---------|----------|
| `ValidationError` | Pydantic schema check | Mutated field value failed type/format validation | Silent return |
| `JSONDecodeError` | `json.loads` inside `parse_raw` | Mutation produced invalid JSON syntax | Silent return |
| `UnicodeDecodeError` | string decode | Byte-level mutation produced non-UTF-8 bytes | Silent return |
| `ValueError` | field coercion | Type cast failed (e.g. string where int expected) | Silent return |
| `TrestleError` | trestle strict model | Extra or unknown fields in the input — **the validator doing its job** | Silent return |

Every exception in Stage 1 is **harmless**.  The mutator regularly produces
inputs with deleted required keys, extra fields, or corrupted values.  Trestle
catching these and raising `TrestleError` or `ValidationError` is exactly
correct behaviour.  The fuzzer accumulates these as corpus entries and mutates
forward.

**Stage 2 — round-tripping `obj1` through serialise → re-parse into `obj2`**:

At this point `obj1` is a `Catalog` that trestle successfully accepted.  Any
exception from here is a genuine defect — trestle is failing to handle data it
just validated.

| Exception | Raised by | Meaning | Handling |
|-----------|-----------|---------|----------|
| `TrestleError` | `obj1.json()` or `Catalog.parse_raw(exported)` | trestle either failed to serialise its own model, or rejected its own serialised output on re-parse | **Re-raise — real bug** |
| `RecursionError` | serialiser | Unbounded recursion in trestle's serialisation logic | **Re-raise — real bug** |
| `AttributeError` | serialiser or re-parser | Code accessed a field that doesn't exist — often a Pydantic v1/v2 API mismatch | **Re-raise — real bug** |
| `RuntimeError` | `_idempotency_violation` | `obj1` and `obj2` differ after normalisation — data was silently lost or changed during the round-trip | **Re-raise — real bug** |

The key distinction: `TrestleError` on `obj1` means *"the input was bad"* —
harmless.  `TrestleError` on `obj2` means *"trestle produced output it cannot
read back"* — that is a real defect.

### Pydantic version note

This harness targets Pydantic v1 (the version currently used by trestle).
When trestle migrates to Pydantic v2, update:

- `Catalog.parse_raw(data)` → `Catalog.model_validate_json(data)`
- `obj.json(by_alias=True, exclude_none=True)` → `obj.model_dump_json(by_alias=True, exclude_none=True)`
- Re-evaluate `_normalise()` — v2's stricter serialisation may eliminate the
  list-ordering false positives that `_normalise()` works around.

## Troubleshooting

- **"NIST seed not found" error on startup** — The seed is required.  Run the
  `curl` command in the Running Locally section above.
- **Fuzzer feels slow or exec/s is very high (>10,000)** — High exec/s with
  static coverage means inputs are bouncing off the validation wall without
  reaching the round-trip logic.  Verify the NIST seed is present and that
  `max_len` in `main()` is at least `10000000`.
- **Unexpected crash volume** — Review the Stage 2 exception list.  A
  `TrestleError` crash in Stage 2 is always a real defect and should be
  investigated, not silenced.