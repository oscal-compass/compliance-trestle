#!/bin/bash -eu

pip3 install atheris
pip3 install "$SRC/compliance-trestle"

# Download the real NIST SP800-53 rev5 catalog as the fuzz seed corpus.
# Using the pinned commit from usnistgov/oscal-content for reproducibility.
SEED_URL="https://raw.githubusercontent.com/usnistgov/oscal-content/941c978d14c57379fbf6f7fb388f675067d5bff7/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json"
CORPUS_DIR="$OUT/fuzz_catalog_seed_corpus"
mkdir -p "$CORPUS_DIR"
curl -fsSL "$SEED_URL" -o "$CORPUS_DIR/nist_sp800_53_rev5.json"

compile_python_fuzzer "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py"