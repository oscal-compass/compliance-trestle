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
"""Tests for trestle file content type module."""
import pytest

from trestle.core.err import TrestleError
from trestle.core.models.file_content_type import FileContentType


def test_to_content_type():
    """Test to_content_type method."""
    assert FileContentType.to_content_type('.json') == FileContentType.JSON
    assert FileContentType.to_content_type('.yaml') == FileContentType.YAML

    with pytest.raises(TrestleError):
        FileContentType.to_content_type('.invalid')


def test_to_file_extension():
    """Test to_file_extension method."""
    assert FileContentType.to_file_extension(FileContentType.JSON) == '.json'
    assert FileContentType.to_file_extension(FileContentType.YAML) == '.yaml'

    with pytest.raises(TrestleError):
        FileContentType.to_file_extension(-1)
