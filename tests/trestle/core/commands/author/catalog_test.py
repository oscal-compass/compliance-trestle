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

import argparse
import copy
import pathlib
import shutil
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from ruamel.yaml import YAML

from tests import test_utils

from trestle.cli import Trestle
from trestle.common import const, file_utils
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_api import CatalogAPI
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.catalog.catalog_merger import CatalogMerger
from trestle.core.commands.author.catalog import CatalogAssemble, CatalogGenerate
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.import_ import ImportCmd
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import ControlInterface, ParameterRep
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal import catalog as cat
from trestle.oscal import profile as prof
from trestle.oscal.common import Part, Property

markdown_name = 'my_md'


def _change_params(ac1_path: pathlib.Path, new_prose: str, make_change: bool) -> None:
    if make_change:
        assert file_utils.insert_text_in_file(ac1_path, 'Procedures {{', f'- \\[d\\] {new_prose}\n')
    assert test_utils.delete_line_in_file(ac1_path, 'ac-1_prm_1', 1)
    assert test_utils.replace_line_in_file_after_tag(
        ac1_path, 'trestle-set-params', '  ac-1_prm_1:\n    values:\n      - new value\n'
    )
    assert test_utils.replace_line_in_file_after_tag(
        ac1_path, 'ac-1_prm_3', '    values:\n      - added param 3 value\n'
    )


@pytest.mark.parametrize('set_parameters_flag', [True, False])
@pytest.mark.parametrize('make_change', [True, False])
@pytest.mark.parametrize('use_orig_cat', [True, False])
@pytest.mark.parametrize('add_header', [True, False])
@pytest.mark.parametrize('use_cli', [True, False])
@pytest.mark.parametrize('dir_exists', [True, False])
def test_catalog_generate_assemble(
    set_parameters_flag: bool,
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

    context = ControlContext.generate(ContextPurpose.CATALOG, True, tmp_trestle_dir, markdown_path)
    context.set_parameters_flag = set_parameters_flag

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
        if set_parameters_flag:
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
            tmp_trestle_dir, md_name, assembled_cat_name, orig_cat_name, set_parameters_flag, False, ''
        )

    orig_cat: cat.Catalog = cat.Catalog.oscal_read(catalog_path)
    assembled_cat: cat.Catalog = cat.Catalog.oscal_read(assembled_cat_dir / 'catalog.json')
    assert (orig_cat.metadata.title == assembled_cat.metadata.title) == use_orig_cat
    interface_orig = CatalogInterface(orig_cat)
    # need to delete withdrawn controls because they won't be in the assembled catalog
    interface_orig.delete_withdrawn_controls()
    ac1 = interface_orig.get_control('ac-1')
    ac44 = interface_orig.get_control('ac-4.4')
    if make_change:
        # add the item manually to the original catalog so we can confirm the item was loaded correctly
        prop = Property(name='label', value='d.')
        new_part = Part(id='ac-1_smt.d', name='item', props=[prop], prose=new_prose)
        ac1.parts[0].parts.append(new_part)
        interface_orig.replace_control(ac1)
        orig_cat = interface_orig.get_catalog()
    if set_parameters_flag:
        ac1.params[0].values = ['new value']
        ac1.params[2].values = ['added param 3 value']
        interface_orig.replace_control(ac1)
        orig_cat = interface_orig.get_catalog()
    elif not use_orig_cat:
        ac1.params = None
        # ac 4.4 has a parameter set in it that needs to be removed if set_param=False and use_orig_cat=False
        ac44.params = None
        interface_orig.replace_control(ac1)
        orig_cat = interface_orig.get_catalog()
    if use_orig_cat:
        ac1 = assembled_cat.groups[0].controls[0]
        assert ac1.props[2].name == 'extra_prop'
        assert ac1.props[2].value == 'extra value'
        assert ac1.parts[0].props[0].name == 'prop_in_part'
        assert ac1.parts[0].props[0].value == 'value in part'
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

    # generate the catalog markdown
    assert CmdReturnCodes.SUCCESS.value == catalog_generate.generate_markdown(
        tmp_trestle_dir, catalog_path, markdown_path, {}, False
    )

    # assemble the catalog the first time
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, cat_name, False, False, new_version
    )

    # load the freshly assembled catalog
    assembled_cat, assembled_cat_path = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        assembled_cat_name,
        cat.Catalog
    )

    # confirm it is a fresh file with the version set as requested
    assert assembled_cat.metadata.version == new_version
    assert ModelUtils.model_age(assembled_cat) < test_utils.NEW_MODEL_AGE_SECONDS
    creation_time = assembled_cat_path.stat().st_mtime

    # assemble same way again and confirm no new write
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, None, False, False, new_version
    )

    assert creation_time == assembled_cat_path.stat().st_mtime

    # assemble same way again with parent name specified and confirm no new write
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, assembled_cat_name, False, False, new_version
    )

    assert creation_time == assembled_cat_path.stat().st_mtime

    # change version and confirm write
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, assembled_cat_name, False, False, 'xx'
    )

    assert creation_time < assembled_cat_path.stat().st_mtime

    control_text = """# control_q - \[The xy control group\] this is control q

## Control Statement
"""
    # add a new markdown control and make sure it is assembled
    control_path = tmp_trestle_dir / 'my_md/xy/control_q.md'
    with open(control_path, 'w') as f:
        f.write(control_text)
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, assembled_cat_name, False, False, 'xx2'
    )

    catalog, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'my_assembled_cat', cat.Catalog, FileContentType.JSON)
    interface = CatalogInterface(catalog)
    assert interface.get_count_of_controls_in_catalog(True) == 7

    # make additions to a sub control and confirm they end up in the assembled catalog
    control_d1_text = """---
x-trestle-set-params:
  param_new:
    values: new param value
---
# control_d1 - \[\] this is control d1

## Control Statement

New control statement.
"""
    control_d1_path = tmp_trestle_dir / 'my_md/control_d1.md'
    with open(control_d1_path, 'w') as f:
        f.write(control_d1_text)
    # need to set parameters during assembly
    assert CmdReturnCodes.SUCCESS.value == CatalogAssemble.assemble_catalog(
        tmp_trestle_dir, md_name, assembled_cat_name, assembled_cat_name, True, False, 'xx3'
    )

    catalog, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'my_assembled_cat', cat.Catalog, FileContentType.JSON)
    interface = CatalogInterface(catalog)
    assert interface.get_count_of_controls_in_catalog(True) == 7
    control_d = interface.get_control('control_d')
    assert control_d.controls[0].params[0].id == 'param_new'
    assert control_d.controls[0].params[0].values[0] == 'new param value'


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


def test_get_statement_parts(simplified_nist_catalog: cat.Catalog) -> None:
    """Test the catalog interface with complex controls."""
    interface = CatalogInterface(simplified_nist_catalog)
    parts = interface.get_statement_parts('ac-1')
    assert len(parts) == 10
    prt = parts[0]
    assert prt['indent'] == 0
    assert prt['label'] == ''
    assert prt['prose'] == 'The organization:'
    prt = parts[4]
    assert prt['indent'] == 3
    assert prt['label'] == '(b)'
    assert prt['prose'].startswith('Is consistent with')


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
    CatalogMerger.merge_controls(control_a, control_b, replace_params)
    assert control_a == control_b
    control_b.params[0].values = ['new value']
    CatalogMerger.merge_controls(control_a, control_b, replace_params)
    if replace_params:
        assert control_a.params[0].values[0] == 'new value'
    else:
        assert control_a.params[0].values[0] == 'param_0_val'
    control_b.params = control_b.params[:1]
    CatalogMerger.merge_controls(control_a, control_b, replace_params)
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
    profile, profile_path = ModelUtils.load_model_for_class(
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
    assert ControlInterface.param_to_str(
        control_param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'all alert personnel'
    assert ControlInterface.param_to_str(
        control_param_dict['ac-1_prm_6'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'monthly'
    # param 7 has no value so its label will be used
    assert ControlInterface.param_to_str(
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
    context = ControlContext.generate(ContextPurpose.CATALOG, True, tmp_path, tmp_path)
    catalog_api = CatalogAPI(catalog=sample_catalog_rich_controls, context=context)
    catalog_api.write_catalog_as_markdown()
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
    prof_path = ModelUtils.get_model_path_for_name_and_class(tmp_trestle_dir, prof_name, prof.Profile)
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    cat_interface = CatalogInterface(catalog)
    control = cat_interface.get_control('ac-4.4')
    val_3 = 'hacking the system'
    # confirm the choice text was set properly
    assert control.params[1].select.choice[3] == val_3
    assert control.params[2].values[0] == val_3
    assert catalog.params[1].values[0] == 'loose_2_val_from_prof'

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
    prof_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, pull_prof_name, prof.Profile, FileContentType.JSON
    )
    prof_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(test_utils.JSON_TEST_DATA_PATH / (pull_prof_name + '.json'), prof_path)

    # get the resolved profile catalog
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    cat_interface = CatalogInterface(catalog)

    # check values
    control = cat_interface.get_control('ac-4.4')
    val_1 = 'blocking the flow of the encrypted information'
    val_2 = 'from pulling profile'
    assert control.params[1].values[0] == val_1
    assert control.params[1].values[1] == val_2

    # confirm the choice text was handled properly
    # the param value and the choice should be set by the pulling profile
    assert control.params[2].values[0] == val_2
    assert control.params[1].select.choice[3] == val_2

    # this confirms the pulling profile sets the value of a loose param
    assert catalog.params[1].values[0] == 'loose_2_val_from_pulling'

    # confirm other attributes are as expected
    control = cat_interface.get_control('ac-1')
    param = control.params[0]
    assert param.props[0].value == 'prop value from prof'
    assert param.props[1].value == 'new prop value from prof'
    assert param.links[0].text == 'new text from prof'
    assert param.links[1].text == 'new link text'
    assert param.constraints[1].description == 'new constraint'
    assert param.guidelines[1].prose == 'new guideline'


def test_generate_group_id() -> None:
    """Test the generation of group ids."""
    cat_int = CatalogInterface()
    group = cat.Group(title='my test title')
    assert cat_int._generate_group_id(group) == 'trestle_group_0000'
    assert cat_int._generate_group_id(group) == 'trestle_group_0001'


def test_validate_catalog_missing_group_id(
    tmp_trestle_dir: pathlib.Path, tmp_path_factory: pytest.TempPathFactory, sample_catalog_rich_controls: cat.Catalog
) -> None:
    """Test validation of catalog with groups that dont have ids."""
    # kill one of the group id's
    sample_catalog_rich_controls.groups[0].id = None
    cat_name = 'my_cat'
    tmp_cat_path = tmp_path_factory.mktemp('temp_dir') / (cat_name + '.json')

    # write catalog with missing group id to tmp location
    sample_catalog_rich_controls.oscal_write(tmp_cat_path)
    import_cmd = ImportCmd()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(tmp_cat_path), output=cat_name, verbose=1, regenerate=False
    )

    # import the file with missing group id into the trestle workspace
    # this should validate the file and assign the missing id a new value in memory - then save the file
    rc = import_cmd._run(args)
    assert rc == 0

    # load the file without doing validation - to make sure the file itself has the group id assigned
    new_cat, new_cat_path = ModelUtils.load_model_for_class(tmp_trestle_dir, cat_name, cat.Catalog)
    assert new_cat.groups[0].id == 'trestle_group_0000'

    md_name = 'md_cat'
    md_path = tmp_trestle_dir / md_name
    md_path.mkdir(parents=True, exist_ok=True)
    cat_generate = CatalogGenerate()
    assert cat_generate.generate_markdown(
        tmp_trestle_dir, new_cat_path, md_path, {}, False
    ) == CmdReturnCodes.SUCCESS.value

    assem_cat_name = 'assem_cat'
    cat_assemble = CatalogAssemble()
    cat_assemble.assemble_catalog(tmp_trestle_dir, md_name, assem_cat_name, None, False, False, None)

    # load the file without doing validation - to make sure the file itself has the group id assigned
    _, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, assem_cat_name, cat.Catalog)
    assert new_cat.groups[0].id == 'trestle_group_0000'


def test_get_control_paths(sample_catalog_rich_controls: cat.Catalog) -> None:
    """Test get control paths."""
    cat_interface = CatalogInterface(sample_catalog_rich_controls)
    path = cat_interface.get_full_control_path('control_s')
    assert path == ['xy', 'sub']
    assert cat_interface.get_control_path('control_s') == ['xy', 'sub']
    path = cat_interface.get_full_control_path('control_d1')
    assert path == ['', 'control_d']
    assert cat_interface.get_control_path('control_d1') == ['']
    control = copy.deepcopy(cat_interface.get_control('control_d1'))
    control.id = 'cat_level'
    sample_catalog_rich_controls.controls = [control]
    cat_interface = CatalogInterface(sample_catalog_rich_controls)
    path = cat_interface.get_full_control_path('cat_level')
    assert path == ['']
    assert cat_interface.get_control_path('cat_level') == ['']


def test_catalog_force_overwrite(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test catalog generate with force-overwrite."""
    catalog = cat.Catalog.oscal_read(test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME)
    ModelUtils.save_top_level_model(catalog, tmp_trestle_dir, 'my_catalog', FileContentType.JSON)

    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog --force-overwrite'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)

    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)

    md_path = tmp_trestle_dir / 'md_catalog/ac/ac-2.md'
    assert md_path.exists()
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(md_path)

    assert header
    old_value = header[const.SET_PARAMS_TAG]['ac-2_prm_1'][const.VALUES]
    header[const.SET_PARAMS_TAG]['ac-2_prm_1'][const.VALUES] = 'New value'
    md_api.write_markdown_with_header(md_path, header, tree.content.raw_text)

    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)

    header, _ = md_api.processor.process_markdown(md_path)
    assert header[const.SET_PARAMS_TAG]['ac-2_prm_1'][const.VALUES] == 'New value'

    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog --force-overwrite'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)

    header, _ = md_api.processor.process_markdown(md_path)
    assert header[const.SET_PARAMS_TAG]['ac-2_prm_1'][const.VALUES] == old_value

    fc = test_utils.FileChecker(tmp_trestle_dir / 'md_catalog/')
    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog --force-overwrite'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)
    assert fc.files_unchanged()


def test_prune_written_controls(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test pruning of written controls."""
    catalog = cat.Catalog.oscal_read(test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME)
    ModelUtils.save_top_level_model(catalog, tmp_trestle_dir, 'my_catalog', FileContentType.JSON)

    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)

    md_path = tmp_trestle_dir / 'md_catalog'

    catalog_interface = CatalogInterface(catalog)
    control_ids = set(catalog_interface.get_control_ids())
    controls_to_delete = sorted(['ac-1', 'ac-2.9', 'at-2.1'])
    id_subset = control_ids - set(controls_to_delete)

    assert CatalogInterface._prune_controls(md_path, id_subset) == controls_to_delete


def test_catalog_assemble_subgroups(
    tmp_trestle_dir: pathlib.Path, sample_catalog_subgroups: cat.Catalog, monkeypatch: MonkeyPatch
) -> None:
    """Test assembly of catalog with group having no controls but does contain subgroup."""
    ModelUtils.save_top_level_model(sample_catalog_subgroups, tmp_trestle_dir, 'my_catalog', FileContentType.JSON)
    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog -vv'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)
    catalog_assemble = 'trestle author catalog-assemble -m md_catalog -o my_catalog -vv'
    test_utils.execute_command_and_assert(catalog_assemble, 0, monkeypatch)


def test_catalog_multiline_statement(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test catalog-assemble with multiline prose for control statement."""
    catalog = cat.Catalog.oscal_read(test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME)
    ModelUtils.save_top_level_model(catalog, tmp_trestle_dir, 'my_catalog', FileContentType.JSON)

    catalog_generate = 'trestle author catalog-generate -n my_catalog -o md_catalog'
    test_utils.execute_command_and_assert(catalog_generate, 0, monkeypatch)
    md_path = tmp_trestle_dir / 'md_catalog/ac/ac-2.md'
    assert md_path.exists()

    control_statement_prose = """The organization:

Test 1

Here goes a long paragraph. Test 2

Test 3
Test 4


"""

    file_utils.insert_text_in_file(md_path, '## Control Statement', control_statement_prose)

    catalog_assemble = 'trestle author catalog-assemble -o my_catalog -m md_catalog'
    test_utils.execute_command_and_assert(catalog_assemble, 0, monkeypatch)

    catalog, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'my_catalog', cat.Catalog)

    assert catalog
    assert catalog.groups[0].controls[1].parts[0].prose == control_statement_prose.strip('\n')
    assert catalog.groups[0].controls[1].parts[0].parts[
        0
    ].prose == 'Define and document the types of accounts allowed and specifically prohibited for use within the system;'  # noqa E501
