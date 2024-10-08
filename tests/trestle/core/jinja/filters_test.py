# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2024 The OSCAL Compass Authors.
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
"""Tests for trestle custom jinja filters functionality."""

from typing import Any, List, Optional

import pytest

from trestle.core.jinja.filters import (diagram_href, first_or_none, get_party, parties_for_role)
from trestle.oscal.common import Link, Party, ResponsibleParty
from trestle.oscal.ssp import Diagram, SystemSecurityPlan


@pytest.mark.parametrize(
    'links,expected',
    [
        (
            [
                Link(rel='other', href='./path/to/local/thing'),
                Link(rel='diagram', href='https://host.name/path/to/diagram.png')
            ],
            'https://host.name/path/to/diagram.png'
        ), ([Link(rel='other', href='./path/to/local/file')], ''), ([], ''), (None, '')
    ]
)
def test_diagram_href(links: Optional[List[Link]], expected: str) -> None:
    """Test retrieving the link href for rel='diagram'."""
    diagram = Diagram(uuid='26c1c7df-fb67-45ba-b60f-35d8b5c1d1dc', links=links)
    assert diagram_href(diagram) == expected


@pytest.mark.parametrize('actual,expected', [[['ok'], 'ok'], ([], None), (None, None)])
def test_first_or_none(actual: Optional[List[Any]], expected: Optional[Any]) -> None:
    """Test behavior of retrieving the first element or None for empty or missing list."""
    assert first_or_none(actual) == expected


def test_get_party(sample_system_security_plan: SystemSecurityPlan, sample_party: Party) -> None:
    """Test behavior of retrieving a ssp.metadata.parties entry by UUID."""
    assert get_party(sample_party.uuid, ssp=sample_system_security_plan) == sample_party


def test_parties_for_role(sample_system_security_plan: SystemSecurityPlan, sample_party: Party) -> None:
    """Test behavior of retrieving all parties for a given role-id."""
    sample_system_security_plan.metadata.responsible_parties = [
        ResponsibleParty(role_id='pytest-tester', party_uuids=[sample_party.uuid])
    ]
    result = list(
        parties_for_role(
            sample_system_security_plan.metadata.responsible_parties,
            role_id='pytest-tester',
            ssp=sample_system_security_plan
        )
    )
    assert len(result) == 1
    assert result[0] == sample_party
