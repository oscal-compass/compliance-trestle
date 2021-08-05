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
import re

import trestle.oscal.profile as profile
import trestle.utils.log as log
from trestle.core import const
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.utils import fs

logger = logging.getLogger(__name__)


class HrefCmd(CommandPlusDocs):
    """Change href of import in profile to point to catalog in trestle project."""

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

        if 'name' in args and args.name:
            profile_name: str = args.name
        else:
            logger.warning('No profile name specified for command href.')
            return 1

        if 'href' in args and args.href:
            new_href: str = args.href.strip("'")
            effective_cwd = pathlib.Path.cwd()
            return self.change_import_href(effective_cwd, profile_name, new_href)

        logger.warning('No href value profied for command href.')
        return 1

    @classmethod
    def change_import_href(cls, effective_cwd: pathlib.Path, profile_name: str, new_href: str) -> int:
        """Change the href of the import in the profile.

        Args:
            profile_name: Name of profile already imported into trestle
            href: New value for the href of the import, pointing to trestle://...

        Returns:
            0 on success, 1 on failure

        Assumptions and requirements:
            The profile must be a valid profile in the trestle project.
            The import must be a valid catalog in the trestle project.
            Assumes only one import by the profile.
            The original href is not checked and will be overwritten.

        Future work:
            Allow multiple imports with matching hrefs.
            Allow href to point to profile in trestle.
        """
        if re.match(const.TRESTLE_HREF_REGEX, new_href) is None:
            logger.warning(f'New href must be of form trestle://...  {new_href}')
            return 1
        trestle_root = fs.get_trestle_project_root(effective_cwd)
        if trestle_root is None:
            logger.warning(f'Effective directory is not in a trestle project: {effective_cwd}')
            return 1
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
