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

import pathlib

from trestle.core.base_model import OscalBaseModel

BASE_TMP_DIR = pathlib.Path('tests/__tmp_dir')


def has_parent_path(cur_path: pathlib.Path, parent_path: pathlib.Path) -> bool:
    """Check if cur_dir has the specified parent_dir path."""
    if len(cur_path.parts) < len(parent_path.parts):
        return False

    for i, part in enumerate(parent_path.parts):
        if part is not cur_path.parts[i]:
            return False

    return True


def clean_tmp_dir(tmp_dir: pathlib.Path):
    """Clean tmp directory."""
    if tmp_dir.exists() and has_parent_path(tmp_dir.parent, BASE_TMP_DIR):
        for item in pathlib.Path.iterdir(tmp_dir):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                clean_tmp_dir(item)

        pathlib.Path.rmdir(tmp_dir)


def verify_file_content(file_path: pathlib.Path, model: OscalBaseModel):
    """Verify that the file contains the correct model data."""
    model.oscal_read(file_path)
