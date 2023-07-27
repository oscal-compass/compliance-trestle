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

import trestle.common.const as const
import trestle.core.inheritance_writer as inheritancewriter
from trestle.core.markdown.markdown_api import MarkdownAPI

provided_uuid = '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'
provided_statement_desc = 'provided statement description'
resp_uuid = '4b34c68f-75fa-4b38-baf0-e50158c13ac2'
resp_statement_desc = 'resp statement description'
satisfied_statement_desc = 'satisfied statement description'


def test_write_inheritance_tree(tmp_path: pathlib.Path) -> None:
    """Test writing statements with both provided and responsibility."""
    statement_tree_path = tmp_path.joinpath('statement_tree.md')

    statement = inheritancewriter.StatementTree(provided_uuid, provided_statement_desc, resp_uuid, resp_statement_desc)

    statement.write_statement_md(statement_tree_path)

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_tree_path)
    assert tree is not None
    assert header[const.TRESTLE_LEVERAGING_COMP_TAG]['name'] == 'REPLACE_ME'
    assert header[const.TRESTLE_STATEMENT_TAG][const.PROVIDED_UUID] == provided_uuid
    assert header[const.TRESTLE_STATEMENT_TAG][const.RESPONSIBILITY_UUID] == resp_uuid

    # Confirm markdown content
    node = tree.get_node_for_key(const.PROVIDED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Provided Statement Description\n\nprovided statement description\n'
    node = tree.get_node_for_key(const.RESPONSIBILITY_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Responsibility Statement Description\n\nresp statement description\n'
    node = tree.get_node_for_key(const.SATISFIED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == (
        '# Satisfied Statement Description\n\n<!-- Use this section to explain '
        'how the inherited responsibility is being satisfied. -->\nREPLACE_ME'
    )


def test_write_inheritance_provided(tmp_path: pathlib.Path) -> None:
    """Test writing statements with only provided."""
    statement_provided_path = tmp_path.joinpath('statement_provided.md')

    statement = inheritancewriter.StatementProvided(provided_uuid, provided_statement_desc)

    statement.write_statement_md(statement_provided_path)

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_provided_path)
    assert tree is not None
    assert header[const.TRESTLE_LEVERAGING_COMP_TAG]['name'] == 'REPLACE_ME'
    assert header[const.TRESTLE_STATEMENT_TAG][const.PROVIDED_UUID] == provided_uuid

    # Confirm markdown content
    node = tree.get_node_for_key(const.PROVIDED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Provided Statement Description\n\nprovided statement description'


def test_write_inheritance_responsibility(tmp_path: pathlib.Path) -> None:
    """Test writing statements with only responsibility."""
    statement_resp_path = tmp_path.joinpath('statement_req.md')

    statement = inheritancewriter.StatementResponsibility(resp_uuid, resp_statement_desc)

    statement.write_statement_md(statement_resp_path)

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(statement_resp_path)
    assert tree is not None
    assert header[const.TRESTLE_LEVERAGING_COMP_TAG]['name'] == 'REPLACE_ME'
    assert header[const.TRESTLE_STATEMENT_TAG][const.RESPONSIBILITY_UUID] == resp_uuid

    # Confirm markdown content
    node = tree.get_node_for_key(const.RESPONSIBILITY_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == '# Responsibility Statement Description\n\nresp statement description\n'
    node = tree.get_node_for_key(const.SATISFIED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == """# Satisfied Statement Description\n
<!-- Use this section to explain how the inherited responsibility is being satisfied. -->
REPLACE_ME"""
