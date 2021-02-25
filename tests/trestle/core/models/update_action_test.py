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
"""Tests for trestle update action class."""

from datetime import datetime
from typing import List

from trestle.core.models.actions import UpdateAction
from trestle.core.models.elements import Element, ElementPath
from trestle.oscal import OSCAL_VERSION, target


def test_update_action(sample_target_def):
    """Test update action."""
    element = Element(sample_target_def)

    metadata = target.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': OSCAL_VERSION
        }
    )

    sub_element_path = ElementPath('target-definition.metadata')
    prev_metadata = element.get_at(sub_element_path)

    uac = UpdateAction(metadata, element, sub_element_path)

    uac.execute()

    assert element.get_at(sub_element_path) is not prev_metadata
    assert element.get_at(sub_element_path) == metadata

    uac.rollback()

    assert element.get_at(sub_element_path) == prev_metadata
    assert element.get_at(sub_element_path) is not metadata


def test_update_list_sub_element_action(sample_target_def):
    """Test setting a list."""
    element = Element(sample_target_def)

    parties: List[target.Party] = []
    parties.append(
        target.Party(**{
            'uuid': 'ff47836c-877c-4007-bbf3-c9d9bd805000', 'name': 'TEST1', 'type': 'organization'
        })
    )
    parties.append(
        target.Party(**{
            'uuid': 'ee88836c-877c-4007-bbf3-c9d9bd805000', 'name': 'TEST2', 'type': 'organization'
        })
    )

    sub_element_path = ElementPath('target-definition.metadata.parties.*')
    uac = UpdateAction(parties, element, sub_element_path)
    uac.execute()

    assert element.get_at(sub_element_path) == parties
