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


def test_element_path_init(sample_target: target.TargetDefinition):
    """Test element path construction."""
    assert ElementPath('metadata.title').get() == ['metadata', 'title']
    assert ElementPath('targets.*').get() == ['targets', '*']
    assert ElementPath('targets.0').get() == ['targets', '0']
    assert ElementPath('metadata.parties.0.uuid').get() == ['metadata', 'parties', '0', 'uuid']

    # expect error
    try:
        ElementPath('*')
    except TrestleError:
        pass

    # expect error
    try:
        ElementPath('*.*')
    except TrestleError:
        pass

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
        ElementPath('catalog.groups.*.controls.*')
    except TrestleError:
        pass

    # expect error
    try:
        ElementPath('metadata..title')
    except TrestleError:
        pass


def test_element_path_get_element_name(sample_target: target.TargetDefinition):
    """Test get element name method."""
    assert ElementPath('metadata.title').get_element_name() == 'title'
    assert ElementPath('metadata').get_element_name() == 'metadata'
    assert ElementPath('metadata.parties.*').get_element_name() == 'parties'


def test_element_path_get_parent(sample_target: target.TargetDefinition):
    """Test get parent path method."""
    assert ElementPath('metadata.title').get_parent_path() == ElementPath('metadata')
    assert ElementPath('metadata').get_parent_path() is None
    assert ElementPath('metadata.parties.*').get_parent_path() == ElementPath('metadata.parties')
    assert ElementPath('metadata.*').get_parent_path() == ElementPath('metadata')


def test_element_path_get(sample_target: target.TargetDefinition):
    """Test get method of element path."""
    assert ElementPath('metadata').get() == ['metadata']
    assert ElementPath('metadata.title').get() == ['metadata', 'title']

    assert ElementPath('metadata.title').get_first() == 'metadata'
    assert ElementPath('metadata.title').get_last() == 'title'
    assert ElementPath('metadata').get_last() == 'metadata'


def test_element_path_str():
    """Test for magic method str."""
    element_path = ElementPath('target.metadata')
    assert str(element_path) == 'target.metadata'


def test_element_path_eq(sample_target):
    """Test for magic method eq."""
    assert ElementPath('target.metadata') == ElementPath('target.metadata')
    assert not (ElementPath('target.metadata') == ElementPath('target.title'))
    assert not (ElementPath('target.metadata') == Element(sample_target))
