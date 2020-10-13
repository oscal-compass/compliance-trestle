# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for fs module."""

import pathlib
from typing import Dict, List

import pytest

from tests import test_utils

from trestle.core.const import IDX_SEP
from trestle.core.err import TrestleError
from trestle.oscal import catalog
from trestle.utils import fs


def test_ensure_directory(tmpdir):
    """Test ensure_directory function."""
    # Happy path
    fs.ensure_directory(tmpdir)

    # Unhappy path
    with pytest.raises(AssertionError):
        fs.ensure_directory(__file__)


def test_should_ignore():
    """Test should_ignore method."""
    assert fs.should_ignore('.test') is True
    assert fs.should_ignore('_test') is True
    assert fs.should_ignore('__test') is True
    assert fs.should_ignore('test') is False


def test_is_valid_project_root(tmp_dir):
    """Test is_valid_project_root method."""
    assert fs.is_valid_project_root(None) is False
    assert fs.is_valid_project_root('') is False
    assert fs.is_valid_project_root(tmp_dir) is False

    test_utils.ensure_trestle_config_dir(tmp_dir)
    assert fs.is_valid_project_root(tmp_dir) is True


def test_has_parent_path(tmp_dir):
    """Test has_parent_path method."""
    assert fs.has_parent_path(tmp_dir, pathlib.Path('')) is False
    assert fs.has_parent_path(tmp_dir, None) is False
    assert fs.has_parent_path(pathlib.Path('tests'), test_utils.BASE_TMP_DIR) is False
    assert fs.has_parent_path(pathlib.Path('/invalid/path'), test_utils.BASE_TMP_DIR) is False

    assert fs.has_parent_path(tmp_dir, test_utils.BASE_TMP_DIR) is True


def test_get_trestle_project_root(tmp_dir, rand_str):
    """Test get_trestle_project_root  method."""
    project_path: pathlib.Path = pathlib.Path.joinpath(tmp_dir, rand_str)
    sub_path: pathlib.Path = project_path.joinpath('samples2')
    fs.ensure_directory(sub_path)
    assert sub_path.exists() and sub_path.is_dir()

    # create a file
    sub_path.joinpath('readme.md').touch()

    # create a data-dir and a file
    sub_data_dir = pathlib.Path.joinpath(sub_path, 'data')
    fs.ensure_directory(sub_data_dir)
    sub_data_dir.joinpath('readme.md').touch()

    assert fs.get_trestle_project_root(sub_data_dir) is None

    test_utils.ensure_trestle_config_dir(project_path)
    assert fs.get_trestle_project_root(sub_data_dir) == project_path
    assert fs.get_trestle_project_root(sub_data_dir.joinpath('readme.md')) == project_path
    assert fs.get_trestle_project_root(sub_path.joinpath('readme.md')) == project_path
    assert fs.get_trestle_project_root(sub_path) == project_path
    assert fs.get_trestle_project_root(project_path.parent) is None


def test_has_trestle_project_in_path(tmp_dir, rand_str):
    """Test has_trestle_project_in_path method."""
    project_path: pathlib.Path = pathlib.Path.joinpath(tmp_dir, rand_str)
    sub_path: pathlib.Path = project_path.joinpath('samples2')
    fs.ensure_directory(sub_path)
    assert sub_path.exists() and sub_path.is_dir()

    # create a file
    sub_path.joinpath('readme.md').touch()

    # create a data-dir and a file
    sub_data_dir = pathlib.Path.joinpath(sub_path, 'data')
    fs.ensure_directory(sub_data_dir)

    # create a file
    sub_data_dir.joinpath('readme.md').touch()

    assert fs.has_trestle_project_in_path(pathlib.Path('/')) is False
    assert fs.has_trestle_project_in_path(sub_data_dir) is False

    test_utils.ensure_trestle_config_dir(project_path)
    assert fs.has_trestle_project_in_path(sub_data_dir) is True
    assert fs.has_trestle_project_in_path(sub_data_dir.joinpath('readme.md')) is True
    assert fs.has_trestle_project_in_path(sub_path.joinpath('readme.md')) is True
    assert fs.has_trestle_project_in_path(sub_path) is True
    assert fs.has_trestle_project_in_path(project_path.parent) is False


def test_clean_project_sub_path(tmp_dir, rand_str):
    """Test clean_project_sub_path method."""
    project_path: pathlib.Path = pathlib.Path.joinpath(tmp_dir, rand_str)
    sub_path: pathlib.Path = project_path.joinpath('samples')
    fs.ensure_directory(sub_path)
    assert sub_path.exists() and sub_path.is_dir()

    # create a file
    sub_path.joinpath('readme.md').touch()

    # create a data-dir and a file
    sub_data_dir = pathlib.Path.joinpath(sub_path, 'data')
    sub_data_dir_file = sub_data_dir.joinpath('readme.md')
    fs.ensure_directory(sub_data_dir)

    # create a file
    sub_data_dir_file.touch()

    try:
        # not having .trestle directory at the project root or tmp_dir should fail
        fs.clean_project_sub_path(sub_path)
    except TrestleError:
        pass

    test_utils.ensure_trestle_config_dir(project_path)

    fs.clean_project_sub_path(sub_data_dir_file)
    assert not sub_data_dir_file.exists()

    # create the file again
    with open(sub_data_dir_file, 'w+'):
        pass

    # clean the sub_path in the trestle project
    fs.clean_project_sub_path(sub_path)
    assert not sub_path.exists()


def test_load_file(tmp_dir):
    """Test load file."""
    json_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'sample-target-definition.json')
    yaml_file_path = pathlib.Path.joinpath(test_utils.YAML_TEST_DATA_PATH, 'good_target.yaml')

    assert fs.load_file(json_file_path) is not None
    assert fs.load_file(yaml_file_path) is not None

    try:
        sample_file_path = tmp_dir.joinpath('sample.txt')
        with open(sample_file_path, 'w'):
            fs.load_file(sample_file_path)
    except TrestleError:
        pass


def test_get_contextual_model_type(tmp_dir):
    """Test get model type and alias based on filesystem context."""
    with pytest.raises(TrestleError):
        fs.get_contextual_model_type(tmp_dir / 'invalidpath') is None

    with pytest.raises(TrestleError):
        fs.get_contextual_model_type(tmp_dir) is None

    create_sample_catalog_project(tmp_dir)

    catalogs_dir = tmp_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    metadata_dir = mycatalog_dir / 'metadata'
    roles_dir = metadata_dir / 'roles'
    rps_dir = metadata_dir / 'responsible-parties'
    props_dir = metadata_dir / 'properties'
    groups_dir = mycatalog_dir / 'groups'
    group_dir = groups_dir / f'00000{IDX_SEP}group'
    controls_dir = group_dir / 'controls'

    with pytest.raises(TrestleError):
        assert fs.get_contextual_model_type(catalogs_dir) is None

    assert fs.get_contextual_model_type(mycatalog_dir) == (catalog.Catalog, 'catalog')
    assert fs.get_contextual_model_type(mycatalog_dir / 'catalog.json') == (catalog.Catalog, 'catalog')
    assert fs.get_contextual_model_type(mycatalog_dir / 'back-matter.json') == (catalog.BackMatter, 'back-matter')
    assert fs.get_contextual_model_type(metadata_dir) == (catalog.Metadata, 'metadata')
    assert fs.get_contextual_model_type(metadata_dir / 'metadata.yaml') == (catalog.Metadata, 'metadata')
    assert fs.get_contextual_model_type(roles_dir) == (List[catalog.Role], 'roles')
    assert fs.get_contextual_model_type(roles_dir / 'roles.json') == (List[catalog.Role], 'roles')
    assert fs.get_contextual_model_type(roles_dir / '00000__role.json') == (catalog.Role, 'role')
    assert fs.get_contextual_model_type(rps_dir) == (Dict[str, catalog.ResponsibleParty], 'responsible-parties')
    assert fs.get_contextual_model_type(rps_dir / 'responsible-parties.json'
                                        ) == (Dict[str, catalog.ResponsibleParty], 'responsible-parties')
    assert fs.get_contextual_model_type(rps_dir / 'creator__responsible-party.json'
                                        ) == (catalog.ResponsibleParty, 'responsible-party')
    assert fs.get_contextual_model_type(props_dir) == (List[catalog.Prop], 'properties')
    assert fs.get_contextual_model_type(props_dir / 'properties.json') == (List[catalog.Prop], 'properties')
    assert fs.get_contextual_model_type(props_dir / f'00000{IDX_SEP}prop.json') == (catalog.Prop, 'prop')
    assert fs.get_contextual_model_type(groups_dir) == (List[catalog.Group], 'groups')
    assert fs.get_contextual_model_type(groups_dir / 'groups.json') == (List[catalog.Group], 'groups')
    assert fs.get_contextual_model_type(group_dir) == (catalog.Group, 'group')
    assert fs.get_contextual_model_type(group_dir / 'group.json') == (catalog.Group, 'group')
    assert fs.get_contextual_model_type(controls_dir) == (List[catalog.Control], 'controls')
    assert fs.get_contextual_model_type(controls_dir / 'controls.json') == (List[catalog.Control], 'controls')
    assert fs.get_contextual_model_type(controls_dir / f'00000{IDX_SEP}control.json') == (catalog.Control, 'control')


def create_sample_catalog_project(trestle_base_dir: pathlib.Path):
    """Create directory structure for a sample catalog named mycatalog."""
    test_utils.ensure_trestle_config_dir(trestle_base_dir)

    mycatalog_dir = trestle_base_dir / 'catalogs' / 'mycatalog'

    directories = [
        mycatalog_dir / 'metadata' / 'roles',
        mycatalog_dir / 'metadata' / 'responsible-parties',
        mycatalog_dir / 'metadata' / 'properties',
        mycatalog_dir / 'groups' / f'00000{IDX_SEP}group' / 'controls'
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    files = [
        mycatalog_dir / 'catalogs.json',
        mycatalog_dir / 'back-matter.json',
        mycatalog_dir / 'metadata' / 'metadata.json',
        mycatalog_dir / 'metadata' / 'roles' / f'00000{IDX_SEP}role.json',
        mycatalog_dir / 'metadata' / 'roles' / 'roles.json',
        mycatalog_dir / 'metadata' / 'responsible-parties' / f'creator{IDX_SEP}responsible-party.json',
        mycatalog_dir / 'metadata' / 'responsible-parties' / 'responsible-parties.json',
        mycatalog_dir / 'metadata' / 'properties' / f'00000{IDX_SEP}prop.json',
        mycatalog_dir / 'metadata' / 'properties' / 'properties.json',
        mycatalog_dir / 'groups' / 'groups.json',
        mycatalog_dir / 'groups' / f'00000{IDX_SEP}group' / 'group.json',
        mycatalog_dir / 'groups' / f'00000{IDX_SEP}group' / 'controls' / 'controls.json',
        mycatalog_dir / 'groups' / f'00000{IDX_SEP}group' / 'controls' / f'00000{IDX_SEP}control.json',
    ]

    for file in files:
        file.touch()


def test_extract_alias():
    """Test extraction of alias from filename or directory names."""
    assert fs.extract_alias(pathlib.Path('catalog')) == 'catalog'
    assert fs.extract_alias(pathlib.Path('/tmp/catalog')) == 'catalog'
    assert fs.extract_alias(pathlib.Path('/catalogs/mycatalog/catalog.json')) == 'catalog'
    assert fs.extract_alias(pathlib.Path('/catalogs/mycatalog/catalog.yaml')) == 'catalog'
    assert fs.extract_alias(pathlib.Path('responsible-parties')) == 'responsible-parties'
    assert fs.extract_alias(pathlib.Path('responsible-parties.json')) == 'responsible-parties'
    assert fs.extract_alias(pathlib.Path('/roles')) == 'roles'
    assert fs.extract_alias(pathlib.Path('/roles/roles.json')) == 'roles'
    assert fs.extract_alias(pathlib.Path(f'/roles/00000{IDX_SEP}role.json')) == 'role'
    assert fs.extract_alias(
        pathlib.Path(f'/metadata/responsible-parties/creator{IDX_SEP}responsible-party.json')
    ) == 'responsible-party'
