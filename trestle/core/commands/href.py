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
"""Trestle Href Command."""

import argparse
import logging
import pathlib
import traceback

import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError
from trestle.oscal.profile import Profile
from trestle.utils import fs

logger = logging.getLogger(__name__)


class HrefCmd(CommandPlusDocs):
    """Change href of import in profile to point to catalog in trestle project.

    This command is needed when generating an SSP with a profile that imports a catalog from a temporary
    location different from the final intended location of the catalog.  Omit the href argument to see
    the list of current imports in the profile.
    """

    name = 'href'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument(
            '-n', '--name', help='Name of trestle profile to modify (just its name).', type=str, required=True
        )

        self.add_argument(
            '-hr',
            '--href',
            help='New href of form trestle://catalogs/mycat/catalog.json.',
            type=str,
            required=False,
            default=''
        )

        self.add_argument(
            '-i',
            '--item',
            help='Item number of href to modify.  Get list by running href with just -n <prof_name> to list values.',
            type=int,
            required=False,
            default=0
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            logger.debug('Entering trestle href.')

            log.set_log_level_from_args(args)

            profile_name: str = args.name

            new_href: str = args.href.strip("'")

            item_num = args.item

            return self.change_import_href(args.trestle_root, profile_name, new_href, item_num)
        except TrestleError as e:
            logger.debug(traceback.format_exc())
            logger.error(f'Error while changing href or import in profile: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            logger.debug(traceback.format_exc())
            logger.error(f'Unexpected error while changing href or import in profile: {e}')
            return CmdReturnCodes.UNKNOWN_ERROR.value

    @classmethod
    def change_import_href(cls, trestle_root: pathlib.Path, profile_name: str, new_href: str, import_num: int) -> int:
        """Change the href of the import in the profile to point to a catalog in a specific location.

        A Profile has an Imports list containing at least one href of a catalog or profile to be imported.
        If the item being referenced is currently in the same trestle project as the main profile, the original
        href is likely different from the one needed to access the item from the profile.  Therefore,
        in order for trestle to find the item directly from the profile, the href must be modified in a way that
        trestle can load it.

        If the item is already at the link referred to by the href as a valid URI or absolute file path then no
        change is needed.  But if the item is being worked on in the same trestle directory as the profile,
        the href should be modified to something like trestle://catalogs/my_catalog/catalog.json

        This change only needs to be made once to the profile while the profile is being used to generate SSP's
        from the local item, but if the final profile is released the href would need to be changed to the
        intended final location of the referenced item.

        Args:
            trestle_root: trestle_root for this call
            profile_name: Name of profile already imported into trestle containing href's to be changed
            new_href: New value for the href of the import.  If blank just list the hrefs
            import_num: Item number of the href to change.


        Returns:
            0 on success, 1 on failure

        Assumptions and requirements:
            The profile must be a valid profile in the trestle project.
            The import must either be a valid uri, including local file, or trestle://
            The original href is not checked and will be overwritten.
            If href is the empty string, just list all hrefs.

        Future work:
            Allow multiple imports with matching hrefs.
            Allow href to point to profile in trestle rather than catalog, and by name.
            Allow full chaining of linked catalogs and profiles.

        """
        profile_data, profile_path = fs.load_top_level_model(trestle_root, profile_name, Profile)
        n_imports = len(profile_data.imports)
        if not new_href:
            logger.info(f'List of imports for profile {profile_name}:')
            for ii, import_ in enumerate(profile_data.imports):
                logger.info(f'{ii:2}: {import_.href}')
            return CmdReturnCodes.SUCCESS.value
        if n_imports <= import_num:
            logger.warning(f'Import number {import_num} is too large.  This profile has only {n_imports} imports.')
            return CmdReturnCodes.COMMAND_ERROR.value
        logger.info(f'Changing import {import_num} in profile {profile_name} from, to:')
        logger.info(f'{profile_data.imports[import_num].href}')
        logger.info(f'{new_href}')
        profile_data.imports[import_num].href = new_href
        profile_data.oscal_write(profile_path)
        return CmdReturnCodes.SUCCESS.value
