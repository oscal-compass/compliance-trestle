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
"""Trestle author docs sub-command."""
import argparse
import logging
import pathlib
import shutil

from pkg_resources import resource_filename

import trestle.core.commands.author.consts as author_const
import trestle.core.markdown_validator as markdown_validator
import trestle.utils.fs as fs
from trestle.core.commands.author.common import AuthorCommonCommand

logger = logging.getLogger(__name__)


class Docs(AuthorCommonCommand):
    """Markdown governed documents - enforcing consistent markdown across a set of files."""

    name = 'docs'

    template_name = 'template.md'

    def _init_arguments(self) -> None:
        self.add_argument(
            author_const.gh_short, author_const.gh_long, help=author_const.gh_help, default=None, type=str
        )
        self.add_argument(
            author_const.short_header_validate,
            author_const.long_header_validate,
            help=author_const.header_validate_help,
            action='store_true'
        )
        self.add_argument(
            author_const.hov_short, author_const.hov_long, help=author_const.hov_help, action='store_true'
        )
        self.add_argument(
            author_const.recurse_short, author_const.recurse_long, help=author_const.recurse_help, action='store_true'
        )
        self.add_argument(author_const.mode_arg_name, choices=author_const.mode_choices)
        tn_help_str = '\n'.join(
            [
                'The name of the the task to be governed.',
                ''
                'The template file is at .trestle/author/[task-name]/template.md',
                'Note that by default this will automatically enforce the task.'
            ]
        )

        self.add_argument(
            author_const.task_name_short, author_const.task_name_long, help=tn_help_str, required=True, type=str
        )
        self.add_argument(
            author_const.short_readme_validate,
            author_const.long_readme_validate,
            help=author_const.readme_validate_help,
            action='store_true'
        )

    def _run(self, args: argparse.Namespace) -> int:
        if self._initialize(args):
            return 1
        status = 1
        try:
            if args.mode == 'create-sample':
                status = self.create_sample()

            elif args.mode == 'template-validate':
                status = self.template_validate(
                    args.governed_heading,
                    args.header_validate,
                    args.header_only_validate,
                )
            elif args.mode == 'setup':
                status = self.setup_template_governed_docs()
            elif args.mode == 'validate':
                # mode is validate
                status = self.validate(
                    args.governed_heading,
                    args.header_validate,
                    args.header_only_validate,
                    args.recurse,
                    args.readme_validate
                )
        except Exception as e:
            logger.error(f'Error "{e}"" occurred when running trestle author docs.')
            logger.error('Exiting')
        return status

    def setup_template_governed_docs(self) -> int:
        """Create structure to allow markdown template enforcement.

        Returns:
            Unix return code.
        """
        if not self.task_path.exists():
            self.task_path.mkdir(exist_ok=True, parents=True)
        elif self.task_path.is_file():
            logger.error(f'Task path: {self.rel_dir(self.task_path)} is a file not a directory.')
            return 1
        if not self.template_dir.exists():
            self.template_dir.mkdir(exist_ok=True, parents=True)
        elif self.template_dir.is_file():
            logger.error(f'Template path: {self.rel_dir(self.template_dir)} is a file not a directory.')
            return 1
        logger.debug(self.template_dir)
        if not self._validate_template_dir():
            logger.error('Aborting setup')
            return 1
        template_file = self.template_dir / self.template_name
        if template_file.is_file():
            return 0
        reference_template = pathlib.Path(resource_filename('trestle.resources', 'template.md')).resolve()
        shutil.copy(reference_template, template_file)
        logger.info(f'Template file setup for task {self.task_name} at {self.rel_dir(template_file)}')
        logger.info(f'Task directory is {self.rel_dir(self.task_path)}')
        return 0

    def create_sample(self) -> int:
        """Presuming the template exists, copy into a sample markdown file with an index."""
        template_file = self.template_dir / self.template_name

        if not self._validate_template_dir():
            logger.error('Aborting setup')
            return 1
        if not template_file.is_file():
            logger.error('No template file ... exiting.')
            return 1

        index = 0
        while True:
            candidate_task = self.task_path / f'{self.task_name}_{index:03d}.md'
            if candidate_task.is_file():
                index = index + 1
            else:
                shutil.copy(str(template_file), str(candidate_task))
                break
        return 0

    def template_validate(self, heading: str, validate_header: bool, validate_only_header: bool) -> int:
        """Validate that the template is acceptable markdown."""
        template_file = self.template_dir / self.template_name
        if not self._validate_template_dir():
            logger.error('Aborting setup')
            return 1
        if not template_file.is_file():
            logger.error(f'Required template file: {self.rel_dir(template_file)} does not exist. Exiting.')
            return 1
        try:
            _ = markdown_validator.MarkdownValidator(template_file, validate_header, validate_only_header, heading)
        except Exception as ex:
            logger.error(f'Template for task {self.task_name} failed to validate due to {ex}')
            return 1
        logger.info(f'TEMPLATES VALID: {self.task_name}')
        return 0

    def _validate_template_dir(self) -> bool:
        """Template directory should only have template file."""
        for child in self.template_dir.iterdir():
            # Only allowable template file in the directory is the template directory.
            if child.name != self.template_name and child.name.lower() != 'readme.md':
                logger.error(f'Unknown file: {child.name} in template directory {self.rel_dir(self.template_dir)}')
                return False
        return True

    def _validate_dir(
        self,
        template_file: pathlib.Path,
        governed_heading: str,
        md_dir: pathlib.Path,
        validate_header: bool,
        validate_only_header: bool,
        recurse: bool,
        readme_validate: bool
    ) -> int:
        """Validate md files in a directory with option to recurse."""
        # status is a linux returncode
        status = 0
        for item_path in md_dir.iterdir():
            if fs.local_and_visible(item_path):
                if item_path.is_file():
                    if not item_path.suffix == '.md':
                        logger.info(
                            f'Unexpected file {self.rel_dir(item_path)} in folder {self.rel_dir(md_dir)}, skipping.'
                        )
                        continue
                    if not readme_validate:
                        if item_path.name.lower() == 'readme.md':
                            continue
                    md_validator = markdown_validator.MarkdownValidator(
                        template_file, validate_header, validate_only_header, governed_heading
                    )
                    if not md_validator.validate(item_path):
                        logger.info(f'INVALID: {self.rel_dir(item_path)}')
                        status = 1
                    else:
                        logger.info(f'VALID: {self.rel_dir(item_path)}')
                elif recurse:
                    if not self._validate_dir(template_file,
                                              governed_heading,
                                              item_path,
                                              validate_header,
                                              validate_only_header,
                                              recurse,
                                              readme_validate):
                        status = 1
        return status

    def validate(
        self,
        governed_heading: str,
        validate_header: bool,
        validate_only_header: bool,
        recurse: bool,
        readme_validate: bool
    ) -> int:
        """
        Validate task.

        Args:
            governed_heading: A heading for which structural enforcement (see online docs).
            validate_header: Whether or not to validate the key structure of the yaml header to the markdown document.
            validate_only_header: Whether to validate just the yaml header.
            recurse: Whether to allow validated files to be in a directory tree.
            readme_validate: Whether to validate readme files, otherwise they will be ignored.

        Returns:
            Return code to be used for the command.
        """
        if not self.task_path.is_dir():
            logger.error(f'Task directory {self.rel_dir(self.task_path)} does not exist. Exiting validate.')
        template_file = self.template_dir / self.template_name
        if not template_file.is_file():
            logger.error(f'Required template file: {self.rel_dir(template_file)} does not exist. Exiting.')
            return 1
        return self._validate_dir(
            template_file,
            governed_heading,
            self.task_path,
            validate_header,
            validate_only_header,
            recurse,
            readme_validate
        )
