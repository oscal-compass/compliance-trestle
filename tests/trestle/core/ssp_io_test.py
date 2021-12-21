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
"""Tests for the ssp_io."""
import pathlib
from typing import Tuple

from _pytest.monkeypatch import MonkeyPatch

from tests.test_utils import execute_command_and_assert, setup_for_ssp
from tests.trestle.core.commands.author.ssp_test import insert_prose

from trestle.core import profile_resolver
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.markdown.markdown_node import MarkdownNode
from trestle.core.remote import cache
from trestle.core.ssp_io import SSPMarkdownWriter
from trestle.oscal.ssp import SystemSecurityPlan

prof_name = 'main_profile'
ssp_name = 'my_ssp'


def setup_test(tmp_trestle_dir: pathlib.Path, testdata_dir: pathlib.Path,
               trestle_root: str) -> Tuple[pathlib.Path, SystemSecurityPlan]:
    """Prepare ssp test."""
    profile_path = tmp_trestle_dir / f'profiles/{prof_name}/profile.json'
    new_catalog_dir = tmp_trestle_dir / f'catalogs/{prof_name}_resolved_catalog'
    new_catalog_dir.mkdir(parents=True, exist_ok=True)

    ssp_json = testdata_dir / 'author/ssp/ssp_example.json'
    fetcher = cache.FetcherFactory.get_fetcher(trestle_root, str(ssp_json))
    ssp_obj, parent_alias = fetcher.get_oscal(True)

    assert parent_alias == 'system-security-plan'

    return profile_path, ssp_obj


def test_ssp_writer(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp writer from cli."""
    gen_args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, prof_name, ssp_name)

    profile_path, ssp_obj = setup_test(tmp_trestle_dir, testdata_dir, gen_args.trestle_root)

    resolved_catalog = profile_resolver.ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    ssp_writer = SSPMarkdownWriter(gen_args.trestle_root)
    ssp_writer.set_catalog(resolved_catalog)
    md_text = ssp_writer.get_control_statement('ac-2', 1)
    assert md_text is not None

    ssp_writer.set_ssp(ssp_obj)
    roles_md = ssp_writer.get_responsible_roles_table('ac-2', 1)
    assert roles_md

    md_text1 = ssp_writer._parameter_table('ac-2', 1)
    assert md_text1

    md_text3 = ssp_writer.get_fedramp_control_tables('ac-2', 1)
    assert md_text3

    md_text4 = ssp_writer.get_control_part('ac-2', 'item', 1)
    assert md_text4


def test_ssp_get_control_response(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test generating SSP from the sample profile and generate markdown representation of it."""
    args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, prof_name, ssp_name)
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    # set responses
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.b', 'This is a response')
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.c', 'This is also a response.')
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.a', 'This is a response.')

    command_ssp_gen = 'trestle author ssp-assemble -m my_ssp -o ssp_json'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    ssp_json_path = tmp_trestle_dir / 'system-security-plans/ssp_json/system-security-plan.json'
    profile_path = tmp_trestle_dir / 'profiles/main_profile/profile.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, str(ssp_json_path))
    ssp_obj, parent_alias = fetcher.get_oscal(True)

    resolved_catalog = profile_resolver.ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)

    ssp_io = SSPMarkdownWriter(tmp_trestle_dir)
    ssp_io.set_catalog(resolved_catalog)
    ssp_io.set_ssp(ssp_obj)

    md_text = ssp_io.get_control_response('ac-1', 1, True)
    assert md_text
    tree = MarkdownNode.build_tree_from_markdown(md_text.split('\n'))

    assert tree.get_node_for_key('## Part a.')
    assert tree.get_node_for_key('## Part c.')
    assert len(list(tree.get_all_headers_for_level(2))) == 3

    md_text = ssp_io.get_control_response('ac-1', 2, False)
    tree = MarkdownNode.build_tree_from_markdown(md_text.split('\n'))

    assert tree.get_node_for_key('### Part a.')
    assert tree.get_node_for_key('### Part c.')
    assert len(list(tree.get_all_headers_for_level(3))) == 3


def test_writers(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test individual writers."""
    ssp_io = SSPMarkdownWriter(tmp_trestle_dir)
    output = ssp_io._write_list_with_header('Empty body', [], 2)
    assert not output

    output = ssp_io._write_list_with_header('Sample list', ['1', '2', '3'], 2)
    tree = MarkdownNode.build_tree_from_markdown(output.split('\n'))
    node = tree.get_node_for_key('### Sample list')
    assert node
    assert node.content.text == ['', '- 1', '', '- 2', '', '- 3']

    output = ssp_io._write_table_with_header('Empty table', [[]], ['c1', 'c2', 'c3'], 0)
    assert not output

    output = ssp_io._write_table_with_header('Sample table', [['1', '2', '3'], ['4', '5', '6']], ['c1', 'c2', 'c3'], 0)
    tree = MarkdownNode.build_tree_from_markdown(output.split('\n'))
    node = tree.get_node_for_key('# Sample table')
    assert node
    assert node.content.tables[0] == '| c1 | c2 | c3 |'
    assert node.content.tables[3] == '| 4 | 5 | 6 |'

    output = ssp_io._write_str_with_header('Empty text', '', 0)
    assert not output

    output = ssp_io._write_str_with_header('Some text', 'this is a text.', 5)
    tree = MarkdownNode.build_tree_from_markdown(output.split('\n'))
    node = tree.get_node_for_key('###### Some text')
    assert node
    assert node.content.raw_text == '###### Some text\n\nthis is a text.'
