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
"""Trestle md governed-docs sub-command."""
import argparse
import logging
import pathlib
import shutil

import trestle.core.const as const
import trestle.core.markdown_validator as markdown_validator
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class GovernedDocs(CommandPlusDocs):
    """Markdown governed documents - enforcing consistent markdown across a set of files."""

    name = 'governed-docs'

    template_name = 'template.md'

    def _init_arguments(self) -> None:
        help_str = """The name of the the task to be governed.

The template file is at .trestle/md/[task-name]/template.md
Note that by default this will automatically enforce the task."""
        self.add_argument('-tn', '--task-name', help=help_str, required=True, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.error(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1
        if not fs.allowed_task_name(args.task_name):
            logger.error(
                f'Task name {args.task_name} is invalid as it interferes with OSCAL and trestle reserved names.'
            )
            return 1
        status = 1
        try:
            if args.mode == 'create-sample':
                status = self.create_sample(args.task_name, trestle_root)

            elif args.mode == 'template-validate':
                status = self.template_validate(
                    args.task_name,
                    trestle_root,
                    args.governed_heading,
                    args.header_validate,
                    args.header_only_validate,
                )
            elif args.mode == 'setup':
                status = self.setup_template_governed_docs(args.task_name, trestle_root)
            elif args.mode == 'validate':
                # mode is validate
                status = self.validate(
                    args.task_name,
                    trestle_root,
                    args.governed_heading,
                    args.header_validate,
                    args.header_only_validate,
                    args.recurse
                )
        except Exception as e:
            logger.error(f'Error "{e}"" occurred when running trestle md governed docs.')
            logger.error('Exiting')
        return status

    def setup_template_governed_docs(self, task_name: str, trestle_root: pathlib.Path) -> int:
        """Create structure to allow markdown template enforcement.

        Args:
            task_name: Task name of md task
            trestle_root: root path for trestle project

        Returns:
            Unix return code.
        """
        task_path = trestle_root / task_name
        task_path.mkdir(exist_ok=True, parents=True)

        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_dir.mkdir(exist_ok=True, parents=True)
        logger.debug(template_dir)
        if not self._validate_template_dir(template_dir):
            logger.error('Aborting setup')
            return 1
        template_file = template_dir / self.template_name
        if template_file.is_file():
            return 0
        fh = template_file.open('w')
        fh.write("""# Template header\nThis file is a pro-forma template.\n""")
        logger.warning(f'Template file setup for task {task_name} at {template_file}')
        logger.warning(f'Task directory is {task_path} ')
        return 0

    def create_sample(self, task_name: str, trestle_root: pathlib.Path) -> int:
        """Presuming the template exists, copy into a sample markdown file with an index."""
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_file = template_dir / self.template_name

        if not self._validate_template_dir(template_dir):
            logger.error('Aborting setup')
            return 1
        if not template_file.is_file():
            logger.error('No template file ... exiting.')
            return 1

        index = 0
        while True:
            candidate_task = trestle_root / task_name / f'{task_name}_{index:03d}.md'
            if candidate_task.is_file():
                index = index + 1
            else:
                shutil.copy(str(template_file), str(candidate_task))
                break
        return 0

    def template_validate(
        self,
        task_name: str,
        trestle_root: pathlib.Path,
        heading: str,
        validate_header: bool,
        validate_only_header: bool
    ) -> int:
        """Validate that the template is acceptable markdown."""
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_file = template_dir / self.template_name
        if not self._validate_template_dir(template_dir):
            logger.error('Aborting setup')
            return 1
        if not template_file.is_file():
            logger.error(f'Required template file: {template_file} does not exist. Exiting.')
            return 1
        try:
            _ = markdown_validator.MarkdownValidator(template_file, validate_header, validate_only_header, heading)
        except Exception as ex:
            logger.error(f'Template for task {task_name} failed to validate due to {ex}')
            return 1
        logger.info(f'TEMPLATES VALID: {task_name}')
        return 0

    def _validate_template_dir(self, template_dir: pathlib.Path) -> bool:
        """Template directory should only have template file."""
        for child in template_dir.iterdir():
            # Only allowable template file in the directory is the template file.
            if child.name != self.template_name:
                logger.error(f'Unknown file: {child.name} in template directory {template_dir}')
                return False
        return True

    def _validate_dir(
        self,
        template_file: pathlib.Path,
        governed_heading: str,
        md_dir: pathlib.Path,
        validate_header: bool,
        validate_only_header: bool,
        recurse: bool
    ) -> int:
        """Validate md files in a directory with option to recurse."""
        status = 0
        for item_path in md_dir.iterdir():
            if fs.local_and_visible(item_path):
                if item_path.is_file():
                    if not item_path.suffix == '.md':
                        logger.warning(f'Unexpected file {item_path} in folder {md_dir}, skipping.')
                        continue
                    md_validator = markdown_validator.MarkdownValidator(
                        template_file, validate_header, validate_only_header, governed_heading
                    )
                    if not md_validator.validate(item_path):
                        logger.info(f'INVALID: {item_path}')
                        status = 1
                    else:
                        logger.info(f'VALID: {item_path}')
                elif recurse:
                    if not self._validate_dir(
                            template_file, governed_heading, md_dir, validate_header, validate_only_header, recurse):
                        status = 1
        return status

    def validate(
        self,
        task_name: str,
        trestle_root: pathlib.Path,
        governed_heading: str,
        validate_header: bool,
        validate_only_header: bool,
        recurse: bool
    ) -> int:
        """Validate task."""
        task_path = trestle_root / task_name
        if not task_path.is_dir():
            logger.error(f'Task directory {task_path} does not exist. Exiting validate.')
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_file = template_dir / self.template_name
        if not template_file.is_file():
            logger.error(f'Required template file: {template_file} does not exist. Exiting.')
            return 1
        return self._validate_dir(
            template_file, governed_heading, task_path, validate_header, validate_only_header, recurse
        )
