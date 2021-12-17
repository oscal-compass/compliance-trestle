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
"""Tests for trestle cmd utils module."""
from typing import List

import pytest

from tests import test_utils

from trestle.core.commands.common import cmd_utils
from trestle.core.err import TrestleError
from trestle.core.models.elements import ElementPath


def prepare_expected_element_paths(element_args: List[str]) -> List[ElementPath]:
    """Prepare a list of ElementPath from a list of path strings."""
    element_paths: List[ElementPath] = []
    for element_arg in element_args:
        element_paths.append(ElementPath(element_arg))

    return element_paths


def test_parse_element_arg(tmp_path, keep_cwd):
    """Unit test parse a single element arg."""
    with pytest.raises(TrestleError):
        cmd_utils.parse_element_arg(None, 'component-definition')

    with pytest.raises(TrestleError):
        cmd_utils.parse_element_arg(None, '*.*')

    with pytest.raises(TrestleError):
        cmd_utils.parse_element_arg(None, '*')

    with pytest.raises(TrestleError):
        cmd_utils.parse_element_arg(None, 'component-definition.components.*.*')

    element_arg = 'catalog.groups.*'
    expected_paths: List[ElementPath] = prepare_expected_element_paths(['catalog.groups.*'])
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    # contextual path
    test_utils.ensure_trestle_config_dir(tmp_path)
    catalog_split_dir = tmp_path / 'catalogs/nist800-53/catalog'
    catalog_split_dir.mkdir(exist_ok=True, parents=True)
    rel_dir = catalog_split_dir.relative_to(tmp_path)
    element_arg = 'groups.*'
    expected_paths = prepare_expected_element_paths(['groups.*'])
    element_paths = cmd_utils.parse_element_arg(None, element_arg, rel_dir)
    assert expected_paths == element_paths

    element_arg = 'catalog.metadata.parties.*'
    expected_paths = prepare_expected_element_paths(['catalog.metadata', 'metadata.parties.*'])
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    element_arg = 'component-definition.components'
    expected_paths = prepare_expected_element_paths(['component-definition.components'])
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    element_arg = 'component-definition.components.*'
    expected_paths = prepare_expected_element_paths(['component-definition.components.*'])
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    element_arg = 'component-definition.metadata.roles'
    expected_paths = prepare_expected_element_paths(['component-definition.metadata', 'metadata.roles'])
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    element_arg = 'catalog.groups.*.controls.*.controls.*'
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls.*', parent_path=p1)
    p3 = ElementPath('control.controls.*', parent_path=p2)
    expected_paths = [p1, p2, p3]
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    element_arg = 'catalog.groups.*.controls'
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls', parent_path=p1)
    expected_paths = [p1, p2]
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    element_arg = 'component-definition.components.*.control-implementations'
    p1 = ElementPath('component-definition.components.*')
    p2 = ElementPath('defined-component.control-implementations', parent_path=p1)
    expected_paths = [p1, p2]
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    element_arg = 'component-definition.components.*.control-implementations.*'
    p1 = ElementPath('component-definition.components.*')
    p2 = ElementPath('defined-component.control-implementations.*', parent_path=p1)
    expected_paths = [p1, p2]
    element_paths = cmd_utils.parse_element_arg(None, element_arg)
    assert expected_paths == element_paths

    # use contextual path for parsing path
    test_utils.ensure_trestle_config_dir(tmp_path)
    comp_def_dir = tmp_path / 'component-definitions/mycomponent/'
    comp_def_dir.mkdir(exist_ok=True, parents=True)
    rel_dir = comp_def_dir.relative_to(tmp_path)
    element_arg = 'metadata.parties.*'
    expected_paths: List[ElementPath] = prepare_expected_element_paths(['metadata.parties.*'])
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(None, element_arg, rel_dir)
    assert expected_paths == element_paths


def test_parse_element_args():
    """Unit test parse multiple element args."""
    element_args = ['catalog.metadata', 'catalog.groups', 'catalog.controls']
    p0 = ElementPath('catalog.metadata')
    p1 = ElementPath('catalog.groups')
    p2 = ElementPath('catalog.controls')
    expected_paths: List[ElementPath] = [p0, p1, p2]
    element_paths = cmd_utils.parse_element_args(None, element_args, False)
    assert expected_paths == element_paths

    # element args with wildcard
    element_args = ['catalog.metadata', 'catalog.groups.*.controls.*.controls.*', 'catalog.controls.*.controls.*']
    p0 = ElementPath('catalog.metadata')
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls.*', parent_path=p1)
    p3 = ElementPath('control.controls.*', parent_path=p2)
    p4 = ElementPath('catalog.controls.*')
    p5 = ElementPath('control.controls.*', parent_path=p4)
    expected: List[ElementPath] = [p0, p1, p2, p3, p4, p5]
    assert cmd_utils.parse_element_args(None, element_args, False) == expected


@pytest.mark.parametrize('element_arg', ['catalog.metadata.*', 'catalog.*'])
def test_parse_element_args_split_model(element_arg, simplified_nist_catalog):
    """Test split of model with wildcard."""
    element_paths = cmd_utils.parse_element_arg(simplified_nist_catalog, element_arg, False)
    assert element_paths


@pytest.mark.parametrize(
    'element_arg',
    [
        ('component-definition.foo', []),
        ('component-definition.*', [['component-definition', 'components'], ['component-definition', 'metadata']]),
        ('component-definition.components', [['component-definition', 'components']]),
        ('component-definition.components.*', [['component-definition', 'components', '*']]),
        (
            'component-definition.components.*.roles',
            [['component-definition', 'components', '*'], ['defined-component', 'roles']]
        )
    ]
)
def test_parse_element_args_split_compdef(element_arg, sample_component_definition):
    """Test split of model with wildcard."""
    element_paths = cmd_utils.parse_element_arg(sample_component_definition, element_arg[0], False)
    assert len(element_paths) == len(element_arg[1])
    for ii in range(len(element_paths)):
        assert element_paths[ii]._path in element_arg[1]


@pytest.mark.parametrize('element_arg', ['catalog.metadata.*.roles', 'catalog', '', '*'])
def test_parse_element_arg_split_model_failures(element_arg, simplified_nist_catalog):
    """Test failures split of model with wildcard."""
    with pytest.raises(TrestleError):
        cmd_utils.parse_element_arg(simplified_nist_catalog, element_arg, False)
