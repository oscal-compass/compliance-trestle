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

import pytest
from pydantic import ValidationError

from trestle.common.err import TrestleError
from trestle.oscal.assessment_results import Result
from trestle.transforms.results import Results


def _make_result() -> Result:
    """Return a minimal valid Result fixture."""
    return Result.model_validate(
        {
            'uuid': 'a1d20136-37e0-42aa-9834-4e9d8c36d798',
            'title': 'Test Result',
            'description': 'Minimal result for testing.',
            'start': '2023-06-02T08:31:20-04:00',
            'reviewed-controls': {'control-selections': [{'include-controls': [{'control-id': 'ac-6.1'}]}]},
        }
    )


# ---------------------------------------------------------------------------
# Validated construction (min_length=1 enforcement)
# ---------------------------------------------------------------------------


def test_validated_construction_empty_raises():
    """Results(root=[]) via normal construction must raise ValidationError (minItems: 1)."""
    with pytest.raises(ValidationError):
        Results(root=[])


def test_validated_construction_one_result():
    """Results(root=[result]) via normal construction must succeed."""
    result = _make_result()
    results = Results(root=[result])
    assert len(results.root) == 1
    assert results.root[0] == result


# ---------------------------------------------------------------------------
# Serialization with actual content
# ---------------------------------------------------------------------------


def test_oscal_serialize_json_bytes_unwrapped_with_content():
    """oscal_serialize_json_bytes(wrapped=False) with one Result returns a JSON list."""
    results = Results(root=[_make_result()])
    json_bytes = results.oscal_serialize_json_bytes(pretty=False, wrapped=False)

    assert isinstance(json_bytes, bytes)
    data = json.loads(json_bytes)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['uuid'] == 'a1d20136-37e0-42aa-9834-4e9d8c36d798'


def test_oscal_serialize_json_bytes_wrapped_with_content():
    """oscal_serialize_json_bytes(wrapped=True) with one Result returns a dict keyed 'results'."""
    results = Results(root=[_make_result()])
    json_bytes = results.oscal_serialize_json_bytes(pretty=False, wrapped=True)

    assert isinstance(json_bytes, bytes)
    data = json.loads(json_bytes)
    assert 'results' in data
    assert len(data['results']) == 1


def test_oscal_serialize_json_bytes_pretty_with_content():
    """oscal_serialize_json_bytes(pretty=True) produces indented output."""
    results = Results(root=[_make_result()])
    json_bytes = results.oscal_serialize_json_bytes(pretty=True, wrapped=True)

    json_str = json_bytes.decode('utf-8')
    # Indented output contains newlines
    assert '\n' in json_str
    data = json.loads(json_str)
    assert 'results' in data


def test_oscal_serialize_json_unwrapped_with_content():
    """oscal_serialize_json(wrapped=False) with one Result returns a JSON list string."""
    results = Results(root=[_make_result()])
    json_str = results.oscal_serialize_json(pretty=False, wrapped=False)

    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert len(data) == 1


# ---------------------------------------------------------------------------
# oscal_write (empty guard + file output)
# ---------------------------------------------------------------------------


def test_oscal_write_empty_raises(tmp_path: pathlib.Path):
    """oscal_write raises TrestleError when Results is empty (OSCAL minItems: 1)."""
    results = Results.model_construct(root=[])
    with pytest.raises(TrestleError, match='minItems: 1'):
        results.oscal_write(tmp_path / 'results.yaml')


def test_oscal_write_yaml(tmp_path: pathlib.Path):
    """oscal_write with a valid Result writes correct YAML."""
    results = Results(root=[_make_result()])
    output_file = tmp_path / 'results.yaml'

    results.oscal_write(output_file)

    assert output_file.exists()
    from ruamel.yaml import YAML

    yaml = YAML(typ='safe')
    with output_file.open('r') as f:
        data = yaml.load(f)
    assert 'results' in data
    assert len(data['results']) == 1


def test_oscal_write_json(tmp_path: pathlib.Path):
    """oscal_write with a valid Result writes correct JSON."""
    results = Results(root=[_make_result()])
    output_file = tmp_path / 'results.json'

    results.oscal_write(output_file)

    assert output_file.exists()
    with output_file.open('r') as f:
        data = json.load(f)
    assert 'results' in data
    assert len(data['results']) == 1


# Made with Bob
