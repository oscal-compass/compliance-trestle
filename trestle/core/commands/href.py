# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Trestle Href Command."""

import argparse
import logging
import pathlib

import trestle.oscal.profile as profile
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.utils import fs

logger = logging.getLogger(__name__)


class HrefCmd(CommandPlusDocs):
    """Change href of import in profile to point to catalog in trestle project.

    This command is needed when generating an SSP with a profile that imports a catalog from a temporary
    location different from the final intended location of the catalog.

    A Profile has an Imports list containing at least one href of a catalog of controls to be imported.
    If the catalog being referenced is currently in the same trestle project as the profile, the original
    href is likely different from the one needed to access the catalog from the profile.  Therefore,
    in order for trestle to find the catalog directly from the profile, the href must be modified in a way that
    trestle can load it.

    If the catalog is already at the link referred to by the href as a valid URI or absolute file path then no
    change is needed.  But if the catalog is being worked on in the same trestle directory as the profile,
    the href should be modified to something like trestle://catalogs/my_catalog/catalog.json

    This change only needs to be made once to the profile while the profile is being used to generate SSP's
    from the local catalog, but if the final profile is released the href would need to be changed to the
    intended final location of the catalog.

    Assumptions and requirements:
        The profile must be a valid profile in the trestle project.
        The import must either be a valid uri, including local file, or trestle://
        Assumes only one import by the profile.
        The original href is not checked and will be overwritten.

    Future work:
        Allow multiple imports with matching hrefs.
        Allow href to point to profile in trestle rather than catalog, and by name.
        Allow full chaining of linked catalogs and profiles.
    """

    name = 'href'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument(
            '-n', '--name', help='Name of trestle profile to modify (just its name).', type=str, required=True
        )

        self.add_argument(
            '-hr', '--href', help='New href of form trestle://catalogs/mycat/catalog.json.', type=str, required=True
        )

    def _run(self, args: argparse.Namespace) -> int:
        logger.debug('Entering trestle href.')

        log.set_log_level_from_args(args)

        profile_name: str = args.name

        new_href: str = args.href.strip("'")
        return self.change_import_href(args.trestle_root, profile_name, new_href)

    @classmethod
    def change_import_href(cls, trestle_root: pathlib.Path, profile_name: str, new_href: str) -> int:
        """Change the href of the import in the profile to point to a catalog in a specific location.

        Args:
            trestle_root: trestle_root for this call
            profile_name: Name of profile already imported into trestle
            new_href: New value for the href of the import

        Returns:
            0 on success, 1 on failure

        Assumptions and requirements:
            The profile must be a valid profile in the trestle project.
            The import must either be a valid uri, including local file, or trestle://
            Assumes only one import by the profile.
            The original href is not checked and will be overwritten.

        Future work:
            Allow multiple imports with matching hrefs.
            Allow href to point to profile in trestle rather than catalog, and by name.
            Allow full chaining of linked catalogs and profiles.

        """
        profile_dir = trestle_root / f'profiles/{profile_name}'
        content_type = fs.get_contextual_file_type(profile_dir)
        profile_path = (profile_dir / 'profile').with_suffix(fs.FileContentType.to_file_extension(content_type))
        profile_data: profile.Profile = profile.Profile.oscal_read(profile_path)
        n_imports = len(profile_data.imports)
        if n_imports != 1:
            logger.warning(f'There must be exactly one import to change the href.  This profile has {n_imports}.')
            return 1
        profile_data.imports[0].href = new_href
        profile_data.oscal_write(profile_path)
        return 0
