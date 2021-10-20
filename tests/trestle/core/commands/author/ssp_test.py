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

from trestle.core import const
from trestle.core.commands.author.ssp import SSPAssemble, SSPGenerate
from trestle.core.commands.href import HrefCmd
from trestle.core.commands.import_ import ImportCmd
from trestle.core.control_io import ControlIOReader
from trestle.core.markdown_validator import MarkdownValidator
from trestle.core.profile_resolver import ProfileResolver

prof_name = 'my_prof'
ssp_name = 'my_ssp'
cat_name = 'imported_nist_cat'


def setup_for_ssp(include_header: bool,
                  big_profile: bool,
                  tmp_trestle_dir: pathlib.Path,
                  import_cat: bool = True) -> Tuple[argparse.Namespace, str]:
    """Create the markdown ssp content from catalog and profile."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    if big_profile:
        prof_path = test_utils.JSON_NIST_DATA_PATH / 'NIST_SP-800-53_rev5_MODERATE-baseline_profile.json'
    else:
        prof_path = test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(prof_path), output=prof_name, verbose=True, regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    # need to change href in profile to either imported location or cached external
    if import_cat:
        args = argparse.Namespace(
            trestle_root=tmp_trestle_dir, file=str(cat_path), output=cat_name, verbose=True, regenerate=True
        )
        assert i._run(args) == 0
        new_href = f'trestle://catalogs/{cat_name}/catalog.json'
    else:
        new_href = str(cat_path.resolve())
    assert HrefCmd.change_import_href(tmp_trestle_dir, prof_name, new_href, 0) == 0

    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    sections = 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence,guidance:Guidance'
    if include_header:
        args = argparse.Namespace(
            trestle_root=tmp_trestle_dir,
            profile=prof_name,
            output=ssp_name,
            verbose=True,
            sections=sections,
            yaml_header=str(yaml_path)
        )
    else:
        args = argparse.Namespace(
            trestle_root=tmp_trestle_dir, profile=prof_name, output=ssp_name, verbose=True, sections=sections
        )
    return args, sections, yaml_path


def insert_prose(trestle_dir: pathlib.Path, statement_id: str, prose: str) -> int:
    """Insert response prose in for a statement of a control."""
    control_dir = trestle_dir / ssp_name / statement_id.split('-')[0]
    md_file = control_dir / (statement_id.split('_')[0] + '.md')

    return test_utils.insert_text_in_file(md_file, f'for item {statement_id}', prose)


def confirm_control_contains(trestle_dir: pathlib.Path, control_id: str, part_label: str, seek_str: str) -> bool:
    """Confirm the text is present in the control markdown in the correct part."""
    control_dir = trestle_dir / ssp_name / control_id.split('-')[0]
    md_file = control_dir / f'{control_id}.md'

    responses = ControlIOReader.read_all_implementation_prose(md_file)
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
        yaml = YAML(typ='safe')
        expected_header = yaml.load(f)
    header, tree = MarkdownValidator.load_markdown_parsetree(ac_1)
    assert tree is not None
    assert expected_header == header
    header, tree = MarkdownValidator.load_markdown_parsetree(ac_1)
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
        yaml_header=str(yaml_path)
    )
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_no_header(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with no yaml header."""
    args, sections, yaml_path = setup_for_ssp(False, False, tmp_trestle_dir)
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

    header, tree = MarkdownValidator.load_markdown_parsetree(ac_1)
    assert tree is not None
    assert not header
    header, tree = MarkdownValidator.load_markdown_parsetree(ac_1)
    assert tree is not None
    assert not header


def test_ssp_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp assemble from cli."""
    gen_args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir)

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    prose_a = 'Hello there\n  How are you\n line with more text\n\ndouble line'
    prose_b = 'This is fun\nline with *bold* text'

    # edit it a bit
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.a', prose_a) == 0
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.b', prose_b) == 0

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
        trestle_root=tmp_trestle_dir, profile='my_prof', output='catalogs', verbose=True, yaml_header='dummy.yaml'
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_profile_resolver(tmp_trestle_dir: pathlib.Path) -> None:
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
