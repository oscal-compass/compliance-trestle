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
import pathlib
from typing import List, Optional, Set

from trestle.common.common_types import TopLevelOscalModel
from trestle.common.model_utils import ModelUtils
from trestle.core.validator import Validator

logger = logging.getLogger(__name__)


class LinksValidator(Validator):
    """Validator to confirm all uuids in links and prose match resources in backmatter."""

    def model_is_valid(
        self, model: TopLevelOscalModel, quiet: bool, trestle_root: Optional[pathlib.Path] = None
    ) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
            quiet: Don't report msgs unless invalid.

        returns:
            Always returns True, but gives warning if links and resources are not one-to-one.
        """
        refs = ModelUtils.find_uuid_refs(model)

        # find uuids in backmatter
        links: List[str] = []
        if model.back_matter and model.back_matter.resources:
            links = [res.uuid for res in model.back_matter.resources]
            seen: Set[str] = set()
            dupes = [uuid for uuid in links if uuid in seen or seen.add(uuid)]
            if dupes:
                if not quiet:
                    logger.warning(f'Backmatter has  {len(dupes)} duplicate link uuids.')
                logger.debug(f'Backmatter has {len(dupes)} duplicate link uuids: {dupes}')

        links = set(links)
        in_refs = refs.difference(links)
        if in_refs:
            if not quiet:
                logger.warning(f'Model references {len(refs)} uuids and {len(in_refs)} of them are not in resources.')
            logger.debug(f'Model references {len(in_refs)} uuids not in resources: {in_refs}')

        in_links = links.difference(refs)
        if in_links:
            if not quiet:
                logger.warning(f'Resources have {len(links)} uuids and {len(in_links)} are not referenced by model.')
            logger.debug(f'Resources have {len(in_links)} uuids not referenced by model: {in_links}')

        # This validator is intended just to give warnings, so it always returns True
        return True
