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
"""Trestle author docs sub-command."""
import argparse
import logging
import pathlib
import re
import shutil
import traceback
from typing import Optional

import trestle.core.commands.author.consts as author_const
import trestle.utils.fs as fs
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.author.versioning.template_versioning import TemplateVersioning
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_api import MarkdownAPI

logger = logging.getLogger(__name__)


class Docs(AuthorCommonCommand):
    """Markdown governed documents - enforcing consistent markdown across a set of files."""

    name = 'docs'

    template_name = 'template.md'

    def _init_arguments(self) -> None:
        self.add_argument(
            author_const.GH_SHORT, author_const.GH_LONG, help=author_const.GH_HELP, default=None, type=str
        )
        self.add_argument(
            author_const.SHORT_HEADER_VALIDATE,
            author_const.LONG_HEADER_VALIDATE,
            help=author_const.HEADER_VALIDATE_HELP,
            action='store_true'
        )
        self.add_argument(
            author_const.SHORT_TEMPLATE_VERSION,
            author_const.LONG_TEMPLATE_VERSION,
            help=author_const.TEMPLATE_VERSION_HELP,
            action='store'
        )
        self.add_argument(
            author_const.HOV_SHORT, author_const.HOV_LONG, help=author_const.HOV_HELP, action='store_true'
        )
        self.add_argument(
            author_const.SHORT_IGNORE, author_const.LONG_IGNORE, help=author_const.IGNORE_HELP, default=None, type=str
        )
        self.add_argument(
            author_const.RECURSE_SHORT, author_const.RECURSE_LONG, help=author_const.RECURSE_HELP, action='store_true'
        )
        self.add_argument(author_const.MODE_ARG_NAME, choices=author_const.MODE_CHOICES)
        tn_help_str = '\n'.join(
            [
                'The name of the the task to be governed.',
                ''
                'The template file is at .trestle/author/[task-name]/template.md',
                'Note that by default this will automatically enforce the task.'
            ]
        )

        self.add_argument(
            author_const.TASK_NAME_SHORT, author_const.TASK_NAME_LONG, help=tn_help_str, required=True, type=str
        )
        self.add_argument(
            author_const.SHORT_README_VALIDATE,
            author_const.LONG_README_VALIDATE,
            help=author_const.README_VALIDATE_HELP,
            action='store_true'
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            status = 1
            if self._initialize(args):
                return status

            if args.mode == 'create-sample':
                status = self.create_sample()

            elif args.mode == 'template-validate':
                status = self.template_validate(
                    args.governed_heading,
                    args.header_validate,
                    args.header_only_validate,
                )
            elif args.mode == 'setup':
                status = self.setup_template_governed_docs(args.template_version)
            elif args.mode == 'validate':
                # mode is validate
                status = self.validate(
                    args.governed_heading,
                    args.header_validate,
                    args.header_only_validate,
                    args.recurse,
                    args.readme_validate,
                    args.template_version,
                    args.ignore
                )

            return status
        except TrestleError as e:
            logger.debug(traceback.format_exc())
            logger.error(f'Error occurred when running trestle author docs: {e}')
            logger.error('Exiting')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            logger.debug(traceback.format_exc())
            logger.error(f'Unexpected error occurred when running trestle author docs: {e}')
            logger.error('Exiting')
            return CmdReturnCodes.UNKNOWN_ERROR.value

    def setup_template_governed_docs(self, template_version: str) -> int:
        """Create structure to allow markdown template enforcement.

        Returns:
            Unix return code.
        """
        if not self.task_path.exists():
            self.task_path.mkdir(exist_ok=True, parents=True)
        elif self.task_path.is_file():
            logger.error(f'Task path: {self.rel_dir(self.task_path)} is a file not a directory.')
            return CmdReturnCodes.COMMAND_ERROR.value
        if not self.template_dir.exists():
            self.template_dir.mkdir(exist_ok=True, parents=True)
        elif self.template_dir.is_file():
            logger.error(f'Template path: {self.rel_dir(self.template_dir)} is a file not a directory.')
            return CmdReturnCodes.COMMAND_ERROR.value
        logger.debug(self.template_dir)
        if not self._validate_template_dir():
            logger.error('Aborting setup')
            return CmdReturnCodes.COMMAND_ERROR.value
        template_file = self.template_dir / self.template_name
        if template_file.is_file():
            return CmdReturnCodes.SUCCESS.value
        TemplateVersioning.write_versioned_template('template.md', self.template_dir, template_file, template_version)
        logger.info(f'Template file setup for task {self.task_name} at {self.rel_dir(template_file)}')
        logger.info(f'Task directory is {self.rel_dir(self.task_path)}')
        return CmdReturnCodes.SUCCESS.value

    def create_sample(self) -> int:
        """Presuming the template exists, copy into a sample markdown file with an index."""
        template_file = self.template_dir / self.template_name

        if not self._validate_template_dir():
            logger.error('Aborting setup')
            return CmdReturnCodes.COMMAND_ERROR.value
        if not template_file.is_file():
            logger.error('No template file ... exiting.')
            return CmdReturnCodes.COMMAND_ERROR.value

        index = 0
        while True:
            candidate_task = self.task_path / f'{self.task_name}_{index:03d}.md'
            if candidate_task.is_file():
                index = index + 1
            else:
                shutil.copy(str(template_file), str(candidate_task))
                break
        return CmdReturnCodes.SUCCESS.value

    def template_validate(self, heading: str, validate_header: bool, validate_only_header: bool) -> int:
        """Validate that the template is acceptable markdown."""
        template_file = self.template_dir / self.template_name
        if not self._validate_template_dir():
            logger.error('Aborting setup')
            return CmdReturnCodes.COMMAND_ERROR.value
        if not template_file.is_file():
            logger.error(f'Required template file: {self.rel_dir(template_file)} does not exist. Exiting.')
            return CmdReturnCodes.COMMAND_ERROR.value
        try:
            md_api = MarkdownAPI()
            md_api.load_validator_with_template(template_file, validate_header, validate_only_header, heading)
        except Exception as ex:
            logger.error(f'Template for task {self.task_name} failed to validate due to {ex}')
            return CmdReturnCodes.COMMAND_ERROR.value
        logger.info(f'TEMPLATES VALID: {self.task_name}')
        return CmdReturnCodes.SUCCESS.value

    def _validate_template_dir(self) -> bool:
        """Template directory should only have template file."""
        for child in fs.iterdir_without_hidden_files(self.template_dir):
            # Only allowable template file in the directory is the template directory.
            if child.name != self.template_name and child.name.lower() != 'readme.md':
                logger.error(f'Unknown file: {child.name} in template directory {self.rel_dir(self.template_dir)}')
                return False
        return True

    def _validate_dir(
        self,
        governed_heading: str,
        md_dir: pathlib.Path,
        validate_header: bool,
        validate_only_header: bool,
        recurse: bool,
        readme_validate: bool,
        template_version: Optional[str] = None,
        ignore: Optional[str] = None
    ) -> int:
        """
        Validate md files in a directory with option to recurse.

        Template version will be fetched from the instance header.
        """
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
                    if not readme_validate and item_path.name.lower() == 'readme.md':
                        continue

                    if ignore:
                        p = re.compile(ignore)
                        matched = p.match(item_path.parts[-1])
                        if matched is not None:
                            logger.info(f'Ignoring file {item_path} from validation.')
                            continue

                    md_api = MarkdownAPI()
                    if template_version != '':
                        template_file = self.template_dir / self.template_name
                    else:
                        instance_version = md_api.processor.fetch_value_from_header(
                            item_path, author_const.TEMPLATE_VERSION_HEADER
                        )
                        if instance_version is None:
                            instance_version = '0.0.1'
                        versione_template_dir = TemplateVersioning.get_versioned_template_dir(
                            self.template_dir, instance_version
                        )
                        template_file = versione_template_dir / self.template_name
                    if not template_file.is_file():
                        logger.error(f'Required template file: {self.rel_dir(template_file)} does not exist. Exiting.')
                        return CmdReturnCodes.COMMAND_ERROR.value
                    md_api.load_validator_with_template(
                        template_file, validate_header, not validate_only_header, governed_heading
                    )
                    if not md_api.validate_instance(item_path):
                        logger.info(f'INVALID: {self.rel_dir(item_path)}')
                        status = 1
                    else:
                        logger.info(f'VALID: {self.rel_dir(item_path)}')
                elif recurse:
                    if ignore:
                        p = re.compile(ignore)
                        if len(list(filter(p.match, str(item_path.relative_to(md_dir)).split('/')))) > 0:
                            logger.info(f'Ignoring directory {item_path} from validation.')
                            continue
                    rc = self._validate_dir(
                        governed_heading,
                        item_path,
                        validate_header,
                        validate_only_header,
                        recurse,
                        readme_validate,
                        template_version,
                        ignore
                    )
                    if rc != 0:
                        status = rc

        return status

    def validate(
        self,
        governed_heading: str,
        validate_header: bool,
        validate_only_header: bool,
        recurse: bool,
        readme_validate: bool,
        template_version: str,
        ignore: str
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
            return CmdReturnCodes.COMMAND_ERROR.value
        return self._validate_dir(
            governed_heading,
            self.task_path,
            validate_header,
            validate_only_header,
            recurse,
            readme_validate,
            template_version,
            ignore
        )
