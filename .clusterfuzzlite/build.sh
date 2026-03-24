#!/bin/bash -eu

# 1. Install Atheris and Trestle
pip3 install atheris
pip3 install "$SRC/compliance-trestle"

# 2. Setup Corpus Directory using absolute $OUT
CORPUS_DIR="$OUT/fuzz_catalog_seed_corpus"
mkdir -p "$CORPUS_DIR"

# 3. Download the seed with -f (fail on server error) and -L (follow redirects)
SEED_URL="https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json"

echo "Downloading seed corpus..."
curl -fsSL "$SEED_URL" -o "$CORPUS_DIR/nist_sp800_53_rev5.json"

# 4. VERIFICATION: Stop the build if the file is missing or empty
if [ ! -s "$CORPUS_DIR/nist_sp800_53_rev5.json" ]; then
  echo "ERROR: Seed catalog is missing or empty at $CORPUS_DIR"
  ls -la "$OUT"
  exit 1
fi

# 5. Compile the fuzzer
compile_python_fuzzer "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py"