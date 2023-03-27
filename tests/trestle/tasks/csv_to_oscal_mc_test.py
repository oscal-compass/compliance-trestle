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
import os
import pathlib
from unittest import mock

from tests import test_utils

import trestle.tasks.csv_to_oscal_mc as csv_to_oscal_mc
from trestle.oscal.mapping import MappingCollection
from trestle.tasks.base_task import TaskOutcome


def _validate_mc(tmp_path: pathlib.Path) -> None:
    """Validate mc."""
    # read component-definition
    fp = pathlib.Path(tmp_path) / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(fp)
    # spot check
    assert mc.metadata.title == 'Mapping collection for FS Cloud to HiTrust'
    assert len(mc.mappings) == 1
    mapping = mc.mappings[0]
    href1 = 'https://github.ibm.com/cloud-governance-framework/hitrust_catalog'
    href2 = '/blob/main/catalogs/Hitrust_CSF_v9.2/catalog.json'
    assert mapping.source_resource.href == href1 + href2
    assert mapping.target_resource.type == 'catalog'
    assert len(mapping.maps) == 9
    map_ = mapping.maps[0]
    assert len(map_.props) == 5
    prop = map_.props[0]
    assert prop.name == 'control2control_map_percentage'
    assert prop.value == '100%'
    assert map_.relationship.type == 'equivalent-to'
    assert len(map_.sources) == 1
    source = map_.sources[0]
    assert source.type == 'HiTrust'
    assert source.id_ref == '06.d Data Protection and Privacy of Covered Information'
    assert len(map_.targets) == 9
    target = map_.targets[0]
    assert target.type == 'NIST'
    assert target.id_ref == 'PM-3'


def _test_init(tmp_path: pathlib.Path):
    """Test init."""
    test_utils.ensure_trestle_config_dir(tmp_path)


def _get_config_section(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(f'tests/data/tasks/csv-to-oscal-mc/{fname}')
    config.read(config_path)
    section = config['task.csv-to-oscal-mc']
    section['output-dir'] = str(tmp_path)
    return (config, section)


def _get_config_section_init(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    _test_init(tmp_path)
    return _get_config_section(tmp_path, fname)


def test_print_info(tmp_path: pathlib.Path) -> None:
    """Test print_info."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.print_info()
    assert retval is None


def test_simulate(tmp_path: pathlib.Path) -> None:
    """Test simulate."""
    config, section = _get_config_section(tmp_path, 'test-csv-to-oscal-mc.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_execute(tmp_path: pathlib.Path) -> None:
    """Test execute."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_mc(tmp_path)


def test_config_missing(tmp_path: pathlib.Path) -> None:
    """Test config missing."""
    section = None
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_title(tmp_path: pathlib.Path) -> None:
    """Test config missing title."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    section.pop('title')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_version(tmp_path: pathlib.Path) -> None:
    """Test config missing version."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    section.pop('version')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file_spec(tmp_path: pathlib.Path) -> None:
    """Test config missing csv file spec."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    section['output-dir'] = str(tmp_path)
    section.pop('csv-file')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_config_missing_csv_file(tmp_path: pathlib.Path) -> None:
    """Test config missing csv file."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    section['csv-file'] = 'foobar'
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_no_overwrite(tmp_path: pathlib.Path) -> None:
    """Test execute no overwrite."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_execute_mock(tmp_path: pathlib.Path) -> None:
    """Test execute mock."""
    config, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.config')
    with mock.patch('trestle.tasks.csv_to_oscal_mc.CsvColumn.get_required_column_names'
                    ) as mock_get_required_column_names:
        mock_get_required_column_names.return_value = ['foobar']
        tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE
