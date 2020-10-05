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

import pathlib

from trestle.core.base_model import OscalBaseModel
from trestle.core.models.elements import Element
from trestle.utils import fs

BASE_TMP_DIR = pathlib.Path('tests/__tmp_dir')


def clean_tmp_dir(tmp_dir: pathlib.Path):
    """Clean tmp directory."""
    if tmp_dir.exists() and fs.has_parent_path(tmp_dir, BASE_TMP_DIR):
        # clean all files/directories under sub_path
        for item in pathlib.Path.iterdir(tmp_dir):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                clean_tmp_dir(item)

        # delete the sub_path
        if tmp_dir.is_file():
            tmp_dir.unlink()
        elif tmp_dir.is_dir():
            tmp_dir.rmdir()


def verify_file_content(file_path: pathlib.Path, model: OscalBaseModel):
    """Verify that the file contains the correct model data."""
    model.oscal_read(file_path)


def is_equal(item1, item2):
    """Check if two obects are equal.

    If the items are OscalBaseModel, it wraps into Element to do the equality check
    """
    if isinstance(item1, OscalBaseModel):
        item1 = Element(item1)

    if isinstance(item2, OscalBaseModel):
        item2 = Element(item2)

    return item1 == item2
