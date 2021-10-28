# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""cis-to-component-definition task tests."""

import configparser
import os
import pathlib
import uuid

from _pytest.monkeypatch import MonkeyPatch

from tests.test_utils import text_files_equal

import trestle
import trestle.tasks.cis_to_component_definition as cis_to_component_definition
from trestle.tasks.base_task import TaskOutcome


def monkey_uuid_1():
    """Monkey create UUID."""
    return uuid.UUID('56666738-0f9a-4e38-9aac-c0fad00a5821')


def monkey_exception():
    """Monkey exception."""
    raise Exception('foobar')


def monkey_trestle_version():
    """Monkey trestle version."""
    return '0.21.0'


def test_cis_to_component_definition_print_info(tmp_path: pathlib.Path):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.print_info()
    assert retval is None


def test_cis_to_component_definition_simulate(tmp_path: pathlib.Path):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_cis_to_component_definition_execute(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test execute call."""
    monkeypatch.setattr(uuid, 'uuid4', monkey_uuid_1)
    monkeypatch.setattr(trestle, '__version__', monkey_trestle_version())
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    tgt.set_timestamp('2021-07-19T14:03:03.000+00:00')
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    assert d_expected != d_produced
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_cis_to_component_definition_execute_selected_rules2(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test execute selected rules call."""
    monkeypatch.setattr(uuid, 'uuid4', monkey_uuid_1)
    monkeypatch.setattr(trestle, '__version__', monkey_trestle_version())
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(tmp_path)
    section['selected-rules'] = 'tests/data/tasks/cis-to-component-definition/selected_rules2.json'
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    tgt.set_timestamp('2021-07-19T14:03:03.000+00:00')
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    assert d_expected != d_produced
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_cis_to_component_definition_execute_enabled_rules2(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test execute enabled rules call."""
    monkeypatch.setattr(uuid, 'uuid4', monkey_uuid_1)
    monkeypatch.setattr(trestle, '__version__', monkey_trestle_version())
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(tmp_path)
    section['enabled-rules'] = 'tests/data/tasks/cis-to-component-definition/enabled_rules2.json'
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    tgt.set_timestamp('2021-07-19T14:03:03.000+00:00')
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    assert d_expected != d_produced
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_cis_to_component_definition_execute_enabled_rules3(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test execute enabled rules call."""
    monkeypatch.setattr(uuid, 'uuid4', monkey_uuid_1)
    monkeypatch.setattr(trestle, '__version__', monkey_trestle_version())
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(tmp_path)
    section['enabled-rules'] = 'tests/data/tasks/cis-to-component-definition/enabled_rules3.json'
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    tgt.set_timestamp('2021-07-19T14:03:03.000+00:00')
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    assert d_expected != d_produced


def test_cis_to_component_definition_bogus_config(tmp_path: pathlib.Path):
    """Test execute call bogus config."""
    section = None
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_profile_list(tmp_path: pathlib.Path):
    """Test execute call missing profile-list."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section.pop('profile-list')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_component_name(tmp_path: pathlib.Path):
    """Test execute call missing component-name."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section.pop('component-name')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_profile_type(tmp_path: pathlib.Path):
    """Test execute call missing profile-type."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section.pop('profile-type')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_profile_ns(tmp_path: pathlib.Path):
    """Test execute call missing profile-ns."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section.pop('profile-ns')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_profile_key(tmp_path: pathlib.Path):
    """Test execute missing profile-file."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    profile_list = section['profile-list'].split()
    for profile in profile_list:
        section.pop(f'profile-file.{profile}')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_profile_file(tmp_path: pathlib.Path):
    """Test execute missing profile-file."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    profile_list = section['profile-list'].split()
    for profile in profile_list:
        section[f'profile-file.{profile}'] = '/foobar'
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS


def test_cis_to_component_definition_missing_profile_url(tmp_path: pathlib.Path):
    """Test execute missinf profile-url."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    profile_list = section['profile-list'].split()
    for profile in profile_list:
        section.pop(f'profile-url.{profile}')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_profile_title(tmp_path: pathlib.Path):
    """Test execute call missing profile-title."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    profile_list = section['profile-list'].split()
    for profile in profile_list:
        section.pop(f'profile-title.{profile}')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_output_dir(tmp_path: pathlib.Path):
    """Test execute call missing output-dir."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section.pop('output-dir')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_no_overwrite(tmp_path: pathlib.Path):
    """Test execute no overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_duplicate_rule(tmp_path: pathlib.Path):
    """Test execute duplicate rule exists."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition2.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_exception(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test _get_cis_rules exception."""
    monkeypatch.setattr(cis_to_component_definition.CisToComponentDefinition, '_get_cis_rules', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition2.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_rules_section(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test missing section selected-rules."""
    monkeypatch.setattr(cis_to_component_definition.CisToComponentDefinition, '_get_cis_rules', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition2.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section.pop('selected-rules')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_rules_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test missing file enabled-rules."""
    monkeypatch.setattr(cis_to_component_definition.CisToComponentDefinition, '_get_cis_rules', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition2.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section['enabled-rules'] = '/foobar'
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_parameters_key(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test missing file enabled-rules."""
    monkeypatch.setattr(cis_to_component_definition.CisToComponentDefinition, '_get_cis_rules', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition2.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section.pop('rule-to-parameters-map')
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_component_definition_missing_parameters_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test missing file enabled-rules."""
    monkeypatch.setattr(cis_to_component_definition.CisToComponentDefinition, '_get_cis_rules', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-component-definition/test-cis-to-component-definition2.config')
    config.read(config_path)
    section = config['task.cis-to-component-definition']
    section['output-dir'] = str(tmp_path)
    section['rule-to-parameters-map'] = '/foobar'
    tgt = cis_to_component_definition.CisToComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
