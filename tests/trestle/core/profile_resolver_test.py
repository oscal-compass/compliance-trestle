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
"""Tests profile_resolver module."""

import pathlib
from typing import List, Tuple

import pytest

from tests import test_utils

from trestle.core import generators as gens
from trestle.core.err import TrestleError
from trestle.core.profile_resolver import CatalogInterface, ProfileResolver
from trestle.core.repository import Repository
from trestle.oscal import catalog as cat
from trestle.oscal import common as com
from trestle.oscal import profile as prof
from trestle.utils import fs


def find_string_in_all_controls_prose(interface: CatalogInterface, seek_str: str) -> List[Tuple[str, str]]:
    """Find all instances of this string in catalog prose and return with control id."""
    hits: List[Tuple[str, str]] = []
    for control in interface.get_all_controls(True):
        hits.extend(interface.find_string_in_control(control, seek_str))
    return hits


def test_profile_resolver(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the resolver."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)

    prof_a_path = fs.path_for_top_level_model(tmp_trestle_dir, 'test_profile_a', prof.Profile, fs.FileContentType.JSON)
    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_a_path)
    interface = CatalogInterface(cat)
    list1 = find_string_in_all_controls_prose(interface, 'Detailed evidence logs')
    list2 = find_string_in_all_controls_prose(interface, 'full and complete compliance')

    assert len(list1) == 1
    assert len(list2) == 1

    assert interface.get_count_of_controls(False) == 6

    assert interface.get_count_of_controls(True) == 7

    assert len(cat.controls) == 1

    assert interface.get_dependent_control_ids('ac-3') == ['ac-3.3']

    assert interface.get_control('a-1').parts[0].parts[0].parts[0].id == 'a-1_deep'
    assert interface.get_control('a-1').parts[0].parts[0].parts[0].prose == 'Extra added part in subpart'


def test_deep_catalog() -> None:
    """Test ssp generation with deep catalog."""
    catalog = test_utils.generate_complex_catalog()
    interface = CatalogInterface(catalog)
    assert interface.get_count_of_controls(False) == 10
    assert interface.get_count_of_controls(True) == 15


def test_fail_when_reference_id_is_not_given_after_or_before(tmp_trestle_dir: pathlib.Path) -> None:
    """Test when by_id is not given and position is set to after or before it fails."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    repo = Repository(tmp_trestle_dir)
    repo.load_and_import_model(cat_path, 'nist_cat')
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'profile_with_incorrect_alter.json'
    repo.load_and_import_model(prof_path, 'incorrect_profile')

    with pytest.raises(TrestleError):
        ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)


def test_ok_when_props_added(tmp_trestle_dir: pathlib.Path) -> None:
    """Test when by_id is not given and position is set to after or before it defaults to after."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    repo = Repository(tmp_trestle_dir)
    repo.load_and_import_model(cat_path, 'nist_cat')
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'profile_with_alter_props.json'
    repo.load_and_import_model(prof_path, 'profile_with_alter_props')

    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    assert catalog


def test_profile_missing_position(tmp_trestle_dir: pathlib.Path) -> None:
    """Test when alter adds parts is missing position it defaults to after."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    repo = Repository(tmp_trestle_dir)
    repo.load_and_import_model(cat_path, 'nist_cat')
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'profile_missing_position.json'
    repo.load_and_import_model(prof_path, 'profile_missing_position')

    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    assert catalog


def test_all_positions_for_alter_can_be_resolved(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that all alter adds positions can be resolved."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    repo = Repository(tmp_trestle_dir)
    repo.load_and_import_model(cat_path, 'nist_cat')

    prof_d_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_d.json'
    repo.load_and_import_model(prof_d_path, 'test_profile_d')

    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_d_path)

    interface = CatalogInterface(cat)
    control_a1 = interface.get_control('ac-1')
    control_a2 = interface.get_control('ac-2')

    assert control_a1.parts[0].id == 'ac-1_first_lev1'
    assert control_a1.parts[1].parts[3].id == 'ac-1_last_lev2'
    assert control_a1.parts[2].id == 'ac-1_after1_ac-1_smt_lev1'
    assert control_a1.parts[3].id == 'ac-1_after2_ac-1_smt_lev1'
    assert control_a1.parts[1].parts[0].parts[1].id == 'ac-1_smt_before1_a.2_lev3'
    assert control_a1.parts[1].parts[0].parts[2].id == 'ac-1_smt_before2_a.2_lev3'
    assert control_a1.parts[1].parts[0].parts[3].parts[0].id == 'ac-1_smt_inside1_at_the_end_a.2_lev4'
    assert control_a1.parts[1].parts[0].parts[3].parts[1].id == 'ac-1_smt_inside2_at_the_end_a.2_lev4'
    assert control_a2.parts[0].id == 'ac-2_implgdn_lev1'


def test_profile_resolver_merge(sample_catalog_rich_controls) -> None:
    """Test profile resolver merge."""
    profile = gens.generate_sample_model(prof.Profile)
    merge = ProfileResolver.Merge(profile)
    merged = gens.generate_sample_model(cat.Catalog)
    new_merged = merge._merge_catalog(merged, sample_catalog_rich_controls)
    catalog_interface = CatalogInterface(new_merged)
    assert catalog_interface.get_count_of_controls(True) == 5

    merged = gens.generate_sample_model(cat.Catalog)
    merged.controls = []
    new_merged = merge._merge_catalog(merged, sample_catalog_rich_controls)
    catalog_interface = CatalogInterface(new_merged)
    assert catalog_interface.get_count_of_controls(True) == 5


def test_profile_resolver_failures() -> None:
    """Test failure modes of profile resolver."""
    profile = gens.generate_sample_model(prof.Profile)
    modify = ProfileResolver.Modify(profile)
    control = gens.generate_sample_model(cat.Control)
    # this should not cause error
    add = prof.Add()
    with pytest.raises(TrestleError):
        modify._add_to_control(add, control)
    add.parts = []
    with pytest.raises(TrestleError):
        modify._add_to_control(add, control)
    add.position = prof.Position.before
    with pytest.raises(TrestleError):
        modify._add_to_control(add, control)


@pytest.mark.parametrize(
    'param_id, param_text, prose, result',
    [
        ('ac-2_smt.1', 'hello', 'ac-2_smt.1', 'hello'), ('ac-2_smt.1', 'hello', 'ac-2_smt.1 there', 'hello there'),
        ('ac-2_smt.1', 'hello', ' ac-2_smt.1 there', ' hello there'),
        ('ac-2_smt.1', 'hello', ' xac-2_smt.1 there', ' xac-2_smt.1 there'),
        ('ac-2_smt.1', 'hello', ' ac-2_smt.1 there ac-2_smt.1', ' hello there hello'),
        ('ac-2_smt.1', 'hello', ' ac-2_smt.1 there ac-2_smt.10', ' hello there ac-2_smt.10')
    ]
)
def test_replace_params(param_id, param_text, prose, result) -> None:
    """Test cases of replacing param in string."""
    assert ProfileResolver.Modify._replace_id_with_text(prose, param_id, param_text) == result


def test_profile_resolver_param_sub() -> None:
    """Test profile resolver param sub via regex."""
    control = gens.generate_sample_model(cat.Control)
    id_1 = 'ac-2_smt.1'
    id_10 = 'ac-2_smt.10'
    param_text = 'Make sure that {{insert: param, ac-2_smt.1}} is very {{ac-2_smt.10}} today.'
    param_raw_dict = {id_1: 'the cat', id_10: 'well fed'}
    param_value_1 = com.ParameterValue(__root__=param_raw_dict[id_1])
    param_value_10 = com.ParameterValue(__root__=param_raw_dict[id_10])
    # the SetParameters would come from the profile and modify control contents via moustaches
    set_param_1 = prof.SetParameter(param_id=id_1, values=[param_value_1])
    set_param_10 = prof.SetParameter(param_id=id_10, values=[param_value_10])
    param_dict = {id_1: set_param_1, id_10: set_param_10}
    param_1 = com.Parameter(id=id_1, values=[param_value_1])
    param_10 = com.Parameter(id=id_10, values=[param_value_10])
    control.params = [param_1, param_10]
    new_text = ProfileResolver.Modify._replace_params(param_text, control, param_dict)
    assert new_text == 'Make sure that the cat is very well fed today.'


def test_parameter_resolution(tmp_trestle_dir: pathlib.Path) -> None:
    """Test whether expected order of operations is preserved for parameter substution."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)

    prof_e_path = fs.path_for_top_level_model(tmp_trestle_dir, 'test_profile_e', prof.Profile, fs.FileContentType.JSON)
    profile_e_parameter_string = '## Override value ##'
    profile_a_value = 'all alert personell'

    # based on 800-53 rev 5
    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_e_path)
    interface = CatalogInterface(cat)
    control = interface.get_control('ac-1')
    locations = interface.find_string_in_control(control, profile_e_parameter_string)
    locations_a = interface.find_string_in_control(control, profile_a_value)
    # TODO: This behaviour will need to be corrected, see issue #
    # Correct behaviour
    # assert len(locations) == 1  # noqa: E800
    # assert len(locations_a) == 0  # noqa: E800
    # Incorrect behaviour
    assert len(locations) == 0
    assert len(locations_a) == 1
