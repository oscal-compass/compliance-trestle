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
"""Tests for trestle actions module."""

import json
import pathlib

from trestle.core.base_model import OscalBaseModel
from trestle.core.models.actions import FileContentType

import yaml

BASE_TMP_DIR = pathlib.Path('tests/__tmp_dir')


def clean_tmp_dir(tmp_dir: pathlib.Path):
    """Clean tmp directory."""
    if tmp_dir.exists() and tmp_dir.parent == BASE_TMP_DIR:
        for file in pathlib.Path.iterdir(tmp_dir):
            pathlib.Path.unlink(file)

        pathlib.Path.rmdir(tmp_dir)


def verify_file_content(file_path, model: OscalBaseModel, content_type: FileContentType):
    """Verify that the file contains the correct model data."""
    file_data = None
    with open(file_path, 'r', encoding='utf8') as read_file:
        if content_type == FileContentType.YAML:
            file_data = yaml.load(read_file, Loader=yaml.Loader)
        elif content_type == FileContentType.JSON:
            file_data = json.load(read_file)

    assert file_data is not None

    model.parse_obj(file_data)
