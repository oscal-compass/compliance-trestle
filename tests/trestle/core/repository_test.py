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

import os
import pathlib

import pytest

from tests import test_utils

import trestle.common.const as const
import trestle.oscal as oscal
import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.common.err import TrestleError
from trestle.core import generators, parser
from trestle.core.repository import AgileAuthoring, ManagedOSCAL, Repository

prof_name = 'comp_prof'
ssp_name = 'my_ssp'
cat_name = 'simplified_nist_catalog'
md_dir = 'test_md'


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
    catalog_data = generators.generate_sample_model(cat.Catalog)

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
    catalog_data = generators.generate_sample_model(cat.Catalog)

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
            'oscal-version': oscal.OSCAL_VERSION,
        },
        'back-matter': {
            'resources': [
                {'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'},
                {'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'},
            ]
        },
    }
    catalog_data = parser.parse_dict(dup_cat, 'trestle.oscal.catalog.Catalog')

    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match=r'Validation .* did not pass'):
        repo.import_model(catalog_data, 'imported')


def test_list(tmp_trestle_dir: pathlib.Path) -> None:
    """Test list models."""
    # 1. Empty list
    repo = Repository(tmp_trestle_dir)
    model_list = repo.list_models(cat.Catalog)
    assert len(model_list) == 0

    # model exists
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo.import_model(catalog_data, 'imported')
    model_list = repo.list_models(cat.Catalog)
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
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    managed_oscal = repo.get_model(cat.Catalog, 'imported')
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
        repo.get_model(cat.Catalog, 'anything')


def test_delete(tmp_trestle_dir: pathlib.Path) -> None:
    """Test delete model."""
    # create a model
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    # created model is 'dist' folder also
    repo.assemble_model(cat.Catalog, 'imported')
    success = repo.delete_model(cat.Catalog, 'imported')
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
        repo.delete_model(cat.Catalog, 'anything')


def test_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test assemble model."""
    # create a model
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    success = repo.assemble_model(cat.Catalog, 'imported')
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
    with pytest.raises(TrestleError):
        repo.assemble_model(cat.Catalog, 'anything')


def test_validate(tmp_trestle_dir: pathlib.Path) -> None:
    """Test validate model."""
    # create a model
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    success = repo.validate_model(cat.Catalog, 'imported')
    assert success


def test_validate_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model."""
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='not a top level model'):
        repo.validate_model(oscal.common.Metadata, 'anything')


def test_validate_model_not_exists(tmp_trestle_dir: pathlib.Path) -> None:
    """Assemble model does not exists."""
    repo = Repository(tmp_trestle_dir)
    success = repo.validate_model(cat.Catalog, 'anything')
    assert not success


def test_managed_oscal(tmp_trestle_dir: pathlib.Path) -> None:
    """Test creating Managed OSCAL object."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    assert managed.model_dir == tmp_trestle_dir / 'catalogs' / 'imported'


def test_managed_invalid_root(tmp_path: pathlib.Path) -> None:
    """Invalid trestle_root directory while creating Managed OSCAL object."""
    with pytest.raises(TrestleError, match='not a valid Trestle root'):
        ManagedOSCAL(tmp_path, cat.Catalog, 'anything')


def test_managed_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top model while creating Managed OSCAL object."""
    with pytest.raises(TrestleError, match='not a top level model'):
        ManagedOSCAL(tmp_trestle_dir, oscal.catalog.Group2, 'anything')


def test_managed_invalid_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid model directory while creating Managed OSCAL object."""
    with pytest.raises(TrestleError, match=r'Model .* does not exist'):
        ManagedOSCAL(tmp_trestle_dir, cat.Catalog, 'anything')


def test_managed_file_not_exist(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model file does not exist while creating a Managed OSCAL object."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # delete file
    managed.filepath.unlink()
    with pytest.raises(TrestleError, match=r'Model file .* does not exist'):
        ManagedOSCAL(tmp_trestle_dir, cat.Catalog, 'imported')


def test_managed_read(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model read."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    model = managed.read()
    assert model.uuid == catalog_data.uuid


def test_managed_write(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model write."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # generate another catalog data for writing
    catalog_data = generators.generate_sample_model(cat.Catalog)
    success = managed.write(catalog_data)
    assert success


def test_managed_write_invalid_top_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Invalid top level model while writing."""
    # generate catalog data and import
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')

    # generate another catalog data for writing
    catalog_data = generators.generate_sample_model(oscal.catalog.Group2)

    with pytest.raises(TrestleError, match='not a top level model'):
        managed.write(catalog_data)


def test_managed_split(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model split."""
    # generate catalog data and import
    filepath = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    catalog_data = cat.Catalog.oscal_read(filepath)
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
    catalog_data = generators.generate_sample_model(cat.Catalog)
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
    catalog_data = cat.Catalog.oscal_read(filepath)
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
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    success = managed.validate()
    assert success


# Test default agile authoring paths to ensure call from repository are correct


def test_agile_authoring_catalog(tmp_trestle_dir: pathlib.Path) -> None:
    """Test catalog generate and assemble through API."""
    test_utils.load_valid_model_from_json(tmp_trestle_dir, cat_name, cat_name, cat.Catalog)

    authoring = AgileAuthoring(tmp_trestle_dir)

    md_cat = os.path.join(md_dir, cat_name)
    success = authoring.generate_catalog_markdown(cat_name, md_cat)

    assert success
    assert pathlib.Path(tmp_trestle_dir / md_cat).exists()

    new_cat = 'temp_cat'
    success = authoring.assemble_catalog_markdown(cat_name, new_cat, md_cat)
    assert success
    assert pathlib.Path(tmp_trestle_dir, const.MODEL_DIR_CATALOG, new_cat).exists()


def test_agile_authoring_profile(tmp_trestle_dir: pathlib.Path) -> None:
    """Test profile generate and assemble through API."""
    test_utils.load_valid_model_from_json(tmp_trestle_dir, cat_name, cat_name, cat.Catalog)
    test_utils.load_valid_model_from_json(tmp_trestle_dir, prof_name, prof_name, prof.Profile)

    authoring = AgileAuthoring(tmp_trestle_dir)

    md_prof = os.path.join(md_dir, prof_name)
    success = authoring.generate_profile_markdown(prof_name, md_prof)

    assert success
    assert pathlib.Path(tmp_trestle_dir / md_prof).exists()

    new_prof = 'temp_prof'
    success = authoring.assemble_profile_markdown(prof_name, new_prof, md_prof)
    assert success
    assert pathlib.Path(tmp_trestle_dir, const.MODEL_DIR_PROFILE, new_prof).exists()


def test_agile_authoring_component(tmp_trestle_dir: pathlib.Path) -> None:
    """Test component generate and assemble through API."""
    comp_name = test_utils.setup_component_generate(tmp_trestle_dir)
    authoring = AgileAuthoring(tmp_trestle_dir)

    md_comp = os.path.join(md_dir, comp_name)
    success = authoring.generate_component_definition_markdown(comp_name, md_comp)

    assert success
    assert pathlib.Path(tmp_trestle_dir / md_comp).exists()

    new_comp = 'temp_comp'
    success = authoring.assemble_component_definition_markdown(comp_name, new_comp, md_comp)
    assert success
    assert pathlib.Path(tmp_trestle_dir, const.MODEL_DIR_COMPDEF, new_comp).exists()


def test_agile_authoring_ssp(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp generate and assemble through API."""
    args, _ = test_utils.setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    authoring = AgileAuthoring(tmp_trestle_dir)

    success = authoring.generate_ssp_markdown(args.profile, args.output, args.compdefs)

    assert success
    assert pathlib.Path(tmp_trestle_dir / args.output).exists()

    success = authoring.assemble_ssp_markdown(ssp_name, ssp_name, args.output, args.compdefs)
    assert success
    assert pathlib.Path(tmp_trestle_dir, const.MODEL_DIR_SSP, args.output).exists()


# ---------------------------------------------------------------------------
# Coverage-improvement tests for trestle/core/repository.py
# ---------------------------------------------------------------------------


def test_managed_oscal_invalid_top_model_write(tmp_trestle_dir: pathlib.Path) -> None:
    """ManagedOSCAL.write: line 94 – raises TrestleError when non-top-level model is written."""
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    import trestle.oscal as oscal

    non_top = generators.generate_sample_model(oscal.catalog.Group2)
    with pytest.raises(TrestleError, match='not a top level model'):
        managed.write(non_top)


def test_managed_split_exception(tmp_trestle_dir: pathlib.Path) -> None:
    """ManagedOSCAL.split: lines 145-146 – bad element path raises TrestleError."""
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    with pytest.raises(TrestleError, match='Error in splitting model'):
        managed.split(pathlib.Path('catalog.json'), ['catalog.NONEXISTENT_FIELD.*'])


def test_managed_merge_exception(tmp_trestle_dir: pathlib.Path) -> None:
    """ManagedOSCAL.merge: lines 170-171 – bad element path raises TrestleError."""
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    managed = repo.import_model(catalog_data, 'imported')
    with pytest.raises(TrestleError, match='Error in merging model'):
        managed.merge(['catalog.NONEXISTENT_FIELD.*'])


def test_repository_import_validation_rollback(tmp_trestle_dir: pathlib.Path) -> None:
    """Repository.import_model: lines 240-252 – validation failure triggers rollback."""
    import trestle.oscal as oscal
    from trestle.core import parser

    dup_cat = {
        'uuid': '525f94af-8007-4376-8069-aa40179e0f6e',
        'metadata': {
            'title': 'Generic catalog created by trestle.',
            'last-modified': '2020-12-11T02:04:51.053+00:00',
            'version': '0.0.0',
            'oscal-version': oscal.OSCAL_VERSION,
        },
        'back-matter': {
            'resources': [
                {'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'},
                {'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'},
            ]
        },
    }
    catalog_data = parser.parse_dict(dup_cat, 'trestle.oscal.catalog.Catalog')
    repo = Repository(tmp_trestle_dir)
    with pytest.raises(TrestleError, match='Validation'):
        repo.import_model(catalog_data, 'imported')
    # After rollback the file should not exist
    cat_path = tmp_trestle_dir / 'catalogs' / 'imported' / 'catalog.json'
    assert not cat_path.exists()


def test_repository_delete_with_dist_file(tmp_trestle_dir: pathlib.Path) -> None:
    """Repository.delete_model: lines 310-315 – dist file is cleaned up when it exists."""
    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')
    # Assemble to create dist file
    repo.assemble_model(cat.Catalog, 'imported')
    dist_path = tmp_trestle_dir / 'dist' / 'catalogs' / 'imported.json'
    assert dist_path.exists()
    success = repo.delete_model(cat.Catalog, 'imported')
    assert success
    assert not dist_path.exists()


def test_repository_assemble_exception(tmp_trestle_dir: pathlib.Path, monkeypatch) -> None:
    """Repository.assemble_model: lines 338-339 – exception from AssembleCmd is re-raised."""
    import trestle.core.commands.assemble as assemblecmd

    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')

    def _bad_assemble(*args, **kwargs):
        raise RuntimeError('forced assemble error')

    monkeypatch.setattr(assemblecmd.AssembleCmd, 'assemble_model', _bad_assemble)
    with pytest.raises(TrestleError, match='Error in assembling model'):
        repo.assemble_model(cat.Catalog, 'imported')


def test_repository_validate_exception(tmp_trestle_dir: pathlib.Path, monkeypatch) -> None:
    """Repository.validate_model: lines 360-361 – exception from ValidateCmd is re-raised."""
    import trestle.core.commands.validate as validatecmd

    catalog_data = generators.generate_sample_model(cat.Catalog)
    repo = Repository(tmp_trestle_dir)
    repo.import_model(catalog_data, 'imported')

    def _bad_validate(*args, **kwargs):
        raise RuntimeError('forced validate error')

    monkeypatch.setattr(validatecmd.ValidateCmd, '_run', _bad_validate)
    with pytest.raises(TrestleError, match='Error in validating model'):
        repo.validate_model(cat.Catalog, 'imported')


def test_agile_authoring_catalog_exception(tmp_trestle_dir: pathlib.Path, monkeypatch) -> None:
    """AgileAuthoring.generate_catalog_markdown and assemble: exception paths (lines 409-410, 546-547)."""
    import trestle.core.commands.author.catalog as catalogauthorcmd
    from trestle.core.repository import AgileAuthoring
    import tests.test_utils as test_utils

    test_utils.load_from_json(tmp_trestle_dir, 'simplified_nist_catalog', 'simplified_nist_catalog', cat.Catalog)
    authoring = AgileAuthoring(tmp_trestle_dir)

    def _bad_run(*args, **kwargs):
        raise RuntimeError('forced error')

    monkeypatch.setattr(catalogauthorcmd.CatalogGenerate, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error generate markdown for catalog'):
        authoring.generate_catalog_markdown('simplified_nist_catalog', 'md_out')

    monkeypatch.setattr(catalogauthorcmd.CatalogAssemble, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error assembling catalog'):
        authoring.assemble_catalog_markdown('simplified_nist_catalog', 'new_cat', 'md_out')


def test_agile_authoring_profile_exception(tmp_trestle_dir: pathlib.Path, monkeypatch) -> None:
    """AgileAuthoring profile generate/assemble exception paths (lines 450-451, 583-584)."""
    import trestle.core.commands.author.prof as profileauthorcmd
    from trestle.core.repository import AgileAuthoring
    import tests.test_utils as test_utils

    test_utils.load_from_json(tmp_trestle_dir, 'comp_prof', 'comp_prof', prof.Profile)
    authoring = AgileAuthoring(tmp_trestle_dir)

    def _bad_run(*args, **kwargs):
        raise RuntimeError('forced error')

    monkeypatch.setattr(profileauthorcmd.ProfileGenerate, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error generate markdown for profile'):
        authoring.generate_profile_markdown('comp_prof', 'md_out')

    monkeypatch.setattr(profileauthorcmd.ProfileAssemble, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error assembling profile'):
        authoring.assemble_profile_markdown('comp_prof', 'new_prof', 'md_out')


def test_agile_authoring_component_exception(tmp_trestle_dir: pathlib.Path, monkeypatch) -> None:
    """AgileAuthoring component generate/assemble exception paths (lines 478-479, 603-604)."""
    import trestle.core.commands.author.component as componentauthorcmd
    from trestle.core.repository import AgileAuthoring
    import tests.test_utils as test_utils

    comp_name = test_utils.setup_component_generate(tmp_trestle_dir)
    authoring = AgileAuthoring(tmp_trestle_dir)

    def _bad_run(*args, **kwargs):
        raise RuntimeError('forced error')

    monkeypatch.setattr(componentauthorcmd.ComponentGenerate, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error generating markdown for component definition'):
        authoring.generate_component_definition_markdown(comp_name, 'md_out')

    monkeypatch.setattr(componentauthorcmd.ComponentAssemble, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error assembling component definition'):
        authoring.assemble_component_definition_markdown(comp_name, 'new_comp', 'md_out')


def test_agile_authoring_ssp_exception(tmp_trestle_dir: pathlib.Path, monkeypatch) -> None:
    """AgileAuthoring ssp generate/assemble exception paths (lines 513-514, 642-643)."""
    import trestle.core.commands.author.ssp as sspauthorcmd
    from trestle.core.repository import AgileAuthoring
    import tests.test_utils as test_utils

    args, _ = test_utils.setup_for_ssp(tmp_trestle_dir, 'comp_prof', 'my_ssp')
    authoring = AgileAuthoring(tmp_trestle_dir)

    def _bad_run(*args, **kwargs):
        raise RuntimeError('forced error')

    monkeypatch.setattr(sspauthorcmd.SSPGenerate, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error in generating markdown for ssp'):
        authoring.generate_ssp_markdown(args.profile, args.output, args.compdefs)

    monkeypatch.setattr(sspauthorcmd.SSPAssemble, '_run', _bad_run)
    with pytest.raises(TrestleError, match='Error assembling ssp'):
        authoring.assemble_ssp_markdown('my_ssp', 'my_ssp', args.output, args.compdefs)
