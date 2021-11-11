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
"""Tanium to OSCAL task tests."""

import configparser
import os
import pathlib

from _pytest.monkeypatch import MonkeyPatch

import trestle.core.const as const
import trestle.tasks.tanium_to_oscal as tanium_to_oscal
import trestle.transforms.implementations.tanium as tanium
from trestle.tasks.base_task import TaskOutcome


class MonkeyBusiness():
    """Monkey business."""

    def __init__(self):
        """Initialize context."""
        self._seed_component = 25529320
        self._seed_inventory = 36618780
        self._seed_observation = 47732990
        self._seed_result = 18847350
        self._seed_result2 = 51169030

    def uuid_component(self):
        """Monkey the creation of uuid for component."""
        self._seed_component += 1
        return str(self._seed_component) + '-71b1-46f6-b2f0-edc34a977809'

    def uuid_inventory(self):
        """Monkey the creation of uuid for inventory."""
        self._seed_inventory += 1
        return str(self._seed_inventory) + '-0f02-40f3-adb7-f1d5cbf15150'

    def uuid_observation(self):
        """Monkey the creation of uuid for observation."""
        self._seed_observation += 1
        return str(self._seed_observation) + '-5c28-45ba-8f0f-9d8c7f51c46e'

    def uuid_result(self):
        """Monkey the creation of uuid for result."""
        self._seed_result += 1
        return str(self._seed_result) + '-8012-434e-801b-19e6ba3cdc0e'

    def uuid_result2(self):
        """Monkey the creation of uuid for result, alternate."""
        self._seed_result2 += 1
        return str(self._seed_result2) + '-ca25-4eec-8152-506286489d9a'


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


def test_tanium_execute(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
    tanium.TaniumTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    assert tanium.TaniumTransformer.get_timestamp() == '2021-02-24T19:31:13+00:00'
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    section['cpus-max'] = '1'
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.json'
    f_produced = tmp_path / 'Tanium.oscal.json'
    assert list(open(f_produced, encoding=const.FILE_ENCODING)) == list(open(f_expected, encoding=const.FILE_ENCODING))


def test_tanium_execute_checking(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
    tanium.TaniumTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    assert tanium.TaniumTransformer.get_timestamp() == '2021-02-24T19:31:13+00:00'
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    section['cpus-max'] = '1'
    section['checking'] = 'true'
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.json'
    f_produced = tmp_path / 'Tanium.oscal.json'
    assert list(open(f_produced, encoding=const.FILE_ENCODING)) == list(open(f_expected, encoding=const.FILE_ENCODING))


def test_tanium_execute_one_file(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
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


def test_tanium_execute_blocksize(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute optional call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    section['blocksize'] = '0'
    section['cpus-max'] = '0'
    section['cpus-min'] = '0'
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS


def test_tanium_execute_cpus(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute optional call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    # set values for number of CPUs to unattainable numbers forcing code to chose reasonable ones.
    section['cpus-max'] = '1000000'
    section['cpus-min'] = '2000000'
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS


def test_tanium_execute_no_config(tmp_path):
    """Test execute no config call."""
    tgt = tanium_to_oscal.TaniumToOscal(None)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
    assert len(os.listdir(str(tmp_path))) == 0


def test_tanium_execute_no_overwrite_dir(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute no overwrite directory call."""
    tanium.TaniumTransformer.set_timestamp('2021-02-24T19:31:13+00:00')
    execute_no_overwrite_dir_part1(tmp_path, monkeypatch)
    execute_no_overwrite_dir_part2(tmp_path, monkeypatch)
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.json'
    f_produced = tmp_path / 'Tanium.oscal.json'
    assert list(open(f_produced, encoding=const.FILE_ENCODING)) == list(open(f_expected, encoding=const.FILE_ENCODING))


def execute_no_overwrite_dir_part1(tmp_path, monkeypatch: MonkeyPatch):
    """Create expected output."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    section['cpus-max'] = '1'
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1


def execute_no_overwrite_dir_part2(tmp_path, monkeypatch: MonkeyPatch):
    """Attempt to overwrite."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-overwrite'] = 'false'
    section['output-dir'] = str(tmp_path)
    section['cpus-max'] = '1'
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


def test_tanium_execute_override_timestamp(tmp_path, monkeypatch: MonkeyPatch):
    """Test execute override timestamp call."""
    monkeybusiness = MonkeyBusiness()
    monkeypatch.setattr(tanium, '_uuid_component', monkeybusiness.uuid_component)
    monkeypatch.setattr(tanium, '_uuid_inventory', monkeybusiness.uuid_inventory)
    monkeypatch.setattr(tanium, '_uuid_observation', monkeybusiness.uuid_observation)
    monkeypatch.setattr(tanium, '_uuid_result', monkeybusiness.uuid_result)
    tanium.TaniumTransformer.set_timestamp('2020-02-24T19:31:13+00:00')
    assert tanium.TaniumTransformer.get_timestamp() == '2020-02-24T19:31:13+00:00'
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/tanium/demo-tanium-to-oscal.config')
    config.read(config_path)
    section = config['task.tanium-to-oscal']
    section['output-dir'] = str(tmp_path)
    section['cpus-max'] = '1'
    tgt = tanium_to_oscal.TaniumToOscal(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    assert len(os.listdir(str(tmp_path))) == 1
    f_expected = pathlib.Path('tests/data/tasks/tanium/output/') / 'Tanium.oscal.2020.json'
    f_produced = tmp_path / 'Tanium.oscal.json'
    assert list(open(f_produced, encoding=const.FILE_ENCODING)) == list(open(f_expected, encoding=const.FILE_ENCODING))
