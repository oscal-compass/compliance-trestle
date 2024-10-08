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
"""Trestle utilities to customize jinja filters."""
import logging
from typing import Any, Iterator, List, Optional

from jinja2.environment import Environment

from trestle.common.list_utils import as_list, get_default
from trestle.core.jinja.base import TrestleJinjaExtension
from trestle.oscal.common import Party, ResponsibleParty
from trestle.oscal.ssp import Diagram, SystemSecurityPlan

logger = logging.getLogger(__name__)


def first_or_none(value: Optional[List[Any]]) -> Optional[Any]:
    """Retrieve the first array entry, or None for lists that are None or empty."""
    return next(iter(as_list(value)), None)


def get_party(uuid: str, ssp: SystemSecurityPlan) -> Optional[Party]:
    """Get the metadata.parties entry for this UUID."""
    return next((x for x in as_list(ssp.metadata.parties) if x.uuid == uuid), None)


def parties_for_role(responsible_parties: List[ResponsibleParty], role_id: str,
                     ssp: SystemSecurityPlan) -> Iterator[Party]:
    """Get a list of parties from a list of responsible_parties and a given role_id."""
    logger.debug(f'Finding parties for role: {role_id}')
    for responsible_party in as_list(responsible_parties):
        if responsible_party.role_id == role_id:
            logger.debug(
                f'Found responsible party for role_id: {role_id} with {len(responsible_party.party_uuids)} parties'
            )
            for uuid in responsible_party.party_uuids:
                logger.debug(f'Looking for parties with uuid: {uuid}')
                party = get_party(uuid, ssp)
                if party:
                    yield party


def diagram_href(diagram: Optional[Diagram]) -> str:
    """Retrieve the diagrams's link href."""
    if diagram:
        return next((link.href for link in as_list(diagram.links) if link.rel == 'diagram'), '')
    else:
        return ''


class JinjaSSPFilters(TrestleJinjaExtension):
    """Collection of useful OSCAL-specific filters."""

    def __init__(self, environment: Environment) -> None:
        """Initialize class and add filters."""
        super(JinjaSSPFilters, self).__init__(environment)

        environment.filters['as_list'] = as_list
        environment.filters['get_default'] = get_default
        environment.filters['first_or_none'] = first_or_none
        environment.filters['get_party'] = get_party
        environment.filters['parties_for_role'] = parties_for_role
        environment.filters['diagram_href'] = diagram_href
