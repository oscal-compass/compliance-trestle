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
from typing import Any, Dict, List

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.core.generic_oscal as generic
import trestle.oscal.catalog as cat
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
from trestle.common import const, file_utils, model_utils
from trestle.core.commands.common.return_codes import CmdReturnCodes
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


def setup_component_generate(tmp_trestle_dir: pathlib.Path) -> List[str]:
    """Create the compdef, profile and catalog content component-generate."""
    comp_names = 'comp_def_a,comp_def_b'
    for comp_name in comp_names.split(','):
        test_utils.load_from_json(tmp_trestle_dir, comp_name, comp_name, comp.ComponentDefinition)
    for prof_name in 'comp_prof,comp_prof_aa,comp_prof_ab,comp_prof_ba,comp_prof_bb'.split(','):
        test_utils.load_from_json(tmp_trestle_dir, prof_name, prof_name, prof.Profile)
    test_utils.load_from_json(tmp_trestle_dir, 'simplified_nist_catalog', 'simplified_nist_catalog', cat.Catalog)

    return comp_names


def check_common_contents(header: Dict[str, Any]) -> None:
    """Check common features of controls markdown."""
    params = header[const.RULES_PARAMS_TAG]['comp_aa']
    assert len(params) == 1
    assert params[0] == {
        'name': 'shared_param_1',
        'description': 'shared param 1 in aa',
        'options': '["shared_param_1_aa_opt_1", "shared_param_1_aa_opt_2"]',
        'rule-id': 'top_shared_rule_1'
    }
    assert header[const.TRESTLE_GLOBAL_TAG][const.PROFILE]['title'] == 'comp prof aa'
    assert header[const.TRESTLE_GLOBAL_TAG][const.PROFILE
                                            ]['href'] == 'trestle://profiles/comp_prof_aa/profile.json'  # noqa E501


def check_ac1_contents(ac1_path: pathlib.Path) -> None:
    """Check the contents of ac-1 md."""
    assert test_utils.confirm_text_in_file(ac1_path, 'enter one of:', 'ac-1 from comp aa')
    assert test_utils.confirm_text_in_file(ac1_path, 'ac-1 from comp aa', 'Status: implemented')
    assert test_utils.confirm_text_in_file(ac1_path, '- comp_rule_aa_1', 'Status: partial')
    markdown_processor = MarkdownProcessor()
    header, _ = markdown_processor.read_markdown_wo_processing(ac1_path)
    assert header[const.PARAM_VALUES_TAG]['ac-1_prm_1'] == 'prof_aa val 1'
    rules = header[const.COMP_DEF_RULES_TAG]['comp_aa']
    assert len(rules) == 2
    assert rules[0] == {'name': 'top_shared_rule_1', 'description': 'top shared rule 1 in aa'}
    assert rules[1] == {'name': 'comp_rule_aa_1', 'description': 'comp rule aa 1'}
    vals = header[const.COMP_DEF_RULES_PARAM_VALS_TAG]['comp_aa']
    assert len(vals) == 1
    assert vals[0]['name'] == 'shared_param_1'
    assert vals[0]['values'] == ['shared_param_1_aa_opt_1']
    check_common_contents(header)


def check_at1_contents(at1_path: pathlib.Path) -> None:
    """Check the contents of at-1 md."""
    markdown_processor = MarkdownProcessor()
    header, _ = markdown_processor.read_markdown_wo_processing(at1_path)
    rules = header[const.COMP_DEF_RULES_TAG]['comp_ab']
    assert len(rules) == 2
    assert rules[0] == {'name': 'XCCDF', 'description': 'The XCCDF must be compliant'}
    assert rules[1] == {'name': 'FancyXtraRule', 'description': 'This is a fancy extra rule'}
    check_common_contents(header)


def test_component_generate(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test component generate."""
    comp_names = setup_component_generate(tmp_trestle_dir)
    comp_name = comp_names.split(',')[0]
    ac1_path = tmp_trestle_dir / 'md_comp/comp_aa/comp_prof_aa/ac/ac-1.md'

    orig_component, _ = model_utils.ModelUtils.load_top_level_model(
        tmp_trestle_dir, comp_name, comp.ComponentDefinition
    )

    generate_cmd = f'trestle author component-generate -n {comp_name} -o {md_path}'

    # generate the md first time
    test_utils.execute_command_and_assert(generate_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    check_ac1_contents(ac1_path)

    file_checker = test_utils.FileChecker(tmp_trestle_dir / md_path)

    generate_cmd = f'trestle author component-generate -n {comp_name} -o {md_path}'
    # confirm it overwrites existing md identically
    test_utils.execute_command_and_assert(generate_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)

    # all files should be the same
    assert file_checker.files_unchanged()

    assem_name = 'assem_comp'

    # confirm assembled is identical except for uuids
    assemble_cmd = f'trestle author component-assemble -m {md_path} -n {comp_name} -o {assem_name}'
    test_utils.execute_command_and_assert(assemble_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    assem_component, _ = model_utils.ModelUtils.load_top_level_model(
        tmp_trestle_dir, assem_name, comp.ComponentDefinition
    )
    assert model_utils.ModelUtils.models_are_equivalent(orig_component, assem_component, True)


def test_generic_oscal() -> None:
    """Test generic oscal conversions."""
    generic_component = generic.GenericComponent.generate()
    def_comp = generic_component.as_defined_component()
    assert def_comp.description == ''

    generic_cont_imp = generic.GenericControlImplementation.generate()
    cont_imp = generic_cont_imp.as_ssp()
    assert cont_imp.description == ''
