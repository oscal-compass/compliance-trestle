#!/bin/bash -eu

pip3 install .

cp "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py" "$OUT/"

cat > "$OUT/fuzz_catalog" << 'EOF'
#!/bin/sh
# Determine the directory where this wrapper resides
SCRIPT_DIR=$(dirname "$0")
exec python3 "$SCRIPT_DIR/fuzz_catalog.py" "$@"
EOF

chmod +x "$OUT/fuzz_catalog"

