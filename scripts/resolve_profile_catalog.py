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
"""Script to generate resolved profile catalog given profile."""
import logging
import sys
from pathlib import Path

import trestle.oscal.profile as prof
from trestle.common.file_utils import FileContentType, is_valid_project_root
from trestle.common.model_utils import ModelUtils
from trestle.core.profile_resolver import ProfileResolver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def create_resolved_profile_catalog(profile_name: str, resolved_profile_catalog_name: str) -> int:
    """Create the catalog from the profile."""
    trestle_root = Path.cwd()
    if not is_valid_project_root(trestle_root):
        logger.info('This script must be run from the top level of a valid trestle project directory.')
        return 1
    profile_path = ModelUtils.full_path_for_top_level_model(trestle_root, profile_name, prof.Profile)
    profile_resolver = ProfileResolver()
    resolved_cat = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
    ModelUtils.save_top_level_model(resolved_cat, trestle_root, resolved_profile_catalog_name, FileContentType.JSON)
    logger.info(
        f'Successfully created resolved profile catalog {resolved_profile_catalog_name} from profile {profile_name}'
    )
    return 0


def _usage():
    logger.info(f'Usage: python {sys.argv[0]} profile_name resolved_profile_catalog_name')


def main():
    """
    Create the resolved profile catalog.

    Usage:
        python resolve_profile_catalog.py profile_name resolved_profile_catalog_name
    """
    if len(sys.argv) != 3:
        _usage()
        return 1
    return create_resolved_profile_catalog(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    sys.exit(main())
