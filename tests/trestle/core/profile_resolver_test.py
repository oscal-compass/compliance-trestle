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

import copy
import pathlib
import shutil
from typing import List, Tuple

import pytest

from tests import test_utils

from trestle.common.const import RESOLUTION_SOURCE
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core import generators as gens
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_interface import ControlInterface, ParameterRep
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.repository import Repository
from trestle.core.resolver.merge import Merge
from trestle.oscal import OSCAL_VERSION
from trestle.oscal import catalog as cat
from trestle.oscal import common as com
from trestle.oscal import profile as prof


def find_string_in_all_controls_prose(interface: CatalogInterface, seek_str: str) -> List[Tuple[str, str]]:
    """Find all instances of this string in catalog prose and return with control id."""
    hits: List[Tuple[str, str]] = []
    for control in interface.get_all_controls_from_catalog(True):
        hits.extend(interface.find_string_in_control(control, seek_str))
    return hits


def test_profile_resolver(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the resolver."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)

    test_prof_name = 'test_profile_a'
    test_prof, test_prof_path = ModelUtils.load_model_for_class(tmp_trestle_dir, test_prof_name, prof.Profile)
    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, test_prof_path)
    interface = CatalogInterface(cat)
    # added part ac-1_expevid from prof a
    list1 = find_string_in_all_controls_prose(interface, 'Detailed evidence logs')
    # modify param ac-3.3_prm_2 in prof b
    list2 = find_string_in_all_controls_prose(interface, 'full and complete compliance')

    assert len(list1) == 1
    assert len(list2) == 1

    assert interface.get_count_of_controls_in_catalog(False) == 6

    assert interface.get_count_of_controls_in_catalog(True) == 7

    assert len(cat.controls) == 3

    assert interface.get_dependent_control_ids('ac-3') == ['ac-3.3']

    # confirm that upstream props are captured
    ac_33 = interface.get_control('ac-3.3')
    assert ac_33.params[0].props[0].name == 'set_param_prof_b_prop'
    assert ac_33.params[0].props[0].value == 'set param prof b prop value'
    assert ac_33.props[0].name == 'add_prof_b_prop'
    assert ac_33.props[0].value == 'add prof b prop value'

    control = interface.get_control('a-1')
    assert control.parts[0].parts[0].id == 'a-1_deep'
    assert control.parts[0].parts[0].prose == 'Extra added part in subpart'

    assert cat.metadata.title == test_prof.metadata.title
    assert cat.metadata.oscal_version.__root__ == OSCAL_VERSION
    assert cat.metadata.links[0].href == 'trestle://catalogs/nist_cat/catalog.json'
    assert cat.metadata.links[0].rel == RESOLUTION_SOURCE
    assert cat.metadata.links[1].href == 'trestle://profiles/test_profile_b/profile.json'
    assert cat.metadata.links[0].rel == RESOLUTION_SOURCE


def test_deep_catalog() -> None:
    """Test ssp generation with deep catalog."""
    catalog = test_utils.generate_complex_catalog()
    interface = CatalogInterface(catalog)
    assert interface.get_count_of_controls_in_catalog(False) == 13
    assert interface.get_count_of_controls_in_catalog(True) == 16


def test_ok_when_reference_id_is_not_given_after_or_before(tmp_trestle_dir: pathlib.Path) -> None:
    """Test when by_id is not given and position is set to after or before it fails."""
    cat_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    repo = Repository(tmp_trestle_dir)
    repo.load_and_import_model(cat_path, 'nist_cat')
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'profile_with_incorrect_alter.json'
    repo.load_and_import_model(prof_path, 'incorrect_profile')

    # this originally failed but now it is OK based on OSCAL saying to default to starting or ending if no by_id
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    assert catalog


def test_ok_when_props_added(tmp_trestle_dir: pathlib.Path) -> None:
    """Test when by_id is not given and position is set to after or before it defaults to after."""
    cat_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    repo = Repository(tmp_trestle_dir)
    repo.load_and_import_model(cat_path, 'nist_cat')
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'profile_with_alter_props.json'
    repo.load_and_import_model(prof_path, 'profile_with_alter_props')

    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    ac_1 = catalog.groups[0].controls[0]
    assert ac_1.props[3].name == 'ac1_foo'
    assert ac_1.props[3].value == 'ac1 bar'
    assert ac_1.parts[2].props[0].name == 'part_prop'
    assert ac_1.parts[2].props[0].value == 'part_prop_val'


def test_profile_missing_position(tmp_trestle_dir: pathlib.Path) -> None:
    """Test when alter adds parts is missing position it defaults to after."""
    cat_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    repo = Repository(tmp_trestle_dir)
    repo.load_and_import_model(cat_path, 'nist_cat')
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'profile_missing_position.json'
    repo.load_and_import_model(prof_path, 'profile_missing_position')

    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    assert catalog


def test_all_positions_for_alter_can_be_resolved(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that all alter adds positions can be resolved."""
    cat_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
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


def test_profile_resolver_merge(sample_catalog_rich_controls: cat.Catalog) -> None:
    """Test profile resolver merge."""
    profile = gens.generate_sample_model(prof.Profile)
    method = 'merge'
    combine = prof.Combine(method=method)
    profile.merge = prof.Merge(combine=combine)
    merge = Merge(profile)

    # merge into empty catalog
    merged = gens.generate_sample_model(cat.Catalog)
    new_merged = merge._merge_catalog(merged, sample_catalog_rich_controls)
    catalog_interface = CatalogInterface(new_merged)
    assert catalog_interface.get_count_of_controls_in_catalog(True) == 6

    # add part to first control and merge, then make sure it is there
    part = com.Part(name='foo', title='added part')
    control_id = sample_catalog_rich_controls.controls[0].id
    cat_with_added_part = copy.deepcopy(sample_catalog_rich_controls)
    cat_with_added_part.controls[0].parts.append(part)
    # add extra control in group and make sure it is handled properly
    n_controls = len(cat_with_added_part.groups[0].controls)
    new_control = copy.deepcopy(cat_with_added_part.groups[0].controls[n_controls - 1])
    new_control.id = new_control.id + 'b'
    cat_with_added_part.groups[0].controls.append(new_control)
    final_merged = merge._merge_catalog(sample_catalog_rich_controls, cat_with_added_part)
    catalog_interface = CatalogInterface(final_merged)
    assert catalog_interface.get_count_of_controls_in_catalog(True) == 7
    assert catalog_interface.get_control(control_id).parts[-1].name == 'foo'

    # add part to first control and merge but with use-first.  The part should not be there at end.
    method = prof.Method.use_first
    combine = prof.Combine(method=method)
    profile.merge = prof.Merge(combine=combine)
    merge = Merge(profile)
    final_merged = merge._merge_catalog(sample_catalog_rich_controls, cat_with_added_part)
    catalog_interface = CatalogInterface(final_merged)
    assert catalog_interface.get_count_of_controls_in_catalog(True) == 7
    assert len(catalog_interface.get_control(control_id).parts) == 1

    # now force a merge with keep
    profile.merge = None
    merge_keep = Merge(profile)
    merged_keep = merge_keep._merge_catalog(new_merged, sample_catalog_rich_controls)
    assert CatalogInterface(merged_keep).get_count_of_controls_in_catalog(True) == 12


@pytest.mark.parametrize(
    'param_id, param_text, prose, result',
    [
        ('ac-2_smt.1', 'hello', 'ac-2_smt.1', 'hello'), ('ac-2_smt.1', 'hello', 'ac-2_smt.1 there', 'hello there'),
        ('ac-2_smt.1', 'hello', ' ac-2_smt.1 there', ' hello there'),
        ('ac-2_smt.1', 'hello', ' xac-2_smt.1 there', ' xac-2_smt.1 there'),
        ('ac-2_smt.1', 'hello', 'ac-2_smt.1 there ac-2_smt.1', 'hello there hello'),
        ('ac-2_smt.1', 'hello', ' ac-2_smt.1 there ac-2_smt.10', ' hello there my 10 str'),
        ('ac-2_smt.1', 'hello', ' ac-2_smt.1 there ac-2_smt.10x', ' hello there ac-2_smt.10x'),
        ('ac-2_smt.1', 'hello', ' ac-2_smt.1 there _ac-2_smt.10', ' hello there _ac-2_smt.10')
    ]
)
def test_replace_params(param_id, param_text, prose, result) -> None:
    """Test cases of replacing param in string."""
    param = com.Parameter(id=param_id, values=[param_text])
    param_10 = com.Parameter(id='ac-2_smt.10', values=['my 10 str'])
    param_dict = {param_id: param, 'ac-1_smt.10': param_10}
    assert ControlInterface._replace_ids_with_text(prose, ParameterRep.VALUE_OR_STRING_NONE, param_dict) == result


def test_replace_params_assignment_mode(simplified_nist_catalog: cat.Catalog) -> None:
    """Test replacement of params in assignment mode."""
    cat_interface = CatalogInterface(simplified_nist_catalog)
    param_dict = cat_interface._get_full_param_dict()
    ac_44 = copy.deepcopy(cat_interface.get_control('ac-4.4'))
    orig_prose = ac_44.parts[0].prose
    # test the case where a selection has parameters in choices but no value was assigned
    ControlInterface.replace_control_prose(
        ac_44, param_dict, '[.]', ParameterRep.ASSIGNMENT_FORM, False, 'IBM Assignment:', 'Assignment:'
    )
    assert ac_44.parts[
        0
    ].prose == 'Prevent encrypted information from bypassing [Assignment: organization-defined information flow control mechanisms] by [Selection (one or more): decrypting the information; blocking the flow of the encrypted information; terminating communications sessions attempting to pass encrypted information;  [IBM Assignment: my procedure] ].'  # noqa E501
    value = 'blocking the flow of the encrypted information'
    param_dict['ac-4.4_prm_2'].values = [value]
    ac_44.parts[0].prose = orig_prose
    # test the case where values for choices are assigned
    ControlInterface.replace_control_prose(
        ac_44, param_dict, '[.]', ParameterRep.ASSIGNMENT_FORM, False, 'IBM Assignment:', 'Assignment:'
    )
    assert ac_44.parts[
        0
    ].prose == f'Prevent encrypted information from bypassing [Assignment: organization-defined information flow control mechanisms] by [IBM Assignment: {value}].'  # noqa E501

    ac_44 = copy.deepcopy(cat_interface.get_control('ac-4.4'))
    ControlInterface.replace_control_prose(ac_44, param_dict, '[.]', ParameterRep.LABEL_FORM, False, None, 'Label:')
    assert ac_44.parts[
        0
    ].prose != f'Prevent encrypted information from bypassing [organization-defined information flow control mechanisms] by  [Label: organization-defined procedure or method] ].'  # noqa E501


def test_profile_resolver_param_sub() -> None:
    """Test profile resolver param sub via regex."""
    id_1 = 'ac-2_smt.1'
    param_1 = com.Parameter(id=id_1, values=['the cat'])
    id_10 = 'ac-2_smt.10'
    param_10 = com.Parameter(id=id_10, values=['well fed'])

    param_text = 'Make sure that {{insert: param, ac-2_smt.1}} is very {{ac-2_smt.10}} today.  Very {{ac-2_smt.10}}!'
    param_dict = {id_1: param_1, id_10: param_10}
    new_text = ControlInterface._replace_params(param_text, param_dict)
    assert new_text == 'Make sure that the cat is very well fed today.  Very well fed!'


def test_parameter_resolution(tmp_trestle_dir: pathlib.Path) -> None:
    """Test whether expected order of operations is preserved for parameter substution."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)

    prof_e_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'test_profile_e', prof.Profile, FileContentType.JSON
    )
    profile_e_parameter_string = '## Override value ##'
    profile_a_value = 'all alert personnel'

    # based on 800-53 rev 5
    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_e_path)
    interface = CatalogInterface(cat)
    control = interface.get_control('ac-1')
    locations = interface.find_string_in_control(control, profile_e_parameter_string)
    locations_a = interface.find_string_in_control(control, profile_a_value)
    assert len(locations) == 1
    assert len(locations_a) == 0
    assert len(control.params[1].constraints) == 1


def test_merge_params() -> None:
    """Test the merge of params."""
    params: List[com.Parameter] = test_utils.generate_param_list('foo', 2)
    # ids don't need to match in merge but normally they would
    params[1].id = params[0].id
    # kill remarks to confirm it is filled in by merge
    params[0].remarks = None
    profile = gens.generate_sample_model(prof.Profile)
    merge = Merge(profile)
    merge._merge_items(params[0], params[1], 'merge')
    assert params[0]
    # the contraints in each are identical so they don't merge
    assert len(params[0].constraints) == 1
    assert len(params[0].guidelines) == 2
    assert len(params[0].props) == 2
    # confirm that in the merge, the source remark overwrote the dest remark because it was None
    assert params[0].remarks == params[1].remarks


def test_merge_two_catalogs() -> None:
    """Test the merge of two complex catalogs."""
    cat_1 = test_utils.generate_complex_catalog('foo')
    cat_2 = test_utils.generate_complex_catalog('bar')
    cat_2.controls[0].id = cat_1.controls[0].id
    method = 'merge'
    combine = prof.Combine(method=method)
    profile = gens.generate_sample_model(prof.Profile)
    profile.merge = prof.Merge(combine=combine)
    merge = Merge(profile)
    merge._merge_two_catalogs(cat_1, cat_2, method, True)
    assert cat_1
    assert len(cat_1.controls) == 7
    assert len(cat_1.groups) == 4
    assert len(cat_1.params) == 6


def test_add_props(tmp_trestle_dir: pathlib.Path) -> None:
    """Test all types of property additions."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    prof_f_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'test_profile_f', prof.Profile, FileContentType.JSON
    )
    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_f_path)
    interface = CatalogInterface(cat)
    ac_3 = interface.get_control('ac-3')

    assert len(ac_3.props) == 6
    assert ac_3.props[-1].value == 'four'

    for part in ac_3.parts:
        if part.id == 'ac-3_stmt':
            assert len(part.props) == 4

    ac_5 = interface.get_control('ac-5')
    for part in ac_5.parts:
        if part.id == 'ac-5_stmt':
            for sub_part in part.parts:
                if sub_part.id == 'ac-5_smt.a':
                    assert len(sub_part.props) == 4


def test_add_props_before_after_ok(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test for property addition behavior with before or after.

    Properties added with before or after will default to starting or ending.
    """
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    prof_g_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'test_profile_g', prof.Profile, FileContentType.JSON
    )
    _ = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_g_path)


def test_get_control_and_group_info_from_catalog(tmp_trestle_dir: pathlib.Path) -> None:
    """Test get all groups from the catalog."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)

    prof_a_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'test_profile_a', prof.Profile, FileContentType.JSON
    )
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_a_path)
    cat_interface = CatalogInterface(catalog)

    all_groups_top = cat_interface.get_all_controls_from_catalog(recurse=False)
    assert len(list(all_groups_top)) == 6

    all_groups_rec = cat_interface.get_all_controls_from_catalog(recurse=True)
    assert len(list(all_groups_rec)) == 7

    all_group_ids = cat_interface.get_group_ids()
    assert len(all_group_ids) == 1

    statement_label, part = cat_interface.get_statement_label_if_exists('ac-1', 'ac-1_smt.c.2')
    assert statement_label == '2.'
    assert part.id == 'ac-1_smt.c.2'

    cat_path = cat_interface.get_control_path('ac-2')
    assert cat_path[0] == 'ac'
    assert len(cat_path) == 1


def test_profile_resolver_circular_ref(tmp_trestle_dir: pathlib.Path) -> None:
    """Test rejection of circular import refs."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    prof_a_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'test_profile_a', prof.Profile, FileContentType.JSON
    )
    # add new import to profile_c so it reloads prof_a in circular manner
    prof_c: prof.Profile
    prof_c, prof_c_path = ModelUtils.load_model_for_class(tmp_trestle_dir, 'test_profile_c', prof.Profile)
    imp = prof.Import(href='trestle://profiles/test_profile_a/profile.json')
    prof_c.imports.append(imp)
    prof_c.oscal_write(prof_c_path)
    with pytest.raises(TrestleError):
        _ = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_a_path)


def test_profile_resolver_no_params(tmp_trestle_dir: pathlib.Path) -> None:
    """Test profile resolver when missing param values."""
    prof_name = 'my_prof'
    nist_catalog_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    trestle_cat_dir = tmp_trestle_dir / 'catalogs/nist_cat'
    trestle_cat_dir.mkdir(exist_ok=True, parents=True)
    shutil.copy(nist_catalog_path, trestle_cat_dir / 'catalog.json')
    profile_dir = tmp_trestle_dir / f'profiles/{prof_name}'
    profile_dir.mkdir(parents=True, exist_ok=True)
    simple_prof_path = test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile_no_params.json'
    profile_path = profile_dir / 'profile.json'
    shutil.copy(simple_prof_path, profile_path)
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    catalog_str = catalog.oscal_serialize_json()
    # make sure no moustaches remain that would confuse jinja
    assert '{{' not in catalog_str


def test_remote_profile_relative_cat(tmp_trestle_dir: pathlib.Path) -> None:
    """Test profile resolver with remote profile and import of relative catalog path."""
    profile_path = 'https://raw.githubusercontent.com/usnistgov/oscal-content/feature-basic-end-to-end-example/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_LOW-baseline_profile.json'  # noqa E501
    resolved_cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    assert len(resolved_cat.groups) > 10
