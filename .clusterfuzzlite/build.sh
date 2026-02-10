#!/bin/bash -eu

pip3 install .

cat > "$OUT/fuzz_catalog" <<EOF
#!/bin/sh
# LLVMFuzzerTestOneInput
exec python3 "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py" "\$@"
EOF

chmod +x "$OUT/fuzz_catalog"
