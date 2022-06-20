# Copyright (c) 2022 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the component author module."""

import argparse
import pathlib
import shutil
from typing import Dict, Tuple

from tests import test_utils

from trestle.core.commands.author.component import ComponentGenerate
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.href import HrefCmd

md_path = 'md_comp'


def edit_files(control_path: pathlib.Path, set_parameters: bool, guid_dict: Dict[str, str]) -> None:
    """Edit the files to show assemble worked."""
    assert control_path.exists()
    assert test_utils.insert_text_in_file(control_path, None, guid_dict['text'])
    if set_parameters:
        assert test_utils.delete_line_in_file(control_path, 'label:')
        assert test_utils.insert_text_in_file(control_path, 'ac-1_prm_1:', '    label: label from edit\n')
        # delete profile values for 4, then replace value for 3 with new value
        assert test_utils.insert_text_in_file(control_path, 'officer', '    profile-values: new value\n')
        assert test_utils.delete_line_in_file(control_path, 'weekly')


def setup_component_generate(
    trestle_root: pathlib.Path
) -> Tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path]:
    """Set up files for profile generate."""
    comp_orig_path = test_utils.JSON_TEST_DATA_PATH / 'comp_def.json'
    comp_name = 'test_comp'
    trestle_comp_dir = trestle_root / ('component-definitions/' + comp_name)
    trestle_comp_dir.mkdir(exist_ok=True, parents=True)
    comp_new_path = trestle_comp_dir / ('component-definition.json')
    shutil.copy(comp_orig_path, comp_new_path)
    cat_name = 'nist_cat'
    cat_orig_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME
    cat_new_dir = trestle_root / ('catalogs/' + cat_name)
    cat_new_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(cat_orig_path, cat_new_dir / 'catalog.json')
    prof_name = 'nist_prof'
    prof_orig_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_PROFILE_NAME
    prof_new_dir = trestle_root / ('profiles/' + prof_name)
    prof_new_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(prof_orig_path, prof_new_dir / 'profile.json')
    new_href = 'trestle://catalogs/nist_cat/catalog.json'
    assert HrefCmd.change_import_href(trestle_root, prof_name, new_href, 0) == 0
    return comp_name, prof_name, cat_name


def test_component_generate(tmp_trestle_dir: pathlib.Path) -> None:
    """Test component generate."""
    comp_name, prof_name, _ = setup_component_generate(tmp_trestle_dir)
    test_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=comp_name,
        profile=prof_name,
        output=md_path,
        overwrite_header_values=False,
        allowed_sections=None,
        yaml_header=None,
        verbose=0,
        set_parameters=False
    )

    comp_gen = ComponentGenerate()
    assert comp_gen._run(test_args) == CmdReturnCodes.SUCCESS.value
