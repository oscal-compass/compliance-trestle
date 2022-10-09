# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""csv-to-oscal-cd task tests."""

import configparser
import os
import pathlib

from _pytest.monkeypatch import MonkeyPatch

import trestle.tasks.csv_to_oscal_cd as csv_to_oscal_cd
from trestle.oscal.component import ComponentDefinition
from trestle.tasks.base_task import TaskOutcome


def monkey_exception():
    """Monkey exception."""
    raise Exception('foobar')


def test_csv_to_oscal_cd_print_info(tmp_path: pathlib.Path):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.print_info()
    assert retval is None


def test_csv_to_oscal_cd_simulate(tmp_path: pathlib.Path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_csv_to_oscal_cd_execute(tmp_path: pathlib.Path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate(tmp_path)


def _validate(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    ns0 = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    ns1 = 'http://abc.github.io/compliance-trestle/schemas/oscal/cd'
    pv0 = 'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth'
    pv1 = 'Ensure that the --anonymous-auth argument is set to false'
    pv3 = 'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth'
    cl0 = 'scc_class'
    cl1 = 'user_class'
    rs0 = 'rule_set_000'
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 2
    assert cd.components[0].control_implementations[0].props[0].name == 'Rule_Id'
    assert cd.components[0].control_implementations[0].props[0].ns == ns0
    assert cd.components[0].control_implementations[0].props[0].value == pv0
    assert cd.components[0].control_implementations[0].props[0].class_ == cl0
    assert cd.components[0].control_implementations[0].props[0].remarks.__root__ == rs0
    assert cd.components[0].control_implementations[0].props[1].name == 'Rule_Description'
    assert cd.components[0].control_implementations[0].props[1].ns == ns0
    assert cd.components[0].control_implementations[0].props[1].value == pv1
    assert cd.components[0].control_implementations[0].props[1].class_ == cl0
    assert cd.components[0].control_implementations[0].props[1].remarks.__root__ == rs0
    assert cd.components[0].control_implementations[0].props[2].name == 'Private_Reference_Id'
    assert cd.components[0].control_implementations[0].props[2].ns == ns1
    assert cd.components[0].control_implementations[0].props[2].value == '300000100'
    assert cd.components[0].control_implementations[0].props[2].class_ == cl1
    assert cd.components[0].control_implementations[0].props[2].remarks.__root__ == rs0
    assert cd.components[0].control_implementations[0].implemented_requirements[0].props[0].name == 'Rule_Id'
    assert cd.components[0].control_implementations[0].implemented_requirements[0].props[0].ns == ns0
    assert cd.components[0].control_implementations[0].implemented_requirements[0].props[0].value == pv3
    assert cd.components[0].control_implementations[0].implemented_requirements[0].props[0].class_ == cl0
    assert cd.components[0].control_implementations[0].implemented_requirements[0].props[0].remarks is None


def test_csv_to_oscal_cd_config_missing(tmp_path: pathlib.Path):
    """Test config missing."""
    section = None
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_csv_to_oscal_cd_config_missing_title(tmp_path: pathlib.Path):
    """Test catalog-file missing."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section.pop('title')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_csv_to_oscal_cd_config_missing_csv_file_spec(tmp_path: pathlib.Path):
    """Test csv-file missing specification."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section.pop('csv-file')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_csv_to_oscal_cd_config_missing_csv_file(tmp_path: pathlib.Path):
    """Test csv-file missing."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['csv-file'] = 'foobar'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_csv_to_oscal_cd_exception(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test _build_rules exception."""
    monkeypatch.setattr(csv_to_oscal_cd.CsvToOscalComponentDefinition, '_build_rules', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_csv_to_oscal_cd_execute_no_overwrite(tmp_path: pathlib.Path):
    """Test execute no overwrite call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate(tmp_path)
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_csv_to_oscal_cd_execute_verbose(tmp_path: pathlib.Path):
    """Test execute verbose call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['quiet'] = 'False'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate(tmp_path)
