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
from typing import Any, Dict, Tuple

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.core.generic_oscal as generic
import trestle.oscal.component as comp
from trestle.common import const, file_utils
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.href import HrefCmd
from trestle.core.control_interface import ControlInterface
from trestle.core.markdown.markdown_processor import MarkdownProcessor

md_path = 'md_comp'


def edit_files(control_path: pathlib.Path, set_parameters_flag: bool, guid_dict: Dict[str, str]) -> None:
    """Edit the files to show assemble worked."""
    assert control_path.exists()
    assert file_utils.insert_text_in_file(control_path, None, guid_dict['text'])
    if set_parameters_flag:
        assert test_utils.delete_line_in_file(control_path, 'label:')
        assert file_utils.insert_text_in_file(control_path, 'ac-1_prm_1:', '    label: label from edit\n')
        # delete profile values for 4, then replace value for 3 with new value
        assert file_utils.insert_text_in_file(control_path, 'officer', '    profile-values: new value\n')
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
    simple_cat_name = 'simple_catalog_no_parts'
    load_file(trestle_root, 'comp_def.json', comp_name, 'component-definition')
    load_file(trestle_root, test_utils.SIMPLIFIED_NIST_CATALOG_NAME, cat_name, 'catalog')
    load_file(trestle_root, simple_cat_name + '.json', simple_cat_name, 'catalog')
    load_file(trestle_root, test_utils.SIMPLIFIED_NIST_PROFILE_NAME, prof_name, 'profile')
    new_href = 'trestle://catalogs/nist_cat/catalog.json'
    assert HrefCmd.change_import_href(trestle_root, prof_name, new_href, 0) == 0
    return comp_name, prof_name, cat_name


def check_common_contents(header: Dict[str, Any]) -> None:
    """Check common features of controls markdown."""
    params = header[const.RULES_PARAMS_TAG]
    assert len(params) == 1
    assert params[0] == {
        'name': 'foo_length', 'description': 'minimum_foo_length', 'rule-id': 'XCCDF', 'options': '["6", "9"]'
    }
    assert header[const.TRESTLE_GLOBAL_TAG][
        const.PROFILE_TITLE] == 'NIST Special Publication 800-53 Revision 5 MODERATE IMPACT BASELINE'  # noqa E501


def check_ac1_contents(ac1_path: pathlib.Path) -> None:
    """Check the contents of ac-1 md."""
    assert test_utils.confirm_text_in_file(ac1_path, 'enter one of:', 'set to 644')
    assert test_utils.confirm_text_in_file(ac1_path, 'set to 644', 'Status: implemented')
    assert test_utils.confirm_text_in_file(ac1_path, 'Status: implemented', 'ac1 remark')
    assert test_utils.confirm_text_in_file(ac1_path, 'ac-1_smt.c', 'Status: planned')
    markdown_processor = MarkdownProcessor()
    header, _ = markdown_processor.read_markdown_wo_processing(ac1_path)
    assert header[const.PARAM_VALUES_TAG]['ac-1_prm_1'] == 'Param_1_value_in_catalog'
    rules = header[const.COMP_DEF_RULES_TAG]
    assert len(rules) == 1
    assert rules[0] == {'name': 'XCCDF', 'description': 'The XCCDF must be compliant'}
    vals = header[const.COMP_DEF_RULES_PARAM_VALS_TAG]
    assert len(vals) == 2
    assert vals['quantity_available'] == '500'
    check_common_contents(header)


def check_ac5_contents(ac5_path: pathlib.Path) -> None:
    """Check the contents of ac-5 md."""
    markdown_processor = MarkdownProcessor()
    header, _ = markdown_processor.read_markdown_wo_processing(ac5_path)
    assert test_utils.confirm_text_in_file(
        ac5_path, '### Implementation Status: partial', '### Implementation Status Remarks: this is my remark'
    )
    rules = header[const.COMP_DEF_RULES_TAG]
    assert len(rules) == 2
    assert rules[0] == {'name': 'XCCDF', 'description': 'The XCCDF must be compliant'}
    assert rules[1] == {'name': 'FancyXtraRule', 'description': 'This is a fancy extra rule'}
    check_common_contents(header)


def test_component_generate(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test component generate."""
    comp_name, _, _ = setup_component_generate(tmp_trestle_dir)
    ac1_path = tmp_trestle_dir / f'{md_path}/OSCO/ac/ac-1.md'
    ac5_path = tmp_trestle_dir / f'{md_path}/OSCO/ac/ac-5.md'

    generate_cmd = f'trestle author component-generate -n {comp_name} -o {md_path}'

    # generate the md first time
    test_utils.execute_command_and_assert(generate_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    check_ac1_contents(ac1_path)
    check_ac5_contents(ac5_path)

    file_checker = test_utils.FileChecker(tmp_trestle_dir / md_path)

    # generate again but force use of source in comp_def to load profile rather than command line
    generate_cmd = f'trestle author component-generate -n {comp_name} -o {md_path}'
    # confirm it overwrites existing md properly
    test_utils.execute_command_and_assert(generate_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)

    # all files should be the same
    assert file_checker.files_unchanged()

    # make edits to status and remarks and control level prose
    assert test_utils.substitute_text_in_file(ac1_path, '644', '567')
    control_prose = '567 or more restrictive'
    assert test_utils.confirm_text_in_file(ac1_path, 'after assembly to JSON', control_prose)
    assert test_utils.substitute_text_in_file(ac5_path, 'Status: partial', 'Status: implemented')
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
    imp_reqs = ControlInterface.get_control_imp_reqs(component.control_implementations[1], 'ac-5')
    new_status = ControlInterface.get_status_from_props(imp_reqs[0])
    assert new_status.state == 'implemented'
    assert new_status.remarks.__root__ == 'this is my new remark'
    imp_reqs = ControlInterface.get_control_imp_reqs(component.control_implementations[0], 'ac-1')
    assert control_prose in imp_reqs[0].description

    orig_uuid = assem_comp_def.uuid

    orig_file_creation = orig_comp_def_path.stat().st_mtime

    # confirm repeat assemble doesn't generate new file since no changes
    test_utils.execute_command_and_assert(assemble_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    assert orig_comp_def_path.stat().st_mtime == orig_file_creation

    # force overwrite of output, regenerate, and new version
    assemble_cmd = f'trestle author component-assemble -o assem_comp -m {md_path} -r -vn 1.2.3'
    test_utils.execute_command_and_assert(assemble_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    assem_comp_def, _ = ModelUtils.load_top_level_model(tmp_trestle_dir, 'assem_comp', comp.ComponentDefinition)
    assert assem_comp_def.uuid != orig_uuid
    assert assem_comp_def.metadata.version.__root__ == '1.2.3'


def test_generic_oscal() -> None:
    """Test generic oscal conversions."""
    generic_component = generic.GenericComponent.generate()
    def_comp = generic_component.as_defined_component()
    assert def_comp.description == const.REPLACE_ME

    generic_cont_imp = generic.GenericControlImplementation.generate()
    cont_imp = generic_cont_imp.as_ssp()
    assert cont_imp.description == const.REPLACE_ME
