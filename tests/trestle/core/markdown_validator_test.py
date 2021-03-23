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

import pytest

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
        )
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
