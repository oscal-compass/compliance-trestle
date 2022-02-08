# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Create resolved catalog from profile."""

import logging
import pathlib

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.core.control_io import ParameterRep
from trestle.core.resolver._import import Import

logger = logging.getLogger(__name__)


class ProfileResolver():
    """Class to resolve a catalog given a profile."""

    @staticmethod
    def get_resolved_profile_catalog(
        trestle_root: pathlib.Path,
        profile_path: pathlib.Path,
        block_adds: bool = False,
        params_format: str = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) -> cat.Catalog:
        """Create the resolved profile catalog given a profile path."""
        logger.debug(f'get resolved profile catalog for {profile_path} via generated Import.')
        import_ = prof.Import(href=str(profile_path), include_all={})
        import_filter = Import(trestle_root, import_, True, block_adds, params_format, param_rep)
        logger.debug('launch pipeline')
        result = next(import_filter.process())
        return result
