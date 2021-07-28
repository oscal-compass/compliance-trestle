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
"""Tests for trestle describe command."""
import argparse
import os
import pathlib

import pytest

from tests import test_utils

from trestle.core.commands.describe import DescribeCmd
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import catalog as oscatalog


@pytest.mark.parametrize('element_path', ['', 'catalog.metadata.roles', 'catalog.metadata'])
def test_describe_functionality(
    element_path: str, tmp_path: pathlib.Path, keep_cwd: pathlib.Path, sample_catalog: oscatalog.Catalog
) -> None:
    """Test basic functionality of describe."""
    # prepare trestle project dir with the file
    catalog_dir, catalog_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        sample_catalog,
        test_utils.CATALOGS_DIR)

    os.chdir(catalog_dir)
    args = argparse.Namespace(file='catalog.json', element=element_path, verbose=1)
    assert DescribeCmd()._run(args) == 0


def test_describe_failures(tmp_path: pathlib.Path) -> None:
    """Test describe failure modes."""
    args = argparse.Namespace(verbose=1)
    assert DescribeCmd()._run(args) == 1
