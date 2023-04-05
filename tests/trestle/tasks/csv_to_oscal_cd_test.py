# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2023 IBM Corp. All rights reserved.
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
import csv
import os
import pathlib
from typing import List
from unittest import mock

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.tasks.csv_to_oscal_cd as csv_to_oscal_cd
from trestle.oscal.component import ComponentDefinition
from trestle.tasks.base_task import TaskOutcome


def monkey_exception() -> None:
    """Monkey exception."""
    raise Exception('foobar')


def _get_rows(file_: str) -> List[List[str]]:
    """Get rows from csv file."""
    rows = []
    csv_path = pathlib.Path(file_)
    with open(csv_path, 'r', newline='') as f:
        csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            rows.append(row)
    return rows


def _validate_ocp(tmp_path: pathlib.Path) -> None:
    """Validate ocp."""
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert cd.metadata.title == 'Component definition for CIS Red Hat OpenShift Container Platform 4 Benchmark profiles'
    assert cd.metadata.version == 'V1.1'
    assert len(cd.components) == 1
    component = cd.components[0]
    assert len(component.props) == 429
    assert component.type == 'Service'
    assert component.title == 'OSCO'
    assert component.props[0].name == 'Rule_Id'
    assert component.props[0].ns == 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    assert component.props[0].value == 'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth'
    assert component.props[0].class_ == 'scc_class'
    assert component.props[0].remarks == 'rule_set_000'
    assert component.props[1].name == 'Rule_Description'
    assert component.props[1].value == 'Ensure that the --anonymous-auth argument is set to false'
    assert component.props[1].remarks == 'rule_set_000'
    assert component.props[2].name == 'Parameter_Id'
    assert component.props[2].value == 'scan_interval_max'
    assert component.props[3].name == 'Parameter_Description'
    assert component.props[3].value == 'Max Scan Interval Days'
    assert component.props[4].name == 'Parameter_Value_Alternatives'
    assert component.props[4].value == '10, 30'
    assert component.props[5].name == 'Private_Reference_Id'
    assert component.props[5].value == '300000100'
    assert component.props[6].name == 'Rule_Id'
    assert component.props[6].value == 'xccdf_org.ssgproject.content_rule_api_server_basic_auth'
    assert component.props[6].remarks == 'rule_set_001'
    assert component.props[428].name == 'Rule_Description'
    assert component.props[428].value == 'Ensure that the --protect-kernel-defaults argument is set to true'
    assert component.props[428].remarks == 'rule_set_200'
    assert component.props[0].name == 'Rule_Id'
    assert len(component.control_implementations) == 2
    assert component.control_implementations[0].description == 'ocp4'
    assert len(component.control_implementations[0].implemented_requirements) == 88
    assert component.control_implementations[0].implemented_requirements[0].control_id == 'CIS-1.2.1'
    assert component.control_implementations[0].implemented_requirements[0].props[0].name == 'Rule_Id'
    assert component.control_implementations[0].implemented_requirements[0].props[
        0].value == 'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth'
    assert component.control_implementations[1].description == 'ocp4-node'
    assert len(component.control_implementations[1].implemented_requirements) == 31
    assert component.control_implementations[1].implemented_requirements[0].control_id == 'CIS-1.1.1'
    assert component.control_implementations[1].implemented_requirements[30].props[
        0].value == 'xccdf_org.ssgproject.content_rule_kubelet_enable_protect_kernel_sysctl'
    assert component.control_implementations[1].implemented_requirements[30].props[
        1].value == 'xccdf_org.ssgproject.content_rule_kubelet_enable_protect_kernel_defaults'


def _validate_bp(tmp_path: pathlib.Path) -> None:
    """Validate bp."""
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    assert cd.metadata.title == 'Component definition for Best Practices'
    assert cd.metadata.version == 'V1.1'
    assert len(cd.components) == 1
    component = cd.components[0]
    assert len(component.props) == 62
    assert component.type == 'Service'
    assert component.title == 'IAM'
    assert len(component.control_implementations) == 1
    assert component.control_implementations[
        0].description == 'NIST Special Publication 800-53 Revision 5 HIGH IMPACT BASELINE'


def _test_init(tmp_path: pathlib.Path):
    """Test init."""
    test_utils.ensure_trestle_config_dir(tmp_path)


def _get_config_section(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(f'tests/data/tasks/csv-to-oscal-cd/{fname}')
    config.read(config_path)
    section = config['task.csv-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    return (config, section)


def _get_config_section_init(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    _test_init(tmp_path)
    return _get_config_section(tmp_path, fname)


def test_print_info(tmp_path: pathlib.Path) -> None:
    """Test print_info."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.print_info()
    assert retval is None


def test_simulate(tmp_path: pathlib.Path) -> None:
    """Test simulate."""
    config, section = _get_config_section(tmp_path, 'test-csv-to-oscal-cd.config')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_execute(tmp_path: pathlib.Path) -> None:
    """Test execute."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_ocp(tmp_path)


def test_config_missing(tmp_path: pathlib.Path) -> None:
    """Test config missing."""
    section = None
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_title(tmp_path: pathlib.Path) -> None:
    """Test config missing title."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    section.pop('title')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_version(tmp_path: pathlib.Path) -> None:
    """Test config missing version."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    section.pop('version')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file_spec(tmp_path: pathlib.Path) -> None:
    """Test config missing csv file spec."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    section['output-dir'] = str(tmp_path)
    section.pop('csv-file')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file(tmp_path: pathlib.Path) -> None:
    """Test config missing csv file."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    section['csv-file'] = 'foobar'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_exception(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test exception."""
    monkeypatch.setattr(csv_to_oscal_cd._RuleSetIdMgr, 'get_next_rule_set_id', monkey_exception)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_mock(tmp_path: pathlib.Path) -> None:
    """Test execute mock."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    # get good data & test that mocking works
    rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
        _validate_ocp(tmp_path)


def _setup_workspace(workspace: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test workspace setup."""
    src = 'tests/data/tasks/csv-to-oscal-cd'
    tgt = workspace / src
    test_utils.copy_tree_with_hidden(src, tgt)
    src = 'tests/data/csv'
    tgt = workspace / src
    test_utils.copy_tree_with_hidden(src, tgt)
    src = 'tests/data/ocp4-cis'
    tgt = workspace / src
    test_utils.copy_tree_with_hidden(src, tgt)
    src = 'nist-content/nist.gov/SP800-53/rev4/json'
    tgt = workspace / src
    test_utils.copy_tree_with_hidden(src, tgt)
    cwd = os.getcwd()
    try:
        os.chdir(workspace)
        command = 'trestle init -v'
        test_utils.execute_command_and_assert(command, 0, monkeypatch)
    finally:
        os.chdir(cwd)


def test_execute_validate_controls(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute validate_controls."""
    workspace = tmp_path / 'trestle.workspace'
    _setup_workspace(workspace, monkeypatch)
    cwd = os.getcwd()
    try:
        os.chdir(workspace)
        config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        section['validate-controls'] = 'warn'
        retval = tgt.execute()
    finally:
        os.chdir(cwd)
    assert retval == TaskOutcome.SUCCESS


def test_execute_validate_controls_nist(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute validate_controls nist."""
    workspace = tmp_path / 'trestle.workspace'
    _setup_workspace(workspace, monkeypatch)
    cwd = os.getcwd()
    try:
        os.chdir(workspace)
        config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
        # replace resolved profile (catalog)
        rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
        for i, row in enumerate(rows):
            if i == 0:
                assert row[3] == 'Profile_Source'
                continue
            elif i == 1:
                continue
            assert row[3] == 'tests/data/ocp4-cis/catalog.json'
            row[3] = 'nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json'
        # test
        with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
            mock_csv_reader.return_value = rows
            section['validate-controls'] = 'warn'
            tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
            retval = tgt.execute()
    finally:
        os.chdir(cwd)
    assert retval == TaskOutcome.SUCCESS


def test_execute_control_invalid(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute control invalid (not in catalog)."""
    workspace = tmp_path / 'trestle.workspace'
    _setup_workspace(workspace, monkeypatch)
    cwd = os.getcwd()
    try:
        os.chdir(workspace)
        config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
        # inject error
        rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
        row = rows[2]
        assert row[6] == 'CIS-1.2.1'
        row[6] = 'CIS-9.9.9'
        # test
        with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
            mock_csv_reader.return_value = rows
            section['validate-controls'] = 'warn'
            tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
            retval = tgt.execute()
    finally:
        os.chdir(cwd)
    assert retval == TaskOutcome.SUCCESS


def test_execute_control_invalid_fail(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute control invalid (not in catalog)."""
    workspace = tmp_path / 'trestle.workspace'
    _setup_workspace(workspace, monkeypatch)
    cwd = os.getcwd()
    try:
        os.chdir(workspace)
        config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
        # inject error
        rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
        row = rows[2]
        assert row[6] == 'CIS-1.2.1'
        row[6] = 'CIS-9.9.9'
        # test
        with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
            mock_csv_reader.return_value = rows
            section['validate-controls'] = 'on'
            tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
            retval = tgt.execute()
    finally:
        os.chdir(cwd)
    assert retval == TaskOutcome.FAILURE


def test_execute_no_overwrite(tmp_path: pathlib.Path) -> None:
    """Test execute no overwrite."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_verbose(tmp_path: pathlib.Path) -> None:
    """Test execute verbose."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    section['quiet'] = 'False'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_ocp(tmp_path)


def test_execute_missing_heading(tmp_path: pathlib.Path) -> None:
    """Test execute missing heading."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    # inject error
    rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
    row = rows[0]
    assert row[2] == 'Rule_Description'
    row[2] = 'foobar'
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_missing_value(tmp_path: pathlib.Path) -> None:
    """Test execute missing value."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    # inject error
    rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
    row = rows[2]
    assert row[2] == 'Ensure that the --anonymous-auth argument is set to false'
    row[2] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_missing_rule_id(tmp_path: pathlib.Path) -> None:
    """Test execute missing rule id."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    # inject error
    rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
    row = rows[2]
    assert row[1] == 'xccdf_org.ssgproject.content_rule_api_server_anonymous_auth'
    row[1] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_missing_control_id_list(tmp_path: pathlib.Path) -> None:
    """Test execute missing control id list."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    # inject error
    rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
    row = rows[2]
    assert row[6] == 'CIS-1.2.1'
    row[6] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 423


def test_execute_missing_parameter_id(tmp_path: pathlib.Path) -> None:
    """Test execute missing parameter id."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd.config')
    # inject error
    rows = _get_rows('tests/data/csv/ocp4-user.v2.csv')
    row = rows[2]
    assert row[9] == 'scan_interval_max'
    row[9] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_bp_sample(tmp_path: pathlib.Path) -> None:
    """Test execute bp sample."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_bp(tmp_path)


def test_execute_bp_cd(tmp_path: pathlib.Path) -> None:
    """Test execute bp cd."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_bp(tmp_path)


def test_execute_bp_cd_missing(tmp_path: pathlib.Path) -> None:
    """Test execute bp cd missing."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/foobar/component-definition.json'
    tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_duplicate_rule(tmp_path: pathlib.Path) -> None:
    """Test execute duplicate rule."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # duplicate rule
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    rows.append(rows[2])
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_delete_rule(tmp_path: pathlib.Path) -> None:
    """Test execute delete rule."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete rule
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    rows.pop(1)
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 57
    assert component.props[0].name == 'Rule_Id'
    assert component.props[0].ns == 'http://abc.github.io/compliance-trestle/schemas/oscal/cd'
    assert component.props[0].value == 'iam_admin_role_users_per_account_maxcount'
    assert component.props[0].class_ == 'scc_class'
    assert component.props[0].remarks == 'rule_set_01'


def test_execute_delete_all_rules_with_params(tmp_path: pathlib.Path) -> None:
    """Test execute delete all rules with params."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete all rules with params
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    rows.pop(11)
    rows.pop(8)
    rows.pop(6)
    rows.pop(3)
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 30
    for prop in component.props:
        if prop.name == 'Parameter_Id':
            assert prop.value != 'allowed_admins_per_account'


def test_execute_delete_rule_with_params(tmp_path: pathlib.Path) -> None:
    """Test execute delete rule with params."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete rule with params
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    rows.pop(3)
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 54
    for prop in component.props:
        if prop.name == 'Parameter_Id':
            assert prop.value != 'allowed_admins_per_account'


def test_execute_add_rule(tmp_path: pathlib.Path) -> None:
    """Test execute add rule."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # add rule
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    row = [
        'add-reference-id',
        'add-rule-id',
        'add-rule-description',
        'add-check-id',
        'add-check-description',
        'add-fetcher',
        'add-fetcher-description',
        'https://abc.com/add-profile-reference-url',
        'add-profile-description',
        'Service',
        'add-control-id-list',
        'IAM',
        'IAM',
        'add-parameter-id',
        'add-parameter-description',
        'add-parameter-value-default',
        'add-parameter-value-alternatives',
        'https://abc.com/add-namespace'
    ]
    rows.append(row)
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    pc = 72
    assert len(component.props) == 72
    assert component.props[pc - 1].name == 'Fetcher_Description'
    assert component.props[pc - 1].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 1].value == 'add-fetcher-description'
    assert component.props[pc - 1].remarks == 'rule_set_10'
    assert component.props[pc - 2].name == 'Fetcher'
    assert component.props[pc - 2].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 2].value == 'add-fetcher'
    assert component.props[pc - 2].remarks == 'rule_set_10'
    assert component.props[pc - 3].name == 'Reference_Id'
    assert component.props[pc - 3].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 3].value == 'add-reference-id'
    assert component.props[pc - 3].remarks == 'rule_set_10'
    assert component.props[pc - 4].name == 'Check_Description'
    assert component.props[pc - 4].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 4].value == 'add-check-description'
    assert component.props[pc - 4].remarks == 'rule_set_10'
    assert component.props[pc - 5].name == 'Check_Id'
    assert component.props[pc - 5].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 5].value == 'add-check-id'
    assert component.props[pc - 5].remarks == 'rule_set_10'
    assert component.props[pc - 6].name == 'Parameter_Value_Alternatives'
    assert component.props[pc - 6].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 6].value == 'add-parameter-value-alternatives'
    assert component.props[pc - 6].remarks == 'rule_set_10'
    assert component.props[pc - 7].name == 'Parameter_Description'
    assert component.props[pc - 7].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 7].value == 'add-parameter-description'
    assert component.props[pc - 7].remarks == 'rule_set_10'
    assert component.props[pc - 8].name == 'Parameter_Id'
    assert component.props[pc - 8].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 8].value == 'add-parameter-id'
    assert component.props[pc - 8].remarks == 'rule_set_10'
    assert component.props[pc - 9].name == 'Rule_Description'
    assert component.props[pc - 9].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 9].value == 'add-rule-description'
    assert component.props[pc - 9].remarks == 'rule_set_10'
    assert component.props[pc - 10].name == 'Rule_Id'
    assert component.props[pc - 10].ns == 'https://abc.com/add-namespace'
    assert component.props[pc - 10].value == 'add-rule-id'
    assert component.props[pc - 10].remarks == 'rule_set_10'
    assert len(component.control_implementations) == 2
    assert len(component.control_implementations[0].set_parameters) == 4
    assert len(component.control_implementations[1].set_parameters) == 1


def test_execute_missing_param_default_value(tmp_path: pathlib.Path) -> None:
    """Test execute missing param default_value."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    # delete default param default value
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    row = rows[3]
    assert row[13] == 'allowed_admins_per_account'
    assert row[15] == '10'
    row[15] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_change_param_default_value(tmp_path: pathlib.Path) -> None:
    """Test execute change param default_value."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # change default param default value
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    row = rows[3]
    assert row[13] == 'allowed_admins_per_account'
    assert row[15] == '10'
    assert row[16] == '10'
    row[15] = '20'
    row[16] = '10 20'
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 62
    assert len(component.control_implementations) == 1
    set_parameters = component.control_implementations[0].set_parameters
    assert len(set_parameters) == 4
    assert len(set_parameters[0].values) == 1
    assert set_parameters[0].values[0] == '20'


def test_execute_delete_param(tmp_path: pathlib.Path) -> None:
    """Test execute delete param."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete param
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    row = rows[3]
    assert row[13] == 'allowed_admins_per_account'
    row[13] = ''
    row[14] = ''
    row[15] = ''
    row[16] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 59
    assert component.props[22].name == 'Parameter_Id'
    assert component.props[22].ns == 'http://abc.github.io/compliance-trestle/schemas/oscal/cd'
    assert component.props[22].value == 'api_keys_rotated_days'
    assert component.props[22].class_ == 'scc_class'
    assert component.props[22].remarks == 'rule_set_04'


def test_execute_delete_params(tmp_path: pathlib.Path) -> None:
    """Test execute delete params."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete params
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    for i in [3, 6, 8, 11]:
        for j in [13, 14, 15, 16]:
            rows[i][j] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 50
    for prop in component.props:
        assert prop.name != 'Parameter_Id'


def test_execute_add_param(tmp_path: pathlib.Path) -> None:
    """Test execute add param."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # add param
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    row = rows[2]
    assert row[13] == ''
    row[13] = 'add-parameter-id'
    row[14] = 'add-parameter-description'
    row[15] = 'add-parameter-default-value'
    row[16] = 'add-parameter-value-alternatives'
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert component.props[2].name == 'Parameter_Id'
    assert component.props[2].value == 'add-parameter-id'
    assert component.props[2].remarks == 'rule_set_00'
    assert component.props[3].name == 'Parameter_Description'
    assert component.props[3].value == 'add-parameter-description'
    assert component.props[3].remarks == 'rule_set_00'
    assert component.props[4].name == 'Parameter_Value_Alternatives'
    assert component.props[4].value == 'add-parameter-value-alternatives'
    assert component.props[4].remarks == 'rule_set_00'
    assert component.props[4].remarks == 'rule_set_00'
    set_parameters = component.control_implementations[0].set_parameters
    assert len(set_parameters) == 5
    assert set_parameters[4].param_id == 'add-parameter-id'
    assert len(set_parameters[4].values) == 1
    assert set_parameters[4].values[0] == 'add-parameter-default-value'


def test_execute_delete_all_control_id_list(tmp_path: pathlib.Path) -> None:
    """Test execute delete all control id list."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete all control lists
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    for i in range(1, len(rows)):
        rows[i][10] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    if cd.components is not None:
        assert len(cd.components) == 0


def test_execute_delete_control_id(tmp_path: pathlib.Path) -> None:
    """Test execute delete control id."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete control id
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    assert rows[2][10] == 'sc-7_smt.a sc-7_smt.b sc-7.3 sc-7.4_smt.a sc-7.5 ia-3'
    rows[2][10] = rows[2][10].replace(' ia-3', '')
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    control_implementation = component.control_implementations[0]
    implemented_requirements = control_implementation.implemented_requirements
    assert len(implemented_requirements) == 20
    assert implemented_requirements[3].control_id == 'sc-7.5'
    assert implemented_requirements[4].control_id == 'ac-6'


def test_execute_delete_control_id_multi(tmp_path: pathlib.Path) -> None:
    """Test execute delete control id multi."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete control id multi
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    for i in range(1, len(rows)):
        rows[i][10] = rows[i][10].replace('ac-6', '')
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    control_implementation = component.control_implementations[0]
    implemented_requirements = control_implementation.implemented_requirements
    assert len(implemented_requirements) == 20
    for implemented_requirement in implemented_requirements:
        assert implemented_requirement.control_id != 'ac-6'


def test_execute_delete_control_id_smt(tmp_path: pathlib.Path) -> None:
    """Test execute delete control id smt."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete control id smt
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    assert rows[4][10] == 'ac-3 ac-4 ac-6 sc-7_smt.a sc-7_smt.b sc-7.4_smt.a ac-14_smt.a cm-7_smt.a cm-7_smt.b'
    rows[4][10] = rows[4][10].replace(' cm-7_smt.b', '')
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    control_implementation = component.control_implementations[0]
    implemented_requirements = control_implementation.implemented_requirements
    assert len(implemented_requirements) == 21
    assert implemented_requirements[10].control_id == 'cm-7'
    statements = implemented_requirements[10].statements
    assert len(statements) == 1
    assert statements[0].statement_id == 'cm-7_smt.a'


def test_execute_add_control_id(tmp_path: pathlib.Path) -> None:
    """Test execute add control id."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # add control id
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    assert rows[2][10] == 'sc-7_smt.a sc-7_smt.b sc-7.3 sc-7.4_smt.a sc-7.5 ia-3'
    rows[2][10] = rows[2][10] + ' ld-0'
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    control_implementation = component.control_implementations[0]
    implemented_requirements = control_implementation.implemented_requirements
    assert len(implemented_requirements) == 22
    assert implemented_requirements[21].control_id == 'ld-0'


def test_execute_add_control_id_smt(tmp_path: pathlib.Path) -> None:
    """Test execute add control mapping smt."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # add control mapping smt
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    assert rows[2][10] == 'sc-7_smt.a sc-7_smt.b sc-7.3 sc-7.4_smt.a sc-7.5 ia-3'
    rows[2][10] = rows[2][10] + ' ld-0_smt.a'
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    control_implementation = component.control_implementations[0]
    implemented_requirements = control_implementation.implemented_requirements
    assert len(implemented_requirements) == 22
    assert implemented_requirements[21].control_id == 'ld-0'
    assert len(implemented_requirements[21].statements) == 1
    statement = implemented_requirements[21].statements[0]
    assert statement.statement_id == 'ld-0_smt.a'
    assert len(statement.props) == 1
    assert statement.props[0].name == 'Rule_Id'
    assert statement.props[0].value == 'account_owner_authorized_ip_range_configured'


def test_execute_delete_property(tmp_path: pathlib.Path) -> None:
    """Test execute delete property."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # delete property
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    assert rows[2][3] == 'account_owner_authorized_ip_range_configured'
    assert rows[2][4] == 'Check whether authorized IP ranges are configured by the account owner'
    rows[2][3] = ''
    rows[2][4] = ''
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 60
    assert component.props[0].name == 'Rule_Id'
    assert component.props[1].name == 'Rule_Description'
    assert component.props[2].name == 'Reference_Id'


def test_execute_add_property(tmp_path: pathlib.Path) -> None:
    """Test execute add property."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # add property
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    assert rows[2][5] == ''
    assert rows[2][6] == ''
    rows[2][5] = 'add-fetcher'
    rows[2][6] = 'add-fetcher-description'
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 64
    assert component.props[0].name == 'Rule_Id'
    assert component.props[1].name == 'Rule_Description'
    assert component.props[2].name == 'Check_Id'
    assert component.props[3].name == 'Check_Description'
    assert component.props[4].name == 'Reference_Id'
    assert component.props[5].name == 'Fetcher'
    assert component.props[5].value == 'add-fetcher'
    assert component.props[6].name == 'Fetcher_Description'
    assert component.props[6].value == 'add-fetcher-description'


def test_execute_add_user_property(tmp_path: pathlib.Path) -> None:
    """Test execute add user property."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-cd-bp.config')
    section['component-definition'] = 'tests/data/csv/component-definitions/bp/component-definition.json'
    # add user property
    rows = _get_rows('tests/data/csv/bp.sample.v2.csv')
    rows[0].append('New_Column_Name')
    rows[1].append('New_Column_Name column description')
    for i in range(2, len(rows)):
        rows[i].append(f'new-column-value-{i}')
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_cd.CsvToOscalComponentDefinition(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'component-definition.json'
    cd = ComponentDefinition.oscal_read(fp)
    # spot check
    component = cd.components[0]
    assert len(component.props) == 71
    assert component.props[5].name == 'New_Column_Name'
    assert component.props[5].value == 'new-column-value-2'
