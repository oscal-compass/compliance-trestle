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
from trestle.oscal import component


def test_element_path_init(sample_nist_component_def: component.ComponentDefinition):
    """Test element path construction."""
    assert ElementPath('component-definition.metadata.title').get() == ['component-definition', 'metadata', 'title']
    assert ElementPath('component-definition.components.*').get() == ['component-definition', 'components', '*']
    assert ElementPath('component-definition.components.0').get() == ['component-definition', 'components', '0']
    assert ElementPath('component-definition.metadata.parties.0.uuid').get() == [
        'component-definition', 'metadata', 'parties', '0', 'uuid'
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


def test_element_path_get_element_name():
    """Test get element name method."""
    assert ElementPath('component-definition.metadata.last-modified').get_element_name() == 'last-modified'
    assert ElementPath('component-definition.metadata.title').get_element_name() == 'title'
    assert ElementPath('component-definition.metadata').get_element_name() == 'metadata'
    assert ElementPath('component-definition.metadata.parties.*').get_element_name() == 'parties'


def test_element_path_get_preceding_path(sample_nist_component_def: component.ComponentDefinition):
    """Test get parent path method."""
    assert ElementPath('component-definition.metadata.title'
                       ).get_preceding_path() == ElementPath('component-definition.metadata')
    assert ElementPath('component-definition.metadata').get_preceding_path() is None
    assert ElementPath('component-definition.metadata.parties.*'
                       ).get_preceding_path() == ElementPath('component-definition.metadata.parties')
    assert ElementPath('component-definition.metadata.*'
                       ).get_preceding_path() == ElementPath('component-definition.metadata')

    # element_path with parent path
    parent_path = ElementPath('component-definition.metadata')
    element_path = ElementPath('metadata.parties.*', parent_path)
    preceding_path = ElementPath('component-definition.metadata.parties')
    assert element_path.get_preceding_path() == preceding_path


def test_element_path_get(sample_nist_component_def: component.ComponentDefinition):
    """Test get method of element path."""
    assert ElementPath('component-definition.metadata').get() == ['component-definition', 'metadata']
    assert ElementPath('component-definition.metadata.title').get() == ['component-definition', 'metadata', 'title']
    assert ElementPath('component-definition.metadata.title').get_first() == 'component-definition'
    assert ElementPath('component-definition.metadata.title').get_last() == 'title'
    assert ElementPath('component-definition.metadata').get_last() == 'metadata'
    assert ElementPath('component-definition.metadata.parties.*').get_last() == '*'
    assert ElementPath('component-definition.metadata.title').get_full() == 'component-definition.metadata.title'


def test_element_path_str():
    """Test for magic method str."""
    element_path = ElementPath('component.metadata')
    assert str(element_path) == 'component.metadata'


def test_element_path_eq(sample_nist_component_def):
    """Test for magic method eq."""
    assert ElementPath('component.metadata') == ElementPath('component.metadata')
    assert not (ElementPath('component.metadata') == ElementPath('component.title'))
    assert not (ElementPath('component.metadata') == Element(sample_nist_component_def))


def test_element_path_to_file_path():
    """Test to file path method."""
    assert ElementPath('component-definition.metadata.title'
                       ).to_file_path() == pathlib.Path('./component-definition/metadata/title')

    assert ElementPath('component-definition.metadata.title').to_file_path(
        FileContentType.YAML
    ) == pathlib.Path('./component-definition/metadata/title.yaml')

    assert ElementPath('component-definition.metadata.parties').to_file_path(
        FileContentType.JSON
    ) == pathlib.Path('./component-definition/metadata/parties.json')

    assert ElementPath('component-definition.metadata.parties.*').to_file_path(
        FileContentType.YAML
    ) == pathlib.Path('./component-definition/metadata/parties.yaml')

    assert ElementPath('group.controls.*').to_file_path(FileContentType.YAML,
                                                        '00000__group') == pathlib.Path('./00000__group/controls.yaml')

    element_path = ElementPath('component.control-implementations.*', ElementPath('component-definition.components.*'))
    assert element_path.to_file_path() == pathlib.Path('./component/control-implementations')

    # error for invalid content type
    with pytest.raises(TrestleError):
        assert ElementPath('component-definition.metadata.parties.*').to_file_path(-1)


def test_element_path_to_root_path():
    """Test to file path method."""
    assert ElementPath('component-definition.metadata.title').to_root_path() == pathlib.Path('./component-definition')
    assert ElementPath('component-definition.metadata.title').to_root_path(
        FileContentType.YAML
    ) == pathlib.Path('./component-definition.yaml')
    assert ElementPath('component-definition.metadata.title').to_root_path(
        FileContentType.JSON
    ) == pathlib.Path('./component-definition.json')

    # error for invalid content type - 1
    with pytest.raises(TrestleError):
        assert ElementPath('component-definition.metadata.title').to_root_path(-1)


def test_full_path():
    """Test full path paths method."""
    element_arg = 'catalog.groups.*.controls.*.controls.*'
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls.*', parent_path=p1)
    p3 = ElementPath('control.controls.*', parent_path=p2)

    full_path_parts = p3.get_full_path_parts()
    full_path = ElementPath.PATH_SEPARATOR.join(full_path_parts)
    assert element_arg == full_path
