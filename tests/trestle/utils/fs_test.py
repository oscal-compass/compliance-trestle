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

import os
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


def test_is_valid_project_model_path(tmp_dir):
    """Test is_valid_project_model method."""
    assert fs.is_valid_project_model_path(None) is False
    assert fs.is_valid_project_model_path('') is False
    assert fs.is_valid_project_model_path(tmp_dir) is False

    test_utils.ensure_trestle_config_dir(tmp_dir)
    assert fs.is_valid_project_model_path(tmp_dir) is False

    create_sample_catalog_project(tmp_dir)

    catalog_dir = tmp_dir / 'catalogs'
    assert fs.is_valid_project_model_path(catalog_dir) is False

    mycatalog_dir = catalog_dir / 'mycatalog'
    assert fs.is_valid_project_model_path(mycatalog_dir) is True

    metadata_dir = mycatalog_dir / 'metadata'
    assert fs.is_valid_project_model_path(metadata_dir) is True


def test_get_project_model_path(tmp_dir):
    """Test get_project_model_path  method."""
    assert fs.get_project_model_path(None) is None
    assert fs.get_project_model_path('') is None
    assert fs.get_project_model_path(tmp_dir) is None

    test_utils.ensure_trestle_config_dir(tmp_dir)
    assert fs.get_project_model_path(tmp_dir) is None

    create_sample_catalog_project(tmp_dir)

    catalog_dir = tmp_dir / 'catalogs'
    assert fs.get_project_model_path(catalog_dir) is None

    mycatalog_dir = catalog_dir / 'mycatalog'
    assert fs.get_project_model_path(mycatalog_dir) == mycatalog_dir

    metadata_dir = mycatalog_dir / 'metadata'
    assert fs.get_project_model_path(metadata_dir) == mycatalog_dir


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
    catalog_dir = mycatalog_dir / 'catalog'
    metadata_dir = catalog_dir / 'metadata'
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
    assert fs.get_contextual_model_type(catalog_dir / 'back-matter.json') == (catalog.BackMatter, 'catalog.back-matter')
    assert fs.get_contextual_model_type(catalog_dir / 'metadata.yaml') == (catalog.Metadata, 'catalog.metadata')
    assert fs.get_contextual_model_type(metadata_dir) == (catalog.Metadata, 'catalog.metadata')
    assert fs.get_contextual_model_type(roles_dir) == (List[catalog.Role], 'catalog.metadata.roles')
    assert fs.get_contextual_model_type(roles_dir / '00000__role.json') == (catalog.Role, 'catalog.metadata.roles.role')
    assert fs.get_contextual_model_type(rps_dir) == (
        Dict[str, catalog.ResponsibleParty], 'catalog.metadata.responsible-parties'
    )
    assert fs.get_contextual_model_type(
        rps_dir / 'creator__responsible-party.json'
    ) == (catalog.ResponsibleParty, 'catalog.metadata.responsible-parties.responsible-party')
    assert fs.get_contextual_model_type(props_dir) == (List[catalog.Prop], 'catalog.metadata.properties')
    assert fs.get_contextual_model_type(props_dir / f'00000{IDX_SEP}prop.json'
                                        ) == (catalog.Prop, 'catalog.metadata.properties.prop')
    assert fs.get_contextual_model_type(groups_dir) == (List[catalog.Group], 'catalog.groups')
    assert fs.get_contextual_model_type(groups_dir / f'00000{IDX_SEP}group.json'
                                        ) == (catalog.Group, 'catalog.groups.group')
    assert fs.get_contextual_model_type(group_dir) == (catalog.Group, 'catalog.groups.group')
    assert fs.get_contextual_model_type(controls_dir) == (List[catalog.Control], 'catalog.groups.group.controls')
    assert fs.get_contextual_model_type(controls_dir / f'00000{IDX_SEP}control.json'
                                        ) == (catalog.Control, 'catalog.groups.group.controls.control')


def create_sample_catalog_project(trestle_base_dir: pathlib.Path):
    """Create directory structure for a sample catalog named mycatalog."""
    test_utils.ensure_trestle_config_dir(trestle_base_dir)

    mycatalog_dir = trestle_base_dir / 'catalogs' / 'mycatalog'

    directories = [
        mycatalog_dir / 'catalog' / 'metadata' / 'roles',
        mycatalog_dir / 'catalog' / 'metadata' / 'responsible-parties',
        mycatalog_dir / 'catalog' / 'metadata' / 'properties',
        mycatalog_dir / 'catalog' / 'groups' / f'00000{IDX_SEP}group' / 'controls'
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    files = [
        mycatalog_dir / 'catalog.json',
        mycatalog_dir / 'catalog' / 'back-matter.json',
        mycatalog_dir / 'catalog' / 'metadata.json',
        mycatalog_dir / 'catalog' / 'metadata' / 'roles' / f'00000{IDX_SEP}role.json',
        mycatalog_dir / 'catalog' / 'metadata' / 'responsible-parties' / f'creator{IDX_SEP}responsible-party.json',
        mycatalog_dir / 'catalog' / 'metadata' / 'properties' / f'00000{IDX_SEP}prop.json',
        mycatalog_dir / 'catalog' / 'groups' / f'00000{IDX_SEP}group.json',
        mycatalog_dir / 'catalog' / 'groups' / f'00000{IDX_SEP}group' / 'controls' / f'00000{IDX_SEP}control.json',
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


def test_get_stripped_contextual_model(tmp_dir):
    """Test get stripped model type and alias based on filesystem context."""
    with pytest.raises(TrestleError):
        fs.get_stripped_contextual_model(tmp_dir / 'invalidpath') is None

    with pytest.raises(TrestleError):
        fs.get_stripped_contextual_model(tmp_dir) is None

    create_sample_catalog_project(tmp_dir)

    catalogs_dir = tmp_dir / 'catalogs'
    with pytest.raises(TrestleError):
        assert fs.get_stripped_contextual_model(catalogs_dir) is None

    def check_stripped_catalog():
        assert 'uuid' in alias_to_field_map
        assert 'metadata' not in alias_to_field_map
        assert 'back-matter' not in alias_to_field_map
        assert 'groups' not in alias_to_field_map

    mycatalog_dir = catalogs_dir / 'mycatalog'
    stripped_catalog = fs.get_stripped_contextual_model(mycatalog_dir)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_catalog()

    stripped_catalog = fs.get_stripped_contextual_model(mycatalog_dir / 'catalog.json')
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_catalog()

    def check_stripped_metadata():
        assert 'title' in alias_to_field_map
        assert 'published' in alias_to_field_map
        assert 'last-modified' in alias_to_field_map
        assert 'version' in alias_to_field_map
        assert 'oscal-version' in alias_to_field_map
        assert 'revision-history' in alias_to_field_map
        assert 'document-ids' in alias_to_field_map
        assert 'links' in alias_to_field_map
        assert 'locations' in alias_to_field_map
        assert 'parties' in alias_to_field_map
        assert 'remarks' in alias_to_field_map
        assert 'roles' not in alias_to_field_map
        assert 'responsible-properties' not in alias_to_field_map
        assert 'properties' not in alias_to_field_map

    catalog_dir = mycatalog_dir / 'catalog'
    metadata_dir = catalog_dir / 'metadata'
    stripped_catalog = fs.get_stripped_contextual_model(metadata_dir)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_metadata()

    stripped_catalog = fs.get_stripped_contextual_model(catalog_dir / 'metadata.json')
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_metadata()

    groups_dir = catalog_dir / 'groups'
    stripped_catalog = fs.get_stripped_contextual_model(groups_dir)

    assert stripped_catalog[0].__name__ == 'Groups'
    assert stripped_catalog[1] == 'catalog.groups'

    def check_stripped_group():
        assert 'id' in alias_to_field_map
        assert 'class' in alias_to_field_map
        assert 'title' in alias_to_field_map
        assert 'parameters' in alias_to_field_map
        assert 'properties' in alias_to_field_map
        assert 'annotations' in alias_to_field_map
        assert 'links' in alias_to_field_map
        assert 'parts' in alias_to_field_map
        assert 'groups' in alias_to_field_map
        assert 'controls' not in alias_to_field_map

    stripped_catalog = fs.get_stripped_contextual_model(groups_dir / f'00000{IDX_SEP}group')
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_group()

    stripped_catalog = fs.get_stripped_contextual_model(groups_dir / f'00000{IDX_SEP}group.json')
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_group()


def test_get_singular_alias():
    """Test get_singular_alias function."""
    # Not of collection type
    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='catalog')

    # Not fullpath. It should be 'catalog.metadata' instead
    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='metadata.something')

    # Invalid alias_path
    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='invalid')
    # Invalid alias_path
    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='')

    assert 'responsible-party' == fs.get_singular_alias(alias_path='catalog.metadata.responsible-parties')
    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='catalog.metadata.responsible-parties.*')
    assert 'prop' == fs.get_singular_alias(alias_path='catalog.metadata.responsible-parties.*.properties')

    assert 'role' == fs.get_singular_alias(alias_path='catalog.metadata.roles')
    assert 'prop' == fs.get_singular_alias(alias_path='catalog.metadata.properties')

    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='target-definition.targets.target-control-implementations')
    assert 'target-control-implementation' == fs.get_singular_alias(
        alias_path='target-definition.targets.*.target-control-implementations'
    )
    assert 'target-control-implementation' == fs.get_singular_alias(
        alias_path='target-definition.targets.8f95894c-5e6b-4e84-92d0-a730429f08fc.target-control-implementations'
    )
    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='target-definitions.targets.*.target-control-implementations')

    assert 'control' == fs.get_singular_alias(alias_path='catalog.groups.*.controls.*.controls')


def test_contextual_get_singular_alias(tmp_dir):
    """Test get_singular_alias in contextual mode."""
    # Contextual model tests
    create_sample_catalog_project(tmp_dir)
    catalogs_dir = tmp_dir.absolute() / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'
    metadata_dir = catalog_dir / 'metadata'
    groups_dir = catalog_dir / 'groups'
    group_dir = groups_dir / f'00000{IDX_SEP}group'

    cwd = os.getcwd()

    os.chdir(mycatalog_dir)
    assert 'responsible-party' == fs.get_singular_alias(
        alias_path='catalog.metadata.responsible-parties', contextual_mode=True
    )
    # Both should work to deal with the case back-matter is already split from the catalog in a separate file
    assert 'resource' == fs.get_singular_alias(alias_path='catalog.back-matter.resources', contextual_mode=True)
    assert 'resource' == fs.get_singular_alias(alias_path='back-matter.resources', contextual_mode=True)

    os.chdir(metadata_dir)
    with pytest.raises(TrestleError):
        fs.get_singular_alias('metadata.roles', contextual_mode=False)
    alias = fs.get_singular_alias('metadata.roles', contextual_mode=True)
    assert alias == 'role'
    with pytest.raises(TrestleError):
        fs.get_singular_alias(alias_path='metadata.responsible-parties.*', contextual_mode=True)
    assert 'prop' == fs.get_singular_alias(alias_path='metadata.responsible-parties.*.properties', contextual_mode=True)

    os.chdir(groups_dir)
    assert 'control' == fs.get_singular_alias(alias_path='groups.*.controls.*.controls', contextual_mode=True)

    os.chdir(group_dir)
    assert 'control' == fs.get_singular_alias(alias_path='group.controls.*.controls', contextual_mode=True)

    os.chdir(cwd)
