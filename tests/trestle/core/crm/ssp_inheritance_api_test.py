# -*- mode:python; coding:utf-8 -*-
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
"""Tests for SSP Inheritance API."""

import copy
import logging
import pathlib

from tests import test_utils

import trestle.oscal.ssp as ossp
from trestle.common import const
from trestle.common.model_utils import ModelUtils
from trestle.core.crm.ssp_inheritance_api import SSPInheritanceAPI
from trestle.core.models.file_content_type import FileContentType

logger = logging.getLogger(__name__)

leveraging_ssp = 'my_ssp'
leveraged_ssp = 'leveraged_ssp'

expected_application_uuid = '11111111-0000-4000-9001-000000000002'
example_provided_uuid = '18ac4e2a-b5f2-46e4-94fa-cc84ab6fe114'
example_responsibility_uuid = '4b34c68f-75fa-4b38-baf0-e50158c13ac2'


def prep_dir(component_dir: pathlib.Path) -> None:
    """Prep dir."""
    ac_2 = component_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    inheritance_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=['Access Control Appliance', 'THIS SYSTEM (SaaS)'],
        leveraged_ssp_href='trestle://system-security-plans/leveraged_ssp/system-security-plan.json'
    )

    file = ac_2 / f'{expected_application_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)

    # test with a statement
    ac_2a = component_dir.joinpath('ac-2_smt.a')
    ac_2a.mkdir(parents=True)

    file = ac_2a / f'{expected_application_uuid}.md'
    with open(file, 'w') as f:
        f.write(inheritance_text)


def unmapped_prep_dir(component_dir: pathlib.Path) -> None:
    """Unmapped prep dir."""
    ac_2 = component_dir.joinpath('ac-2')
    ac_2.mkdir(parents=True)

    unmapped_text = test_utils.generate_test_inheritance_md(
        provided_uuid=example_provided_uuid,
        responsibility_uuid=example_responsibility_uuid,
        leveraged_statement_names=[const.REPLACE_ME],
        leveraged_ssp_href='trestle://system-security-plans/leveraged_ssp/system-security-plan.json'
    )

    file = ac_2 / f'{expected_application_uuid}.md'
    with open(file, 'w') as f:
        f.write(unmapped_text)

    # test with a statement
    ac_2a = component_dir.joinpath('ac-2_smt.a')
    ac_2a.mkdir(parents=True)

    file = ac_2a / f'{expected_application_uuid}.md'
    with open(file, 'w') as f:
        f.write(unmapped_text)


def test_update_ssp_inheritance(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that a leveraged authorization is created."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)
    application_dir = inheritance_path.joinpath('Application')
    prep_dir(application_dir)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraged_ssp', leveraged_ssp, ossp.SystemSecurityPlan)
    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    components = orig_ssp.system_implementation.components

    assert len(components) == 5
    assert len(orig_ssp.system_implementation.leveraged_authorizations) == 1

    ssp_inheritance_api = SSPInheritanceAPI(inheritance_path, tmp_trestle_dir)
    ssp_inheritance_api.update_ssp_inheritance(orig_ssp)

    assert orig_ssp.system_implementation.leveraged_authorizations is not None

    assert len(orig_ssp.system_implementation.leveraged_authorizations) == 1

    auth = orig_ssp.system_implementation.leveraged_authorizations[0]

    assert auth.links is not None
    assert len(auth.links) == 1
    assert auth.links[0].href == 'trestle://system-security-plans/leveraged_ssp/system-security-plan.json'

    components = orig_ssp.system_implementation.components

    # This reduce to 4 by removing old leveraged components and adding application
    assert len(components) == 4

    # Verify that all expected components are present
    component_titles = [obj.title for obj in components]

    assert 'Access Control Appliance' in component_titles
    assert 'THIS SYSTEM (SaaS)' in component_titles
    assert 'Application' in component_titles
    assert 'This System' in component_titles

    assert components[3].title == 'Application'
    assert components[3].props is not None
    assert len(components[3].props) == 3
    assert components[3].props[0].name == 'implementation-point'
    assert components[3].props[0].value == 'external'
    assert components[3].props[1].name == 'leveraged-authorization-uuid'
    assert components[3].props[1].value == auth.uuid
    assert components[3].props[2].name == 'inherited-uuid'
    assert components[3].props[2].value == expected_application_uuid

    # Run twice and assert with no changes that the ssp is the same
    copy_ssp = copy.deepcopy(orig_ssp)
    ssp_inheritance_api.update_ssp_inheritance(orig_ssp)
    assert ModelUtils.models_are_equivalent(orig_ssp, copy_ssp)  # type: ignore


def test_no_leveraged_comps(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that a leveraged authorization is not created."""
    inheritance_path = tmp_trestle_dir.joinpath(leveraged_ssp, const.INHERITANCE_VIEW_DIR)
    application_dir = inheritance_path.joinpath('Application')
    unmapped_prep_dir(application_dir)

    test_utils.load_from_json(tmp_trestle_dir, 'leveraged_ssp', leveraged_ssp, ossp.SystemSecurityPlan)
    test_utils.load_from_json(tmp_trestle_dir, 'leveraging_ssp', leveraging_ssp, ossp.SystemSecurityPlan)

    orig_ssp, _ = ModelUtils.load_model_for_class(
        tmp_trestle_dir,
        leveraging_ssp,
        ossp.SystemSecurityPlan,
        FileContentType.JSON)

    components = orig_ssp.system_implementation.components

    assert len(components) == 5
    assert len(orig_ssp.system_implementation.leveraged_authorizations) == 1

    ssp_inheritance_api = SSPInheritanceAPI(inheritance_path, tmp_trestle_dir)
    ssp_inheritance_api.update_ssp_inheritance(orig_ssp)

    assert orig_ssp.system_implementation.leveraged_authorizations is None
