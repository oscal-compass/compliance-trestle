# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for Results class."""

import json
import pathlib

from trestle.transforms.results import Results


def test_oscal_serialize_json_bytes_unwrapped():
    """Test oscal_serialize_json_bytes with wrapped=False to cover line 60."""
    results = Results(root=[])
    json_bytes = results.oscal_serialize_json_bytes(pretty=False, wrapped=False)

    assert isinstance(json_bytes, bytes)
    data = json.loads(json_bytes)
    # When unwrapped, should be a list directly
    assert isinstance(data, list)
    assert data == []


def test_oscal_serialize_json_bytes_not_pretty():
    """Test oscal_serialize_json_bytes with pretty=False to cover line 69."""
    results = Results(root=[])
    json_bytes = results.oscal_serialize_json_bytes(pretty=False, wrapped=True)

    assert isinstance(json_bytes, bytes)
    # Compact JSON
    json_str = json_bytes.decode('utf-8')
    data = json.loads(json_str)
    assert 'results' in data


def test_oscal_serialize_json_unwrapped():
    """Test oscal_serialize_json with wrapped=False to cover line 81."""
    results = Results(root=[])
    json_str = results.oscal_serialize_json(pretty=False, wrapped=False)

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    # When unwrapped, should be a list directly
    assert isinstance(data, list)
    assert data == []


def test_oscal_write_yaml(tmp_path: pathlib.Path):
    """Test oscal_write with YAML file to cover lines 100-102."""
    results = Results(root=[])
    output_file = tmp_path / 'results.yaml'

    results.oscal_write(output_file)

    assert output_file.exists()
    # Verify it's valid YAML by reading it
    from ruamel.yaml import YAML

    yaml = YAML(typ='safe')
    with output_file.open('r') as f:
        data = yaml.load(f)
    assert 'results' in data
    assert data['results'] == []


# Made with Bob
