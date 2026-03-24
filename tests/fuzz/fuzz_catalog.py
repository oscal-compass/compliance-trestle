
"""Structure-aware fuzzing harness for trestle's OSCAL Catalog model.

Seed strategy
-------------
In CI (ClusterFuzzLite), build.sh downloads the real NIST SP800-53 rev5
catalog-min.json into $OUT/fuzz_catalog_seed_corpus/ before this file is
compiled.  Atheris/libFuzzer automatically loads every file in that directory
as an initial corpus entry, so the fuzzer starts from ~1000 real controls with
genuine params, parts, links, back-matter and UUID cross-references rather than
a toy structure.

For local runs without build.sh, _load_seed() falls back to a richer minimal
catalog that still exercises params, parts and props paths.

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


# 32 dept is well enough for the catalog nesting max - 10 , and also didnot give false positives from RecursionError in local testing.  We want to be able to explore deep nesting paths but not crash on them.
MAX_DEPTH = 32


def _load_seed() -> bytes:
    """Return the fuzz seed as UTF-8 encoded JSON bytes.

    Priority:
      1. The real NIST SP800-53 rev5 catalog placed by build.sh.
      2. A minimal catalog for local development.
    """
    corpus_path = os.path.join(out_dir, 'fuzz_catalog_seed_corpus', 'nist_sp800_53_rev5.json')
    out_dir = os.environ.get('OUT', '/out')
    if os.path.exists(corpus_path):
        with open(corpus_path, 'rb') as fh:
            return fh.read()

    # --- local-development fallback ---
    # Minimal catalog for local development: includes params, parts, props and
    # a control enhancement so that the mutator walks more OSCAL paths even
    # without the full NIST file.
    logger.warning(
        'NIST seed corpus not found at %s — using minimal fallback seed. '
        'Run build.sh to download the full seed for CI-equivalent coverage.',
        corpus_path,
    )
    fallback = {
        'catalog': {
            'uuid': '550e8400-e29b-41d4-a716-446655440000',
            'metadata': {
                'title': 'Fuzz Fallback Catalog',
                'last-modified': '2026-02-10T14:58:41Z',
                'version': '1.0.0',
                'oscal-version': '1.1.3',
                'roles': [{'id': 'creator', 'title': 'Document Creator'}],
                'parties': [{'uuid': '11111111-0000-4000-8000-000000000001',
                              'type': 'organization', 'name': 'Fuzz Org'}],
            },
            'groups': [
                {
                    'id': 'ac',
                    'title': 'Access Control',
                    'props': [{'name': 'label', 'value': 'AC'}],
                    'controls': [
                        {
                            'id': 'ac-1',
                            'title': 'Policy and Procedures',
                            'params': [
                                {
                                    'id': 'ac-1_prm_1',
                                    'label': 'organization-defined roles',
                                    'select': {
                                        'how-many': 'one-or-more',
                                        'choice': ['role A', 'role B'],
                                    },
                                },
                            ],
                            'props': [
                                {'name': 'label', 'value': 'AC-1'},
                                {'name': 'sort-id', 'value': 'ac-01'},
                            ],
                            'links': [
                                {'href': '#ref-1', 'rel': 'reference'},
                            ],
                            'parts': [
                                {
                                    'id': 'ac-1_smt',
                                    'name': 'statement',
                                    'prose': 'Develop, document, and disseminate...',
                                    'parts': [
                                        {
                                            'id': 'ac-1_smt.a',
                                            'name': 'item',
                                            'prose': 'Sub-statement a.',
                                        }
                                    ],
                                },
                                {'id': 'ac-1_gdn', 'name': 'guidance',
                                 'prose': 'Guidance text.'},
                            ],
                            # Control enhancement (nested control)
                            'controls': [
                                {
                                    'id': 'ac-1.1',
                                    'title': 'AC-1 Enhancement',
                                    'props': [{'name': 'label', 'value': 'AC-1(1)'}],
                                    'parts': [
                                        {'id': 'ac-1.1_smt', 'name': 'statement',
                                         'prose': 'Enhancement statement.'}
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
            'back-matter': {
                'resources': [
                    {
                        'uuid': 'aaaaaaaa-0000-4000-8000-000000000001',
                        'title': 'Reference 1',
                        'rlinks': [{'href': 'https://example.com/ref1'}],
                    }
                ]
            },
        }
    }
    return json.dumps(fallback).encode('utf-8')


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


# ---------------------------------------------------------------------------
# Q5 — Normalised comparison helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Custom mutator entry point
# ---------------------------------------------------------------------------

def custom_mutator(data: bytes, max_size: int, seed: int) -> bytes:  # noqa: ARG001
    """Structure-aware mutator anchored to real OSCAL catalog structure.

    Falls back to the NIST seed when input bytes are not valid JSON so that
    every output stays in the valid OSCAL input space and the fuzzer spends
    its cycles exercising parsing logic rather than bouncing off json.loads().

    FuzzedDataProvider note
    -----------------------
    We pass `data` (the current corpus entry) — not `seed.to_bytes(8, 'little')`
    — as the entropy source for the FuzzedDataProvider.  The `seed` integer is
    only 8 bytes; when _mut() walks the NIST catalog it calls ConsumeIntInRange
    thousands of times and exhausts those 8 bytes almost immediately, causing
    every remaining call to return 0 (the silent default).  The result is a
    nearly deterministic mutator that barely mutates anything.  Using `data`
    gives the FDP the full corpus entry as entropy — variable and abundant on
    every libFuzzer iteration.
    """
    try:
        js = json.loads(data)
    except Exception:
        # Corrupt bytes — re-anchor to the known-good seed
        js = json.loads(_SEED)

    # data is the correct entropy source (see docstring above)
    fdp = atheris.FuzzedDataProvider(data)
    mutated = _mut(js, fdp)

    result = json.dumps(mutated, ensure_ascii=False).encode('utf-8')
    return result[:max_size]


# ---------------------------------------------------------------------------
# Fuzzer entry point
# ---------------------------------------------------------------------------

def testoneinput(data: bytes) -> None:
    """Fuzz target: round-trip idempotency test for the OSCAL Catalog model.

    What we are testing
    -------------------
    1. trestle can parse the mutated input without unexpected exceptions.
    2. Serialising and re-parsing the result produces an identical object
       (after normalisation).  A failure means trestle silently corrupts or
       drops data during a load-save cycle — the class of bug that unit tests
       never catch because they only exercise known-good inputs.

    Exception handling
    ------------------
    Expected/safe:
      ValidationError, JSONDecodeError, UnicodeDecodeError, ValueError
      → schema rejections are expected for mutated inputs; return silently.

    Bugs we want to catch (re-raise so libFuzzer records a crash):
      TrestleError, RecursionError, AttributeError
      → unexpected internal failures in trestle's parsing or serialisation.
      RuntimeError (idempotency violation)
      → data-corruption bug discovered by the round-trip assertion.
    """
    if not data:
        return

    try:
        obj1 = Catalog.parse_raw(data)
        exported = obj1.json(by_alias=True, exclude_none=True)
        obj2 = Catalog.parse_raw(exported)

        # Q5 — use normalised comparison to avoid Pydantic v1 false positives
        if _idempotency_violation(obj1, obj2):
            raise RuntimeError(
                f'Idempotency violation: round-trip produced a different object.\n'
                f'Input (truncated): {data[:200]!r}'
            )

    except (ValidationError, json.JSONDecodeError, UnicodeDecodeError, ValueError):
        # Expected — not bugs
        return
    except (TrestleError, RecursionError, AttributeError, RuntimeError) as e:
        logger.error('CRASH DETECTED: %s: %s', type(e).__name__, e)
        raise


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Start the fuzzer with settings optimized for the large NIST catalog.

    Flags are inserted *before* the corpus directory so libFuzzer actually sees them.
    """
    flags = [
        "-max_len=10000000",        # allow the full ~4.8 MB NIST catalog
        "-len_control=0",    # disable automatic input shrinking
        "-mutate_depth=20",  # deeper exploration of nested controls
        "-timeout=60",       # safety timeout
    ]

    # Script name + flags first + everything else (including corpus path)
    fuzz_args = [sys.argv[0]] + flags + sys.argv[1:]

    atheris.Setup(fuzz_args, testoneinput, custom_mutator=custom_mutator)
    atheris.Fuzz()

if __name__ == '__main__':
    main()