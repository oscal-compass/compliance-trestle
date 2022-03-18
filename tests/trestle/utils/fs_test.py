# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Tests for fs module."""

import pathlib
from datetime import datetime, timedelta
from typing import List

import pytest

from tests import test_utils

import trestle.common.const as const
import trestle.oscal.common as common
from trestle.common import file_utils, trash
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import catalog

if file_utils.is_windows():  # pragma: no cover
    import win32api
    import win32con


def test_should_ignore() -> None:
    """Test should_ignore method."""
    assert ModelUtils._should_ignore('.test') is True
    assert ModelUtils._should_ignore('_test') is True
    assert ModelUtils._should_ignore('__test') is True
    assert ModelUtils._should_ignore('test') is False


def test_oscal_dir_valid(tmp_path: pathlib.Path) -> None:
    """Test if oscal dir is valid or not."""
    assert file_utils.check_oscal_directories(tmp_path)

    create_sample_catalog_project(tmp_path)

    assert file_utils.check_oscal_directories(tmp_path)

    # add some hidden files
    hidden_file = tmp_path / 'catalogs' / '.hidden.txt'
    test_utils.make_hidden_file(hidden_file)

    keep_file = tmp_path / 'catalogs' / '.keep'
    test_utils.make_hidden_file(keep_file)

    assert file_utils.check_oscal_directories(tmp_path)
    # bad hidden files are not removed but user is asked to remove them
    assert hidden_file.exists()
    assert keep_file.exists()

    # add some markdown readme
    readme_file = tmp_path / 'catalogs' / 'README.md'
    readme_file.touch()
    assert file_utils.check_oscal_directories(tmp_path)


def test_oscal_dir_notvalid(tmp_path: pathlib.Path) -> None:
    """Test OSCAL directory not valid."""
    assert file_utils.check_oscal_directories(tmp_path)
    create_sample_catalog_project(tmp_path)
    assert file_utils.check_oscal_directories(tmp_path)

    profiles_dir = tmp_path / 'profiles'
    profiles_dir.mkdir(parents=True, exist_ok=True)

    invalid_file = profiles_dir / 'shouldnt_be_here.txt'
    invalid_file.touch()

    assert not file_utils.check_oscal_directories(tmp_path)

    invalid_file.unlink()

    assert file_utils.check_oscal_directories(tmp_path)

    metadata_dir = tmp_path / 'catalogs' / 'mycatalog' / 'catalog' / 'metadata'
    deep_invalid_file = metadata_dir / 'responsible-parties' / 'should_be_here.docx'
    readme_file = tmp_path / 'catalogs' / 'readme.md'
    deep_invalid_file.touch()
    readme_file.touch()

    assert not file_utils.check_oscal_directories(tmp_path)


def test_is_valid_project_root(tmp_path: pathlib.Path) -> None:
    """Test is_valid_project_root method."""
    assert file_utils.is_valid_project_root(tmp_path) is False

    test_utils.ensure_trestle_config_dir(tmp_path)
    assert file_utils.is_valid_project_root(tmp_path) is True


def test_has_parent_path(tmp_path: pathlib.Path) -> None:
    """Test has_parent_path method."""
    assert trash.has_parent_path(pathlib.Path('tests'), test_utils.BASE_TMP_DIR) is False
    assert trash.has_parent_path(pathlib.Path('/invalid/path'), test_utils.BASE_TMP_DIR) is False


def test_get_trestle_project_root(tmp_path: pathlib.Path, rand_str: str) -> None:
    """Test get_trestle_project_root  method."""
    project_path: pathlib.Path = pathlib.Path.joinpath(tmp_path, rand_str)
    sub_path: pathlib.Path = project_path.joinpath('samples2')
    sub_path.mkdir(exist_ok=True, parents=True)
    assert sub_path.exists() and sub_path.is_dir()

    # create a file
    sub_path.joinpath('readme.md').touch()

    # create a data-dir and a file
    sub_data_dir = pathlib.Path.joinpath(sub_path, 'data')
    sub_data_dir.mkdir(exist_ok=True, parents=True)
    sub_data_dir.joinpath('readme.md').touch()

    assert file_utils.extract_trestle_project_root(sub_data_dir) is None

    test_utils.ensure_trestle_config_dir(project_path)
    assert file_utils.extract_trestle_project_root(sub_data_dir) == project_path
    assert file_utils.extract_trestle_project_root(sub_data_dir.joinpath('readme.md')) == project_path
    assert file_utils.extract_trestle_project_root(sub_path.joinpath('readme.md')) == project_path
    assert file_utils.extract_trestle_project_root(sub_path) == project_path
    assert file_utils.extract_trestle_project_root(project_path.parent) is None


def test_is_valid_project_model_path(tmp_path: pathlib.Path) -> None:
    """Test is_valid_project_model method."""
    assert file_utils._is_valid_project_model_path(tmp_path) is False

    test_utils.ensure_trestle_config_dir(tmp_path)
    assert file_utils._is_valid_project_model_path(tmp_path) is False

    create_sample_catalog_project(tmp_path)

    catalog_dir = tmp_path / 'catalogs'
    assert file_utils._is_valid_project_model_path(catalog_dir) is False

    mycatalog_dir = catalog_dir / 'mycatalog'
    assert file_utils._is_valid_project_model_path(mycatalog_dir) is True

    metadata_dir = mycatalog_dir / 'metadata'
    assert file_utils._is_valid_project_model_path(metadata_dir) is True

    foo_dir = tmp_path / 'foo/bar'
    foo_dir.mkdir(parents=True)
    assert file_utils._is_valid_project_model_path(foo_dir) is False


def test_get_project_model_path(tmp_path: pathlib.Path) -> None:
    """Test get_project_model_path  method."""
    assert file_utils.extract_project_model_path(tmp_path) is None

    test_utils.ensure_trestle_config_dir(tmp_path)
    assert file_utils.extract_project_model_path(tmp_path) is None

    create_sample_catalog_project(tmp_path)

    catalog_dir = tmp_path / 'catalogs'
    assert file_utils.extract_project_model_path(catalog_dir) is None

    mycatalog_dir = catalog_dir / 'mycatalog'
    assert file_utils.extract_project_model_path(mycatalog_dir) == mycatalog_dir

    metadata_dir = mycatalog_dir / 'metadata'
    assert file_utils.extract_project_model_path(metadata_dir) == mycatalog_dir


def test_load_file(tmp_path: pathlib.Path) -> None:
    """Test load file."""
    json_file_path = test_utils.NIST_SAMPLE_CD_JSON
    yaml_file_path = pathlib.Path.joinpath(test_utils.YAML_TEST_DATA_PATH, 'good_component.yaml')

    assert file_utils.load_file(json_file_path) is not None
    assert file_utils.load_file(yaml_file_path) is not None

    try:
        sample_file_path = tmp_path.joinpath('sample.txt')
        with open(sample_file_path, 'w', encoding=const.FILE_ENCODING):
            file_utils.load_file(sample_file_path)
    except TrestleError:
        pass


def test_get_relative_model_type(tmp_path: pathlib.Path) -> None:
    """Test get model type and alias based on filesystem context."""
    import trestle.common.type_utils as cutils
    with pytest.raises(TrestleError):
        ModelUtils.get_relative_model_type(pathlib.Path('invalidpath'))

    with pytest.raises(TrestleError):
        ModelUtils.get_relative_model_type(pathlib.Path('./'))

    catalogs_dir = pathlib.Path('catalogs')
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'
    metadata_dir = catalog_dir / 'metadata'
    roles_dir = metadata_dir / 'roles'
    rps_dir = metadata_dir / 'responsible-parties'
    props_dir = metadata_dir / 'props'
    groups_dir = catalog_dir / 'groups'
    group_dir = groups_dir / f'00000{const.IDX_SEP}group'
    controls_dir = group_dir / 'controls'
    with pytest.raises(TrestleError):
        ModelUtils.get_relative_model_type(catalogs_dir)

    assert ModelUtils.get_relative_model_type(mycatalog_dir) == (catalog.Catalog, 'catalog')
    assert ModelUtils.get_relative_model_type(mycatalog_dir / 'catalog.json') == (catalog.Catalog, 'catalog')
    assert ModelUtils.get_relative_model_type(catalog_dir / 'back-matter.json'
                                              ) == (common.BackMatter, 'catalog.back-matter')
    assert ModelUtils.get_relative_model_type(catalog_dir / 'metadata.yaml') == (common.Metadata, 'catalog.metadata')
    assert ModelUtils.get_relative_model_type(metadata_dir) == (common.Metadata, 'catalog.metadata')
    assert ModelUtils.get_relative_model_type(roles_dir) == (List[common.Role], 'catalog.metadata.roles')
    (type_, element) = ModelUtils.get_relative_model_type(roles_dir)
    assert cutils.get_origin(type_) == list
    assert element == 'catalog.metadata.roles'
    assert ModelUtils.get_relative_model_type(roles_dir / '00000__role.json'
                                              ) == (common.Role, 'catalog.metadata.roles.role')
    model_type, full_alias = ModelUtils.get_relative_model_type(rps_dir)
    assert model_type == List[common.ResponsibleParty]
    assert full_alias == 'catalog.metadata.responsible-parties'
    assert ModelUtils.get_relative_model_type(
        rps_dir / 'creator__responsible-party.json'
    ) == (common.ResponsibleParty, 'catalog.metadata.responsible-parties.responsible-party')
    (type_, element) = ModelUtils.get_relative_model_type(props_dir)
    assert cutils.get_origin(type_) == list
    assert cutils.get_inner_type(type_) == common.Property
    assert element == 'catalog.metadata.props'
    (expected_type, expected_json_path) = ModelUtils.get_relative_model_type(
        props_dir / f'00000{const.IDX_SEP}property.json'
    )
    assert expected_type == common.Property
    assert expected_json_path == 'catalog.metadata.props.property'
    assert cutils.get_origin(type_) == list
    assert ModelUtils.get_relative_model_type(groups_dir / f'00000{const.IDX_SEP}group.json'
                                              ) == (catalog.Group, 'catalog.groups.group')
    assert ModelUtils.get_relative_model_type(group_dir) == (catalog.Group, 'catalog.groups.group')
    assert ModelUtils.get_relative_model_type(controls_dir / f'00000{const.IDX_SEP}control.json'
                                              ) == (catalog.Control, 'catalog.groups.group.controls.control')


def create_sample_catalog_project(trestle_base_dir: pathlib.Path) -> None:
    """Create directory structure for a sample catalog named mycatalog."""
    test_utils.ensure_trestle_config_dir(trestle_base_dir)

    mycatalog_dir = trestle_base_dir / 'catalogs' / 'mycatalog'

    directories = [
        mycatalog_dir / 'catalog' / 'metadata' / 'roles',
        mycatalog_dir / 'catalog' / 'metadata' / 'responsible-parties',
        mycatalog_dir / 'catalog' / 'metadata' / 'props',
        mycatalog_dir / 'catalog' / 'groups' / f'00000{const.IDX_SEP}group' / 'controls'
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    files = [
        mycatalog_dir / 'catalog.json',
        mycatalog_dir / 'catalog' / 'back-matter.json',
        mycatalog_dir / 'catalog' / 'metadata.json',
        mycatalog_dir / 'catalog' / 'metadata' / 'roles' / f'00000{const.IDX_SEP}role.json',
        mycatalog_dir / 'catalog' / 'metadata' / 'responsible-parties'
        / f'creator{const.IDX_SEP}responsible-party.json',
        mycatalog_dir / 'catalog' / 'metadata' / 'props' / f'00000{const.IDX_SEP}property.json',
        mycatalog_dir / 'catalog' / 'groups' / f'00000{const.IDX_SEP}group.json',
        mycatalog_dir / 'catalog' / 'groups' / f'00000{const.IDX_SEP}group' / 'controls'
        / f'00000{const.IDX_SEP}control.json',
    ]

    for file in files:
        file.touch()


def test_extract_alias() -> None:
    """Test extraction of alias from filename or directory names."""
    assert ModelUtils._extract_alias(pathlib.Path('catalog').name) == 'catalog'
    assert ModelUtils._extract_alias(pathlib.Path('/tmp/catalog').name) == 'catalog'
    assert ModelUtils._extract_alias(pathlib.Path('/catalogs/mycatalog/catalog.json').name) == 'catalog'
    assert ModelUtils._extract_alias(pathlib.Path('/catalogs/mycatalog/catalog.yaml').name) == 'catalog'
    assert ModelUtils._extract_alias(pathlib.Path('responsible-parties').name) == 'responsible-parties'
    assert ModelUtils._extract_alias(pathlib.Path('responsible-parties.json').name) == 'responsible-parties'
    assert ModelUtils._extract_alias(pathlib.Path('/roles').name) == 'roles'
    assert ModelUtils._extract_alias(pathlib.Path('/roles/roles.json').name) == 'roles'
    assert ModelUtils._extract_alias(pathlib.Path(f'/roles/00000{const.IDX_SEP}role.json').name) == 'role'
    assert ModelUtils._extract_alias(
        pathlib.Path(f'/metadata/responsible-parties/creator{const.IDX_SEP}responsible-party.json').name
    ) == 'responsible-party'


def test_get_stripped_model_type(tmp_path: pathlib.Path) -> None:
    """Test get stripped model type and alias based on filesystem context."""
    with pytest.raises(TrestleError):
        ModelUtils.get_stripped_model_type(tmp_path / 'invalidpath', tmp_path)

    with pytest.raises(TrestleError):
        ModelUtils.get_stripped_model_type(tmp_path, tmp_path)

    create_sample_catalog_project(tmp_path)

    catalogs_dir = tmp_path / 'catalogs'
    with pytest.raises(TrestleError):
        ModelUtils.get_stripped_model_type(catalogs_dir, tmp_path)

    def check_stripped_catalog() -> None:
        assert 'uuid' in alias_to_field_map
        assert 'metadata' not in alias_to_field_map
        assert 'back-matter' not in alias_to_field_map
        assert 'groups' not in alias_to_field_map

    mycatalog_dir = catalogs_dir / 'mycatalog'
    stripped_catalog = ModelUtils.get_stripped_model_type(mycatalog_dir, tmp_path)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_catalog()

    stripped_catalog = ModelUtils.get_stripped_model_type(mycatalog_dir / 'catalog.json', tmp_path)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_catalog()

    def check_stripped_metadata(a2f_map) -> None:
        assert 'title' in a2f_map
        assert 'published' in a2f_map
        assert 'last-modified' in a2f_map
        assert 'version' in a2f_map
        assert 'oscal-version' in a2f_map
        assert 'revisions' in a2f_map
        assert 'document-ids' in a2f_map
        assert 'links' in a2f_map
        assert 'locations' in a2f_map
        assert 'parties' in a2f_map
        assert 'remarks' in a2f_map
        assert 'roles' not in alias_to_field_map
        assert 'responsible-properties' not in a2f_map
        assert 'props' not in a2f_map

    catalog_dir = mycatalog_dir / 'catalog'
    metadata_dir = catalog_dir / 'metadata'
    stripped_catalog = ModelUtils.get_stripped_model_type(metadata_dir, tmp_path)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_metadata(alias_to_field_map)

    stripped_catalog = ModelUtils.get_stripped_model_type(catalog_dir / 'metadata.json', tmp_path)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_metadata(alias_to_field_map)

    groups_dir = catalog_dir / 'groups'
    stripped_catalog = ModelUtils.get_stripped_model_type(groups_dir, tmp_path)

    assert stripped_catalog[0].__name__ == 'Groups'
    assert stripped_catalog[1] == 'catalog.groups'

    def check_stripped_group() -> None:
        assert 'id' in alias_to_field_map
        assert 'class' in alias_to_field_map
        assert 'title' in alias_to_field_map
        assert 'params' in alias_to_field_map
        assert 'props' in alias_to_field_map
        assert 'links' in alias_to_field_map
        assert 'parts' in alias_to_field_map
        assert 'groups' in alias_to_field_map
        assert 'controls' not in alias_to_field_map

    stripped_catalog = ModelUtils.get_stripped_model_type(groups_dir / f'00000{const.IDX_SEP}group', tmp_path)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_group()

    stripped_catalog = ModelUtils.get_stripped_model_type(groups_dir / f'00000{const.IDX_SEP}group.json', tmp_path)
    alias_to_field_map = stripped_catalog[0].alias_to_field_map()
    check_stripped_group()


def test_get_singular_alias() -> None:
    """Test get_singular_alias function."""
    assert ModelUtils.get_singular_alias(alias_path='catalog') == 'catalog'

    # Not fullpath. It should be 'catalog.metadata' instead
    with pytest.raises(TrestleError):
        ModelUtils.get_singular_alias(alias_path='metadata.something')

    # Invalid alias_path
    with pytest.raises(TrestleError):
        ModelUtils.get_singular_alias(alias_path='invalid')
    # Invalid alias_path
    with pytest.raises(TrestleError):
        ModelUtils.get_singular_alias(alias_path='')

    assert ModelUtils.get_singular_alias(alias_path='catalog.metadata.responsible-parties') == 'responsible-party'
    assert ModelUtils.get_singular_alias(alias_path='catalog.metadata.responsible-parties.*.props') == 'property'
    assert 'responsible-party' == ModelUtils.get_singular_alias(alias_path='catalog.metadata.responsible-parties.*')

    assert 'role' == ModelUtils.get_singular_alias(alias_path='catalog.metadata.roles')
    assert 'property' == ModelUtils.get_singular_alias(alias_path='catalog.metadata.props')

    assert 'control-implementations' == ModelUtils.get_singular_alias(
        alias_path='component-definition.components.control-implementations'
    )
    assert 'control-implementation' == ModelUtils.get_singular_alias(
        alias_path='component-definition.components.*.control-implementations'
    )
    assert 'control-implementation' == ModelUtils.get_singular_alias(
        alias_path='component-definition.components.0.control-implementations'
    )
    # FIXME ideally this should report error
    assert '0' == ModelUtils.get_singular_alias(alias_path='component-definition.components.0')

    assert 'control' == ModelUtils.get_singular_alias(alias_path='catalog.groups.*.controls.*.controls')


def test_contextual_get_singular_alias(tmp_path: pathlib.Path, keep_cwd: pathlib.Path) -> None:
    """Test get_singular_alias in contextual mode."""
    # Contextual model tests
    create_sample_catalog_project(tmp_path)
    catalogs_dir = tmp_path.resolve() / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'
    metadata_dir = catalog_dir / 'metadata'
    groups_dir = catalog_dir / 'groups'
    group_dir = groups_dir / f'00000{const.IDX_SEP}group'

    rel_dir = mycatalog_dir.relative_to(tmp_path)
    assert 'responsible-party' == ModelUtils.get_singular_alias('catalog.metadata.responsible-parties', rel_dir)
    # Both should work to deal with the case back-matter is already split from the catalog in a separate file
    assert 'resource' == ModelUtils.get_singular_alias('catalog.back-matter.resources', rel_dir)
    assert 'resource' == ModelUtils.get_singular_alias('back-matter.resources', rel_dir)

    rel_dir = metadata_dir.relative_to(tmp_path)
    with pytest.raises(TrestleError):
        ModelUtils.get_singular_alias('metadata.roles')
    alias = ModelUtils.get_singular_alias('metadata.roles', rel_dir)
    assert alias == 'role'
    assert 'responsible-party' == ModelUtils.get_singular_alias('metadata.responsible-parties.*', rel_dir)

    assert 'property' == ModelUtils.get_singular_alias('metadata.responsible-parties.*.props', rel_dir)

    rel_dir = groups_dir.relative_to(tmp_path)
    assert 'control' == ModelUtils.get_singular_alias('groups.*.controls.*.controls', rel_dir)

    rel_dir = group_dir.relative_to(tmp_path)
    assert 'control' == ModelUtils.get_singular_alias('group.controls.*.controls', rel_dir)


def test_get_contextual_file_type(tmp_path: pathlib.Path) -> None:
    """Test fs.get_contextual_file_type()."""
    (tmp_path / 'file.json').touch()
    with pytest.raises(TrestleError):
        file_utils.get_contextual_file_type(pathlib.Path(tmp_path / 'gu.json'))
    (tmp_path / 'file.json').unlink()

    (tmp_path / '.trestle').mkdir()
    (tmp_path / 'catalogs').mkdir()
    catalogs_dir = tmp_path / 'catalogs'
    (catalogs_dir / 'mycatalog').mkdir()
    mycatalog_dir = catalogs_dir / 'mycatalog'

    pathlib.Path(mycatalog_dir / 'file2.json').touch()
    assert file_utils.get_contextual_file_type(mycatalog_dir) == FileContentType.JSON
    (mycatalog_dir / 'file2.json').unlink()

    if file_utils.is_windows():
        hidden_file = mycatalog_dir / 'hidden.txt'
        hidden_file.touch()
        atts = win32api.GetFileAttributes(str(hidden_file))
        win32api.SetFileAttributes(str(hidden_file), win32con.FILE_ATTRIBUTE_HIDDEN | atts)
    else:
        pathlib.Path(mycatalog_dir / '.DS_Store').touch()

    pathlib.Path(mycatalog_dir / 'file2.json').touch()
    assert file_utils.get_contextual_file_type(mycatalog_dir) == FileContentType.JSON

    if file_utils.is_windows():
        hidden_file.unlink()
    else:
        (mycatalog_dir / '.DS_Store').unlink()
    (mycatalog_dir / 'file2.json').unlink()

    pathlib.Path(mycatalog_dir / 'file3.yml').touch()
    assert file_utils.get_contextual_file_type(mycatalog_dir) == FileContentType.YAML
    (mycatalog_dir / 'file3.yml').unlink()

    (mycatalog_dir / 'catalog').mkdir()
    (mycatalog_dir / 'catalog/groups').mkdir()
    (mycatalog_dir / 'catalog/groups/file4.yaml').touch()
    assert file_utils.get_contextual_file_type(mycatalog_dir) == FileContentType.YAML


def test_get_models_of_type(tmp_trestle_dir) -> None:
    """Test fs.get_models_of_type()."""
    create_sample_catalog_project(tmp_trestle_dir)
    catalogs_dir = tmp_trestle_dir.resolve() / 'catalogs'
    components_dir = tmp_trestle_dir.resolve() / 'component-definitions'
    # mycatalog is already there
    (catalogs_dir / 'mycatalog2').mkdir()
    (catalogs_dir / '.myfile').touch()
    (components_dir / 'my_component').mkdir()
    models = ModelUtils.get_models_of_type('catalog', tmp_trestle_dir)
    assert len(models) == 2
    assert 'mycatalog' in models
    assert 'mycatalog2' in models
    all_models = ModelUtils.get_all_models(tmp_trestle_dir)
    assert len(all_models) == 3
    assert ('catalog', 'mycatalog') in all_models
    assert ('catalog', 'mycatalog2') in all_models
    assert ('component-definition', 'my_component') in all_models
    with pytest.raises(TrestleError):
        ModelUtils.get_models_of_type('foo', tmp_trestle_dir)


def test_get_models_of_type_bad_cwd(tmp_path) -> None:
    """Test fs.get_models_of_type() from outside trestle dir."""
    with pytest.raises(TrestleError):
        ModelUtils.get_models_of_type('catalog', tmp_path)


def test_is_hidden_posix(tmp_path) -> None:
    """Test is_hidden on posix systems."""
    if not file_utils.is_windows():
        hidden_file = tmp_path / '.hidden.md'
        hidden_dir = tmp_path / '.hidden/'
        visible_file = tmp_path / 'visible.md'
        visible_dir = tmp_path / 'visible/'

        assert file_utils.is_hidden(hidden_file)
        assert file_utils.is_hidden(hidden_dir)
        assert not file_utils.is_hidden(visible_file)
        assert not file_utils.is_hidden(visible_dir)
    else:
        pass


def test_is_hidden_windows(tmp_path) -> None:
    """Test is_hidden on windows systems."""
    if file_utils.is_windows():
        visible_file = tmp_path / 'visible.md'
        visible_dir = tmp_path / 'visible/'
        visible_file.touch()
        visible_dir.touch()
        assert not file_utils.is_hidden(visible_file)
        assert not file_utils.is_hidden(visible_dir)

        atts = win32api.GetFileAttributes(str(visible_file))
        win32api.SetFileAttributes(str(visible_file), win32con.FILE_ATTRIBUTE_HIDDEN | atts)
        atts = win32api.GetFileAttributes(str(visible_dir))
        win32api.SetFileAttributes(str(visible_dir), win32con.FILE_ATTRIBUTE_HIDDEN | atts)

        assert file_utils.is_hidden(visible_file)
        assert file_utils.is_hidden(visible_dir)
    else:
        pass


@pytest.mark.parametrize(
    'task_name, outcome',
    [
        ('hello', True), ('.trestle', False), ('task/name', True), ('.bad,', False), ('catalogs', False),
        ('catalog', True), ('component-definitions', False), ('hello.world', False),
        ('component-definitions/hello', False)
    ]
)
def test_allowed_task_name(task_name: str, outcome: bool) -> None:
    """Test whether task names are allowed."""
    assert file_utils.is_directory_name_allowed(task_name) == outcome


def test_model_type_to_model_dir() -> None:
    """Test model type to model dir."""
    assert ModelUtils.model_type_to_model_dir('catalog') == 'catalogs'
    try:
        ModelUtils.model_type_to_model_dir('foo')
    except Exception:
        pass
    else:
        assert 'test failed'


def test_local_and_visible(tmp_path) -> None:
    """Test if file is local (not symlink) and visible (not hidden)."""
    local_file = tmp_path / 'local.md'
    local_file.touch()
    if file_utils.is_windows():
        link_file = tmp_path / 'not_local.lnk'
        link_file.touch()
    else:
        link_file = tmp_path / 'linked.md'
        link_file.symlink_to(local_file)
    assert file_utils.is_local_and_visible(local_file)
    assert not file_utils.is_local_and_visible(link_file)


@pytest.mark.parametrize(
    'candidate, build, expect_failure',
    [
        (pathlib.Path('relative_file.json'), False, False),
        (pathlib.Path('relative_file.json'), True, False),
        (pathlib.Path('/random/absolute/path'), False, True),
        (pathlib.Path('/random/absolute/path'), False, True),
        (pathlib.Path('~/random/home_directory/path'), False, True),
        (pathlib.Path('~/random/home_directory/path'), True, False),
        (pathlib.Path('../relative_file.json'), False, True),
        (pathlib.Path('../relative_file.json'), True, True),
        (
            pathlib.Path('./hello/../relative_file.json'),
            False,
            False,
        ),
        (
            pathlib.Path('./hello/../relative_file.json'),
            True,
            False,
        ),
    ]
)
def test_relative_resolve(tmp_path, candidate: pathlib.Path, build: bool, expect_failure: bool):
    """Test relative resolve capability."""
    if build:
        input_path = tmp_path / candidate
    else:
        input_path = candidate
    if expect_failure:
        with pytest.raises(TrestleError):
            _ = file_utils.relative_resolve(input_path, tmp_path)
    else:
        _ = file_utils.relative_resolve(input_path, tmp_path)


def test_iterdir_without_hidden_files(tmp_path: pathlib.Path) -> None:
    """Test that hidden files are filtered from the path."""
    pathlib.Path(tmp_path / 'visible.txt').touch()
    pathlib.Path(tmp_path / 'visibleDir/').mkdir()

    if file_utils.is_windows():
        """Windows"""
        hidden_file = tmp_path / 'hidden.txt'
        hidden_dir = tmp_path / 'hiddenDir/'
        hidden_file.touch()
        hidden_dir.mkdir()
        atts = win32api.GetFileAttributes(str(hidden_file))
        win32api.SetFileAttributes(str(hidden_file), win32con.FILE_ATTRIBUTE_HIDDEN | atts)
        atts = win32api.GetFileAttributes(str(hidden_dir))
        win32api.SetFileAttributes(str(hidden_dir), win32con.FILE_ATTRIBUTE_HIDDEN | atts)

        assert len(list(file_utils.iterdir_without_hidden_files(tmp_path))) == 3
    else:

        pathlib.Path(tmp_path / '.DS_Store').touch()
        pathlib.Path(tmp_path / '.hidden.txt').touch()
        pathlib.Path(tmp_path / '.hiddenDir/').mkdir()

        assert len(list(file_utils.iterdir_without_hidden_files(tmp_path))) == 3


def test_make_hidden_file(tmp_path: pathlib.Path) -> None:
    """Test make hidden files."""
    file_path = tmp_path / '.keep'
    file_utils.make_hidden_file(file_path)

    file_path2 = tmp_path / 'hidden.txt'
    file_utils.make_hidden_file(file_path2)

    assert file_path.exists() and not file_utils.is_local_and_visible(file_path)
    if file_utils.is_windows():
        assert file_path2.exists() and not file_utils.is_local_and_visible(file_path2)
    else:
        assert (tmp_path / '.hidden.txt').exists() and not file_utils.is_local_and_visible(tmp_path / '.hidden.txt')


def test_full_path_for_top_level_model(tmp_trestle_dir: pathlib.Path, sample_catalog_minimal: catalog.Catalog) -> None:
    """Test full path for top level model."""
    ModelUtils.save_top_level_model(sample_catalog_minimal, tmp_trestle_dir, 'mycat', FileContentType.JSON)
    cat_path = ModelUtils.full_path_for_top_level_model(tmp_trestle_dir, 'mycat', catalog.Catalog)
    assert cat_path == tmp_trestle_dir / 'catalogs/mycat/catalog.json'


def test_update_last_modified(sample_catalog_rich_controls: catalog.Catalog) -> None:
    """Test update timestamps."""
    hour_ago = datetime.now().astimezone() - timedelta(seconds=const.HOUR_SECONDS)
    ModelUtils.update_last_modified(sample_catalog_rich_controls, hour_ago)
    assert sample_catalog_rich_controls.metadata.last_modified.__root__ == hour_ago
    ModelUtils.update_last_modified(sample_catalog_rich_controls)
    assert ModelUtils.model_age(sample_catalog_rich_controls) < test_utils.NEW_MODEL_AGE_SECONDS
