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
import csv
import pathlib
from typing import Dict, List

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.tasks.oscal_catalog_to_csv as oscal_catalog_to_csv
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.oscal.common import HowMany
from trestle.tasks.base_task import TaskOutcome

CONFIG_BY_CONTROL = 'test-oscal-catalog-to-csv-rev-5-by-control.config'
CONFIG_BY_STATEMENT = 'test-oscal-catalog-to-csv-rev-5-by-statement.config'

CONFIG_LIST = [f'{CONFIG_BY_CONTROL}', f'{CONFIG_BY_STATEMENT}']


def monkey_exception():
    """Monkey exception."""
    raise RuntimeError('foobar')


def monkey_get_dependent_control_ids(self, control_id: str):
    """Monkey get_dependent_control_ids."""
    return ['parent', 'parent']


def _get_rows(csv_path: pathlib.Path) -> List[List[str]]:
    """Get rows from csv file."""
    rows = []
    with open(csv_path, 'r', newline='') as f:
        csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            rows.append(row)
    return rows


def _validate(config: str, section: Dict[str, str]) -> None:
    """Validate."""
    odir = section['output-dir']
    oname = section['output-name']
    opth = pathlib.Path(odir) / oname
    rows = _get_rows(opth)
    # spot check
    if config == CONFIG_BY_CONTROL:
        assert len(rows) == 1190
        row = rows[0]
        assert row[0] == 'Control Identifier'
        assert row[1] == 'Control Title'
        assert row[2] == 'Control Text'
        row = rows[1]
        assert row[0] == 'AC-1'
        assert row[1] == 'Policy and Procedures'
        assert row[
            2
        ] == 'a. Develop, document, and disseminate to [Assignment: organization-defined personnel or roles]: 1. [Selection (one or more): organization-level; mission/business process-level; system-level] access control policy that: 2. Procedures to facilitate the implementation of the access control policy and the associated access controls; b. Designate an [Assignment: official] to manage the development, documentation, and dissemination of the access control policy and procedures; and c. Review and update the current access control: 1. Policy [Assignment: frequency] and following [Assignment: events] ; and 2. Procedures [Assignment: frequency] and following [Assignment: events].'  # noqa
    elif config == CONFIG_BY_STATEMENT:
        assert len(rows) == 1750
        row = rows[0]
        assert row[0] == 'Control Identifier'
        assert row[1] == 'Control Title'
        assert row[2] == 'Statement Identifier'
        assert row[3] == 'Statement Text'
        row = rows[1]
        assert row[0] == 'AC-1'
        assert row[1] == 'Policy and Procedures'
        assert row[2] == 'AC-1(a)'
        assert row[
            3
        ] == 'a. Develop, document, and disseminate to [Assignment: organization-defined personnel or roles]: 1. [Selection (one or more): organization-level; mission/business process-level; system-level] access control policy that: 2. Procedures to facilitate the implementation of the access control policy and the associated access controls;'  # noqa


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
        section['output-name'] = f'{config}.csv'
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.SUCCESS
        _validate(config, section)


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


def test_unresolved_param(tmp_path: pathlib.Path):
    """Test unresolved param."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        ifile = section['input-file']
        ipth = pathlib.Path(ifile)
        catalog_helper = oscal_catalog_to_csv.CatalogHelper(ipth)
        for control in catalog_helper.get_controls():
            utext = 'foo {{ insert: param, xx-11_odp.02 }} bar'
            try:
                catalog_helper._resolve_parms(control, utext)
                raise RuntimeError('huh?')
            except RuntimeError:
                break


def test_one_choice(tmp_path: pathlib.Path):
    """Test one choice."""
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        ifile = section['input-file']
        ipth = pathlib.Path(ifile)
        catalog_helper = oscal_catalog_to_csv.CatalogHelper(ipth)
        for control in catalog_helper.get_controls():
            if control.params:
                for param in control.params:
                    if param.select:
                        param.select.how_many = HowMany.one
                        catalog_helper._get_parm_value(control, param.id)
                        return


def test_duplicate(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test duplicate."""
    monkeypatch.setattr(CatalogInterface, 'get_dependent_control_ids', monkey_get_dependent_control_ids)
    for config in CONFIG_LIST:
        _, section = _get_config_section_init(tmp_path, config)
        section['output-dir'] = str(tmp_path)
        tgt = oscal_catalog_to_csv.OscalCatalogToCsv(section)
        retval = tgt.execute()
        assert retval == TaskOutcome.FAILURE
