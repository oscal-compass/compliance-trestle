# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Author commands to generate profile as markdown and assemble to json after edit."""

import argparse
import logging
import pathlib
import shutil

import trestle.oscal.common as com
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
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root
        if not fs.allowed_task_name(args.output):
            logger.warning(f'{args.output} is not an allowed directory name')
            return 1

        profile_path = trestle_root / f'profiles/{args.name}/profile.json'

        markdown_path = trestle_root / args.output

        return self.generate_markdown(trestle_root, profile_path, markdown_path)

    def generate_markdown(
        self, trestle_root: pathlib.Path, profile_path: pathlib.Path, markdown_path: pathlib.Path
    ) -> int:
        """Generate markdown for the controls in the profile."""
        _, _, profile = load_distributed(profile_path, trestle_root)
        catalog = ProfileResolver().get_resolved_profile_catalog(trestle_root, profile_path)
        catalog_interface = CatalogInterface(catalog)
        catalog_interface.write_catalog_as_markdown(markdown_path, {}, None, False, True)
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
        log.set_log_level_from_args(args)
        trestle_root = pathlib.Path(args.trestle_root)
        self.assemble_profile(trestle_root, args.name, args.markdown, args.output)
        return 0

    @staticmethod
    def _insert_part(my_part: com.Part, profile: prof.Profile) -> None:
        """Insert the part as an add in the profile for the specified control."""
        # FIXME this can be simplified
        control_id = my_part.id.split('_')[0]
        by_id = f'{control_id}_smt'
        my_add = prof.Add(position='after', by_id=by_id, parts=[my_part])
        my_alter = prof.Alter(control_id=control_id, adds=[my_add])
        if not profile.modify:
            profile.modify = prof.Modify(alters=[my_alter])
        elif not profile.modify.alters:
            profile.modify.alters = [my_alter]
        else:
            added = False
            new_alters = []
            for alter in profile.modify.alters:
                if alter.adds:
                    new_adds = []
                    for add in alter.adds:
                        if add.by_id == by_id:
                            added = True
                            if add.parts:
                                add.parts.append(my_part)
                            else:
                                add.parts = [my_part]
                        new_adds.append(add)
                    if not added:
                        added = True
                        new_adds.append(my_add)
                    alter.adds = new_adds
                new_alters.append(alter)
            profile.modify.alters = new_alters
            if not added:
                profile.modify.alters.append(my_alter)

    @staticmethod
    def assemble_profile(
        trestle_root: pathlib.Path, orig_profile_name: str, md_name: str, new_profile_name: str
    ) -> int:
        """
        Assemble the markdown directory into a json profile model file.

        Args:
            trestle_root: The trestle root directory
            md_name: The name of the directory containing the markdown control files for the ssp
            profile_name: The output name of the profile json file to be created from the assembly

        Returns:
            0 on success, 1 otherwise

        """
        md_dir = trestle_root / md_name
        profile_path = trestle_root / f'profiles/{orig_profile_name}/profile.json'
        _, _, orig_profile = load_distributed(profile_path, trestle_root, prof.Profile)
        added_parts = CatalogInterface.read_additional_content(md_dir)
        for part in added_parts:
            ProfileAssemble._insert_part(part, orig_profile)
        new_prof_dir = trestle_root / f'profiles/{new_profile_name}'

        if new_prof_dir.exists():
            logger.info('Creating profile from markdown and destination profile directory exists, so deleting.')
            try:
                shutil.rmtree(str(new_prof_dir))
            except Exception as e:
                raise TrestleError(f'Error deleting existing catalog directory {new_prof_dir}: {e}')
        try:
            new_prof_dir.mkdir()
            orig_profile.oscal_write(new_prof_dir / 'profile.json')
        except Exception as e:
            raise TrestleError(f'Error writing profile from markdown to {new_prof_dir}: {e}')
        return 0
