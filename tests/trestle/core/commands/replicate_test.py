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
"""Tests for trestle replicate command."""
import shutil
from pathlib import Path

import dictdiffer

from tests import test_utils

from trestle.oscal.catalog import Catalog, ResponsibleParty, Role
from trestle.utils import fs
from trestle.utils.load_distributed import _load_dict, _load_list, load_distributed



import argparse
import pathlib
import random
import string
import sys
import tempfile
from json.decoder import JSONDecodeError
from unittest.mock import patch

from tests import test_utils

import trestle.core.commands.replicate as repcmd
import trestle.core.err as err
import trestle.oscal
from trestle.cli import Trestle
from trestle.core import generators
from trestle.core.commands import create
from trestle.oscal.catalog import Catalog


def test_replicate_cmd(testdata_dir, tmp_trestle_dir) -> None:
    """Test replicate command."""
    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = Path('catalogs/')
    catalog_name = 'mycatalog'
    rep_name = 'repcatalog'
    rep_file = catalogs_dir / rep_name / 'catalog.json'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    # execute the command to replicate the model into replicated
    test_args = f'trestle replicate catalog -f {catalog_name} -o {rep_name}'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 0

    # now load the replicate and compare

    rep_model_type, rep_model_alias, rep_model_instance = load_distributed(rep_file)

    expected_model_type, _ = fs.get_contextual_model_type(rep_file.absolute())

    expected_model_instance = Catalog.oscal_read(testdata_dir / 'split_merge/load_distributed/catalog.json')

    assert rep_model_type == expected_model_type
    assert rep_model_alias == 'catalog'
    assert len(list(dictdiffer.diff(expected_model_instance, rep_model_instance))) == 0


# def test_replicate_cmd2(tmp_trestle_dir: pathlib.Path) -> None:
#     """Happy path test at the cli level."""
#     # 1. Input file, profile:
#     rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
#     profile_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
#     profile_data = generators.generate_sample_model(trestle.oscal.profile.Profile)
#     profile_data.oscal_write(pathlib.Path(profile_file))
#     # 2. Input file, target:
#     rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
#     target_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
#     target_data = generators.generate_sample_model(trestle.oscal.target.TargetDefinition)
#     target_data.oscal_write(pathlib.Path(target_file))
#     # Test 1
#     test_args = f'trestle replicate -f {profile_file} -o replicated'.split()
#     with patch.object(sys, 'argv', test_args):
#         rc = Trestle().run()
#         assert rc == 0
#     # Test 2
#     test_args = f'trestle replicate -f {target_file} -o replicated'.split()
#     with patch.object(sys, 'argv', test_args):
#         rc = Trestle().run()
#         assert rc == 0


# def test_replicate_run(tmp_trestle_dir: pathlib.Path) -> None:
#     """Test successful _run() on valid and invalid."""
#     rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
#     catalog_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
#     catalog_data = generators.generate_sample_model(trestle.oscal.catalog.Catalog)
#     catalog_data.oscal_write(pathlib.Path(catalog_file))
#     i = repcmd.ReplicateCmd()
#     args = argparse.Namespace(file=catalog_file, output='replicated', verbose=True)
#     rc = i._run(args)
#     assert rc == 0


