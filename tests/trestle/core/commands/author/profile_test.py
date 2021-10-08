# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Tests for the profile author module."""

import pathlib
import shutil
import sys
from typing import Dict
from unittest.mock import patch

import pytest

from tests import test_utils

from trestle.cli import Trestle
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.profile import ProfileAssemble, ProfileGenerate
from trestle.core.profile_resolver import ProfileResolver

markdown_name = 'my_md'

ref_text = 'for suggested types. -->'

my_guidance_text = """

## Control my_guidance

This is my_guidance.
"""

my_guidance_dict = {'names': ['my_guidance'], 'text': my_guidance_text}

added_guidance_text = """

## Control guidance

This is guidance.
"""

new_guidance_dict = {'names': ['guidance'], 'text': added_guidance_text}

multi_guidance_text = my_guidance_text = """

## Control guidance

This is guidance.

## Control my_guidance

This is my_guidance.
"""

multi_guidance_dict = {'names': ['guidance', 'my_guidance'], 'text': multi_guidance_text}


@pytest.mark.parametrize('guid_dict', [my_guidance_dict, new_guidance_dict, multi_guidance_dict])
@pytest.mark.parametrize('use_cli', [True, False])
@pytest.mark.parametrize('dir_exists', [True, False])
def test_profile_generate_assemble(
    guid_dict: Dict, use_cli: bool, dir_exists: bool, tmp_trestle_dir: pathlib.Path
) -> None:
    """Test the profile markdown generator."""
    nist_catalog_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    trestle_cat_dir = tmp_trestle_dir / 'catalogs/nist_cat'
    trestle_cat_dir.mkdir(exist_ok=True, parents=True)
    shutil.copy(nist_catalog_path, trestle_cat_dir / 'catalog.json')
    prof_name = 'my_prof'
    md_name = 'my_md'
    assembled_prof_name = 'my_assembled_prof'
    profile_dir = tmp_trestle_dir / f'profiles/{prof_name}'
    profile_dir.mkdir(parents=True, exist_ok=True)
    simple_prof_path = test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json'
    profile_path = profile_dir / 'profile.json'
    shutil.copy(simple_prof_path, profile_path)
    markdown_path = tmp_trestle_dir / md_name
    ac1_path = markdown_path / 'ac/ac-1.md'
    assembled_prof_dir = tmp_trestle_dir / f'profiles/{assembled_prof_name}'

    # convert resolved profile catalog to markdown then assemble it after adding an item to a control
    if use_cli:
        test_args = f'trestle author profile-generate -n {prof_name} -o {md_name}'.split()
        with patch.object(sys, 'argv', test_args):
            Trestle().run()
        assert ac1_path.exists()
        test_utils.insert_text_in_file(ac1_path, ref_text, guid_dict['text'])
        test_args = f'trestle author profile-assemble -n {prof_name} -m {md_name} -o {assembled_prof_name}'.split()
        if dir_exists:
            assembled_prof_dir.mkdir()
        with patch.object(sys, 'argv', test_args):
            Trestle().run()
    else:
        profile_generate = ProfileGenerate()
        profile_generate.generate_markdown(tmp_trestle_dir, profile_path, markdown_path)
        assert ac1_path.exists()
        test_utils.insert_text_in_file(ac1_path, ref_text, guid_dict['text'])
        if dir_exists:
            assembled_prof_dir.mkdir()
        ProfileAssemble.assemble_profile(tmp_trestle_dir, prof_name, md_name, assembled_prof_name)

    # now create the resolved profile catalog from the assembled json profile and confirm the addition is there

    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, assembled_prof_dir / 'profile.json')
    catalog_interface = CatalogInterface(catalog)
    for name in guid_dict['names']:
        prose = catalog_interface.get_control_part_prose('ac-1', name)
        assert prose.find(f'This is {name}.') >= 0
