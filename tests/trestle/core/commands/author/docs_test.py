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
"""Tests for trestle author docs subcommand."""
import pathlib
import shutil
import sys
from uuid import uuid4

from _pytest.monkeypatch import MonkeyPatch

import pytest

import trestle.cli
from trestle.core.commands.author.consts import START_TEMPLATE_VERSION


@pytest.mark.parametrize(
    'command_string, return_code',
    [
        ('trestle author docs setup', 2), ('trestle author docs setup --task-name foobaa', 0),
        ('trestle author docs setup --task-name catalogs', 1)
    ]
)
def test_governed_docs_high(
    tmp_trestle_dir: pathlib.Path, command_string: str, return_code: int, monkeypatch: MonkeyPatch
) -> None:
    """Simple execution tests of trestle author docs."""
    monkeypatch.setattr(sys, 'argv', command_string.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == return_code


@pytest.mark.parametrize(
    'task_name, template_content, target_content, recurse, setup_code, template_code, validate_code',
    [
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            False,
            0,
            0,
            0
        ),
        (
            'catalogs',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            False,
            1,
            1,
            1,
        ),
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/bad_instance_missing_heading.md'),
            False,
            0,
            0,
            1
        ),
        (
            'test_task',
            pathlib.Path('author/utf16test/sample_okay.md'),
            pathlib.Path('author/utf16test/sample_utf16.md'),
            False,
            0,
            0,
            1
        ),
        (
            'test_task',
            pathlib.Path('author/utf16test/sample_utf16.md'),
            pathlib.Path('author/utf16test/sample_okay.md'),
            False,
            0,
            1,
            1
        ),
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            True,
            0,
            0,
            0
        ),
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            True,
            0,
            0,
            1
        )
    ]
)
def test_e2e(
    task_name: str,
    template_content: pathlib.Path,
    target_content: pathlib.Path,
    recurse: bool,
    setup_code: int,
    template_code: int,
    validate_code: int,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path,
    monkeypatch: MonkeyPatch
) -> None:
    """Run an E2E workflow with two test criteria for success."""
    # Note testdata_dir must be before tmp_trestle_dir in the argument order.
    recurse_flag = '-r' if recurse else ''
    command_string_setup = f'trestle author docs setup -tn {task_name}'
    command_string_create_sample = f'trestle author docs create-sample -tn {task_name}'
    command_string_validate_template = f'trestle author docs template-validate -tn {task_name}'
    command_string_validate_content = (f'trestle author docs validate -tn {task_name} --header-validate {recurse_flag}')
    template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name / START_TEMPLATE_VERSION / 'template.md'
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}.md'
    # Test setup
    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == setup_code
    if setup_code > 0:
        return
    # Copy in template:
    shutil.copyfile(str(testdata_dir / template_content), str(template_target_loc))
    monkeypatch.setattr(sys, 'argv', command_string_validate_template.split())
    rc = trestle.cli.Trestle().run()
    assert rc == template_code
    if template_code > 0:
        return

    # Create sample - should always work if we are here.
    monkeypatch.setattr(sys, 'argv', command_string_create_sample.split())
    rc = trestle.cli.Trestle().run()
    assert rc == 0

    shutil.copyfile(str(testdata_dir / target_content), str(test_content_loc))
    if recurse:
        # choose source file based on expected result
        sub_file_name = 'correct_instance_extra_features.md' if validate_code else 'bad_instance_missing_heading.md'
        sub_file_path = testdata_dir / 'author/0.0.1/test_1_md_format' / sub_file_name
        subdir = tmp_trestle_dir / task_name / 'subdir'
        subdir.mkdir()
        sub_content = subdir / f'{uuid4()}.md'
        shutil.copyfile(str(sub_file_path), str(sub_content))

    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = trestle.cli.Trestle().run()
    assert rc == validate_code


def test_failure_bad_template_dir(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Create and test a bad directory."""
    setup_ = 'trestle author docs setup --task-name foobaa'

    bad_template_sub_directory = tmp_trestle_dir / '.trestle' / 'author' / 'foobaa' / 'test'
    bad_template_sub_directory.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sys, 'argv', setup_.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 1


def test_success_repeated_call(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test double setup."""
    setup_ = 'trestle author docs setup --task-name foobaa'

    monkeypatch.setattr(sys, 'argv', setup_.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 0
    monkeypatch.setattr(sys, 'argv', setup_.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 0


def test_e2e_debugging(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Run an E2E workflow with two test criteria for success."""
    # hardcoded arguments for testing
    task_name = 'test_task'
    recurse = False
    template_content = pathlib.Path('author/0.0.1/test_1_md_format/template.md')
    target_content = pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md')
    setup_code = 0
    template_code = 0
    validate_code = 0

    # Note testdata_dir must be before tmp_trestle_dir in the argument order.
    recurse_flag = '-r' if recurse else ''
    command_string_setup = f'trestle author docs setup -tn {task_name}'
    command_string_create_sample = f'trestle author docs create-sample -tn {task_name}'
    command_string_validate_template = f'trestle author docs template-validate -tn {task_name}'
    command_string_validate_content = (f'trestle author docs validate -tn {task_name} --header-validate {recurse_flag}')
    template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name / 'template.md'
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}.md'
    # Test setup
    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == setup_code
    if setup_code > 0:
        return
    # Copy in template:
    shutil.copyfile(str(testdata_dir / template_content), str(template_target_loc))

    monkeypatch.setattr(sys, 'argv', command_string_validate_template.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == template_code
    if template_code > 0:
        return
    # Create sample - should always work if we are here.
    monkeypatch.setattr(sys, 'argv', command_string_create_sample.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 0

    shutil.copyfile(str(testdata_dir / target_content), str(test_content_loc))
    if recurse:
        # choose source file based on expected result
        sub_file_name = 'correct_instance_extra_features.md' if validate_code else 'bad_instance_missing_heading.md'
        sub_file_path = testdata_dir / 'author/0.0.1/test_1_md_format' / sub_file_name
        subdir = tmp_trestle_dir / task_name / 'subdir'
        subdir.mkdir()
        sub_content = subdir / f'{uuid4()}.md'
        shutil.copyfile(str(sub_file_path), str(sub_content))
    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == validate_code


@pytest.mark.parametrize(
    'task_name, template_source_directory, target_source_directory, readme_validate, template_code, validate_code',
    [
        (
            'test_task_0',
            pathlib.Path('author/docs/template_folder_valid_with_readme'),
            pathlib.Path('author/docs/candidate_valid_readme'),
            False,
            0,
            0
        ),
        (
            'test_task_1',
            pathlib.Path('author/docs/template_folder_valid_with_readme'),
            pathlib.Path('author/docs/candidate_valid_readme'),
            True,
            0,
            1
        ),
        (
            'test_task_2',
            pathlib.Path('author/docs/template_folder_invalid'),
            pathlib.Path('author/docs/candidate_valid_readme'),
            False,
            1,
            1
        ),
        (
            'test_task_3',
            pathlib.Path('author/docs/template_folder_invalid'),
            pathlib.Path('author/docs/candidate_valid_readme'),
            True,
            1,
            1
        ),
        (
            'test_task_4',
            pathlib.Path('author/docs/template_folder_valid_with_readme'),
            pathlib.Path('author/docs/candidate_invalid_readme'),
            False,
            0,
            1
        ),
        (
            'test_task_5',
            pathlib.Path('author/docs/template_folder_valid_with_readme'),
            pathlib.Path('author/docs/candidate_invalid_readme'),
            True,
            0,
            1
        )
    ]
)
def test_directory_content(
    task_name: str,
    template_source_directory: pathlib.Path,
    target_source_directory: pathlib.Path,
    readme_validate: bool,
    template_code: int,
    validate_code: int,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path,
    monkeypatch: MonkeyPatch
):
    """Test setup where groups of files are tested to allow testing of readme flags."""
    readme_validate_flag = '-rv' if readme_validate else ''
    command_string_create_sample = f'trestle author docs create-sample -tn {task_name}'
    command_string_validate_template = f'trestle author docs template-validate -tn {task_name}'
    command_string_validate_content = (
        f'trestle author docs validate -tn {task_name} --header-validate {readme_validate_flag}'
    )
    template_target_directory = tmp_trestle_dir / '.trestle' / 'author' / task_name
    task_directory = tmp_trestle_dir / task_name
    # Test setup
    shutil.copytree(str(testdata_dir / template_source_directory), str(template_target_directory))
    shutil.copytree(str(testdata_dir / target_source_directory), str(task_directory))
    monkeypatch.setattr(sys, 'argv', command_string_validate_template.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == template_code
    if template_code > 0:
        return
    # Create sample - should always work if we are here.
    monkeypatch.setattr(sys, 'argv', command_string_create_sample.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 0

    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == validate_code


@pytest.mark.parametrize(
    'task_name, template_content, target_content, recurse, setup_code, template_code, validate_code',
    [
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            False,
            0,
            0,
            0
        ),
        (
            'catalogs',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            False,
            1,
            1,
            1,
        ),
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/bad_instance_missing_heading.md'),
            False,
            0,
            0,
            1
        ),
        (
            'test_task',
            pathlib.Path('author/utf16test/sample_okay.md'),
            pathlib.Path('author/utf16test/sample_utf16.md'),
            False,
            0,
            0,
            1
        ),
        (
            'test_task',
            pathlib.Path('author/utf16test/sample_utf16.md'),
            pathlib.Path('author/utf16test/sample_okay.md'),
            False,
            0,
            1,
            1
        ),
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            True,
            0,
            0,
            0
        ),
        (
            'test_task',
            pathlib.Path('author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            True,
            0,
            0,
            1
        )
    ]
)
def test_e2e_backward_compatibility(
    task_name: str,
    template_content: pathlib.Path,
    target_content: pathlib.Path,
    recurse: bool,
    setup_code: int,
    template_code: int,
    validate_code: int,
    testdata_dir: pathlib.Path,
    tmp_trestle_dir: pathlib.Path,
    monkeypatch: MonkeyPatch
) -> None:
    """Same as E2E test but pretend like workspace existed and needs to be updated."""
    # Note testdata_dir must be before tmp_trestle_dir in the argument order.
    recurse_flag = '-r' if recurse else ''
    command_string_setup = f'trestle author docs setup -tn {task_name}'
    command_string_create_sample = f'trestle author docs create-sample -tn {task_name}'
    command_string_validate_template = f'trestle author docs template-validate -tn {task_name}'
    command_string_validate_content = (f'trestle author docs validate -tn {task_name} --header-validate {recurse_flag}')
    template_target_loc = tmp_trestle_dir / '.trestle' / 'author' / task_name / 'template.md'
    test_content_loc = tmp_trestle_dir / task_name / f'{uuid4()}.md'

    # Copy in template using old path
    (tmp_trestle_dir / '.trestle' / 'author' / task_name).mkdir(exist_ok=True, parents=True)
    shutil.copyfile(str(testdata_dir / template_content), str(template_target_loc))

    # Test setup
    monkeypatch.setattr(sys, 'argv', command_string_setup.split())
    rc = trestle.cli.Trestle().run()
    assert rc == setup_code
    if setup_code > 0:
        return
    assert not template_target_loc.exists()
    assert (tmp_trestle_dir / '.trestle' / 'author' / task_name / START_TEMPLATE_VERSION / 'template.md').exists()

    monkeypatch.setattr(sys, 'argv', command_string_validate_template.split())
    rc = trestle.cli.Trestle().run()
    assert rc == template_code
    if template_code > 0:
        return

    # Create sample - should always work if we are here.
    monkeypatch.setattr(sys, 'argv', command_string_create_sample.split())
    rc = trestle.cli.Trestle().run()
    assert rc == 0

    shutil.copyfile(str(testdata_dir / target_content), str(test_content_loc))
    if recurse:
        # choose source file based on expected result
        sub_file_name = 'correct_instance_extra_features.md' if validate_code else 'bad_instance_missing_heading.md'
        sub_file_path = testdata_dir / 'author/0.0.1/test_1_md_format' / sub_file_name
        subdir = tmp_trestle_dir / task_name / 'subdir'
        subdir.mkdir()
        sub_content = subdir / f'{uuid4()}.md'
        shutil.copyfile(str(sub_file_path), str(sub_content))

    monkeypatch.setattr(sys, 'argv', command_string_validate_content.split())
    rc = trestle.cli.Trestle().run()
    assert rc == validate_code
