#!/bin/bash -eu

pip3 install atheris
pip3 install "$SRC/compliance-trestle"

CORPUS_DIR="$OUT/fuzz_catalog_seed_corpus"
mkdir -p "$CORPUS_DIR"


# this is used to pass the smoke test, which runs the first corpus entry immediately after build to verify the fuzzer doesn't crash on startup. The NIST catalog is 4.65 MB and takes several seconds to parse, which can time out the smoke test. This tiny but structurally valid catalog parses in milliseconds and lets the smoke test pass instantly.
echo '{"catalog":{"uuid":"550e8400-e29b-41d4-a716-446655440000","metadata":{"title":"Smoke Test Seed","last-modified":"2026-03-24T00:00:00Z","version":"1.0.0","oscal-version":"1.1.3"}}}' \
    > "$CORPUS_DIR/tiny_seed.json"

# ── Seed 2: real NIST SP800-53 rev5 catalog for coverage depth ──────────────
# Pinned to a specific commit so the seed is reproducible across all builds.
# If a bug is found, the exact seed that produced it can always be recovered.
#
# To update the pin:
#   1. Find the latest commit hash on usnistgov/oscal-content
#   2. Verify: python3 -c "from trestle.oscal.catalog import Catalog;
#                           Catalog.parse_raw(open('catalog-min.json').read())"
#   3. Update SEED_COMMIT below
#
SEED_COMMIT="941c978d14c57379fbf6f7fb388f675067d5bff7"
SEED_URL="https://raw.githubusercontent.com/usnistgov/oscal-content/${SEED_COMMIT}/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog-min.json"

echo "Downloading NIST SP800-53 rev5 catalog (commit ${SEED_COMMIT})..."
if curl -fsSL --retry 3 --retry-delay 5 "$SEED_URL" \
        -o "$CORPUS_DIR/nist_sp800_53_rev5.json"; then
    echo "NIST seed downloaded: $(wc -c < "$CORPUS_DIR/nist_sp800_53_rev5.json") bytes"
else
    echo "WARNING: NIST seed download failed. Fuzzer will use fallback seed only." >&2
fi

compile_python_fuzzer "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py"