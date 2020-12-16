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
"""OSCO to OSCAL task tests."""

import configparser
import os

import trestle.tasks.osco_to_oscal as osco_to_oscal
from trestle.tasks.base_task import TaskOutcome

def test_print_info(tmpdir):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.print_info()
    assert retval is None

def test_simulate(tmpdir):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS

def test_simulate_no_config(tmpdir):
    """Test simulate no config call."""
    tgt = osco_to_oscal.OscoToOscal(None)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE

def test_simulate_no_overwrite(tmpdir):
    """Test simulate no overwrite call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 6
    section['output-overwrite'] = 'false'
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE

def test_simulate_no_input_dir(tmpdir):
    """Test simulate with no input dir call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'input-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE

def test_simulate_no_ouput_dir(tmpdir):
    """Test simulate with no output dir call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'output-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE

def test_execute(tmpdir):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 6

def test_execute_no_config(tmpdir):
    """Test execute no config call."""
    tgt = osco_to_oscal.OscoToOscal(None)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE

def test_execute_no_overwrite(tmpdir):
    """Test execute no overwrite call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 6
    section['output-overwrite'] = 'false'
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE

def test_execute_no_input_dir(tmpdir):
    """Test execute with no input dir call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'input-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE

def test_execute_no_ouput_dir(tmpdir):
    """Test execute with no output dir call."""
    config = configparser.ConfigParser()
    config_path = 'tests/data/tasks/osco/demo-osco-to-oscal.config'
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'output-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
