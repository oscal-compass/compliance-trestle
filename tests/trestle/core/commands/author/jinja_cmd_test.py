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
"""Tests for Jinja command."""
import os
import pathlib
import shutil

from _pytest.monkeypatch import MonkeyPatch

from tests.test_utils import execute_command_and_assert, setup_for_ssp

from trestle.core.commands.author.jinja import _number_captions
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.markdown.markdown_node import MarkdownNode


def test_jinja_ssp_output(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test Jinja SSP output."""
    input_template = 'ssp_template.md.jinja'

    args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, 'main_profile', 'my_ssp')
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    command_ssp_gen = 'trestle author ssp-assemble -m my_ssp -o ssp_json'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    for file_name in os.listdir(testdata_dir / 'jinja'):
        full_file_name = os.path.join(testdata_dir / 'jinja', file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, tmp_trestle_dir)

    command_import = f'trestle author jinja -i {input_template} -o output_file.md -ssp ssp_json -p main_profile'
    execute_command_and_assert(command_import, 0, monkeypatch)

    with open('output_file.md') as test_output:
        output = test_output.read()
        tree = MarkdownNode.build_tree_from_markdown(output.split('\n'))
        assert tree
        node1 = tree.get_node_for_key('# A')
        node2 = tree.get_node_for_key('# C')
        assert node1.subnodes[0].key == node2.subnodes[0].key
        assert len(node1.subnodes) == len(node2.subnodes)


def test_jinja_lookup_table(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test Jinja lookup table substitions."""
    input_template = 'use_lookup_table.md.jinja'
    luk_table = 'lookup_table.yaml'
    args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, 'main_profile', 'my_ssp')
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    command_ssp_gen = 'trestle author ssp-assemble -m my_ssp -o ssp_json'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    for file_name in os.listdir(testdata_dir / 'jinja'):
        full_file_name = os.path.join(testdata_dir / 'jinja', file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, tmp_trestle_dir)
    command_import = f'trestle author jinja -i {input_template} -o output_file.md ' \
                     f'-lut {luk_table} -ssp ssp_json -p main_profile -elp lut.prefix'  # noqa: N400
    execute_command_and_assert(command_import, 0, monkeypatch)

    with open('output_file.md') as test_output:
        output = test_output.read()
        tree = MarkdownNode.build_tree_from_markdown(output.split('\n'))
        assert tree
        node1 = tree.get_node_for_key('### Substitutions')
        node2 = tree.get_node_for_key('# B')
        assert node1.content.text[1] == 'This word: compliance-trestle, was substituted.'
        assert node2.content.text


def test_number_captions(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test numbering of captions in markdown."""
    with open(testdata_dir / 'jinja_cmd/number_captions_data.md', 'r') as fp:
        test_data = fp.read()

    with open(testdata_dir / 'jinja_cmd/number_captions_expected_output.md', 'r') as fp:
        expected_output = fp.read().splitlines()

    for idx, row in enumerate(_number_captions(test_data).splitlines()):
        assert row == expected_output[idx]


def test_params_formatting(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that parameters are substituted with the given formatting."""
    input_template = 'ssp_template.md.jinja'

    args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, 'main_profile', 'my_ssp')
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    command_ssp_gen = 'trestle author ssp-assemble -m my_ssp -o ssp_json'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    for file_name in os.listdir(testdata_dir / 'jinja'):
        full_file_name = os.path.join(testdata_dir / 'jinja', file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, tmp_trestle_dir)

    command_md_gen = f'trestle author jinja -pf *.* -i {input_template} -o output.md -ssp ssp_json -p main_profile'
    execute_command_and_assert(command_md_gen, 0, monkeypatch)

    with open('output.md') as test_output:
        output = test_output.read()
        tree = MarkdownNode.build_tree_from_markdown(output.split('\n'))
        assert tree
        parent = tree.get_node_for_key('### AC-1 - Policy and Procedures')
        child1 = parent.get_node_for_key('#### AC-1 Summary information')
        child2 = parent.get_node_for_key('#### Control Statement')
        for i in range(0, len(child1.content.tables)):
            if i >= 2:
                cells = child1.content.tables[i].split('|')
                if len(cells) < 2:
                    continue
                value = cells[2].strip()
                is_found = False
                for line in child2.content.text:
                    if '*' + value + '*' in line:
                        is_found = True
                        break
                assert is_found

    command_md_gen = f'trestle author jinja -pf Prefix:. -i {input_template} -o output.md -ssp ssp_json -p main_profile'
    execute_command_and_assert(command_md_gen, 0, monkeypatch)

    with open('output.md') as test_output:
        output = test_output.read()
        tree = MarkdownNode.build_tree_from_markdown(output.split('\n'))
        assert tree
        parent = tree.get_node_for_key('### AC-1 - Policy and Procedures')
        child1 = parent.get_node_for_key('#### AC-1 Summary information')
        child2 = parent.get_node_for_key('#### Control Statement')
        for i in range(2, len(child1.content.tables)):
            cells = child1.content.tables[i].split('|')
            if len(cells) < 2:
                continue
            value = cells[2].strip()
            is_found = False
            for line in child2.content.text:
                if 'Prefix:' + value in line:
                    is_found = True
                    break
            assert is_found


def test_jinja_profile_docs(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test Jinja Profile to multiple md files output."""
    input_template = 'profile_to_docs.md.jinja'

    args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, 'main_profile', 'my_ssp')
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    command_ssp_gen = 'trestle author ssp-assemble -m my_ssp -o ssp_json'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    for file_name in os.listdir(testdata_dir / 'jinja'):
        full_file_name = os.path.join(testdata_dir / 'jinja', file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, tmp_trestle_dir)

    command_import = f'trestle author jinja -i {input_template} -o controls -p main_profile --docs-profile'
    execute_command_and_assert(command_import, 0, monkeypatch)

    for md_control in (tmp_trestle_dir / 'controls' / 'ac').iterdir():
        with open(md_control) as md_file:
            contents = md_file.read()
            tree = MarkdownNode.build_tree_from_markdown(contents.split('\n'))
            assert tree
            node1 = tree.get_node_for_key('# Control Page')
            assert node1
            node2 = tree.get_node_for_key('## Control Statement Header')
            assert node2


def test_jinja_profile_docs_fails(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test jinja docs generate fails."""
    input_template = 'profile_to_docs.md.jinja'

    args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, 'main_profile', 'my_ssp')
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    command_ssp_gen = 'trestle author ssp-assemble -m my_ssp -o ssp_json'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    for file_name in os.listdir(testdata_dir / 'jinja'):
        full_file_name = os.path.join(testdata_dir / 'jinja', file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, tmp_trestle_dir)

    command_jinja = f'trestle author jinja -i {input_template} -o controls --docs-profile'
    execute_command_and_assert(command_jinja, 2, monkeypatch)

    command_jinja = f'trestle author jinja -i {input_template} -o controls -ssp ssp_json -p main_profile --docs-profile'
    execute_command_and_assert(command_jinja, 2, monkeypatch)
