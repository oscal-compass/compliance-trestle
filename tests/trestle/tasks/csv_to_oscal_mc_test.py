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
"""csv-to-oscal-mc task tests."""

import configparser
import csv
import os
import pathlib
from typing import List
from unittest import mock

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.tasks.csv_to_oscal_mc as csv_to_oscal_mc
from trestle.oscal.mapping import MappingCollection
from trestle.tasks.base_task import TaskOutcome


def _get_rows(file_: str) -> List[List[str]]:
    """Get rows from csv file."""
    rows = []
    csv_path = pathlib.Path(file_)
    with open(csv_path, 'r', newline='') as f:
        csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            rows.append(row)
    return rows


def _validate_mc_pci(tmp_path: pathlib.Path) -> None:
    """Validate mc pci."""
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(fp)
    # spot check
    assert mc.metadata.title == 'Mapping collection for PCI to Unified'
    assert len(mc.mappings) == 1
    mapping = mc.mappings[0]
    assert mapping.source_resource.type == 'catalog'
    assert mapping.source_resource.href == 'catalogs/PCI/catalog.json'
    assert mapping.target_resource.type == 'catalog'
    assert mapping.target_resource.href == 'catalogs/FedRAMP_rev5_HIGH/catalog.json'
    assert len(mapping.maps) == 8
    map_ = mapping.maps[0]
    assert len(map_.props) == 5
    prop = map_.props[0]
    assert prop.name == 'control2control_map_percentage'
    assert prop.value == '50%'
    assert map_.relationship.type == 'intersects-with'
    assert len(map_.sources) == 1
    source = map_.sources[0]
    assert source.type == 'control'
    assert source.id_ref == 'PCI-6.3.1'
    assert len(map_.targets) == 1
    target = map_.targets[0]
    assert target.type == 'statement'
    assert target.id_ref == 'ra-5_smt.a'


def _validate_mc_soc2(tmp_path: pathlib.Path, tgt_type: str = 'catalog') -> None:
    """Validate mc soc2."""
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(fp)
    # spot check
    assert mc.metadata.title == 'Mapping collection for SOC2 to Unified'
    assert len(mc.mappings) == 1
    mapping = mc.mappings[0]
    assert mapping.source_resource.type == 'catalog'
    assert mapping.source_resource.href == 'catalogs/SOC2/catalog.json'
    assert mapping.target_resource.type == f'{tgt_type}'
    assert mapping.target_resource.href == f'{tgt_type}s/FedRAMP_rev5_HIGH/{tgt_type}.json'
    assert len(mapping.maps) == 4
    map_ = mapping.maps[0]
    assert len(map_.props) == 5
    prop = map_.props[0]
    assert prop.name == 'control2control_map_percentage'
    assert prop.value == '20%'
    assert map_.relationship.type == 'subset-of'
    assert len(map_.sources) == 1
    source = map_.sources[0]
    assert source.type == 'control'
    assert source.id_ref == 'd4'
    assert len(map_.targets) == 5
    target = map_.targets[0]
    assert target.type == 'statement'
    assert target.id_ref == 'ra-5_smt.a'


def _test_init(tmp_path: pathlib.Path) -> None:
    """Test init."""
    test_utils.ensure_trestle_config_dir(tmp_path)


def _orient(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Get config section."""
    monkeypatch.chdir('tests/data/trestle.ws/')


def _get_config_section(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(f'{fname}')
    config.read(config_path)
    section = config['task.csv-to-oscal-mc']
    section['output-dir'] = str(tmp_path)
    return (config, section)


def _get_config_section_init(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    _test_init(tmp_path)
    return _get_config_section(tmp_path, fname)


def test_print_info(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test print_info."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.print_info()
    assert retval is None
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.print_info()
    assert retval is None


def test_simulate(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test simulate."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_execute_pci(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute pci."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_mc_pci(tmp_path)


def test_execute_soc2(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute soc2."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_mc_soc2(tmp_path)


def test_config_missing(tmp_path: pathlib.Path) -> None:
    """Test config missing."""
    section = None
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_title(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test config missing title."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    section.pop('title')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_version(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test config missing version."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    section.pop('version')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file_spec(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test config missing csv file spec."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    section.pop('csv-file')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test config missing csv file."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    section['csv-file'] = 'foobar'
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_no_overwrite(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute no overwrite."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_mock(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute mock."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    csv_file = section['csv-file']
    # get good data & test that mocking works
    rows = _get_rows(csv_file)
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
        _validate_mc_soc2(tmp_path)


def test_execute_invalid_target_id(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute invalid target id."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    csv_file = section['csv-file']
    # get good data & test that mocking works
    rows = _get_rows(csv_file)
    expected = 'ra-5_smt.a ra-5_smt.b ra-5_smt.c ra-5_smt.d si-2_smt.a'
    modified = 'ra-5_smt.z ra-5_smt.y ra-5_smt.x ra-5_smt.w si-2_smt.q'
    assert rows[2][3] == expected
    rows[2][3] = modified
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_invalid_source_id(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute invalid source id."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    csv_file = section['csv-file']
    # get good data & test that mocking works
    rows = _get_rows(csv_file)
    expected = 'd4'
    modified = 'x0'
    assert rows[2][2] == expected
    rows[2][2] = modified
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_execute_profile_target(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute profile target."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    csv_file = section['csv-file']
    # get good data & test that mocking works
    rows = _get_rows(csv_file)
    expected = 'catalogs/FedRAMP_rev5_HIGH/catalog.json'
    modified = 'profiles/FedRAMP_rev5_HIGH/profile.json'
    for i in range(len(rows)):
        if i < 2:
            continue
        assert rows[i][1] == expected
        rows[i][1] = modified
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
        _validate_mc_soc2(tmp_path, 'profile')


def test_execute_missing_column(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test execute missing column."""
    _orient(tmp_path, monkeypatch)
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.soc2.config')
    csv_file = section['csv-file']
    # get good data & test that mocking works
    rows = _get_rows(csv_file)
    expected = '$$Source_Resource'
    modified = '$$FOOBAR_Resource'
    assert rows[0][0] == expected
    rows[0][0] = modified
    with mock.patch('trestle.tasks.csv_to_oscal_cd.csv.reader') as mock_csv_reader:
        mock_csv_reader.return_value = rows
        tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE
