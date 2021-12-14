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
"""Tests for trestle markdown_validator module."""
import pathlib

import frontmatter

import pytest

import trestle.core.const as const
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.markdown.markdown_node import MarkdownNode


@pytest.mark.parametrize('md_path', [(pathlib.Path('tests/data/markdown/valid_complex_md.md'))])
def test_tree_text_equal_to_md(md_path: pathlib.Path) -> None:
    """Test tree construction."""
    contents = frontmatter.loads(md_path.open('r', encoding=const.FILE_ENCODING).read())
    markdown_wo_header = contents.content
    lines = markdown_wo_header.split('\n')

    tree: MarkdownNode = MarkdownNode.build_tree_from_markdown(lines)
    assert markdown_wo_header == tree.content.raw_text


@pytest.mark.parametrize('md_path', [(pathlib.Path('tests/data/markdown/valid_complex_md.md'))])
def test_md_get_node_for_key(md_path: pathlib.Path) -> None:
    """Test node fetching."""
    contents = frontmatter.loads(md_path.open('r', encoding=const.FILE_ENCODING).read())
    markdown_wo_header = contents.content
    lines = markdown_wo_header.split('\n')

    tree: MarkdownNode = MarkdownNode.build_tree_from_markdown(lines)
    assert tree.get_node_for_key('header1') is None
    assert tree.get_node_for_key('nonexisting header') is None
    node: MarkdownNode = tree.get_node_for_key('# 2. MD Header 2 Blockquotes')
    assert node is not None
    # Assert returned node has content
    assert node.key == '# 2. MD Header 2 Blockquotes'
    assert len(node.content.blockquotes) == 2
    assert node.content.text[2] == 'some text after blockquote'
    # Assert unstrict and strict matching return same notes
    deep_node_unstrict = tree.get_node_for_key('5.2.2.1', strict_matching=False)
    deep_node_strict = tree.get_node_for_key('#### 5.2.2.1 A even deeper section here 2')
    assert deep_node_strict == deep_node_unstrict
    # Assert substrings are matched
    node = tree.get_node_for_key('Header 4 Tricky', strict_matching=False)
    assert node is not None
    # Assert first match returned if strict matching is off
    node = tree.get_node_for_key('5.1.1', strict_matching=False)
    assert node.key == '### 5.1.1 A deeper section 1'


@pytest.mark.parametrize('md_path', [(pathlib.Path('tests/data/markdown/valid_complex_md.md'))])
def test_md_content_is_correct(md_path: pathlib.Path) -> None:
    """Test that read content is correct."""
    contents = frontmatter.loads(md_path.open('r', encoding=const.FILE_ENCODING).read())
    markdown_wo_header = contents.content
    lines = markdown_wo_header.split('\n')

    tree: MarkdownNode = MarkdownNode.build_tree_from_markdown(lines)
    assert tree is not None
    assert len(tree.content.subnodes_keys) == 28
    assert tree.content.raw_text == markdown_wo_header
    assert tree.key == 'root'
    assert len(tree.content.blockquotes) == 5
    assert len(tree.content.tables) == 7
    assert len(tree.content.code_lines) == 12
    deep_node = tree.get_node_for_key('5.1.1.1.1', strict_matching=False)
    assert deep_node.content.text[1] == 'some very deep text'


@pytest.mark.parametrize('md_path', [(pathlib.Path('tests/data/markdown/valid_complex_md.md'))])
def test_md_headers_in_html_blocks_are_ignored(md_path: pathlib.Path) -> None:
    """Test that headers in the various html blocks are ignored."""
    contents = frontmatter.loads(md_path.open('r', encoding=const.FILE_ENCODING).read())
    markdown_wo_header = contents.content
    lines = markdown_wo_header.split('\n')

    tree: MarkdownNode = MarkdownNode.build_tree_from_markdown(lines)
    assert tree is not None
    tricky_node = tree.get_node_for_key('1.3', strict_matching=False)
    assert tricky_node.key == '## 1.3 MD Subheader 1.3 HTML'
    assert len(tricky_node.content.subnodes_keys) == 4
    assert len(tricky_node.content.html_lines) == 36


def test_modify_md_node_header_lvl(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test that header modification works."""
    markdown_file = testdata_dir / 'markdown/valid_levels_no_text.md'
    expected_file = testdata_dir / 'markdown/valid_levels_no_text_increased_level.md'
    md_api = MarkdownAPI()
    _, tree = md_api.processor.process_markdown(markdown_file)

    tree.change_header_level_by(1)

    _, tree_expected = md_api.processor.process_markdown(expected_file)
    assert tree_expected.content.raw_text == tree.content.raw_text
    assert tree_expected.content.text == tree.content.text
    assert len(list(tree.get_all_headers_for_level(1))) == len(list(tree_expected.get_all_headers_for_level(1)))
    assert len(list(tree.get_all_headers_for_level(2))) == len(list(tree_expected.get_all_headers_for_level(2)))
    assert len(list(tree.get_all_headers_for_level(3))) == len(list(tree_expected.get_all_headers_for_level(3)))
    assert tree.get_node_for_key('####### Header 3.2.1.1.1.1').content.raw_text == tree_expected.get_node_for_key(
        '####### Header 3.2.1.1.1.1'
    ).content.raw_text
    assert len(tree.get_node_for_key('## Header 3 a deeper tree').subnodes) == len(
        tree_expected.get_node_for_key('## Header 3 a deeper tree').subnodes
    )

    for key in tree_expected.content.subnodes_keys:
        node = tree.get_node_for_key(key)
        assert node is not None
        expected_node = tree_expected.get_node_for_key(key)
        assert node.content.raw_text == expected_node.content.raw_text
        assert len(node.subnodes) == len(expected_node.subnodes)

    tree.change_header_level_by(-1)

    _, tree_expected = md_api.processor.process_markdown(markdown_file)

    assert tree_expected.content.raw_text == tree.content.raw_text
    assert tree_expected.content.text == tree.content.text
    assert len(list(tree.get_all_headers_for_level(1))) == len(list(tree_expected.get_all_headers_for_level(1)))
    assert len(list(tree.get_all_headers_for_level(2))) == len(list(tree_expected.get_all_headers_for_level(2)))
    assert len(list(tree.get_all_headers_for_level(3))) == len(list(tree_expected.get_all_headers_for_level(3)))
    assert len(tree.get_node_for_key('# Header 3 a deeper tree').subnodes) == len(
        tree_expected.get_node_for_key('# Header 3 a deeper tree').subnodes
    )

    for key in tree_expected.content.subnodes_keys:
        node = tree.get_node_for_key(key)
        assert node is not None
        expected_node = tree_expected.get_node_for_key(key)
        assert node.content.raw_text == expected_node.content.raw_text
        assert len(node.subnodes) == len(expected_node.subnodes)


def test_modify_md_node_remove_restore_headers(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test that header modification works."""
    markdown_file = testdata_dir / 'markdown/valid_no_lvl1_headers.md'
    expected_file = testdata_dir / 'markdown/valid_no_headers.md'
    md_api = MarkdownAPI()
    _, tree = md_api.processor.process_markdown(markdown_file)

    tree.change_header_level_by(-99)

    _, tree_expected = md_api.processor.process_markdown(expected_file)

    assert tree_expected.content.raw_text == tree.content.raw_text
    assert len(list(tree.get_all_headers_for_level(1))) == len(list(tree_expected.get_all_headers_for_level(1)))
    assert len(list(tree.get_all_headers_for_level(2))) == len(list(tree_expected.get_all_headers_for_level(2)))
    assert len(list(tree.get_all_headers_for_level(3))) == len(list(tree_expected.get_all_headers_for_level(3)))

    tree.change_header_level_by(4)

    assert len(list(tree.get_all_headers_for_level(4))) == 14


def test_modify_subtree(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test modification of the subtree."""
    markdown_file = testdata_dir / 'markdown/valid_no_lvl1_headers.md'
    md_api = MarkdownAPI()
    _, tree = md_api.processor.process_markdown(markdown_file)

    assert tree.get_node_header_lvl() is None

    subtree = tree.get_node_for_key('## Header root child 2')

    subtree.change_header_level_by(-1)

    assert len(subtree.content.subnodes_keys) == 10
    assert subtree.key == '# Header root child 2'
    assert len(list(subtree.get_all_headers_for_level(2))) == 2
    assert len(list(subtree.get_all_headers_for_level(3))) == 4
    assert len(list(subtree.get_all_headers_for_level(4))) == 4
    assert subtree.get_node_header_lvl() == 1
