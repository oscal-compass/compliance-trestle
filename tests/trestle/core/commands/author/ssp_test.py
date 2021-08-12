# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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

from trestle.core.commands.author.ssp import SSPAssemble, SSPGenerate, SSPManager
from trestle.core.commands.href import HrefCmd
from trestle.core.commands.import_ import ImportCmd
from trestle.core.markdown_validator import MarkdownValidator

prof_name = 'my_prof'
ssp_name = 'my_ssp'


def setup_for_ssp(include_header: bool,
                  big_profile: bool,
                  tmp_trestle_dir: pathlib.Path,
                  import_cat: bool = True) -> Tuple[argparse.Namespace, str]:
    """Create the markdown ssp content from catalog and profile."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    cat_name = 'imported_nist_cat'
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
    assert HrefCmd.change_import_href(tmp_trestle_dir, prof_name, new_href) == 0

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


def insert_prose(trestle_dir: pathlib.Path, statement_id: str, prose: str) -> None:
    """Insert response prose in for a statement of a control."""
    control_dir = trestle_dir / ssp_name / statement_id.split('-')[0]
    md_file = control_dir / (statement_id.split('_')[0] + '.md')

    with open(md_file, 'r') as md:
        lines = md.readlines()

    with open(md_file, 'w') as md:
        for line in lines:
            # replace the 'Add control implementation' line with the new lines of prose
            if line.find(statement_id) < 0:
                md.write(line)
            else:
                md.write(prose + '\n')


@pytest.mark.parametrize('import_cat', [False, True])
def test_ssp_generator(import_cat, tmp_trestle_dir: pathlib.Path) -> None:
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

    with open(yaml_path, 'r', encoding='utf8') as f:
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


def test_ssp_generator_large_profile(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with a large profile."""
    args, sections, yaml_path = setup_for_ssp(True, True, tmp_trestle_dir)
    ssp_cmd = SSPGenerate()
    # run the command for happy path
    assert ssp_cmd._run(args) == 0
    controls_dir = tmp_trestle_dir / ssp_name
    ac_dir = controls_dir / 'ac'
    ac_1 = ac_dir / 'ac-1.md'
    ac_2 = ac_dir / 'ac-2.md'
    assert ac_1.exists()
    assert ac_2.exists()
    assert ac_1.stat().st_size > 1000
    assert ac_2.stat().st_size > 2000
    n_expected_groups = 18
    assert len(list(controls_dir.glob('*'))) == n_expected_groups


def test_ssp_generator_no_header(tmp_trestle_dir: pathlib.Path) -> None:
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


@pytest.mark.parametrize('use_tree', [False, True])
def test_ssp_assemble(use_tree: bool, tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp assemble."""
    args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir)

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(args) == 0

    prose_a = 'Hello there\n  How are you\n line with more text\n\ndouble line'
    prose_b = 'This is fun\nline with *bold* text'

    # edit it a bit
    insert_prose(tmp_trestle_dir, 'ac-1_smt.a', prose_a)
    insert_prose(tmp_trestle_dir, 'ac-1_smt.b', prose_b)

    # now assemble the edited controls into json ssp
    # two different invocations modes are used so that use_tree can be overridden
    if use_tree:
        ssp_assemble = SSPAssemble()
        args = argparse.Namespace(trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True)
        assert ssp_assemble._run(args) == 0
    else:
        ssp_manager = SSPManager()
        assert ssp_manager.assemble_ssp(ssp_name, ssp_name, True) == 0


def test_ssp_bad_name(tmp_trestle_dir: pathlib.Path) -> None:
    """Test bad output name."""
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile='my_prof', output='catalogs', verbose=True, yaml_header='dummy.yaml'
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_ssp_bad_dir(tmp_path: pathlib.Path) -> None:
    """Test ssp not in trestle project."""
    ssp_cmd = SSPGenerate()
    args = argparse.Namespace(
        trestle_root=tmp_path, profile='my_prof', output='my_ssp', verbose=True, yaml_header='dummy.yaml'
    )
    assert ssp_cmd._run(args) == 1

    ssp_cmd = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_path, markdown='my_ssp', output='my_json_ssp', verbose=True, yaml_header='dummy.yaml'
    )
    assert ssp_cmd._run(args) == 1


def test_ssp_internals() -> None:
    """Test unusual cases in ssp."""
    tree = [
        {
            'type': 'thematic_break'
        }, {
            'type': 'foo'
        }, {
            'type': 'heading', 'children': [{
                'text': 'Part a'
            }]
        }, {
            'type': 'bar'
        }
    ]
    ssp_manager = SSPManager()
    result = ssp_manager._get_label_prose(0, tree)
    assert result == (-1, 'a', '')
