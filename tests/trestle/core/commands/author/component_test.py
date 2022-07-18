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

import pathlib
import shutil
from typing import Dict, Tuple

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.oscal.component as comp
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.href import HrefCmd
from trestle.core.control_interface import ControlInterface

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


def load_file(trestle_root: pathlib.Path, source_name: str, dest_name: str, source_type: str) -> None:
    """Load file into workspace."""
    item_orig_path = test_utils.JSON_TEST_DATA_PATH / (source_name)
    item_dir = trestle_root / f'{source_type}s/{dest_name}'
    item_dir.mkdir(exist_ok=True, parents=True)
    item_new_path = item_dir / f'{source_type}.json'
    shutil.copy(item_orig_path, item_new_path)


def setup_component_generate(trestle_root: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Set up files for profile generate."""
    comp_name = 'test_comp'
    cat_name = 'nist_cat'
    prof_name = 'nist_prof'
    load_file(trestle_root, 'comp_def.json', comp_name, 'component-definition')
    load_file(trestle_root, test_utils.SIMPLIFIED_NIST_CATALOG_NAME, cat_name, 'catalog')
    load_file(trestle_root, test_utils.SIMPLIFIED_NIST_PROFILE_NAME, prof_name, 'profile')
    new_href = 'trestle://catalogs/nist_cat/catalog.json'
    assert HrefCmd.change_import_href(trestle_root, prof_name, new_href, 0) == 0
    return comp_name, prof_name, cat_name


def check_ac1_contents(ac1_path: pathlib.Path) -> None:
    """Check the contents of ac-1 md."""
    assert test_utils.confirm_text_in_file(ac1_path, 'enter one of:', 'set to 644')
    assert test_utils.confirm_text_in_file(ac1_path, 'set to 644', 'Status: operational')
    assert test_utils.confirm_text_in_file(ac1_path, 'Status: operational', 'ac1 remark')


def test_component_generate(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test component generate."""
    comp_name, prof_name, _ = setup_component_generate(tmp_trestle_dir)
    ac1_path = tmp_trestle_dir / f'{md_path}/OSCO/ac/ac-1.md'
    ac5_path = tmp_trestle_dir / f'{md_path}/OSCO/ac/ac-5.md'

    generate_cmd = f'trestle author component-generate -n {comp_name} -p {prof_name} -o {md_path}'

    # generate the md first time
    test_utils.execute_command_and_assert(generate_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    check_ac1_contents(ac1_path)

    # confirm it overwrites existing md properly
    test_utils.execute_command_and_assert(generate_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    check_ac1_contents(ac1_path)

    # make edits to status and remarks
    assert test_utils.substitute_text_in_file(ac5_path, 'Status: under-development', 'Status: implemented')
    assert test_utils.confirm_text_in_file(ac5_path, 'garbage collection', 'Status: implemented')
    assert test_utils.substitute_text_in_file(ac5_path, 'my remark', 'my new remark')
    assert test_utils.confirm_text_in_file(ac5_path, 'garbage collection', 'my new remark')

    assemble_cmd = f'trestle author component-assemble -n {comp_name} -o assem_comp -m {md_path}'
    test_utils.execute_command_and_assert(assemble_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)

    # confirm assembled model is as expected
    assem_comp_def, orig_comp_def_path = ModelUtils.load_top_level_model(
        tmp_trestle_dir,
        'assem_comp',
        comp.ComponentDefinition
    )
    component = ControlInterface.get_component_by_name(assem_comp_def, 'OSCO')
    imp_reqs = ControlInterface.get_control_imp_reqs(component, 'ac-5')
    new_status = ControlInterface.get_status_from_props(imp_reqs[0])
    assert new_status.state == 'implemented'
    assert new_status.remarks.__root__ == 'this is my new remark'

    orig_file_creation = orig_comp_def_path.stat().st_mtime

    # confirm repeat assemble doesn't generate new file since no changes
    test_utils.execute_command_and_assert(assemble_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    assert orig_comp_def_path.stat().st_mtime == orig_file_creation
