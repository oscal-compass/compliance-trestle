#!/bin/bash -eu
# ... pip installs ...

# Download Raw JSON
SEED_URL="https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json"
CORPUS_DIR="$OUT/fuzz_catalog_seed_corpus"
mkdir -p "$CORPUS_DIR"
curl -fsSL "$SEED_URL" -o "$CORPUS_DIR/nist_sp800_53_rev5.json"

compile_python_fuzzer "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py"