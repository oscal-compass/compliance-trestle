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
"""OSCO to OSCAL task tests."""

import configparser
import os
import pathlib
import uuid

from _pytest.monkeypatch import MonkeyPatch

from tests.test_utils import text_files_equal

import trestle.tasks.osco_to_oscal as osco_to_oscal
import trestle.transforms.implementations.osco as osco
from trestle.tasks.base_task import TaskOutcome


class MonkeyBusiness():
    """Monkey business."""

    def uuid_mock1(self):
        """Mock uuid v1."""
        return uuid.UUID('56666738-0f9a-4e38-9aac-c0fad00a5821')

    def uuid_mock2(self):
        """Mock uuid v2."""
        return uuid.UUID('46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e')


def test_osco_print_info(tmp_path):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.print_info()
    assert retval is None


def test_osco_simulate(tmp_path):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_simulate_compressed(tmp_path):
    """Test simulate call with compressed OSCO xml data."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-compressed.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_simulate_no_config(tmp_path):
    """Test simulate no config call."""
    tgt = osco_to_oscal.OscoToOscal(None)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_simulate_no_overwrite(tmp_path):
    """Test simulate no overwrite call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 1


def test_osco_simulate_no_input_dir(tmp_path):
    """Test simulate with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'input-dir')
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_simulate_no_ouput_dir(tmp_path):
    """Test simulate with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'output-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_simulate_input_fetcher(tmp_path):
    """Test simulate call OSCO fetcher json data."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-fetcher.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_simulate_input_bad_yaml(tmp_path):
    """Test simulate call OSCO bad yaml data."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-bad-yaml.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_execute(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_checking(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    section['checking'] = 'true'
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_1_3_5(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-1.3.5.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_1_3_5_checking(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-1.3.5.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    section['checking'] = 'true'
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_compressed(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call with compressed OSCO xml data."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-compressed.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_no_config(tmp_path):
    """Test execute no config call."""
    tgt = osco_to_oscal.OscoToOscal(None)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_execute_no_overwrite(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute no overwrite call."""
    execute_no_overwrite_part1(tmp_path, monkeypatch)
    execute_no_overwrite_part2(tmp_path, monkeypatch)


def execute_no_overwrite_part1(tmp_path, monkeypatch: MonkeyPatch):
    """Create expected output."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def execute_no_overwrite_part2(tmp_path, monkeypatch: MonkeyPatch):
    """Attempt to overwrite."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock2)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_osco_execute_no_input_dir(tmp_path):
    """Test execute with no input dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'input-dir')
    section = config['task.osco-to-oscal']
    section['output-dir'] = str(tmp_path)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_execute_no_ouput_dir(tmp_path):
    """Test execute with no output dir call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    config.remove_option('task.osco-to-oscal', 'output-dir')
    section = config['task.osco-to-oscal']
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_execute_bad_timestamp(tmp_path):
    """Test execute with bad timestamp."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    section['timestamp'] = str('bogus')
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_osco_execute_input_fetcher(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call OSCO fetcher json data."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-fetcher.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 6
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_input_xml_rhel7(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call OSCO xml data."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-xml-rhel7.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_input_xml_ocp4(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call OSCO xml data."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-xml-ocp4.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_osco_execute_input_configmaps(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call OSCO configmaps data."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(uuid, 'uuid4', monkeybusiness.uuid_mock1)
    osco.OscoTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/osco/test-osco-to-oscal-configmaps.config')
    config.read(config_path)
    section = config['task.osco-to-oscal']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = osco_to_oscal.OscoToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)
