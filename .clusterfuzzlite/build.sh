#!/bin/bash -eu

pip3 install atheris
pip3 install "$SRC/compliance-trestle"

CORPUS_DIR="$OUT/fuzz_catalog_seed_corpus"
mkdir -p "$CORPUS_DIR"

# 1. Create a TINY seed for the build-verification (Smoke Test)
# This ensures the fuzzer starts instantly during the build phase
echo '{"catalog": {"uuid": "550e8400-e2b9-11d4-a716-446655440000", "metadata": {"title": "Fast Seed", "last-modified": "2026-03-24T00:00:00Z", "version": "1.0", "oscal-version": "1.1.2"}}}' > "$CORPUS_DIR/tiny_seed.json"

# 2. Download the BIG NIST catalog for the actual fuzzing run
SEED_URL="https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json"
curl -fsSL "$SEED_URL" -o "$CORPUS_DIR/nist_sp800_53_rev5.json"

# 3. Compile
compile_python_fuzzer "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py"