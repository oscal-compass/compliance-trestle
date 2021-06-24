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
"""Tests for trestle author folders subcommand."""
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
        ('trestle author folders setup', 2), ('trestle author folders setup --task-name foobaa', 0),
        ('trestle author folders setup --task-name catalogs', 1)
    ]
)
def test_governed_folders_high(tmp_trestle_dir: pathlib.Path, command_string: str, return_code: int) -> None:
    """Simple execution tests of trestle author folders."""
    with mock.patch.object(sys, 'argv', command_string.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == return_code


@pytest.mark.parametrize(
    'task_name, template_content, target_content, setup_code, template_code, validate_code, readme_validate',
    [
        (
            'test_task',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/good_instance'),
            0,
            0,
            0,
            False
        ),
        (
            'catalogs',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/good_instance'),
            1,
            1,
            1,
            False
        ),
        (
            'another_test_task/with_a_sub_dir',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/good_instance_limits_of_changes'),
            0,
            0,
            0,
            False
        ),
        (
            'another_test_task/with_a_sub_dir',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/bad_instance_renamed'),
            0,
            0,
            1,
            False
        ),
        (
            'another_test_task/with_a_sub_dir',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/bad_instance_mixed_name'),
            0,
            0,
            1,
            False
        ),
        (
            'another_test_task/with_a_sub_dir',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/bad_instance_missing'),
            0,
            0,
            1,
            False
        ),
        (
            'another_test_task/with_a_sub_dir',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/bad_instance_bad_content'),
            0,
            0,
            1,
            False
        ),
        (
            'another_test_task_1',
            pathlib.Path('author/governed_folders/utf16test_good'),
            pathlib.Path('author/governed_folders/utf16test_bad'),
            0,
            0,
            1,
            False
        ),
        (
            'another_test_task_2',
            pathlib.Path('author/governed_folders/utf16test_bad'),
            pathlib.Path('author/governed_folders/utf16test_good'),
            0,
            1,
            1,
            False
        ),
        (
            'another_test_task_3',
            pathlib.Path('author/governed_folders/template_with_readme'),
            pathlib.Path('author/governed_folders/good_instance_with_readme'),
            0,
            1,
            1,
            False
        ),
        (
            'another_test_task_4',
            pathlib.Path('author/governed_folders/template_with_readme'),
            pathlib.Path('author/governed_folders/good_instance_with_readme'),
            0,
            0,
            0,
            True
        ),
        (
            'another_test_task_5',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/good_instance_with_readme'),
            0,
            0,
            0,
            False
        ),
        # Note this will pass as templates are permissive to allow extra files
        # (e.g. it validates what people want to be validated and not supplementary assets)
        (
            'another_test_task_6',
            pathlib.Path('author/governed_folders/template_folder'),
            pathlib.Path('author/governed_folders/good_instance_with_readme'),
            0,
            0,
            0,
            True
        ),
        (
            'another_test_task_7',
            pathlib.Path('author/governed_folders/template_with_readme'),
            pathlib.Path('author/governed_folders/good_instance'),
            0,
            0,
            1,
            True
        ),
        (
            'another_test_task_8',
            pathlib.Path('author/governed_folders/template_with_readme'),
            pathlib.Path('author/governed_folders/good_instance'),
            0,
            1,
            1,
            False
        ),
        (
            'another_test_task_9',
            pathlib.Path('author/governed_folders/template_folder_with_drawio'),
            pathlib.Path('author/governed_folders/bad_folder_is_a_file'),
            0,
            0,
            0,  # this passes as random extra files are allowed there. This should be looked at.
            True
        ),
        (
            'another_test_task_10',
            pathlib.Path('author/governed_folders/bad_folder_is_a_file'),
            pathlib.Path('author/governed_folders/good_instance'),
            0,
            1,
            1,
            True
        ),
        (
            'another_test_task_11',
            pathlib.Path('author/governed_folders/template_folder_with_drawio'),
            pathlib.Path('author/governed_folders/template_folder_with_drawio'),
            0,
            0,
            0,
            True
        ),
        (
            'another_test_task_12',
            pathlib.Path('author/governed_folders/template_folder_with_drawio'),
            pathlib.Path('author/governed_folders/folder_with_bad_drawio'),
            0,
            0,
            1,
            True
        )
    ]
)
def test_e2e(
    task_name: str,
    template_content: pathlib.Path,
    target_content: pathlib.Path,
    setup_code: int,
    template_code: int,
    validate_code: int,
    readme_validate: bool,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path
) -> None:
    """Run an E2E workflow with two test criteria for success."""
    # Note testdata_dir must be before tmp_trestle_dir in the argument order.
    readme_flag = '-rv' if readme_validate else ''
    command_string_setup = f'trestle author folders setup -tn {task_name} {readme_flag}'
    command_string_create_sample = f'trestle author folders create-sample -tn {task_name} {readme_flag}'
    command_string_validate_template = f'trestle author folders template-validate -tn {task_name} {readme_flag}'
    command_string_validate_content = f'trestle author folders validate -tn {task_name} --header-validate {readme_flag}'
    template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}'
    with mock.patch.object(sys, 'argv', command_string_setup.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == setup_code
    if setup_code > 0:
        return
    shutil.rmtree(str(template_target_loc))
    template_loc = testdata_dir / template_content
    if template_loc.is_dir():
        shutil.copytree(str(template_loc), str(template_target_loc))
    else:
        shutil.copy2(str(template_loc), str(template_target_loc))

    with mock.patch.object(sys, 'argv', command_string_validate_template.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == template_code
    if template_code > 0:
        return

    # Create sample - should always work if we are here.
    with mock.patch.object(sys, 'argv', command_string_create_sample.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 0
    target_source = testdata_dir / target_content
    if target_source.is_dir():
        shutil.copytree(str(target_source), str(test_content_loc))
    else:
        shutil.copy2(str(target_source), str(test_content_loc))

    with mock.patch.object(sys, 'argv', command_string_validate_content.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == validate_code
