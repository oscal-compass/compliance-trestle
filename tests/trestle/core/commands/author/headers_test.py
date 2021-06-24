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
"""Tests for trestle author headers command."""

import pathlib
import shutil
import sys
from unittest import mock
from uuid import uuid4

import pytest

import trestle.cli


@pytest.mark.parametrize(
    'task_name, template_path, content_path, setup_rc, template_validate_rc, validate_rc',
    [
        ('catalogs', pathlib.Path('irrelevant'), pathlib.Path('irrelevant_2'), 1, 1, 1),
        (
            'test_tasks_1',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/meets_templates'),
            0,
            0,
            0
        ),
        (
            'test_tasks_2',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            0,
            0,
            0
        ),
        (
            'test_tasks_3',
            pathlib.Path('author/headers/bad_templates_drawio'),
            pathlib.Path('author/headers/recursive_pass'),
            0,
            1,
            1
        ),
        (
            'test_tasks_4',
            pathlib.Path('author/headers/bad_templates_wrong_names'),
            pathlib.Path('author/headers/recursive_pass'),
            0,
            1,
            1
        ),
        (
            'test_tasks_5',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_drawio'),
            0,
            0,
            1
        ),
        (
            'test_tasks_6',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_drawio_bad_file'),
            0,
            0,
            1
        ),
        (
            'test_tasks_7',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_md'),
            0,
            0,
            1
        ),
        (
            'test_tasks_8',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_md_bad_file'),
            0,
            0,
            1
        ),
        (
            'test_tasks_9',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/passes_with_extraneous_files'),
            0,
            0,
            0
        ),
        (
            'test_tasks_10',
            pathlib.Path('author/headers/bad_templates_md'),
            pathlib.Path('author/headers/passes_with_extraneous_files'),
            0,
            1,
            1
        )
    ]
)
def test_e2e(
    task_name: str,
    template_path: pathlib.Path,
    content_path: pathlib.Path,
    setup_rc: int,
    template_validate_rc: int,
    validate_rc: int,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path
) -> None:
    """Run an E2E workflow with a number of test criteria."""
    command_string_setup = f'trestle author headers setup -tn {task_name}'
    command_string_create_sample = f'trestle author headers create-sample -tn {task_name}'
    command_string_validate_template = f'trestle author headers template-validate -tn {task_name}'
    command_string_validate_content = f'trestle author headers validate -tn {task_name} -r'
    template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}'
    with mock.patch.object(sys, 'argv', command_string_setup.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == setup_rc
    if setup_rc > 0:
        return
    shutil.rmtree(str(template_target_loc))
    shutil.copytree(str(testdata_dir / template_path), str(template_target_loc))

    with mock.patch.object(sys, 'argv', command_string_validate_template.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == template_validate_rc
    if template_validate_rc > 0:
        return

    # Create sample - should always work if we are here.
    with mock.patch.object(sys, 'argv', command_string_create_sample.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 0

    shutil.copytree(str(testdata_dir / content_path), str(test_content_loc))
    with mock.patch.object(sys, 'argv', command_string_validate_content.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == validate_rc


def test_abort_safely_on_missing_directory(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test that validation fails cleanly on a missing directory."""
    task_name = 'tester'
    command_string_setup = f'trestle author headers setup -tn {task_name}'
    command_string_validate_content = f'trestle author headers validate -tn {task_name} -r'
    task_dir = tmp_trestle_dir / task_name
    with mock.patch.object(sys, 'argv', command_string_setup.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 0
    shutil.rmtree(str(task_dir))

    with mock.patch.object(sys, 'argv', command_string_validate_content.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 1


def test_taskpath_is_a_file(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test that validation fails cleanly on a missing directory."""
    task_name = 'tester'
    command_string_setup = f'trestle author headers setup -tn {task_name}'
    command_string_validate_content = f'trestle author headers validate -tn {task_name} -r'
    task_dir = tmp_trestle_dir / task_name
    with mock.patch.object(sys, 'argv', command_string_setup.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 0
    shutil.rmtree(str(task_dir))

    task_dir.touch()

    with mock.patch.object(sys, 'argv', command_string_validate_content.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 1
