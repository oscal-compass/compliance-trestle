# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Tests for trestle write actions class."""

import os

from tests import test_utils

import trestle.core.const as const
from trestle.core.models.actions import WriteAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType


def test_write_action_yaml(tmp_yaml_file, sample_nist_component_def):
    """Test write yaml action."""
    element = Element(sample_nist_component_def, 'component-definition')

    with open(tmp_yaml_file, 'w+', encoding=const.FILE_ENCODING) as writer:
        wa = WriteAction(writer, element, FileContentType.YAML)
        wa.execute()
        writer.flush()
        writer.close()

    test_utils.verify_file_content(tmp_yaml_file, element.get())

    os.remove(tmp_yaml_file)


def test_write_action_json(tmp_json_file, sample_nist_component_def):
    """Test write json action."""
    element = Element(sample_nist_component_def, 'component-definition')

    with open(tmp_json_file, 'w+', encoding=const.FILE_ENCODING) as writer:
        wa = WriteAction(writer, element, FileContentType.JSON)
        wa.execute()
        writer.flush()
        writer.close()

    test_utils.verify_file_content(tmp_json_file, element.get())

    os.remove(tmp_json_file)
