#!/bin/bash -eu

pip3 install atheris
pip3 install "$SRC/compliance-trestle"

PYTHON_PATH=$(which python3)

python3 - << EOF
shebang = "#!${PYTHON_PATH}\n"
with open("$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py", "r") as f:
    content = f.read()
with open("$OUT/fuzz_catalog", "w") as f:
    f.write(shebang + content)
EOF

chmod +x "$OUT/fuzz_catalog"