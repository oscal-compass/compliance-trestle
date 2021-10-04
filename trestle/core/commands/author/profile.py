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

import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.profile_interface import ProfileInterface
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


class ProfileGenerate(AuthorCommonCommand):
    """Generate profile in markdown form from a profile in the trestle workspace."""

    name = 'profile-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the profile model in the trestle workspace'
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
        profile_interface = ProfileInterface(profile)
        profile_interface.write_profile_as_markdown(markdown_path, {}, None, False, False)
        return 0


class ProfileAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Profile json file."""

    name = 'profile-assemble'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Profile'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = pathlib.Path(args.trestle_root)
        self.assemble_profile(trestle_root, args.markdown, args.output)
        return 0

    def assemble_profile(self, trestle_root: pathlib.Path, md_name: str, profile_name: str) -> int:
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
        profile_interface = ProfileInterface()
        profile = profile_interface.read_profile_from_markdown(md_dir)
        new_cat_dir = trestle_root / f'profiles/{profile_name}'
        new_cat_dir.mkdir()
        profile.oscal_write(new_cat_dir / 'profile.json')
        return 0
