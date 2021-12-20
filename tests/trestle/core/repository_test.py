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
"""Tests for trestle Repository APIs."""

import pathlib

import pytest

from tests import test_utils

import trestle.core.parser as parser
import trestle.oscal as oscal
from trestle.core import generators
from trestle.core.err import TrestleError
from trestle.core.repository import ManagedOSCAL, Repository


def test_repo(tmp_trestle_dir: pathlib.Path) -> None:
    """Test creating Repository object."""
    repo = Repository(tmp_trestle_dir)
    assert repo.root_dir == tmp_trestle_dir


def test_repo_invalid_root(tmp_path: pathlib.Path) -> None:
    """Invalid trestle_root directory while creating Repository object."""
    with pytest.raises(TrestleError, match='not a valid Trestle root'):
        Repository(tmp_path)


def test_import(tmp_trestle_dir: pathlib.Path) -> None:
    """Test import."""
    # Generate sample catalog model
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)

    repo = Repository(tmp_trestle_dir)
    managed_oscal = repo.import_model(catalog_data, 'imported')
    assert managed_oscal.root_dir == tmp_trestle_dir
    assert managed_oscal.model_name == 'imported'
    assert managed_oscal.model_type == catalog_data.__class__
    assert managed_oscal.filepath.exists()


def test_import_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model."""
    # try to import Metadata
    metadata = generators.generate_sample_model(oscal.common.Metadata)

    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='not a top level model'):
        repo.import_model(metadata, 'imported')


def test_import_model_exists(tmp_trestle_dir: pathlib.Path) -> None:
    """Model already exists."""
    # Generate sample catalog model
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)

    repo = Repository(tmp_trestle_dir)
    managed_oscal = repo.import_model(catalog_data, 'imported')
    assert managed_oscal.filepath.exists()

    with pytest.raises(TrestleError, match=r'OSCAL file .* exists'):
        repo.import_model(catalog_data, 'imported')


def test_import_validation_fail(tmp_trestle_dir: pathlib.Path) -> None:
    """Validation failed."""
    # catalog data
    dup_cat = {
        'uuid': '525f94af-8007-4376-8069-aa40179e0f6e',
        'metadata': {
            'title': 'Generic catalog created by trestle.',
            'last-modified': '2020-12-11T02:04:51.053+00:00',
            'version': '0.0.0',
            'oscal-version': oscal.OSCAL_VERSION
        },
        'back-matter': {
            'resources': [
                {
                    'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'
                }, {
                    'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'
                }
            ]
        }
    }
    catalog_data = parser.parse_dict(dup_cat, 'trestle.oscal.catalog.Catalog')

    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match=r'Validation .* did not pass'):
        repo.import_model(catalog_data, 'imported')


def test_list(tmp_trestle_dir: pathlib.Path) -> None:
    """Test list models."""
    # 1. Empty list
    repo = Repository(tmp_trestle_dir)
    model_list = repo.list_models(oscal.catalog.Catalog)
    assert len(model_list) == 0

    # model exists
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo.import_model(catalog_data, 'imported')
    model_list = repo.list_models(oscal.catalog.Catalog)
    assert len(model_list) == 1
    assert 'imported' in model_list


def test_list_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='not a top level model'):
        repo.list_models(oscal.common.Metadata)


def test_get(tmp_trestle_dir: pathlib.Path) -> None:
    """Test get model."""
    # create a model
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    managed_oscal = repo.get_model(oscal.catalog.Catalog, 'imported')
    assert managed_oscal.model_name == 'imported'


def test_get_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='not a top level model'):
        repo.get_model(oscal.common.Metadata, 'anything')


def test_get_model_not_exists(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid get model does not exists."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='does not exist'):
        repo.get_model(oscal.catalog.Catalog, 'anything')


def test_delete(tmp_trestle_dir: pathlib.Path) -> None:
    """Test delete model."""
    # create a model
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    # created model is 'dist' folder also
    repo.assemble_model(oscal.catalog.Catalog, 'imported')
    success = repo.delete_model(oscal.catalog.Catalog, 'imported')
    assert success


def test_delete_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='not a top level model'):
        repo.delete_model(oscal.common.Metadata, 'anything')


def test_delete_model_not_exists(tmp_trestle_dir: pathlib.Path) -> None:
    """Delete model does not exists."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='does not exist'):
        repo.delete_model(oscal.catalog.Catalog, 'anything')


def test_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test assemble model."""
    # create a model
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    success = repo.assemble_model(oscal.catalog.Catalog, 'imported')
    assert success
    dist_model_path = pathlib.Path(tmp_trestle_dir, 'dist', 'catalogs', 'imported.json')
    assert dist_model_path.exists()


def test_assemble_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='not a top level model'):
        repo.assemble_model(oscal.common.Metadata, 'anything')


def test_assemble_model_not_exists(tmp_trestle_dir: pathlib.Path) -> None:
    """Assemble model does not exists."""
    repo = Repository(tmp_trestle_dir)
    success = repo.assemble_model(oscal.catalog.Catalog, 'anything')
    assert not success


def test_validate(tmp_trestle_dir: pathlib.Path) -> None:
    """Test validate model."""
    # create a model
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    success = repo.validate_model(oscal.catalog.Catalog, 'imported')
    assert success


def test_validate_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='not a top level model'):
        repo.validate_model(oscal.common.Metadata, 'anything')


def test_validate_model_not_exists(tmp_trestle_dir: pathlib.Path) -> None:
    """Assemble model does not exists."""
    repo = Repository(tmp_trestle_dir)
    success = repo.validate_model(oscal.catalog.Catalog, 'anything')
    assert not success


def test_managed_oscal(tmp_trestle_dir: pathlib.Path) -> None:
    """Test creating Managed OSCAL object."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    assert managed.model_dir == tmp_trestle_dir / 'catalogs' / 'imported'


def test_managed_invalid_root(tmp_path: pathlib.Path) -> None:
    """Invalid trestle_root directory while creating Managed OSCAL object."""
    with pytest.raises(TrestleError, match='not a valid Trestle root'):
        ManagedOSCAL(tmp_path, oscal.catalog.Catalog, 'anything')


def test_managed_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model while creating Managed OSCAL object."""
    with pytest.raises(TrestleError, match='not a top level model'):
        ManagedOSCAL(tmp_trestle_dir, oscal.catalog.Group, 'anything')


def test_managed_invalid_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid model directory while creating Managed OSCAL object."""
    with pytest.raises(TrestleError, match=r'Model .* does not exist'):
        ManagedOSCAL(tmp_trestle_dir, oscal.catalog.Catalog, 'anything')


def test_managed_file_not_exist(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model file does not exist while creating a Managed OSCAL object."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # delete file
    managed.filepath.unlink()
    with pytest.raises(TrestleError, match=r'Model file .* does not exist'):
        ManagedOSCAL(tmp_trestle_dir, oscal.catalog.Catalog, 'imported')


def test_managed_read(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model read."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    model = managed.read()
    assert model.uuid == catalog_data.uuid


def test_managed_write(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model write."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # generate another catalog data for writing
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    success = managed.write(catalog_data)
    assert success


def test_managed_write_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top level model while writing."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # generate another catalog data for writing
    catalog_data = generators.generate_sample_model(oscal.catalog.Group)

    with pytest.raises(TrestleError, match='not a top level model'):
        managed.write(catalog_data)


def test_managed_split(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model split."""
    # generate catalog data and import
    filepath = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    catalog_data = parser.parse_file(filepath, None)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # store current working directory
    cwd = pathlib.Path.cwd()

    # test splitting
    success = managed.split(pathlib.Path('catalog.json'), ['catalog.metadata'])
    assert success
    assert pathlib.Path(tmp_trestle_dir / 'catalogs' / 'imported' / 'catalog' / 'metadata.json').exists()

    # test cwd is restored after splitting
    assert pathlib.Path.cwd() == cwd

    success = managed.split(pathlib.Path('catalog/metadata.json'), ['metadata.props'])
    assert success
    assert pathlib.Path(tmp_trestle_dir / 'catalogs' / 'imported' / 'catalog' / 'metadata' / 'props.json').exists()


def test_managed_split_multi(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model split multiple elements."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # store current working directory
    cwd = pathlib.Path.cwd()

    # test splitting
    success = managed.split(pathlib.Path('catalog.json'), ['catalog.metadata', 'catalog.groups.*'])
    assert success

    # test cwd is restored after splitting
    assert pathlib.Path.cwd() == cwd


def test_managed_merge(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model merge."""
    # generate catalog data and import and split
    filepath = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    catalog_data = parser.parse_file(filepath, None)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # split should be success
    success = managed.split(pathlib.Path('catalog.json'), ['catalog.metadata'])
    assert success
    assert pathlib.Path(tmp_trestle_dir / 'catalogs' / 'imported' / 'catalog' / 'metadata.json').exists()

    success = managed.split(pathlib.Path('catalog/metadata.json'), ['metadata.props'])
    assert success
    assert pathlib.Path(tmp_trestle_dir / 'catalogs' / 'imported' / 'catalog' / 'metadata' / 'props.json').exists()

    # store current working directory before merge
    cwd = pathlib.Path.cwd()

    # merge should be success
    success = managed.merge(['metadata.*'], pathlib.Path('catalog'))
    assert success
    assert not pathlib.Path(tmp_trestle_dir / 'catalogs' / 'imported' / 'catalog' / 'metadata' / 'props.json').exists()

    success = managed.merge(['catalog.*'])
    assert success
    assert not pathlib.Path(tmp_trestle_dir / 'catalogs' / 'imported' / 'catalog' / 'metadata.json').exists()

    # test cwd is restored after splitting
    assert pathlib.Path.cwd() == cwd


def test_managed_validate(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model validate."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(oscal.catalog.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    success = managed.validate()
    assert success
