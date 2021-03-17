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
import pathlib
import uuid
from unittest.mock import Mock, patch

import trestle.tasks.osco_to_oscal as osco_to_oscal
from trestle.tasks.base_task import TaskOutcome

uuid_mock1 = Mock(return_value=uuid.UUID('56666738-0f9a-4e38-9aac-c0fad00a5821'))
uuid_mock2 = Mock(return_value=uuid.UUID('46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e'))

def test_print_info(tmpdir):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.print_info()
    assert retval is None

def test_simulate(tmpdir):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmpdir))) == 0
    
def test_simulate_compressed(tmpdir):
    """Test simulate call with compressed OSCO xml data."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal-compressed.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmpdir))) == 0
    
def test_simulate_no_config(tmpdir):
    """Test simulate no config call."""
    tgt = osco_to_oscal.OscoToOscal(None)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_simulate_no_overwrite(tmpdir):
    """Test simulate no overwrite call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 1

def test_simulate_no_input_dir(tmpdir):
    """Test simulate with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'input-dir')
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_simulate_no_oscal_metadata_file(tmpdir):
    """Test simulate with no metadata file call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal-no-oscal-metadata.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['input-metadata'] = 'non-existant.yaml'
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmpdir))) == 0

def test_simulate_no_ouput_dir(tmpdir):
    """Test simulate with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'output-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmpdir))) == 0
    
def test_simulate_input_fetcher(tmpdir):
    """Test simulate call OSCO fetcher json data."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal-fetcher.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmpdir))) == 0
    
@patch(target='uuid.uuid4', new=uuid_mock1)
def test_execute(tmpdir):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1
    f_expected = pathlib.Path('tests/data/tasks/osco/output/') / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    f_produced = tmpdir  / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]

@patch(target='uuid.uuid4', new=uuid_mock1)
def test_execute_compressed(tmpdir):
    """Test execute call with compressed OSCO xml data."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal-compressed.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1
    f_expected = pathlib.Path('tests/data/tasks/osco/output-fetcher/') / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    f_produced = tmpdir  / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]
    
def test_execute_no_config(tmpdir):
    """Test execute no config call."""
    tgt = osco_to_oscal.OscoToOscal(None)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

def test_execute_no_overwrite(tmpdir):
    """Test execute no overwrite call."""
    execute_no_overwrite_part1(tmpdir)
    execute_no_overwrite_part2(tmpdir)
    f_expected = pathlib.Path('tests/data/tasks/osco/output/') / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    f_produced = tmpdir  / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]
    
@patch(target='uuid.uuid4', new=uuid_mock1)
def execute_no_overwrite_part1(tmpdir):
    """Create expected output."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1

@patch(target='uuid.uuid4', new=uuid_mock2)
def execute_no_overwrite_part2(tmpdir):
    """Attempt to overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE

def test_execute_no_input_dir(tmpdir):
    """Test execute with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'input-dir')
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

@patch(target='uuid.uuid4', new=uuid_mock2)
def test_execute_no_oscal_metadata_file(tmpdir):
    """Test execute with no metadata file call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal-no-oscal-metadata.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['input-metadata'] = 'non-existant.yaml'
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 1
    f_expected = pathlib.Path('tests/data/tasks/osco/output-no-oscal-metadata/') / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    f_produced = tmpdir  / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]

def test_execute_no_ouput_dir(tmpdir):
    """Test execute with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'output-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmpdir))) == 0

@patch(target='uuid.uuid4', new=uuid_mock1)
def test_execute_input_fetcher(tmpdir):
    """Test execute call OSCO fetcher json data."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/demo-osco-to-oscal-fetcher.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmpdir)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmpdir))) == 2
    f_expected = pathlib.Path('tests/data/tasks/osco/output-fetcher/') / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    f_produced = tmpdir  / 'ssg-ocp4-ds-cis-111.222.333.444-pod.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]
    f_expected = pathlib.Path('tests/data/tasks/osco/output-fetcher/') / 'ssg-ocp4-ds-cis-111.222.333.555-pod.json'
    f_produced = tmpdir  / 'ssg-ocp4-ds-cis-111.222.333.555-pod.json'
    assert [row for row in open(f_produced)] == [row for row in open(f_expected)]
