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
"""Tests for trestle elements module."""

from datetime import datetime
from typing import List

import pytest

from trestle.common.err import TrestleError
from trestle.core.models.elements import Element, ElementPath
from trestle.oscal import common, component


def test_element_get_at(sample_nist_component_def: component.ComponentDefinition):
    """Test element get method."""
    element = Element(sample_nist_component_def)

    # field alias should succeed
    assert (
        element.get_at(ElementPath('component-definition.metadata.last-modified'))
        == sample_nist_component_def.metadata.last_modified
    )

    # field name should fail
    assert element.get_at(ElementPath('component-definition.metadata.last_modified')) is None

    assert element.get() == sample_nist_component_def
    assert element.get_at() == element.get()
    assert element.get_at(ElementPath('component-definition.metadata')) == sample_nist_component_def.metadata
    assert (
        element.get_at(ElementPath('component-definition.metadata.title')) == sample_nist_component_def.metadata.title
    )
    assert element.get_at(ElementPath('component-definition.components')) == sample_nist_component_def.components
    assert element.get_at(ElementPath('component-definition.components.*')) == sample_nist_component_def.components
    assert (
        element.get_at(ElementPath('component-definition.metadata.parties.*'))
        == sample_nist_component_def.metadata.parties
    )
    assert (
        element.get_at(ElementPath('component-definition.metadata.parties.0'))
        == sample_nist_component_def.metadata.parties[0]
    )
    assert (
        element.get_at(ElementPath('component-definition.metadata.parties.0.uuid'))
        == sample_nist_component_def.metadata.parties[0].uuid
    )

    for index in range(len(sample_nist_component_def.components)):
        path_str = f'component-definition.components.{index}'
        assert element.get_at(ElementPath(path_str)) == sample_nist_component_def.components[index]

    # invalid indexing
    assert element.get_at(ElementPath('component-definition.metadata.title.0')) is None

    # invalid path with missing root model
    assert element.get_at(ElementPath('metadata.title')) is None

    # element_path with parent path
    parent_path = ElementPath('component-definition.metadata')
    element_path = ElementPath('metadata.parties.*', parent_path)
    assert element.get_at(element_path) == sample_nist_component_def.metadata.parties

    # element_path with parent path
    parent_path = ElementPath('component-definition.components.*')
    element_path = ElementPath('component.control-implementations.*', parent_path)
    component_list = element.get_at(parent_path)
    for component_item in component_list:
        component_element = Element(component_item)
        assert component_element.get_at(element_path) == component_item.control_implementations

    # element_path in a list with parent path
    parent_path = ElementPath('component-definition.components.*')
    element_path = ElementPath('component.control-implementations.0', parent_path)
    component_list = element.get_at(parent_path)
    for component_item in component_list:
        component_element = Element(component_item)
        assert component_element.get_at(element_path) == component_item.control_implementations[0]


def test_element_set_at(sample_nist_component_def: component.ComponentDefinition):
    """Test element get method."""
    element = Element(sample_nist_component_def)

    metadata = common.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': '1.0.0',
        }
    )

    parties: List[common.Party] = []
    parties.append(
        common.Parties(**{'uuid': 'ff47836c-877c-4007-bbf3-c9d9bd805000', 'name': 'TEST1', 'type': 'organization'})
    )
    parties.append(
        common.Parties(**{'uuid': 'ee88836c-877c-4007-bbf3-c9d9bd805000', 'name': 'TEST2', 'type': 'organization'})
    )

    assert (
        element.set_at(ElementPath('component-definition.metadata'), metadata).get_at(
            ElementPath('component-definition.metadata')
        )
        == metadata
    )

    assert (
        element.set_at(ElementPath('component-definition.metadata.parties'), parties).get_at(
            ElementPath('component-definition.metadata.parties')
        )
        == parties
    )

    assert (
        element.set_at(ElementPath('component-definition.metadata.parties.*'), parties).get_at(
            ElementPath('component-definition.metadata.parties')
        )
        == parties
    )

    # unset
    assert (
        element.set_at(ElementPath('component-definition.metadata.parties'), None).get_at(
            ElementPath('component-definition.metadata.parties')
        )
        is None
    )

    # string element path
    assert (
        element.set_at('component-definition.metadata.parties', parties).get_at(
            ElementPath('component-definition.metadata.parties')
        )
        == parties
    )

    with pytest.raises(TrestleError):
        assert (
            element.set_at(ElementPath('component-definition.metadata'), parties).get_at(
                ElementPath('component-definition.metadata.parties')
            )
            == parties
        )

    # wildcard requires it to be an OscalBaseModel or list
    with pytest.raises(TrestleError):
        assert element.set_at(ElementPath('component-definition.metadata.parties.*'), 'INVALID')

    # invalid attribute
    with pytest.raises(TrestleError):
        assert element.set_at(ElementPath('component-definition.metadata.groups.*'), parties)


def test_element_str(sample_nist_component_def):
    """Test for magic method str."""
    element = Element(sample_nist_component_def)
    assert str(element) == 'ComponentDefinition'


# ---------------------------------------------------------------------------
# Coverage-improvement tests for trestle/core/models/elements.py
# ---------------------------------------------------------------------------


def test_element_get_at_invalid_parent_path(sample_nist_component_def: component.ComponentDefinition):
    """Element.get_at line 504 — invalid parent path raises TrestleNotFoundError."""
    from trestle.common.err import TrestleNotFoundError

    element = Element(sample_nist_component_def)
    parent_path = ElementPath('component-definition.nonexistent')
    element_path = ElementPath('nonexistent.title', parent_path)
    with pytest.raises(TrestleNotFoundError):
        element.get_at(element_path)


def test_element_get_sub_element_obj_wraps_element(sample_nist_component_def: component.ComponentDefinition):
    """Element._get_sub_element_obj line 542 — Element input is unwrapped to get()."""
    element = Element(sample_nist_component_def)
    sub = Element(sample_nist_component_def.metadata)
    result = element._get_sub_element_obj(sub)
    assert result == sample_nist_component_def.metadata


def test_element_get_sub_element_obj_disallowed_type(sample_nist_component_def: component.ComponentDefinition):
    """Element._get_sub_element_obj line 536 — disallowed type raises TrestleError."""
    element = Element(sample_nist_component_def)
    with pytest.raises(TrestleError):
        element._get_sub_element_obj(42)


def test_element_set_at_invalid_preceding_element(sample_nist_component_def: component.ComponentDefinition):
    """Element.set_at line 580 — invalid sub element path raises TrestleError."""
    # To hit line 580 we need a path whose preceding element exists but resolves to None.
    # Use a path ending in a non-existent attribute so get_preceding_element returns None.
    metadata_el = Element(sample_nist_component_def.metadata)
    with pytest.raises(TrestleError):
        metadata_el.set_at(ElementPath('metadata.nonexistent_field'), sample_nist_component_def.metadata)


def test_element_to_json_ignore_wrapper(sample_nist_component_def: component.ComponentDefinition):
    """Element.to_json line 619 — IGNORE_WRAPPER_ALIAS path uses unwrapped serialization."""
    element = Element(sample_nist_component_def, Element.IGNORE_WRAPPER_ALIAS)
    json_str = element.to_json()
    assert 'metadata' in json_str
