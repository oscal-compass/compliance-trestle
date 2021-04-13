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

import trestle.tasks.tanium_to_oscal as tanium_to_oscal
import trestle.transforms.implementations.tanium as tanium
from trestle.tasks.base_task import TaskOutcome

uuid_mock1 = Mock(return_value=uuid.UUID('56666738-0f9a-4e38-9aac-c0fad00a5821'))
uuid_mock2 = Mock(return_value=uuid.UUID('46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e'))

def test_print_info(tmpdir):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.print_info()
    assert retval is None

def test_simulate(tmpdir):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmpdir))) == 0
    
def test_simulate_no_config(tmpdir):
    """Test simulate no config call."""
    tgt = tanium_to_oscal.TaniumToOscal(None)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_simulate_no_overwrite(tmpdir):
    """Test simulate no overwrite call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 1

def test_simulate_no_input_dir(tmpdir):
    """Test simulate with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'input-dir')
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_simulate_no_ouput_dir(tmpdir):
    """Test simulate with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'output-dir')
    section = config['task.tanium-to-oscal']
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_simulate_bad_input_file(tmpdir):
    """Test simulate with bad input file call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'input-dir')
    config.set('task.tanium-to-oscal', 'input-dir', 'tests/data/tasks/tanium/input-bad')
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

@patch(target='uuid.uuid4', new=uuid_mock1)
def test_execute(tmpdir):
    """Test execute call."""
    tanium.TaniumTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    assert tanium.TaniumTransformer.get_timestamp() == '2021-02-24T19:31:13+00:00'
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.json'
    f_produced = tmpdir  / 'Tanium.oscal.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]

def test_execute_no_config(tmpdir):
    """Test execute no config call."""
    tgt = tanium_to_oscal.TaniumToOscal(None)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_execute_no_overwrite_dir(tmpdir):
    """Test execute no overwrite directory call."""
    tanium.TaniumTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    execute_no_overwrite_dir_part1(tmpdir)
    execute_no_overwrite_dir_part2(tmpdir)
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.json'
    f_produced = tmpdir  / 'Tanium.oscal.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]
    
@patch(target='uuid.uuid4', new=uuid_mock1)
def execute_no_overwrite_dir_part1(tmpdir):
    """Create expected output."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1

@patch(target='uuid.uuid4', new=uuid_mock2)
def execute_no_overwrite_dir_part2(tmpdir):
    """Attempt to overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE

def test_execute_no_input_dir(tmpdir):
    """Test execute with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'input-dir')
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_execute_no_ouput_dir(tmpdir):
    """Test execute with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.tanium-to-oscal', 'output-dir')
    section = config['task.tanium-to-oscal']
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_execute_bad_timestamp(tmpdir):
    """Test execute with bad timestamp."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['timestamp'] = str('bogus')
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmpdir))) == 0
    
@patch(target='uuid.uuid4', new=uuid_mock1)
def test_execute_override_timestamp(tmpdir):
    """Test execute override timestamp call."""
    tanium.TaniumTransformer.set_timestamp('2020-02-24T19:31:13+00:00')
    assert tanium.TaniumTransformer.get_timestamp() == '2020-02-24T19:31:13+00:00'
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.2020.json'
    f_produced = tmpdir  / 'Tanium.oscal.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]
