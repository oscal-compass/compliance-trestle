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

# This script is designed to test whether the bdist is behaving correctly.
# Note that it encodes the stanndard testing protocol and should be updated.

# Build trestle as a wheel
python setup.py bdist_wheel
# Create an isolated venv with fresh packages
mkdir tmp_bin_test
python -m venv tmp_bin_test/venv
source tmp_bin_test/venv/bin/activate
# Install in the compliance-trestle wheel away from the source repo
python -m pip install dist/*.whl
# install required test libraries
python -m pip install pytest-xdist
# this is required to get away from the damn base directory
cd tmp_bin_test
# link in the tests.
ln -s ../tests
# Ensure nist content is accessible (requires submodules to be checked out.)
ln -s ../nist-content
python -m pytest --exitfirst -n auto

