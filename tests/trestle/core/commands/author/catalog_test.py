# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Tests for the catalog author module."""

import copy
import pathlib
import shutil
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from ruamel.yaml import YAML

from tests import test_utils

from trestle.cli import Trestle
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.catalog import CatalogAssemble, CatalogGenerate, CatalogInterface
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_io import ControlIOReader, ParameterRep
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal import catalog as cat
from trestle.oscal import profile as prof
from trestle.oscal.common import ParameterValue, Part, Property

markdown_name = 'my_md'


def _change_params(ac1_path: pathlib.Path, new_prose: str, make_change: bool) -> None:
    if make_change:
        assert test_utils.insert_text_in_file(ac1_path, 'Procedures {{', f'- \\[d\\] {new_prose}\n')
    assert test_utils.insert_text_in_file(ac1_path, 'Param_1_value', '    values: new value\n')
    assert test_utils.delete_line_in_file(ac1_path, 'Param_1_value')
    assert test_utils.insert_text_in_file(ac1_path, 'ac-1_prm_3', '    values: added param 3 value\n')


@pytest.mark.parametrize('set_parameters', [True, False])
@pytest.mark.parametrize('make_change', [True, False])
@pytest.mark.parametrize('use_orig_cat', [True, False])
@pytest.mark.parametrize('add_header', [True, False])
@pytest.mark.parametrize('use_cli', [True, False])
@pytest.mark.parametrize('dir_exists', [True, False])
def test_catalog_generate_assemble(
    set_parameters: bool,
    make_change: bool,
    use_orig_cat: bool,
    add_header: bool,
    use_cli: bool,
    dir_exists: bool,
    tmp_trestle_dir: pathlib.Path,
    monkeypatch: MonkeyPatch
) -> None:
    """Test the catalog markdown generator."""
    nist_catalog_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    cat_name = 'my_cat'
    md_name = 'my_md'
    assembled_cat_name = 'my_assembled_cat'
    catalog_dir = tmp_trestle_dir / f'catalogs/{cat_name}'
    catalog_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = catalog_dir / 'catalog.json'
    shutil.copy(nist_catalog_path, catalog_path)
    markdown_path = tmp_trestle_dir / md_name
    markdown_path.mkdir(parents=True, exist_ok=True)
    ac1_path = markdown_path / 'ac/ac-1.md'
    new_prose = 'My added item'
    assembled_cat_dir = tmp_trestle_dir / f'catalogs/{assembled_cat_name}'
    yaml_header_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    # convert catalog to markdown then assemble it after adding an item to a control
    if use_cli:
        test_args = f'trestle author catalog-generate -n {cat_name} -o {md_name}'.split()
        if add_header:
            test_args.extend(['-y', str(yaml_header_path)])
        monkeypatch.setattr(sys, 'argv', test_args)
        assert Trestle().run() == 0
        assert ac1_path.exists()
        _change_params(ac1_path, new_prose, make_change)
        test_args = f'trestle author catalog-assemble -m {md_name} -o {assembled_cat_name}'.split()
        if set_parameters:
            test_args.append('-sp')
        if use_orig_cat:
            test_args.extend(f'-n {cat_name}'.split())
        if dir_exists:
            assembled_cat_dir.mkdir()
        monkeypatch.setattr(sys, 'argv', test_args)
        assert Trestle().run() == 0
    else:
        catalog_generate = CatalogGenerate()
        yaml_header = {}
        if add_header:
            yaml = YAML(typ='safe')
            yaml_header = yaml.load(yaml_header_path.open('r'))
        assert CmdReturnCodes.SUCCESS.value == catalog_generate.generate_markdown(
            tmp_trestle_dir, catalog_path, markdown_path, yaml_header, False
        )
        assert (markdown_path / 'ac/ac-1.md').exists()
        _change_params(ac1_path, new_prose, make_change)
        if dir_exists:
            assembled_cat_dir.mkdir()
        orig_cat_name = cat_name if use_orig_cat else None
        assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
            tmp_trestle_dir, md_name, assembled_cat_name, orig_cat_name, set_parameters, False, ''
        )

    orig_cat: cat.Catalog = cat.Catalog.oscal_read(catalog_path)
    assembled_cat: cat.Catalog = cat.Catalog.oscal_read(assembled_cat_dir / 'catalog.json')
    assert (orig_cat.metadata.title == assembled_cat.metadata.title) == use_orig_cat
    interface_orig = CatalogInterface(orig_cat)
    # need to delete withdrawn controls because they won't be in the assembled catalog
    interface_orig.delete_withdrawn_controls()
    ac1 = interface_orig.get_control('ac-1')
    if make_change:
        # add the item manually to the original catalog so we can confirm the item was loaded correctly
        prop = Property(name='label', value='d.')
        new_part = Part(id='ac-1_smt.d', name='item', props=[prop], prose=new_prose)
        ac1.parts[0].parts.append(new_part)
        interface_orig.replace_control(ac1)
        orig_cat = interface_orig.get_catalog()
    if set_parameters:
        ac1.params[0].values = [ParameterValue(__root__='new value')]
        ac1.params[2].values = [ParameterValue(__root__='added param 3 value')]
        interface_orig.replace_control(ac1)
        orig_cat = interface_orig.get_catalog()
    elif not use_orig_cat:
        ac1.params = None
        interface_orig.replace_control(ac1)
        orig_cat = interface_orig.get_catalog()
    assert test_utils.catalog_interface_equivalent(interface_orig, assembled_cat, False)


def test_catalog_assemble_version(sample_catalog_rich_controls: cat.Catalog, tmp_trestle_dir: pathlib.Path) -> None:
    """Test catalog assemble version."""
    cat_name = 'my_cat'
    md_name = 'my_md'
    new_version = '1.2.3'
    assembled_cat_name = 'my_assembled_cat'
    catalog_dir = tmp_trestle_dir / f'catalogs/{cat_name}'
    catalog_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = catalog_dir / 'catalog.json'
    sample_catalog_rich_controls.oscal_write(catalog_path)
    markdown_path = tmp_trestle_dir / md_name
    catalog_generate = CatalogGenerate()
    assert CmdReturnCodes.SUCCESS.value == catalog_generate.generate_markdown(
        tmp_trestle_dir, catalog_path, markdown_path, {}, False
    )
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, cat_name, False, False, new_version
    )
    assembled_cat, assembled_cat_path = ModelUtils.load_top_level_model(
        tmp_trestle_dir,
        assembled_cat_name,
        cat.Catalog
    )
    assert assembled_cat.metadata.version.__root__ == new_version
    assert ModelUtils.model_age(assembled_cat) < test_utils.NEW_MODEL_AGE_SECONDS

    creation_time = assembled_cat_path.stat().st_mtime

    # assemble same way again and confirm no new write
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, assembled_cat_name, False, False, new_version
    )

    assert creation_time == assembled_cat_path.stat().st_mtime

    # assemble same way again but without parent specified and confirm no new write
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, None, False, False, new_version
    )

    assert creation_time == assembled_cat_path.stat().st_mtime

    # change version and confirm write
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, assembled_cat_name, False, False, 'xx'
    )

    assert creation_time < assembled_cat_path.stat().st_mtime


def test_catalog_interface(sample_catalog_rich_controls: cat.Catalog) -> None:
    """Test the catalog interface with complex controls."""
    interface = CatalogInterface(sample_catalog_rich_controls)
    n_controls = interface.get_count_of_controls_in_catalog(True)
    assert n_controls == 6

    control = interface.get_control('control_d1')
    new_title = 'updated d1'
    control.title = new_title
    interface.replace_control(control)
    interface.update_catalog_controls()
    assert interface._catalog.controls[1].controls[0].title == new_title


def test_catalog_interface_groups() -> None:
    """Test handling of groups of groups in CatalogInterface."""
    catalog: cat.Catalog = cat.Catalog.oscal_read(test_utils.JSON_TEST_DATA_PATH / 'nist_tutorial_catalog.json')
    interface = CatalogInterface(catalog)
    interface.update_catalog_controls()
    assert interface.get_count_of_controls_in_catalog(True) == 4
    assert interface.get_count_of_controls_in_catalog(False) == 4
    groups = list(interface.get_all_groups_from_catalog())
    assert len(groups) == 4


def test_get_sorted_controls_in_group(simplified_nist_catalog: cat.Catalog) -> None:
    """Test get sorted controls in group."""
    catalog_interface = CatalogInterface(simplified_nist_catalog)
    controls = catalog_interface.get_sorted_controls_in_group('ac')
    ids = [control.id for control in controls]
    # Confirm the start of list is not alphabetical but is numeric since it uses the control sort-ids for order
    ref_ids = ['ac-1', 'ac-2', 'ac-2.1', 'ac-2.2', 'ac-2.3', 'ac-2.4', 'ac-2.5', 'ac-2.6', 'ac-2.7', 'ac-2.8', 'ac-2.9']
    assert ids[:11] == ref_ids


@pytest.mark.parametrize('replace_params', [True, False])
def test_catalog_interface_merge_controls(replace_params: bool, sample_catalog_rich_controls: cat.Catalog) -> None:
    """Test merging of controls."""
    control_a = sample_catalog_rich_controls.groups[0].controls[0]
    control_b = copy.deepcopy(control_a)
    CatalogInterface.merge_controls(control_a, control_b, replace_params)
    assert control_a == control_b
    control_b.params[0].values = [ParameterValue(__root__='new value')]
    CatalogInterface.merge_controls(control_a, control_b, replace_params)
    if replace_params:
        assert control_a.params[0].values[0].__root__ == 'new value'
    else:
        assert control_a.params[0].values[0].__root__ == 'param_0_val'
    control_b.params = control_b.params[:1]
    CatalogInterface.merge_controls(control_a, control_b, replace_params)
    assert len(control_a.params) == 1 if replace_params else 2


def test_catalog_generate_failures(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test failures of author catalog."""
    # disallowed output name
    test_args = 'trestle author catalog-generate -n foo -o profiles'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1

    # catalog doesn't exist
    test_args = 'trestle author catalog-generate -n foo -o my_md'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1

    # bad yaml
    bad_yaml_path = str(test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml')
    test_args = f'trestle author catalog-generate -n foo -o my_md -y {bad_yaml_path}'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1


def test_catalog_assemble_failures(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test failurs of catalog assemble."""
    test_args = 'trestle author catalog-assemble -m foo -o my_md'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1

    (tmp_trestle_dir / 'foo').mkdir()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1


def test_get_profile_param_dict(tmp_trestle_dir: pathlib.Path) -> None:
    """Test get profile param dict for control."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    profile, profile_path = ModelUtils.load_top_level_model(
        tmp_trestle_dir,
        'test_profile_a',
        prof.Profile,
        FileContentType.JSON
    )
    profile_resolver = ProfileResolver()
    catalog = profile_resolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    catalog_interface = CatalogInterface(catalog)
    control = catalog_interface.get_control('ac-1')

    full_param_dict = CatalogInterface._get_full_profile_param_dict(profile)
    control_param_dict = CatalogInterface._get_profile_param_dict(control, full_param_dict, False)
    assert ControlIOReader.param_to_str(
        control_param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'all alert personnel'
    assert ControlIOReader.param_to_str(
        control_param_dict['ac-1_prm_6'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'monthly'
    # param 7 has no value so its label will be used
    assert ControlIOReader.param_to_str(
        control_param_dict['ac-1_prm_7'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'organization-defined events'


def test_catalog_generate_withdrawn(tmp_path: pathlib.Path, sample_catalog_rich_controls: cat.Catalog) -> None:
    """Test catalog generate when some controls are marked withdrawn."""
    control_a = sample_catalog_rich_controls.groups[0].controls[0]
    control_b = sample_catalog_rich_controls.groups[0].controls[1]
    group_id = sample_catalog_rich_controls.groups[0].id
    if not control_b.props:
        control_b.props = []
    control_b.props.append(Property(name='status', value='Withdrawn'))
    catalog_interface = CatalogInterface(sample_catalog_rich_controls)
    catalog_interface.write_catalog_as_markdown(tmp_path, {}, None, False)
    # confirm that the first control was written out but not the second
    path_a = tmp_path / group_id / (control_a.id + '.md')
    assert path_a.exists()
    path_b = tmp_path / group_id / (control_b.id + '.md')
    assert not path_b.exists()


def test_params_in_choice(
    tmp_trestle_dir: pathlib.Path, simplified_nist_catalog: cat.Catalog, simplified_nist_profile: prof.Profile
) -> None:
    """Confirm that parameters in choices are substituted properly."""
    # the nist simplified profile defines ac-4.4_prm_3, which is in the choices of ac-4.4_prm_2
    cat_name = 'simplified_nist_catalog'
    prof_name = 'simplified_nist_profile'
    ModelUtils.save_top_level_model(simplified_nist_catalog, tmp_trestle_dir, cat_name, FileContentType.JSON)
    ModelUtils.save_top_level_model(simplified_nist_profile, tmp_trestle_dir, prof_name, FileContentType.JSON)
    prof_path = ModelUtils.full_path_for_top_level_model(tmp_trestle_dir, prof_name, prof.Profile)
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    cat_interface = CatalogInterface(catalog)
    control = cat_interface.get_control('ac-4.4')
    val_1 = 'blocking the flow of the encrypted information'
    val_2 = 'terminating communications sessions attempting to pass encrypted information'
    val_3 = 'hacking the system'
    assert control.params[1].values[0].__root__ == val_1
    assert control.params[1].values[1].__root__ == val_2
    # confirm the choice text was set properly
    assert control.params[1].select.choice[3] == val_3
    assert control.params[2].values[0].__root__ == val_3
    assert catalog.params[1].values[0].__root__ == 'loose_2_val_from_prof'

    control = cat_interface.get_control('ac-1')
    param = control.params[0]
    assert param.props[0].value == 'prop value from prof'
    assert param.props[1].value == 'new prop value from prof'
    assert param.links[0].text == 'new text from prof'
    assert param.links[1].text == 'new link text'
    assert param.constraints[1].description == 'new constraint'
    assert param.guidelines[1].prose == 'new guideline'


def test_pulled_params_in_choice(
    tmp_trestle_dir: pathlib.Path, simplified_nist_catalog: cat.Catalog, simplified_nist_profile: prof.Profile
) -> None:
    """Confirm that parameters in choices are substituted properly and give lower priority to upstream subs."""
    # the nist catalog defines ac-4.4_prm_3, which is referenced by the choices of ac-4.4_prm_2
    # the nist simplified profile itself defines ac-4.4_prm_3 and thereby defines the choices in ac-4.4_prm_2
    # but it is also set by the pulling profile, which should have final say
    # in addition, both the simplified profile and the pulling profile define the desired values for ac-4.4_prm_2
    # the provided values need to be a subset of the choice options
    # the pulling profile should dictate what happens in a generate-assemble cycle for values and choices
    # so the generated markdown needs to substitute current set-param values into the choices instead of holding back
    cat_name = 'simplified_nist_catalog'
    prof_name = 'simplified_nist_profile'
    ModelUtils.save_top_level_model(simplified_nist_catalog, tmp_trestle_dir, cat_name, FileContentType.JSON)
    ModelUtils.save_top_level_model(simplified_nist_profile, tmp_trestle_dir, prof_name, FileContentType.JSON)
    pull_prof_name = 'pull_nist_profile'
    prof_path = ModelUtils.path_for_top_level_model(tmp_trestle_dir, pull_prof_name, prof.Profile, FileContentType.JSON)
    prof_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(test_utils.JSON_TEST_DATA_PATH / (pull_prof_name + '.json'), prof_path)

    # get the resolved profile catalog
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    cat_interface = CatalogInterface(catalog)

    # check values
    control = cat_interface.get_control('ac-4.4')
    val_1 = 'blocking the flow of the encrypted information'
    val_2 = 'from pulling profile'
    assert control.params[1].values[0].__root__ == val_1
    assert control.params[1].values[1].__root__ == val_2

    # confirm the choice text was handled properly
    # the param value and the choice should be set by the pulling profile
    assert control.params[2].values[0].__root__ == val_2
    assert control.params[1].select.choice[3] == val_2

    # this confirms the pulling profile sets the value of a loose param
    assert catalog.params[1].values[0].__root__ == 'loose_2_val_from_pulling'

    # confirm other attributes are as expected
    control = cat_interface.get_control('ac-1')
    param = control.params[0]
    assert param.props[0].value == 'prop value from prof'
    assert param.props[1].value == 'new prop value from prof'
    assert param.links[0].text == 'new text from prof'
    assert param.links[1].text == 'new link text'
    assert param.constraints[1].description == 'new constraint'
    assert param.guidelines[1].prose == 'new guideline'
