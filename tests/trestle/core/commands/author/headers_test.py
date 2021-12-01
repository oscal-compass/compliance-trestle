# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Tests for trestle author headers command."""

import pathlib
import shutil
import sys
from uuid import uuid4

from _pytest.monkeypatch import MonkeyPatch

import pytest

from trestle.cli import Trestle
from trestle.core.commands.author.consts import START_TEMPLATE_VERSION
from trestle.utils import fs


@pytest.mark.parametrize(
    'task_name, template_path, content_path, global_, setup_rc, template_validate_rc, validate_rc',
    [
        ('catalogs', pathlib.Path('irrelevant'), pathlib.Path('irrelevant_2'), False, 1, 1, 1),
        (
            'test_tasks_1',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/meets_templates'),
            False,
            0,
            0,
            0
        ),
        (
            'test_tasks_2',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            False,
            0,
            0,
            0
        ),
        (
            'test_tasks_3',
            pathlib.Path('author/headers/bad_templates_drawio'),
            pathlib.Path('author/headers/recursive_pass'),
            False,
            0,
            1,
            1
        ),
        (
            'test_tasks_4',
            pathlib.Path('author/headers/bad_templates_wrong_names'),
            pathlib.Path('author/headers/recursive_pass'),
            False,
            0,
            1,
            1
        ),
        (
            'test_tasks_5',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_drawio'),
            False,
            0,
            0,
            3
        ),
        (
            'test_tasks_6',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_drawio_bad_file'),
            False,
            0,
            0,
            1
        ),
        (
            'test_tasks_7',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_md'),
            False,
            0,
            0,
            3
        ),
        (
            'test_tasks_8',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_md_bad_file'),
            False,
            0,
            0,
            3
        ),
        (
            'test_tasks_9',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/passes_with_extraneous_files'),
            False,
            0,
            0,
            0
        ),
        (
            'test_tasks_10',
            pathlib.Path('author/headers/bad_templates_md'),
            pathlib.Path('author/headers/passes_with_extraneous_files'),
            False,
            0,
            1,
            1
        ),
        (
            'test_tasks_11',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            True,
            0,
            0,
            0
        ),
        (
            None,
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            True,
            0,
            0,
            0
        ),
        (
            None,
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            False,
            1,
            1,
            1
        ),
    ]
)
def test_e2e(
    task_name: str,
    template_path: pathlib.Path,
    content_path: pathlib.Path,
    global_: bool,
    setup_rc: int,
    template_validate_rc: int,
    validate_rc: int,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path,
    monkeypatch: MonkeyPatch
) -> None:
    """Run an E2E workflow with a number of test criteria."""
    command_string_setup = 'trestle author headers setup'
    command_string_create_sample = 'trestle author headers create-sample'
    command_string_validate_template = 'trestle author headers template-validate'
    command_string_validate_content = 'trestle author headers validate -r'
    template_target_loc: pathlib.Path
    if task_name:
        tn_string = f' -tn {task_name}'
        command_string_setup += tn_string
        command_string_create_sample += tn_string
        command_string_validate_template += tn_string
        command_string_validate_content += tn_string
        template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name / START_TEMPLATE_VERSION
    else:
        task_name = 'placeholder'
    if global_:
        global_str = ' --global'
        command_string_setup += global_str
        command_string_create_sample += global_str
        command_string_validate_template += global_str
        command_string_validate_content += global_str
        template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / '__global__' / START_TEMPLATE_VERSION
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}'
    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    rc = Trestle().run()
    assert rc == setup_rc
    if setup_rc > 0:
        return
    shutil.rmtree(str(template_target_loc))
    shutil.copytree(str(testdata_dir / template_path), str(template_target_loc))

    monkeypatch.setattr(sys, 'argv', command_string_validate_template.split())
    rc = Trestle().run()
    assert rc == template_validate_rc
    if template_validate_rc > 0:
        return

    # Create sample - should always work if we are here.
    monkeypatch.setattr(sys, 'argv', command_string_create_sample.split())
    rc = Trestle().run()
    assert rc == 0

    shutil.copytree(str(testdata_dir / content_path), str(test_content_loc))
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc == validate_rc


def test_abort_safely_on_missing_directory(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that validation fails cleanly on a missing directory."""
    task_name = 'tester'
    command_string_setup = f'trestle author headers setup -tn {task_name}'
    command_string_validate_content = f'trestle author headers validate -tn {task_name} -r'
    task_dir = tmp_trestle_dir / task_name

    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    rc = Trestle().run()
    assert rc == 0
    shutil.rmtree(str(task_dir))

    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc > 0


def test_taskpath_is_a_file(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that validation fails cleanly on a missing directory."""
    task_name = 'tester'
    command_string_setup = f'trestle author headers setup -tn {task_name}'
    command_string_validate_content = f'trestle author headers validate -tn {task_name} -r'
    task_dir = tmp_trestle_dir / task_name

    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    rc = Trestle().run()
    assert rc == 0

    shutil.rmtree(str(task_dir))

    task_dir.touch()
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc > 0


def test_taskpath_is_a_file_setup(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that setup fails cleanly when taskpath is a file."""
    task_name = 'tester'
    command_string_setup = f'trestle author headers setup -tn {task_name}'
    task_dir = tmp_trestle_dir / task_name
    task_dir.open('w').write('hello')
    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    rc = Trestle().run()
    assert rc > 0


@pytest.mark.parametrize(
    'sample_project, exclusions, acceptable',
    [
        (pathlib.Path('author/headers/global/good'), '', True),
        (pathlib.Path('author/headers/global/pass_with_exceptions'), '', False),
        (pathlib.Path('author/headers/global/pass_with_exceptions'), 'bad_sample', True),
        (pathlib.Path('author/headers/global/pass_with_exceptions'), 'sample_indexable_1', False),
        (pathlib.Path('author/headers/global/pass_with_nested_exceptions'), 'nested/bad', True),
        (pathlib.Path('author/headers/global/pass_with_nested_exceptions'), 'nested/good', False),
        (pathlib.Path('author/headers/global/pass_with_nested_exceptions'), 'nested', True)
    ]
)
def test_exclude_global(
    sample_project: pathlib.Path,
    exclusions: str,
    acceptable: bool,
    testdata_dir: pathlib.Path,
    tmp_path: pathlib.Path,
    monkeypatch: MonkeyPatch
) -> None:
    """Test behaviour of --all flag for trestle author headers."""
    command_string = f'trestle author headers validate -r --global --trestle-root={tmp_path}'
    if not exclusions == '':
        exclusions_arr = exclusions.split(',')
        for exclusion in exclusions_arr:
            command_string += f' --exclude={exclusion.strip()}'
    # delete temp dir before copy
    # Required to be
    shutil.rmtree(tmp_path)
    shutil.copytree(str(testdata_dir / sample_project), str(tmp_path))

    template_path_original = testdata_dir / 'author' / 'headers' / 'good_templates'
    template_path_parent = tmp_path / '.trestle' / 'author'
    template_path_parent.mkdir(parents=True)
    template_path_target = template_path_parent / '__global__'
    shutil.copytree(str(template_path_original), str(template_path_target))

    monkeypatch.setattr(sys, 'argv', command_string.split())
    rc = Trestle().run()  # noqa: E800
    assert (rc == 0) == acceptable  # noqa: E800


@pytest.mark.parametrize(
    'task_name, template_path, content_path, global_, setup_rc, template_validate_rc, validate_rc',
    [
        ('catalogs', pathlib.Path('irrelevant'), pathlib.Path('irrelevant_2'), False, 1, 1, 1),
        (
            'test_tasks_1',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/meets_templates'),
            False,
            0,
            0,
            0
        ),
        (
            'test_tasks_2',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            False,
            0,
            0,
            0
        ),
        (
            'test_tasks_3',
            pathlib.Path('author/headers/bad_templates_drawio'),
            pathlib.Path('author/headers/recursive_pass'),
            False,
            0,
            1,
            1
        ),
        (
            'test_tasks_4',
            pathlib.Path('author/headers/bad_templates_wrong_names'),
            pathlib.Path('author/headers/recursive_pass'),
            False,
            0,
            1,
            1
        ),
        (
            'test_tasks_5',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_drawio'),
            False,
            0,
            0,
            3
        ),
        (
            'test_tasks_6',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_drawio_bad_file'),
            False,
            0,
            0,
            1
        ),
        (
            'test_tasks_7',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_md'),
            False,
            0,
            0,
            3
        ),
        (
            'test_tasks_8',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/fails_validation_md_bad_file'),
            False,
            0,
            0,
            3
        ),
        (
            'test_tasks_9',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/passes_with_extraneous_files'),
            False,
            0,
            0,
            0
        ),
        (
            'test_tasks_10',
            pathlib.Path('author/headers/bad_templates_md'),
            pathlib.Path('author/headers/passes_with_extraneous_files'),
            False,
            0,
            1,
            1
        ),
        (
            'test_tasks_11',
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            True,
            0,
            0,
            0
        ),
        (
            None,
            pathlib.Path('author/headers/good_templates'),
            pathlib.Path('author/headers/recursive_pass'),
            True,
            0,
            0,
            0
        )
    ]
)
def test_e2e_backward_compatibility(
    task_name: str,
    template_path: pathlib.Path,
    content_path: pathlib.Path,
    global_: bool,
    setup_rc: int,
    template_validate_rc: int,
    validate_rc: int,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path,
    monkeypatch: MonkeyPatch
) -> None:
    """Run an E2E workflow with existing files."""
    command_string_setup = 'trestle author headers setup'
    command_string_create_sample = 'trestle author headers create-sample'
    command_string_validate_template = 'trestle author headers template-validate'
    command_string_validate_content = 'trestle author headers validate -r'
    template_target_loc: pathlib.Path
    if task_name:
        tn_string = f' -tn {task_name}'
        command_string_setup += tn_string
        command_string_create_sample += tn_string
        command_string_validate_template += tn_string
        command_string_validate_content += tn_string
        template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name / START_TEMPLATE_VERSION
        old_template_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name
    else:
        task_name = 'placeholder'
    if global_:
        global_str = ' --global'
        command_string_setup += global_str
        command_string_create_sample += global_str
        command_string_validate_template += global_str
        command_string_validate_content += global_str
        template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / '__global__' / START_TEMPLATE_VERSION
        old_template_loc = tmp_trestle_dir / '.trestle' / 'author' / '__global__'
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}'

    # Copy in template using old path
    template_loc = testdata_dir / template_path
    if template_loc.is_dir():
        shutil.copytree(str(template_loc), str(old_template_loc))
    else:
        if not old_template_loc.exists():
            old_template_loc.mkdir(parents=True)
        if template_loc.is_file():
            shutil.copy2(str(template_loc), str(old_template_loc))

    assert old_template_loc.exists()
    assert not template_target_loc.exists()

    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    rc = Trestle().run()
    assert rc == setup_rc
    if setup_rc > 0:
        return

    all_files_wo_version = list(filter(lambda p: p.is_file() and not fs.is_hidden(p), (old_template_loc.iterdir())))
    all_files_w_version = list(filter(lambda p: p.is_file() and not fs.is_hidden(p), (template_target_loc.iterdir())))

    if template_loc.is_dir():
        all_old_files = list(filter(lambda p: p.is_file() and not fs.is_hidden(p), (template_loc.iterdir())))
        all_old_files = [el.parts[-1] for el in all_old_files]
    else:
        all_old_files = [template_loc.parts[-1]]

    assert len(all_files_wo_version) == 0
    assert template_target_loc.exists()
    assert all(el in [el.parts[-1] for el in all_files_w_version] for el in all_old_files)

    shutil.rmtree(str(template_target_loc))
    shutil.copytree(str(testdata_dir / template_path), str(template_target_loc))

    monkeypatch.setattr(sys, 'argv', command_string_validate_template.split())
    rc = Trestle().run()
    assert rc == template_validate_rc
    if template_validate_rc > 0:
        return

    # Create sample - should always work if we are here.
    monkeypatch.setattr(sys, 'argv', command_string_create_sample.split())
    rc = Trestle().run()
    assert rc == 0

    shutil.copytree(str(testdata_dir / content_path), str(test_content_loc))
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc == validate_rc


def test_ignore_flag(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that ignored files are not validated. Validation will fail if attempted."""
    task_template_folder = tmp_trestle_dir / '.trestle/author/test_task/'
    test_template_folder = testdata_dir / 'author/headers/good_templates'
    test_instances_folder = testdata_dir / 'author/headers/ignored_files'
    task_instance_folder = tmp_trestle_dir / 'test_task'

    shutil.copytree(test_template_folder, task_template_folder)

    # copy all files
    shutil.copytree(test_instances_folder, task_instance_folder)

    command_string_validate_content = 'trestle author headers validate -tn test_task -ig ^_.*'
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc == 0

    # test recursive validation
    command_string_validate_content = 'trestle author headers validate -tn test_task -ig ^_.* -r'
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc == 0


def test_instance_no_header(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test behaviour when validating instance with no header."""
    task_template_folder = tmp_trestle_dir / '.trestle/author/test_task/'
    test_template_folder = testdata_dir / 'author/headers/good_templates'
    test_instances_folder = testdata_dir / 'author/headers/empty_headers'
    task_instance_folder = tmp_trestle_dir / 'test_task'

    shutil.copytree(test_template_folder, task_template_folder)

    # copy all files
    shutil.copytree(test_instances_folder, task_instance_folder)

    command_string_validate_content = 'trestle author headers validate -tn test_task'
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc == 3

    command_string_validate_content = 'trestle author headers validate -tn test_task -tv 0.0.1'
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc == 3

    command_string_validate_content = 'trestle author headers validate -tv 0.0.1'
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = Trestle().run()
    assert rc == 1
