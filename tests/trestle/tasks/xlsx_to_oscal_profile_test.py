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
"""XLSX to OSCAL component-definition task tests."""

import configparser
import os
import pathlib
import uuid
from unittest.mock import Mock, patch

from tests.test_utils import text_files_equal

import trestle.tasks.xlsx_to_oscal_profile as xlsx_to_oscal_profile
from trestle.tasks.base_task import TaskOutcome

uuid_mock1 = Mock(return_value=uuid.UUID('56666738-0f9a-4e38-9aac-c0fad00a5821'))
get_trestle_version_mock1 = Mock(return_value='0.21.0')

CONFIG_PATH = pathlib.Path('tests/data/tasks/xlsx/test-xlsx-to-oscal-profile.config')


def test_xlsx_print_info(tmp_path):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.print_info()
    assert retval is None


def test_xlsx_simulate(tmp_path):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


@patch(target='uuid.uuid4', new=uuid_mock1)
@patch(target='trestle.tasks.xlsx_to_oscal_profile.get_trestle_version', new=get_trestle_version_mock1)
def test_xlsx_execute(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
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


@patch(target='uuid.uuid4', new=uuid_mock1)
@patch(target='trestle.tasks.xlsx_to_oscal_profile.get_trestle_version', new=get_trestle_version_mock1)
def test_xlsx_execute_filter(tmp_path):
    """Test execute filter call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    d_expected = pathlib.Path(section['output-dir'] + '-filtered')
    d_produced = tmp_path
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    tgt.set_timestamp('2021-07-19T14:03:03.000+00:00')
    section['filter-column'] = 'Include in FS Cloud Profile?'
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


def test_xlsx_execute_bogus_spread_sheet(tmp_path):
    """Test execute call bogus spread sheet."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    section['spread-sheet-file'] = 'bogus'
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_bogus_config(tmp_path):
    """Test execute call bogus config."""
    section = None
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_missing_spread_sheet(tmp_path):
    """Test execute call missing spread sheet."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    del section['spread-sheet-file']
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_missing_spread_sheet_url(tmp_path):
    """Test execute call missing spread sheet url."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    del section['spread-sheet-url']
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_missing_profile_title(tmp_path):
    """Test execute call missing profile title."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    del section['profile-title']
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_no_overwrite(tmp_path):
    """Test execute call output already exists."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_spread_sheet_missing(tmp_path):
    """Test execute call spread sheet missing."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section.pop('spread-sheet-file')
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_spread_sheet_not_found(tmp_path):
    """Test execute call spread sheet not found."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['spread-sheet-file'] = '/foobar'
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_work_sheet_name_missing(tmp_path):
    """Test execute call work sheet name missing."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section.pop('work-sheet-name')
    section['output-dir'] = str(tmp_path)
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_missing_column_heading(tmp_path):
    """Test execute call missing column heading."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    section['spread-sheet-file'] = 'tests/data/spread-sheet/missing_column_heading.xlsx'
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_xlsx_execute_embedded_blank_in_goal_name_id(tmp_path):
    """Test execute with embedded blank in goal_name_id."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(CONFIG_PATH)
    config.read(config_path)
    section = config['task.xlsx-to-oscal-profile']
    section['output-dir'] = str(tmp_path)
    section['spread-sheet-file'] = 'tests/data/spread-sheet/embedded_blank_in_goal_name_id.xlsx'
    tgt = xlsx_to_oscal_profile.XlsxToOscalProfile(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
