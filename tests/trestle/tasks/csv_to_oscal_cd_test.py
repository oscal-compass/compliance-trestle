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


def _validate01(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # constants
    ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    cl = 'scc_class'
    rs0 = 'rule_set_000'
    rs1 = 'rule_set_001'
    cd_props = [
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
            'Resource_Instance_Type',
            'public-cloud',
            rs0,
            None,
            None,
        ],
        [
            3,
            'Private_Reference_Id',
            '300000100',
            rs0,
            None,
            None,
        ],
        [
            4,
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
    for prop in cd_props:
        index = prop[0]
        assert cd.components[0].props[index].name == prop[1]
        assert cd.components[0].props[index].value == prop[2]
        assert cd.components[0].props[index].remarks.__root__ == prop[3]
        if prop[4] is not None:
            assert cd.components[0].props[index].ns == prop[4]
        if prop[5] is not None:
            assert cd.components[0].props[index].class_ == prop[5]
    # implemented requirements props
    for prop in ir_props:
        index = prop[0]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].name == prop[1]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].value == prop[2]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].remarks is None
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].ns == prop[4]
        assert cd.components[0].control_implementations[0].implemented_requirements[0].props[index].class_ == prop[5]


def _validate02(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # constants
    ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    cl = 'scc_class'
    rs0 = 'rule_set_0'
    rs1 = 'rule_set_1'
    cd_props = [
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
    for prop in cd_props:
        index = prop[0]
        assert cd.components[0].props[index].name == prop[1]
        assert cd.components[0].props[index].value == prop[2]
        assert cd.components[0].props[index].remarks.__root__ == prop[3]
        if prop[4] is not None:
            assert cd.components[0].props[index].ns == prop[4]
        if prop[5] is not None:
            assert cd.components[0].props[index].class_ == prop[5]
    # set parameters
    for param in set_params:
        index = param[0]
        assert cd.components[0].control_implementations[0].set_parameters[index].param_id == param[1]
        assert cd.components[0].control_implementations[0].set_parameters[index].values[0].__root__ == param[2]
    return


def _validate03(tmp_path: pathlib.Path):
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


def _validate04(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # constants
    ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    cl = 'scc_class'
    rs0 = 'rule_set_0'
    rs05 = 'rule_set_05'
    cd_props = [
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
            10,
            'Rule_Id',
            'xccdf_org.ssgproject.content_rule_api_server_oauth_https_serving_cert',
            rs05,
            ns,
            cl,
        ],
        [
            11,
            'Rule_Description',
            'Ensure that the --kubelet-https argument is set to true',
            rs05,
            ns,
            cl,
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
        [
            3,
            'Rule_Id',
            'xccdf_org.ssgproject.content_rule_api_server_https_for_kubelet_conn',
            None,
            ns,
            cl,
        ],
    ]
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    # control implementations props
    for prop in cd_props:
        index = prop[0]
        assert cd.components[0].props[index].name == prop[1]
        assert cd.components[0].props[index].value == prop[2]
        assert cd.components[0].props[index].remarks.__root__ == prop[3]
        if prop[4] is not None:
            assert cd.components[0].props[index].ns == prop[4]
        if prop[5] is not None:
            assert cd.components[0].props[index].class_ == prop[5]
    # implemented requirements props
    for prop in ir_props:
        index = prop[0]
        assert cd.components[0].control_implementations[0].implemented_requirements[index].props[0].name == prop[1]
        assert cd.components[0].control_implementations[0].implemented_requirements[index].props[0].value == prop[2]
        assert cd.components[0].control_implementations[0].implemented_requirements[index].props[0].remarks is None
        assert cd.components[0].control_implementations[0].implemented_requirements[index].props[0].ns == prop[4]
        assert cd.components[0].control_implementations[0].implemented_requirements[index].props[0].class_ == prop[5]


def _validate10(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 166
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 31


def _validate11(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 10
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 4


def _validate12(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4


def _validate13(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 36
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 2


def _validate14(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 52
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 13
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4


def _validate15(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert 'MODIFIED' in cd.components[0].props[1].value


def _validate16(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 64
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert 'ADD' in cd.components[0].props[4].value
    assert 'ADD' in cd.components[0].props[5].value


def _validate17(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 60
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4


def _validate18(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 59
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 3


def _validate19(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 61
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    sections = [
        'Check whether permissions for API key creation are limited ',
        'and configured in IAM settings for the account owner',
    ]
    for section in sections:
        assert section in cd.components[0].props[34].value
    assert cd.components[0].props[34].remarks.__root__ == 'rule_set_05'
    assert cd.components[0].props[35].value == 'iam_admin_role__user_maxcount'
    assert cd.components[0].props[35].remarks.__root__ == 'rule_set_06'


def _validate20(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    sections = [
        'Check whether permissions for API key creation are limited ',
        'and configured in IAM settings for the account owner',
    ]
    for section in sections:
        assert section in cd.components[0].props[34].value
    assert cd.components[0].props[34].remarks.__root__ == 'rule_set_05'
    assert cd.components[0].props[35].value == '3000027'
    assert cd.components[0].props[35].remarks.__root__ == 'rule_set_05'
    assert cd.components[0].props[36].value == 'iam_admin_role__user_maxcount'
    assert cd.components[0].props[36].remarks.__root__ == 'rule_set_06'


def _validate21(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 50
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert cd.components[0].control_implementations[0].set_parameters is None


def _validate22(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert len(cd.components[0].control_implementations[0].set_parameters[0].values) == 1
    assert cd.components[0].control_implementations[0].set_parameters[0].values[0].__root__ == '20'


def _validate23(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert len(cd.components[0].control_implementations[0].implemented_requirements[7].props) == 3
    assert cd.components[0].control_implementations[0].implemented_requirements[7].control_id == 'ac-3'


def _validate24(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 20
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert cd.components[0].control_implementations[0].implemented_requirements[6].control_id == 'ac-5'
    assert cd.components[0].control_implementations[0].implemented_requirements[7].control_id == 'ac-4'
    assert cd.components[0].control_implementations[0].implemented_requirements[8].control_id == 'ac-14'


def _validate25(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert len(cd.components[0].control_implementations[0].implemented_requirements[6].statements[0].props) == 5
    assert cd.components[0].control_implementations[0].implemented_requirements[6].control_id == 'ac-5'


def _validate26(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert len(cd.components[0].control_implementations[0].implemented_requirements[7].props) == 4
    assert cd.components[0].control_implementations[0].implemented_requirements[7].control_id == 'ac-3'


def _validate27(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert len(cd.components[0].control_implementations[0].implemented_requirements[6].statements[0].props) == 6
    assert cd.components[0].control_implementations[0].implemented_requirements[6].control_id == 'ac-5'


def _validate28(tmp_path: pathlib.Path):
    # read catalog
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert len(cd.components) == 1
    assert len(cd.components[0].control_implementations) == 1
    assert len(cd.components[0].props) == 62
    assert len(cd.components[0].control_implementations[0].implemented_requirements) == 21
    assert len(cd.components[0].control_implementations[0].set_parameters) == 4
    assert len(cd.components[0].control_implementations[0].implemented_requirements[0].statements[0].props) == 2
    assert len(cd.components[0].control_implementations[0].implemented_requirements[0].props) == 1
    assert cd.components[0].control_implementations[0].implemented_requirements[0].control_id == 'sc-7'
    assert cd.components[0].control_implementations[0].implemented_requirements[0].props[
        0].value == 'iam_admin_role_users_per_account_maxcount'


def test_print_info(tmp_path: pathlib.Path):
    """Test print_info."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.print_info()
    assert retval is None


def test_simulate(tmp_path: pathlib.Path):
    """Test simulate."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
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
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate01(tmp_path)


def test_config_missing(tmp_path: pathlib.Path):
    """Test config missing."""
    section = None
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_title(tmp_path: pathlib.Path):
    """Test config missing title."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section.pop('title')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_version(tmp_path: pathlib.Path):
    """Test config missing version."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section.pop('version')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file_spec(tmp_path: pathlib.Path):
    """Test config missing csv file spec."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
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
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['csv-file'] = 'foobar'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_namespace(tmp_path: pathlib.Path):
    """Test config missing namespace."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    config.remove_option('task.csv-to-oscal-cd', 'namespace')
    section = config['task.csv-to-oscal-cd']
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_user_namespace(tmp_path: pathlib.Path):
    """Test config missing user-namespace."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    config.remove_option('task.csv-to-oscal-cd', 'user-namespace')
    section = config['task.csv-to-oscal-cd']
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_exception(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test exception."""
    monkeypatch.setattr(csv_to_oscal_cd._RuleSetIdMgr, 'get_next_rule_set_id', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_no_overwrite(tmp_path: pathlib.Path):
    """Test execute no overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate01(tmp_path)
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_verbose(tmp_path: pathlib.Path):
    """Test execute verbose."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['quiet'] = 'False'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate01(tmp_path)


def test_execute_missing_heading(tmp_path: pathlib.Path):
    """Test execute missing heading."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-missing-heading.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_missing_value(tmp_path: pathlib.Path):
    """Test execute missing value."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-missing-value.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_missing_rule_id(tmp_path: pathlib.Path):
    """Test execute missing rule id."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-missing-rule-id.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_missing_control_mapping(tmp_path: pathlib.Path):
    """Test execute missing control mapping."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-missing-control-mapping.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS


def test_execute_missing_parameter_id(tmp_path: pathlib.Path):
    """Test execute missing parameter id."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-missing-parameter-id.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_user_parameters(tmp_path: pathlib.Path):
    """Test execute user parameters."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-parameters.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate02(tmp_path)


def test_execute_user_parameters_del(tmp_path: pathlib.Path):
    """Test execute user parameters del."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-parameters-del.csv'
    section['component-definition'] = 'tests/data/component-definitions/ocp4-user-parameters/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS


def test_execute_user_ocp4_node_del(tmp_path: pathlib.Path):
    """Test execute user ocp4-node delete."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-ocp4-node.csv'
    section['component-definition'] = 'tests/data/component-definitions/ocp-user/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate10(tmp_path)


def test_execute_parameters_missing_default(tmp_path: pathlib.Path):
    """Test execute parameters missing default."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-parameters-missing-default.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_optional_columns(tmp_path: pathlib.Path):
    """Test execute optional columns."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-optional-columns.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate03(tmp_path)


def test_execute_whitespace(tmp_path: pathlib.Path):
    """Test execute leading and trailing whitespace."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-whitespace.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS


def test_execute_duplicate_rule(tmp_path: pathlib.Path):
    """Test execute duplicate rule."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp4-user-duplicate-rule.csv'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_component_definition(tmp_path: pathlib.Path):
    """Test execute component definition."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['component-definition'] = 'tests/data/component-definitions/ocp-user/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate01(tmp_path)


def test_execute_component_definition_add(tmp_path: pathlib.Path):
    """Test execute component definition add."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp-rows-01-10.csv'
    section['component-definition'] = 'tests/data/component-definitions/ocp-user-01-05/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate04(tmp_path)


def test_execute_component_definition_del(tmp_path: pathlib.Path):
    """Test execute component definition del."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/ocp-rows-01-05.csv'
    section['component-definition'] = 'tests/data/component-definitions/ocp-user-01-10/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate11(tmp_path)


def test_config_missing_cd_file(tmp_path: pathlib.Path):
    """Test config missing csv file."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['component-definition'] = 'tests/data/component-definitions/missing/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_bp_sample(tmp_path: pathlib.Path):
    """Test execute bp sample."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate12(tmp_path)


def test_execute_bp_sample_empty_arrays(tmp_path: pathlib.Path):
    """Test execute bp sample empty arrays."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['component-definition'
            ] = 'tests/data/component-definitions/bp-sample-missing-component-arrays/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate12(tmp_path)


def test_execute_bp_sample_del(tmp_path: pathlib.Path):
    """Test execute bp sample delete."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-del-rows.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate13(tmp_path)


def test_execute_bp_sample_del_smt(tmp_path: pathlib.Path):
    """Test execute bp sample delete statement."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-del-smt.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate14(tmp_path)


def test_execute_bp_sample_rule_definition_modify(tmp_path: pathlib.Path):
    """Test execute bp sample rule definition modify."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-property-modify.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate15(tmp_path)


def test_execute_bp_sample_rule_definition_add(tmp_path: pathlib.Path):
    """Test execute bp sample rule definition add."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-property-add.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate16(tmp_path)


def test_execute_bp_sample_rule_definition_remove(tmp_path: pathlib.Path):
    """Test execute bp sample rule definition remove."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-property-remove.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate17(tmp_path)


def test_execute_bp_sample_set_parameter_del(tmp_path: pathlib.Path):
    """Test execute bp sample set parameter del."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-set-parameter-del.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate18(tmp_path)


def test_execute_bp_sample_set_parameter_add(tmp_path: pathlib.Path):
    """Test execute bp sample set parameter add."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample3/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate12(tmp_path)


def test_execute_bp_sample_user_property_remove(tmp_path: pathlib.Path):
    """Test execute bp sample user property remove."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-user-property-remove.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate19(tmp_path)


def test_execute_bp_sample_user_property_add(tmp_path: pathlib.Path):
    """Test execute bp sample user property add."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample4/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate20(tmp_path)


def test_execute_bp_sample_set_parameter_del_all(tmp_path: pathlib.Path):
    """Test execute bp sample set parameter del all."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-set-parameter-del-all.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample2/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate21(tmp_path)


def test_execute_bp_sample_set_parameter_add_all(tmp_path: pathlib.Path):
    """Test execute bp sample set parameter add all."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample5/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate12(tmp_path)


def test_execute_bp_sample_set_parameter_mod(tmp_path: pathlib.Path):
    """Test execute bp sample set parameter mod."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample-set-parameter-mod.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate22(tmp_path)


def test_execute_bp_sample_ctl_del(tmp_path: pathlib.Path):
    """Test execute bp sample control delete."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample6.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate23(tmp_path)


def test_execute_bp_sample_ctl_del_all(tmp_path: pathlib.Path):
    """Test execute bp sample control delete."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample7.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate24(tmp_path)


def test_execute_bp_sample_ctl_smt_del(tmp_path: pathlib.Path):
    """Test execute bp sample control statement delete."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample8.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate25(tmp_path)


def test_execute_bp_sample_ctl_add(tmp_path: pathlib.Path):
    """Test execute bp sample control add."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample6/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate26(tmp_path)


def test_execute_bp_sample_ctl_smt_add(tmp_path: pathlib.Path):
    """Test execute bp sample control statement add."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample8/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate27(tmp_path)


def test_execute_bp_sample_ctl_add_no_props(tmp_path: pathlib.Path):
    """Test execute bp sample control add no rpops."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-cd/test-csv-to-oscal-cd-bp.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    section['csv-file'] = 'tests/data/csv/bp.sample9.csv'
    section['component-definition'] = 'tests/data/component-definitions/bp-sample/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate28(tmp_path)
