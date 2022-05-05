# -*- mode:python; coding:utf-8 -*-

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
"""Validate catalog by confirming control links match resources in backmatter."""
import logging

from trestle.common.common_types import TopLevelOscalModel
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.validator import Validator
from trestle.oscal.catalog import Catalog

logger = logging.getLogger(__name__)


class LinksValidator(Validator):
    """Validator to confirm all links in controls match resources in backmatter."""

    def model_is_valid(self, model: TopLevelOscalModel) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
        returns:
            True (valid) if it is not a catalog, or it is a catalog and its links are 1:1 with resources.
        """
        if not isinstance(model, Catalog):
            return True
        catalog: Catalog = model
        cat_interface = CatalogInterface(catalog)
        uuids = cat_interface.find_needed_uuid_refs()
        links = set()
        if catalog.back_matter and catalog.back_matter.resources:
            for res in catalog.back_matter.resources:
                links.add(res.uuid)
        if uuids == links:
            return True
        in_uuids = uuids.difference(links)
        if in_uuids:
            logger.warning(f'Prose references {len(uuids)} uuids and the following are not in resources: {in_uuids}')
        in_links = links.difference(uuids)
        if in_links:
            logger.warning(f'Resources have {len(links)} uuids and the following are not refd by prose: {in_links}')
        # This validator is intended just to give warnings, so it currently always returns True
        return True
