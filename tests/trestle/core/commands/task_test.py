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
"""Trestle Validate command tests."""
import argparse
import configparser
import pathlib
import sys
from unittest import mock

import pytest

import trestle.cli
import trestle.core.commands.task as taskcmd
import trestle.core.const as const
import trestle.core.err as err


def test_get_list_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Simple test which does E2E tests."""
    command = 'trestle task -l'

    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 0


def test_arguments(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that the argument loading behave correctly."""
    # should pass and print a list
    # also should work but same as above
    # NOTE: When passing arguments by hand like this - they are defined if missing and passed as None
    args = argparse.Namespace(name='task', list=True, verbose=1, task=None, config=None, info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc == 0

    # Conflicting arguments: info an dlist
    args = argparse.Namespace(name='task', list=True, verbose=1, task='stuff', config=None, info=True)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc > 0

    # should not work - missing required arguments
    args = argparse.Namespace(name='task', config='config_file.json', verbose=1, list=False, task=None, info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc > 0
    # Failure due to task not in task pool.
    args = argparse.Namespace(name='task', list=False, verbose=1, task='this-is-not-a-task', config=False, info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc > 0


def test_load_default_config(tmp_trestle_dir: pathlib.Path) -> None:
    """Overwrite the default config file to ensure success. Note this is coupled to PassFail class."""
    # Load and overwrite config file
    section_name = 'task.pass-fail'
    config_object = configparser.ConfigParser()
    config_path = pathlib.Path(const.TRESTLE_CONFIG_DIR) / const.TRESTLE_CONFIG_FILE
    config_object.read(config_path)
    # add section
    config_object.add_section(section_name)
    config_object[section_name]['execute_status'] = 'True'
    config_object[section_name]['simulate_status'] = 'True'
    config_object.write(config_path.open('w'))
    # Now good.

    # should print info.
    args = argparse.Namespace(name='task', list=False, verbose=1, task='pass-fail', config=None, info=True)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc == 0
    args = argparse.Namespace(name='task', list=False, verbose=1, task='pass-fail', config=None, info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc == 0
    #


def test_load_custom_config(tmp_trestle_dir: pathlib.Path) -> None:
    """Test functionality."""
    section_name = 'task.pass-fail'
    config_object = configparser.ConfigParser()
    config_path = pathlib.Path('config_file.json')
    config_object.read(config_path)
    # add section
    config_object.add_section(section_name)
    config_object[section_name]['execute_status'] = 'True'
    config_object[section_name]['simulate_status'] = 'True'
    config_object.write(config_path.open('w'))

    args = argparse.Namespace(
        name='task', list=False, verbose=1, task='pass-fail', config='config_file.json', info=True
    )
    rc = taskcmd.TaskCmd()._run(args)
    assert rc == 0

    args = argparse.Namespace(
        name='task', list=False, verbose=1, task='pass-fail', config='config_file.json', info=False
    )
    rc = taskcmd.TaskCmd()._run(args)
    assert rc == 0


def test_task_cmd_not_trestle_dir(tmp_empty_cwd: pathlib.Path) -> None:
    """Ensure that failure occurs when tasks is executed outside of a trestle dirctory."""
    section_name = 'task.pass-fail'
    config_object = configparser.ConfigParser()
    config_path = pathlib.Path('config_file.json')
    config_object.read(config_path)
    # add section
    config_object.add_section(section_name)
    config_object[section_name]['execute_status'] = 'True'
    config_object[section_name]['simulate_status'] = 'True'
    config_object.write(config_path.open('w'))

    args = argparse.Namespace(
        name='task', list=False, verbose=1, task='pass-fail', config='config_file.json', info=True
    )
    rc = taskcmd.TaskCmd()._run(args)
    assert rc > 0


def test_task_cmd_incorrect_config_path_when_passed(tmp_trestle_dir: pathlib.Path) -> None:
    """Test failure occurs cleanly when a passed config file is not a config file."""
    args = argparse.Namespace(name='task', list=False, verbose=1, task='pass-fail', config='made_up.json', info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc > 0


def test_pass_fail_respect_config(tmp_trestle_dir: pathlib.Path) -> None:
    """This tests whether pass-fail configuration is being successfully respected."""
    # Load and overwrite config file
    section_name = 'task.pass-fail'
    config_object = configparser.ConfigParser()
    config_path = pathlib.Path(const.TRESTLE_CONFIG_DIR) / const.TRESTLE_CONFIG_FILE
    config_object.read(config_path)
    # add section
    config_object.add_section(section_name)
    config_object[section_name]['execute_status'] = 'False'
    config_object[section_name]['simulate_status'] = 'True'
    config_object.write(config_path.open('w'))
    # Now good.

    args = argparse.Namespace(name='task', list=False, verbose=1, task='pass-fail', config=None, info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc > 0

    config_object['task.pass-fail']['execute_status'] = 'True'
    config_object['task.pass-fail']['simulate_status'] = 'False'
    config_object.write(config_path.open('w'))
    args = argparse.Namespace(name='task', list=False, verbose=1, task='pass-fail', config=None, info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc > 0


def test_trestle_no_config(tmp_trestle_dir: pathlib.Path) -> None:
    """Warn but in this case fail when no config is provided."""
    args = argparse.Namespace(name='task', list=False, verbose=1, task='pass-fail', config=None, info=False)
    rc = taskcmd.TaskCmd()._run(args)
    assert rc == 1


def test_trestle_fail_on_task_exception(tmp_trestle_dir: pathlib.Path) -> None:
    """Force an exception in a running trestle task and ensure it is captured."""
    # Load and overwrite config file
    section_name = 'task.pass-fail'
    config_object = configparser.ConfigParser()
    config_path = pathlib.Path(const.TRESTLE_CONFIG_DIR) / const.TRESTLE_CONFIG_FILE
    config_object.read(config_path)
    # add section
    config_object.add_section(section_name)
    config_object[section_name]['execute_status'] = 'True'
    config_object[section_name]['simulate_status'] = 'True'
    config_object.write(config_path.open('w'))
    # Now good.
    with mock.patch('trestle.tasks.base_task.PassFail.execute') as simulate_mock:
        simulate_mock.side_effect = err.TrestleError('stuff')
        args = argparse.Namespace(name='task', list=False, verbose=1, task='pass-fail', config=None, info=False)
        rc = taskcmd.TaskCmd()._run(args)
        assert rc > 0
