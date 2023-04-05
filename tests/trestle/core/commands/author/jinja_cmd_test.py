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
from trestle.core.markdown.docs_markdown_node import DocsMarkdownNode


def setup_ssp(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch):
    """Prepare repository for docs generation."""
    args, _ = setup_for_ssp(tmp_trestle_dir, 'comp_prof', 'my_ssp')
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    command_ssp_assem = f'trestle author ssp-assemble -m my_ssp -o ssp_json -cd {args.compdefs} -vv'
    execute_command_and_assert(command_ssp_assem, 0, monkeypatch)

    for file_name in os.listdir(testdata_dir / 'jinja'):
        full_file_name = os.path.join(testdata_dir / 'jinja', file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, tmp_trestle_dir)


def test_jinja_ssp_output(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test Jinja SSP output."""
    input_template = 'ssp_template.md.jinja'
    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)
    command_import = f'trestle author jinja -i {input_template} -o output_file.md -ssp ssp_json -p comp_prof'
    execute_command_and_assert(command_import, 0, monkeypatch)

    with open('output_file.md') as test_output:
        output = test_output.read()
        tree = DocsMarkdownNode.build_tree_from_markdown(output.split('\n'))
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
    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)
    command_import = f'trestle author jinja -i {input_template} -o output_file.md ' \
                     f'-lut {luk_table} -ssp ssp_json -p comp_prof -elp lut.prefix'  # noqa: N400
    execute_command_and_assert(command_import, 0, monkeypatch)

    with open('output_file.md') as test_output:
        output = test_output.read()
        tree = DocsMarkdownNode.build_tree_from_markdown(output.split('\n'))
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

    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)

    command_md_gen = f'trestle author jinja -bf *.* -vap "IBM Assignment:" -vnap "Assignment:" -i {input_template} -o output.md -ssp ssp_json -p comp_prof'  # noqa E501
    execute_command_and_assert(command_md_gen, 0, monkeypatch)

    with open('output.md') as test_output:
        output = test_output.read()
        tree = DocsMarkdownNode.build_tree_from_markdown(output.split('\n'))
        assert tree
        parent = tree.get_node_for_key('### AC-1 - Policy and Procedures')
        child1 = parent.get_node_for_key('#### AC-1 Summary information')
        assert child1
        child2 = parent.get_node_for_key('#### Control Statement')
        assert '*Assignment: organization-defined official*' in child2.content.raw_text

    command_md_gen = f'trestle author jinja -bf Prefix:[.] -vap "IBM Assignment:" -vnap "Assignment:" -i {input_template} -o output.md -ssp ssp_json -p comp_prof'  # noqa E501
    execute_command_and_assert(command_md_gen, 0, monkeypatch)

    with open('output.md') as test_output:
        output = test_output.read()
        tree = DocsMarkdownNode.build_tree_from_markdown(output.split('\n'))
        assert tree
        parent = tree.get_node_for_key('### AC-1 - Policy and Procedures')
        child1 = parent.get_node_for_key('#### AC-1 Summary information')
        child2 = parent.get_node_for_key('#### Control Statement')
        assert child1
        assert 'Prefix:[Assignment: organization-defined official]' in child2.content.raw_text


def test_jinja_profile_docs(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test Jinja Profile to multiple md files output."""
    input_template = 'profile_to_docs.md.jinja'

    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)

    command_import = f'trestle author jinja -i {input_template} -o controls -p comp_prof --docs-profile'
    execute_command_and_assert(command_import, 0, monkeypatch)

    for md_control in (tmp_trestle_dir / 'controls' / 'ac').iterdir():
        with open(md_control) as md_file:
            contents = md_file.read()
            tree = DocsMarkdownNode.build_tree_from_markdown(contents.split('\n'))
            assert tree
            node1 = tree.get_node_for_key('# Control Page')
            assert node1
            node2 = tree.get_node_for_key('## Statement Header')
            assert node2
            if md_control.name == 'ac-1.md':
                node3 = tree.get_node_for_key('## Implementation Guidance')
                assert node3

                node4 = tree.get_node_for_key('# AC-1 - Policy and Procedures')
                assert node4.get_node_for_key('## Implementation Guidance')


def test_jinja_profile_docs_with_group_title(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test Jinja Profile to multiple md files output with group title."""
    input_template = 'profile_to_docs_with_group_title.md.jinja'

    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)

    command_import = f'trestle author jinja -i {input_template} -o controls -p comp_prof --docs-profile'
    execute_command_and_assert(command_import, 0, monkeypatch)

    md_control = tmp_trestle_dir / 'controls' / 'ac' / 'ac-1.md'
    with open(md_control) as md_file:
        contents = md_file.read()
        tree = DocsMarkdownNode.build_tree_from_markdown(contents.split('\n'))
        assert tree
        node1 = tree.get_node_for_key('# Control Page')
        assert node1
        node2 = tree.get_node_for_key('# AC-1 - \\[Access Control\\] Policy and Procedures')
        assert node2
        assert '{: #ac-1}' in node2.content.raw_text  # noqa: FS003 - not f string but tag
        assert node2.content.text[1] == ''  # assert new line after tag
        node3 = tree.get_node_for_key('## Table of Control Parameters')
        assert node3
        assert '{: #table-of-control-parameters}' in node3.content.raw_text  # noqa: FS003 - not f string but tag
        assert '{: #"Parameters for AC-1" caption-side="top"}' in node3.content.raw_text  # noqa: FS003 - not f string
        assert 'AC-1 (a) (1)' in node3.content.tables[2]
        assert 'ac-1_prm_3' in node3.content.tables[4]


def test_jinja_profile_docs_with_selected_sections(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test Jinja Profile to multiple md files output with group title."""
    input_template = 'profile_to_docs_only_some_sections.md.jinja'

    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)

    command_import = f'trestle author jinja -i {input_template} -o controls -p comp_prof --docs-profile'
    execute_command_and_assert(command_import, 0, monkeypatch)

    md_control = tmp_trestle_dir / 'controls' / 'ac' / 'ac-1.md'
    with open(md_control) as md_file:
        contents = md_file.read()
        tree = DocsMarkdownNode.build_tree_from_markdown(contents.split('\n'))
        assert tree
        node1 = tree.get_node_for_key('# Control Page')
        assert node1
        node2 = tree.get_node_for_key('## Control Statement Header')
        assert node2
        assert '{: #control-statement-header}' in node2.content.raw_text  # noqa: FS003 - not f string but tag
        assert len(tree.content.subnodes_keys) == 3


def test_jinja_profile_docs_with_selected_sections_and_multiple_parts(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test Jinja Profile to multiple md files output with selected sections and multiple subparts."""
    input_template = 'profile_to_docs_with_subparts.md.jinja'
    profile_path = testdata_dir / 'json/profile_with_alter_subparts.json'

    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)

    command_import = f'trestle import -f {profile_path} -o myprofile'
    execute_command_and_assert(command_import, 0, monkeypatch)

    command_jinja = f'trestle author jinja -i {input_template} -o controls -p myprofile --docs-profile'
    execute_command_and_assert(command_jinja, 0, monkeypatch)

    md_control = tmp_trestle_dir / 'controls' / 'ac' / 'ac-1.md'
    with open(md_control) as md_file:
        contents = md_file.read()
        tree = DocsMarkdownNode.build_tree_from_markdown(contents.split('\n'))
        assert tree
        node1 = tree.get_node_for_key('## The above the line guidance')
        assert node1
        node2 = tree.get_node_for_key('### Add to part a')
        assert node2
        node3 = tree.get_node_for_key('#### Evidence Guidance')
        assert node3
        tag = '{: #the-above-the-line-guidance-add-to-part-a-evidence-guidance}'  # noqa: FS003
        assert tag in node2.content.raw_text
        assert len(tree.content.subnodes_keys) == 7


def test_jinja_profile_docs_fails(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test jinja docs generate fails."""
    input_template = 'profile_to_docs.md.jinja'

    setup_ssp(testdata_dir, tmp_trestle_dir, monkeypatch)

    command_jinja = f'trestle author jinja -i {input_template} -o controls --docs-profile'
    execute_command_and_assert(command_jinja, 2, monkeypatch)

    command_jinja = f'trestle author jinja -i {input_template} -o controls -ssp ssp_json -p main_profile --docs-profile'
    execute_command_and_assert(command_jinja, 2, monkeypatch)

    input_template = 'profile_to_docs_invalid.md.jinja'
    command_jinja = f'trestle author jinja -i {input_template} -o controls -p main_profile --docs-profile'
    execute_command_and_assert(command_jinja, 1, monkeypatch)
