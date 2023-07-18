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
"""synthesize-oscal-cd task tests."""
import configparser
import csv
import os
import pathlib
from typing import List

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.tasks.synthesize_oscal_cd as synthesize_oscal_cd
from trestle.tasks.base_task import TaskOutcome


def _get_rows(csv_path: pathlib.Path) -> List[List[str]]:
    """Get rows from csv file."""
    rows = []
    with open(csv_path, 'r', newline='') as f:
        csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            rows.append(row)
    return rows


def _validate(tmp_path: pathlib.Path) -> None:
    """Validate csv."""
    csv_path = tmp_path / 'component-definition.csv'
    rows = _get_rows(csv_path)
    # spot check
    assert rows[0][0] == '$$Component_Title'
    assert rows[0][13] == '$Check_Description'
    assert rows[1][0] == 'A human readable name for the component.'
    assert rows[1][
        11
    ] == 'A list of textual labels that uniquely identify the controls or statements that the component implements.'
    assert rows[2][0] == 'billing'
    assert rows[11][3] == 'rule-a637949b-7e51-46c4-afd4-b96619001bf1'
    assert rows[11][4] == 'Check that sign out due to inactivity is set to # seconds or less for IBM Cloud accounts'
    assert rows[11][5] == 'session_invalidation_in_seconds'
    assert rows[11][14] == 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd/ibmcloud'
    assert rows[55][11] == ''
    assert rows[56][11] == 'PCI-6.3.1 PCI-6.3.3 PCI-6.4.1 PCI-11.3.1 PCI-11.3.1.1 PCI-11.3.1.3 PCI-a1.2.3'
    assert rows[83][0] == 'transit'
    assert len(rows) == 149


def _test_init(tmp_path: pathlib.Path) -> None:
    """Test init."""
    test_utils.ensure_trestle_config_dir(tmp_path)


def _orient(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Get config section."""
    monkeypatch.chdir('tests/data/tasks/synthesize-oscal-cd')


def _get_config_section(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(f'{fname}')
    config.read(config_path)
    section = config['task.synthesize-oscal-cd']
    section['output-dir'] = str(tmp_path)
    return (config, section)


def _get_config_section_init(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    _test_init(tmp_path)
    return _get_config_section(tmp_path, fname)


def test_print_info(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test print_info."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-synthesize-oscal-cd.config')
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.print_info()
    assert retval is None


def test_simulate(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test simulate."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-synthesize-oscal-cd.config')
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) <= 1


def test_execute(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-synthesize-oscal-cd.config')
    section['output-dir'] = str(tmp_path)
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate(tmp_path)


def test_config_missing(tmp_path: pathlib.Path) -> None:
    """Test config missing."""
    section = None
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_cd(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test config missing cd."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-synthesize-oscal-cd.config')
    section.pop('cd')
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cd_not_found(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test cd not found."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-synthesize-oscal-cd.config')
    section['cd'] = 'foobar'
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_mc(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test config missing mc."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-synthesize-oscal-cd.config')
    section.pop('mc')
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_mc_not_found(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test mc not found."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-synthesize-oscal-cd.config')
    section['mc'] = 'foobar'
    tgt = synthesize_oscal_cd.SynthesizeOscalComponentDefinition(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
