# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""cis-to-catalog task tests."""

import configparser
import os
import pathlib

from _pytest.monkeypatch import MonkeyPatch

import trestle.tasks.cis_to_catalog as cis_to_catalog
from trestle.oscal.catalog import Catalog
from trestle.tasks.base_task import TaskOutcome


def monkey_exception():
    """Monkey exception."""
    raise Exception('foobar')


def monkey_get_filelist(self, idir):
    """Monkey _get_filelist."""
    filelist = [pathlib.Path('foobar.profile')]
    return filelist


def test_cis_to_catalog_print_info(tmp_path: pathlib.Path):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.print_info()
    assert retval is None


def test_cis_to_catalog_simulate(tmp_path: pathlib.Path):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_cis_to_catalog_execute(tmp_path: pathlib.Path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate(tmp_path)


def _validate(tmp_path: pathlib.Path):
    # read catalog
    file_path = tmp_path / 'catalog.json'
    catalog = Catalog.oscal_read(file_path)
    # spot check
    assert len(catalog.groups) == 2
    # group 0
    group = catalog.groups[0]
    assert group.title == '1 Control Plane Components'
    assert len(group.groups) == 2
    assert len(group.groups[0].controls) == 3
    assert group.groups[0].title == '1.2 API Server'
    assert group.groups[0].controls[0].title == '1.2.1 Ensure that the --anonymous-auth argument is set to false'
    assert group.groups[0].controls[1].title == '1.2.2 Ensure that the --basic-auth-file argument is not set'
    assert group.groups[0].controls[2].title == '1.2.3 Ensure that the --token-auth-file parameter is not set'
    assert group.groups[1].title == '1.3 Controller Manager'
    assert len(group.groups[1].controls) == 1
    assert group.groups[1].controls[
        0].title == '1.3.2 Ensure that controller manager healthz endpoints are protected by RBAC. (Automated)'
    # group 1
    group = catalog.groups[1]
    assert group.title == '2 etcd'
    assert len(group.controls) == 2
    assert group.controls[0].title == '2.1 Ensure that the --cert-file and --key-file arguments are set as appropriate'
    assert group.controls[1].title == '2.2 Ensure that the --client-cert-auth argument is set to true'


def test_cis_to_catalog_config_missing(tmp_path: pathlib.Path):
    """Test config missing."""
    section = None
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_catalog_config_missing_key(tmp_path: pathlib.Path):
    """Test config missing key."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    section.pop('output-dir')
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_catalog_exception(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test _parse exception."""
    monkeypatch.setattr(cis_to_catalog.CisToCatalog, '_parse', monkey_exception)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_catalog_no_overwrite(tmp_path: pathlib.Path):
    """Test no overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    section['output-dir'] = str(tmp_path)
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    section['output-overwrite'] = 'false'
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_catalog_no_input(tmp_path: pathlib.Path):
    """Test no input."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    idir = str(tmp_path)
    ipth = pathlib.Path(idir) / 'foobar'
    ipth.mkdir(exist_ok=True, parents=True)
    section['input-dir'] = str(ipth.resolve())
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_catalog_no_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test no file."""
    monkeypatch.setattr(cis_to_catalog.CisToCatalog, '_get_filelist', monkey_get_filelist)
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_cis_to_catalog_input_bogus(tmp_path: pathlib.Path):
    """Test no input."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/cis-to-catalog/test-cis-to-catalog.config')
    config.read(config_path)
    section = config['task.cis-to-catalog']
    section['input-dir'] = 'tests/data/tasks/cis-to-catalog/input-bogus'
    tgt = cis_to_catalog.CisToCatalog(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE
