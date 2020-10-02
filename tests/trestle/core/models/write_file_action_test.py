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
"""Tests for trestle actions module."""

import os

from tests import test_utils

from trestle.core.models.actions import FileContentType, WriteFileAction
from trestle.core.models.elements import Element


def test_write_file_action_yaml(tmp_yaml_file, sample_target):
    """Test write yaml action."""
    element = Element(sample_target)
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()
    test_utils.verify_file_content(tmp_yaml_file, element.get(), FileContentType.YAML)
    os.remove(tmp_yaml_file)


def test_write_file_rollback(tmp_yaml_file, sample_target):
    """Test rollback."""
    element = Element(sample_target)
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()
    test_utils.verify_file_content(tmp_yaml_file, element.get(), FileContentType.YAML)

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
