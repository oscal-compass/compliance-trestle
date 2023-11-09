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

import pathlib
import uuid

import pytest

from tests import test_utils

import trestle.common.const as const
import trestle.core.crm.export_reader as exportreader
import trestle.core.generators as gens
import trestle.oscal.ssp as ossp
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType

leveraged_ssp = 'leveraged_ssp'
leveraging_ssp = 'my_ssp'

expected_appliance_uuid = '22222222-0000-4000-9001-000000000003'
expected_saas_uuid = '22222222-0000-4000-9001-000000000001'

example_provided_uuid = '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'
example_responsibility_uuid = '4b34c68f-75fa-4b38-baf0-e50158c13ac2'


@pytest.fixture(scope='function')
def sample_implemented_requirement() -> ossp.ImplementedRequirement:
    """Return a valid ComponentDefinition object with some contents."""
    # one component has no properties - the other has two
    impl_req: ossp.ImplementedRequirement = gens.generate_sample_model(ossp.ImplementedRequirement)
    by_comp: ossp.ByComponent = gens.generate_sample_model(ossp.ByComponent)
    impl_req.by_components = [by_comp]
    return impl_req


def prep_inheritance_dir(ac_appliance_dir: pathlib.Path, inheritance_text: str) -> None:
    """Prepare inheritance directory with basic information."""
    ac_2 = ac_appliance_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)

    # test with a statement
    ac_2a = ac_appliance_dir.joinpath('ac-2_smt.a')
    ac_2a.mkdir(parents=True)

    file = ac_2a / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)


def test_read_exports_from_markdown(tmp_trestle_dir: pathlib.Path) -> None:
    """Test exports reader with inheritance view."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)
    ac_appliance_dir = inheritance_path.joinpath('Access Control Appliance')
    inheritance_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Access Control Appliance', 'THIS SYSTEM (SaaS)'],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )
    prep_inheritance_dir(ac_appliance_dir, inheritance_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(inheritance_path, orig_ssp)
    ssp = reader.read_exports_from_markdown()

    implemented_requirements = ssp.control_implementation.implemented_requirements

    assert implemented_requirements[0].control_id == 'ac-2'
    assert implemented_requirements[0].by_components[0].component_uuid == expected_appliance_uuid  # type: ignore

    by_comp = implemented_requirements[0].by_components[0]  # type: ignore

    assert by_comp.inherited[0].provided_uuid == '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'  # type: ignore
    assert by_comp.satisfied[0].responsibility_uuid == '4b34c68f-75fa-4b38-baf0-e50158c13ac2'  # type: ignore
    assert by_comp.satisfied[0].description == 'My Satisfied Description'  # type: ignore

    assert implemented_requirements[0].by_components[1].component_uuid == expected_saas_uuid  # type: ignore
    by_comp = implemented_requirements[0].by_components[1]  # type: ignore

    assert by_comp.inherited[0].provided_uuid == '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'  # type: ignore
    assert by_comp.satisfied[0].responsibility_uuid == '4b34c68f-75fa-4b38-baf0-e50158c13ac2'  # type: ignore
    assert by_comp.satisfied[0].description == 'My Satisfied Description'  # type: ignore

    # Ensure that the statement is also added to the SSP
    assert implemented_requirements[0].statements is not None
    assert implemented_requirements[0].statements[0].statement_id == 'ac-2_smt.a'


def test_read_inheritance_markdown_dir(tmp_trestle_dir: pathlib.Path) -> None:
    """Test reading inheritance view directory."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)
    ac_appliance_dir = inheritance_path.joinpath('Access Control Appliance')
    inheritance_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Access Control Appliance', 'THIS SYSTEM (SaaS)'],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )
    prep_inheritance_dir(ac_appliance_dir, inheritance_text)

    unmapped_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=[const.REPLACE_ME],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )

    ac_21 = ac_appliance_dir.joinpath('ac-2.1')
    ac_21.mkdir(parents=True)
    # Ensure this file does not get added to the dictionary
    file = ac_21 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(unmapped_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(inheritance_path, orig_ssp)
    markdown_dict: exportreader.InheritanceViewDict = reader._read_inheritance_markdown_directory()

    assert len(markdown_dict) == 3
    assert 'ac-2' in markdown_dict
    assert len(markdown_dict['ac-2']) == 2
    assert expected_appliance_uuid in markdown_dict['ac-2']

    assert len(markdown_dict['ac-2.1']) == 0

    inheritance_info = markdown_dict['ac-2'][expected_appliance_uuid]

    assert inheritance_info[0][0].provided_uuid == '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'
    assert inheritance_info[1][0].responsibility_uuid == '4b34c68f-75fa-4b38-baf0-e50158c13ac2'
    assert inheritance_info[1][0].description == 'My Satisfied Description'


def test_read_inheritance_markdown_dir_with_multiple_leveraged_components(tmp_trestle_dir: pathlib.Path) -> None:
    """Test reading inheritance view directory with components that span multiple leveraged components."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)

    ac_appliance_dir = inheritance_path.joinpath('Access Control Appliance')
    inheritance_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Access Control Appliance', 'THIS SYSTEM (SaaS)'],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )
    prep_inheritance_dir(ac_appliance_dir, inheritance_text)

    inheritance_text_2 = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Access Control Appliance'],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )

    unmapped_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=[const.REPLACE_ME],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )

    this_system_dir = inheritance_path.joinpath('This System')
    ac_2 = this_system_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text_2)

    ac_2a = this_system_dir.joinpath('ac-2_smt.a')
    ac_2a.mkdir(parents=True)

    file = ac_2a / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(unmapped_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(inheritance_path, orig_ssp)
    markdown_dict: exportreader.InheritanceViewDict = reader._read_inheritance_markdown_directory()

    assert len(markdown_dict) == 2
    assert 'ac-2' in markdown_dict
    assert len(markdown_dict['ac-2']) == 2

    assert expected_appliance_uuid in markdown_dict['ac-2']
    inheritance_info = markdown_dict['ac-2'][expected_appliance_uuid]

    assert len(inheritance_info[0]) == 2
    assert len(inheritance_info[1]) == 2

    assert 'ac-2_smt.a' in markdown_dict
    assert len(markdown_dict['ac-2_smt.a']) == 2

    assert expected_appliance_uuid in markdown_dict['ac-2_smt.a']
    inheritance_info = markdown_dict['ac-2_smt.a'][expected_appliance_uuid]

    # Only leveraging from one component
    assert len(inheritance_info[0]) == 1
    assert len(inheritance_info[1]) == 1


def test_read_inheritance_markdown_dir_with_invalid_mapping(tmp_trestle_dir: pathlib.Path) -> None:
    """Test reading inheritance view directory with a component that does not exist."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)

    invalid_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Invalid Component'],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )

    this_system_dir = inheritance_path.joinpath('This System')
    ac_2 = this_system_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(invalid_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    with pytest.raises(TrestleError):
        reader = exportreader.ExportReader(inheritance_path, orig_ssp)
        _ = reader._read_inheritance_markdown_directory()


def test_get_leveraged_ssp_reference(tmp_trestle_dir: pathlib.Path) -> None:
    """Test retrieving leveraged SSP reference from Markdown."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)

    ac_appliance_dir = inheritance_path.joinpath('Access Control Appliance')
    inheritance_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Access Control Appliance', 'THIS SYSTEM (SaaS)'],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )
    prep_inheritance_dir(ac_appliance_dir, inheritance_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(inheritance_path, orig_ssp)
    assert reader.get_leveraged_ssp_href() == 'trestle://leveraged_ssp.json'


def test_get_leveraged_components(tmp_trestle_dir: pathlib.Path) -> None:
    """Test leveraged mapped components from Markdown."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)

    ac_appliance_dir = inheritance_path.joinpath('Access Control Appliance')
    unmapped_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=[const.REPLACE_ME],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )
    prep_inheritance_dir(ac_appliance_dir, unmapped_text)

    this_system_dir = inheritance_path.joinpath('This System')
    ac_2 = this_system_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    inheritance_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Access Control Appliance', 'THIS SYSTEM (SaaS)'],
        leveraged_ssp_href='trestle://leveraged_ssp.json'
    )

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(inheritance_path, orig_ssp)
    _ = reader.read_exports_from_markdown()

    leveraged_components = reader.get_leveraged_components()

    assert len(leveraged_components) == 1
    assert 'Access Control Appliance' not in leveraged_components
    assert 'This System' in leveraged_components


def test_update_type_with_by_comp(sample_implemented_requirement: ossp.ImplementedRequirement) -> None:
    """Test update type with by component."""
    test_ssp: ossp.SystemSecurityPlan = gens.generate_sample_model(ossp.SystemSecurityPlan)
    reader = exportreader.ExportReader('', test_ssp)

    test_inherited: ossp.Inherited = gens.generate_sample_model(ossp.Inherited)
    test_satisfied: ossp.Satisfied = gens.generate_sample_model(ossp.Satisfied)

    test_comp_uuid = str(uuid.uuid4())

    test_by_comp_dict: exportreader.ByComponentDict = {test_comp_uuid: ([test_inherited], [test_satisfied])}

    assert len(sample_implemented_requirement.by_components) == 1

    reader._update_type_with_by_comp(sample_implemented_requirement, test_by_comp_dict)

    # Ensure a new by_comp was added, but the original was not removed
    assert len(sample_implemented_requirement.by_components) == 2

    # Test update the existing without adding a new component
    test_satisfied.description = 'Updated Description'
    test_by_comp_dict: exportreader.ByComponentDict = {test_comp_uuid: ([test_inherited], [test_satisfied])}
    reader._update_type_with_by_comp(sample_implemented_requirement, test_by_comp_dict)

    assert len(sample_implemented_requirement.by_components) == 2
    new_by_comp = sample_implemented_requirement.by_components[1]  # type: ignore

    assert new_by_comp.component_uuid == test_comp_uuid
    assert new_by_comp.satisfied is not None
    assert new_by_comp.satisfied[0].description == 'Updated Description'

    # Test removing the existing inheritance info
    test_by_comp_dict: exportreader.ByComponentDict = {}
    reader._update_type_with_by_comp(sample_implemented_requirement, test_by_comp_dict)

    new_by_comp = sample_implemented_requirement.by_components[1]  # type: ignore

    assert new_by_comp.component_uuid == test_comp_uuid
    assert new_by_comp.satisfied is None
    assert new_by_comp.inherited is None
