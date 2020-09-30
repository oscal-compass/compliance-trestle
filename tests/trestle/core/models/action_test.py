# -*- mode:python; coding:utf-8 -*-

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
"""Tests for trestle action module."""

import json
import os

from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.action import AppendFileAction, FileContentType, WriteAction, WriteFileAction
from trestle.core.models.element import Element

import yaml


def verify_file_content(file_path, model: OscalBaseModel, content_type: FileContentType):
    """Verify that the file contains the correct model data."""
    file_data = None
    with open(file_path, 'r', encoding='utf8') as read_file:
        if content_type == FileContentType.YAML:
            file_data = yaml.load(read_file, Loader=yaml.Loader)
        elif content_type == FileContentType.JSON:
            file_data = json.load(read_file)

    assert file_data is not None

    model.parse_obj(file_data)


def test_write_action_yaml(tmp_yaml_file, sample_target):
    """Test write yaml action."""
    element = Element(sample_target)

    with open(tmp_yaml_file, 'w+') as writer:
        wa = WriteAction(writer, element, FileContentType.YAML)
        wa.execute()
        verify_file_content(tmp_yaml_file, element.get(), FileContentType.YAML)

    os.remove(tmp_yaml_file)


def test_write_action_json(tmp_json_file, sample_target):
    """Test write json action."""
    element = Element(sample_target)

    with open(tmp_json_file, 'w+') as writer:
        wa = WriteAction(writer, element, FileContentType.JSON)
        wa.execute()
        verify_file_content(tmp_json_file, element.get(), FileContentType.JSON)

    os.remove(tmp_json_file)


def test_write_file_action_yaml(tmp_yaml_file, sample_target):
    """Test write yaml action."""
    element = Element(sample_target)
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()
    verify_file_content(tmp_yaml_file, element.get(), FileContentType.YAML)
    os.remove(tmp_yaml_file)


def test_write_file_rollback(tmp_yaml_file, sample_target):
    """Test rollback."""
    element = Element(sample_target)
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()
    verify_file_content(tmp_yaml_file, element.get(), FileContentType.YAML)

    # verify the file content is not empty
    with open(tmp_yaml_file, 'r', encoding='utf8') as read_file:
        assert read_file.tell() >= 0

    wa.rollback()
    assert os.path.isfile(tmp_yaml_file) is False


def test_write_existing_file_rollback(tmp_yaml_file, sample_target):
    """Test rollback."""
    # add some content
    current_pos = 0
    with open(tmp_yaml_file, 'w+') as writer:
        writer.write('....\n')
        current_pos = writer.tell()

    # write to the file
    element = Element(sample_target)
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()

    # verify the file content is not empty
    with open(tmp_yaml_file, 'a+', encoding='utf8') as fp:
        assert fp.tell() > current_pos

    # rollback to the original
    wa.rollback()
    assert os.path.isfile(tmp_yaml_file) is True

    # # verify the file content is empty
    with open(tmp_yaml_file, 'a+', encoding='utf8') as fp:
        assert fp.tell() == current_pos

    os.remove(tmp_yaml_file)


def test_append_file_rollback(tmp_yaml_file, sample_target):
    """Test append file and rollback."""
    element = Element(sample_target)

    # appending to a non-existing file will error
    try:
        wa = AppendFileAction(tmp_yaml_file, element, FileContentType.YAML)
    except TrestleError:
        pass

    # add some content to a file
    current_pos = 0
    with open(tmp_yaml_file, 'w+') as writer:
        writer.write('....\n')
        current_pos = writer.tell()

    # write to the file
    wa = AppendFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()

    # verify the file content is not empty
    with open(tmp_yaml_file, 'a+', encoding='utf8') as fp:
        assert fp.tell() > current_pos

    # rollback to the original
    wa.rollback()
    assert os.path.isfile(tmp_yaml_file) is True

    # # verify the file content is empty
    with open(tmp_yaml_file, 'a+', encoding='utf8') as fp:
        assert fp.tell() == current_pos

    os.remove(tmp_yaml_file)
