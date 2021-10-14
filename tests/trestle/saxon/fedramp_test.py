# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Testing fedramp validation functionality."""

import pathlib

import pytest

from tests import test_utils

from trestle.core import const
from trestle.core.err import TrestleError
from trestle.saxon.fedramp import FedrampValidator


def test_init() -> None:
    """Test creating Fedramp validator object."""
    validator = FedrampValidator()
    assert str(validator.baselines_path) != ''
    assert str(validator.baselines_path) != ''


def test_init_invalid_baseline(monkeypatch, tmp_path: pathlib.Path) -> None:
    """Invalid baseline path."""
    # change Fedramp baseline path
    monkeypatch.setattr(const, 'FEDRAM_BASELINE', str(tmp_path / 'invalid_file'))
    with pytest.raises(TrestleError, match='Fedramp baseline directory'):
        FedrampValidator()


def test_init_invalid_registry(monkeypatch, tmp_path: pathlib.Path) -> None:
    """Invalid registry path."""
    # change Fedramp baseline path
    monkeypatch.setattr(const, 'FEDRAMP_REGISTRY', str(tmp_path / 'invalid_file'))
    with pytest.raises(TrestleError, match='Fedramp registry directory'):
        FedrampValidator()


def test_validate_ssp(tmp_path: pathlib.Path) -> None:
    """Test Fedramp SSP validation."""
    file_path = pathlib.Path(test_utils.JSON_FEDRAMP_SSP_PATH) / test_utils.JSON_FEDRAMP_SSP_NAME
    with open(file_path, 'r') as f:
        json_content = f.read()
    validator = FedrampValidator()
    success = validator.validate_ssp(json_content, 'json')
    assert not success

    file_path = pathlib.Path(test_utils.XML_FEDRAMP_SSP_PATH) / test_utils.XML_FEDRAMP_SSP_NAME
    with open(file_path, 'r') as f:
        xml_content = f.read()
    validator = FedrampValidator()
    success = validator.validate_ssp(xml_content, 'xml')
    assert not success


def test_validate_ssp_worng_format(tmp_path: pathlib.Path) -> None:
    """Inavlid format of content."""
    file_path = pathlib.Path(test_utils.JSON_FEDRAMP_SSP_PATH) / test_utils.JSON_FEDRAMP_SSP_NAME
    with open(file_path, 'r') as f:
        json_content = f.read()
    validator = FedrampValidator()
    with pytest.raises(TrestleError, match='Unknown SSP format'):
        validator.validate_ssp(json_content, 'yaml')
