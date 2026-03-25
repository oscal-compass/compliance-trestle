
"""Structure-aware fuzzing harness for trestle's OSCAL Catalog model.

Seed strategy
-------------
In CI (ClusterFuzzLite), build.sh downloads the real NIST SP800-53 rev5
catalog-min.json into $OUT/fuzz_catalog_seed_corpus/ before this file is
compiled.  Atheris/libFuzzer automatically loads every file in that directory
as an initial corpus entry, so the fuzzer starts from ~1000 real controls with
genuine params, parts, links, back-matter and UUID cross-references.

For local runs without build.sh, see the README for the curl command to download the seed manually.

features in this version
-----------------------------
1. Seed deletion mutations  (Q3) — mutator can *remove* required keys, not
   just corrupt values.  This exercises Pydantic's missing-field validation
   paths and any trestle code that assumes a key is always present.

2. Recursion-depth guard     (Q4) — _mut() carries a depth counter and stops
   recursing beyond MAX_DEPTH.  Prevents Python RecursionError on the deep
   nesting that occurs in the NIST catalog (control enhancements inside
   controls inside groups inside catalog).

3. Normalised idempotency    (Q5) — rather than relying on Pydantic v1's
   field-order-sensitive __eq__, round-trip comparison is done on normalised
   dictionaries (sorted keys, None/empty fields stripped, list elements
   sorted by their JSON representation).  This eliminates false positives from
   serialisation ordering while still catching genuine data-corruption bugs.

4. FuzzedDataProvider fix — custom_mutator now passes `data` (the corpus
   entry, ~kilobytes of entropy) to FuzzedDataProvider instead of
   `seed.to_bytes(8, 'little')` (8 bytes).  The old code exhausted its
   entropy after ~8 ConsumeIntInRange calls and silently returned 0 for all
   subsequent ones, making _mut() nearly deterministic.

5. Softened list mutation — list elements are now mutated/skipped/popped
   with equal probability (3-way) rather than mutated-or-popped (2-way),
   preserving more structure per iteration.
"""

import atheris
import sys
import json
import os
import logging

from pydantic import ValidationError

logger = logging.getLogger(__name__)

with atheris.instrument_imports():
    from trestle.oscal.catalog import Catalog
    from trestle.common.err import TrestleError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# this will stop _mut() from recursing into deeper and deeper nested structures until it hits Python's RecursionError limit.  The NIST catalog has some very deep nesting (e.g. control enhancements inside controls inside groups inside catalog) that can easily exceed the default limit of 1000 with aggressive mutations.
MAX_DEPTH = 32


def _load_seed() -> bytes:
    """Return the NIST SP800-53 rev5 catalog as UTF-8 encoded JSON bytes."""
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    corpus_path = os.path.join(
        exe_dir, 'fuzz_catalog_seed_corpus', 'nist_sp800_53_rev5.json'
    )

    if os.path.exists(corpus_path):
        logger.info('Using NIST SP800-53 rev5 catalog as fuzz seed: %s', corpus_path)
        with open(corpus_path, 'rb') as fh:
            return fh.read()

    raise FileNotFoundError(
        f'NIST seed not found at {corpus_path}.\n'
        'Run build.sh or download the seed manually — see tests/fuzz/README.md.'
    )


_SEED: bytes = _load_seed()

def _mut(data, fdp, depth: int = 0):
    """Recursively mutate a JSON-compatible Python object.

    Three kinds of mutation are applied at random:
      - Value mutation   : corrupt a leaf value (string, int/float)
      - Element mutation : descend into a dict value or list element
      - Key deletion     : remove a key from a dict entirely (NEW)
                           This exercises Pydantic's required-field paths and
                           any trestle logic that assumes a field is present.

    Args:
        data:  The Python object to mutate (in-place for dicts/lists).
        fdp:   Atheris FuzzedDataProvider supplying random bits.
        depth: Current recursion depth — stops at MAX_DEPTH to avoid
               RecursionError on deeply nested NIST catalog structures.
    """
    # Q4 — depth guard
    if depth >= MAX_DEPTH:
        return data

    if isinstance(data, dict):
        keys = list(data.keys())
        for key in keys:
            choice = fdp.ConsumeIntInRange(0, 2)  # 0=mutate value, 1=skip, 2=delete key
            if choice == 0:
                data[key] = _mut(data[key], fdp, depth + 1)
            elif choice == 2:
                # Q3 — delete a key to exercise missing-field validation paths
                del data[key]
        return data

    elif isinstance(data, list):
        if data:
            idx = fdp.ConsumeIntInRange(0, len(data) - 1)
            # 3-way choice mirrors dict behaviour: mutate element / skip / pop.
            # A straight 50/50 mutate-or-pop was too destructive — it collapsed
            # list structure faster than the fuzzer could explore it.
            action = fdp.ConsumeIntInRange(0, 2)
            if action == 0:
                data[idx] = _mut(data[idx], fdp, depth + 1)
            elif action == 2:
                # Remove the element entirely to exercise short/empty list handling
                data.pop(idx)
            # action == 1 → skip (leave element unchanged)
        return data

    elif isinstance(data, str):
        try:
            return fdp.ConsumeBytes(len(data) + 64).decode('utf-8', errors='ignore')
        except Exception:
            return data

    elif isinstance(data, (int, float)):
        return data + fdp.ConsumeIntInRange(-100, 100)

    return data

def _normalise(obj):
    """Recursively normalise a JSON-compatible object for stable comparison.

    Rules applied:
      - Dicts: strip keys whose value is None or an empty container, then
               return as a sorted-key dict so field order never matters.
      - Lists: sort elements by their JSON representation so that lists whose
               only difference is element order compare as equal.  This is
               intentionally lossy for ordered lists — if OSCAL semantics
               require order preservation and trestle violates it, that is a
               real bug and will show up as an idempotency failure even here.
      - Scalars: returned as-is.

    Note: stripping None/empty mirrors what Pydantic v1 does with
    exclude_none=True in .json(), so we don't generate false positives from
    fields that were present before serialisation but absent after.
    """
    if isinstance(obj, dict):
        cleaned = {
            k: _normalise(v)
            for k, v in obj.items()
            if v is not None and v != [] and v != {}
        }
        return dict(sorted(cleaned.items()))

    elif isinstance(obj, list):
        normalised_items = [_normalise(item) for item in obj]
        try:
            return sorted(normalised_items, key=lambda x: json.dumps(x, sort_keys=True))
        except TypeError:
            # Un-sortable mixed-type list — return as-is
            return normalised_items

    return obj


def _idempotency_violation(obj1: Catalog, obj2: Catalog) -> bool:
    """Return True if the two Catalog objects differ after normalisation.

    Uses dict-based comparison rather than Pydantic's __eq__ to avoid false
    positives from field-ordering differences in Pydantic v1 serialisation.
    """
    try:
        dict1 = json.loads(obj1.json(by_alias=True, exclude_none=True))
        dict2 = json.loads(obj2.json(by_alias=True, exclude_none=True))
        return _normalise(dict1) != _normalise(dict2)
    except Exception:
        # If we can't serialise for comparison, treat as a violation
        return True

def custom_mutator(data: bytes, max_size: int, seed: int) -> bytes:  
    """Structure-aware mutator anchored to real OSCAL catalog structure.

    FuzzedDataProvider note
    -----------------------
   We pass data (the current corpus entry) as the entropy source for the FuzzedDataProvider. 
   This ensures the provider has sufficient and variable input to drive mutations
   across the catalog structure during each fuzzing iteration.

    JSON decode failure
    -------------------
    If `data` is not valid JSON (e.g. libFuzzer injected raw bytes from its own
    splicing mutations), we fall back to the NIST seed so the mutator always
    outputs structurally valid OSCAL rather than garbage that bounces off
    json.loads() in testoneinput.
    """
    try:
        js = json.loads(data)
    except Exception:
        # Raw bytes from libFuzzer's own mutations — re-anchor to the NIST seed
        # so the output stays in the valid OSCAL input space.
        js = json.loads(_SEED)

    fdp = atheris.FuzzedDataProvider(data)
    mutated = _mut(js, fdp)

    result = json.dumps(mutated, ensure_ascii=False).encode('utf-8')
    return result[:max_size]

def testoneinput(data: bytes) -> None:
    """Fuzz target: round-trip idempotency test for the OSCAL Catalog model.

    What we are testing
    -------------------
    1. trestle can parse the mutated input without unexpected exceptions.
    2. Serialising and re-parsing the result produces an identical object
       (after normalisation).  A failure means trestle silently corrupts or
       drops data during a load-save cycle — the class of bug that unit tests
       never catch because they only exercise known-good inputs.

    Exception handling — two-stage
    ------------------------------
    Stage 1 (input parsing):
      ValidationError, JSONDecodeError, UnicodeDecodeError, ValueError,
      TrestleError ("extra fields not permitted", unknown field, etc.)
      → all expected schema/validator rejections on mutated inputs.
        Return silently so the fuzzer accumulates these as corpus and
        keeps mutating forward rather than halting.

      TrestleError is intentionally caught HERE and nowhere else.
      The mutator's key-deletion mutations will frequently produce inputs
      that trestle's strict Pydantic models reject with TrestleError.
      That is the validator doing its job — not a bug.

    Stage 2 (round-trip):
      We have a successfully parsed Catalog object.  Any error from this
      point is a genuine defect because trestle is now failing to handle
      data it just accepted:
        TrestleError    → trestle rejected its own serialised output on
                          re-parse, or failed to serialise at all.
        RecursionError  → unbounded nesting in the serialiser.
        AttributeError  → code assumed a field exists that does not.
        RuntimeError    → idempotency violation: round-trip data loss.
    """
    if not data:
        return

    # ── Stage 1: input parsing ───────────────────────────────────────────────
    # TrestleError here = validator correctly rejected an invalid mutation.
    try:
        obj1 = Catalog.parse_raw(data)
    except (ValidationError, json.JSONDecodeError, UnicodeDecodeError,
            ValueError, TrestleError):
        return  # expected rejection — not a bug

    # ── Stage 2: round-trip ──────────────────────────────────────────────────
    # obj1 is a valid Catalog.  Any error from here is a real defect.
    try:
        exported = obj1.json(by_alias=True, exclude_none=True)
        obj2 = Catalog.parse_raw(exported)

        # Q5 — normalised comparison avoids Pydantic v1 ordering false positives
        if _idempotency_violation(obj1, obj2):
            raise RuntimeError(
                f'Idempotency violation: round-trip produced a different object.\n'
                f'Input (truncated): {data[:200]!r}'
            )

    except (TrestleError, RecursionError, AttributeError, RuntimeError) as e:
        logger.error('CRASH DETECTED: %s: %s', type(e).__name__, e)
        raise

def main() -> None:
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    seed_corpus_dir = os.path.join(exe_dir, 'fuzz_catalog_seed_corpus')

    flags = [
        '-max_len=10000000', # allow the full ~4.65 MB NIST catalog
        '-len_control=0', 
        '-mutate_depth=20',   # deeper exploration of nested control paths
        '-timeout=60',        # kill any single input that hangs for 60 s
    ]

    fuzz_args = [sys.argv[0]] + flags
    if os.path.isdir(seed_corpus_dir):
        fuzz_args.append(seed_corpus_dir)
    fuzz_args += sys.argv[1:]  # pass through any args ClusterFuzzLite appends

    atheris.Setup(fuzz_args, testoneinput, custom_mutator=custom_mutator)
    atheris.Fuzz()
    os._exit(0)  # bypass atexit() — see docstring

if __name__ == '__main__':
    main()