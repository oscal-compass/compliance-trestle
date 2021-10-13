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
"""Author commands to generate profile as markdown and assemble to json after edit."""

import argparse
import logging
import pathlib
import shutil
import traceback
from typing import List

import trestle.oscal.profile as prof
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.err import TrestleError
from trestle.core.profile_resolver import ProfileResolver
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


class ProfileGenerate(AuthorCommonCommand):
    """Generate profile in markdown form from a profile in the trestle workspace."""

    name = 'profile-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source profile model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated profile markdown folder'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = args.trestle_root
            if not fs.allowed_task_name(args.output):
                logger.warning(f'{args.output} is not an allowed directory name')
                return 1

            profile_path = trestle_root / f'profiles/{args.name}/profile.json'

            markdown_path = trestle_root / args.output

            return self.generate_markdown(trestle_root, profile_path, markdown_path)
        except Exception as e:
            logger.error(f'Generation of the profile markdown failed with error: {e}')
            logger.debug(traceback.format_exc())
            return 1

    def generate_markdown(
        self, trestle_root: pathlib.Path, profile_path: pathlib.Path, markdown_path: pathlib.Path
    ) -> int:
        """Generate markdown for the controls in the profile.

        Args:
            trestle_root: Root directory of the trestle workspace
            profile_path: Path of the profile json file
            markdown_path: Path to the directory into which the markdown will be written

        Returns:
            0 on success, 1 on error
        """
        _, _, profile = load_distributed(profile_path, trestle_root)
        catalog = ProfileResolver().get_resolved_profile_catalog(trestle_root, profile_path, True)
        catalog_interface = CatalogInterface(catalog)
        catalog_interface.write_catalog_as_markdown(markdown_path, {}, None, False, True, profile)
        return 0


class ProfileAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Profile json file."""

    name = 'profile-assemble'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the profile model in the trestle workspace that is being modified'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        file_help_str = 'Name of the source markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Profile (ok to overwrite original)'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            return self.assemble_profile(trestle_root, args.name, args.markdown, args.output)
        except Exception as e:
            logger.error(f'Assembly of markdown to profile failed with error: {e}')
            logger.debug(traceback.format_exc())
            return 1

    @staticmethod
    def _replace_alter_adds(profile: prof.Profile, alters: List[prof.Alter]) -> prof.Profile:
        """Replace the alter adds in the orig_profile with the new ones."""
        if not profile.modify:
            profile.modify = prof.Modify(alters=alters)
        elif not profile.modify.alters:
            profile.modify.alters = alters
        else:
            alter_dict = {}
            # if an alter has adds - remove them up front and build dict of alters by control id
            for alter in profile.modify.alters:
                alter.adds = None
                alter_dict[alter.control_id] = alter
            # now go through new alters and add them to each control in dict by control id
            for new_alter in alters:
                alter = alter_dict.get(new_alter.control_id, None)
                if alter is None:
                    alter_dict[new_alter.control_id] = alter
                else:
                    # even though we removed adds at start, we may have added one already
                    if alter.adds:
                        alter.adds.extend(new_alter.adds)
                    else:
                        alter.adds = new_alter.adds
                    # update the dict with the new alter with its added adds
                    alter_dict[new_alter.control_id] = alter
            # get the new list of alters from the dict and update profile
            new_alters = list(alter_dict.values())
            profile.modify.alters = new_alters
        return profile

    @staticmethod
    def assemble_profile(
        trestle_root: pathlib.Path, orig_profile_name: str, md_name: str, new_profile_name: str
    ) -> int:
        """
        Assemble the markdown directory into a json profile model file.

        Args:
            trestle_root: The trestle root directory
            orig_profile_name: The output name of the profile json file to be created from the assembly
            md_name: The name of the directory containing the markdown control files for the ssp
            new_profile_name: The name of the new json profile.  It can be the same as original to overwrite

        Returns:
            0 on success, 1 otherwise

        """
        md_dir = trestle_root / md_name
        profile_path = trestle_root / f'profiles/{orig_profile_name}/profile.json'
        _, _, orig_profile = load_distributed(profile_path, trestle_root, prof.Profile)
        # load the editable sections of the markdown and create Adds for them
        # then overwrite the Adds in the existing profile with the new ones
        found_alters = CatalogInterface.read_additional_content(md_dir)
        if found_alters:
            orig_profile = ProfileAssemble._replace_alter_adds(orig_profile, found_alters)

        new_prof_dir = trestle_root / f'profiles/{new_profile_name}'

        if new_prof_dir.exists():
            logger.info('Creating profile from markdown and destination profile directory exists, so deleting.')
            try:
                shutil.rmtree(str(new_prof_dir))
            except OSError as e:
                raise TrestleError(f'OSError deleting existing catalog directory with rmtree {new_prof_dir}: {e}')
        try:
            new_prof_dir.mkdir()
            orig_profile.oscal_write(new_prof_dir / 'profile.json')
        except OSError as e:
            raise TrestleError(f'OSError writing profile from markdown to {new_prof_dir}: {e}')
        return 0
