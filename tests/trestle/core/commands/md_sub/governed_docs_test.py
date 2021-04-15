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
"""Tests for trestle md governed-docs subcommand."""
import pathlib
import shutil
import sys
from unittest import mock
from uuid import uuid4

import pytest

import trestle.cli


@pytest.mark.parametrize(
    'command_string, return_code',
    [
        ('trestle md governed-docs setup', 1), ('trestle md governed-docs setup --task-name foobaa', 0),
        ('trestle md governed-docs setup --task-name catalogs', 1)
    ]
)
def test_governed_docs_high(tmp_trestle_dir: pathlib.Path, command_string: str, return_code: int) -> None:
    """Simple execution tests of trestle md governed-docs."""
    with mock.patch.object(sys, 'argv', command_string.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == return_code


@pytest.mark.parametrize(
    'task_name, template_content, target_content, setup_code, template_code, validate_code',
    [
        (
            'test_task',
            pathlib.Path('md/test_1_md_format/template.md'),
            pathlib.Path('md/test_1_md_format/correct_instance_extra_features.md'),
            0,
            0,
            0
        ),
        (
            'catalogs',
            pathlib.Path('md/test_1_md_format/template.md'),
            pathlib.Path('md/test_1_md_format/correct_instance_extra_features.md'),
            1,
            1,
            1,
        ),
        (
            'test_task',
            pathlib.Path('md/test_1_md_format/template.md'),
            pathlib.Path('md/test_1_md_format/bad_instance_missing_heading.md'),
            0,
            0,
            1
        ), (
            'test_task',
            pathlib.Path('md/utf16test/sample_okay.md'),
            pathlib.Path('md/utf16test/sample_utf16.md'),
            0,
            0,
            1
        ), (
            'test_task',
            pathlib.Path('md/utf16test/sample_utf16.md'),
            pathlib.Path('md/utf16test/sample_okay.md'),
            0,
            1,
            1
        )
    ]
)
def test_e2e(
    task_name: str,
    template_content: pathlib.Path,
    target_content: pathlib.Path,
    setup_code: bool,
    template_code: bool,
    validate_code: bool,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path
) -> None:
    """Run an E2E workflow with two test criteria for success."""
    # Note testdata_dir must be before tmp_trestle_dir in the argument order.
    command_string_setup = f'trestle md governed-docs setup -tn {task_name}'
    command_string_create_sample = f'trestle md governed-docs create-sample -tn {task_name}'
    command_string_validate_template = f'trestle md governed-docs template-validate -tn {task_name}'
    command_string_validate_content = f'trestle md governed-docs validate -tn {task_name} --header-validate'
    template_target_loc = tmp_trestle_dir / '.trestle' / 'md' / task_name / 'template.md'
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}.md'
    # Test setup
    with mock.patch.object(sys, 'argv', command_string_setup.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == setup_code
    if setup_code > 0:
        return

    # Copy in template:
    shutil.copyfile(str(testdata_dir / template_content), str(template_target_loc))

    with mock.patch.object(sys, 'argv', command_string_validate_template.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == template_code
    if template_code > 0:
        return
    # Create sample - should always work if we are here.
    with mock.patch.object(sys, 'argv', command_string_create_sample.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 0

    shutil.copyfile(str(testdata_dir / target_content), str(test_content_loc))
    with mock.patch.object(sys, 'argv', command_string_validate_content.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == validate_code


def test_failure_bad_template_dir(tmp_trestle_dir: pathlib.Path) -> None:
    """Create and test a bad directory."""
    setup_ = 'trestle md governed-docs setup --task-name foobaa'

    bad_template_sub_directory = tmp_trestle_dir / '.trestle' / 'md' / 'foobar' / 'test'
    bad_template_sub_directory.mkdir(parents=True, exist_ok=True)
    with mock.patch.object(sys, 'argv', setup_.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_success_repeated_call(tmp_trestle_dir: pathlib.Path) -> None:
    """Test double setup."""
    setup_ = 'trestle md governed-docs setup --task-name foobaa'

    with mock.patch.object(sys, 'argv', setup_.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 0
    with mock.patch.object(sys, 'argv', setup_.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 0
