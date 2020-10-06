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
from datetime import datetime
from typing import List

from trestle.core.err import TrestleError
from trestle.core.models.elements import Element, ElementPath
from trestle.oscal import target


def test_element_get_at(sample_target: target.TargetDefinition):
    """Test element get method."""
    element = Element(sample_target)

    assert element.get() == sample_target
    assert element.get_at() == element.get()
    assert element.get_at(ElementPath('metadata')) == sample_target.metadata
    assert element.get_at(ElementPath('metadata.title')) == sample_target.metadata.title
    assert element.get_at(ElementPath('targets')) == sample_target.targets
    assert element.get_at(ElementPath('targets.*')) == sample_target.targets
    assert element.get_at(ElementPath('metadata.parties.*')) == sample_target.metadata.parties
    assert element.get_at(ElementPath('metadata.parties.0')) == sample_target.metadata.parties[0]
    assert element.get_at(ElementPath('metadata.parties.0.uuid')) == sample_target.metadata.parties[0].uuid

    # invalid indexing
    assert element.get_at(ElementPath('metadata.title.0')) is None


def test_element_set_at(sample_target: target.TargetDefinition):
    """Test element get method."""
    element = Element(sample_target)

    metadata = target.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now(),
            'version': '0.0.0',
            'oscal-version': '1.0.0-Milestone3'
        }
    )

    title: target.Title = target.Title(__root__='TEST')

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

    assert element.set_at(ElementPath('metadata'), metadata).get_at(ElementPath('metadata')) == metadata
    assert element.set_at(ElementPath('metadata.title'), title).get_at(ElementPath('metadata.title')) == title

    assert element.set_at(ElementPath('metadata.parties'), parties).get_at(ElementPath('metadata.parties')) == parties
    assert element.set_at(ElementPath('metadata.parties.*'), parties).get_at(ElementPath('metadata.parties')) == parties

    # unset
    assert element.set_at(ElementPath('metadata.parties'), None).get_at(ElementPath('metadata.parties')) is None

    # string element path
    assert element.set_at('metadata.parties', parties).get_at(ElementPath('metadata.parties')) == parties

    try:
        assert element.set_at(ElementPath('metadata.title'), parties).get_at(ElementPath('metadata.parties')) == parties
    except TrestleError:
        pass

    # wildcard requires it to be an OscalBaseModel or list
    try:
        assert element.set_at(ElementPath('metadata.parties.*'), 'INVALID')
    except TrestleError:
        pass

    # invalid attribute
    try:
        assert element.set_at(ElementPath('metadata.groups.*'), parties)
    except TrestleError:
        pass


def test_element_str(sample_target):
    """Test for magic method str."""
    element = Element(sample_target)
    assert str(element) == 'TargetDefinition'
