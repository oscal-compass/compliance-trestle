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
"""oscal-catalog-to-csv task tests."""

import configparser
import pathlib

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.tasks.oscal_catalog_to_csv as oscal_catalog_to_csv
from trestle.tasks.base_task import TaskOutcome

CONFIG_BY_CONTROL = 'test-oscal-catalog-to-csv-rev-5-by-control.config'
CONFIG_BY_STATEMENT = 'test-oscal-catalog-to-csv-rev-5-by-statement.config'

CONFIG_LIST = [f'{CONFIG_BY_CONTROL}', f'{CONFIG_BY_STATEMENT}']


def monkey_exception():
    """Monkey exception."""
    raise RuntimeError('foobar')


def _validate(tmp_path: pathlib.Path, config: str) -> None:
    """Validate."""


def _test_init(tmp_path: pathlib.Path):
    """Test init."""
    test_utils.ensure_trestle_config_dir(tmp_path)


def _get_config_section(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(f'tests/data/tasks/oscal-catalog-to-csv/{fname}')
    config.read(config_path)
    section = config['task.oscal-catalog-to-csv']
    section['output-dir'] = str(tmp_path)
    return (config, section)


def _get_config_section_init(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    _test_init(tmp_path)
    return _get_config_section(tmp_path, fname)


def test_print_info(tmp_path: pathlib.Path) -> None:
    """Test print_info."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.print_info()
        assert retval is None


def test_missing_section(tmp_path: pathlib.Path):
    """Test missing section."""
    section = None
    tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_missing_input(tmp_path: pathlib.Path):
    """Test missing input."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section.pop('input-file')
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_missing_output(tmp_path: pathlib.Path):
    """Test missing output."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section.pop('output-dir')
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_bogus_level(tmp_path: pathlib.Path):
    """Test bogus level."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section['level'] = 'foobar'
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_simulate(tmp_path: pathlib.Path):
    """Test execute."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section['output-dir'] = str(tmp_path)
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.simulate()
        assert retval == TaskOutcome.SIM_SUCCESS


def test_execute(tmp_path: pathlib.Path):
    """Test execute."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section['output-dir'] = str(tmp_path)
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
        _validate(tmp_path, config)


def test_no_overwrite(tmp_path: pathlib.Path):
    """Test no overwrite."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section['output-dir'] = str(tmp_path)
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
        section['output-overwrite'] = 'false'
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_exception(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test exception."""
    monkeypatch.setattr(oscal_catalog_to_csv.CsvHelper, 'write', monkey_exception)
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section['output-dir'] = str(tmp_path)
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE


def test_join():
    """Test join."""
    oscal_catalog_to_csv.join_str(None, None)
    oscal_catalog_to_csv.join_str('x', None)
    oscal_catalog_to_csv.join_str(None, 'y')
    oscal_catalog_to_csv.join_str('x', 'y')


def test_derive_id(tmp_path: pathlib.Path):
    """Test derive_id."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        ifile = section['input-file']
        ipth = pathlib.Path(ifile)
        catalog_helper = oscal_catalog_to_csv.CatalogHelper(ipth)
        ids = ['ac-4.1_smt', 'ac-4.1_smt.a', 'ac-4.1_smt.a.b', 'ac-4.1_smt.a.b.c', 'ac-4.1_smt.a.b.c.d']
        for id_ in ids:
            catalog_helper._derive_id(id_)
