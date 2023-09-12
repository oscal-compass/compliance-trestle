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
"""Tests for the profile author module."""

import argparse
import pathlib
import shutil
import sys
from typing import Dict, Optional, Tuple

from _pytest.monkeypatch import MonkeyPatch

import pytest

from ruamel.yaml import YAML

from tests import test_utils

import trestle.common.const as const
import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.common as com
import trestle.oscal.profile as prof
from trestle.cli import Trestle
from trestle.common import file_utils
from trestle.common.err import TrestleError
from trestle.common.list_utils import comma_colon_sep_to_dict, comma_sep_to_list
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.commands.author.profile import ProfileAssemble, ProfileGenerate, ProfileInherit
from trestle.core.control_interface import ControlInterface
from trestle.core.markdown.docs_markdown_node import DocsMarkdownNode
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

# test dicts are of form {'name_exp': [(name, exp_str)...], 'text': prose}
# the text is appended to the end of the file
# then the assembled control is searched for exp_str in the prose of the named parts

markdown_name = 'my_md'
prof_name = 'my_prof'
md_name = 'my_md'
assembled_prof_name = 'my_assembled_prof'

my_guidance_text = """
## Control My Guidance

This is My Guidance.
"""

# name_exp maps the name of the section to the expected prose
# text is the text to be inserted in the markdown at the end of the file

# just add a new addition
my_guidance_dict = {'name_exp': [('ac-1_my_guidance', 'my_guidance', 'This is My Guidance.')], 'text': my_guidance_text}

multi_guidance_text = """
## Control A Guidance

This is A Guidance.

## Control B Guidance

This is B Guidance.
"""
# add two additions
multi_guidance_dict = {
    'name_exp': [
        ('ac-1_a_guidance', 'a_guidance', 'This is A Guidance.'),
        ('ac-1_b_guidance', 'b_guidance', 'This is B Guidance.')
    ],
    'text': multi_guidance_text
}

control_subparts_text = """
## Control A Guidance

Control A prose

### A Subpart

A subpart prose

#### A Subsubpart

A subsubpart prose

### B Subpart

B subpart prose

## Part a.

### a by_id subpart

a by_id subpart prose
"""

# part.id, part.name, part.prose
control_subparts_dict = {
    'name_exp': [
        ('ac-1_a_guidance', 'a_guidance', 'Control A prose'),
        ('ac-1_a_guidance.a_subpart', 'a_subpart', 'A subpart prose'),
        ('ac-1_a_guidance.a_subpart.a_subsubpart', 'a_subsubpart', 'A subsubpart prose'),
        ('ac-1_a_guidance.b_subpart', 'b_subpart', 'B subpart prose'),
        ('ac-1_smt.a', 'item', 'Develop, document, and disseminate'),  # this is the original NIST prose
        ('ac-1_smt.a.a_by_id_subpart', 'a_by_id_subpart', 'a by_id subpart prose')
    ],
    'text': control_subparts_text
}

all_sections_str = (
    'guidance:Guidance,implgdn:Implementation Guidance,expevid:Expected Evidence,my_guidance:My Guidance,'
    'a_guidance:A Guidance,b_guidance:B Guidance,NeededExtra:Needed Extra,a_subpart:A Subpart,'
    'a_subsubpart:A Subsubpart,b_subpart:B Subpart,a_by_id_subpart:a by_id subpart'
)

all_sections_dict = {
    'guidance': 'Guidance',
    'implgdn': 'Implementation Guidance',
    'expevid': 'Expected Evidence',
    'my_guidance': 'My Guidance',
    'a_guidance': 'A Guidance',
    'b_guidance': 'B Guidance',
    'NeededExtra': 'Needed Extra',
    'a_subpart': 'A Subpart',
    'a_subsubpart': 'A Subsubpart',
    'b_subpart': 'B Subpart',
    'a_by_id_subpart': 'a by_id subpart'
}


def edit_files(control_path: pathlib.Path, change_parameters: bool, guid_dict: Dict[str, str]) -> None:
    """Edit the files to show assemble worked."""
    assert control_path.exists()
    # need to insert guidance above needed extra since it is added last
    # if detailed logs text is not found just put it at end of file
    if not file_utils.insert_text_in_file(control_path, 'Detailed logs.', guid_dict['text']):
        assert file_utils.insert_text_in_file(control_path, None, guid_dict['text'])
    if control_path.stem == 'ac-1':
        assert test_utils.replace_line_in_file_after_tag(
            control_path, 'prop with ns', '    ns: https://my_new_namespace\n'
        )
        assert file_utils.insert_text_in_file(control_path, 'prop with no ns', '    ns: https://my_added_namespace\n')
    if change_parameters:
        # delete profile values for 4, then replace value for 3 with new value
        assert test_utils.substitute_text_in_file(control_path, 'officer', 'new value')
        assert test_utils.delete_line_in_file(control_path, 'weekly')
        assert test_utils.delete_line_in_file(control_path, 'label:')
        assert file_utils.insert_text_in_file(control_path, 'ac-1_prm_1:', '    label: label from edit\n')


def setup_profile_generate(trestle_root: pathlib.Path,
                           source_prof_name: str) -> Tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path]:
    """Set up files for profile generate."""
    nist_catalog_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    trestle_cat_dir = trestle_root / 'catalogs/nist_cat'
    trestle_cat_dir.mkdir(exist_ok=True, parents=True)
    shutil.copy(nist_catalog_path, trestle_cat_dir / 'catalog.json')
    profile_dir = trestle_root / f'profiles/{prof_name}'
    profile_dir.mkdir(parents=True, exist_ok=True)
    # simple test profile sets values for ac-1 params 1-6 but not param_7
    source_prof_path = test_utils.JSON_TEST_DATA_PATH / source_prof_name
    profile_path = profile_dir / 'profile.json'
    shutil.copy(source_prof_path, profile_path)
    markdown_path = trestle_root / md_name
    ac1_path = markdown_path / 'ac/ac-1.md'
    assembled_prof_dir = trestle_root / f'profiles/{assembled_prof_name}'
    return ac1_path, assembled_prof_dir, profile_path, markdown_path


@pytest.mark.parametrize('add_header', [True, False])
@pytest.mark.parametrize('guid_dict', [my_guidance_dict, multi_guidance_dict, control_subparts_dict])
@pytest.mark.parametrize('use_cli', [True, False])
@pytest.mark.parametrize('dir_exists', [True, False])
@pytest.mark.parametrize('set_parameters_flag', [True, False])
def test_profile_generate_assemble(
    add_header: bool,
    guid_dict: Dict,
    use_cli: bool,
    dir_exists: bool,
    set_parameters_flag: bool,
    tmp_trestle_dir: pathlib.Path,
    monkeypatch: MonkeyPatch
) -> None:
    """Test the profile markdown generator."""
    ac1_path, assembled_prof_dir, profile_path, markdown_path = setup_profile_generate(
        tmp_trestle_dir,
        'simple_test_profile.json'
    )
    yaml_header_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'

    ac_path = markdown_path / 'ac'

    # convert resolved profile catalog to markdown then assemble it after adding an item to a control
    # generate, edit, assemble
    if use_cli:
        test_args = f'trestle author profile-generate -n {prof_name} -o {md_name} -rs NeededExtra'.split(  # noqa E501
        )
        if add_header:
            test_args.extend(['-y', str(yaml_header_path)])
        test_args.extend(['-s', all_sections_str])
        monkeypatch.setattr(sys, 'argv', test_args)

        assert Trestle().run() == 0

        fc = test_utils.FileChecker(ac_path)

        assert Trestle().run() == 0

        assert fc.files_unchanged()

        # change officer to new value in md
        edit_files(ac1_path, True, guid_dict)

        # assemble based on set_parameters_flag
        test_args = f'trestle author profile-assemble -n {prof_name} -m {md_name} -o {assembled_prof_name}'.split()
        if set_parameters_flag:
            test_args.append('-sp')
        if dir_exists:
            assembled_prof_dir.mkdir()
        monkeypatch.setattr(sys, 'argv', test_args)
        assert Trestle().run() == 0
    else:
        profile_generate = ProfileGenerate()
        yaml_header = {}
        if add_header:
            yaml = YAML()
            yaml_header = yaml.load(yaml_header_path.open('r'))
        sections_dict = comma_colon_sep_to_dict(all_sections_str)

        profile_generate.generate_markdown(
            tmp_trestle_dir, profile_path, markdown_path, yaml_header, False, sections_dict, ['NeededExtra']
        )

        fc = test_utils.FileChecker(ac_path)

        profile_generate.generate_markdown(
            tmp_trestle_dir, profile_path, markdown_path, yaml_header, False, sections_dict, ['NeededExtra']
        )

        assert fc.files_unchanged()

        # change officer to new value in md
        edit_files(ac1_path, True, guid_dict)

        # assemble based on set_parameters_flag
        if dir_exists:
            assembled_prof_dir.mkdir()
        assert ProfileAssemble.assemble_profile(
            tmp_trestle_dir, prof_name, md_name, assembled_prof_name, set_parameters_flag, False, None, {}, [], None
        ) == 0

    assert test_utils.confirm_text_in_file(ac1_path, const.TRESTLE_GLOBAL_TAG, 'title: Trestle test profile')

    # check the assembled profile is as expected
    profile: prof.Profile
    profile, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, assembled_prof_name,
                                                 prof.Profile, FileContentType.JSON)
    assert ModelUtils.model_age(profile) < test_utils.NEW_MODEL_AGE_SECONDS
    # get the set_params from the assembled profile
    set_params = profile.modify.set_parameters
    if set_parameters_flag:
        assert set_params[2].values[0] == 'new value'
        assert set_params[1].props[0].ns == const.TRESTLE_GENERIC_NS
        assert len(set_params) == 18
    else:
        # the original profile did not have ns set for this display name
        # confirm the namespace is not defined unless set_parameters_flag is True
        # i.e. the setting of ns for display-name is not automatic unless set-parameters is true
        assert set_params[2].values[0] == 'officer'
        assert set_params[1].props[0].ns is None
        assert len(set_params) == 15
    assert set_params[0].param_id == 'ac-1_prm_1'
    assert set_params[0].values[0] == 'all personnel'
    assert set_params[0].props[0].name == const.DISPLAY_NAME
    assert set_params[0].props[0].value.startswith('Pretty')
    assert set_params[0].props[0].ns == const.TRESTLE_GENERIC_NS
    assert set_params[1].param_id == 'ac-1_prm_2'
    assert set_params[1].values[0] == 'Organization-level'
    assert set_params[1].values[1] == 'System-level'
    assert set_params[1].props[0].name == const.DISPLAY_NAME
    assert set_params[2].param_id == 'ac-1_prm_3'
    add = profile.modify.alters[0].adds[0]
    assert add.props[0].ns == 'https://my_new_namespace'
    assert add.props[1].ns == 'https://my_added_namespace'

    # now create the resolved profile catalog from the assembled json profile and confirm the addition is there

    assem_prof_path = assembled_prof_dir / 'profile.json'
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, assem_prof_path)
    catalog_interface = CatalogInterface(catalog)
    # confirm correct ids, names, and prose for the parts
    ac_1 = catalog_interface.get_control('ac-1')
    for part_id, name, exp_str in guid_dict['name_exp']:
        part = ControlInterface.get_part_by_id(ac_1, part_id)
        assert part.name == name
        assert part.prose.find(exp_str) >= 0

    # regen and make sure markdown is unchanged

    # ac_2.1 has changes to the comment section due to parts not being present, then being added - so remove it
    ac_21_path = tmp_trestle_dir / 'my_md/ac/ac-2.1.md'
    ac_21_path.unlink()

    fc = test_utils.FileChecker(ac_path)

    # generate md from assembled profile.  md should not change value of new value back to officer ever
    profile_generate = ProfileGenerate()
    profile_generate.generate_markdown(
        tmp_trestle_dir, assem_prof_path, markdown_path, {}, False, all_sections_dict, ['NeededExtra']
    )

    ac_21_path.unlink()
    # order of sections changes
    assert fc.files_unchanged()


@pytest.mark.parametrize(
    'required_sections, success', [(None, True), ('a_guidance,b_guidance', True), ('a_guidance,c_guidance', False)]
)
@pytest.mark.parametrize('ohv', [True, False])
def test_profile_ohv(required_sections: Optional[str], success: bool, ohv: bool, tmp_trestle_dir: pathlib.Path) -> None:
    """Test profile generate assemble with overwrite-header-values."""
    ac1_path, assembled_prof_dir, profile_path, markdown_path = setup_profile_generate(
        tmp_trestle_dir,
        'simple_test_profile.json'
    )
    yaml_header_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    new_version = '1.2.3'

    required_sections_list = comma_sep_to_list(required_sections)

    # convert resolved profile catalog to markdown then assemble it after adding an item to a control
    # if set_parameters_flag is true, the yaml header will contain all the parameters
    profile_generate = ProfileGenerate()
    yaml = YAML()
    yaml_header = yaml.load(yaml_header_path.open('r'))
    profile_generate.generate_markdown(tmp_trestle_dir, profile_path, markdown_path, yaml_header, ohv, None, None)

    edit_files(ac1_path, True, multi_guidance_dict)
    markdown_path = tmp_trestle_dir / md_name
    # change guidance in the other two controls but don't change header
    ac2_path = markdown_path / 'ac/ac-2.md'
    ac21_path = markdown_path / 'ac/ac-2.1.md'
    edit_files(ac2_path, False, multi_guidance_dict)
    edit_files(ac21_path, False, multi_guidance_dict)

    if success:
        # always doing set_params True
        assert ProfileAssemble.assemble_profile(
            tmp_trestle_dir,
            prof_name,
            md_name,
            assembled_prof_name,
            True,
            False,
            new_version, {},
            required_sections_list,
            None
        ) == 0

        # check the assembled profile is as expected
        profile: prof.Profile
        profile, _ = ModelUtils.load_model_for_class(
            tmp_trestle_dir, assembled_prof_name,
            prof.Profile,
            FileContentType.JSON
        )
        set_params = profile.modify.set_parameters

        assert len(set_params) == 18
        assert set_params[0].values[0] == 'all personnel'
        # the label is present in the header so it ends up in the set_parameter
        assert set_params[0].label == 'label from edit'
        assert set_params[1].param_id == 'ac-1_prm_2'
        assert set_params[1].values[0] == 'Organization-level'
        assert set_params[1].values[1] == 'System-level'
        assert set_params[2].values[0] == 'new value'
        assert profile.metadata.version == new_version
        if ohv:
            assert set_params[4].values[0] == 'no meetings from cli yaml'
            assert set_params[4].label == 'meetings cancelled from cli yaml'
        else:
            assert set_params[4].values[0] == 'all meetings'
            assert set_params[4].label is None

        catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, assembled_prof_dir / 'profile.json')
        catalog_interface = CatalogInterface(catalog)
        # confirm correct ids, names, and prose for the parts
        ac_1 = catalog_interface.get_control('ac-1')
        for part_id, name, exp_str in multi_guidance_dict['name_exp']:
            part = ControlInterface.get_part_by_id(ac_1, part_id)
            assert part.name == name
            assert part.prose.find(exp_str) >= 0

    else:
        with pytest.raises(TrestleError):
            ProfileAssemble.assemble_profile(
                tmp_trestle_dir,
                prof_name,
                md_name,
                assembled_prof_name,
                True,
                False,
                new_version, {},
                required_sections_list,
                None
            )


def test_profile_failures(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test failure modes of profile generate and assemble."""
    # no trestle root specified direct command
    test_args = argparse.Namespace(name='my_prof', output='new_prof', verbose=0, set_parameters=False, sections=None)
    profile_generate = ProfileGenerate()
    assert profile_generate._run(test_args) == 1

    # no trestle root specified
    profile_assemble = ProfileAssemble()
    assert profile_assemble._run(test_args) == 1

    # bad yaml
    bad_yaml_path = str(test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml')
    trestle_root = tmp_trestle_dir
    test_args = argparse.Namespace(
        trestle_root=trestle_root,
        name='my_prof',
        output='new_prof',
        yaml_header=bad_yaml_path,
        verbose=0,
        set_parameters=False,
        sections=None,
        force_overwrite=False
    )
    profile_generate = ProfileGenerate()
    assert profile_generate._run(test_args) == 1

    # profile not available for load
    test_args = 'trestle author profile-generate -n my_prof -o my_md -v'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1

    # setup for generate and assemble
    profile_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'my_prof', prof.Profile, FileContentType.JSON
    )
    profile_path.parent.mkdir()
    shutil.copyfile(test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json', profile_path)
    cat_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'nist_cat', cat.Catalog, FileContentType.JSON
    )
    cat_path.parent.mkdir()
    shutil.copyfile(test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME, cat_path)

    # generate markdown with required section but don't give it any prose
    test_args = argparse.Namespace(
        trestle_root=trestle_root,
        name='my_prof',
        output='md_prof',
        verbose=0,
        set_parameters_flag=False,
        overwrite_header_values=False,
        yaml_header=None,
        sections='NeededExtra:Needed Extra,implgdn:Implementation Guidance,expevid:Expected Evidence',
        required_sections=None,
        force_overwrite=False
    )
    profile_generate = ProfileGenerate()
    assert profile_generate._run(test_args) == 0

    # set arguments for assemble
    test_args = argparse.Namespace(
        trestle_root=trestle_root,
        name=None,
        markdown='md_prof',
        output='my_prof',
        verbose=0,
        set_parameters=False,
        yaml_header=None,
        required_sections='NeededExtra',
        regenerate=False,
        version=None,
        allowed_sections=None,
        sections=None,
        force_overwrite=False
    )
    # fail since required section not present
    profile_assemble = ProfileAssemble()
    assert profile_assemble._run(test_args) == 1

    # succeed if not specifying required section
    test_args.required_sections = None
    assert profile_assemble._run(test_args) == 0

    # fail if allowed sections doesn't include all needed
    test_args.allowed_sections = 'NeededExtra,DummySection'
    assert profile_assemble._run(test_args) == 1

    # succed if allowed sections has all
    test_args.allowed_sections = 'expevid,implgdn,NeededExtra'
    assert profile_assemble._run(test_args) == 0

    # disallowed output name
    test_args = 'trestle author profile-generate -n my_prof -o profiles -v'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1


def test_profile_overwrite(tmp_trestle_dir: pathlib.Path) -> None:
    """Test blocking overwrite if no change to assembled profile relative to one it would overwrite."""
    _, _, profile_path, markdown_path = setup_profile_generate(tmp_trestle_dir, 'simple_test_profile.json')

    # generate the markdown and assemble
    profile_generate = ProfileGenerate()
    profile_generate.generate_markdown(tmp_trestle_dir, profile_path, markdown_path, {}, False, all_sections_dict, [])

    assert ProfileAssemble.assemble_profile(
        tmp_trestle_dir, prof_name, md_name, prof_name, True, False, None, {}, [], None
    ) == 0

    # note the file timestamp, then regenerate and assemble again
    orig_time = profile_path.stat().st_mtime

    profile_generate.generate_markdown(tmp_trestle_dir, profile_path, markdown_path, {}, False, all_sections_dict, [])

    assert ProfileAssemble.assemble_profile(
        tmp_trestle_dir, prof_name, md_name, prof_name, True, False, None, {}, [], None
    ) == 0

    # the timestamp should be the same, indicating the file was not written
    new_time = profile_path.stat().st_mtime

    assert new_time == orig_time

    # now generate again but with different section title, causing change in generated profile markdown
    new_sections = {'implgdn': 'Different Title'}
    profile_generate.generate_markdown(tmp_trestle_dir, profile_path, markdown_path, {}, False, new_sections, [])

    assert ProfileAssemble.assemble_profile(
        tmp_trestle_dir, prof_name, md_name, prof_name, True, False, None, {}, [], None
    ) == 0

    # the timestamp should now be different
    new_time = profile_path.stat().st_mtime

    assert new_time != orig_time


def test_profile_alter_adds(simplified_nist_profile: prof.Profile) -> None:
    """Test profile alter adds involving Nones."""
    adds = [prof.Add(props=[com.Property(name='prop_1', value='prop_1_val')])]
    alters = [prof.Alter(control_id='ac-1', adds=adds)]
    # first case modify is None
    assert ProfileAssemble._replace_alter_adds(simplified_nist_profile, alters)
    simplified_nist_profile.modify.alters = None
    # second case modify is not None but alters is None
    assert ProfileAssemble._replace_alter_adds(simplified_nist_profile, alters)


def _check_parts(part: com.Part, prose_1: str) -> None:
    assert part.parts[0].id == 'ac-1_smt.b.new_guidance'
    assert part.parts[0].name == 'new_guidance'
    assert part.parts[0].prose == 'This is my added prose for a part in the statement'
    assert part.parts[1].id == 'ac-1_smt.b.new_evidence'
    assert part.parts[1].prose == prose_1


def _check_multi_section(part: com.Part) -> None:
    assert part.id == 'ac-1_multi_section'
    assert part.parts[0].id == 'ac-1_multi_section.sub_a'
    assert part.parts[0].parts[0].id == 'ac-1_multi_section.sub_a.sub_sub_a'


def test_profile_alter_props(tmp_trestle_dir: pathlib.Path) -> None:
    """Test profile alter adds involving props."""
    ac1_path, _, profile_path, markdown_path = setup_profile_generate(tmp_trestle_dir, 'profile_with_alter_props.json')
    sections = {'implgdn': 'Implementation Guidance', 'expevid': 'Expected Evidence', 'guidance': 'Guidance'}
    # generate markdown twice and confirm no changes
    profile_generate = ProfileGenerate()
    assert profile_generate.generate_markdown(
        tmp_trestle_dir, profile_path, markdown_path, {}, False, sections, []
    ) == 0

    fc = test_utils.FileChecker(ac1_path.parent)

    assert profile_generate.generate_markdown(
        tmp_trestle_dir, profile_path, markdown_path, {}, False, sections, []
    ) == 0

    assert fc.files_unchanged()

    text = """  - name: ac-1_new
    value: ac-1 new value
    remarks: ac-1 new stuff
  - name: ac-1_new_part
    value: ac-1 new part value
    smt-part: c.
  - name: prop_in_expevid
    value: value in expevid
    smt-part: ac-1_expevid
  - name: cannot_add_to_resolved_cat_because_no_part_id
    value: doesnt work
    smt-part: foo_bar
"""

    # insert four new props, one is by id attached to part c., another is to ac-1_expevid
    # a final one is attached to cannot_add and will give warning that it isn't found on assemble
    assert file_utils.insert_text_in_file(ac1_path, const.TRESTLE_ADD_PROPS_TAG, text)

    assert ProfileAssemble.assemble_profile(
        tmp_trestle_dir, prof_name, md_name, assembled_prof_name, True, False, None, sections, [], None
    ) == 0

    # check the assembled profile is as expected
    profile: prof.Profile
    profile, prof_path = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        assembled_prof_name,
        prof.Profile, FileContentType.JSON
    )
    adds = profile.modify.alters[0].adds
    assert len(adds) == 5
    assert adds[0].position.value == 'ending'
    assert adds[0].by_id is None
    assert len(adds[0].parts) == 2
    assert len(adds[0].props) == 2
    assert adds[1].by_id == 'ac-1_expevid'
    assert adds[1].props[0].name == 'prop_in_expevid'
    assert adds[1].props[0].value == 'value in expevid'
    assert adds[2].by_id == 'ac-1_smt.a'
    assert adds[3].by_id == 'ac-1_smt.c'
    assert adds[4].by_id == 'foo_bar'

    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    ac1 = catalog.groups[0].controls[0]
    assert ac1.parts[0].parts[0].id == 'ac-1_smt.a'
    assert ac1.parts[0].parts[0].props[1].name == 'ac1_a_foo'
    assert ac1.parts[0].parts[0].props[1].value == 'ac1 a bar'
    assert ac1.parts[0].parts[2].id == 'ac-1_smt.c'
    assert ac1.parts[0].parts[2].props[1].name == 'ac-1_new_part'
    assert ac1.parts[0].parts[2].props[1].value == 'ac-1 new part value'
    assert ac1.parts[3].props[0].name == 'prop_in_expevid'

    prose = """
## Control Multi Section

### Sub A

Text in Sub A

#### Sub Sub A

Text in Sub Sub A

### Sub B

Text in Sub B

## Part b.

### New Guidance

This is my added prose for a part in the statement

### New Evidence

More evidence

"""
    sections['sub_a'] = 'Sub A'
    sections['sub_sub_a'] = 'Sub Sub A'
    sections['sub_b'] = 'Sub B'
    sections['newguidance'] = 'New Guidance'
    sections['newevidence'] = 'New Evidence'

    assert file_utils.insert_text_in_file(ac1_path, None, prose)
    assert ProfileAssemble.assemble_profile(
        tmp_trestle_dir, prof_name, md_name, assembled_prof_name, True, False, None, sections, [], None
    ) == 0

    # check the assembled profile is as expected
    profile, prof_path = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        assembled_prof_name,
        prof.Profile, FileContentType.JSON
    )
    adds = profile.modify.alters[0].adds
    assert len(adds) == 6
    assert adds[0].position.value == 'ending'
    assert adds[1].by_id == 'ac-1_expevid'
    assert adds[2].by_id == 'ac-1_smt.a'
    assert adds[3].by_id == 'ac-1_smt.b'
    assert adds[4].by_id == 'ac-1_smt.c'
    assert adds[0].parts[2].id == 'ac-1_multi_section'
    assert adds[0].parts[2].parts[0].id == 'ac-1_multi_section.sub_a'
    assert adds[0].parts[2].parts[0].parts[0].id == 'ac-1_multi_section.sub_a.sub_sub_a'

    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    _check_parts(catalog.groups[0].controls[0].parts[0].parts[1], 'More evidence')

    # Confirm that changed prose in the markdown is retained on new profile-generate
    assert test_utils.substitute_text_in_file(ac1_path, 'More evidence', 'Updated evidence')
    assert profile_generate.generate_markdown(tmp_trestle_dir, prof_path, markdown_path, {}, False, sections, []) == 0
    assert ProfileAssemble.assemble_profile(
        tmp_trestle_dir, prof_name, md_name, assembled_prof_name, True, False, None, sections, [], None
    ) == 0
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    _check_parts(catalog.groups[0].controls[0].parts[0].parts[1], 'Updated evidence')
    _check_multi_section(part=catalog.groups[0].controls[0].parts[4])

    fresh_md_name = 'fresh_markdown'
    fresh_md_path = tmp_trestle_dir / fresh_md_name
    fresh_assem_prof_name = 'fresh_assem'
    fresh_assem_prof_path = tmp_trestle_dir / 'profiles' / fresh_assem_prof_name / 'profile.json'
    assert profile_generate.generate_markdown(tmp_trestle_dir, prof_path, fresh_md_path, {}, False, sections, []) == 0
    assert ProfileAssemble.assemble_profile(
        tmp_trestle_dir, prof_name, fresh_md_name, fresh_assem_prof_name, True, False, None, sections, [], None
    ) == 0
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, fresh_assem_prof_path)
    _check_parts(catalog.groups[0].controls[0].parts[0].parts[1], 'Updated evidence')
    _check_multi_section(part=catalog.groups[0].controls[0].parts[4])


def test_adding_removing_sections(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the profile generate and assemble in cycles, with incremental changes."""

    def generate_assemble(md_path: pathlib.Path) -> DocsMarkdownNode:
        prof_assemble = f'trestle author profile-assemble -n main_profile -m {md_name} -o main_profile'
        test_utils.execute_command_and_assert(prof_assemble, 0, monkeypatch)

        # generate markdown again, ensure section is there
        prof_generate = f'trestle author profile-generate -n main_profile -o {md_name}'
        test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

        assert md_path.exists()
        _, tree = md_api.processor.process_markdown(md_path)

        return tree

    test_utils.setup_for_multi_profile(tmp_trestle_dir, True, True)

    prof_generate = f'trestle author profile-generate -n main_profile -o {md_name}'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    ac1_path = tmp_trestle_dir / md_name / 'ac/ac-1.md'
    ac2_path = tmp_trestle_dir / md_name / 'ac/ac-2.md'

    md_api = MarkdownAPI()

    assert ac1_path.exists()
    assert file_utils.insert_text_in_file(ac1_path, None, '## Control this_should_appear_in_parts \n Test text.')
    _, tree = md_api.processor.process_markdown(ac1_path)

    assert tree.get_node_for_key('## Control this_should_appear_in_parts', strict_matching=True)

    # Scenario 1: Profile has no alters at all, ensure new sections is added
    tree = generate_assemble(ac1_path)
    assert tree.get_node_for_key('## Control this_should_appear_in_parts', strict_matching=True)

    # Scenario 2: Profiles has one alter for ac-1, now add new section to ac-2, ensure new sectio is added
    assert ac2_path.exists()
    assert file_utils.insert_text_in_file(ac2_path, None, '## Control this_should_appear_in_parts2 \n Test text.')
    _, tree = md_api.processor.process_markdown(ac2_path)
    assert tree.get_node_for_key('## Control this_should_appear_in_parts2', strict_matching=True)

    tree = generate_assemble(ac2_path)
    assert tree.get_node_for_key('## Control this_should_appear_in_parts2', strict_matching=True)

    # Scenario 3: Remove added section from the ac-1, ensure the alters are deleted
    assert ac1_path.exists()
    assert test_utils.delete_line_in_file(ac1_path, '## Control this_should_appear_in_parts', 2)
    _, tree = md_api.processor.process_markdown(ac1_path)
    assert not tree.get_node_for_key('## Control this_should_appear_in_parts')

    tree = generate_assemble(ac1_path)
    assert not tree.get_node_for_key('## Control this_should_appear_in_parts')


@pytest.mark.parametrize('bracket_format', [True, False])
@pytest.mark.parametrize('show_values', [True, False])
def test_profile_resolve(
    tmp_trestle_dir: pathlib.Path, show_values: bool, bracket_format: bool, monkeypatch: MonkeyPatch
) -> None:
    """Test profile resolve to create resolved profile catalog."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, False)
    cat_name = 'resolved_catalog'
    command_profile_resolve = f'trestle author profile-resolve -n main_profile -o {cat_name}'
    if show_values:
        command_profile_resolve += ' -sv'
    if bracket_format:
        command_profile_resolve += ' -bf [(.])'
    test_utils.execute_command_and_assert(command_profile_resolve, 0, monkeypatch)
    res_cat, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, cat_name, cat.Catalog, FileContentType.JSON)
    ac_1 = res_cat.groups[0].controls[0]
    expected_value = '{{ insert: param, ac-1_prm_3 }}'
    if show_values:
        expected_value = 'officer'
        if bracket_format:
            expected_value = f'[({expected_value}])'
    expected_prose = f'Designate an {expected_value} to manage the development, documentation, and dissemination of the access control policy and procedures; and'  # noqa E501
    assert ac_1.parts[0].parts[1].prose == expected_prose


@pytest.mark.parametrize('show_values', [True, False])
def test_profile_resolve_fail(tmp_trestle_dir: pathlib.Path, show_values: bool, monkeypatch: MonkeyPatch) -> None:
    """Test profile resolve to create resolved profile catalog."""
    # confirm failure for non-existent profile
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, False)
    cat_name = 'resolved_catalog'
    command_profile_resolve = f'trestle author profile-resolve -n foo -o {cat_name}'
    if show_values:
        command_profile_resolve += ' -sv'
    test_utils.execute_command_and_assert(command_profile_resolve, 1, monkeypatch)

    # confirm failure for existing but corrupt profile
    bad_prof_dir = tmp_trestle_dir / 'profiles/bad_prof'
    bad_prof_dir.mkdir(exist_ok=True, parents=True)
    src_path = test_utils.JSON_TEST_DATA_PATH / 'bad_simple.json'
    shutil.copy2(str(src_path), str(bad_prof_dir / 'profile.json'))
    command_profile_resolve = f'trestle author profile-resolve -n bad_prof -o {cat_name}'
    if show_values:
        command_profile_resolve += ' -sv'
    test_utils.execute_command_and_assert(command_profile_resolve, 1, monkeypatch)


def test_profile_generate_updates_statement(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test proper update of statement contents on regenerate."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    prof_generate = f'trestle author profile-generate -n main_profile -o {md_name} -ohv'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    # confirm that disallowed edits to the control statement are overwritten on next generate
    bad_text = '  - \[3.\] Count kangaroos.'
    ac1_path = tmp_trestle_dir / md_name / 'ac/ac-1.md'
    tag = 'param, ac-1_prm_7'
    file_utils.insert_text_in_file(ac1_path, tag, bad_text)
    assert test_utils.confirm_text_in_file(ac1_path, tag, bad_text)
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)
    assert not test_utils.confirm_text_in_file(ac1_path, tag, bad_text)

    # put bad text back in disallowed part of control statement
    file_utils.insert_text_in_file(ac1_path, tag, bad_text)

    # add a new allowed part to the profile
    # and change a parameter value on a control
    main_prof, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'main_profile', prof.Profile, FileContentType.JSON)
    main_prof.modify.alters[0].adds[0].parts.append(com.Part(id='ac-1_wombat', name='wombat', prose='Assess wombats.'))
    main_prof.modify.set_parameters[2].values = ['echidna']
    ModelUtils.save_top_level_model(main_prof, tmp_trestle_dir, 'main_profile', FileContentType.JSON)

    # now add a part to the catalog
    nist_cat, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'nist_cat', cat.Catalog, FileContentType.JSON)
    nist_cat.groups[0].controls[0].parts.append(com.Part(id='ac-1_koala', name='koala', prose='Enjoy koalas'))
    ModelUtils.save_top_level_model(nist_cat, tmp_trestle_dir, 'nist_cat', FileContentType.JSON)

    # generate the markdown from the profile
    prof_generate = f'trestle author profile-generate -n main_profile -o {md_name} -ohv'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    # assemble into new profile
    prof_assem = f'trestle author profile-assemble -n main_profile -o assem_prof -m {md_name} -sp'
    test_utils.execute_command_and_assert(prof_assem, 0, monkeypatch)

    prof_resolve = 'trestle author profile-resolve -n main_profile -o resolved_cat -sv'
    test_utils.execute_command_and_assert(prof_resolve, 0, monkeypatch)

    # echidna and wombat came from changes to main profile
    # koala came from edit to the nist catalog
    resolved_cat, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        'resolved_cat',
        cat.Catalog,
        FileContentType.JSON
    )
    ac1 = resolved_cat.groups[0].controls[0]
    assert ac1.params[2].values[0] == 'echidna'
    assert ac1.parts[3].id == 'ac-1_wombat'
    assert ac1.parts[5].id == 'ac-1_koala'


def test_profile_generate_inherited_props(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test generation of inherited props in header."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    prof_generate = f'trestle author profile-generate -n test_profile_f -o {md_name} -ohv'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    md_path = tmp_trestle_dir / 'my_md/ac/ac-3.3.md'
    assert md_path.exists()
    md_api = MarkdownAPI()
    header, _ = md_api.processor.process_markdown(md_path)
    inherited_props = header[const.TRESTLE_INHERITED_PROPS_TAG]
    assert len(inherited_props) == 2
    assert inherited_props[0] == {'name': 'add_prof_b_prop', 'value': 'add prof b prop value'}
    assert inherited_props[1] == {
        'name': 'add_prof_b_prop_by_id', 'value': 'add prof b prop by id value', 'part_name': 'ac-3.3_prm_2'
    }
    set_params = header[const.SET_PARAMS_TAG]
    assert set_params['ac-3.3_prm_1'][const.PROFILE_VALUES] == ['from prof f set-param']
    assert set_params['ac-3.3_prm_1'][const.VALUES] == ['key power users']

    ac5_path = tmp_trestle_dir / 'my_md/ac/ac-5.md'
    assert test_utils.confirm_text_in_file(ac5_path, 'value: one', 'smt-part: a.')
    assert test_utils.confirm_text_in_file(ac5_path, 'test_five', 'smt-part: ac-5_gdn')
    assert test_utils.confirm_text_in_file(ac5_path, 'value: two', 'ns: https://prof_f_ns')


def test_profile_force_overwrite(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test profile generate with force-overwrite."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)

    prof_generate = f'trestle author profile-generate -n test_profile_f -o {md_name} --force-overwrite'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    prof_generate = f'trestle author profile-generate -n test_profile_f -o {md_name}'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    md_path = tmp_trestle_dir / 'my_md/ac/ac-5.md'
    assert md_path.exists()
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(md_path)

    assert header
    header[const.SET_PARAMS_TAG]['ac-5_prm_1'][const.VALUES] = []
    old_value = header[const.SET_PARAMS_TAG]['ac-5_prm_1'][const.VALUES]
    header[const.SET_PARAMS_TAG]['ac-5_prm_1'][const.VALUES] = 'New value'

    md_api.write_markdown_with_header(md_path, header, tree.content.raw_text)

    prof_generate = f'trestle author profile-generate -n test_profile_f -o {md_name}'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    header, _ = md_api.processor.process_markdown(md_path)
    assert header[const.SET_PARAMS_TAG]['ac-5_prm_1'][const.VALUES] == 'New value'

    prof_generate = f'trestle author profile-generate -n test_profile_f -o {md_name} --force-overwrite'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)

    header, _ = md_api.processor.process_markdown(md_path)
    header[const.SET_PARAMS_TAG]['ac-5_prm_1'][const.VALUES] = []
    assert header[const.SET_PARAMS_TAG]['ac-5_prm_1'][const.VALUES] == old_value

    # test that file is unchanged
    fc = test_utils.FileChecker(tmp_trestle_dir / 'my_md/')
    prof_generate = f'trestle author profile-generate -n test_profile_f -o {md_name} --force-overwrite'
    test_utils.execute_command_and_assert(prof_generate, 0, monkeypatch)
    assert fc.files_unchanged()


def test_profile_resolve_assignment(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test profile resolve to create resolved profile catalog in assignment mode."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, False)
    cat_name = 'resolved_catalog'
    command_profile_resolve = f'trestle author profile-resolve -n main_profile -o {cat_name} -bf (.) -sv -vap "IBM Assignment:" -vnap "Assignment:"'  # noqa E501
    test_utils.execute_command_and_assert(command_profile_resolve, 0, monkeypatch)
    res_cat, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, cat_name, cat.Catalog, FileContentType.JSON)
    ac_1 = res_cat.groups[0].controls[0]
    expected_value = '(IBM Assignment: officer)'
    expected_prose = f'Designate an {expected_value} to manage the development, documentation, and dissemination of the access control policy and procedures; and'  # noqa E501
    assert ac_1.parts[0].parts[1].prose == expected_prose
    ac_21 = res_cat.groups[0].controls[-1].controls[0]
    assert ac_21.parts[
        0
    ].prose == 'Support the management of system accounts using (Assignment: organization-defined automated mechanisms).'  # noqa E501


def test_profile_resolve_label_mode(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test profile resolve to create resolved profile catalog in label mode."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, False)
    cat_name = 'resolved_catalog'
    command_profile_resolve = f'trestle author profile-resolve -n main_profile -o {cat_name} -bf (.) -sl -lp Label:'  # noqa E501
    test_utils.execute_command_and_assert(command_profile_resolve, 0, monkeypatch)
    res_cat, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, cat_name, cat.Catalog, FileContentType.JSON)
    ac_1 = res_cat.groups[0].controls[0]
    expected_value = '(Label: organization-defined official)'
    expected_prose = f'Designate an {expected_value} to manage the development, documentation, and dissemination of the access control policy and procedures; and'  # noqa E501
    assert ac_1.parts[0].parts[1].prose == expected_prose
    ac_21 = res_cat.groups[0].controls[-1].controls[0]
    assert ac_21.parts[
        0
    ].prose == 'Support the management of system accounts using (Label: organization-defined automated mechanisms).'  # noqa E501


def test_profile_resolve_assignment_simple(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test profile resolve with simple profile."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, True, False)
    cat_name = 'resolved_catalog'
    command_profile_resolve = f'trestle author profile-resolve -n main_profile -o {cat_name} -bf (.) -sv -vap "IBM Assignment:" -vnap "Assignment:"'  # noqa E501
    test_utils.execute_command_and_assert(command_profile_resolve, 0, monkeypatch)
    res_cat, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, cat_name, cat.Catalog, FileContentType.JSON)
    ac_1 = res_cat.groups[0].controls[0]
    expected_value = '(Assignment: organization-defined official)'
    expected_prose = f'Designate an {expected_value} to manage the development, documentation, and dissemination of the access control policy and procedures; and'  # noqa E501
    assert ac_1.parts[0].parts[1].prose == expected_prose
    ac_21 = res_cat.groups[0].controls[1].controls[0]
    assert ac_21.parts[
        0
    ].prose == 'Support the management of system accounts using (Assignment: organization-defined automated mechanisms).'  # noqa E501


def test_profile_resolve_failures(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test profile resolve failure due to disallowed argument combinations."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, True, False)
    core_command = 'trestle author profile-resolve -n main_profile -o resolved_catalog -bf (.) '
    test_utils.execute_command_and_assert(core_command + '-sv -sl', 1, monkeypatch)
    test_utils.execute_command_and_assert(core_command + '-sv -lp prefix', 1, monkeypatch)
    test_utils.execute_command_and_assert(core_command + '-lp prefix', 1, monkeypatch)
    test_utils.execute_command_and_assert(core_command + '-vap prefix', 1, monkeypatch)
    test_utils.execute_command_and_assert(core_command + '-sl -vap prefix', 1, monkeypatch)


def test_profile_inherit(tmp_trestle_dir: pathlib.Path):
    """Test profile initialization and seeding for various use cases."""
    output_profile = 'my_profile'
    excluded = prof.WithId(__root__='ac-1')

    # Test with a profile and ssp that has all controls with exported information
    args = test_utils.setup_for_inherit(tmp_trestle_dir, 'simple_test_profile', output_profile, 'leveraged_ssp')
    prof_inherit = ProfileInherit()
    assert prof_inherit._run(args) == 0

    result_prof, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        output_profile,
        prof.Profile,
        FileContentType.JSON
    )

    assert result_prof.imports[0].href == 'trestle://profiles/simple_test_profile/profile.json'
    assert len(result_prof.imports[0].include_controls[0].with_ids) == 2
    assert len(result_prof.imports[0].exclude_controls[0].with_ids) == 1
    assert result_prof.imports[0].exclude_controls[0].with_ids[0] == excluded

    # Test with a profile that has more controls than the ssp
    args = test_utils.setup_for_inherit(tmp_trestle_dir, 'simple_test_profile_more', output_profile, 'leveraged_ssp')
    prof_inherit = ProfileInherit()
    assert prof_inherit._run(args) == 0

    result_prof, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        output_profile,
        prof.Profile,
        FileContentType.JSON
    )

    assert result_prof.imports[0].href == 'trestle://profiles/simple_test_profile_more/profile.json'
    assert len(result_prof.imports[0].include_controls[0].with_ids) == 3
    assert len(result_prof.imports[0].exclude_controls[0].with_ids) == 1
    assert result_prof.imports[0].exclude_controls[0].with_ids[0] == excluded

    # Test with a profile that has less controls than the ssp
    args = test_utils.setup_for_inherit(tmp_trestle_dir, 'simple_test_profile_less', output_profile, 'leveraged_ssp')
    prof_inherit = ProfileInherit()
    assert prof_inherit._run(args) == 0

    result_prof, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        output_profile,
        prof.Profile,
        FileContentType.JSON
    )

    assert result_prof.imports[0].href == 'trestle://profiles/simple_test_profile_less/profile.json'
    assert len(result_prof.imports[0].include_controls[0].with_ids) == 1
    assert len(result_prof.imports[0].exclude_controls[0].with_ids) == 1
    assert result_prof.imports[0].exclude_controls[0].with_ids[0] == excluded

    # Test with a profile that has all controls filtered out
    args = test_utils.setup_for_inherit(tmp_trestle_dir, 'simple_test_profile_single', output_profile, 'leveraged_ssp')
    prof_inherit = ProfileInherit()
    assert prof_inherit._run(args) == 0

    result_prof, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        output_profile,
        prof.Profile,
        FileContentType.JSON
    )

    assert result_prof.imports[0].href == 'trestle://profiles/simple_test_profile_single/profile.json'
    assert len(result_prof.imports[0].include_controls[0].with_ids) == 0
    assert len(result_prof.imports[0].exclude_controls[0].with_ids) == 1
    assert result_prof.imports[0].exclude_controls[0].with_ids[0] == excluded

    # Test with version set
    args = test_utils.setup_for_inherit(tmp_trestle_dir, 'simple_test_profile_less', output_profile, 'leveraged_ssp')
    prof_inherit = ProfileInherit()
    args.version = '1.0.0'
    assert prof_inherit._run(args) == 0

    result_prof, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        output_profile,
        prof.Profile,
        FileContentType.JSON
    )

    assert result_prof.metadata.version == '1.0.0'

    # Force a failure with non-existent profile
    args.profile = 'bad_prof'
    prof_inherit = ProfileInherit()
    assert prof_inherit._run(args) == 1

    # Force a failure with a cyclic dependency
    args.output = args.profile
    prof_inherit = ProfileInherit()
    assert prof_inherit._run(args) == 2


def test_profile_generate_assemble_parameter_aggregation(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test the profile markdown generator."""
    _, assembled_prof_dir, _, markdown_path = setup_profile_generate(tmp_trestle_dir, 'simple_test_profile.json')
    yaml_header_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    ac_path = markdown_path / 'ac'

    nist_cat, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'nist_cat', cat.Catalog, FileContentType.JSON)

    appended_prop = {'name': 'aggregates', 'value': 'at-02_odp.01'}
    second_appended_prop = {'name': 'aggregates', 'value': 'at-02_odp.02'}
    third_appended_prop = {'name': 'alt-identifier', 'value': 'this_is_an_identifier'}
    ac_1 = nist_cat.groups[0].controls[0]
    ac_1.params[6].props = []
    ac_1.params[6].props.append(appended_prop)
    ac_1.params[6].props.append(second_appended_prop)
    ac_1.params[6].props.append(third_appended_prop)
    appended_extra_param = {
        'id': 'at-02_odp.01',
        'props': [{
            'name': 'label', 'value': 'AT-02_ODP[01]', 'class': 'sp800-53a'
        }],
        'label': 'frequency',
        'values': ['value-1', 'value-2'],
        'guidelines': [{
            'prose': 'blah'
        }]
    }
    second_appended_extra_param = {
        'id': 'at-02_odp.02',
        'props': [{
            'name': 'label', 'value': 'AT-02_ODP[02]', 'class': 'sp800-53a'
        }],
        'label': 'frequency',
        'values': ['value-3', 'value-4'],
        'guidelines': [{
            'prose': 'blah'
        }]
    }
    ac_1.params.append(appended_extra_param)
    ac_1.params.append(second_appended_extra_param)

    ModelUtils.save_top_level_model(nist_cat, tmp_trestle_dir, 'nist_cat', FileContentType.JSON)

    # convert resolved profile catalog to markdown then assemble it after adding an item to a control
    # generate, edit, assemble
    test_args = f'trestle author profile-generate -n {prof_name} -o {md_name} -rs NeededExtra'.split(  # noqa E501
    )
    test_args.extend(['-y', str(yaml_header_path)])
    test_args.extend(['-s', all_sections_str])
    monkeypatch.setattr(sys, 'argv', test_args)

    assert Trestle().run() == 0

    fc = test_utils.FileChecker(ac_path)

    assert Trestle().run() == 0

    assert fc.files_unchanged()

    # assemble based on set_parameters_flag
    test_args = f'trestle author profile-assemble -n {prof_name} -m {md_name} -o {assembled_prof_name}'.split()
    test_args.append('-sp')
    assembled_prof_dir.mkdir()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 0


def test_profile_generate_assesment_objectives(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the profile markdown generator."""
    _, _, _, _ = setup_profile_generate(tmp_trestle_dir, 'simple_test_profile.json')
    yaml_header_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'

    profile, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'my_prof', prof.Profile, FileContentType.JSON)

    # create with-id to load at-2 control with its corresponding assesment objectives
    with_id_at_2 = gens.generate_sample_model(prof.WithId)
    with_id_at_2.__root__ = 'at-2'

    profile.imports[0].include_controls[0].with_ids.append(with_id_at_2)

    ModelUtils.save_top_level_model(profile, tmp_trestle_dir, 'my_prof', FileContentType.JSON)

    nist_cat, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'nist_cat', cat.Catalog, FileContentType.JSON)
    # create assesment objectives json for adding it to the control in the catalog
    assesment_objectives = {
        'id': 'at-2_obj',
        'name': 'assessment-objective',
        'props': [{
            'name': 'label', 'value': 'AT-02', 'class': 'sp800-53a'
        }],
        'parts': [
            {
                'id': 'at-2_obj.a',
                'name': 'assessment-objective',
                'props': [{
                    'name': 'label', 'value': 'AT-02a.', 'class': 'sp800-53a'
                }],
                'parts': [
                    {
                        'id': 'at-2_obj.a.1-2',
                        'name': 'assessment-objective',
                        'props': [{
                            'name': 'label', 'value': 'AT-02a.01[02]', 'class': 'sp800-53a'
                        }],
                        'prose': 'some example prose'
                    },
                    {
                        'id': 'at-2_obj.a.1-3',
                        'name': 'assessment-objective',
                        'props': [{
                            'name': 'label', 'value': 'AT-02a.01[03]', 'class': 'sp800-53a'
                        }],
                        'prose': 'some example prose'
                    }
                ]
            }
        ]
    }

    at_2 = nist_cat.groups[1].controls[1]
    at_2.parts.append(assesment_objectives)
    ModelUtils.save_top_level_model(nist_cat, tmp_trestle_dir, 'nist_cat', FileContentType.JSON)

    # convert resolved profile catalog to markdown then assemble it after adding an item to a control
    # generate, edit, assemble
    test_args = f'trestle author profile-generate -n {prof_name} -o {md_name} -rs NeededExtra'.split(  # noqa E501
    )
    test_args.extend(['-y', str(yaml_header_path)])
    test_args.extend(['-s', all_sections_str])
    monkeypatch.setattr(sys, 'argv', test_args)

    assert Trestle().run() == 0
