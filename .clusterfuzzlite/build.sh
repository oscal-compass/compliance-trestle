#!/bin/bash -eu

# Install project and fuzzing dependency
pip3 install atheris
pip3 install "$SRC/compliance-trestle"

# compile_python_fuzzer is provided by base-builder-python.
# It handles $LIB_FUZZING_ENGINE linking, output to $OUT, and
# generates the correct wrapper script automatically.
compile_python_fuzzer "$SRC/compliance-trestle/tests/fuzz/fuzz_catalog.py"