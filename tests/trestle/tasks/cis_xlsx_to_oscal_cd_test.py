# Copyright (c) 2025 The OSCAL Compass Authors. All rights reserved.
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
"""cis-xlsx-to-oscal-cd task tests."""

import configparser
import os
import pathlib
from typing import Dict
from unittest.mock import patch

import trestle.tasks.cis_xlsx_to_oscal_cd as cis_xlsx_to_oscal_cd
from trestle.oscal.component import ComponentDefinition
from trestle.tasks.base_task import TaskOutcome

db2_config = 'tests/data/tasks/cis-xlsx-to-oscal-cd/test-cis-xlsx-to-oscal-cd.db2.snippet.config'


def _get_section(tmp_path: pathlib.Path, file_: str) -> Dict:
    """Get section."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(file_)
    config.read(config_path)
    section = config['task.cis-xlsx-to-oscal-cd']
    section['output-dir'] = str(tmp_path)
    return section


def test_cis_xlsx_to_oscal_cd_compare(tmp_path: pathlib.Path):
    """Test compare."""
    x = cis_xlsx_to_oscal_cd.SortHelper.compare('A', 'B')
    assert x == -1
    x = cis_xlsx_to_oscal_cd.SortHelper.compare('0.0', '1.0')
    assert x == -1
    x = cis_xlsx_to_oscal_cd.SortHelper.compare('1.0', '0.0')
    assert x == 1
    x = cis_xlsx_to_oscal_cd.SortHelper.compare('1.1', '1.1')
    assert x == 0


def test_cis_xlsx_to_oscal_cd_print_info(tmp_path: pathlib.Path):
    """Test print_info call."""
    section = _get_section(tmp_path, db2_config)
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.print_info()
    assert retval is None


def test_cis_xlsx_to_oscal_cd_simulate(tmp_path: pathlib.Path):
    """Test simulate call."""
    section = _get_section(tmp_path, db2_config)
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_cis_xlsx_to_oscal_cd_execute(tmp_path: pathlib.Path):
    """Test execute call - db2."""
    section = _get_section(tmp_path, db2_config)
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_db2(tmp_path)


def test_cis_xlsx_to_oscal_cd_execute_combined(tmp_path: pathlib.Path):
    """Test execute call - db2."""
    section = _get_section(tmp_path, db2_config)
    section['benchmark-file'
            ] = 'tests/data/tasks/cis-xlsx-to-oscal-cd/CIS_IBM_Db2_11_Benchmark_v1.1.0.snippet_combined.xlsx'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_db2(tmp_path)


def test_cis_xlsx_to_oscal_cd_execute_missing_column(tmp_path: pathlib.Path):
    """Test execute call - missing column."""
    section = _get_section(tmp_path, db2_config)
    section['benchmark-file'
            ] = 'tests/data/tasks/cis-xlsx-to-oscal-cd/CIS_IBM_Db2_11_Benchmark_v1.1.0.snippet_missing_column.xlsx'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_xlsx_to_oscal_cd_execute_bad_config(tmp_path: pathlib.Path):
    """Test execute call - bad config."""
    section = _get_section(tmp_path, db2_config)
    del section['benchmark-file']
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_xlsx_to_oscal_cd_execute_bad_overwrite(tmp_path: pathlib.Path):
    """Test execute call - bad overwrite."""
    section = _get_section(tmp_path, db2_config)
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_xlsx_to_oscal_cd_execute_merge(tmp_path: pathlib.Path):
    """Test execute call - merge."""
    section = _get_section(tmp_path, db2_config)
    section['benchmark-file'
            ] = 'tests/data/tasks/cis-xlsx-to-oscal-cd/CIS_IBM_Db2_11_Benchmark_v1.1.0.snippet_merge.xlsx'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_db2(tmp_path)


def test_cis_xlsx_to_oscal_cd_execute_rule_prefix(tmp_path: pathlib.Path):
    """Test execute call - rule prefix."""
    section = _get_section(tmp_path, db2_config)
    section['benchmark-rule-prefix'] = 'CIS'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_db2(tmp_path)


def test_cis_xlsx_to_oscal_cd_execute_control_prefix(tmp_path: pathlib.Path):
    """Test execute call - control prefix."""
    section = _get_section(tmp_path, db2_config)
    section['benchmark-control-prefix'] = 'cisc'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_db2(tmp_path)


def test_cis_xlsx_to_oscal_cd_execute_control_bad(tmp_path: pathlib.Path):
    """Test execute call - control bad."""
    section = _get_section(tmp_path, db2_config)
    section['benchmark-file'
            ] = 'tests/data/tasks/cis-xlsx-to-oscal-cd/CIS_IBM_Db2_11_Benchmark_v1.1.0.snippet_bad_control.xlsx'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_xlsx_to_oscal_cd_execute_columns_exclude(tmp_path: pathlib.Path):
    """Test execute call - control prefix."""
    section = _get_section(tmp_path, db2_config)
    section['columns-exclude'] = '"Recommendation #", "Profile", "Description"'
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_db2(tmp_path)


def test_cis_xlsx_to_oscal_cd_execute_config_missing(tmp_path: pathlib.Path):
    """Test execute call - config_missing."""
    section = None
    tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_xlsx_to_oscal_cd_execute_count_mismatch(tmp_path: pathlib.Path):
    """Test execute call - count mismatch."""
    with patch('trestle.tasks.cis_xlsx_to_oscal_cd.CombineHelper._populate_combined_map') as mock_original_function:
        mock_original_function.return_value = -5
        section = _get_section(tmp_path, db2_config)
        tgt = cis_xlsx_to_oscal_cd.CisXlsxToOscalCd(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_cis_xlsx_to_oscal_cd_execute_csv_row_mgr(tmp_path: pathlib.Path):
    """Test execute call - csv row mgr."""
    row_names = ['row1', 'row2', 'row3']
    # create new row mgr
    csv_row_mgr = cis_xlsx_to_oscal_cd.CsvRowMgr(row_names)
    # test valid case
    try:
        csv_row_mgr.put('row1', '')
    except RuntimeError:
        assert 0 == 1
    # test invalid case
    try:
        csv_row_mgr.put('rowX', '')
        assert 0 == 1
    except RuntimeError:
        pass


def _validate_db2(tmp_path: pathlib.Path):
    """Validate produced OSCAL for db2 cd."""
    # read catalog
    file_path = tmp_path / 'component-definition.json'
    component_definition = ComponentDefinition.oscal_read(file_path)
    # spot check
    assert len(component_definition.components) == 1
    assert component_definition.metadata.title == 'CIS IBM Db2 11 Benchmark'
    assert component_definition.metadata.version == '1.1.0'
    component = component_definition.components[0]
    assert component.type == 'software'
    assert len(component.props) == 552
    prop = component.props[0]
    assert prop.name == 'Rule_Id'
    assert prop.ns == 'https://oscal-compass/compliance-trestle/schemas/oscal/cd'
    assert prop.value == 'CIS-1.1.1'
    assert prop.remarks == 'rule_set_00'
    assert len(component.control_implementations) == 1
    prop = component.props[551]
    assert prop.name == 'Group_Description_Level_1'
    assert prop.ns == 'https://oscal-compass/compliance-trestle/schemas/oscal/cd'
    assert prop.value.startswith('This section provides guidance on various database configuration parameters.')
    assert prop.remarks == 'rule_set_22'
    assert len(component.control_implementations) == 1
    control_implementation = component.control_implementations[0]
    assert len(control_implementation.implemented_requirements) == 6
    assert control_implementation.source == 'catalogs/CIS_controls_v8/catalog.json'
    assert control_implementation.description == 'CIS catalog v8'
    implemented_requirement = control_implementation.implemented_requirements[0]
    assert implemented_requirement.control_id == 'cisc-7.4'
    assert len(implemented_requirement.props) == 1
    prop = implemented_requirement.props[0]
    assert prop.name == 'Rule_Id'
    assert prop.ns == 'https://oscal-compass/compliance-trestle/schemas/oscal/cd'
    assert prop.value == 'CIS-1.1.1'
    implemented_requirement = control_implementation.implemented_requirements[5]
    assert implemented_requirement.control_id == 'cisc-3.10'
