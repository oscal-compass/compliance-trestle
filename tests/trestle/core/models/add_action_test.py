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
"""Tests for trestle add action class."""

from datetime import datetime
from typing import List

from tests import test_utils

from trestle.core.models.actions import AddAction
from trestle.core.models.elements import Element, ElementPath
from trestle.oscal import target


def test_add_action(sample_target):
    """Test add action."""
    element = Element(sample_target)

    metadata = target.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': '1.0.0-Milestone3'
        }
    )

    sub_element_path = ElementPath('metadata')
    prev_metadata = element.get_at(sub_element_path)

    ac = AddAction(metadata, element, sub_element_path)

    ac.execute()

    assert not test_utils.is_equal(element.get_at(sub_element_path), prev_metadata)
    assert test_utils.is_equal(element.get_at(sub_element_path), metadata)

    ac.rollback()

    assert test_utils.is_equal(element.get_at(sub_element_path), prev_metadata)
    assert not test_utils.is_equal(element.get_at(sub_element_path), metadata)


def test_add_list_sub_element_action(sample_target):
    """Test setting a list."""
    element = Element(sample_target)

    parties: List[target.Party] = []
    parties.append(
        target.Party(**{
            'uuid': 'ff47836c-877c-4007-bbf3-c9d9bd805000', 'party-name': 'TEST1', 'type': 'organization'
        })
    )
    parties.append(
        target.Party(**{
            'uuid': 'ee88836c-877c-4007-bbf3-c9d9bd805000', 'party-name': 'TEST2', 'type': 'organization'
        })
    )

    sub_element_path = ElementPath('metadata.parties.*')
    ac = AddAction(parties, element, sub_element_path)
    ac.execute()

    assert test_utils.is_equal(element.get_at(sub_element_path), parties)
