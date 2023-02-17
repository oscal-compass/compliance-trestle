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
from typing import Any, Dict

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

import trestle.core.generic_oscal as generic
import trestle.oscal.component as comp
from trestle.common import const, model_utils
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.markdown.markdown_processor import MarkdownProcessor

md_path = 'md_comp'


def add_comp(comp_path: pathlib.Path, ac1_path: pathlib.Path) -> None:
    """Add a new component to the markdown."""
    ac_path = comp_path / 'comp_new/ac'
    ac_path.mkdir(parents=True, exist_ok=True)
    new_ac1_path = ac_path / 'ac-1.md'
    shutil.copyfile(str(ac1_path), str(new_ac1_path))


def check_common_contents(header: Dict[str, Any]) -> None:
    """Check common features of controls markdown."""
    params = header[const.RULES_PARAMS_TAG]['comp_aa']
    assert len(params) == 1
    assert params[0] == {
        'name': 'shared_param_1',
        'description': 'shared param 1 in aa',
        'options': '["shared_param_1_aa_opt_1", "shared_param_1_aa_opt_2", "shared_param_1_aa_opt_3"]',
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
    assert test_utils.confirm_text_in_file(ac1_path, 'ac-1_prm_3:', '- set by comp aa imp req')
    markdown_processor = MarkdownProcessor()
    header, _ = markdown_processor.read_markdown_wo_processing(ac1_path)
    assert header[const.PARAM_VALUES_TAG]['ac-1_prm_1'] == ['prof_aa val 1']
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
    comp_name = test_utils.setup_component_generate(tmp_trestle_dir)
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
    assem_component, assem_comp_path = model_utils.ModelUtils.load_top_level_model(
        tmp_trestle_dir, assem_name, comp.ComponentDefinition
    )
    creation_time = assem_comp_path.stat().st_mtime
    assert model_utils.ModelUtils.models_are_equivalent(orig_component, assem_component, True)

    test_utils.execute_command_and_assert(assemble_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    assert creation_time == assem_comp_path.stat().st_mtime

    ac1_path = tmp_trestle_dir / 'md_comp/comp_aa/comp_prof_aa/ac/ac-1.md'

    # confirm we can add a new component via markdown
    add_comp(tmp_trestle_dir / 'md_comp', ac1_path)
    test_utils.execute_command_and_assert(assemble_cmd, CmdReturnCodes.SUCCESS.value, monkeypatch)
    assem_component, _ = model_utils.ModelUtils.load_top_level_model(
        tmp_trestle_dir, assem_name, comp.ComponentDefinition
    )
    assert assem_component.components[2].title == 'comp_new'


def test_generic_oscal() -> None:
    """Test generic oscal conversions."""
    generic_component = generic.GenericComponent.generate()
    def_comp = generic_component.as_defined_component()
    assert def_comp.description == ''

    generic_cont_imp = generic.GenericControlImplementation.generate()
    cont_imp = generic_cont_imp.as_ssp()
    assert cont_imp.description == ''
