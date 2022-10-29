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
"""Tests for the ssp_generator module."""

import argparse
import pathlib
from typing import List

import pytest

from tests import test_utils
from tests.test_utils import delete_line_in_file, setup_for_ssp

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.common import const, file_utils
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPAssemble, SSPFilter, SSPGenerate
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_reader import ControlReader
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

prof_name = 'main_profile'
ssp_name = 'my_ssp'
cat_name = 'nist_cat'


def insert_prose(trestle_dir: pathlib.Path, statement_id: str, prose: str) -> bool:
    """Insert response prose in for a statement of a control."""
    control_dir = trestle_dir / ssp_name / statement_id.split('-')[0]
    md_file = control_dir / (statement_id.split('_')[0] + '.md')

    return file_utils.insert_text_in_file(md_file, f'for item {statement_id}', prose)


def confirm_control_contains(trestle_dir: pathlib.Path, control_id: str, part_label: str, seek_str: str) -> bool:
    """Confirm the text is present in the control markdown in the correct part."""
    control_dir = trestle_dir / ssp_name / control_id.split('-')[0]
    md_file = control_dir / f'{control_id}.md'
    context = ControlContext.generate(ContextPurpose.SSP, False, trestle_dir, trestle_dir)
    comp_dict, _ = ControlReader.read_all_implementation_prose_and_header(None, md_file, context)
    for label_dict in comp_dict.values():
        if part_label in label_dict:
            prose = label_dict[part_label].prose
            if seek_str in prose:
                return True
    return False


@pytest.mark.parametrize('import_cat', [False, True])
@pytest.mark.parametrize('specify_sections', [False, True])
def test_ssp_generate(import_cat, specify_sections, tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator."""
    args, _, _ = setup_for_ssp(True, False, tmp_trestle_dir, prof_name, ssp_name, import_cat)
    if specify_sections:
        args.allowed_sections = 'implgdn,expevid'

    ssp_cmd = SSPGenerate()
    # run the command for happy path
    assert ssp_cmd._run(args) == 0
    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'
    ac_2 = ac_dir / 'ac-2.md'
    assert ac_1.exists()
    assert ac_2.exists()
    assert ac_1.stat().st_size > 1000
    assert ac_2.stat().st_size > 2000

    assert test_utils.confirm_text_in_file(ac_1, '## Control', '## Control Guidance') != specify_sections
    md_api = MarkdownAPI()
    _, tree = md_api.processor.process_markdown(ac_1)
    # if sections specified then Control Guidance does not appear
    rc = 11 if specify_sections else 12
    assert tree.get_count_of_subnodes() == rc
    _, tree = md_api.processor.process_markdown(ac_2)
    rc = 29 if specify_sections else 30
    assert tree.get_count_of_subnodes() == rc


def test_ssp_failures(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp failure modes."""
    ssp_cmd = SSPGenerate()

    # bad yaml
    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=0,
        sections=None,
        yaml_header=str(yaml_path),
        overwrite_header_values=False
    )
    assert ssp_cmd._run(args) == 1

    # test missing profile
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile='foo',
        output=ssp_name,
        sections=None,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None
    )
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_no_header(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with no yaml header."""
    args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir, prof_name, ssp_name)
    ssp_cmd = SSPGenerate()
    args.sections = None
    # run the command for happy path
    assert ssp_cmd._run(args) == 0
    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'
    ac_2 = ac_dir / 'ac-2.md'
    assert ac_1.exists()
    assert ac_2.exists()
    assert ac_1.stat().st_size > 1000
    assert ac_2.stat().st_size > 2000

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    assert header[const.SORT_ID] == 'ac-01'
    header, tree = md_api.processor.process_markdown(ac_2)
    assert tree is not None
    assert header[const.SORT_ID] == 'ac-02'


def test_ssp_generate_fail_statement_section(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test the ssp generator fails if const.STATEMENT is provided.

    Also checking code where not label is provided.
    """
    args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir, prof_name, ssp_name)
    args.sections = const.STATEMENT
    ssp_cmd = SSPGenerate()
    # run the command for happy path
    assert ssp_cmd._run(args) > 0


@pytest.mark.parametrize('load_yaml_header', [False, True])
def test_ssp_generate_header_edit(load_yaml_header: bool, tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp generate does not overwrite header edits."""
    # always start by creating the markdown with the yaml header
    args, sections, yaml_path = setup_for_ssp(True, False, tmp_trestle_dir, prof_name, ssp_name)
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    # confirm info from the yaml header was loaded
    assert len(header['control-origination']) == 2

    # edit the header by adding a list item and removing a value
    assert file_utils.insert_text_in_file(ac_1, 'System Specific', '  - My new edits\n')
    assert test_utils.delete_line_in_file(ac_1, 'Corporate')

    # if the yaml header is not written out, the new header should be the one currently in the control
    # if the yaml header is written out, it is merged with the current header giving priority to current header
    # so if not written out, the header should have one item added and another deleted due to edits in this test
    # if written out, it should just have the one added item because the deleted one will be put back in

    # tell it not to add the yaml header
    if not load_yaml_header:
        args.yaml_header = None

    assert ssp_cmd._run(args) == 0
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None

    co = header['control-origination']
    assert co[0] == 'Service Provider System Specific'
    assert co[1] == 'My new edits'
    if not load_yaml_header:
        assert len(co) == 2
    else:
        assert co[2] == 'Service Provider Corporate'
        assert len(co) == 3


def test_ssp_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp assemble from cli."""
    gen_args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, prof_name, ssp_name)

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0
    acme_string = 'Do the ACME requirements'
    new_version = '1.2.3'

    prose_a = 'Hello there\n  How are you\n line with more text\n\ndouble line'
    prose_b = 'This is fun\nline with *bold* text\n\n### ACME Component\n\n' + acme_string

    # edit it a bit
    ac_1_path = tmp_trestle_dir / ssp_name / 'ac/ac-1.md'
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.a', prose_a)
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.b', prose_b)
    assert delete_line_in_file(ac_1_path, 'Add control implementation description')
    assert delete_line_in_file(ac_1_path, 'Add control implementation description')

    # special handling for ac-2.1 because it has no statement sub-parts
    add_prompt = 'Add control implementation description here for control ac-2.1'
    add_response = 'My statement level prose'
    ac_21_path = tmp_trestle_dir / ssp_name / 'ac/ac-2.1.md'
    assert test_utils.substitute_text_in_file(ac_21_path, add_prompt, add_response)

    # generate markdown again on top of previous markdown to make sure it is not removed
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version=new_version,
        name=None
    )
    assert ssp_assemble._run(args) == 0

    orig_ssp, orig_ssp_path = ModelUtils.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    orig_uuid = orig_ssp.uuid
    assert len(orig_ssp.system_implementation.components) == 2
    assert orig_ssp.metadata.version.__root__ == new_version
    assert ModelUtils.model_age(orig_ssp) < test_utils.NEW_MODEL_AGE_SECONDS
    imp_reqs = orig_ssp.control_implementation.implemented_requirements
    imp_req = next((i_req for i_req in imp_reqs if i_req.control_id == 'ac-2.1'), None)
    assert imp_req.statements[0].by_components[0].description == add_response

    orig_file_creation = orig_ssp_path.stat().st_mtime

    # now write it back out and confirm text is still there
    assert ssp_gen._run(gen_args) == 0
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'a.', 'Hello there')
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'a.', 'line with more text')
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'b.', 'This is fun')
    assert test_utils.confirm_text_in_file(ac_21_path, const.SSP_MD_IMPLEMENTATION_QUESTION, add_response)

    # now assemble it again but don't regen uuid's and don't change version
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        name=None,
        version=None
    )
    assert ssp_assemble._run(args) == 0

    # confirm the file was not written out since no change
    assert orig_ssp_path.stat().st_mtime == orig_file_creation

    repeat_ssp, _ = ModelUtils.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    assert orig_ssp.control_implementation == repeat_ssp.control_implementation
    assert orig_ssp.system_implementation == repeat_ssp.system_implementation
    assert len(repeat_ssp.system_implementation.components) == 2
    assert repeat_ssp.metadata.version.__root__ == new_version

    found_it = False
    for imp_req in repeat_ssp.control_implementation.implemented_requirements:
        if imp_req.control_id == 'ac-1':
            statements = imp_req.statements
            assert len(statements) == 4
            for statement in statements:
                for by_component in statement.by_components:
                    if by_component.description == acme_string:
                        found_it = True
                        assert len(statement.by_components) == 2
                        break
        if found_it:
            break
    assert found_it

    # assemble it again but regen uuid's
    # this should not regen uuid's because the file is not written out if only difference is uuid's
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=True,
        name=None,
        version=None
    )
    assert ssp_assemble._run(args) == 0
    assert orig_uuid == test_utils.get_model_uuid(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    # confirm the file was not written out since no change
    assert orig_ssp_path.stat().st_mtime == orig_file_creation

    # assemble it again but give new version and regen uuid's
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=True,
        name=None,
        version='new version to force write'
    )
    assert ssp_assemble._run(args) == 0
    assert orig_uuid != test_utils.get_model_uuid(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    # confirm the file was not written out since no change
    assert orig_ssp_path.stat().st_mtime > orig_file_creation


def test_ssp_generate_bad_name(tmp_trestle_dir: pathlib.Path) -> None:
    """Test bad output name."""
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile=prof_name, output='catalogs', verbose=0, yaml_header='dummy.yaml'
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_resolved_catalog(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator to create a resolved profile catalog."""
    _, _, _ = setup_for_ssp(False, True, tmp_trestle_dir, prof_name, ssp_name)
    profile_path = tmp_trestle_dir / f'profiles/{prof_name}/profile.json'
    new_catalog_dir = tmp_trestle_dir / f'catalogs/{prof_name}_resolved_catalog'
    new_catalog_dir.mkdir(parents=True, exist_ok=True)
    new_catalog_path = new_catalog_dir / 'catalog.json'

    profile_resolver = ProfileResolver()
    resolved_catalog = profile_resolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    assert resolved_catalog
    # FIXME this should test with a more complex catalog
    assert len(resolved_catalog.groups) == 1

    resolved_catalog.oscal_write(new_catalog_path)


def test_ssp_filter(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp filter."""
    # install the catalog and profiles
    gen_args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir, prof_name, ssp_name, True)
    # create markdown with profile a
    gen_args.profile = 'test_profile_a'
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # add responses by component
    ac1_path = tmp_trestle_dir / ssp_name / 'ac/ac-1.md'
    imp_text = """
### foo
implement the foo requirements

### bar
also do the bar stuff

"""
    file_utils.insert_text_in_file(ac1_path, 'ac-1_smt.a', imp_text)

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        name=None,
        version=None,
        regenerate=False
    )
    assert ssp_assemble._run(args) == 0

    # load the ssp so we can add a setparameter to it for more test coverage
    ssp: ossp.SystemSecurityPlan
    ssp, _ = ModelUtils.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
    # confirm all by_comps are there for this system, foo, bar
    assert len(ssp.control_implementation.implemented_requirements[1].statements[1].by_components) == 3

    # get the original uuid
    orig_uuid = ssp.uuid

    # confirm there are seven controls and corresponding imp_reqs
    assert len(ssp.control_implementation.implemented_requirements) == 7

    new_setparam = ossp.SetParameter(param_id='ac-1_prm_1', values=['new_value'])
    ssp.control_implementation.set_parameters = [new_setparam]
    ModelUtils.save_top_level_model(ssp, tmp_trestle_dir, ssp_name, FileContentType.JSON)

    filtered_name = 'filtered_ssp'

    # now filter the ssp through test_profile_d
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile='test_profile_d',
        output=filtered_name,
        verbose=0,
        regenerate=False,
        version=None,
        components=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_top_level_model(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # confirm the imp_reqs have been culled by profile_d to only two controls
    assert len(ssp.control_implementation.implemented_requirements) == 2

    # confirm there are three by_comps for: this system, foo, bar
    assert len(ssp.control_implementation.implemented_requirements[0].statements[1].by_components) == 3

    # confirm uuid was not regenerated
    assert ssp.uuid == orig_uuid

    # now filter the ssp by components
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components='this system:foo'
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_top_level_model(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # get the uuid and confirm it was regenerated this time
    new_uuid = ssp.uuid
    assert new_uuid != orig_uuid

    # confirm the bar by_comp has been filtered out
    assert len(ssp.control_implementation.implemented_requirements[1].statements[1].by_components) == 2

    # filter the filtered ssp again to confirm uuid does not change even with regen because contents are the same
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=filtered_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components='this system:foo'
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    assert new_uuid == test_utils.get_model_uuid(tmp_trestle_dir, filtered_name, ossp.SystemSecurityPlan)

    # now filter without profile or components to trigger error
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1

    # now filter the ssp through test_profile_b to force error because b references controls not in the ssp
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile='test_profile_b',
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1


def test_ssp_bad_control_id(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp gen when profile has bad control id."""
    profile = prof.Profile.oscal_read(test_utils.JSON_TEST_DATA_PATH / 'profile_bad_control.json')
    ModelUtils.save_top_level_model(profile, tmp_trestle_dir, 'bad_prof', FileContentType.JSON)
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile='bad_prof', output='my_ssp', verbose=0, sections=None, yaml_header=None
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_ssp_assemble_header_metadata(tmp_trestle_dir: pathlib.Path) -> None:
    """Test parsing of metadata from yaml header."""
    catalog = test_utils.generate_complex_catalog()
    ModelUtils.save_top_level_model(catalog, tmp_trestle_dir, 'complex_cat', FileContentType.JSON)
    prof_name = 'test_profile_c'
    ssp_name = 'my_ssp'
    profile = prof.Profile.oscal_read(test_utils.JSON_TEST_DATA_PATH / f'{prof_name}.json')
    ModelUtils.save_top_level_model(profile, tmp_trestle_dir, prof_name, FileContentType.JSON)
    header_path = test_utils.YAML_TEST_DATA_PATH / 'header_with_metadata.yaml'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=0,
        sections=None,
        yaml_header=header_path,
        overwrite_header_values=False,
        allowed_sections=None
    )
    # generate the markdown with header content
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        name=None,
        version=None,
        regenerate=False
    )
    assert ssp_assemble._run(args) == 0

    # read the assembled ssp and confirm roles are in metadata
    ssp, _ = ModelUtils.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
    assert len(ssp.metadata.roles) == 2


def test_ssp_generate_generate(tmp_trestle_dir: pathlib.Path) -> None:
    """Test repeat generate with various controls including statement with no parts."""
    cat_name = 'complex_cat'
    prof_name = 'my_prof'
    ssp_name = 'my_ssp'
    catalog = test_utils.generate_complex_catalog()
    ModelUtils.save_top_level_model(catalog, tmp_trestle_dir, cat_name, FileContentType.JSON)
    test_utils.create_profile_in_trestle_dir(tmp_trestle_dir, cat_name, prof_name)

    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=0,
        sections=None,
        yaml_header=None,
        overwrite_header_values=False,
        allowed_sections=None
    )
    # generate the markdown with no implementation response text
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    # insert implementation text into the high level statement of a control that has no sub-parts
    control_path = tmp_trestle_dir / ssp_name / 'test-1.md'
    file_utils.insert_text_in_file(control_path, 'control test-1', '\nHello there')

    control_a1_path = tmp_trestle_dir / ssp_name / 'a-1.md'
    file_utils.insert_text_in_file(control_a1_path, const.SSP_ADD_IMPLEMENTATION_PREFIX, 'Text with prompt removed')
    test_utils.delete_line_in_file(control_a1_path, const.SSP_ADD_IMPLEMENTATION_PREFIX)

    assert ssp_cmd._run(args) == 0

    # confirm the added text is still there
    assert test_utils.confirm_text_in_file(control_path, 'control test-1', 'Hello there')
    # confirm added text in a1 is there
    assert test_utils.confirm_text_in_file(control_a1_path, '## Implementation', 'Text with prompt removed')
    # confirm prompt is not there
    assert not test_utils.confirm_text_in_file(
        control_a1_path, '## Implementation', const.SSP_ADD_IMPLEMENTATION_PREFIX
    )


def test_ssp_generate_tutorial(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with the nist tutorial catalog and profile."""
    catalog = cat.Catalog.oscal_read(test_utils.JSON_TEST_DATA_PATH / 'nist_tutorial_catalog.json')
    ModelUtils.save_top_level_model(catalog, tmp_trestle_dir, 'nist_tutorial_catalog', FileContentType.JSON)
    profile = prof.Profile.oscal_read(test_utils.JSON_TEST_DATA_PATH / 'nist_tutorial_profile.json')
    ModelUtils.save_top_level_model(profile, tmp_trestle_dir, 'nist_tutorial_profile', FileContentType.JSON)
    ssp_gen = SSPGenerate()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile='nist_tutorial_profile',
        output='ssp_md',
        sections=None,
        overwrite_header_values=False,
        verbose=0,
        yaml_header=None,
        allowed_sections=None
    )
    assert ssp_gen._run(args) == 0

    ssp_assem = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        output='ssp_json',
        markdown='ssp_md',
        verbose=0,
        name=None,
        version=None,
        regenerate=False
    )
    assert ssp_assem._run(args) == 0
    json_ssp: ossp.SystemSecurityPlan
    json_ssp, _ = ModelUtils.load_top_level_model(tmp_trestle_dir, 'ssp_json', ossp.SystemSecurityPlan)
    comp_def = json_ssp.system_implementation.components[0]
    assert comp_def.title == 'This System'
    assert comp_def.status.state == ossp.State1.other
    imp_reqs: List[ossp.ImplementedRequirement] = json_ssp.control_implementation.implemented_requirements
    assert len(imp_reqs) == 2
    assert imp_reqs[0].control_id == 's1.1.1'
    assert imp_reqs[1].control_id == 's2.1.2'
