# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Tests for the ssp_generator module."""

import argparse
import pathlib
from typing import Dict, List

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils
from tests.test_utils import FileChecker, setup_for_ssp, setup_for_ssp_fedramp

import trestle.core.generators as gens
import trestle.core.generic_oscal as generic
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.common import const, file_utils, list_utils
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPAssemble, SSPFilter, SSPGenerate
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_reader import ControlReader
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

prof_name = 'comp_prof'
ssp_name = 'my_ssp'
cat_name = 'nist_cat'


def confirm_control_contains(trestle_dir: pathlib.Path, control_id: str, part_label: str, seek_str: str) -> bool:
    """Confirm the text is present in the control markdown in the correct part."""
    control_dir = trestle_dir / ssp_name / control_id.split('-')[0]
    md_file = control_dir / f'{control_id}.md'
    context = ControlContext.generate(ContextPurpose.SSP, False, trestle_dir, trestle_dir)
    _, comp_dict = ControlReader.read_control_info_from_md(md_file, context)
    for label_dict in comp_dict.values():
        if part_label in label_dict:
            prose = label_dict[part_label].prose
            if seek_str in prose:
                return True
    return False


part_a_text = """## Implementation for part a.

### comp_aa

statement prose for part a. from comp aa

#### Rules:

  - comp_rule_aa_1

#### Implementation Status: partial

### comp_ab

<!-- Add control implementation description here for item a. -->

#### Rules:

  - comp_rule_ab_1

#### Implementation Status: partial

______________________________________________________________________"""


def test_ssp_generate(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)

    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    md_dir = tmp_trestle_dir / ssp_name
    ac_dir = md_dir / 'ac'
    ac_1 = ac_dir / 'ac-1.md'
    assert ac_1.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert header[const.TRESTLE_GLOBAL_TAG][const.SORT_ID] == 'ac-01'
    assert header[const.COMP_DEF_RULES_PARAM_VALS_TAG]['comp_aa'][0] == {
        'name': 'shared_param_1', 'values': ['shared_param_1_aa_opt_1']
    }

    node = tree.get_node_for_key('## Implementation for part a.')
    assert node.content.raw_text == part_a_text

    fc = FileChecker(md_dir)

    assert ssp_cmd._run(args) == 0

    assert fc.files_unchanged()

    assert ssp_cmd._run(args) == 0

    assert fc.files_unchanged()


def test_ssp_generate_no_cds(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with no comp defs."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)

    args.compdefs = None
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    md_dir = tmp_trestle_dir / ssp_name
    ac_1 = md_dir / 'ac/ac-1.md'
    assert ac_1.exists()
    at_2 = md_dir / 'at/at-2.md'
    assert at_2.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert header[const.TRESTLE_GLOBAL_TAG][const.SORT_ID] == 'ac-01'

    node = tree.get_node_for_key(const.SSP_MD_IMPLEMENTATION_QUESTION, False)
    assert len(node.subnodes) == 1
    assert len(node.subnodes[0].subnodes) == 1
    assert node.subnodes[0].key == '### This System'
    assert node.subnodes[0].subnodes[0].key == '#### Implementation Status: planned'

    fc = FileChecker(md_dir)

    assert ssp_cmd._run(args) == 0

    assert fc.files_unchanged()


def test_ssp_failures(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp failure modes."""
    ssp_cmd = SSPGenerate()

    # bad yaml
    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'bad_simple.yaml'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        output=ssp_name,
        verbose=0,
        yaml_header=str(yaml_path),
        overwrite_header_values=False
    )
    assert ssp_cmd._run(args) == 1

    # test missing profile
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile='foo',
        output=ssp_name,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None
    )
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_with_yaml_header(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with yaml header."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name, True)
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'
    assert ac_1.exists()
    assert ac_1.stat().st_size > 1000

    # confirm content from the cli yaml header is now in the header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    assert header[const.TRESTLE_GLOBAL_TAG][const.SORT_ID] == 'ac-01'
    assert header['control-origination'][0] == 'Service Provider Corporate'


def test_ssp_generate_header_edit(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp generate does not overwrite header edits."""
    # always start by creating the markdown with the yaml header
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name, True)
    ssp_cmd = SSPGenerate()

    cli_yaml_header = args.yaml_header
    args.yaml_header = None

    # first generate with no yaml header
    assert ssp_cmd._run(args) == 0

    ac_dir = tmp_trestle_dir / (ssp_name + '/ac')
    ac_1 = ac_dir / 'ac-1.md'

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert tree is not None
    # confirm info from the yaml header is not present
    assert 'control-origination' not in header
    assert 'label' not in header['x-trestle-set-params']['ac-1_prm_5']

    # generate again with header but do not overwrite header values
    args.yaml_header = cli_yaml_header
    assert ssp_cmd._run(args) == 0

    # confirm new items were added from yaml but not when the same key was alread present (values not updated)
    header, tree = md_api.processor.process_markdown(ac_1)
    assert 'control-origination' in header
    assert header['x-trestle-set-params']['ac-1_prm_5']['label'] == 'meetings cancelled from cli yaml'

    # generate again with header and DO overwrite header values
    args.overwrite_header_values = True
    assert ssp_cmd._run(args) == 0

    # confirm values was now changed
    header, tree = md_api.processor.process_markdown(ac_1)
    assert 'control-origination' in header
    assert header['x-trestle-set-params']['ac-1_prm_5']['values'] == 'new values from cli yaml'
    assert header['x-trestle-set-params']['ac-1_prm_5']['label'] == 'meetings cancelled from cli yaml'

    # edit the header by adding a list item and removing a value
    assert file_utils.insert_text_in_file(ac_1, 'System Specific', '  - My new edits\n')
    assert test_utils.delete_line_in_file(ac_1, 'Corporate')

    # tell it not to add the yaml header
    args.yaml_header = None

    assert ssp_cmd._run(args) == 0
    header, tree = md_api.processor.process_markdown(ac_1)

    co = header['control-origination']
    assert co[0] == 'Service Provider System Specific'
    assert co[1] == 'My new edits'
    assert len(co) == 2

    # tell it to add the yaml header but not overwrite header values
    args.yaml_header = cli_yaml_header
    args.overwrite_header_values

    assert ssp_cmd._run(args) == 0
    header, tree = md_api.processor.process_markdown(ac_1)

    # confirm the extra list item from the cli yaml header is added to the list
    co = header['control-origination']
    assert co[2] == 'Service Provider Corporate'
    assert len(co) == 3


def test_ssp_generate_with_inheritance(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp-generate with inheritance view."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name, False, 'leveraged_ssp')
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    # Test output for each type of file

    # Find export files under This System
    this_system_dir = tmp_trestle_dir / ssp_name / const.INHERITANCE_VIEW_DIR / 'This System'

    expected_uuid = '11111111-0000-4000-9009-001001002001'
    ac_21 = this_system_dir / 'ac-2.1'
    test_provided = ac_21 / f'{expected_uuid}.md'
    assert test_provided.exists()

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(test_provided)
    assert tree is not None

    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'REPLACE_ME'}]
    assert header[const.TRESTLE_STATEMENT_TAG][const.PROVIDED_UUID] == expected_uuid

    expected_provided = """# Provided Statement Description

Consumer-appropriate description of what may be inherited.

In the context of the application component in satisfaction of AC-2.1."""

    # Confirm markdown content
    node = tree.get_node_for_key(const.PROVIDED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == expected_provided

    expected_uuid = '11111111-0000-4000-9009-002001001001'
    ac_2_stm = this_system_dir / 'ac-2_stmt.a'
    test_provided = ac_2_stm / f'{expected_uuid}.md'
    assert test_provided.exists()

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(test_provided)
    assert tree is not None

    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'REPLACE_ME'}]
    assert header[const.TRESTLE_STATEMENT_TAG][const.RESPONSIBILITY_UUID] == expected_uuid

    expected_responsibility = """# Responsibility Statement Description

Leveraging system's responsibilities with respect to inheriting this capability.

In the context of the application component in satisfaction of AC-2, part a.
"""

    # Confirm markdown content
    node = tree.get_node_for_key(const.RESPONSIBILITY_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == expected_responsibility

    # Fine export files under Application
    application_dir = tmp_trestle_dir / ssp_name / const.INHERITANCE_VIEW_DIR / 'Application'

    expected_provided_uuid = '11111111-0000-4000-9009-002001002001'
    expected_responsibility_uuid = '11111111-0000-4000-9009-002001002002'
    ac_2_stm = application_dir / 'ac-2_stmt.a'
    test_provided = ac_2_stm / f'{expected_provided_uuid}_{expected_responsibility_uuid}.md'
    assert test_provided.exists()

    # confirm content in yaml header
    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(test_provided)
    assert tree is not None

    comp_header_value = header[const.TRESTLE_LEVERAGING_COMP_TAG]
    assert comp_header_value == [{'name': 'REPLACE_ME'}]
    assert header[const.TRESTLE_STATEMENT_TAG][const.PROVIDED_UUID] == expected_provided_uuid
    assert header[const.TRESTLE_STATEMENT_TAG][const.RESPONSIBILITY_UUID] == expected_responsibility_uuid

    expected_provided = """# Provided Statement Description

Consumer-appropriate description of what may be inherited.

In the context of the application component in satisfaction of AC-2, part a.
"""

    expected_responsibility = """# Responsibility Statement Description

Leveraging system's responsibilities with respect to inheriting this capability.

In the context of the application component in satisfaction of AC-2, part a.
"""

    # Confirm markdown content
    node = tree.get_node_for_key(const.PROVIDED_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == expected_provided

    node = tree.get_node_for_key(const.RESPONSIBILITY_STATEMENT_DESCRIPTION, False)
    assert node.content.raw_text == expected_responsibility


def test_ssp_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp assemble from cli."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    args_compdefs = gen_args.compdefs

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0
    new_version = '1.2.3'

    prose_sys = 'My response for This System'
    prose_aa = 'My response for comp aa'
    prose_aa_a = 'My response for comp aa part a.'

    # edit it a bit
    ac_1_path = tmp_trestle_dir / ssp_name / 'ac/ac-1.md'
    assert test_utils.substitute_text_in_file(
        ac_1_path, '<!-- Add implementation prose for the main This System component for control: ac-1 -->', prose_sys
    )
    assert test_utils.substitute_text_in_file(ac_1_path, 'imp req prose for ac-1 from comp aa', prose_aa)
    assert test_utils.substitute_text_in_file(ac_1_path, 'statement prose for part a. from comp aa', prose_aa_a)
    # change status for sys comp
    assert test_utils.substitute_text_in_file(ac_1_path, 'Status: planned', 'Status: alternative')

    add_prompt = 'statement prose for part a. from comp ba'
    ac_67_path = tmp_trestle_dir / ssp_name / 'ac/ac-6.7.md'
    assert test_utils.substitute_text_in_file(ac_67_path, add_prompt, prose_aa_a)

    # generate markdown again on top of previous markdown to make sure it is not removed
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    assert test_utils.replace_line_in_file_after_tag(
        ac_1_path, 'ac-1_prm_2:', '    values:\n    ssp-values:\n      - my ssp val\n'
    )
    assert test_utils.replace_line_in_file_after_tag(
        ac_1_path, '- shared_param_1_aa_opt_1', '      ssp-values:\n        - shared_param_1_aa_opt_1\n  comp_ab:\n'
    )

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version=new_version,
        name=None,
        compdefs=args_compdefs
    )
    assert ssp_assemble._run(args) == 0

    orig_ssp, orig_ssp_path = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    orig_uuid = orig_ssp.uuid
    assert len(orig_ssp.system_implementation.components) == 5
    assert orig_ssp.metadata.version == new_version
    assert ModelUtils.model_age(orig_ssp) < test_utils.NEW_MODEL_AGE_SECONDS
    imp_reqs = orig_ssp.control_implementation.implemented_requirements
    imp_req = next((i_req for i_req in imp_reqs if i_req.control_id == 'ac-6.7'), None)
    assert imp_req.statements[0].by_components[0].description == prose_aa_a

    assert imp_reqs[0].by_components[0].set_parameters[1].param_id == 'shared_param_1'
    assert imp_reqs[0].by_components[0].set_parameters[1].values[0] == 'shared_param_1_aa_opt_1'
    assert imp_reqs[0].set_parameters[0].values[0] == 'my ssp val'

    by_comp = orig_ssp.control_implementation.implemented_requirements[0].by_components[2]
    assert by_comp.description == prose_sys

    orig_file_creation = orig_ssp_path.stat().st_mtime

    # now write it back out and confirm text is still there
    assert ssp_gen._run(gen_args) == 0
    assert confirm_control_contains(tmp_trestle_dir, 'ac-1', 'a.', prose_aa_a)
    assert test_utils.confirm_text_in_file(ac_1_path, const.SSP_MD_IMPLEMENTATION_QUESTION, prose_sys)

    # now assemble it again but don't regen uuid's and don't change version
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        name=None,
        version=None,
        compdefs=args_compdefs
    )
    assert ssp_assemble._run(args) == 0

    # confirm the file was not written out since no change
    assert orig_ssp_path.stat().st_mtime == orig_file_creation

    repeat_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    assert len(repeat_ssp.system_implementation.components) == 5
    assert repeat_ssp.metadata.version == new_version

    # assemble it again but regen uuid's
    # this should not regen uuid's because the file is not written out if only difference is uuid's
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=True,
        name=None,
        version=None,
        compdefs=args_compdefs
    )
    assert ssp_assemble._run(args) == 0
    assert orig_uuid == test_utils.get_model_uuid(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    # confirm the file was not written out since no change
    assert orig_ssp_path.stat().st_mtime == orig_file_creation
    # assemble it again but give new version and regen uuid's
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=True,
        name=None,
        version='new version to force write',
        compdefs=args_compdefs
    )
    assert ssp_assemble._run(args) == 0
    assert orig_uuid != test_utils.get_model_uuid(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    # confirm the file was not written out since no change
    assert orig_ssp_path.stat().st_mtime > orig_file_creation


def test_ssp_assemble_fedramp_profile(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Tests ssp assemble with a fedramp profile."""
    gen_args = setup_for_ssp_fedramp(tmp_trestle_dir, ssp_name)
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # first assemble
    ssp_assemble = f'trestle author ssp-assemble -m {ssp_name} -o {ssp_name} -cd {gen_args.compdefs}'
    test_utils.execute_command_and_assert(ssp_assemble, 0, monkeypatch)


def test_ssp_assemble_remove_comp_defs(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Tests the removal of component definitions that are no longer valid for an ssp."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # first assemble
    ssp_assemble = f'trestle author ssp-assemble -m {ssp_name} -o {ssp_name} -cd {gen_args.compdefs}'
    test_utils.execute_command_and_assert(ssp_assemble, 0, monkeypatch)
    # modify component uuids for testing removal
    orig_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    imp_reqs = orig_ssp.control_implementation.implemented_requirements
    components = orig_ssp.system_implementation.components
    generic_uuid = '46b7a556-72bb-4281-b805-a8f4030ca0e3'
    new_component = gens.generate_sample_model(ossp.SystemComponent)
    new_component.uuid = generic_uuid
    new_component.title = 'foo'
    components.append(new_component)
    by_comp = gens.generate_sample_model(ossp.ByComponent)
    by_comp.component_uuid = generic_uuid
    imp_reqs[0].by_components.append(by_comp)

    ModelUtils.save_top_level_model(orig_ssp, tmp_trestle_dir, ssp_name, FileContentType.JSON)
    # reassemble with changes
    ssp_assemble = f'trestle author ssp-assemble -m {ssp_name} -o {ssp_name} -cd {gen_args.compdefs}'
    test_utils.execute_command_and_assert(ssp_assemble, 0, monkeypatch)

    # loads edited ssp again
    edited_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    components = edited_ssp.system_implementation.components
    imp_reqs = edited_ssp.control_implementation.implemented_requirements
    assert not [x for x in components if x.uuid == generic_uuid]
    assert not [x for x in imp_reqs[0].by_components if x.component_uuid == generic_uuid]


def test_ssp_generate_bad_name(tmp_trestle_dir: pathlib.Path) -> None:
    """Test bad output name."""
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile=prof_name, output='catalogs', verbose=0, yaml_header='dummy.yaml'
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_ssp_generate_resolved_catalog(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator to create a resolved profile catalog."""
    _, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    profile_path = tmp_trestle_dir / f'profiles/{prof_name}/profile.json'
    new_catalog_dir = tmp_trestle_dir / f'catalogs/{prof_name}_resolved_catalog'
    new_catalog_dir.mkdir(parents=True, exist_ok=True)
    new_catalog_path = new_catalog_dir / 'catalog.json'

    profile_resolver = ProfileResolver()
    resolved_catalog = profile_resolver.get_resolved_profile_catalog(tmp_trestle_dir, profile_path)
    assert resolved_catalog
    # FIXME this should test with a more complex catalog
    assert len(resolved_catalog.groups) == 2

    resolved_catalog.oscal_write(new_catalog_path)


def test_ssp_assemble_with_inheritance(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp assemble from cli with inheritance view."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name, False, 'leveraged_ssp')
    args_compdefs = gen_args.compdefs

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    this_system_dir = tmp_trestle_dir / ssp_name / const.INHERITANCE_VIEW_DIR / 'This System'

    expected_uuid = '11111111-0000-4000-9009-001001002001'
    ac_21 = this_system_dir / 'ac-2.1'
    test_provided = ac_21 / f'{expected_uuid}.md'

    test_utils.replace_in_file(test_provided, 'REPLACE_ME', 'comp_aa')

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        name=None,
        compdefs=args_compdefs,
        version=None
    )
    assert ssp_assemble._run(args) == 0

    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)

    imp_reqs = ssp.control_implementation.implemented_requirements
    imp_req = next((i_req for i_req in imp_reqs if i_req.control_id == 'ac-2.1'), None)
    inherited = imp_req.by_components[1].inherited[0]  # type: ignore
    assert inherited.description == (
        'Consumer-appropriate description of what may be inherited.\n\n\
In the context of the application component in satisfaction of AC-2.1.'
    )
    assert inherited.provided_uuid == expected_uuid


def test_ssp_filter(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp filter."""
    # FIXME enhance coverage
    # install the catalog and profiles
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        name=None,
        version=None,
        regenerate=False,
        compdefs=gen_args.compdefs
    )
    assert ssp_assemble._run(args) == 0

    ssp: ossp.SystemSecurityPlan
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)

    assert len(ssp.control_implementation.implemented_requirements) == 8

    filtered_name = 'filtered_ssp'

    # now filter the ssp through comp_prof_aa
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile='comp_prof_aa',
        output=filtered_name,
        verbose=0,
        regenerate=False,
        version=None,
        components=None,
        implementation_status=None,
        control_origination=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # confirm the imp_reqs have been culled by profile_d to only two controls
    assert len(ssp.control_implementation.implemented_requirements) == 3

    # confirm there are three by_comps for: this system, foo, bar
    assert len(ssp.control_implementation.implemented_requirements[0].statements[0].by_components) == 2

    # now filter the ssp by components
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components='comp_aa',
        implementation_status=None,
        control_origination=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # filter the filtered ssp again to confirm uuid does not change even with regen because contents are the same
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=filtered_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components='comp_aa',
        implementation_status=None,
        control_origination=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    # now filter the ssp by multiple implementation statuses
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=False,
        version=None,
        components=None,
        implementation_status='not-applicable,implemented',
        control_origination=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # confirm the imp_reqs have been culled by impl_status to five controls
    assert len(ssp.control_implementation.implemented_requirements) == 5
    # confirm there are is two by_comps for the first impl_req
    assert len(ssp.control_implementation.implemented_requirements[0].by_components) == 2

    # now filter the ssp by an implementation status that is unused
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=False,
        version=None,
        components=None,
        implementation_status='not-applicable',
        control_origination=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # confirm the imp_reqs have been culled by impl_status to zero controls
    assert len(ssp.control_implementation.implemented_requirements) == 0

    # now filter without profile or components to trigger error
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components=None,
        implementation_status=None,
        control_origination=None
    )

    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1

    # now filter the ssp through comp_prof_bad to force error because it references a control not in the ssp
    bad_prof = 'comp_prof_bad'
    test_utils.load_from_json(tmp_trestle_dir, bad_prof, bad_prof, prof.Profile)
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=bad_prof,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components=None,
        implementation_status=None,
        control_origination=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1

    # now filter with an invalid implementation status to trigger error
    bad_impl = 'impl_bad'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components=None,
        implementation_status=bad_impl,
        control_origination=None
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1


def test_ssp_filter_control_origination(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp filter when filtering by control origination."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        name=None,
        version=None,
        regenerate=False,
        compdefs=gen_args.compdefs
    )
    assert ssp_assemble._run(args) == 0

    ssp: ossp.SystemSecurityPlan
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)

    assert len(ssp.control_implementation.implemented_requirements) == 8

    filtered_name = 'filtered_ssp'

    # now filter the ssp by multiple control origination values
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=False,
        version=None,
        components=None,
        implementation_status=None,
        control_origination='customer-configured,system-specific'
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # confirm the imp_reqs have been culled to two controls
    assert len(ssp.control_implementation.implemented_requirements) == 2

    # now filter the ssp by a control origination that is unused
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=False,
        version=None,
        components=None,
        implementation_status=None,
        control_origination='inherited'
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 0

    ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        filtered_name,
        ossp.SystemSecurityPlan,
        FileContentType.JSON
    )

    # confirm the imp_reqs have been culled to zero controls
    assert len(ssp.control_implementation.implemented_requirements) == 0

    # filter with an invalid control origination to trigger error
    bad_co = 'co_bad'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        name=ssp_name,
        profile=None,
        output=filtered_name,
        verbose=0,
        regenerate=True,
        version=None,
        components=None,
        implementation_status=None,
        control_origination=bad_co
    )
    ssp_filter = SSPFilter()
    assert ssp_filter._run(args) == 1


def test_ssp_bad_control_id(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp gen when profile has bad control id."""
    profile = prof.Profile.oscal_read(test_utils.JSON_TEST_DATA_PATH / 'profile_bad_control.json')
    ModelUtils.save_top_level_model(profile, tmp_trestle_dir, 'bad_prof', FileContentType.JSON)
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile='bad_prof', output='my_ssp', verbose=0, sections=None, yaml_header=None
    )
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 1


def test_ssp_assemble_header_metadata(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test parsing of metadata from yaml header."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    header_path = test_utils.YAML_TEST_DATA_PATH / 'header_with_metadata.yaml'
    args.yaml_header = header_path
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0

    # create ssp from the markdown
    ssp_assemble = f'trestle author ssp-assemble -m {ssp_name} -o {ssp_name} -cd {args.compdefs}'
    test_utils.execute_command_and_assert(ssp_assemble, 0, monkeypatch)

    # read the assembled ssp and confirm roles are in metadata
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
    # FIXME assert len(ssp.metadata.roles) == 2


def test_ssp_force_overwrite(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp generate with force-overwrite."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)

    # confirm that setting force_overwrite with empty dir does not fail on generate
    args.force_overwrite = True
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    fc = test_utils.FileChecker(tmp_trestle_dir / 'my_ssp/')

    ac_1 = tmp_trestle_dir / ssp_name / 'ac' / 'ac-1.md'
    assert ac_1.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)

    assert tree
    old_value = '<!-- Add implementation prose for the main This System component for control: ac-1 -->'
    assert old_value in tree.content.raw_text
    tree.content.raw_text = tree.content.raw_text.replace(old_value, 'Custom control implementation')
    md_api.write_markdown_with_header(ac_1, header, tree.content.raw_text)

    # re-run without force overwrite and confirm edits still there
    args.force_overwrite = False
    assert ssp_cmd._run(args) == 0

    header, tree = md_api.processor.process_markdown(ac_1)
    assert 'Custom control implementation' in tree.content.raw_text

    # run again with overwrite and confirm edits are gone
    args.force_overwrite = True
    assert ssp_cmd._run(args) == 0

    header, tree = md_api.processor.process_markdown(ac_1)
    assert old_value in tree.content.raw_text

    assert fc.files_unchanged()


def test_merge_statement() -> None:
    """Test merge statement."""
    imp_req = gens.generate_sample_model(ossp.ImplementedRequirement, True)
    new_statement = gens.generate_sample_model(ossp.Statement, True)
    prose = 'my new prose'
    new_statement.by_components[0].description = prose
    SSPAssemble._merge_statement(imp_req, new_statement, [])
    assert imp_req.statements[0].by_components[0].description == prose


def test_merge_imp_req() -> None:
    """Test merge statement."""
    imp_req_a = gens.generate_sample_model(ossp.ImplementedRequirement, True)
    imp_req_b = generic.GenericImplementedRequirement.generate()
    statement = generic.GenericStatement(statement_id=const.REPLACE_ME, uuid=const.SAMPLE_UUID_STR, description='foo')
    by_comp = generic.GenericByComponent.generate()
    prose = 'my new prose'
    by_comp.description = prose
    statement.by_components = [by_comp]
    imp_req_b.statements = [statement]
    SSPAssemble._merge_imp_req_into_imp_req(imp_req_a, imp_req_b, [])
    assert imp_req_a.statements[0].by_components[0].description == prose


def test_ssp_warning_missing_control(tmp_trestle_dir: pathlib.Path, capsys) -> None:
    """Test ssp success when profile missing control."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    prof_path = tmp_trestle_dir / 'profiles/comp_prof/profile.json'
    # remove the reference to control ac-1
    test_utils.delete_line_in_file(prof_path, 'ac-1')
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0
    _, err = capsys.readouterr()
    assert 'Component comp_aa references control ac-1 not in profile.' in err


def test_ssp_assemble_no_comps(tmp_trestle_dir: pathlib.Path, capsys) -> None:
    """Test ssp assemble with no compdefs."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    gen_args.compdefs = None
    gen_args.yaml_header = None

    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    prose_sys = 'My response for This System'

    # edit it a bit
    ac_1_path = tmp_trestle_dir / ssp_name / 'ac/ac-1.md'
    assert test_utils.substitute_text_in_file(
        ac_1_path, '<!-- Add implementation prose for the main This System component for control: ac-1 -->', prose_sys
    )
    # change status for sys comp
    assert test_utils.substitute_text_in_file(ac_1_path, 'Status: planned', 'Status: alternative')

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version=None,
        name=None,
        compdefs=None
    )
    assert ssp_assemble._run(args) == 0

    assem_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    assert len(assem_ssp.system_implementation.components) == 1
    # following tests pass on windows but not others
    imp_req = list_utils.get_item_from_list(
        assem_ssp.control_implementation.implemented_requirements, 'ac-1', lambda x: x.control_id
    )
    by_comp = imp_req.by_components[0]
    assert by_comp.description == prose_sys
    assert by_comp.implementation_status.state == 'alternative'

    assert test_utils.replace_line_in_file_after_tag(
        ac_1_path, 'Status: alternative', '\n### Bad Component\n\n#### Status planned\n'
    )
    assert ssp_assemble._run(args) == 1
    _, err = capsys.readouterr()
    assert 'Control ac-1 references component Bad Component not defined' in err
    assert 'Please specify the names of any component-definitions' in err


def test_ssp_gen_and_assemble_more_than_one_param(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp generate and assemble with more than 1 parameters per rule."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name, False, '', 'comp_def_more_params')
    args_compdefs = gen_args.compdefs

    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0
    new_version = '1.2.3'

    md_path = tmp_trestle_dir / ssp_name / 'ac' / 'ac-1.md'
    assert md_path.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(md_path)
    rule_parameters = header['x-trestle-comp-def-rules-param-vals']['comp_ca']
    rule_parameters.append({'name': 'allowed_admins_per_account2', 'values': ['20']})

    md_api.write_markdown_with_header(md_path, header, tree.content.raw_text)

    # verifies a second parameter has beend added to the top shared rule
    assert header['x-trestle-rules-params']['comp_ca'][1]['name'] == 'allowed_admins_per_account2'

    # verifies the parameter value for the rule has been written down correctly in the markdown file
    assert header['x-trestle-comp-def-rules-param-vals']['comp_ca'][1]['values'] == ['20']

    # now assemble controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version=new_version,
        name=None,
        compdefs=args_compdefs
    )
    assert ssp_assemble._run(args) == 0

    assem_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    set_parameters = assem_ssp.control_implementation.implemented_requirements[0].by_components[0].set_parameters
    set_params = [
        set_param.param_id for set_param in set_parameters if set_param.param_id == 'allowed_admins_per_account2'
    ]
    # this demonstrates there's only one iteration of the parameter and not being repeated
    assert len(set_params) == 1


def test_ssp_gen_throw_exception_for_rep_comps(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp generate for duplicated component uuids between diff component definition."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name, False, '',
                                'comp_def_more_params,comp_def_more_params_dup')
    # first create the markdown
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 1


def test_ssp_gen_and_assemble_add_props(tmp_trestle_dir: pathlib.Path) -> None:
    """Test ssp generate and assemble with additional properties processing."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    gen_args.yaml_header = None
    ssp_cmd = SSPGenerate()

    assert ssp_cmd._run(gen_args) == 0

    md_path = tmp_trestle_dir / ssp_name / 'ac' / 'ac-1.md'
    assert md_path.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(md_path)

    # Create key in header for add props for now
    ac_1_properties: Dict[str, str] = {
        'name': 'prop_with_ns', 'value': 'prop with ns', 'ns': 'https://my_new_namespace'
    }
    ac_1_smt_properties: Dict[str, str] = {'name': 'smt_prop', 'value': 'smt prop', 'smt-part': 'a.'}
    # Verify the add props header value is present
    properties: List[Dict[str, str]] = header.get('x-trestle-add-props')
    properties.extend([ac_1_properties, ac_1_smt_properties])

    md_api.write_markdown_with_header(md_path, header, tree.content.raw_text)

    args_compdefs = gen_args.compdefs
    # now assemble controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=1,
        name=None,
        version=None,
        compdefs=args_compdefs,
        regenerate=False,
    )
    assert ssp_assemble._run(args) == 0

    assem_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    impl_reqs = assem_ssp.control_implementation.implemented_requirements
    impl_req = next((i_req for i_req in impl_reqs if i_req.control_id == 'ac-1'), None)
    assert len(impl_req.props) == 1
    assert impl_req.props[0].name == 'prop_with_ns'
    assert impl_req.props[0].value == 'prop with ns'
    assert impl_req.props[0].ns == 'https://my_new_namespace'

    smt_a = next((smt for smt in impl_req.statements if smt.statement_id == 'ac-1_smt.a'), None)
    assert len(smt_a.props) == 1
    assert smt_a.props[0].name == 'smt_prop'
    assert smt_a.props[0].value == 'smt prop'


def test_ssp_gen_and_assemble_implementation_parts(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp generate and assemble edit implementation parts."""
    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    args_compdefs = gen_args.compdefs
    gen_args.include_all_parts = True

    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    prose_sys = 'My response for This System'
    prose_aa = 'My response for comp aa'
    prose_sys_a = 'My response for This System part a.'
    prose_aa_a = 'My response for comp aa part a.'

    # ac-1 edit
    ac_1_path = tmp_trestle_dir / ssp_name / 'ac/ac-1.md'
    assert test_utils.substitute_text_in_file(
        ac_1_path, '<!-- Add implementation prose for the main This System component for control: ac-1 -->', prose_sys
    )
    assert test_utils.substitute_text_in_file(
        ac_1_path,
        '<!-- Add implementation prose for the main This System component for control: ac-1_smt.a -->',
        prose_sys_a
    )
    assert test_utils.substitute_text_in_file(ac_1_path, 'imp req prose for ac-1 from comp aa', prose_aa)
    assert test_utils.substitute_text_in_file(ac_1_path, 'statement prose for part a. from comp aa', prose_aa_a)
    # change status for sys comp
    assert test_utils.substitute_text_in_file(ac_1_path, 'Status: planned', 'Status: alternative')

    part_a_text_edited = """## Implementation for part a.

### This System

My response for This System part a.

#### Implementation Status: planned

### comp_aa

My response for comp aa part a.

#### Rules:

  - comp_rule_aa_1

#### Implementation Status: partial

### comp_ab

<!-- Add control implementation description here for item a. -->

#### Rules:

  - comp_rule_ab_1

#### Implementation Status: partial

______________________________________________________________________
"""

    md_api = MarkdownAPI()
    _, tree = md_api.processor.process_markdown(ac_1_path)
    node = tree.get_node_for_key('## Implementation for part a.')
    assert node.content.raw_text == part_a_text_edited

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version='',
        name=None,
        compdefs=args_compdefs
    )
    assert ssp_assemble._run(args) == 0

    # Verify the correct information is in the assembled ssp
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
    imp_reqs = ssp.control_implementation.implemented_requirements
    ac_1_imp_req = next((i_req for i_req in imp_reqs if i_req.control_id == 'ac-1'), None)
    assert ac_1_imp_req is not None

    # comp_aa is the first component in the list and This System is the last
    assert ac_1_imp_req.by_components[0].description == prose_aa  # type: ignore
    assert ac_1_imp_req.by_components[2].implementation_status.state == 'alternative'  # type: ignore
    assert ac_1_imp_req.by_components[2].description == prose_sys  # type: ignore
    ac_1_a_smt = next((smt for smt in ac_1_imp_req.statements if smt.statement_id == 'ac-1_smt.a'), None)
    assert ac_1_a_smt is not None
    assert ac_1_a_smt.by_components[0].description == prose_aa_a  # type: ignore
    assert ac_1_a_smt.by_components[2].description == prose_sys_a  # type: ignore

    # Regeneration checks to make sure the markdown is not overwritten
    assert ssp_gen._run(gen_args) == 0
    _, tree = md_api.processor.process_markdown(ac_1_path)
    node = tree.get_node_for_key('## Implementation for part a.')
    assert node.content.raw_text == part_a_text_edited
    assert test_utils.confirm_text_in_file(ac_1_path, const.SSP_MD_IMPLEMENTATION_QUESTION, prose_sys)


def test_ssp_generate_no_cds_include_all_parts(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with no comp defs and include all parts are true."""
    args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)

    args.compdefs = None
    args.include_all_parts = True
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    md_dir = tmp_trestle_dir / ssp_name
    ac_1 = md_dir / 'ac/ac-1.md'
    assert ac_1.exists()
    at_2 = md_dir / 'at/at-2.md'
    assert at_2.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(ac_1)
    assert header[const.TRESTLE_GLOBAL_TAG][const.SORT_ID] == 'ac-01'

    part_a_text_no_comp = """## Implementation for part a.

### This System

<!-- Add implementation prose for the main This System component for control: ac-1_smt.a -->

#### Implementation Status: planned

______________________________________________________________________
"""

    node = tree.get_node_for_key('## Implementation for part a.')
    assert node.content.raw_text == part_a_text_no_comp


def test_ssp_generate_aggregates_no_cds(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator with no comp defs does aggregate values from aggregated parameters."""
    args, _ = setup_for_ssp(tmp_trestle_dir, 'profile_aggregation', ssp_name)

    args.compdefs = None
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    md_dir = tmp_trestle_dir / ssp_name
    si_7 = md_dir / 'si-7.md'
    assert si_7.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(si_7)
    si_7_odp_01 = header['x-trestle-set-params']['si-07_odp.01']
    si_7_odp_01['ssp-values'] = ['changed value in the ssp markdown']

    md_api.write_markdown_with_header(si_7, header, tree.content.raw_text)

    # now assemble the edited controls into json ssp
    ssp_assemble = SSPAssemble()
    assemble_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version='',
        name=None,
        compdefs=None
    )
    assert ssp_assemble._run(assemble_args) == 0

    # Verify the correct information is in the assembled ssp
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
    imp_reqs = ssp.control_implementation.implemented_requirements
    si_7_imp_req = next((i_req for i_req in imp_reqs if i_req.control_id == 'si-7'), None)
    si_07_odp_01 = next((param for param in si_7_imp_req.set_parameters if param.param_id == 'si-07_odp.01'), None)
    changed_value_in_ssp = next(
        (val for val in si_07_odp_01.values if val == 'changed value in the ssp markdown'), None
    )
    assert changed_value_in_ssp is not None

    # regenerate the SSP again
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    md_dir = tmp_trestle_dir / ssp_name
    si_7 = md_dir / 'si-7.md'
    assert si_7.exists()

    md_api = MarkdownAPI()
    header, tree = md_api.processor.process_markdown(si_7)
    si_7_odp_01 = header['x-trestle-set-params']['si-07_odp.01']
    assert 'changed value in the ssp markdown' in si_7_odp_01['ssp-values']


def test_ssp_generate_aggregates_no_param_value_orig(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the ssp generator aggregate parameters have no parame-value-origin."""
    args, _ = setup_for_ssp(tmp_trestle_dir, 'profile_aggregation', ssp_name)

    args.compdefs = None
    ssp_cmd = SSPGenerate()
    assert ssp_cmd._run(args) == 0
    md_dir = tmp_trestle_dir / ssp_name
    si_7 = md_dir / 'si-7.md'
    assert si_7.exists()

    md_api = MarkdownAPI()
    header, _ = md_api.processor.process_markdown(si_7)
    si_7_prm_1 = header['x-trestle-set-params']['si-7_prm_1']
    assert const.PARAM_VALUE_ORIGIN not in si_7_prm_1.keys()
