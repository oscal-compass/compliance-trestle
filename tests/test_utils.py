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
import sys
from typing import Any, List

from _pytest.monkeypatch import MonkeyPatch

from trestle.cli import Trestle
from trestle.core import const, generators, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands.import_ import ImportCmd
from trestle.core.common_types import TopLevelOscalModel
from trestle.core.err import TrestleError
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import catalog as cat
from trestle.oscal import common

logger = logging.getLogger(__name__)

BASE_TMP_DIR = pathlib.Path('tests/__tmp_path').resolve()
YAML_TEST_DATA_PATH = pathlib.Path('tests/data/yaml/').resolve()
JSON_TEST_DATA_PATH = pathlib.Path('tests/data/json/').resolve()
ENV_TEST_DATA_PATH = pathlib.Path('tests/data/env/').resolve()
JSON_NIST_DATA_PATH = pathlib.Path('nist-content/nist.gov/SP800-53/rev5/json/').resolve()
JSON_NIST_CATALOG_NAME = 'NIST_SP-800-53_rev5_catalog.json'
JSON_NIST_PROFILE_NAME = 'NIST_SP-800-53_rev5_MODERATE-baseline_profile.json'

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
    except BaseException as e:
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


def insert_text_in_file(file_path: pathlib.Path, tag: str, text: str) -> int:
    r"""Insert text lines after line containing tag.

    Return 0 on success, 1 tag not found.
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
            return 0
    return 1


def generate_control_list(label: str, count: int) -> List[cat.Control]:
    """Generate a list of controls with indexed names."""
    controls: List[cat.Control] = []
    for ii in range(count):
        control = generators.generate_sample_model(cat.Control, True)
        control.id = f'{label}-{ii + 1}'
        controls.append(control)
    return controls


def generate_complex_catalog() -> cat.Catalog:
    """Generate a complex and deep catalog for testing."""
    group_a = generators.generate_sample_model(cat.Group, True)
    group_a.id = 'a'
    group_a.controls = generate_control_list('a', 4)
    part = generators.generate_sample_model(common.Part)
    part.id = 'a-1_smt'
    part.parts = None
    group_a.controls[0].parts[0].id = 'part_with_subpart'
    group_a.controls[0].parts[0].parts = [part]
    group_b = generators.generate_sample_model(cat.Group, True)
    group_b.id = 'b'
    group_b.controls = generate_control_list('b', 3)
    group_b.controls[2].controls = generate_control_list('b-2', 3)
    group_ba = generators.generate_sample_model(cat.Group, True)
    group_ba.id = 'ba'
    group_ba.controls = generate_control_list('ba', 2)
    group_b.groups = [group_ba]

    catalog = generators.generate_sample_model(cat.Catalog, True)
    catalog.controls = generate_control_list('cat', 3)
    catalog.groups = [group_a, group_b]

    return catalog


def patch_raise_exception() -> None:
    """Raise TrestleError exception, to be used for testing."""
    raise TrestleError('Forced raising of an errors')
