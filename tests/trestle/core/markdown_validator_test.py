# -*- mode:python; coding:utf-8 -*-

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
"""Tests for trestle markdown_validator module."""
import pathlib
from typing import Any, Dict

import pytest

import trestle.core.err as err
import trestle.core.markdown_validator as markdown_validator


def test_partition_ast() -> None:
    """Test whether partition_ast can execute correctly."""
    import mistune
    import pathlib
    import frontmatter
    test_data = pathlib.Path('tests/data/md/test_3_md_hand_edited/decisions_000.md')
    fm = frontmatter.loads(test_data.open('r').read())
    content = fm.content
    mistune_ast_parser = mistune.create_markdown(renderer=mistune.AstRenderer())
    parse = mistune_ast_parser(content)
    tree, index = markdown_validator.partition_ast(parse)
    tree


@pytest.mark.parametrize(
    'template_path, instance_path, status, header_validate',
    [
        (
            pathlib.Path('tests/data/md/test_1_md_format/template.md'),
            pathlib.Path('tests/data/md/test_1_md_format/correct_instance.md'),
            True,
            True
        ),
        (
            pathlib.Path('tests/data/md/test_1_md_format/template.md'),
            pathlib.Path('tests/data/md/test_1_md_format/correct_instance_extra_features.md'),
            True,
            True
        ),
        (
            pathlib.Path('tests/data/md/test_1_md_format/template.md'),
            pathlib.Path('tests/data/md/test_1_md_format/bad_instance_yaml_header_change.md'),
            False,
            True
        ),
        (
            pathlib.Path('tests/data/md/test_1_md_format/template.md'),
            pathlib.Path('tests/data/md/test_1_md_format/bad_instance_yaml_header_change.md'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/md/test_1_md_format/template.md'),
            pathlib.Path('tests/data/md/test_1_md_format/bad_instance_reordered.md'),
            False,
            False
        ),
        (
            pathlib.Path('tests/data/md/test_1_md_format/template.md'),
            pathlib.Path('tests/data/md/test_1_md_format/bad_instance_missing_heading.md'),
            False,
            False
        ),
        (
            pathlib.Path('tests/data/md/test_1_md_format/template.md'),
            pathlib.Path('tests/data/md/test_1_md_format/bad_instance_heading_wrong_type.md'),
            False,
            False
        ),
    ]
)
def test_md_validator_pass(
    template_path: pathlib.Path, instance_path: pathlib.Path, status: bool, header_validate: bool
) -> None:
    """Run markdown validator to expected outcome."""
    md_validator = markdown_validator.MarkdownValidator(template_path, header_validate)
    result = md_validator.validate(instance_path)
    assert result == status


def test_md_by_hand() -> None:
    """Simpler test to enable debugging."""
    template_path = pathlib.Path('tests/data/md/test_3_md_hand_edited/template.md')
    instance_path = pathlib.Path('tests/data/md/test_3_md_hand_edited/decisions_000.md')
    header_validate = False
    status = True
    md_validator = markdown_validator.MarkdownValidator(template_path, header_validate, 'Governed Document')
    result = md_validator.validate(instance_path)
    assert result == status


@pytest.mark.parametrize(
    'template_path, instance_path, status, yaml_header_validate',
    [
        (
            pathlib.Path('tests/data/md/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/md/test_2_md_with_md_header/instance.md'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/md/test_3_md_hand_edited/template.md'),
            pathlib.Path('tests/data/md/test_3_md_hand_edited/decisions_000.md'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/md/test_3_md_hand_edited/template.md'),
            pathlib.Path('tests/data/md/test_3_md_hand_edited/decisions_001.md'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/md/test_3_md_hand_edited/template.md'),
            pathlib.Path('tests/data/md/test_3_md_hand_edited/decisions_002.md'),
            True,
            False
        )
    ]
)
def test_md_validator_with_md_header(
    template_path: pathlib.Path, instance_path: pathlib.Path, status: bool, yaml_header_validate: bool
) -> None:
    """Test with validation of heading."""
    md_validator = markdown_validator.MarkdownValidator(template_path, yaml_header_validate, 'Governed Document')
    result = md_validator.validate(instance_path)
    assert result == status


def test_bad_file_path(tmp_path: pathlib.Path):
    """Check errors are thrown with bad files."""
    no_file = tmp_path / 'non_existent.md'
    with pytest.raises(err.TrestleError):
        _ = markdown_validator.MarkdownValidator(no_file, False)


@pytest.mark.parametrize(
    'template, candidate, expected_status',
    [
        ({
            'hello': {
                'world': 'stuff'
            }
        }, {
            'hello': {
                'world': 'banana'
            }
        }, True), ({
            'hello': {
                'world': 'stuff'
            }
        }, {
            'hello': {
                'banana': 'world'
            }
        }, False),
        ({
            'hello': {
                'world': 'stuff'
            }
        }, {
            'hello': {
                'world': ['results can be arrays with no restrictions']
            }
        }, True), ({
            'hello': 1,
            'world': 2,
        }, {
            'hello': 1,
            'my-world': 2,
        }, False)
    ]
)
def test_key_compare(template: Dict[str, Any], candidate: Dict[str, Any], expected_status):
    """Test key_compare behaves as expected."""
    status = markdown_validator.MarkdownValidator.compare_keys(template, candidate)
    assert status == expected_status


@pytest.mark.parametrize(
    'template_path, instance_path, status, governed_header',
    [
        (
            pathlib.Path('tests/data/md/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/md/test_2_md_with_md_header/instance.md'),
            True,
            'Governed Document'
        ),
        (
            pathlib.Path('tests/data/md/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/md/test_2_md_with_md_header/instance.md'),
            True,
            'Governed Document      '
        ),
        (
            pathlib.Path('tests/data/md/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/md/test_2_md_with_md_header/instance.md'),
            False,
            'Governed Documeent'
        ),
        (
            pathlib.Path('tests/data/md/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/md/test_2_md_with_md_header/bad_heading_content_changed_header.md'),
            False,
            'Governed Document'
        ),
        (
            pathlib.Path('tests/data/md/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/md/test_2_md_with_md_header/bad_heading_content_extra_lines.md'),
            False,
            'Governed Document'
        ),
        (
            pathlib.Path('tests/data/md/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/md/test_2_md_with_md_header/wrong_heading_title.md'),
            False,
            'Governed Document'
        )
    ]
)
def test_validate_for_governed_header(
    template_path: pathlib.Path, instance_path: pathlib.Path, status: bool, governed_header: str
) -> None:
    """Test scenarios for validate w.r.t the governed header."""
    md_validator = markdown_validator.MarkdownValidator(template_path, False, governed_header)
    result = md_validator.validate(instance_path)
    assert result == status


def test_compare_tree_force_failure():
    """Test unhappy path of compare_tree by manipulating content."""
    template_path = pathlib.Path('tests/data/md/test_1_md_format/template.md')
    header_validate = True
    md_validator = markdown_validator.MarkdownValidator(template_path, header_validate)
    ast_parse = markdown_validator.partition_ast(md_validator._template_parse)
    _ = md_validator.wrap_content(ast_parse)


def test_search_for_headings():
    """Test to search for headings and sub-headings."""
    pass
