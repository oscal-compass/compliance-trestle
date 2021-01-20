# -*- mode:python; coding:utf-8 -*-

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
"""Test utils module."""

import os
import pathlib
from typing import List

from trestle.core import const, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands import cmd_utils
from trestle.core.models.elements import ElementPath
from trestle.core.models.file_content_type import FileContentType

BASE_TMP_DIR = pathlib.Path('tests/__tmp_path')
YAML_TEST_DATA_PATH = pathlib.Path('tests/data/yaml/')
JSON_TEST_DATA_PATH = pathlib.Path('tests/data/json/')
ENV_TEST_DATA_PATH = pathlib.Path('tests/data/env/')
JSON_NIST_DATA_PATH = pathlib.Path('nist-content/nist.gov/SP800-53/rev4/json/')
JSON_NIST_CATALOG_NAME = 'NIST_SP-800-53_rev4_catalog.json'

TARGET_DEFS_DIR = 'target-definitions'
CATALOGS_DIR = 'catalogs'


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
    trestle_dir = pathlib.Path.joinpath(sub_dir, const.TRESTLE_CONFIG_DIR)
    trestle_dir.mkdir(exist_ok=True, parents=True)


def prepare_element_paths(base_dir, element_args) -> List[ElementPath]:
    """Prepare element paths for tests."""
    cur_dir = pathlib.Path.cwd()
    os.chdir(base_dir)
    element_paths: List[ElementPath] = cmd_utils.parse_element_args(element_args, True)
    os.chdir(cur_dir)

    return element_paths


def prepare_trestle_project_dir(
    tmp_path, content_type: FileContentType, model_obj: OscalBaseModel, models_dir_name: str
):
    """Prepare a temp directory with an example OSCAL model."""
    ensure_trestle_config_dir(tmp_path)

    model_alias = utils.classname_to_alias(model_obj.__class__.__name__, 'json')

    file_ext = FileContentType.to_file_extension(content_type)
    models_full_path = tmp_path / models_dir_name / 'my_test_model'
    model_def_file = models_full_path / f'{model_alias}{file_ext}'
    models_full_path.mkdir(exist_ok=True, parents=True)
    model_obj.oscal_write(model_def_file)

    return models_full_path, model_def_file


def list_unordered_equal(list1, list2):
    """Given 2 lists, check if the items in both the lists are same, regardless of order."""
    list1 = list(list1)  # make a mutable copy
    try:
        for elem in list2:
            list1.remove(elem)
    except ValueError:
        return False
    return not list1
