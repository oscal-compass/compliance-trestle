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


def _validate1(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # constants
    ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    cl = 'scc_class'
    rs0 = 'rule_set_000'
    rs1 = 'rule_set_001'
    cr_props = [
        [
            0,
            'Rule_Id',
            'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth',
            rs0,
            ns,
            cl,
        ],
        [
            1,
            'Rule_Description',
            'Ensure that the --anonymous-auth argument is set to false',
            rs0,
            ns,
            cl,
        ],
        [
            2,
            'Private_Reference_Id',
            '300000100',
            rs0,
            None,
            None,
        ],
        [
            3,
            'Rule_Id',
            'xccdf_org.ssgproject.content_rule_api_server_basic_auth',
            rs1,
            None,
            None,
        ],
    ]
    ir_props = [
        [
            0,
            'Rule_Id',
            'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth',
            None,
            ns,
            cl,
        ],
    ]
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 2
    # control implementations props
    for prop in cr_props:
        index = prop[0]
        assert cd.components[0].control_implementations[0].props[index].name == prop[1]
        assert cd.components[0].control_implementations[0].props[index].value == prop[2]
        assert cd.components[0].control_implementations[0].props[index].remarks.__root__ == prop[3]
        if prop[4] is not None:
            assert cd.components[0].control_implementations[0].props[index].ns == prop[4]
        if prop[5] is not None:
            assert cd.components[0].control_implementations[0].props[index].class_ == prop[5]
    # implemented requirements props
    for prop in ir_props:
        index = prop[0]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].name == prop[1]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].value == prop[2]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].remarks is None
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].ns == prop[4]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].class_ == prop[5]


def _validate2(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # constants
    ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    cl = 'scc_class'
    rs0 = 'rule_set_0'
    rs1 = 'rule_set_1'
    cr_props = [
        [
            0,
            'Rule_Id',
            'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth',
            rs0,
            ns,
            cl,
        ],
        [
            1,
            'Rule_Description',
            'Ensure that the --anonymous-auth argument is set to false',
            rs0,
            ns,
            cl,
        ],
        [
            2,
            'Parameter_Id',
            'scan_interval_max',
            rs0,
            ns,
            cl,
        ],
        [
            3,
            'Parameter_Description',
            'Max Scan Interval Days',
            rs0,
            ns,
            cl,
        ],
        [
            4,
            'Parameter_Value_Alternatives',
            '10, 30',
            rs0,
            ns,
            cl,
        ],
        [
            5,
            'Rule_Id',
            'xccdf_org.ssgproject.content_rule_api_server_basic_auth',
            rs1,
            ns,
            cl,
        ],
    ]
    set_params = [
        [
            0,
            'scan_interval_max',
            '7',
        ],
        [
            1,
            'no_of_admins_for_secrets_manager',
            '3',
        ],
    ]
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    # control implementations props
    for prop in cr_props:
        index = prop[0]
        assert cd.components[0].control_implementations[0].props[index].name == prop[1]
        assert cd.components[0].control_implementations[0].props[index].value == prop[2]
        assert cd.components[0].control_implementations[0].props[index].remarks.__root__ == prop[3]
        if prop[4] is not None:
            assert cd.components[0].control_implementations[0].props[index].ns == prop[4]
        if prop[5] is not None:
            assert cd.components[0].control_implementations[0].props[index].class_ == prop[5]
    # set parameters
    for param in set_params:
        index = param[0]
        assert cd.components[0].control_implementations[0].set_parameters[index].param_id == param[1]
        assert cd.components[0].control_implementations[0].set_parameters[index].values[0].__root__ == param[2]
    return


def _validate3(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # constants
    irs = [
        [
            0,
            'ac-6',
            '',
        ],
        [1, 'ac-5', ''],
        [2, 'ia-7', ''],
        [3, 'ac-3', ''],
    ]
    statements = [
        [
            0,
            None,
            None,
        ],
        [
            1,
            0,
            'ac-5_smt.c',
        ],
        [
            2,
            None,
            None,
        ],
        [
            3,
            None,
            None,
        ],
        [
            4,
            0,
            'ac-2_smt.d',
        ],
        [
            5,
            0,
            'au-2_smt.a',
        ],
        [
            5,
            1,
            'au-2_smt.d',
        ],
    ]
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    # implemented requirements
    for ir in irs:
        index = ir[0]
        assert cd.components[0].control_implementations[0].implemented_requirements[index].control_id == ir[1]
        assert cd.components[0].control_implementations[0].implemented_requirements[index].description == ir[2]
    for smt in statements:
        index_a = smt[0]
        index_b = smt[1]
        if index_b is None:
            assert cd.components[0].control_implementations[0].implemented_requirements[index_a].statements is None
        else:
            assert cd.components[0].control_implementations[0].implemented_requirements[index_a].statements[
                index_b].statement_id == smt[2]


def test_print_info(tmp_path: pathlib.Path):
    """Test print_info."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.print_info()
    assert retval is None


def test_simulate(tmp_path: pathlib.Path):
    """Test simulate."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_execute(tmp_path: pathlib.Path):
    """Test execute."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate1(tmp_path)


def test_config_missing(tmp_path: pathlib.Path):
    """Test config missing."""
    section = None
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_title(tmp_path: pathlib.Path):
    """Test config missing title."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section.pop('title')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_version(tmp_path: pathlib.Path):
    """Test config missing version."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section.pop('version')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file_spec(tmp_path: pathlib.Path):
    """Test config missing csv file spec."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section.pop('csv-file')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file(tmp_path: pathlib.Path):
    """Test config missing csv file."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['csv-file'] = 'foobar'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_exception(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test exception."""
    monkeypatch.setattr(csv_to_oscal_cd.CsvToOscalComponentDefinition, '_process_rows', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_no_overwrite(tmp_path: pathlib.Path):
    """Test execute no overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate1(tmp_path)
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_verbose(tmp_path: pathlib.Path):
    """Test execute verbose."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['quiet'] = 'False'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate1(tmp_path)


def test_execute_missing_heading(tmp_path: pathlib.Path):
    """Test execute missing heading."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/spread-sheet/ocp4-user-missing-heading.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_missing_value(tmp_path: pathlib.Path):
    """Test execute missing value."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/spread-sheet/ocp4-user-missing-value.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_missing_rule_id(tmp_path: pathlib.Path):
    """Test execute missing rule id."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/spread-sheet/ocp4-user-missing-rule-id.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_user_parameters(tmp_path: pathlib.Path):
    """Test execute user parameters."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/spread-sheet/ocp4-user-parameters.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate2(tmp_path)


def test_execute_parameters_missing_default(tmp_path: pathlib.Path):
    """Test execute parameters missing default."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/spread-sheet/ocp4-user-parameters-missing-default.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_optional_columns(tmp_path: pathlib.Path):
    """Test execute optional columns."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/spread-sheet/ocp4-optional-columns.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate3(tmp_path)


def test_execute_duplicate_rule(tmp_path: pathlib.Path):
    """Test execute duplicate rule."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/spread-sheet/ocp4-user-duplicate-rule.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
