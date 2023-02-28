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

import frontmatter

import pytest

from tests.test_utils import execute_command_and_assert

import trestle
from trestle.core.commands.author.consts import START_TEMPLATE_VERSION
from trestle.core.markdown.markdown_api import MarkdownAPI

import yaml


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
        sub_file_name = 'bad_instance_missing_heading.md' if validate_code else 'correct_instance_extra_features.md'
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
        sub_file_name = 'bad_instance_missing_heading.md' if validate_code else 'correct_instance_extra_features.md'
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
    """Same as E2E test but pretend like trestle workspace existed and needs to be updated."""
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

    execute_command_and_assert(command_string_validate_template, template_code, monkeypatch)
    if template_code > 0:
        return

    # Create sample - should always work if we are here.
    execute_command_and_assert(command_string_create_sample, 0, monkeypatch)

    shutil.copyfile(str(testdata_dir / target_content), str(test_content_loc))
    if recurse:
        # choose source file based on expected result
        sub_file_name = 'bad_instance_missing_heading.md' if validate_code else 'correct_instance_extra_features.md'
        sub_file_path = testdata_dir / 'author/0.0.1/test_1_md_format' / sub_file_name
        subdir = tmp_trestle_dir / task_name / 'subdir'
        subdir.mkdir()
        sub_content = subdir / f'{uuid4()}.md'
        shutil.copyfile(str(sub_file_path), str(sub_content))

    execute_command_and_assert(command_string_validate_content, validate_code, monkeypatch)


def test_ignore_flag(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that ignored files are not validated. Validation will fail if attempted."""
    task_template_folder = tmp_trestle_dir / '.trestle/author/test_task/'
    author_template = task_template_folder / 'template.md'
    test_data_folder = testdata_dir / 'author/0.0.1/test_5_md_ignored'
    task_instance_folder = tmp_trestle_dir / 'test_task'
    task_template_folder.mkdir(exist_ok=True, parents=True)
    author_template.touch()
    shutil.copyfile(test_data_folder / 'template.md', author_template)

    # copy all files
    shutil.copytree(test_data_folder, task_instance_folder)

    command_string_validate_content = 'trestle author docs validate -tn test_task -hv -ig ^_.*'
    execute_command_and_assert(command_string_validate_content, 0, monkeypatch)

    command_string_validate_content = 'trestle author docs validate -tn test_task -hv -ig ^_.* -r'
    execute_command_and_assert(command_string_validate_content, 0, monkeypatch)

    command_string_validate_content = 'trestle author docs validate -tn test_task -hv -r'
    execute_command_and_assert(command_string_validate_content, 1, monkeypatch)


def test_fail_when_no_task(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that validation fails when task does not exists."""
    command_validate = 'trestle author docs validate -tn test_task'
    execute_command_and_assert(command_validate, 1, monkeypatch)


def test_fail_when_no_template(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test that validation fails when template does not exists."""
    task_template_folder = tmp_trestle_dir / '.trestle/author/test_task/'
    source_instance = testdata_dir / 'author/0.0.1/test_1_md_format/correct_instance.md'
    task_instance = tmp_trestle_dir / 'test_task/correct_instance.md'
    task_template_folder.mkdir(exist_ok=True, parents=True)
    (tmp_trestle_dir / 'test_task').mkdir(parents=True)
    task_instance.touch()
    shutil.copyfile(source_instance, task_instance)

    command_validate = 'trestle author docs validate -tn test_task'
    execute_command_and_assert(command_validate, 1, monkeypatch)


def test_instance_no_header(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test behaviour when validating instance with no header."""
    test_data_folder = testdata_dir / 'author/0.0.1/test_1_md_format'
    bad_source_instance = test_data_folder / 'bad_instance_no_header.md'

    task_template_folder = tmp_trestle_dir / '.trestle/author/test_task/'
    task_instance_folder = tmp_trestle_dir / 'test_task'
    task_template = task_template_folder / 'template.md'
    task_instance = task_instance_folder / 'no_header_instance.md'
    task_template_folder.mkdir(exist_ok=True, parents=True)
    task_instance_folder.mkdir(parents=True)

    shutil.copy(test_data_folder / 'template.md', task_template)
    shutil.copy(bad_source_instance, task_instance)

    command_string_validate_content = 'trestle author docs validate -tn test_task -hv'
    execute_command_and_assert(command_string_validate_content, 1, monkeypatch)

    command_string_validate_content = 'trestle author docs validate -tn test_task'
    execute_command_and_assert(command_string_validate_content, 0, monkeypatch)

    command_string_validate_content = 'trestle author docs validate -tn test_task -tv 0.0.1'
    execute_command_and_assert(command_string_validate_content, 0, monkeypatch)

    command_string_validate_content = 'trestle author docs validate -tn test_task -tv 0.0.1 -hv'
    execute_command_and_assert(command_string_validate_content, 1, monkeypatch)

    # place bad instance in subfolder
    good_source_instance = test_data_folder / 'correct_instance.md'
    shutil.copyfile(good_source_instance, task_instance)
    (task_instance_folder / 'subfolder').mkdir(parents=True)
    shutil.copy(bad_source_instance, task_instance_folder / 'subfolder/bad_instance.md')

    command_string_validate_content = 'trestle author docs validate -tn test_task -hv -r'
    execute_command_and_assert(command_string_validate_content, 1, monkeypatch)


def test_template_validate_no_template(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test that template validation fails when no template."""
    task_template_folder = tmp_trestle_dir / '.trestle/author/test_task/'
    task_template_folder.mkdir(exist_ok=True, parents=True)
    command_validate = 'trestle author docs template-validate -tn test_task'
    execute_command_and_assert(command_validate, 1, monkeypatch)


def test_001_template_folder_is_not_created(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test that folder 0.0.1 is not recreated."""
    command = 'trestle author docs setup -tn my_task'
    execute_command_and_assert(command, 0, monkeypatch)

    # move template
    template_folder_old = tmp_trestle_dir.joinpath('.trestle/author/my_task/0.0.1')
    template_folder_new = tmp_trestle_dir.joinpath('.trestle/author/my_task/0.1.0')
    template_folder_new.mkdir(parents=True)
    template_path_old = template_folder_old.joinpath('template.md')
    template_path_new = template_folder_new.joinpath('template.md')

    shutil.copy(template_path_old, template_folder_new)

    # remove old template folder
    shutil.rmtree(template_folder_old)

    # modify the header in the template
    contents = frontmatter.loads(template_path_new.open('r').read())
    header = contents.metadata
    header['x-trestle-template-version'] = '0.1.0'

    # write file back
    with open(template_path_new, 'w') as template:
        template.write('---\n')
        yaml.dump(header, template, sort_keys=False)
        template.write('---\n\n')
        template.write(contents.content)

    command = 'trestle author docs validate -tn my_task'
    execute_command_and_assert(command, 0, monkeypatch)

    # ensure that 0.0.1 is not recreated and content is preserved
    assert not template_folder_old.exists()
    assert template_folder_new.exists()
    assert template_folder_new.joinpath('template.md').exists()

    contents = frontmatter.loads(template_path_new.open('r').read())
    header = contents.metadata
    assert header['x-trestle-template-version'] == '0.1.0'


def test_instance_validate_with_governed_heading(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test behaviour when validating good instance with governed heading and various changes."""
    task_template = tmp_trestle_dir / '.trestle/author/test_task/template.md'
    test_template_folder = testdata_dir / 'author/0.0.1/test_3_md_hand_edited'
    test_template = testdata_dir / 'author/0.0.1/test_3_md_hand_edited/template.md'
    task_instance_folder = tmp_trestle_dir / 'test_task'

    (tmp_trestle_dir / '.trestle/author/test_task').mkdir(parents=True)
    task_template.touch()
    shutil.copy(test_template, task_template)
    shutil.copytree(test_template_folder, task_instance_folder)

    command_validate = 'trestle author docs validate -tn test_task'
    execute_command_and_assert(command_validate, 0, monkeypatch)

    command_validate = 'trestle author docs validate -tn test_task -gh Governed_Section'
    execute_command_and_assert(command_validate, 0, monkeypatch)

    # Change second section named Governed Section, should fail
    task_markdown = task_instance_folder / 'decisions_000.md'
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(task_markdown)

    # Make sure two nodes of the same name exists
    gov_nodes = tree.get_all_nodes_for_keys(['## Governed_Section'], True, False)

    assert len(gov_nodes) == 2

    # Change non-governed text
    tree.content.raw_text = tree.content.raw_text.replace('Not governed text', 'This is fine')
    md_api.write_markdown_with_header(task_markdown, header, tree.content.raw_text)

    command_string_validate_content = 'trestle author docs validate -tn test_task -gh Governed_Section'
    execute_command_and_assert(command_string_validate_content, 0, monkeypatch)

    # Now change governed stuff
    tree.content.raw_text = tree.content.raw_text.replace('Financial Approver', 'This is not fine')
    md_api.write_markdown_with_header(task_markdown, header, tree.content.raw_text)

    command_string_validate_content = 'trestle author docs validate -tn test_task -gh=Governed_Section'
    execute_command_and_assert(command_string_validate_content, 1, monkeypatch)

    # Now rename back
    tree.content.raw_text = tree.content.raw_text.replace('This is not fine', 'Financial Approver')
    md_api.write_markdown_with_header(task_markdown, header, tree.content.raw_text)

    command_string_validate_content = 'trestle author docs validate -tn test_task -gh=Governed_Section'
    execute_command_and_assert(command_string_validate_content, 0, monkeypatch)

    # Rename other governed section
    tree.content.raw_text = tree.content.raw_text.replace('Another_Governed_Section', 'Renamed Governed Section')
    md_api.write_markdown_with_header(task_markdown, header, tree.content.raw_text)

    command_string_validate_content = 'trestle author docs validate -tn test_task -gh=Another_Governed_Section'
    execute_command_and_assert(command_string_validate_content, 1, monkeypatch)

    # Validate non existing governed section
    command_string_validate_content = 'trestle author docs validate -tn test_task -gh=NonExisting'
    execute_command_and_assert(command_string_validate_content, 1, monkeypatch)


def test_template_validate_flags_invalid_body(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test behaviour of flags when validating template with invalid body."""
    task_template = tmp_trestle_dir / '.trestle/author/test_task/0.0.1/template.md'
    test_template = testdata_dir / 'author/0.0.1/test_1_md_format/template.md'

    (tmp_trestle_dir / '.trestle/author/test_task/0.0.1').mkdir(parents=True)
    task_template.touch()
    shutil.copy(test_template, task_template)

    command_validate = 'trestle author docs template-validate -tn test_task'
    execute_command_and_assert(command_validate, 0, monkeypatch)

    command_validate = 'trestle author docs template-validate -tn test_task -hv'
    execute_command_and_assert(command_validate, 0, monkeypatch)

    # Make invalid change in the body
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(task_template)
    a_node = tree.get_node_for_key('# Required header 1', True)

    assert a_node
    tree.content.raw_text = tree.content.raw_text.replace('# Required header 1', '<unclosed_html>')
    md_api.write_markdown_with_header(task_template, header, tree.content.raw_text)

    command_validate = 'trestle author docs template-validate -tn test_task'
    execute_command_and_assert(command_validate, 1, monkeypatch)

    command_validate = 'trestle author docs template-validate -tn test_task -hov'
    execute_command_and_assert(command_validate, 0, monkeypatch)

    command_validate = 'trestle author docs template-validate -tn test_task -hv'
    execute_command_and_assert(command_validate, 1, monkeypatch)
