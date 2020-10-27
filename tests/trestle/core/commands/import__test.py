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
"""Tests for trestle import command."""


def test_import_success(tmp_dir):
    """Test for success cross multiple models."""
    pass


def test_import_failure_invalid_model(tmp_dir):
    """Test model failures throw errors and exit badly."""
    pass


def test_failure_reference_inside_trestle_project(tmp_dir):
    """Ensure failure if a reference pulls in an object which is inside the current context."""
    pass


def test_failure_duplicate_output_key(tmp_dir):
    """Fail if output name and type is duplicated."""
    pass
