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
"""Tests for the ssp_generator module."""

import argparse
import pathlib

from tests import test_utils

from trestle.core.commands.import_ import ImportCmd
from trestle.core.commands.md_subs.ssp import SSP


def test_ssp_generator(tmp_trestle_dir: pathlib.Path):
    """Test the ssp generator."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json'
    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    cat_name = 'my_cat'
    prof_name = 'my_prof'
    ssp_name = 'my_ssp'
    i = ImportCmd()
    args = argparse.Namespace(file=str(cat_path), output=cat_name, verbose=True, regenerate=True)
    assert i._run(args) == 0
    args = argparse.Namespace(file=str(prof_path), output=prof_name, verbose=True, regenerate=True)
    assert i._run(args) == 0
    sections = 'ImplGuidance:Implicit Guidance,ExpectedEvidence:Expected Evidence'
    args = argparse.Namespace(
        file=cat_name, profile=prof_name, output=ssp_name, verbose=True, sections=sections, yaml_header=str(yaml_path)
    )
    ssp_cmd = SSP()
    assert ssp_cmd._run(args) == 0
    ac_dir = tmp_trestle_dir / ('md/' + ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'
    ac_2 = ac_dir / 'ac-2.md'
    assert ac_1.exists()
    assert ac_2.exists()
    assert ac_1.stat().st_size > 1000
    assert ac_2.stat().st_size > 2000

    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml'
    args = argparse.Namespace(
        file=cat_name, profile=prof_name, output=ssp_name, verbose=True, sections=sections, yaml_header=str(yaml_path)
    )
    assert ssp_cmd._run(args) == 1
