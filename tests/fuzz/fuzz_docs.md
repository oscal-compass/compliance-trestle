# Fuzzing Harness for compliance-trestle

This folder contains **structure-aware fuzzing** for trestle's OSCAL models, starting with the `Catalog` model.

The main purpose is to automatically find bugs in how trestle parses and saves OSCAL JSON documents — especially silent data corruption or unexpected crashes that normal unit tests usually miss.

## Why This Fuzzer Exists

* Helps improve our OpenSSF Scorecard fuzzing score.
* Finds real-world issues in deep nesting, missing fields, UUID handling, parameter resolution, and round-trip behaviour.
* Runs automatically on every pull request (10 minutes, non-blocking).
* Uses real NIST data so the fuzzer works with production-like documents instead of artificial test cases.

## What It Actually Does

On every iteration the fuzzer:

1. Takes a (mutated) OSCAL JSON document.
2. Parses it into a trestle `Catalog` Pydantic model.
3. Serialises the model back to JSON.
4. Parses that JSON again into a second `Catalog` object.
5. Checks whether the two objects are semantically identical.

If they differ → it raises a crash so the bug is recorded.

The mutator deliberately deletes required keys, removes list items, corrupts strings/numbers, and changes structure to stress-test trestle’s parsing and serialisation logic.

## Key Files

| File                            | Purpose                                             |
| ------------------------------- | --------------------------------------------------- |
| `fuzz_catalog.py`               | Main fuzzing harness (this is the file you edit)    |
| `.clusterfuzzlite/build.sh`     | Downloads the real NIST seed and builds the fuzzer  |
| `.clusterfuzzlite/project.yaml` | Configures ClusterFuzzLite for Python               |
| `.github/workflows/fuzzing.yml` | GitHub Actions workflow that runs the fuzzer on PRs |

## How to Run Locally

### 1. Quick run (uses built-in fallback seed)

```bash
cd /path/to/compliance-trestle

# Install dependencies
pip install -e ".[test]"

# Run the fuzzer
python tests/fuzz/fuzz_catalog.py
```

### 2. Run with the real NIST SP800-53 catalog (strongly recommended)

```bash
# Create the seed directory
mkdir -p .clusterfuzzlite/out/fuzz_catalog_seed_corpus

# Download the real NIST catalog
curl -fsSL "https://raw.githubusercontent.com/usnistgov/oscal-content/941c978d14c57379fbf6f7fb388f675067d5bff7/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json" \
  -o .clusterfuzzlite/out/fuzz_catalog_seed_corpus/nist_sp800_53_rev5.json

# Start fuzzing
python tests/fuzz/fuzz_catalog.py
```

Press Ctrl + C to stop.

## Data Model Compatibility

Not all OSCAL models are equally easy to fuzz with this approach. Here's the current status and future plans:

| Model                      | Round-trip Fit | Seed Availability                     | Current Status      | Notes                                                                             |
| -------------------------- | -------------- | ------------------------------------- | ------------------- | --------------------------------------------------------------------------------- |
| Catalog                    | Excellent      | Real NIST SP800-53 rev5 (public)      | Done (this harness) | Self-contained, deep nesting, perfect for structure-aware fuzzing                 |
| Profile                    | Very Good      | NIST FISMA Low/Moderate/High profiles | Planned (next)      | Needs extra test for profile resolution logic                                     |
| Component Definition       | Very Good      | Available in trestle test fixtures    | Planned (next)      | Similar structure to Catalog                                                      |
| System Security Plan (SSP) | Good           | Generated from test fixtures          | Planned (later)     | Cross-document UUID references need special handling (stub resolver or workspace) |
| SAP                        | Good           | Generated from test fixtures          | Planned (later)     | References SSP — similar challenges as SSP                                        |
| SAR                        | Good           | Generated from test fixtures          | Planned (later)     | References SAP                                                                    |
| POAM                       | Shallow        | Low value                             | Not recommended     | Better suited for property-based testing (Hypothesis)                             |

## Future Plans

* Next step: Generalise the harness into a reusable factory and add fuzz_profile.py + fuzz_component_def.py.
* Later: Implement SSP, SAP, and SAR using document-local isolation first (strip cross-document resolution) to keep things simple.
* Long-term: Add a nightly long-running job and support for full workspace-based fuzzing.

## Important Technical Details (for maintainers)

### Harness Architecture & ClusterFuzzLite Integration
The harness uses [Atheris](https://github.com/google/atheris) for coverage-guided Python fuzzing and integrates with ClusterFuzzLite via OSS-Fuzz base images (`Dockerfile`).
During CI builds (`build.sh`), the real NIST SP800-53 catalog is downloaded directly into `$OUT/fuzz_catalog_seed_corpus/`. libFuzzer loads this automatically as the initial corpus, ensuring that the fuzzer starts with ~1000 structurally sound real-world controls with genuine UUID links and parameters instead of byte-level garbage.

### Structure-Aware Mutator Design
The custom mutator (`_mut`) is specifically designed to stress-test Pydantic validation paths and Trestle's data handling without destroying the OSCAL structure immediately:
* **Seed deletion mutations**: The mutator can *remove* required keys entirely, not just corrupt their values. This aggressively exercises Pydantic's missing-field validation paths.
* **Recursion-depth guard**: To prevent native Python `RecursionError` exceptions that obscure real bugs on deeply nested catalogs, the mutator tracks nesting depth and skips mutating beyond `MAX_DEPTH = 32`.
* **Softened list mutation**: List elements are mutated, skipped, or popped with equal (3-way) probability. This preserves more of the document's structure per iteration compared to naive dropping.
* **Entropy Management**: The custom mutator continuously passes the corpus payload to `FuzzedDataProvider` to maintain rich deterministic fuzzing entropy across all sub-fields throughout the run.

### Normalised Idempotency Comparison
Comparing the first parse against the round-trip parse uses a strictly normalised approach (`_normalise`). Instead of relying on Pydantic v1's field-order-sensitive `__eq__`, the round-trip comparison uses sorted keys, strips `None`/empty fields, and sorts list elements by their JSON representation. This eliminates false positives caused by generic serialization ordering quirks while reliably catching genuine data corruption bugs.

### Expected Error Handling
Expected Pydantic `ValidationError`s raised due to structural fuzzing are explicitly caught and ignored. Only genuinely unhandled internal errors (`TrestleError`, `AttributeError`, etc.) or idempotency violations trigger a fuzzer crash, signaling a real bug to maintainers.

### Technical debt note:
This harness is written for Pydantic v1 (the version currently used by trestle). When trestle migrates to Pydantic v2, the parsing/serialisation calls (`parse_raw`, `.json()`) must be updated to the v2 equivalents (`model_validate_json`, `.model_dump_json`). The normalisation logic should also be re-evaluated as v2's strictness might eliminate the need for custom sorting.

## Troubleshooting

* "NIST seed not found" warning → This is expected on fresh clones. The fallback seed still works, but using the real NIST file gives much better coverage.
* Fuzzer feels too slow or not mutating enough → Make sure you are using the real NIST seed.
* Too many crashes → Check the exception handling lists in testoneinput() or the normalisation logic.
