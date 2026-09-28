#!/usr/bin/env bash
# run from the root of compliance trestle

# This setup is only for OSX - milage will vary on other platforms

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pip install --require-hashes -r "$SCRIPT_DIR/profiling-requirements.txt"
brew install graphviz
