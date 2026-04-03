"""Structure-aware fuzzing harness for trestle's OSCAL Catalog model.

Seed strategy
-------------
In CI, build.sh downloads the real NIST SP800-53 rev5 catalog into the seed corpus.
Locally, download it manually (see tests/fuzz/README.md).

Key features:
  - Structure-aware mutator with key deletion
  - Recursion depth guard (MAX_DEPTH)
  - Normalised round-trip idempotency check
  - Proper FuzzedDataProvider usage
  - Two-stage exception handling
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

# Prevent RecursionError on deeply nested OSCAL structures (NIST catalog)
MAX_DEPTH = 32


def _load_seed() -> bytes:
    """Return the NIST catalog as bytes. Raises if missing."""
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    corpus_path = os.path.join(exe_dir, 'fuzz_catalog_seed_corpus', 'nist_sp800_53_rev5.json')

    if os.path.exists(corpus_path):
        logger.info('Using NIST SP800-53 rev5 catalog as fuzz seed: %s', corpus_path)
        with open(corpus_path, 'rb') as f:
            return f.read()

    raise FileNotFoundError(
        f'NIST seed not found at {corpus_path}. '
        'Run build.sh or download manually (see tests/fuzz/README.md).'
    )


_SEED: bytes = _load_seed()


def _mut(data, fdp, depth: int = 0):
    """Recursively mutate JSON-compatible object (dict/list/scalar)."""
    if depth >= MAX_DEPTH:
        return data

    if isinstance(data, dict):
        keys = list(data.keys())
        for key in keys:
            choice = fdp.ConsumeIntInRange(0, 2)  # 0=mutate, 1=skip, 2=delete
            if choice == 0:
                data[key] = _mut(data[key], fdp, depth + 1)
            elif choice == 2:
                del data[key]  # Q3: exercises missing required fields
        return data

    elif isinstance(data, list):
        if data:
            idx = fdp.ConsumeIntInRange(0, len(data) - 1)
            action = fdp.ConsumeIntInRange(0, 2)  # 0=mutate, 1=skip, 2=pop
            if action == 0:
                data[idx] = _mut(data[idx], fdp, depth + 1)
            elif action == 2:
                data.pop(idx)
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
    """Normalise for stable comparison (ignore order, None/empty fields)."""
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
            return normalised_items

    return obj


def _idempotency_violation(obj1: Catalog, obj2: Catalog) -> bool:
    """Return True if objects differ after normalisation (Q5)."""
    try:
        d1 = json.loads(obj1.json(by_alias=True, exclude_none=True))
        d2 = json.loads(obj2.json(by_alias=True, exclude_none=True))
        return _normalise(d1) != _normalise(d2)
    except Exception:
        return True


def custom_mutator(data: bytes, max_size: int, seed: int) -> bytes:
    """Structure-aware mutator anchored to real OSCAL structure (see fuzz_docs.md)."""
    try:
        js = json.loads(data)
    except Exception:
        js = json.loads(_SEED)   # fallback to known-good seed

    fdp = atheris.FuzzedDataProvider(data)
    mutated = _mut(js, fdp)

    result = json.dumps(mutated, ensure_ascii=False).encode('utf-8')
    return result[:max_size]


def testoneinput(data: bytes) -> None:
    """Round-trip idempotency test for OSCAL Catalog (details in fuzz_docs.md)."""
    if not data:
        return

    raw = data

    # Strip optional OSCAL envelope {"catalog": {...}}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "catalog" in parsed and len(parsed) == 1:
            raw = json.dumps(parsed["catalog"]).encode()
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass

    try:
        obj1 = Catalog.parse_raw(raw)
    except (ValidationError, json.JSONDecodeError, UnicodeDecodeError, ValueError, TrestleError):
        return  # Stage 1: expected for mutated input

    # Stage 2: round-trip — any failure here is a real bug
    try:
        exported = obj1.json(by_alias=True, exclude_none=True)
        obj2 = Catalog.parse_raw(exported)

        if _idempotency_violation(obj1, obj2):
            raise RuntimeError(f'Idempotency violation. Input (truncated): {data[:200]!r}')

    except (TrestleError, RecursionError, AttributeError, RuntimeError) as e:
        logger.error('CRASH DETECTED: %s: %s', type(e).__name__, e)
        raise


def _validate_seed_on_startup(seed_path: str) -> None:
    """Fail fast if the NIST seed is invalid or doesn't round-trip."""
    with open(seed_path, "rb") as f:
        raw = f.read()

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "catalog" in parsed and len(parsed) == 1:
            raw = json.dumps(parsed["catalog"]).encode()
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"NIST seed is not valid JSON: {exc}") from exc

    try:
        obj = Catalog.parse_raw(raw)
        obj2 = Catalog.parse_raw(obj.json(by_alias=True, exclude_none=True))
        print(f"INFO: NIST seed validated — {len(raw):,} bytes, {len(obj.groups or [])} groups")
    except Exception as exc:
        raise RuntimeError(f"NIST seed validation failed: {exc}") from exc


def main() -> None:
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    seed_corpus_dir = os.path.join(exe_dir, "fuzz_catalog_seed_corpus")
    nist_seed = os.path.join(seed_corpus_dir, "nist_sp800_53_rev5.json")

    if not os.path.isfile(nist_seed):
        raise FileNotFoundError(f"NIST seed not found at {nist_seed}. See README for instructions.")

    _validate_seed_on_startup(nist_seed)

    # Override ClusterFuzzLite defaults
    sys.argv = [arg for arg in sys.argv if not arg.startswith("-timeout=")]
    sys.argv.append("-timeout=120")

    flags = [
        '-max_len=10000000',
        '-len_control=0',
        '-mutate_depth=20',
        '-timeout=120',
    ]

    fuzz_args = sys.argv + flags
    if os.path.isdir(seed_corpus_dir):
        fuzz_args.append(seed_corpus_dir)

    atheris.Setup(fuzz_args, testoneinput, custom_mutator=custom_mutator)
    atheris.Fuzz()
    os._exit(0)


if __name__ == '__main__':
    main()