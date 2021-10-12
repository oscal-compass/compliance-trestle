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
"""Tests for trestle write to file actions class."""

import pathlib

from tests import test_utils

import trestle.core.const as const
from trestle.core.err import TrestleError
from trestle.core.models.actions import WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType


def test_write_file_action_yaml(tmp_yaml_file: pathlib.Path, sample_nist_component_def):
    """Test write yaml action."""
    element = Element(sample_nist_component_def, 'component-definition')

    try:
        # string path should error
        wa = WriteFileAction(tmp_yaml_file.as_posix(), element, FileContentType.YAML)
    except TrestleError:
        pass

    try:
        # invalid file extension should error
        wa = WriteFileAction(tmp_yaml_file, element, FileContentType.JSON)
    except TrestleError:
        pass

    try:
        # writing to a non-existing file will error
        wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
        wa.execute()
    except TrestleError:
        pass

    tmp_yaml_file.touch()
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()
    test_utils.verify_file_content(tmp_yaml_file, element.get())


def test_write_file_rollback(tmp_yaml_file: pathlib.Path, sample_nist_component_def):
    """Test rollback."""
    element = Element(sample_nist_component_def, 'component-definition')
    tmp_yaml_file.touch()
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()
    test_utils.verify_file_content(tmp_yaml_file, element.get())

    # verify the file content is not empty
    with open(tmp_yaml_file, 'r', encoding=const.FILE_ENCODING) as read_file:
        assert read_file.tell() >= 0

    wa.rollback()

    # verify the file content is empty
    with open(tmp_yaml_file, 'r', encoding=const.FILE_ENCODING) as read_file:
        assert read_file.tell() == 0


def test_write_existing_file_rollback(tmp_yaml_file, sample_nist_component_def):
    """Test rollback."""
    # add some content
    tmp_yaml_file.touch()
    current_pos = 0
    with open(tmp_yaml_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        fp.write('....\n')
        current_pos = fp.tell()

    # write to the file
    element = Element(sample_nist_component_def, 'component-definition')
    wa = WriteFileAction(tmp_yaml_file, element, FileContentType.YAML)
    wa.execute()

    # verify the file content is not empty
    with open(tmp_yaml_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        assert fp.tell() > current_pos

    # rollback to the original
    wa.rollback()

    # # verify the file content is empty
    with open(tmp_yaml_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        assert fp.tell() == current_pos
