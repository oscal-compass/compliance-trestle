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
"""Testing format conversion functionality."""

import pathlib

import pytest

from tests import test_utils

from trestle.core.err import TrestleError
from trestle.saxon.format_convert import JsonXmlConverter


def test_init() -> None:
    """Test creating JSON XML converter object."""
    converter = JsonXmlConverter()
    assert str(converter.ssp_j_x_xsl_path) != ''


def test_json2xml(tmp_path: pathlib.Path) -> None:
    """Test JSON to XML conversion."""
    file_path = pathlib.Path(test_utils.JSON_FEDRAMP_SSP_PATH) / test_utils.JSON_FEDRAMP_SSP_NAME
    with open(file_path, 'r') as f:
        json_content = f.read()
    converter = JsonXmlConverter()
    xml_str = converter.json2xml('ssp', json_content)
    assert '<system-security-plan' in xml_str


def test_json2xml_wrong_model(tmp_path: pathlib.Path) -> None:
    """Wrong OSCAL model."""
    file_path = pathlib.Path(test_utils.JSON_FEDRAMP_SSP_PATH) / test_utils.JSON_FEDRAMP_SSP_NAME
    with open(file_path, 'r') as f:
        json_content = f.read()
    converter = JsonXmlConverter()
    with pytest.raises(TrestleError, match='Invalid model name'):
        converter.json2xml('catalog', json_content)


def test_json2xml_invalid_xsl(monkeypatch, tmp_path: pathlib.Path) -> None:
    """Inavlid XSL path."""
    file_path = pathlib.Path(test_utils.JSON_FEDRAMP_SSP_PATH) / test_utils.JSON_FEDRAMP_SSP_NAME
    with open(file_path, 'r') as f:
        json_content = f.read()
    converter = JsonXmlConverter()
    # modify xsl path to a wrong value
    monkeypatch.setattr(converter, 'ssp_j_x_xsl_path', tmp_path / 'invalid_file')
    with pytest.raises(TrestleError, match=r'xslt converter .* does not exist'):
        converter.json2xml('ssp', json_content)
