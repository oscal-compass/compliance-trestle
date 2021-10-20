# -*- mode:python; coding:utf-8 -*-

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
"""Trestle author headers command."""
import argparse
import logging
import pathlib
import shutil
from typing import Dict, List

from pkg_resources import resource_filename

import trestle.core.commands.author.consts as author_const
import trestle.utils.fs as fs
from trestle.core import const
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.draw_io import DrawIOMetadataValidator
from trestle.core.markdown_validator import MarkdownValidator

logger = logging.getLogger(__name__)


class Headers(AuthorCommonCommand):
    """Enforce header / metadata across file types supported by author (markdown and drawio)."""

    name = 'headers'

    def _init_arguments(self) -> None:
        self.add_argument(
            author_const.RECURSE_SHORT, author_const.RECURSE_LONG, help=author_const.RECURSE_HELP, action='store_true'
        )
        self.add_argument(author_const.MODE_ARG_NAME, choices=author_const.MODE_CHOICES)
        tn_help_str = '\n'.join(
            [
                'The name of the the task to be governed.',
                '',
                'The template files for header metadata governance are located at .trestle/author/[task name]',
                'Currently supported types are:',
                'Markdown: .trestle/author/[task name]/template.md',
                'Drawio: .trestle/author/[task name]/template.drawio',
                '',
                'Note that by default this will automatically enforce the task.'
            ]
        )
        self.add_argument(
            author_const.TASK_NAME_SHORT, author_const.TASK_NAME_LONG, help=tn_help_str, type=str, default=None
        )
        self.add_argument(
            author_const.SHORT_README_VALIDATE,
            author_const.LONG_README_VALIDATE,
            help=author_const.README_VALIDATE_HELP,
            action='store_true'
        )

        self.add_argument(
            author_const.GLOBAL_SHORT, author_const.GLOBAL_LONG, help=author_const.GLOBAL_HELP, action='store_true'
        )
        self.add_argument(
            author_const.EXCLUDE_SHORT,
            author_const.EXCLUDE_LONG,
            help=author_const.EXCLUDE_HELP,
            type=pathlib.Path,
            nargs='*',
            default=None
        )

    def _run(self, args: argparse.Namespace) -> int:
        if self._initialize(args):
            return 1
        status = 1
        # Handle conditional requirement of args.task_name
        # global is special so we need to use get attribute.
        if not self.global_ and not self.task_name:
            logger.warning('Task name (-tn) argument is required when global is not specified')
            return status

        try:
            if args.mode == 'create-sample':
                status = self.create_sample()

            elif args.mode == 'template-validate':
                status = self.template_validate()
            elif args.mode == 'setup':
                status = self.setup()
            elif args.mode == 'validate':
                exclusions = []
                if args.exclude:
                    exclusions = args.exclude
                # mode is validate
                status = self.validate(args.recurse, args.readme_validate, exclusions)
        except Exception as e:
            logger.error(f'Error "{e}"" occurred when running trestle author docs.')
            logger.error('Exiting')
        return status

    def create_sample(self) -> int:
        """Create sample object, this always defaults to markdown."""
        logger.info('Header only validation does not support sample creation.')
        logger.info('Exiting')
        return 0

    def setup(self) -> int:
        """Create template directory and templates."""
        # Step 1 - validation

        if self.task_name and not self.task_path.exists():
            self.task_path.mkdir(exist_ok=True, parents=True)
        elif self.task_name and self.task_path.is_file():
            logger.error(f'Task path: {self.rel_dir(self.task_path)} is a file not a directory.')
            return 1
        if not self.template_dir.exists():
            self.template_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f'Populating template files to {self.rel_dir(self.template_dir)}')
        for template in author_const.REFERENCE_TEMPLATES.values():
            template_path = pathlib.Path(resource_filename('trestle.resources', template)).resolve()
            destination_path = self.template_dir / template
            shutil.copy(template_path, destination_path)
            logger.info(f'Template directory populated {self.rel_dir(destination_path)}')
        return 0

    def template_validate(self) -> int:
        """Validate the integrity of the template files."""
        logger.info('Checking template file integrity')
        for template_file in self.template_dir.iterdir():
            if (template_file.name not in author_const.REFERENCE_TEMPLATES.values()
                    and template_file.name.lower() != 'readme.md'):
                logger.error(f'Unexpected template file {self.rel_dir(template_file)}')
                logger.error('Exiting')
                return 1
            if template_file.suffix == '.md':
                try:
                    _ = MarkdownValidator(template_file, True, True)
                except Exception as ex:
                    logger.error(f'Template for task {self.task_name} failed to validate due to {ex}')
                    return 1
            elif template_file.suffix == '.drawio':
                try:
                    _ = DrawIOMetadataValidator(template_file)
                except Exception as ex:
                    logger.error(f'Template for task {self.task_name} failed to validate due to {ex}')
                    return 1
        logger.info('Templates validated')
        return 0

    def _discover_templates(self) -> Dict[str, pathlib.Path]:
        """Based on an initial known set of templates."""
        # Hardcoded list of supported types
        new_templates: Dict[str, pathlib.Path] = {}
        for template_name, template_fname in author_const.REFERENCE_TEMPLATES.items():
            template_path = self.template_dir / template_fname
            if template_path.exists() and template_path.is_file():
                new_templates[template_name] = template_path
        return new_templates

    def _validate_dir(
        self,
        template_lut: Dict[str, pathlib.Path],
        candidate_dir: pathlib.Path,
        recurse: bool,
        readme_validate: bool,
        relative_excludes: List[pathlib.Path]
    ) -> bool:
        """Validate a directory within the trestle project."""
        for candidate_path in candidate_dir.iterdir():
            if fs.local_and_visible(candidate_path):
                if candidate_path.is_file():
                    clean_suffix = candidate_path.suffix.lstrip('.')
                    if clean_suffix == 'md':
                        logger.info(f'Validating: {self.rel_dir(candidate_path)}')
                        md_validator = MarkdownValidator(template_lut['md'], True, True)
                        validate_status = md_validator.validate(candidate_path)
                        if not validate_status:
                            logger.info(f'Invalid: {self.rel_dir(candidate_path)}')
                            return False
                        logger.info(f'Valid: {self.rel_dir(candidate_path)}')
                    elif clean_suffix == 'drawio':
                        logger.info(f'Validating: {self.rel_dir(candidate_path)}')
                        drawio_validator = DrawIOMetadataValidator(template_lut['drawio'])
                        validate_status = drawio_validator.validate(candidate_path)
                        if not validate_status:
                            logger.info(f'Invalid: {self.rel_dir(candidate_path)}')
                            return False
                        logger.info(f'Valid: {self.rel_dir(candidate_path)}')
                    else:
                        logger.info(f'Unsupported file {self.rel_dir(candidate_path)} ignored.')
                elif recurse:
                    if candidate_path.relative_to(self.trestle_root) in relative_excludes:
                        continue
                    if not self._validate_dir(template_lut, candidate_path, recurse, readme_validate,
                                              relative_excludes):
                        return False
        return True

    def validate(self, recurse: bool, readme_validate: bool, relative_excludes: List[pathlib.Path]) -> int:
        """Run validation based on available templates."""
        template_lut = self._discover_templates()
        paths = []
        if self.task_name:
            if not self.task_path.is_dir():
                logger.error(f'Task directory {self.rel_dir(self.task_path)} does not exist. Exiting validate.')
                return 1
            paths = [self.task_path]
        else:
            for path in self.trestle_root.iterdir():
                relative_path = path.relative_to(self.trestle_root)
                # Files in the root directory must be exclused
                if path.is_file():
                    continue
                if not fs.allowed_task_name(path):
                    continue
                if str(relative_path).rstrip('/') in const.MODEL_DIR_LIST:
                    continue
                if (relative_path in relative_excludes):
                    continue
                if not fs.is_hidden(path):
                    paths.append(path)

        for path in paths:
            try:
                valid = self._validate_dir(template_lut, path, recurse, readme_validate, relative_excludes)
                if not valid:
                    logger.info(f'validation failed on {path}')
                    return 1
            except Exception as e:
                logger.error(f'Error during header validation on {path} {e}')
                logger.error('Aborting')
                return 1
        return 0
