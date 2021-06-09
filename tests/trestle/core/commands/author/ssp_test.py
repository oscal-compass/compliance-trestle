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
from typing import Tuple

from tests import test_utils

import trestle.utils.fs as fs
from trestle.core.commands.author.ssp import SSP
from trestle.core.commands.import_ import ImportCmd
from trestle.core.markdown_validator import MarkdownValidator

import yaml

prof_name = 'my_prof'
ssp_name = 'my_ssp'


def setup_for_ssp() -> Tuple[argparse.Namespace, str]:
    """Create the markdown ssp content from catalog and profile."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    cat_name = fs.model_name_from_href_path(cat_path)
    prof_path = test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json'
    i = ImportCmd()
    args = argparse.Namespace(file=str(cat_path), output=cat_name, verbose=True, regenerate=True)
    assert i._run(args) == 0
    args = argparse.Namespace(file=str(prof_path), output=prof_name, verbose=True, regenerate=True)
    assert i._run(args) == 0
    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    sections = 'ImplGuidance:Implicit Guidance,ExpectedEvidence'
    args = argparse.Namespace(
        file=prof_name, output=ssp_name, verbose=True, sections=sections, mode='setup', yaml_header=str(yaml_path)
    )
    return args, sections, yaml_path


def test_ssp_generator(tmp_trestle_dir: pathlib.Path):
    """Test the ssp generator."""
    args, sections, yaml_path = setup_for_ssp()
    ssp_cmd = SSP()
    assert ssp_cmd._run(args) == 0
    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'
    ac_2 = ac_dir / 'ac-2.md'
    assert ac_1.exists()
    assert ac_2.exists()
    assert ac_1.stat().st_size > 1000
    assert ac_2.stat().st_size > 2000
    with open(yaml_path, 'r', encoding='utf8') as f:
        expected_header = yaml.load(f, yaml.FullLoader)
    header, tree = MarkdownValidator.load_markdown_parsetree(ac_1)
    assert tree is not None
    assert expected_header == header
    header, tree = MarkdownValidator.load_markdown_parsetree(ac_1)
    assert tree is not None
    assert expected_header == header

    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml'
    args = argparse.Namespace(
        file=prof_name, output=ssp_name, verbose=True, sections=sections, mode='setup', yaml_header=str(yaml_path)
    )
    assert ssp_cmd._run(args) == 1


def test_ssp_assemble(tmp_trestle_dir: pathlib.Path):
    """Test ssp assemble."""
    args, _, _ = setup_for_ssp()
    ssp_cmd = SSP()
    assert ssp_cmd._run(args) == 0
    args = argparse.Namespace(file=ssp_name, profile=prof_name, output=ssp_name, verbose=True, mode='create-sample')
    assert ssp_cmd._run(args) == 0


def test_ssp_bad_name(tmp_trestle_dir: pathlib.Path):
    """Test bad output name."""
    ssp_cmd = SSP()
    args = argparse.Namespace(file='my_prof', output='catalogs', verbose=True, mode='setup', yaml_header='dummy.yaml')
    assert ssp_cmd._run(args) == 1


def test_ssp_bad_dir(tmp_path: pathlib.Path):
    """Test ssp not in trestle project."""
    ssp_cmd = SSP()
    args = argparse.Namespace(file='my_prof', output='my_ssp', verbose=True, mode='setup', yaml_header='dummy.yaml')
    assert ssp_cmd._run(args) == 1
