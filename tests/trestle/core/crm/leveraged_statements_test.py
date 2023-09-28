# -*- mode:python; coding:utf-8 -*-

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
"""Tests for control input output methods."""

import pathlib
from typing import Any, Dict

import trestle.common.const as const
from trestle.core.crm.leveraged_statements import (
    InheritanceMarkdownReader, StatementProvided, StatementResponsibility, StatementTree
)
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.markdown.md_writer import MDWriter

provided_uuid = '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'
provided_statement_desc = 'provided statement description'
resp_uuid = '4b34c68f-75fa-4b38-baf0-e50158c13ac2'
resp_statement_desc = 'resp statement description'
satisfied_statement_desc = 'satisfied statement description'

test_href = 'trestle://ssp/ssp.json'


def add_authored_content(test_file: pathlib.Path, yaml_header: Dict[str, Any]) -> None:
    """Update the yaml header with a test component and satisfied description to simulate editing."""
    md_writer = MDWriter(test_file)
    yaml_header[const.TRESTLE_LEVERAGING_COMP_TAG] = [{'name': 'My_Comp'}]
    md_writer.add_yaml_header(yaml_header)
    md_writer.new_header(level=1, title=const.SATISFIED_STATEMENT_DESCRIPTION)
    md_writer.new_line(const.SATISFIED_STATEMENT_COMMENT)
    md_writer.new_line('My Satisfied Description')
    md_writer.write_out()


def test_write_inheritance_tree(tmp_path: pathlib.Path) -> None:
    """Test writing statements with both provided and responsibility."""
    statement_tree_path = tmp_path.joinpath('statement_tree.md')

    statement = StatementTree(provided_uuid, provided_statement_desc, resp_uuid, resp_statement_desc, test_href)

    statement.write_statement_md(statement_tree_path)

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_tree_path)
    assert tree is not None

    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'REPLACE_ME'}]

    assert header[const.TRESTLE_STATEMENT_TAG][const.PROVIDED_UUID] == provided_uuid
    assert header[const.TRESTLE_STATEMENT_TAG][const.RESPONSIBILITY_UUID] == resp_uuid
    assert header[const.TRESTLE_GLOBAL_TAG][const.LEVERAGED_SSP][const.HREF] == test_href

    # Confirm markdown content
    node = tree.get_node_for_key(const.PROVIDED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Provided Statement Description\n\nprovided statement description\n'
    node = tree.get_node_for_key(const.RESPONSIBILITY_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Responsibility Statement Description\n\nresp statement description\n'
    node = tree.get_node_for_key(const.SATISFIED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == (
        '# Satisfied Statement Description\n\n<!-- Use this section to explain '
        'how the inherited responsibility is being satisfied. -->'
    )

    # Update the component mapping and run again to make sure it persists
    add_authored_content(statement_tree_path, header)

    statement.write_statement_md(statement_tree_path)

    # Reread the Markdown
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_tree_path)

    # Ensure My_Comp and satisfied description persists
    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'My_Comp'}]
    node = tree.get_node_for_key(const.SATISFIED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == """# Satisfied Statement Description\n
<!-- Use this section to explain how the inherited responsibility is being satisfied. -->\nMy Satisfied Description"""


def test_write_inheritance_provided(tmp_path: pathlib.Path) -> None:
    """Test writing statements with only provided."""
    statement_provided_path = tmp_path.joinpath('statement_provided.md')

    statement = StatementProvided(provided_uuid, provided_statement_desc, test_href)

    statement.write_statement_md(statement_provided_path)

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_provided_path)
    assert tree is not None

    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'REPLACE_ME'}]

    assert header[const.TRESTLE_STATEMENT_TAG][const.PROVIDED_UUID] == provided_uuid
    assert header[const.TRESTLE_GLOBAL_TAG][const.LEVERAGED_SSP][const.HREF] == test_href

    # Confirm markdown content
    node = tree.get_node_for_key(const.PROVIDED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Provided Statement Description\n\nprovided statement description'

    # Update the component mapping and run again to make sure it persists
    add_authored_content(statement_provided_path, header)

    statement.write_statement_md(statement_provided_path)

    # Reread the markdown
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_provided_path)

    # Ensure My_Comp persists
    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'My_Comp'}]
    node = tree.get_node_for_key(const.SATISFIED_STATEMENT_DESCRIPTION, False)
    assert node is None


def test_write_inheritance_responsibility(tmp_path: pathlib.Path) -> None:
    """Test writing statements with only responsibility."""
    statement_resp_path = tmp_path.joinpath('statement_req.md')

    statement = StatementResponsibility(resp_uuid, resp_statement_desc, test_href)

    statement.write_statement_md(statement_resp_path)

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_resp_path)
    assert tree is not None

    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'REPLACE_ME'}]

    assert header[const.TRESTLE_STATEMENT_TAG][const.RESPONSIBILITY_UUID] == resp_uuid
    assert header[const.TRESTLE_GLOBAL_TAG][const.LEVERAGED_SSP][const.HREF] == test_href

    # Confirm markdown content
    node = tree.get_node_for_key(const.RESPONSIBILITY_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Responsibility Statement Description\n\nresp statement description\n'
    node = tree.get_node_for_key(const.SATISFIED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == """# Satisfied Statement Description\n
<!-- Use this section to explain how the inherited responsibility is being satisfied. -->"""

    # Update the component mapping and run again to make sure it persists
    add_authored_content(statement_resp_path, header)

    statement.write_statement_md(statement_resp_path)

    # Reread the Markdown
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_resp_path)

    # Ensure My_Comp and satisfied description persists
    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'My_Comp'}]
    node = tree.get_node_for_key(const.SATISFIED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == """# Satisfied Statement Description\n
<!-- Use this section to explain how the inherited responsibility is being satisfied. -->\nMy Satisfied Description"""


def test_process_leveraged_statement_default_mapping(tmp_path: pathlib.Path) -> None:
    """Test processing leveraged statement markdown with no set mapping."""
    statement_tree_path = tmp_path.joinpath('statement_tree.md')

    statement = StatementTree(provided_uuid, provided_statement_desc, resp_uuid, resp_statement_desc, test_href)

    statement.write_statement_md(statement_tree_path)

    md_reader: InheritanceMarkdownReader = InheritanceMarkdownReader(statement_tree_path)

    leveraging_information = md_reader.process_leveraged_statement_markdown()

    assert leveraging_information is None


def test_process_leveraged_statement_markdown_tree(tmp_path: pathlib.Path) -> None:
    """Test processing a statement tree in Markdown."""
    statement_tree_path = tmp_path.joinpath('statement_tree.md')

    # Add test mapped component
    test_header: Dict[str, Any] = {}
    add_authored_content(statement_tree_path, test_header)

    statement = StatementTree(provided_uuid, provided_statement_desc, resp_uuid, resp_statement_desc, test_href)

    statement.write_statement_md(statement_tree_path)

    md_reader: InheritanceMarkdownReader = InheritanceMarkdownReader(statement_tree_path)

    leveraging_information = md_reader.process_leveraged_statement_markdown()

    assert leveraging_information

    assert 'My_Comp' in leveraging_information.leveraging_comp_titles

    assert leveraging_information.inherited is not None
    inherited = leveraging_information.inherited
    assert inherited.provided_uuid == provided_uuid
    assert inherited.description == provided_statement_desc

    assert leveraging_information.satisfied is not None
    satisfied = leveraging_information.satisfied
    assert satisfied.responsibility_uuid == resp_uuid
    assert satisfied.description == 'My Satisfied Description'


def test_process_leveraged_statement_markdown_provided(tmp_path: pathlib.Path) -> None:
    """Test processing a statement provided markdown."""
    statement_provided_path = tmp_path.joinpath('statement_provided.md')

    # Add test mapped component
    test_header: Dict[str, Any] = {}
    add_authored_content(statement_provided_path, test_header)

    statement = StatementProvided(provided_uuid, provided_statement_desc, test_href)

    statement.write_statement_md(statement_provided_path)

    md_reader: InheritanceMarkdownReader = InheritanceMarkdownReader(statement_provided_path)

    leveraging_information = md_reader.process_leveraged_statement_markdown()

    assert leveraging_information

    assert 'My_Comp' in leveraging_information.leveraging_comp_titles

    assert leveraging_information.inherited is not None
    inherited = leveraging_information.inherited
    assert inherited.provided_uuid == provided_uuid
    assert inherited.description == provided_statement_desc

    assert leveraging_information.satisfied is None


def test_process_leveraged_statement_markdown_responsibility(tmp_path: pathlib.Path) -> None:
    """Test processing a statement responsibility Markdown."""
    statement_resp_path = tmp_path.joinpath('statement_req.md')

    # Add test mapped component
    test_header: Dict[str, Any] = {}
    add_authored_content(statement_resp_path, test_header)

    statement = StatementResponsibility(resp_uuid, resp_statement_desc, test_href)

    statement.write_statement_md(statement_resp_path)

    md_reader: InheritanceMarkdownReader = InheritanceMarkdownReader(statement_resp_path)

    leveraging_information = md_reader.process_leveraged_statement_markdown()

    assert leveraging_information

    assert 'My_Comp' in leveraging_information.leveraging_comp_titles

    assert leveraging_information.inherited is None

    assert leveraging_information.satisfied is not None
    satisfied = leveraging_information.satisfied
    assert satisfied.responsibility_uuid == resp_uuid
    assert satisfied.description == 'My Satisfied Description'
