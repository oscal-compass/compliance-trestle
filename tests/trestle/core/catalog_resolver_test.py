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
"""Tests for models module."""

import argparse
import logging
import pathlib

from tests import test_utils

from trestle.core.catalog_resolver import CatalogResolver
from trestle.core.commands.import_ import ImportCmd
from trestle.utils import log

prof_name = 'my_prof'


def test_resolver(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the resolver."""
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_a.json'

    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        file=str(cat_path),
        output='NIST_SP-800-53_rev5_catalog',
        verbose=False,
        regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    prof_b_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_b.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(prof_b_path), output='test_profile_b', verbose=False, regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    log.set_global_logging_levels(logging.DEBUG)

    cat = CatalogResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_path)
    assert cat
