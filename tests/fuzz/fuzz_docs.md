# Fuzzing Harness for compliance-trestle — Complete Maintainer Guide

This document is the single authoritative reference for the structure-aware
fuzzing harness in `tests/fuzz/`. It covers why the harness exists, how every
component works, the deliberate two-seed design, the full CI pipeline, and a
concrete walkthrough of what a mutation actually looks like at runtime.

---

## Table of Contents

1. [Why this fuzzer exists](#1-why-this-fuzzer-exists)
2. [What the fuzzer tests](#2-what-the-fuzzer-tests)
3. [The two-seed design — small seed vs large seed](#3-the-two-seed-design--small-seed-vs-large-seed)
4. [The real NIST SP800-53 catalog — what it contains](#4-the-real-nist-sp800-53-catalog--what-it-contains)
5. [Architecture overview](#5-architecture-overview)
6. [Component-by-component explanation](#6-component-by-component-explanation)
7. [Mutation walkthrough — a concrete example](#7-mutation-walkthrough--a-concrete-example)
8. [The round-trip idempotency test](#8-the-round-trip-idempotency-test)
9. [Exception handling — two stages](#9-exception-handling--two-stages)
10. [Normalisation — why and how](#10-normalisation--why-and-how)
11. [CI pipeline — GitHub Actions and ClusterFuzzLite](#11-ci-pipeline--github-actions-and-clusterfuzzlite)
12. [Key files reference](#12-key-files-reference)
13. [Running locally](#13-running-locally)
14. [Interpreting fuzzer output](#14-interpreting-fuzzer-output)
15. [Roadmap for future harnesses](#15-roadmap-for-future-harnesses)
16. [Troubleshooting](#16-troubleshooting)

---

## 1. Why this fuzzer exists

Normal unit tests exercise known-good inputs. They verify that a valid OSCAL
catalog parses correctly and that specific fields contain expected values. What
they cannot find is the class of bug that only appears when the input is
*almost* valid — a missing required field, a UUID that contains null bytes, a
list that is empty where the code assumes it has at least one element.

This fuzzer exists to find exactly those bugs by generating millions of
structurally plausible but semantically broken inputs and observing how trestle
responds.

Specific goals:

- **Silent data corruption** — trestle accepts a document, serialises it, and
  the re-parsed version is missing fields. The user never knows.
- **Unexpected crashes** — an `AttributeError` or `RecursionError` deep in
  trestle's serialisation logic when it encounters edge-case inputs.
- **OpenSSF Scorecard** — the Fuzzing metric requires a continuously running
  fuzzer integrated with the CI pipeline (addresses issue #2018).

---

## 2. What the fuzzer tests

On every iteration the fuzzer runs this pipeline:

```
mutated bytes
     │
     ▼
[1] json.loads() — is this valid JSON?
     │ no → Stage 1 return (expected)
     ▼
[2] strip OSCAL envelope {"catalog": {...}} if present
     │
     ▼
[3] Catalog.model_validate_json(raw) — can trestle parse it?
     │ ValidationError / TrestleError → Stage 1 return (expected)
     ▼
[4] obj1.model_dump_json(by_alias=True, exclude_none=True) — serialise
     │
     ▼
[5] Catalog.model_validate_json(exported) → obj2 — re-parse
     │
     ▼
[6] _normalise(obj1) == _normalise(obj2)? — idempotency check
     │ not equal → RuntimeError → CRASH (real bug)
     ▼
    OK — continue fuzzing
```

A failure at step 6 means trestle accepted a document, wrote it out, and then
the written version was different from what it read in. This is a silent
data-corruption bug — the kind that is nearly impossible to find with unit tests
because those tests use inputs that were designed to round-trip correctly.

---

## 3. The two-seed design — small seed vs large seed

This is the most important design decision in the harness and the one most
likely to confuse maintainers. There are **two corpus files** with completely
different purposes.

### Seed 1 — `aaa_smoke_test_seed.json` (180 bytes)

```json
{
  "catalog": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "title": "Smoke Test Seed",
      "last-modified": "2026-03-24T00:00:00Z",
      "version": "1.0.0",
      "oscal-version": "1.1.3"
    }
  }
}
```

**Purpose:** To pass ClusterFuzzLite's smoke test.

After every build, ClusterFuzzLite runs a smoke test — it feeds the
**first corpus file** (sorted alphabetically) to the fuzzer immediately after
compilation to verify the binary does not crash on startup. If the smoke test
fails, the build is marked broken and the run never starts.

The NIST catalog is 4.65 MB. Parsing it through Pydantic's validators, running
the round-trip, and normalising the result takes 40–60 seconds on a loaded CI
runner. The smoke test has a 25-second default timeout. If the NIST file were
loaded first, the smoke test would always time out and the build would always be
marked broken.

The tiny seed is named `aaa_smoke_test_seed.json` specifically because `a`
sorts before `n`. LibFuzzer loads corpus files in alphabetical order. The tiny
seed is always first, parses in under one millisecond, passes the smoke test,
and then the NIST catalog is loaded as the second corpus entry for actual
coverage depth.

**What happens if you rename it?** If the tiny seed sorts after the NIST file
alphabetically (e.g. `tiny_seed.json`), the smoke test always loads the
4.65 MB file first, always times out, and the pipeline breaks on every single
run. This was the original cause of the `100% of fuzz targets broken` failure
that this harness was designed to fix.

### Seed 2 — `nist_sp800_53_rev5.json` (4.65 MB)

This is the real NIST SP800-53 revision 5 catalog downloaded from the official
USNIST OSCAL content repository at a pinned commit:

```
https://raw.githubusercontent.com/usnistgov/oscal-content/
941c978d14c57379fbf6f7fb388f675067d5bff7/
nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json
```

**Purpose:** To give the fuzzer real, production-scale OSCAL structure to
mutate from.

A minimal hand-crafted catalog with one group and one control gives the fuzzer
almost nothing to work with. The mutator walks a shallow tree, exhausts the
interesting structure in a few iterations, and the fuzzer spends the rest of its
time bouncing off Pydantic's validation wall. Exec/s climbs to 50,000+ but
coverage stays completely flat.

The NIST catalog contains approximately 1,000 controls across 20 control
families, each with multiple parameters, parts, links, responsible-roles, and
back-matter entries. It exercises every code path in trestle's OSCAL parser.
With this seed, exec/s drops to 2–5 per second and coverage grows meaningfully
on each new iteration.

**The seed is pinned to a specific commit** so that if a bug is found, the
exact input that triggered it can always be reproduced. If the seed URL changes
or the content changes, the fuzzer may start producing false positives or
failing seed validation on startup.

---

## 4. The real NIST SP800-53 catalog — what it contains

The seed file `NIST_SP-800-53_rev5_catalog-min.json` is the machine-readable
version of NIST Special Publication 800-53 Revision 5, *Security and Privacy
Controls for Information Systems and Organizations*. It is the primary US
federal government security control catalog.

Its top-level OSCAL structure looks like this:

```json
{
  "catalog": {
    "uuid": "...",
    "metadata": {
      "title": "NIST SP 800-53 Rev 5 ...",
      "last-modified": "...",
      "oscal-version": "1.1.2"
    },
    "groups": [
      {
        "id": "ac",
        "title": "Access Control",
        "controls": [
          {
            "id": "ac-1",
            "title": "Policy and Procedures",
            "params": [ { "id": "ac-1_prm_1", "label": "..." } ],
            "props": [ { "name": "label", "value": "AC-1" } ],
            "parts": [
              {
                "id": "ac-1_smt",
                "name": "statement",
                "parts": [
                  { "id": "ac-1_smt.a", "name": "item", "prose": "..." }
                ]
              }
            ],
            "controls": [
              {
                "id": "ac-1.1",
                "title": "Control Enhancement ...",
                "parts": [ ... ]
              }
            ]
          }
        ]
      }
    ],
    "back-matter": {
      "resources": [ { "uuid": "...", "title": "...", "rlinks": [...] } ]
    }
  }
}
```

The catalog has 20 control families (AC, AU, AT, CA, CM, CP, IA, IR, MA, MP,
PE, PL, PM, PS, PT, RA, SA, SC, SI, SR), each with multiple controls and
control enhancements. Controls can be nested up to 4 levels deep
(catalog → group → control → enhancement). This nesting is what makes the NIST
seed so valuable — it forces the mutator and the round-trip logic to handle
recursive structures, which is where most real bugs hide.

---

## 5. Architecture overview

```
┌──────────────────────────────────────────────────────────────────┐
│  ClusterFuzzLite / GitHub Actions                                │
│                                                                  │
│  build_fuzzers                      run_fuzzers                  │
│  ┌─────────────┐                   ┌──────────────────────────┐  │
│  │ Dockerfile  │                   │ libFuzzer engine         │  │
│  │ build.sh    │──builds──►        │                          │  │
│  │             │    ↓              │  custom_mutator()        │  │
│  │  aaa_smoke  │  fuzz_catalog     │       │                  │  │
│  │  nist_seed  │  .pkg binary      │       ▼                  │  │
│  └─────────────┘                   │  testoneinput()          │  │
│                                    │       │                  │  │
│                                    │  Stage 1: parse          │  │
│                                    │  Stage 2: round-trip     │  │
│                                    │  Stage 2: normalise      │  │
│                                    └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

          ┌─────────────────────────────────────┐
          │  Atheris (Python coverage bridge)   │
          │  instruments trestle imports        │
          │  reports coverage to libFuzzer      │
          └─────────────────────────────────────┘
```

Atheris is the bridge between libFuzzer (a C++ coverage-guided fuzzer) and
Python code. The `with atheris.instrument_imports():` block tells Atheris to
instrument every Python module that trestle imports, so libFuzzer's coverage
tracking sees which lines of trestle code were hit on each input. Without this
instrumentation, libFuzzer has no coverage signal and cannot guide mutation —
exec/s climbs above 50,000 but no new corpus entries are ever added.

---

## 6. Component-by-component explanation

### `_load_seed()` — module-level seed loading

```python
_SEED: bytes = _load_seed()
```

This runs at **import time**, before `main()` is called. It loads the NIST
catalog bytes into memory so that `custom_mutator` can fall back to it when
libFuzzer injects raw bytes that are not valid JSON.

The path is constructed relative to the compiled binary location so it works
both locally (relative to the script) and inside the ClusterFuzzLite container
(relative to `$OUT`).

### `_mut(data, fdp, depth)` — structure-aware mutator

The mutator takes a parsed JSON object and corrupts it using three operations:

| Operation | Dict | List | Scalar |
|-----------|------|------|--------|
| Mutate value | recurse into value | mutate one element | replace bytes / add number |
| Skip | leave unchanged | leave unchanged | leave unchanged |
| Delete | remove key entirely | pop element | N/A |

**Key deletion** is the most important operation. It exercises Pydantic's
required-field validation paths. Without it, the mutator only corrupts values —
it never tests what happens when a required field like `uuid` or `metadata` is
completely absent.

**Recursion depth guard** (`MAX_DEPTH = 32`) prevents Python's default
`RecursionError` on the NIST catalog's deep nesting. Without it, the mutator
would crash Python's call stack on the 4-level deep control enhancement
structures.

**3-way list mutation** (mutate/skip/pop with equal probability) preserves more
document structure per iteration than aggressive mutate-or-pop. A list that is
immediately emptied gives the fuzzer nothing to mutate in the next iteration.

### `custom_mutator(data, max_size, seed)` — libFuzzer integration

LibFuzzer calls this function to produce each new test input. The mutator:

1. Tries to `json.loads(data)` — the current corpus entry.
2. If it fails (libFuzzer injected raw bytes from its own splicing), falls back
   to `_SEED` to re-anchor to valid OSCAL structure.
3. Calls `_mut()` to corrupt the parsed object.
4. Serialises back to JSON bytes and truncates to `max_size`.

The `FuzzedDataProvider` is initialised with the full `data` bytes, not the
8-byte `seed` integer. This is critical — an `FDP` initialised with only 8
bytes exhausts its entropy after approximately 8 `ConsumeIntInRange` calls and
silently returns 0 for all subsequent calls, making all mutations after the
first few dictionary keys completely deterministic and non-random.

### `testoneinput(data)` — the fuzz target

This is the function libFuzzer calls on every iteration. It implements the
two-stage pipeline described in section 2.

### `_normalise(obj)` — stable comparison

See section 10 for the full explanation.

### `_validate_seed_on_startup(seed_path)` — startup validation

Runs before `atheris.Setup()` in `main()`. If the NIST seed cannot be parsed
by trestle, it raises `RuntimeError` immediately with a clear message rather
than letting the fuzzer run silently with only the tiny seed, which would
produce near-zero useful coverage.

### `main()` — entry point and flag management

The `-timeout=120` flag is injected by stripping any existing `-timeout=` from
`sys.argv` first, then appending the correct value. This is necessary because
ClusterFuzzLite injects its own `-timeout=25` flag which would be overridden by
a simple append only if Atheris respects argument ordering, which it does not
reliably.

---

## 7. Mutation walkthrough — a concrete example

Here is a concrete example of one mutation iteration on a small fragment of the
NIST catalog.

**Input corpus entry (simplified):**

```json
{
  "id": "ac-2",
  "title": "Account Management",
  "params": [
    { "id": "ac-2_prm_1", "label": "organization-defined account types" }
  ],
  "parts": [
    {
      "id": "ac-2_smt",
      "name": "statement",
      "prose": "Manage system accounts..."
    }
  ]
}
```

**Step 1 — `_mut()` processes the top-level dict:**

The FDP provides random bits. Suppose the choices are:

| Key | Choice | Action |
|-----|--------|--------|
| `id` | 1 (skip) | unchanged |
| `title` | 0 (mutate) | recurse into string |
| `params` | 2 (delete) | key removed entirely |
| `parts` | 0 (mutate) | recurse into list |

**Step 2 — string mutation on `title`:**

```python
fdp.ConsumeBytes(len("Account Management") + 64)
# returns e.g. b'\x00\xff\xc3\xa9...'
# decoded with errors='ignore' → "é..." or empty string
```

**Step 3 — list mutation on `parts`:**

The FDP picks index 0 and action 0 (mutate). It recurses into the `parts[0]`
dict. The FDP picks:

| Key | Choice | Action |
|-----|--------|--------|
| `id` | 2 (delete) | key removed |
| `name` | 1 (skip) | unchanged |
| `prose` | 0 (mutate) | string corrupted |

**Resulting mutated object:**

```json
{
  "id": "ac-2",
  "title": "\u00e9\u0000corrupted",
  "parts": [
    {
      "name": "statement",
      "prose": "\u00ff\u0000garbage bytes"
    }
  ]
}
```

**What trestle sees:**

- `params` is missing entirely — Pydantic checks if it is required.
  If optional, fine. If required, `ValidationError` → Stage 1 return.
- `parts[0].id` is missing — same check.
- `title` contains non-ASCII and null bytes — string validators run.
- `prose` contains garbage — same.

If trestle accepts this input (Stage 1 passes), the round-trip check then
verifies that serialising and re-parsing produces an identical object. If
`prose` is normalised differently on re-parse (e.g. null bytes stripped), the
idempotency check catches it as a real bug.

---

## 8. The round-trip idempotency test

The core insight of this harness is that **any input trestle accepts must
survive a round-trip unchanged**. If trestle reads a document and writes it
back out, reading the output must produce an identical model.

This catches a specific class of bug that unit tests never find: trestle
silently drops or transforms a field during serialisation. The field was valid
enough to parse but trestle's serialiser omits it, truncates it, or reorders it
in a way that changes its semantics.

The comparison is done on normalised dicts rather than the Pydantic objects
directly. See section 10 for why.

---

## 9. Exception handling — two stages

The same exception class has completely different meanings depending on where
it is raised. The two-stage try block keeps these cases separate.

### Stage 1 — parsing external (mutated) input into `obj1`

All exceptions here happen when attempting to generate `obj1` from the fuzzer's raw, mutated input.  
These are **expected and harmless**. The mutator regularly produces invalid inputs. Trestle catching them is correct behaviour and prevents them from becoming `obj1`.

| Exception | Source | Meaning |
|-----------|--------|---------|
| `ValidationError` | Pydantic | Field type/format check failed |
| `JSONDecodeError` | `json.loads` | Not valid JSON |
| `UnicodeDecodeError` | string decode | Non-UTF-8 bytes |
| `ValueError` | type coercion | String where int expected |
| `TrestleError` | trestle model | Extra/unknown fields — validator doing its job |

All of these → `return` silently. The fuzzer accumulates the input as a corpus
entry and continues mutating.

### Stage 2 — round-tripping a valid Catalog into `obj2`

At this point `obj1` is a `Catalog` that trestle successfully accepted. The harness now serialises `obj1` and parses it back into `obj2`. 
Any exception from here indicates `obj2` failed to generate, which is a **genuine defect** because trestle generated the JSON itself.

| Exception | Source | Meaning |
|-----------|--------|---------|
| `TrestleError` | `model_dump_json()` or re-parse | Trestle cannot serialise or re-parse its own output |
| `RecursionError` | serialiser | Unbounded nesting in trestle's serialisation logic |
| `AttributeError` | serialiser/re-parser | Code accessed a field that does not exist |
| `RuntimeError` | `_idempotency_violation` | Round-trip produced a different object — data loss |

All of these → `raise`. ClusterFuzzLite records the input as a crash artifact.

---

## 10. Normalisation — why and how

Comparing `obj1 == obj2` directly using Pydantic's `__eq__` produces a crash
on almost every valid input that passes Stage 1, because Pydantic does not
guarantee the order in which list elements are serialised. A list of `props` on
a control may come out in a different order on the second parse even though the
data is identical.

`_normalise()` removes all ordering noise before comparison.

**Rules applied:**

- **Dicts**: strip keys whose value is `None` or an empty container, then return as a sorted-key dict so field order never matters.
- **Lists**: sort elements by their JSON representation so that lists whose only difference is element order compare as equal. This is intentionally lossy for ordered lists — if OSCAL semantics require order preservation and trestle violates it, that is a real bug and will show up as an idempotency failure even here.
- **Scalars**: returned as-is.

**Note:** stripping `None`/empty mirrors what Pydantic v1 does with `exclude_none=True` in `.json()`, so we don't generate false positives from fields that were present before serialisation but absent after.

**Step 1 — serialise to plain dicts:**

```python
dict1 = json.loads(obj1.model_dump_json(by_alias=True, exclude_none=True))
dict2 = json.loads(obj2.model_dump_json(by_alias=True, exclude_none=True))
```

`exclude_none=True` ensures optional fields absent from the input are not
present as `None` in the dict.

**Step 2 — strip None and empty containers recursively:**

```python
cleaned = {
    k: _normalise(v)
    for k, v in obj.items()
    if v is not None and v != [] and v != {}
}
```

Even after `exclude_none=True`, Pydantic can produce `None`, `[]`, or `{}`
from default values. Stripping them prevents false positives.

**Step 3 — sort dict keys:**

```python
return dict(sorted(cleaned.items()))
```

Field serialisation order is not guaranteed in Pydantic. Sorting eliminates
this as a source of false positives.

**Step 4 — sort list elements by JSON representation:**

```python
return sorted(normalised_items, key=lambda x: json.dumps(x, sort_keys=True))
```

List element order is not guaranteed in Pydantic's serialiser. Sorting by JSON
representation makes element-order differences invisible to the comparison.

**Known limitation:** This is intentionally lossy for one class of bug. If OSCAL
semantics require a specific list order (e.g. `parts` must appear in document
order) and trestle violates that order on round-trip, this normalisation hides
it. This trade-off is accepted because false positives from ordering noise
destroy the harness's usefulness far more than missing that specific bug class.

---

## 11. CI pipeline — GitHub Actions and ClusterFuzzLite

### Workflow file — `.github/workflows/fuzzing.yml`

```yaml
name: ClusterFuzzLite PR Fuzzing
on:
  workflow_dispatch:
  pull_request:

permissions:
  contents: read
  actions: write
  security-events: write

jobs:
  Fuzzing:
    runs-on: ubuntu-latest
    concurrency:
      group: ${{ github.workflow }}-${{ matrix.sanitizer }}-${{ github.ref }}
      cancel-in-progress: true
    strategy:
      fail-fast: false
      matrix:
        sanitizer: [address]
    steps:
      - name: Build Fuzzers
        uses: google/clusterfuzzlite/actions/build_fuzzers@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          language: python
          bad-build-check: false      # ← required on first run, see note below
          sanitizer: ${{ matrix.sanitizer }}

      - name: Run Fuzzers
        uses: google/clusterfuzzlite/actions/run_fuzzers@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          fuzz-seconds: 100
          mode: 'batch'               # ← required on first run, see note below
          sanitizer: ${{ matrix.sanitizer }}
```

**`bad-build-check: false` and `mode: 'batch'`** — these two settings are
required the first time this fuzzer is introduced to the repository. On the
very first run, there is no `cifuzz-coverage-latest` artifact on `main` because
no previous successful run has generated one. `code-change` mode requires this
artifact to diff coverage against. Without it, the build step fails with
`Could not find artifact: cifuzz-coverage-latest`.

Once a successful run completes on `main` and the coverage artifact exists,
revert to `mode: 'code-change'` and remove `bad-build-check: false`.

### Build pipeline — `build.sh`

```
build.sh
  │
  ├─ pip install atheris
  ├─ pip install compliance-trestle
  │
  ├─ mkdir $OUT/fuzz_catalog_seed_corpus
  │
  ├─ write aaa_smoke_test_seed.json     ← tiny seed, sorts first, passes smoke test
  │
  ├─ curl NIST SP800-53 rev5 catalog   ← real seed, 4.65 MB, coverage depth
  │   (pinned to commit 941c978d...)
  │
  └─ compile_python_fuzzer fuzz_catalog.py
       → produces fuzz_catalog.pkg (PyInstaller bundle)
       → produces fuzz_catalog shell wrapper (LD_PRELOAD ASAN)
```

### Container — `Dockerfile`

The `base-builder-python` image from OSS-Fuzz provides:
- Clang with AddressSanitizer and libFuzzer
- Python 3.11 with Atheris pre-installed
- `compile_python_fuzzer` script that runs PyInstaller

The Dockerfile installs trestle's dependencies at image build time. The
`build.sh` then reinstalls trestle at container runtime to pick up any changes
since the image was last built.

---

## 12. Key files reference

| File | Purpose |
|------|---------|
| `tests/fuzz/fuzz_catalog.py` | Main fuzzing harness — mutator, fuzz target, startup validation |
| `tests/fuzz/fuzz_docs.md` | This document |
| `.clusterfuzzlite/Dockerfile` | OSS-Fuzz base image + trestle installation |
| `.clusterfuzzlite/build.sh` | Downloads seeds, compiles fuzzer binary |
| `.clusterfuzzlite/project.yaml` | Tells ClusterFuzzLite this is a Python project |
| `.github/workflows/fuzzing.yml` | GitHub Actions workflow — triggers on every PR |

---

## 13. Running locally

**Step 1 — install dependencies:**

```bash
cd /path/to/compliance-trestle
pip install -e ".[test]"
pip install atheris
```

**Step 2 — download the NIST seed:**

```bash
mkdir -p tests/fuzz/fuzz_catalog_seed_corpus

curl -fsSL \
  "https://raw.githubusercontent.com/usnistgov/oscal-content/\
941c978d14c57379fbf6f7fb388f675067d5bff7/\
nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json" \
  -o tests/fuzz/fuzz_catalog_seed_corpus/nist_sp800_53_rev5.json
```

This is the exact same file that `build.sh` downloads in CI. The pinned commit
`941c978d...` ensures the file content is identical across all environments.

**Step 3 — run the fuzzer:**

```bash
python tests/fuzz/fuzz_catalog.py
```

Press `Ctrl+C` to stop. The fuzzer runs indefinitely. On a laptop you will see
approximately 2–5 exec/s because of the large seed size — this is normal and
expected.

**What to look for in the output:**

```
INFO: seed corpus: files: 2 min: 180b max: 4878039b total: 4878219b
#4    INITED cov: 513 ft: 678 corp: 2/4763Kb
#5    NEW    cov: 516 ft: 689 corp: 3/4764Kb
```

`cov` and `ft` growing means the fuzzer is finding new code paths. `corp` 
growing means it is accumulating interesting inputs. These are signs of a
healthy run.

**To update the seed pin** when a new NIST catalog revision is released:

1. Find the latest commit on `usnistgov/oscal-content`.
2. Download and verify:
   ```bash
   python3 -c "
   from trestle.oscal.catalog import Catalog
   import json
   raw = open('nist_sp800_53_rev5.json').read()
   parsed = json.loads(raw)
   inner = json.dumps(parsed['catalog'])
   obj = Catalog.model_validate_json(inner)
   print('Groups:', len(obj.groups or []))
   "
   ```
3. Update `SEED_COMMIT` in `build.sh`.
4. Update the `curl` URL in this document and in the Running Locally section.

---

## 14. Interpreting fuzzer output

### Healthy run

```
INFO: Using preloaded libfuzzer
INFO: Running with entropic power schedule (0xFF, 100).
INFO: Seed: 2585384259
INFO:        0 files found in /github/workspace/cifuzz-corpus/fuzz_catalog
INFO:        2 files found in /github/workspace/build-out/fuzz_catalog_seed_corpus
INFO: seed corpus: files: 2 min: 180b max: 4878039b total: 4878219b rss: 288Mb
#4	pulse  cov: 189 ft: 678 corp: 1/180b exec/s: 0 rss: 414Mb
Slowest unit: 48 s:
artifact_prefix='/tmp/tmp2t8g9rry/'; Test unit written to /tmp/tmp2t8g9rry/slow-unit-07bde8306e295aead3f608d74ed1f5d81b7d9727
#4	INITED cov: 513 ft: 678 corp: 2/4763Kb exec/s: 0 rss: 414Mb
2026-04-03 14:28:37,435 - root - INFO - Uploading corpus in /github/workspace/cifuzz-corpus/fuzz_catalog for fuzz_catalog.
2026-04-03 14:28:38,428 - root - INFO - Done uploading corpus.
2026-04-03 14:28:38,428 - root - INFO - Deleting corpus and seed corpus of fuzz_catalog to save disk.
2026-04-03 14:28:38,429 - root - INFO - Done deleting.
2026-04-03 14:28:38,429 - root - INFO - Fuzzer fuzz_catalog finished running without reportable crashes.
2026-04-03 14:28:38,429 - root - INFO - No crashes in /github/workspace/out/artifacts. Not uploading.
```

| Field | Meaning | Healthy value |
|-------|---------|---------------|
| `cov` | Lines/branches covered | Growing over time |
| `ft` | Coverage features (finer than cov) | Growing over time |
| `corp` | Corpus size (count / total bytes) | Growing over time |
| `exec/s` | Executions per second | 2–10 (low is OK with large seed) |
| `rss` | Memory usage | Stable, not growing unboundedly |

### Warning signs

| Signal | Meaning | Fix |
|--------|---------|-----|
| `corp: 1/1b` never growing | No coverage signal — trestle not instrumented | Restore `with atheris.instrument_imports()` |
| `exec/s > 10,000` and flat `cov` | Inputs bouncing off validation wall — NIST seed missing | Verify seed downloaded |
| `WARNING: no interesting inputs found` | Same as above | Same fix |
| `Slowest unit: 44s` | NIST catalog parse time — normal | Not a problem if under `-timeout=120` |

### Crash artifacts

When a crash is found, libFuzzer writes the crashing input to a file:

```
artifact_prefix='/tmp/tmpca3q4me_/';
Test unit written to /tmp/tmpca3q4me_/crash-abc123
```

To reproduce the crash locally:

```bash
python tests/fuzz/fuzz_catalog.py /path/to/crash-abc123
```

All Stage 2 crashes are real bugs. Do not silence them — investigate and fix
the underlying trestle defect.

---

## 15. Roadmap for future harnesses

The current harness covers the `Catalog` model. The following models are
planned, roughly in priority order:

| Model | Complexity | Seed source | Blocker |
|-------|-----------|-------------|---------|
| Profile | Medium | NIST FISMA Low/Moderate/High profiles | Profile resolution logic needs stub |
| ComponentDefinition | Medium | trestle test fixtures | None — straightforward |
| SSP | High | Generated from trestle test fixtures | Cross-document UUID refs need stub resolver |
| SAP | High | Generated from trestle test fixtures | Same as SSP |
| SAR | High | Generated from trestle test fixtures | Same as SSP |
| POAM | Low | Not recommended | Better suited for Hypothesis property-based testing |

**Implementation approach for future harnesses:**

The `Catalog` harness can serve as a template. The key steps for each new model
are:

1. Find a real, public, pinned seed document (prefer official government sources).
2. Add the seed download to `build.sh`.
3. Copy `fuzz_catalog.py`, replace `Catalog` with the new model class.
4. Verify round-trip on the seed before enabling in CI.
5. Add a new entry in the `build.sh` `compile_python_fuzzer` section.

For cross-document models (SSP, SAP, SAR), the harness needs to stub out
workspace resolution so the fuzzer operates on a single document without
requiring a full trestle workspace. This is the main technical challenge for
those models.

---

## 16. Troubleshooting

**"NIST seed not found" on startup**

The seed file is required. The harness raises `FileNotFoundError` immediately
if it is absent rather than running silently with near-zero coverage. Run the
`curl` command from section 13.

**"Could not download coverage" in the Build phase**

This happens on the first run because `cifuzz-coverage-latest` does not exist
on `main` yet. Set `bad-build-check: false` and `mode: 'batch'` in
`fuzzing.yml`. Once a run completes and generates the coverage artifact, revert
both settings.

**`100% of fuzz targets seem to be broken`**

The smoke test is timing out. Check that `aaa_smoke_test_seed.json` sorts
before `nist_sp800_53_rev5.json` alphabetically. If you have renamed the tiny
seed to anything starting with a letter after `n`, rename it back to something
starting with `a`.

**`corp: 1/1b` and `exec/s > 50,000` — flat coverage**

The fuzzer has no coverage signal. This means trestle's imports are not
instrumented. Verify that `fuzz_catalog.py` has:

```python
with atheris.instrument_imports():
    from trestle.oscal.catalog import Catalog
    from trestle.common.err import TrestleError
```

If this block was removed (e.g. to work around a timeout), the fuzzer runs but
is completely blind — it cannot guide mutations toward interesting code paths.

**`AttributeError: type object 'Catalog' has no attribute 'parse_raw'`**

The harness is using Pydantic v1 APIs against a trestle installation that uses
Pydantic v2. Update all occurrences of:

- `Catalog.parse_raw(data)` → `Catalog.model_validate_json(data)`
- `obj.json(by_alias=True, exclude_none=True)` → `obj.model_dump_json(by_alias=True, exclude_none=True)`

**Fuzzer runs but never finds crashes**

This is expected and correct behaviour for a healthy codebase. The fuzzer is
exercising trestle's parsing and serialisation logic. No crashes means no
data-corruption bugs were found in this run. The corpus continues to grow and
will provide better starting points for future runs.

**Stage 2 crash from `RuntimeError: Idempotency violation`**

This is a real bug in trestle. The fuzzer found an input that trestle accepts
but cannot round-trip cleanly. Reproduce with:

```bash
python tests/fuzz/fuzz_catalog.py /path/to/crash-file
```

File a bug against trestle with the crashing input attached. Do not silence
this exception — it represents data that users could write and have silently
corrupted on the next save.