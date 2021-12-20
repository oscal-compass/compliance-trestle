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
