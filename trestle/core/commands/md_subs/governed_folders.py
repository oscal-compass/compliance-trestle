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
from typing import List

import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core import const
from trestle.core import markdown_validator
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class GovernedFolders(CommandPlusDocs):
    """Markdown governed folders - enforcing consistent files and templates across directories."""

    name = 'governed-folders'

    def _init_arguments(self) -> None:
        help_str = """The name of the the task to be governed.

The template files are at .trestle/md/[task-name], where the directory tree established and the markdown files within
that directory tree are enforced."""
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
                    args.task_name, trestle_root, args.governed_heading, args.header_validate
                )
            elif args.mode == 'setup':
                status = self.setup_template(args.task_name, trestle_root)
            elif args.mode == 'validate':
                # mode is validate
                status = self.validate(args.task_name, trestle_root, args.governed_heading, args.header_validate)
        except Exception as e:
            logger.error(f'Exception "{e}" running trestle md governed folders.')
        return status

    @classmethod
    def setup_template(cls, task_name: str, trestle_root: pathlib.Path, project_override: bool = False) -> int:
        """Create structure to allow markdown template enforcement."""
        if project_override:
            assert task_name == '.trestle'
        task_path = trestle_root / task_name
        task_path.mkdir(exist_ok=True, parents=True)
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_dir.mkdir(exist_ok=True, parents=True)
        template_file_a = template_dir / 'a_template.md'
        template_file_b = template_dir / 'another_template.md'
        template_content = """---\nyaml:header\n---\n# Template header\nThis file is a pro-forma template.\n"""
        if not template_file_a.is_file():
            fh = template_file_a.open('w')
            fh.write(template_content)
        if not template_file_b.is_file():
            fh = template_file_b.open('w')
            fh.write(template_content)

        logger.info(f'Template file setup for task {task_name} at {template_file_a} and {template_file_b}')
        logger.info(f'Task directory is {task_path} ')
        return 0

    @classmethod
    def template_validate(cls, task_name: str, trestle_root: pathlib.Path, heading: str, validate_header: bool) -> int:
        """Validate that the template is acceptable markdown."""
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        if not template_dir.is_dir():
            logger.error(f'Template directory {template_dir} for task {task_name} does not exist.')
            return 1
        # get list of files:
        template_files = template_dir.rglob('*')

        for template_file in template_files:
            if template_file.stem[0] == '.':
                # TODO: windows equivalent
                # Ignore '.' files
                continue
            elif template_file.is_dir():
                continue
            elif template_file.suffix.lower() == '.md':
                try:
                    _ = markdown_validator.MarkdownValidator(template_file, validate_header, heading)
                except Exception as ex:
                    logger.error(f'Template file {template_file} for task {task_name} failed to validate due to {ex}')
                    return 1
            else:
                logger.info(f'File: {template_file} within the template directory was ignored as it is not markdown.')
        return 0

    @classmethod
    def _measure_template_folder(
        cls, template_dir: pathlib.Path, instance_dir: pathlib.Path, governed_heading: str, validate_header: bool
    ) -> bool:

        r_instance_files: List[pathlib.Path] = []
        for instance_file in instance_dir.rglob('*'):
            if not fs.is_hidden(instance_file):
                r_instance_files.append(instance_file.relative_to(instance_dir))

        for template_file in template_dir.rglob('*'):
            r_template_path = template_file.relative_to(template_dir)
            # find example directories
            if fs.is_hidden(template_file):
                continue
            elif template_file.is_dir():
                # assert template directories exist
                if r_template_path not in r_instance_files:
                    logger.error(f'Directory {r_template_path} does not exist in instance {instance_dir}')
                    return False
            elif template_file.suffix == '.md':
                if r_template_path not in r_instance_files:
                    logger.error(
                        f'Required template file {template_file} does not exist in measured instance {instance_dir}'
                    )
                    return False
                else:
                    # Measure
                    md_validator = markdown_validator.MarkdownValidator(
                        template_file, validate_header, governed_heading
                    )
                    full_path = instance_dir / r_template_path
                    status = md_validator.validate(full_path)
                    if not status:
                        logger.error(f'Markdown file {full_path} failed validation.')
                        return False
        return True

    def create_sample(self, task_name: str, trestle_root: pathlib.Path) -> int:
        """Create a sample folder within the task and populate with template content.

        Args:
            task_name: the task name to generate content for
            trestle_root: the root of the trestle project.
        Returns:
            Unix return code for running sample as a command.
        """
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        task_path = trestle_root / task_name
        ii = 0
        while True:
            sample_path = task_path / f'sample_folder_{ii}'
            if sample_path.exists():
                ii = ii + 1
                continue
            shutil.copytree(str(template_dir), str(sample_path))
            return 0

    def validate(
        self,
        task_name: str,
        trestle_root: pathlib.Path,
        governed_heading: str,
        validate_header: bool,
        project_override: bool = False
    ) -> int:
        """Validate task."""
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        if project_override:
            task_path = trestle_root
        else:
            task_path = trestle_root / task_name
        if not task_path.is_dir():
            logger.error(f'Task directory {task_path} does not exist. Exiting validate.')
            return 1

        for task_instance in task_path.iterdir():
            if task_instance.is_dir():
                result = self._measure_template_folder(template_dir, task_instance, governed_heading, validate_header)
                if not result:
                    logger.error(f'Governed-folder validation failed for task {task_name} on directory {task_instance}')
                    return 1
            else:
                logger.info(f'Unexpected file {task_path} identified in {task_name} directory, ignoring.')
        return 0
