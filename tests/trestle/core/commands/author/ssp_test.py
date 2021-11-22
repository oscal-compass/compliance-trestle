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
from typing import Tuple

import pytest

from ruamel.yaml import YAML

from tests import test_utils

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


def setup_for_ssp(include_header: bool,
                  big_profile: bool,
                  tmp_trestle_dir: pathlib.Path,
                  import_nist_cat: bool = True) -> Tuple[argparse.Namespace, str]:
    """Create the markdown ssp content from catalog and profile."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, big_profile, import_nist_cat)

    sections = 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence,guidance:Guidance'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=True,
        sections=sections,
        header_dont_merge=False
    )

    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    if include_header:
        args.yaml_header = str(yaml_path)

    return args, sections, yaml_path


def insert_prose(trestle_dir: pathlib.Path, statement_id: str, prose: str) -> bool:
    """Insert response prose in for a statement of a control."""
    control_dir = trestle_dir / ssp_name / statement_id.split('-')[0]
    md_file = control_dir / (statement_id.split('_')[0] + '.md')

    return test_utils.insert_text_in_file(md_file, f'for item {statement_id}', prose)


def confirm_control_contains(trestle_dir: pathlib.Path, control_id: str, part_label: str, seek_str: str) -> bool:
    """Confirm the text is present in the control markdown in the correct part."""
    control_dir = trestle_dir / ssp_name / control_id.split('-')[0]
    md_file = control_dir / f'{control_id}.md'

    responses, _ = ControlIOReader.read_all_implementation_prose_and_header(md_file)
    if part_label not in responses:
        return False
    prose = '\n'.join(responses[part_label])
    return seek_str in prose


@pytest.mark.parametrize('import_cat', [False, True])
def test_ssp_generate(import_cat, tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator."""
    args, sections, yaml_path = setup_for_ssp(True, False, tmp_trestle_dir, import_cat)
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

    # test simple failure mode
    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=True,
        sections=sections,
        yaml_header=str(yaml_path),
        header_dont_merge=False
    )
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_no_header(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with no yaml header."""
    args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir)
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
    args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir)
    args.sections = 'statement'
    ssp_cmd = SSPGenerate()
    # run the command for happy path
    assert ssp_cmd._run(args) > 0


@pytest.mark.parametrize('yaml_header', [False, True])
def test_ssp_generate_header_edit(yaml_header: bool, tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp generate does not overwrite header edits."""
    # always start by creating the markdown with the yaml header
    args, _, yaml_path = setup_for_ssp(True, False, tmp_trestle_dir)
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'

    with open(yaml_path, 'r', encoding=const.FILE_ENCODING) as f:
        yaml = YAML()
        expected_header = yaml.load(f)

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    assert expected_header == header

    assert test_utils.insert_text_in_file(ac_1, 'System Specific', '  - My new edits\n')
    assert test_utils.delete_line_in_file(ac_1, 'Corporate')

    # if the yaml header is not written out, the new header should be the one currently in the control
    # if the yaml header is written out, it is merged with the current header giving priority to current header
    # so if not written out, the header should have one item added and another deleted
    # if written out, it should just have the one added item because the deleted one will be put back in

    # tell it not to add the yaml header
    if not yaml_header:
        args.yaml_header = None

    assert ssp_cmd._run(args) == 0
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    new_expected_header = expected_header
    new_expected_header['control-origination'].append('My new edits')

    if not yaml_header:
        new_expected_header['control-origination'] = new_expected_header['control-origination'][1:]
    assert new_expected_header == header


def test_ssp_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp assemble from cli."""
    gen_args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir)

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    prose_a = 'Hello there\n  How are you\n line with more text\n\ndouble line'
    prose_b = 'This is fun\nline with *bold* text'

    # edit it a bit
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.a', prose_a)
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.b', prose_b)

    # generate markdown again on top of previous markdown to make sure it is not removed
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True)
    assert ssp_assemble._run(args) == 0

    # now write it back out and confirm text is still there
    assert ssp_gen._run(gen_args) == 0
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'a.', 'Hello there')
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'a.', 'line with more text')
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'b.', 'This is fun')


def test_ssp_generate_bad_name(tmp_trestle_dir: pathlib.Path) -> None:
    """Test bad output name."""
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile=prof_name, output='catalogs', verbose=True, yaml_header='dummy.yaml'
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_resolved_catalog(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator to create a resolved profile catalog."""
    _, _, _ = setup_for_ssp(False, True, tmp_trestle_dir)
    profile_path = tmp_trestle_dir / f'profiles/{prof_name}/profile.json'
    new_catalog_dir = tmp_trestle_dir / f'catalogs/{prof_name}_resolved_catalog'
    new_catalog_dir.mkdir(parents=True, exist_ok=True)
    new_catalog_path = new_catalog_dir / 'catalog.json'

    profile_resolver = ProfileResolver()
    resolved_catalog = profile_resolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    assert resolved_catalog
    assert len(resolved_catalog.groups) == 18

    resolved_catalog.oscal_write(new_catalog_path)


def test_ssp_filter(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp filter."""
    # install the catalog and profiles
    gen_args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir, True)
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

    # now filter the ssp through test_profile_d
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, name=ssp_name, profile='test_profile_d', output='filtered_ssp', verbose=True
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    # now filter the ssp through test_profile_b
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, name=ssp_name, profile='test_profile_b', output='filtered_ssp', verbose=True
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1
