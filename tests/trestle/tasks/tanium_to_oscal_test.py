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
"""Tanium to OSCAL task tests."""

import configparser
import os
import pathlib
import uuid
from unittest.mock import Mock, patch

import trestle.core.const as const
import trestle.tasks.tanium_to_oscal as tanium_to_oscal
import trestle.transforms.implementations.tanium as tanium
from trestle.tasks.base_task import TaskOutcome

uuid_mock1 = Mock(return_value=uuid.UUID('56666738-0f9a-4e38-9aac-c0fad00a5821'))
uuid_mock2 = Mock(return_value=uuid.UUID('46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e'))


def test_tanium_print_info(tmp_path):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.print_info()
    assert retval is None


def test_tanium_simulate(tmp_path):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_simulate_no_config(tmp_path):
    """Test simulate no config call."""
    tgt = tanium_to_oscal.TaniumToOscal(None)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_simulate_no_overwrite(tmp_path):
    """Test simulate no overwrite call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 1


def test_tanium_simulate_no_input_dir(tmp_path):
    """Test simulate with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'input-dir')
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_simulate_no_ouput_dir(tmp_path):
    """Test simulate with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'output-dir')
    section = config['task.tanium-to-oscal']
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_simulate_bad_input_file(tmp_path):
    """Test simulate with bad input file call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'input-dir')
    config.set('task.tanium-to-oscal', 'input-dir', 'tests/data/tasks/tanium/input-bad')
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


@patch(target='uuid.uuid4', new=uuid_mock1)
def test_tanium_execute(tmp_path):
    """Test execute call."""
    tanium.TaniumTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    assert tanium.TaniumTransformer.get_timestamp() == '2021-02-24T19:31:13+00:00'
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.json'
    f_produced = tmp_path / 'Tanium.oscal.json'
    assert list(open(f_produced, encoding=const.FILE_ENCODING)) == list(open(f_expected, encoding=const.FILE_ENCODING))


def test_tanium_execute_no_config(tmp_path):
    """Test execute no config call."""
    tgt = tanium_to_oscal.TaniumToOscal(None)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_execute_no_overwrite_dir(tmp_path):
    """Test execute no overwrite directory call."""
    tanium.TaniumTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    execute_no_overwrite_dir_part1(tmp_path)
    execute_no_overwrite_dir_part2(tmp_path)
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.json'
    f_produced = tmp_path / 'Tanium.oscal.json'
    assert list(open(f_produced, encoding=const.FILE_ENCODING)) == list(open(f_expected, encoding=const.FILE_ENCODING))


@patch(target='uuid.uuid4', new=uuid_mock1)
def execute_no_overwrite_dir_part1(tmp_path):
    """Create expected output."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1


@patch(target='uuid.uuid4', new=uuid_mock2)
def execute_no_overwrite_dir_part2(tmp_path):
    """Attempt to overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_tanium_execute_no_input_dir(tmp_path):
    """Test execute with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'input-dir')
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_execute_no_ouput_dir(tmp_path):
    """Test execute with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'output-dir')
    section = config['task.tanium-to-oscal']
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_execute_bad_timestamp(tmp_path):
    """Test execute with bad timestamp."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['timestamp'] = str('bogus')
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


@patch(target='uuid.uuid4', new=uuid_mock1)
def test_tanium_execute_override_timestamp(tmp_path):
    """Test execute override timestamp call."""
    tanium.TaniumTransformer.set_timestamp('2020-02-24T19:31:13+00:00')
    assert tanium.TaniumTransformer.get_timestamp() == '2020-02-24T19:31:13+00:00'
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.2020.json'
    f_produced = tmp_path / 'Tanium.oscal.json'
    assert list(open(f_produced, encoding=const.FILE_ENCODING)) == list(open(f_expected, encoding=const.FILE_ENCODING))
