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
"""Tests for trestle md command module."""
import pathlib
import sys
from unittest import mock

import pytest

import trestle.cli
import trestle.core.commands.md as md_


def test_cidd_success_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md cidd subcommand from the cli."""
    command = 'trestle md cidd'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_governed_docs_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md governed-docs subcommand."""
    command = 'trestle md governed-docs'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_governed_folders_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md governed-folders subcommand."""
    command = 'trestle md governed-folders'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_governed_projects_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md governed-projects subcommand."""
    command = 'trestle md governed-projects'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_partition_ast() -> None:
    """Test whether partition_ast can execute correctly."""
    import mistune
    import pathlib
    import frontmatter
    test_data = pathlib.Path('tests/data/md/test_1_md_format/correct_instance_extra_features.md')
    fm = frontmatter.loads(test_data.open('r').read())
    content = fm.content
    mistune_ast_parser = mistune.create_markdown(renderer=mistune.AstRenderer())
    parse = mistune_ast_parser(content)
    tree, index = md_.partition_ast(parse)


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
def test_md_validator_pass(template_path, instance_path, status, header_validate):
    """Run markdown validator to expected outcome."""
    md_validator = md_.MarkdownValidator(template_path, header_validate)
    result = md_validator.validate(instance_path)
    assert result == status


def test_md_by_hand():
    """Simpler test to enable debugging."""
    template_path = pathlib.Path('tests/data/md/test_1_md_format/template.md')
    instance_path = pathlib.Path('tests/data/md/test_1_md_format/correct_instance_extra_features.md')
    header_validate = False
    status = True
    md_validator = md_.MarkdownValidator(template_path, header_validate)
    result = md_validator.validate(instance_path)
    assert result == status
