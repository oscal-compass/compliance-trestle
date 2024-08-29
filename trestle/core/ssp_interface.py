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
"""Helper methods for querying SSP values."""
import logging
from operator import attrgetter
from typing import Any, Iterator, List, Optional

from trestle.common.list_utils import as_list, get_default
from trestle.oscal.common import (Party, ResponsibleParty)
from trestle.oscal.ssp import Diagram, SystemSecurityPlan

logger = logging.getLogger(__name__)


class SSPInterface():
    """
    Class to query SSP values.

    Functions in this class are mainly used by jinja and not by the trestle code itself.
    """

    def __init__(self, ssp: SystemSecurityPlan) -> None:
        """Initialize the class."""
        self._ssp = ssp

    def safe_retrieval(self, obj: Optional[Any], method_chain: str, default: str = '') -> Any:
        """Retrieve the method chain or return the default value."""
        if obj:
            try:
                return get_default(attrgetter(method_chain)(obj), default)
            except AttributeError:
                logger.warning(f'object {obj} does not have attribute in {method_chain}')
                return default
        else:
            return default

    def first_array_entry(self,
                          array_or_none: Optional[List[Any]],
                          method_chain: Optional[str] = None) -> Optional[Any]:
        """Retrieve the first array entry, optionally safely retrieving an attribute chain."""
        array_entry = next(iter(as_list(array_or_none)), None)
        if method_chain:
            return self.safe_retrieval(array_entry, method_chain)
        return array_entry

    def get_diagram_href(self, diagram: Optional[Diagram]) -> str:
        """Retrieve the diagram's link href."""
        if diagram:
            return next((link.href for link in as_list(diagram.links) if link.rel == 'diagram'), '')
        else:
            return ''

    def get_party_by_uuid(self, uuid: str) -> Optional[Party]:
        """Get the metadata.parties entry for this UUID."""
        return next((x for x in as_list(self._ssp.metadata.parties) if x.uuid == uuid), None)

    def get_parties_for_role(self, responsible_parties: List[ResponsibleParty], role_id: str) -> Iterator[Party]:
        """Get a list of parties from a list of responsible_parties and a given role_id."""
        logger.debug(f'Finding parties for role: {role_id}')
        for responsible_party in as_list(responsible_parties):
            if responsible_party.role_id == role_id:
                logger.debug(
                    f'Found responsible party for role_id: {role_id} with {len(responsible_party.party_uuids)} parties'
                )
                for uuid in responsible_party.party_uuids:
                    logger.debug(f'Looking for parties with uuid: {uuid}')
                    party = self.get_party_by_uuid(uuid)
                    if party:
                        yield party
