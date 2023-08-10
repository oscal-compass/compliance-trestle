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

from tests import test_utils

import trestle.common.const as const
import trestle.core.crm.export_reader as exportreader
import trestle.oscal.ssp as ossp
from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType

leveraged_ssp = 'leveraged_ssp'
leveraging_ssp = 'my_ssp'

expected_appliance_uuid = '22222222-0000-4000-9001-000000000003'
expected_saas_uuid = '22222222-0000-4000-9001-000000000001'

inheritance_text = """---
x-trestle-statement:
  # Add or modify leveraged SSP Statements here.
  provided-uuid: 18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114
  responsibility-uuid: 4b34c68f-75fa-4b38-baf0-e50158c13ac2
x-trestle-leveraging-comp:
  # Leveraged statements can be optionally associated with components in this system.
  # Associate leveraged statements to Components of this system here:
  - name: Access Control Appliance
  - name: THIS SYSTEM (SaaS)
---

# Provided Statement Description

provided statement description

# Responsibility Statement Description

resp statement description

# Satisfied Statement Description

<!-- Use this section to explain how the inherited responsibility is being satisfied. -->
My Satisfied Description
"""

inheritance_text_2 = """---
x-trestle-statement:
  # Add or modify leveraged SSP Statements here.
  provided-uuid: 18ac4e2a-b5f2-46e4-94fa-cc84ab6fe115
  responsibility-uuid: 4b34c68f-75fa-4b38-baf0-e50158c13ac3
x-trestle-leveraging-comp:
  # Leveraged statements can be optionally associated with components in this system.
  # Associate leveraged statements to Components of this system here:
  - name: Access Control Appliance
---

# Provided Statement Description

provided statement description

# Responsibility Statement Description

resp statement description

# Satisfied Statement Description

<!-- Use this section to explain how the inherited responsibility is being satisfied. -->
My Satisfied Description
"""


def test_read_exports_from_markdown(tmp_trestle_dir: pathlib.Path) -> None:
    """Test exports reader with inheritance view."""
    ipath = tmp_trestle_dir.joinpath(leveraging_ssp, const.INHERITANCE_VIEW_DIR)

    ac_appliance_dir = ipath.joinpath('Access Control Appliance')
    ac_2 = ac_appliance_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(ipath, orig_ssp)  # type: ignore
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


def test_read_inheritance_markdown_dir(tmp_trestle_dir: pathlib.Path) -> None:
    """Test reading inheritance view directory."""
    ipath = tmp_trestle_dir.joinpath(leveraging_ssp, const.INHERITANCE_VIEW_DIR)
    ac_appliance_dir = ipath.joinpath('Access Control Appliance')
    ac_2 = ac_appliance_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(ipath, orig_ssp)  # type: ignore
    markdown_dict: exportreader.InheritanceViewDict = reader._read_inheritance_markdown_directory()

    assert len(markdown_dict) == 1
    assert 'ac-2' in markdown_dict
    assert len(markdown_dict['ac-2']) == 2
    assert expected_appliance_uuid in markdown_dict['ac-2']

    inheritance_info = markdown_dict['ac-2'][expected_appliance_uuid]

    assert inheritance_info[0][0].provided_uuid == '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'
    assert inheritance_info[1][0].responsibility_uuid == '4b34c68f-75fa-4b38-baf0-e50158c13ac2'
    assert inheritance_info[1][0].description == 'My Satisfied Description'


def test_read_inheritance_markdown_dir_with_multiple_leveraged_components(tmp_trestle_dir: pathlib.Path) -> None:
    """Test reading inheritance view directory with components that span multiple leveraged components."""
    ipath = tmp_trestle_dir.joinpath(leveraging_ssp, const.INHERITANCE_VIEW_DIR)

    ac_appliance_dir = ipath.joinpath('Access Control Appliance')
    ac_2 = ac_appliance_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)

    this_system_dir = ipath.joinpath('This System')
    ac_2 = this_system_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    file = ac_2 / f'{expected_appliance_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text_2)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    reader = exportreader.ExportReader(ipath, orig_ssp)  # type: ignore
    markdown_dict: exportreader.InheritanceViewDict = reader._read_inheritance_markdown_directory()

    assert len(markdown_dict) == 1
    assert 'ac-2' in markdown_dict
    assert len(markdown_dict['ac-2']) == 2

    assert expected_appliance_uuid in markdown_dict['ac-2']
    inheritance_info = markdown_dict['ac-2'][expected_appliance_uuid]

    assert len(inheritance_info[0]) == 2
    assert len(inheritance_info[1]) == 2
