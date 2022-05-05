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
import re
from typing import List

import trestle.common.const as const
import trestle.oscal.common as com
from trestle.common.common_types import TopLevelOscalModel
from trestle.common.model_utils import ModelUtils
from trestle.core.validator import Validator

logger = logging.getLogger(__name__)


class LinksValidator(Validator):
    """Validator to confirm all uuids in links and prose match resources in backmatter."""

    def model_is_valid(self, model: TopLevelOscalModel) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
        returns:
            Always returns True, but gives warning if links and resources are not one-to-one.
        """
        # links have href of form #foo or #uuid
        links_list: List[List[com.Link]] = ModelUtils.find_values_by_name(model, 'links')
        uuid_strs = [link.href for links in links_list for link in links]

        # prose has uuid refs in markdown form: [foo](#bar) or [foo](#uuid)
        prose_list = ModelUtils.find_values_by_name(model, 'prose')
        uuid_strs.extend(
            [
                match[1] for prose in prose_list for matches in re.findall(const.MARKDOWN_URL_REGEX, prose)
                for match in matches
            ]
        )

        # collect the strings that start with # and are potential uuids
        uuid_strs = [uuid_str for uuid_str in uuid_strs if uuid_str and uuid_str[0] == '#']

        # go through all matches and build set of those that are uuids
        refs = {uuid_match[0] for uuid_str in uuid_strs for uuid_match in re.findall(const.UUID_REGEX, uuid_str[1:])}

        # find uuids in backmatter
        # should check for duplicates
        links = set()
        if model.back_matter and model.back_matter.resources:
            links.update([res.uuid for res in model.back_matter.resources])

        in_refs = refs.difference(links)
        if in_refs:
            logger.warning(f'Model references {len(refs)} uuids and {len(in_refs)} of them are not in resources.')
            logger.debug(f'Model references {len(in_refs)} uuids not in resources: {in_refs}')

        in_links = links.difference(refs)
        if in_links:
            logger.warning(f'Resources have {len(links)} uuids and {len(in_links)} are not referenced by model.')
            logger.debug(f'Resources have {len(in_links)} not in referenced by model: {in_links}')

        # This validator is intended just to give warnings, so it always returns True
        return True
