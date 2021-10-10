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
"""Tests for trestle remove action class."""

from typing import List

from trestle.core.models.actions import RemoveAction, UpdateAction
from trestle.core.models.elements import Element, ElementPath
from trestle.oscal import common, component


def prepare_element(sample_nist_component_def: component.ComponentDefinition):
    """Prepare a target element for remove tests."""
    element = Element(sample_nist_component_def)

    parties: List[common.Party] = []
    parties.append(
        common.Party(**{
            'uuid': 'ff47836c-877c-4007-bbf3-c9d9bd805000', 'name': 'TEST1', 'type': 'organization'
        })
    )
    parties.append(
        common.Party(**{
            'uuid': 'ee88836c-877c-4007-bbf3-c9d9bd805000', 'name': 'TEST2', 'type': 'organization'
        })
    )

    sub_element_path = ElementPath('component-definition.metadata.parties.*')
    ac = UpdateAction(parties, element, sub_element_path)
    ac.execute()

    assert element.get_at(sub_element_path) == parties

    return element


def test_remove_action(sample_nist_component_def):
    """Test remove action."""
    element = prepare_element(sample_nist_component_def)
    sub_element_path = ElementPath('component-definition.metadata.parties')
    prev_sub_element = element.get_at(sub_element_path)

    rac = RemoveAction(element, sub_element_path)

    rac.execute()

    assert element.get_at(sub_element_path) is None

    rac.rollback()

    assert element.get_at(sub_element_path) == prev_sub_element
