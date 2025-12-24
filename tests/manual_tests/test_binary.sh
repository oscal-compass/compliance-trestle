#!/usr/bin/env bash
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Binary Distribution Test
# ========================
# This test verifies the wheel package works correctly when installed
# in isolation, ensuring all required assets are bundled properly.
# This cannot be done with `hatch test` as that uses editable installs.

set -euo pipefail

TEST_DIR="tmp_bin_test"

# Clean up any previous test artifacts
rm -rf "$TEST_DIR" dist/

# Build wheel using hatch
hatch build -t wheel

# Create isolated test environment
python -m venv "$TEST_DIR/venv"
source "$TEST_DIR/venv/bin/activate"

# Install wheel and test dependencies
pip install --quiet dist/*.whl pytest pytest-xdist

# Run tests from isolated directory (away from source)
cd "$TEST_DIR"
ln -s ../tests
ln -s ../nist-content

pytest --exitfirst -n auto tests/
