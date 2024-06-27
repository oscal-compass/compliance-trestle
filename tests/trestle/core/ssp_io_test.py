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

from tests.test_utils import execute_command_and_assert, setup_for_ssp, substitute_text_in_file

from trestle.common.const import CONTROL_ORIGINATION, IMPLEMENTATION_STATUS, STATUS_INHERITED, STATUS_PLANNED
from trestle.common.model_utils import ModelUtils
from trestle.core import profile_resolver
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_reader import ControlReader
from trestle.core.markdown.docs_markdown_node import DocsMarkdownNode
from trestle.core.models.file_content_type import FileContentType
from trestle.core.remote import cache
from trestle.core.ssp_io import SSPMarkdownWriter
from trestle.oscal.common import Property
from trestle.oscal.profile import Profile
from trestle.oscal.ssp import SystemSecurityPlan

prof_name = 'comp_prof'
ssp_name = 'my_ssp'


def setup_test(tmp_trestle_dir: pathlib.Path, testdata_dir: pathlib.Path,
               trestle_root: str) -> Tuple[pathlib.Path, SystemSecurityPlan]:
    """Prepare ssp test."""
    profile_path = tmp_trestle_dir / f'profiles/{prof_name}/profile.json'
    new_catalog_dir = tmp_trestle_dir / f'catalogs/{prof_name}_resolved_catalog'
    new_catalog_dir.mkdir(parents=True, exist_ok=True)

    ssp_json = testdata_dir / 'author/ssp/ssp_example.json'
    fetcher = cache.FetcherFactory.get_fetcher(trestle_root, str(ssp_json))
    ssp_obj: SystemSecurityPlan
    ssp_obj, parent_alias = fetcher.get_oscal(True)
    ssp_obj.control_implementation.implemented_requirements[0].props = [
        Property(name=IMPLEMENTATION_STATUS, value=STATUS_PLANNED),
        Property(name=CONTROL_ORIGINATION, value=STATUS_INHERITED),
    ]

    assert parent_alias == 'system-security-plan'

    return profile_path, ssp_obj


def test_ssp_writer(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp writer from cli."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)

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

    md_text2 = ssp_writer._parameter_table('ac-2', 1, True)
    assert md_text2
    assert '| Label or Choices |' in md_text2

    md_text3 = ssp_writer.get_fedramp_control_tables('ac-2', 1, 1)
    assert md_text3

    md_text4 = ssp_writer.get_control_part('ac-2', 'item', 1)
    assert md_text4


def test_ssp_get_control_response(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test generating SSP from the sample profile and generate markdown representation of it."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    ac1_path = tmp_trestle_dir / ssp_name / 'ac/ac-1.md'

    context = ControlContext.generate(ContextPurpose.SSP, True, tmp_trestle_dir, ssp_name)
    _, comp_dict = ControlReader.read_control_info_from_md(ac1_path, context)
    orig_imp_prose = 'imp req prose for ac-1 from comp aa'
    orig_a_prose = 'statement prose for part a. from comp aa'
    assert comp_dict['comp_aa'][''].prose == orig_imp_prose
    assert comp_dict['comp_aa']['a.'].prose == orig_a_prose

    command_ssp_assem = f'trestle author ssp-assemble -m my_ssp -o ssp_json -cd {args.compdefs}'
    execute_command_and_assert(command_ssp_assem, 0, monkeypatch)

    ssp_obj, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'ssp_json', SystemSecurityPlan, FileContentType.JSON)
    profile_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, prof_name, Profile, FileContentType.JSON
    )
    resolved_catalog = profile_resolver.ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    ssp_io = SSPMarkdownWriter(tmp_trestle_dir)
    ssp_io.set_catalog(resolved_catalog)
    ssp_io.set_ssp(ssp_obj)

    md_text = ssp_io.get_control_response('ac-1', 1, True, True, True)
    assert md_text
    tree = DocsMarkdownNode.build_tree_from_markdown(md_text.split('\n'))

    assert tree.get_node_for_key('## Implementation for part a.')
    assert len(list(tree.get_all_headers_for_level(2))) == 6
    assert len(list(tree.get_all_headers_for_level(3))) == 5

    md_text = ssp_io.get_control_response('ac-3', 1, True)
    assert md_text
    tree = DocsMarkdownNode.build_tree_from_markdown(md_text.split('\n'))

    # change responses
    new_imp_prose = 'edited imp req prose'
    new_a_prose = 'edited a prose'
    substitute_text_in_file(ac1_path, orig_imp_prose, new_imp_prose)
    substitute_text_in_file(ac1_path, orig_a_prose, new_a_prose)

    execute_command_and_assert(command_ssp_assem, 0, monkeypatch)
    ssp_obj, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, 'ssp_json', SystemSecurityPlan, FileContentType.JSON)
    profile_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, prof_name, Profile, FileContentType.JSON
    )
    resolved_catalog = profile_resolver.ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    ssp_io = SSPMarkdownWriter(tmp_trestle_dir)
    ssp_io.set_catalog(resolved_catalog)
    ssp_io.set_ssp(ssp_obj)

    # confirm edited response is there and that comp name presence is controlled
    md_text = ssp_io.get_control_response('ac-1', 1, False, False)
    assert 'comp_aa' not in md_text
    assert new_a_prose not in md_text

    md_text = ssp_io.get_control_response('ac-1', 1, False, True)
    assert 'comp_aa' in md_text
    assert new_a_prose in md_text
    assert '\n### Implementation Status: partial' in md_text


def test_writers(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test individual writers."""
    ssp_io = SSPMarkdownWriter(tmp_trestle_dir)
    output = ssp_io._write_list_with_header('Empty body', [], 2)
    assert not output

    output = ssp_io._write_list_with_header('Sample list', ['1', '2', '3'], 2)
    tree = DocsMarkdownNode.build_tree_from_markdown(output.split('\n'))
    node = tree.get_node_for_key('### Sample list')
    assert node
    assert node.content.text == ['', '- 1', '', '- 2', '', '- 3']

    output = ssp_io._write_table_with_header('Empty table', [[]], ['c1', 'c2', 'c3'], 0)
    assert not output

    output = ssp_io._write_table_with_header('Sample table', [['1', '2', '3'], ['4', '5', '6']], ['c1', 'c2', 'c3'], 0)
    tree = DocsMarkdownNode.build_tree_from_markdown(output.split('\n'))
    node = tree.get_node_for_key('# Sample table')
    assert node
    assert node.content.tables[0] == '| c1 | c2 | c3 |'
    assert node.content.tables[3] == '| 4 | 5 | 6 |'

    output = ssp_io._write_str_with_header('Empty text', '', 0)
    assert not output

    output = ssp_io._write_str_with_header('Some text', 'this is a text.', 5)
    tree = DocsMarkdownNode.build_tree_from_markdown(output.split('\n'))
    node = tree.get_node_for_key('###### Some text')
    assert node
    assert node.content.raw_text == '###### Some text\n\nthis is a text.'
