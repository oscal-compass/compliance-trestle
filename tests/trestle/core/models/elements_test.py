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
from trestle.core.err import TrestleError
from trestle.core.models.elements import Element, ElementPath
from trestle.oscal import target


def test_element_get(sample_target: target.TargetDefinition):
    """Test element get method."""
    element = Element(sample_target)

    assert element.get() == sample_target
    assert element.get(ElementPath('*')) == sample_target
    assert element.get(ElementPath('metadata')) == sample_target.metadata
    assert element.get(ElementPath('metadata.title')) == sample_target.metadata.title
    assert element.get(ElementPath('targets')) == sample_target.targets
    assert element.get(ElementPath('targets.*')) == sample_target.targets
    assert element.get(ElementPath('metadata.parties.*')) == sample_target.metadata.parties
    assert element.get(ElementPath('metadata.parties.0')) == sample_target.metadata.parties[0]
    assert element.get(ElementPath('metadata.parties.0.uuid')) == sample_target.metadata.parties[0].uuid


def test_element_path_constructor(sample_target: target.TargetDefinition):
    """Test element path construction."""
    assert ElementPath('*').get() == ['*']
    assert ElementPath('metadata.title').get() == ['metadata', 'title']
    assert ElementPath('targets.*').get() == ['targets', '*']
    assert ElementPath('targets.0').get() == ['targets', '0']
    assert ElementPath('metadata.parties.0.uuid').get() == ['metadata', 'parties', '0', 'uuid']

    # expect error
    try:
        ElementPath('.')
    except TrestleError:
        pass

    # expect error
    try:
        ElementPath('.*')
    except TrestleError:
        pass

    # expect error
    try:
        ElementPath('metadata..title')
    except TrestleError:
        pass
