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

from trestle.core.err import TrestleError
from trestle.core.models.actions import AppendFileAction, FileContentType
from trestle.core.models.elements import Element


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
