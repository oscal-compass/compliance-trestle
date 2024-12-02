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
"""cis-xlsx-to-oscal-cd task tests."""

import configparser
import os
import pathlib
from typing import Dict

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


def _validate_db2(tmp_path: pathlib.Path):
    """Validate produced OSCAL for db2 cd."""
    # read catalog
    file_path = tmp_path / 'component-definition.json'
    component_definition = ComponentDefinition.oscal_read(file_path)
    # spot check
    assert len(component_definition.components) == 1
