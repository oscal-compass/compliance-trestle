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
from typing import List

from pkg_resources import resource_filename

import trestle.core.commands.author.consts as author_const
import trestle.core.draw_io as draw_io
import trestle.core.markdown_validator as markdown_validator
import trestle.utils.fs as fs
from trestle.core.commands.author.common import AuthorCommonCommand

logger = logging.getLogger(__name__)


class Folders(AuthorCommonCommand):
    """Markdown governed folders - enforcing consistent files and templates across directories."""

    name = 'folders'

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
        self.add_argument(author_const.mode_arg_name, choices=author_const.mode_choices)
        tn_help_str = '\n'.join(
            [
                'The name of the the task to be governed.',
                '',
                'The template files are at .trestle/author/[task-name],',
                'where the directory tree established and the markdown files within that directory'
                + 'tree are enforced.'
            ]
        )

        self.add_argument(
            author_const.task_name_short, author_const.task_name_long, help=tn_help_str, required=True, type=str
        )
        self.add_argument(
            author_const.short_readme_validate,
            author_const.long_readme_validate,
            help=author_const.readme_validate_folders_help,
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
                    args.header_validate, args.header_only_validate, args.governed_heading, args.readme_validate
                )
            elif args.mode == 'setup':
                status = self.setup_template()
            elif args.mode == 'validate':
                # mode is validate
                status = self.validate(
                    args.header_validate, args.header_only_validate, args.governed_heading, args.readme_validate
                )
        except Exception as e:
            logger.error(f'Exception "{e}" running trestle md governed folders.')
        return status

    def setup_template(self) -> int:
        """Create structure to allow markdown template enforcement."""
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

        template_file_a_md = self.template_dir / 'a_template.md'
        template_file_another_md = self.template_dir / 'another_template.md'
        template_file_drawio = self.template_dir / 'architecture.drawio'
        md_template = pathlib.Path(resource_filename('trestle.resources', 'template.md')).resolve()
        drawio_template = pathlib.Path(resource_filename('trestle.resources', 'template.drawio')).resolve()
        shutil.copy(md_template, template_file_a_md)
        shutil.copy(md_template, template_file_another_md)
        shutil.copy(drawio_template, template_file_drawio)
        return 0

    def template_validate(
        self, validate_header: bool, validate_only_header: bool, heading: str, readme_validate: bool
    ) -> int:
        """Validate that the template is acceptable markdown."""
        if not self.template_dir.is_dir():
            logger.error(
                f'Template directory {self.rel_dir(self.template_dir)} for task {self.task_name} does not exist.'
            )
            return 1
        # get list of files:
        template_files = self.template_dir.rglob('*')

        for template_file in template_files:
            if not fs.local_and_visible(template_file):
                continue
            elif template_file.is_dir():
                continue
            elif template_file.suffix.lower() == '.md':
                if not readme_validate and template_file.name == 'readme.md':
                    logger.error('Template directory contains a readme.md file and readme validation is off.')
                    return 1
                try:
                    _ = markdown_validator.MarkdownValidator(
                        template_file, validate_header, validate_only_header, heading
                    )
                except Exception as ex:
                    logger.error(
                        f'Template file {self.rel_dir(template_file)} for task {self.task_name}'
                        + f' failed to validate due to {ex}'
                    )
                    return 1
            elif template_file.suffix.lower().lstrip('.') == 'drawio':
                try:
                    _ = draw_io.DrawIOMetadataValidator(template_file)
                except Exception as ex:
                    logger.error(
                        f'Template file {self.rel_dir(template_file)} for task {self.task_name}'
                        + f' failed to validate due to {ex}'
                    )
                    return 1
            else:
                logger.info(
                    f'File: {self.rel_dir(template_file)} within the template directory was ignored'
                    + 'as it is not markdown.'
                )
        logger.info(f'TEMPLATES VALID: {self.task_name}.')
        return 0

    def _measure_template_folder(
        self,
        template_dir: pathlib.Path,
        instance_dir: pathlib.Path,
        validate_header: bool,
        validate_only_header: bool,
        governed_heading: str,
        readme_validate: bool
    ) -> bool:

        r_instance_files: List[pathlib.Path] = []
        for instance_file in instance_dir.rglob('*'):
            if fs.local_and_visible(instance_file):
                if instance_file.name.lower() == 'readme.md' and not readme_validate:
                    continue
                r_instance_files.append(instance_file.relative_to(instance_dir))

        for template_file in template_dir.rglob('*'):
            r_template_path = template_file.relative_to(template_dir)
            # find example directories
            clean_suffix = template_file.suffix.lstrip('.')
            if not fs.local_and_visible(template_file):
                continue
            if not readme_validate and template_file.name.lower() == 'readme.md':
                continue
            elif template_file.is_dir():
                # assert template directories exist
                if r_template_path not in r_instance_files:
                    logger.error(f'Directory {r_template_path} does not exist in instance {self.rel_dir(instance_dir)}')
                    return False
            elif clean_suffix in author_const.reference_templates:
                if r_template_path not in r_instance_files:
                    logger.error(
                        f'Required template file {self.rel_dir(template_file)} does not exist in measured instance'
                        + f'{self.rel_dir(instance_dir)}'
                    )
                    return False
                else:
                    full_path = instance_dir / r_template_path
                    if clean_suffix == 'md':
                        # Measure
                        md_validator = markdown_validator.MarkdownValidator(
                            template_file, validate_header, validate_only_header, governed_heading
                        )

                        status = md_validator.validate(full_path)
                        if not status:
                            logger.error(
                                f'Markdown file {self.rel_dir(full_path)} failed validation against'
                                + f' {self.rel_dir(template_file)}'
                            )
                            return False
                    elif clean_suffix == 'drawio':
                        drawio_validator = draw_io.DrawIOMetadataValidator(template_file)
                        status = drawio_validator.validate(full_path)
                        if not status:
                            logger.error(
                                f'Drawio file {self.rel_dir(full_path)} failed validation against'
                                + f' {self.rel_dir(template_file)}'
                            )
                            return False
        return True

    def create_sample(self) -> int:
        """
        Create a sample folder within the task and populate with template content.

        Returns:
            Unix return code for running sample as a command.
        """
        ii = 0
        while True:
            sample_path = self.task_path / f'sample_folder_{ii}'
            if sample_path.exists():
                ii = ii + 1
                continue
            shutil.copytree(str(self.template_dir), str(sample_path))
            return 0

    def validate(
        self, validate_header: bool, validate_only_header: bool, governed_heading: str, readme_validate: bool
    ) -> int:
        """Validate task."""
        if not self.task_path.is_dir():
            logger.error(f'Task directory {self.task_path} does not exist. Exiting validate.')
            return 1

        for task_instance in self.task_path.iterdir():
            if task_instance.is_dir():
                if fs.is_symlink(task_instance):
                    continue
                result = self._measure_template_folder(
                    self.template_dir,
                    task_instance,
                    validate_header,
                    validate_only_header,
                    governed_heading,
                    readme_validate
                )
                if not result:
                    logger.error(
                        'Governed-folder validation failed for task'
                        + f'{self.task_name} on directory {self.rel_dir(task_instance)}'
                    )
                    return 1
            else:
                logger.warning(
                    f'Unexpected file {self.rel_dir(task_instance)} identified in {self.task_name}'
                    + ' directory, ignoring.'
                )
        return 0
