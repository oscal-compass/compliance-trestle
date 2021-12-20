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

import pytest

from ruamel.yaml import YAML

from tests import test_utils
from tests.test_utils import setup_for_ssp

import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.core import const
from trestle.core.commands.author.ssp import SSPAssemble, SSPFilter, SSPGenerate
from trestle.core.control_io import ControlIOReader
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.profile_resolver import ProfileResolver
from trestle.utils import fs

prof_name = 'main_profile'
ssp_name = 'my_ssp'
cat_name = 'nist_cat'


def insert_prose(trestle_dir: pathlib.Path, statement_id: str, prose: str) -> bool:
    """Insert response prose in for a statement of a control."""
    control_dir = trestle_dir / ssp_name / statement_id.split('-')[0]
    md_file = control_dir / (statement_id.split('_')[0] + '.md')

    return test_utils.insert_text_in_file(md_file, f'for item {statement_id}', prose)


def confirm_control_contains(trestle_dir: pathlib.Path, control_id: str, part_label: str, seek_str: str) -> bool:
    """Confirm the text is present in the control markdown in the correct part."""
    control_dir = trestle_dir / ssp_name / control_id.split('-')[0]
    md_file = control_dir / f'{control_id}.md'

    comp_dict, _ = ControlIOReader.read_all_implementation_prose_and_header(md_file)
    for label_dict in comp_dict.values():
        if part_label in label_dict:
            prose = '\n'.join(label_dict[part_label])
            if seek_str in prose:
                return True
    return False


@pytest.mark.parametrize('import_cat', [False, True])
@pytest.mark.parametrize('sections', [False, True])
def test_ssp_generate(import_cat, sections, tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator."""
    args, _, yaml_path = setup_for_ssp(True, False, tmp_trestle_dir, prof_name, ssp_name, import_cat)
    if not sections:
        args.sections = None
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

    with open(yaml_path, 'r', encoding=const.FILE_ENCODING) as f:
        yaml = YAML()
        expected_header = yaml.load(f)
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    assert expected_header == header
    header, tree = md_api.processor.process_markdown(ac_2)
    assert tree is not None
    assert expected_header == header


def test_ssp_failures(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp failure modes."""
    ssp_cmd = SSPGenerate()

    # bad yaml
    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=True,
        sections=None,
        yaml_header=str(yaml_path),
        preserve_header_values=False
    )
    assert ssp_cmd._run(args) == 1

    # test missing profile
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile='foo',
        output=ssp_name,
        sections=None,
        verbose=True,
        preserve_header_values=False
    )
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_no_header(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with no yaml header."""
    args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir, prof_name, ssp_name)
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

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    assert not header
    header, tree = md_api.processor.process_markdown(ac_2)
    assert tree is not None
    assert not header


def test_ssp_generate_fail_statement_section(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test the ssp generator fails if 'statement' is provided.

    Also checking code where not label is provided.
    """
    args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir, prof_name, ssp_name)
    args.sections = 'statement'
    ssp_cmd = SSPGenerate()
    # run the command for happy path
    assert ssp_cmd._run(args) > 0


@pytest.mark.parametrize('yaml_header', [False, True])
def test_ssp_generate_header_edit(yaml_header: bool, tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp generate does not overwrite header edits."""
    # always start by creating the markdown with the yaml header
    args, _, yaml_path = setup_for_ssp(True, False, tmp_trestle_dir, prof_name, ssp_name)
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'

    with open(yaml_path, 'r', encoding=const.FILE_ENCODING) as f:
        yaml = YAML()
        yaml_header = yaml.load(f)

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    assert yaml_header == header

    # edit the header by adding a list item and removing a value
    assert test_utils.insert_text_in_file(ac_1, 'System Specific', '  - My new edits\n')
    assert test_utils.delete_line_in_file(ac_1, 'Corporate')

    # if the yaml header is not written out, the new header should be the one currently in the control
    # if the yaml header is written out, it is merged with the current header giving priority to current header
    # so if not written out, the header should have one item added and another deleted due to edits in this test
    # if written out, it should just have the one added item because the deleted one will be put back in

    # tell it not to add the yaml header
    if not yaml_header:
        args.yaml_header = None

    assert ssp_cmd._run(args) == 0
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None

    assert len(header['control-origination']) == 2
    if not yaml_header:
        assert 'new' in header['control-origination'][0]
    else:
        assert 'new' not in header['control-origination'][0]


def test_ssp_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp assemble from cli."""
    gen_args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, prof_name, ssp_name)

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0
    acme_string = 'Do the ACME requirements'

    prose_a = 'Hello there\n  How are you\n line with more text\n\ndouble line'
    prose_b = 'This is fun\nline with *bold* text\n\n### ACME Component\n\n' + acme_string

    # edit it a bit
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.a', prose_a)
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.b', prose_b)

    # generate markdown again on top of previous markdown to make sure it is not removed
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True, regenerate=False
    )
    assert ssp_assemble._run(args) == 0

    orig_ssp, _ = fs.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    orig_uuid = orig_ssp.uuid
    assert len(orig_ssp.system_implementation.components) == 2

    # now write it back out and confirm text is still there
    assert ssp_gen._run(gen_args) == 0
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'a.', 'Hello there')
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'a.', 'line with more text')
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'b.', 'This is fun')

    # now assemble it again but don't regen uuid's
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True, regenerate=False
    )
    assert ssp_assemble._run(args) == 0

    repeat_ssp, _ = fs.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    assert orig_ssp.control_implementation == repeat_ssp.control_implementation
    assert orig_ssp.system_implementation == repeat_ssp.system_implementation
    assert len(repeat_ssp.system_implementation.components) == 2

    found_it = False
    for imp_req in repeat_ssp.control_implementation.implemented_requirements:
        if imp_req.control_id == 'ac-1':
            statements = imp_req.statements
            assert len(statements) == 3
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
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True, regenerate=True
    )
    assert ssp_assemble._run(args) == 0
    assert orig_uuid != test_utils.get_model_uuid(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)


def test_ssp_generate_bad_name(tmp_trestle_dir: pathlib.Path) -> None:
    """Test bad output name."""
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile=prof_name, output='catalogs', verbose=True, yaml_header='dummy.yaml'
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

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True)
    assert ssp_assemble._run(args) == 0

    # load the ssp so we can add a setparameter to it for more test coverage
    ssp, _ = fs.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, fs.FileContentType.JSON)
    new_setparam = ossp.SetParameter(param_id='ac-1_prm_1', values=['new_value'])
    ssp.control_implementation.set_parameters = [new_setparam]
    fs.save_top_level_model(ssp, tmp_trestle_dir, ssp_name, fs.FileContentType.JSON)

    filtered_name = 'filtered_ssp'

    # now filter the ssp through test_profile_d
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile='test_profile_d',
        output=filtered_name,
        verbose=True,
        regenerate=False
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    orig_uuid = test_utils.get_model_uuid(tmp_trestle_dir, filtered_name, ossp.SystemSecurityPlan)

    # filter it again to confirm uuid is same
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile='test_profile_d',
        output=filtered_name,
        verbose=True,
        regenerate=False
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    assert orig_uuid == test_utils.get_model_uuid(tmp_trestle_dir, filtered_name, ossp.SystemSecurityPlan)

    # filter again to confirm uuid is different with regen
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile='test_profile_d',
        output=filtered_name,
        verbose=True,
        regenerate=True
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    assert orig_uuid != test_utils.get_model_uuid(tmp_trestle_dir, filtered_name, ossp.SystemSecurityPlan)

    # now filter the ssp through test_profile_b to force error because b references controls not in the ssp
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile='test_profile_b',
        output=filtered_name,
        verbose=True,
        regenerate=True
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1


def test_ssp_bad_control_id(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp gen when profile has bad control id."""
    profile = prof.Profile.oscal_read(test_utils.JSON_TEST_DATA_PATH / 'profile_bad_control.json')
    fs.save_top_level_model(profile, tmp_trestle_dir, 'bad_prof', fs.FileContentType.JSON)
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile='bad_prof', output='my_ssp', verbose=False, sections=None
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_ssp_assemble_header_metadata(tmp_trestle_dir: pathlib.Path) -> None:
    """Test parsing of metadata from yaml header."""
    catalog = test_utils.generate_complex_catalog()
    fs.save_top_level_model(catalog, tmp_trestle_dir, 'complex_cat', fs.FileContentType.JSON)
    prof_name = 'test_profile_c'
    ssp_name = 'my_ssp'
    profile = prof.Profile.oscal_read(test_utils.JSON_TEST_DATA_PATH / f'{prof_name}.json')
    fs.save_top_level_model(profile, tmp_trestle_dir, prof_name, fs.FileContentType.JSON)
    header_path = test_utils.YAML_TEST_DATA_PATH / 'header_with_metadata.yaml'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=False,
        sections=None,
        yaml_header=header_path,
        preserve_header_values=False
    )
    # generate the markdown with header content
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=False)
    assert ssp_assemble._run(args) == 0

    # read the assembled ssp and confirm roles are in metadata
    ssp, _ = fs.load_top_level_model(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, fs.FileContentType.JSON)
    assert len(ssp.metadata.roles) == 2


def test_ssp_generate_generate(tmp_trestle_dir: pathlib.Path) -> None:
    """Test repeat generate with various controls including statement with no parts."""
    cat_name = 'complex_cat'
    prof_name = 'my_prof'
    ssp_name = 'my_ssp'
    catalog = test_utils.generate_complex_catalog()
    fs.save_top_level_model(catalog, tmp_trestle_dir, cat_name, fs.FileContentType.JSON)
    test_utils.create_profile_in_trestle_dir(tmp_trestle_dir, cat_name, prof_name)

    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=False,
        sections=None,
        yaml_header=None,
        preserve_header_values=False
    )
    # generate the markdown with no implementation response text
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    # insert implementation text into the high level statement of a control that has no sub-parts
    control_path = tmp_trestle_dir / ssp_name / 'test-1.md'
    test_utils.insert_text_in_file(control_path, 'control test-1', '\nHello there')

    control_a1_path = tmp_trestle_dir / ssp_name / 'a-1.md'
    test_utils.insert_text_in_file(control_a1_path, const.SSP_ADD_IMPLEMENTATION_PREFIX, 'Text with prompt removed')
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
