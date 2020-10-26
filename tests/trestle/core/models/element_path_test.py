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
"""Tests for trestle elements module."""
import pathlib

import pytest

from trestle.core.err import TrestleError
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import target


def test_element_path_init(sample_target_def: target.TargetDefinition):
    """Test element path construction."""
    assert ElementPath('target-definition.metadata.title').get() == ['target-definition', 'metadata', 'title']
    assert ElementPath('target-definition.targets.*').get() == ['target-definition', 'targets', '*']
    assert ElementPath('target-definition.targets.0').get() == ['target-definition', 'targets', '0']
    assert ElementPath('target-definition.metadata.parties.0.uuid').get() == [
        'target-definition', 'metadata', 'parties', '0', 'uuid'
    ]
    assert ElementPath('groups.*').get() == ['groups', '*']

    # expect error
    with pytest.raises(TrestleError):
        ElementPath('*')

    # expect error
    with pytest.raises(TrestleError):
        ElementPath('*.*')

    # expect error
    with pytest.raises(TrestleError):
        ElementPath('.')

    # expect error
    with pytest.raises(TrestleError):
        ElementPath('.*')

    # expect error
    with pytest.raises(TrestleError):
        ElementPath('catalog.groups.*.controls.*')

    # expect error
    with pytest.raises(TrestleError):
        ElementPath('catalog.metadata..title')

    # expect error
    with pytest.raises(TrestleError):
        ElementPath('catalog')


def test_element_path_get_element_name(sample_target_def: target.TargetDefinition):
    """Test get element name method."""
    assert ElementPath('target-definition.metadata.last-modified').get_element_name() == 'last-modified'
    assert ElementPath('target-definition.metadata.title').get_element_name() == 'title'
    assert ElementPath('target-definition.metadata').get_element_name() == 'metadata'
    assert ElementPath('target-definition.metadata.parties.*').get_element_name() == 'parties'


def test_element_path_get_preceding_path(sample_target_def: target.TargetDefinition):
    """Test get parent path method."""
    assert ElementPath('target-definition.metadata.title'
                       ).get_preceding_path() == ElementPath('target-definition.metadata')
    assert ElementPath('target-definition.metadata').get_preceding_path() is None
    assert ElementPath('target-definition.metadata.parties.*'
                       ).get_preceding_path() == ElementPath('target-definition.metadata.parties')
    assert ElementPath('target-definition.metadata.*').get_preceding_path() == ElementPath('target-definition.metadata')

    # element_path with parent path
    parent_path = ElementPath('target-definition.metadata')
    element_path = ElementPath('metadata.parties.*', parent_path)
    preceding_path = ElementPath('target-definition.metadata.parties')
    assert element_path.get_preceding_path() == preceding_path


def test_element_path_get(sample_target_def: target.TargetDefinition):
    """Test get method of element path."""
    assert ElementPath('target-definition.metadata').get() == ['target-definition', 'metadata']
    assert ElementPath('target-definition.metadata.title').get() == ['target-definition', 'metadata', 'title']
    assert ElementPath('target-definition.metadata.title').get_first() == 'target-definition'
    assert ElementPath('target-definition.metadata.title').get_last() == 'title'
    assert ElementPath('target-definition.metadata').get_last() == 'metadata'
    assert ElementPath('target-definition.metadata.parties.*').get_last() == '*'
    assert ElementPath('target-definition.metadata.title').get_full() == 'target-definition.metadata.title'


def test_element_path_str():
    """Test for magic method str."""
    element_path = ElementPath('target.metadata')
    assert str(element_path) == 'target.metadata'


def test_element_path_eq(sample_target_def):
    """Test for magic method eq."""
    assert ElementPath('target.metadata') == ElementPath('target.metadata')
    assert not (ElementPath('target.metadata') == ElementPath('target.title'))
    assert not (ElementPath('target.metadata') == Element(sample_target_def))


def test_element_path_to_file_path():
    """Test to file path method."""
    assert ElementPath('target-definition.metadata.title'
                       ).to_file_path() == pathlib.Path('./target-definition/metadata/title')

    assert ElementPath('target-definition.metadata.title').to_file_path(
        FileContentType.YAML
    ) == pathlib.Path('./target-definition/metadata/title.yaml')

    assert ElementPath('target-definition.metadata.parties').to_file_path(
        FileContentType.JSON
    ) == pathlib.Path('./target-definition/metadata/parties.json')

    assert ElementPath('target-definition.metadata.parties.*').to_file_path(
        FileContentType.YAML
    ) == pathlib.Path('./target-definition/metadata/parties.yaml')

    assert ElementPath('group.controls.*').to_file_path(FileContentType.YAML,
                                                        '00000__group') == pathlib.Path('./00000__group/controls.yaml')

    element_path = ElementPath('target.target-control-implementations.*', ElementPath('target-definition.targets.*'))
    assert element_path.to_file_path() == pathlib.Path('./target/target-control-implementations')

    # error for invalid content type
    with pytest.raises(TrestleError):
        assert ElementPath('target-definition.metadata.parties.*').to_file_path(-1)


def test_element_path_to_root_path():
    """Test to file path method."""
    assert ElementPath('target-definition.metadata.title').to_root_path() == pathlib.Path('./target-definition')
    assert ElementPath('target-definition.metadata.title').to_root_path(FileContentType.YAML
                                                                        ) == pathlib.Path('./target-definition.yaml')
    assert ElementPath('target-definition.metadata.title').to_root_path(FileContentType.JSON
                                                                        ) == pathlib.Path('./target-definition.json')

    # error for invalid content type - 1
    with pytest.raises(TrestleError):
        assert ElementPath('target-definition.metadata.title').to_root_path(-1)


def test_full_path():
    """Test full path parths method."""
    element_arg = 'catalog.groups.*.controls.*.controls.*'
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls.*', parent_path=p1)
    p3 = ElementPath('control.controls.*', parent_path=p2)

    full_path_parts = p3.get_full_path_parts()
    full_path = ElementPath.PATH_SEPARATOR.join(full_path_parts)
    assert element_arg == full_path
