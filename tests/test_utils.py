# -*- mode:python; coding:utf-8 -*-

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
"""Test utils module."""

import argparse
import logging
import os
import pathlib
import shutil
import sys
from typing import Any, List, Tuple

from _pytest.monkeypatch import MonkeyPatch

from trestle.cli import Trestle
from trestle.core import const, generators, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands.href import HrefCmd
from trestle.core.commands.import_ import ImportCmd
from trestle.core.common_types import TopLevelOscalModel
from trestle.core.err import TrestleError
from trestle.core.models.file_content_type import FileContentType
from trestle.core.repository import Repository
from trestle.oscal import catalog as cat
from trestle.oscal import common
from trestle.oscal import profile as prof
from trestle.utils import fs

if os.name == 'nt':  # pragma: no cover
    import win32api
    import win32con

logger = logging.getLogger(__name__)

BASE_TMP_DIR = pathlib.Path('tests/__tmp_path').resolve()
YAML_TEST_DATA_PATH = pathlib.Path('tests/data/yaml/').resolve()
JSON_TEST_DATA_PATH = pathlib.Path('tests/data/json/').resolve()
ENV_TEST_DATA_PATH = pathlib.Path('tests/data/env/').resolve()
JSON_NIST_DATA_PATH = pathlib.Path('nist-content/nist.gov/SP800-53/rev5/json/').resolve()
JSON_NIST_CATALOG_NAME = 'NIST_SP-800-53_rev5_catalog.json'
JSON_NIST_PROFILE_NAME = 'NIST_SP-800-53_rev5_MODERATE-baseline_profile.json'
SIMPLIFIED_NIST_CATALOG_NAME = 'simplified_nist_catalog.json'
SIMPLIFIED_NIST_PROFILE_NAME = 'simplified_nist_profile.json'

CATALOGS_DIR = 'catalogs'
PROFILES_DIR = 'profiles'
COMPONENT_DEF_DIR = 'component-definitions'

NIST_EXAMPLES = pathlib.Path('nist-content/examples')
NIST_SAMPLE_CD_JSON = NIST_EXAMPLES / 'component-definition' / 'json' / 'example-component.json'


def clean_tmp_path(tmp_path: pathlib.Path):
    """Clean tmp directory."""
    if tmp_path.exists():
        # clean all files/directories under sub_path
        for item in pathlib.Path.iterdir(tmp_path):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                clean_tmp_path(item)

        # delete the sub_path
        if tmp_path.is_file():
            tmp_path.unlink()
        elif tmp_path.is_dir():
            tmp_path.rmdir()


def verify_file_content(file_path: pathlib.Path, model: OscalBaseModel):
    """Verify that the file contains the correct model data."""
    model.oscal_read(file_path)


def ensure_trestle_config_dir(sub_dir: pathlib.Path):
    """Ensure that the sub_dir has trestle config dir."""
    trestle_dir = sub_dir / const.TRESTLE_CONFIG_DIR
    trestle_dir.mkdir(exist_ok=True, parents=True)


def prepare_trestle_project_dir(
    repo_dir: pathlib.Path, content_type: FileContentType, model_obj: OscalBaseModel, models_dir_name: str
):
    """Prepare a temp directory with an example OSCAL model."""
    ensure_trestle_config_dir(repo_dir)

    model_alias = utils.classname_to_alias(model_obj.__class__.__name__, 'json')

    file_ext = FileContentType.to_file_extension(content_type)
    models_full_path = repo_dir / models_dir_name / 'my_test_model'
    model_def_file = models_full_path / f'{model_alias}{file_ext}'
    models_full_path.mkdir(exist_ok=True, parents=True)
    model_obj.oscal_write(model_def_file)

    return models_full_path, model_def_file


def create_trestle_project_with_model(
    top_dir: pathlib.Path, model_obj: OscalBaseModel, model_name: str, monkeypatch: MonkeyPatch
) -> pathlib.Path:
    """Create initialized trestle project and import the model into it."""
    cur_dir = pathlib.Path.cwd()

    # create subdirectory for trestle project
    trestle_root = top_dir / 'my_trestle'
    trestle_root.mkdir()
    os.chdir(trestle_root)

    try:
        testargs = ['trestle', 'init']
        monkeypatch.setattr(sys, 'argv', testargs)
        assert Trestle().run() == 0

        # place model object in top directory outside trestle project
        # so it can be imported
        tmp_model_path = top_dir / (model_name + '.json')
        model_obj.oscal_write(tmp_model_path)

        i = ImportCmd()
        args = argparse.Namespace(
            trestle_root=trestle_root, file=str(tmp_model_path), output=model_name, verbose=False, regenerate=False
        )
        assert i._run(args) == 0
    except Exception as e:
        raise TrestleError(f'Error creating trestle project with model: {e}')
    finally:
        os.chdir(cur_dir)
    return trestle_root


def list_unordered_equal(list1: List[Any], list2: List[Any]) -> bool:
    """Given 2 lists, check if the items in both the lists are same, regardless of order."""
    list1 = list(list1)  # make a mutable copy
    try:
        for elem in list2:
            list1.remove(elem)
    except ValueError:
        return False
    return not list1


def models_are_equivalent(model_a: TopLevelOscalModel, model_b: TopLevelOscalModel) -> bool:
    """Test if models are equivalent except for last modified."""
    # this will change the second model as a side-effect
    model_b.metadata.last_modified = model_a.metadata.last_modified
    return model_a == model_b


def text_files_equal(path_a: pathlib.Path, path_b: pathlib.Path) -> bool:
    """Determine if files are equal, ignoring newline style."""
    try:
        with open(path_a, 'r') as file_a:
            with open(path_b, 'r') as file_b:
                lines_a = file_a.readlines()
                lines_b = file_b.readlines()
                nlines = len(lines_a)
                if nlines != len(lines_b):
                    logger.info(f'n lines differ: {len(lines_a)} vs. {len(lines_b)}')
                    return False
                for ii in range(nlines):
                    if lines_a[ii].rstrip('\r\n') != lines_b[ii].rstrip('\r\n'):
                        logger.info('lines differ:')
                        logger.info(lines_a[ii])
                        logger.info(lines_b[ii])
                        return False
    except Exception:
        return False
    return True


def insert_text_in_file(file_path: pathlib.Path, tag: str, text: str) -> bool:
    r"""Insert text lines after line containing tag.

    Return True on success, False tag not found.
    Text is a string with appropriate \n line endings.
    """
    lines: List[str] = []
    with file_path.open('r') as f:
        lines = f.readlines()
    for ii, line in enumerate(lines):
        if line.find(tag) >= 0:
            lines.insert(ii + 1, text)
            with file_path.open('w') as f:
                f.writelines(lines)
            return True
    return False


def confirm_text_in_file(file_path: pathlib.Path, tag: str, text: str) -> bool:
    """Confirm the expected text is in the file after the tag."""
    lines: List[str] = []
    with file_path.open('r') as f:
        lines = f.readlines()
    found_tag = False
    for line in lines:
        if line.find(tag) >= 0:
            found_tag = True
            continue
        if found_tag and line.find(text) >= 0:
            return True
    return False


def delete_line_in_file(file_path: pathlib.Path, tag: str) -> bool:
    """Delete a line in a file containing tag."""
    lines: List[str] = []
    with file_path.open('r') as f:
        lines = f.readlines()
    for ii, line in enumerate(lines):
        if line.find(tag) >= 0:
            del lines[ii]
            with file_path.open('w') as f:
                f.writelines(lines)
            return True
    return False


def generate_control_list(label: str, count: int) -> List[cat.Control]:
    """Generate a list of controls with indexed names."""
    controls: List[cat.Control] = []
    for ii in range(count):
        control = generators.generate_sample_model(cat.Control, True)
        control.id = f'{label}-{ii + 1}'
        control.params[0].id = f'{control.id}.param'
        sub_part = common.Part(
            id=f'{control.id}_smt.a',
            name='item',
            props=[common.Property(name='label', value='a.')],
            prose=f'Prose for item a. of control {control.id}'
        )
        control.parts = [
            common.Part(
                id=f'{control.id}_smt',
                name='statement',
                prose=f'Prose for the statement part of control {control.id}',
                parts=[sub_part]
            ),
        ]
        controls.append(control)
    return controls


def generate_param_list(label: str, count: int) -> List[cat.Control]:
    """Generate a list of params with indexed names."""
    params: List[common.Parameter] = []
    for ii in range(count):
        param = generators.generate_sample_model(common.Parameter, True)
        param.id = f'{label}-{ii + 1}'
        param.label = f'label-{param.id}'
        param.props[0].name = f'name-{param.id}'
        param.props[0].value = f'value-{param.id}'
        param.guidelines[0].prose = f'prose-{param.id}'
        params.append(param)
    return params


def generate_complex_catalog(stem: str = '') -> cat.Catalog:
    """Generate a complex and deep catalog for testing."""
    group_a = generators.generate_sample_model(cat.Group, True)
    group_a.id = f'{stem}a'
    group_a.controls = generate_control_list(group_a.id, 4)
    group_b = generators.generate_sample_model(cat.Group, True)
    group_b.id = f'{stem}b'
    group_b.controls = generate_control_list(group_b.id, 3)
    group_b.controls[2].controls = generate_control_list(f'{group_b.id}-2', 3)
    group_ba = generators.generate_sample_model(cat.Group, True)
    group_ba.id = f'{stem}ba'
    group_ba.controls = generate_control_list(group_ba.id, 2)
    group_b.groups = [group_ba]

    catalog = generators.generate_sample_model(cat.Catalog, True)
    catalog.controls = generate_control_list(f'{stem}cat', 3)
    catalog.params = generate_param_list(f'{stem}parm', 3)

    test_control = generators.generate_sample_model(cat.Control, False)
    test_control.id = f'{stem}test-1'
    test_control.params = [common.Parameter(id=f'{test_control.id}_prm_1', values=['Default', 'Values'])]
    test_control.parts = [
        common.Part(
            id=f'{test_control.id}_smt',
            name='statement',
            prose='Statement with no parts.  Prose with param value {{ insert: param, test-1_prm_1 }}'
        )
    ]
    catalog.controls.append(test_control)
    catalog.groups = [group_a, group_b]

    return catalog


def patch_raise_exception() -> None:
    """Raise TrestleError exception, to be used for testing."""
    raise TrestleError('Forced raising of an errors')


def setup_for_multi_profile(trestle_root: pathlib.Path, big_profile: bool, import_nist_cat: bool) -> None:
    """Initiallize trestle directory with catalogs and profiles."""
    repo = Repository(trestle_root)
    main_profile_name = 'main_profile'

    if big_profile:
        prof_path = JSON_TEST_DATA_PATH / SIMPLIFIED_NIST_PROFILE_NAME
    else:
        prof_path = JSON_TEST_DATA_PATH / 'simple_test_profile.json'
    repo.load_and_import_model(prof_path, main_profile_name)

    for letter in 'abcdefg':
        prof_name = f'test_profile_{letter}'
        prof_path = JSON_TEST_DATA_PATH / f'{prof_name}.json'
        repo.load_and_import_model(prof_path, prof_name)

    complex_cat = generate_complex_catalog()
    repo.import_model(complex_cat, 'complex_cat')

    cat_name = 'nist_cat'
    cat_path = JSON_TEST_DATA_PATH / SIMPLIFIED_NIST_CATALOG_NAME
    if import_nist_cat:
        repo.load_and_import_model(cat_path, cat_name)
        new_href = f'trestle://catalogs/{cat_name}/catalog.json'
    else:
        new_href = str(cat_path.resolve())
    assert HrefCmd.change_import_href(trestle_root, main_profile_name, new_href, 0) == 0


def setup_for_ssp(
    include_header: bool,
    big_profile: bool,
    tmp_trestle_dir: pathlib.Path,
    prof_name: str,
    output_name: str,
    import_nist_cat: bool = True
) -> Tuple[argparse.Namespace, str, pathlib.Path]:
    """Create the markdown ssp content from catalog and profile."""
    setup_for_multi_profile(tmp_trestle_dir, big_profile, import_nist_cat)

    sections = 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence,guidance:Guidance'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=output_name,
        verbose=True,
        sections=sections,
        preserve_header_values=False
    )

    yaml_path = YAML_TEST_DATA_PATH / 'good_simple.yaml'
    if include_header:
        args.yaml_header = str(yaml_path)

    return args, sections, yaml_path


def make_file_hidden(file_path: pathlib.Path, if_dot=False) -> None:
    """
    Make a file hidden on windows.

    if_dot will make the change only if the filename is of the form .*
    """
    if os.name == 'nt':
        if not if_dot or file_path.stem.startswith('.'):
            atts = win32api.GetFileAttributes(str(file_path))
            win32api.SetFileAttributes(str(file_path), win32con.FILE_ATTRIBUTE_HIDDEN | atts)


def make_dot_files_in_tree_hidden(dir_path: pathlib.Path) -> None:
    """On windows change all .* files to have hidden attributes."""
    for dot_file in dir_path.rglob('.*'):
        make_file_hidden(dot_file, True)


def copy_tree_with_hidden(src_path: pathlib.Path, dest_path: pathlib.Path) -> None:
    """Copy directory and make sure dot files are hidden."""
    if not dest_path.parent.exists():
        dest_path.parent.mkdir(parents=True)
    shutil.copytree(str(src_path), str(dest_path), copy_function=shutil.copy2)
    make_dot_files_in_tree_hidden(dest_path)


def copy_file_with_hidden(src_path: pathlib.Path, dest_path: pathlib.Path) -> None:
    """Copy a file and if it is a dot file make it hidden."""
    if not dest_path.parent.exists():
        dest_path.mkdir(parents=True)
    shutil.copy2(str(src_path), str(dest_path))
    make_file_hidden(dest_path, True)


def copy_tree_or_file_with_hidden(src_path: pathlib.Path, dest_path: pathlib.Path) -> None:
    """Copy directory tree along with file attributes."""
    if src_path.is_dir():
        copy_tree_with_hidden(src_path, dest_path)
    else:
        copy_file_with_hidden(src_path, dest_path)


def make_hidden_file(file_path: pathlib.Path) -> None:
    """Make a hidden file with the given file path."""
    file_path.touch()
    make_file_hidden(file_path)


def get_model_uuid(trestle_root: pathlib.Path, model_name: str, model_class: TopLevelOscalModel) -> str:
    """Load the model and extract its uuid."""
    model, _ = fs.load_top_level_model(trestle_root, model_name, model_class)
    return model.uuid


def execute_command_and_assert(command: str, return_code: int, monkeypatch: MonkeyPatch) -> None:
    """Execute given command using monkeypatch and assert return code."""
    monkeypatch.setattr(sys, 'argv', command.split())
    rc = Trestle().run()
    assert rc == return_code


def create_profile_in_trestle_dir(trestle_root: pathlib.Path, catalog_name: str, profile_name: str) -> None:
    """Create a profile in the trestle dir with href to load all from specified catalog."""
    profile = generators.generate_sample_model(prof.Profile)
    import_ = prof.Import(href=f'{const.TRESTLE_HREF_HEADING}catalogs/{catalog_name}/catalog.json', include_all={})
    profile.imports = [import_]
    fs.save_top_level_model(profile, trestle_root, profile_name, fs.FileContentType.JSON)
