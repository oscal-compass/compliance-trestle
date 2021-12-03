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
from typing import List

import trestle.core.commands.author.consts as author_const
import trestle.core.draw_io as draw_io
import trestle.utils.fs as fs
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.author.versioning.template_versioning import TemplateVersioning
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_api import MarkdownAPI

logger = logging.getLogger(__name__)


class Folders(AuthorCommonCommand):
    """Markdown governed folders - enforcing consistent files and templates across directories."""

    name = 'folders'

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
            author_const.HOV_SHORT, author_const.HOV_LONG, help=author_const.HOV_HELP, action='store_true'
        )
        self.add_argument(
            author_const.SHORT_TEMPLATE_VERSION,
            author_const.LONG_TEMPLATE_VERSION,
            help=author_const.TEMPLATE_VERSION_HELP,
            action='store'
        )
        self.add_argument(
            author_const.SHORT_IGNORE, author_const.LONG_IGNORE, help=author_const.IGNORE_HELP, default=None, type=str
        )
        self.add_argument(author_const.MODE_ARG_NAME, choices=author_const.MODE_CHOICES)
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
            author_const.TASK_NAME_SHORT, author_const.TASK_NAME_LONG, help=tn_help_str, required=True, type=str
        )
        self.add_argument(
            author_const.SHORT_README_VALIDATE,
            author_const.LONG_README_VALIDATE,
            help=author_const.README_VALIDATE_FOLDERS_HELP,
            action='store_true'
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            if self._initialize(args):
                return CmdReturnCodes.COMMAND_ERROR.value
            if args.mode == 'create-sample':
                status = self.create_sample()

            elif args.mode == 'template-validate':
                status = self.template_validate(
                    args.header_validate, args.header_only_validate, args.governed_heading, args.readme_validate
                )
            elif args.mode == 'setup':
                status = self.setup_template(args.template_version)
            elif args.mode == 'validate':
                # mode is validate
                status = self.validate(
                    args.header_validate,
                    args.header_only_validate,
                    args.governed_heading,
                    args.readme_validate,
                    args.template_version,
                    args.ignore
                )
            else:
                logger.error(f'Unsupported mode: {args.mode} for folders command.')
                return CmdReturnCodes.INCORRECT_ARGS.value
            return status
        except TrestleError as e:
            logger.error(f'Error occurred when running trestle author folders: {e}')
            logger.error('Exiting')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            logger.error(f'Unexpected error occurred when running trestle author folders: {e}')
            logger.error('Exiting')
            return CmdReturnCodes.COMMAND_ERROR.value

    def setup_template(self, template_version: str) -> int:
        """Create structure to allow markdown template enforcement."""
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

        template_file_a_md = self.template_dir / 'a_template.md'
        template_file_another_md = self.template_dir / 'another_template.md'
        template_file_drawio = self.template_dir / 'architecture.drawio'
        TemplateVersioning.write_versioned_template(
            'template.md', self.template_dir, template_file_a_md, template_version
        )
        TemplateVersioning.write_versioned_template(
            'template.md', self.template_dir, template_file_another_md, template_version
        )
        TemplateVersioning.write_versioned_template(
            'template.drawio', self.template_dir, template_file_drawio, template_version
        )

        return CmdReturnCodes.SUCCESS.value

    def template_validate(
        self, validate_header: bool, validate_only_header: bool, heading: str, readme_validate: bool
    ) -> int:
        """Validate that the template is acceptable markdown."""
        if not self.template_dir.is_dir():
            logger.error(
                f'Template directory {self.rel_dir(self.template_dir)} for task {self.task_name} does not exist.'
            )
            return CmdReturnCodes.COMMAND_ERROR.value
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
                    return CmdReturnCodes.COMMAND_ERROR.value
                try:
                    md_api = MarkdownAPI()
                    md_api.load_validator_with_template(
                        template_file, validate_header, not validate_only_header, heading
                    )
                except Exception as ex:
                    logger.error(
                        f'Template file {self.rel_dir(template_file)} for task {self.task_name}'
                        + f' failed to validate due to {ex}'
                    )
                    return CmdReturnCodes.COMMAND_ERROR.value
            elif template_file.suffix.lower().lstrip('.') == 'drawio':
                try:
                    _ = draw_io.DrawIOMetadataValidator(template_file)
                except Exception as ex:
                    logger.error(
                        f'Template file {self.rel_dir(template_file)} for task {self.task_name}'
                        + f' failed to validate due to {ex}'
                    )
                    return CmdReturnCodes.COMMAND_ERROR.value
            else:
                logger.info(
                    f'File: {self.rel_dir(template_file)} within the template directory was ignored'
                    + 'as it is not markdown.'
                )
        logger.info(f'TEMPLATES VALID: {self.task_name}.')
        return CmdReturnCodes.SUCCESS.value

    def _measure_template_folder(
        self,
        instance_dir: pathlib.Path,
        validate_header: bool,
        validate_only_header: bool,
        governed_heading: str,
        readme_validate: bool,
        template_version: str,
        ignore: str
    ) -> bool:
        """
        Validate instances against templates.

        Validation will succeed iff:
            1. All template files from the specified version are present in the task
            2. All of the instances are valid
        """
        all_versioned_templates = {}
        instance_version = template_version
        instance_file_names: List[pathlib.Path] = []
        # Fetch all instances versions and build dictionary of required template files
        for instance_file in instance_dir.iterdir():
            if not fs.local_and_visible(instance_file):
                continue
            if not instance_file.is_file():
                continue
            if instance_file.name.lower() == 'readme.md' and not readme_validate:
                continue
            if ignore:
                p = re.compile(ignore)
                matched = p.match(instance_file.parts[-1])
                if matched is not None:
                    logger.info(f'Ignoring file {instance_file} from validation.')
                    continue
            instance_file_name = instance_file.relative_to(instance_dir)
            instance_file_names.append(instance_file_name)
            if instance_file.suffix == '.md':
                md_api = MarkdownAPI()
                versioned_template_dir = None
                if template_version != '':
                    template_file = self.template_dir / instance_file_name
                    versioned_template_dir = self.template_dir
                else:
                    instance_version = md_api.processor.fetch_value_from_header(
                        instance_file, author_const.TEMPLATE_VERSION_HEADER
                    )
                    if instance_version is None:
                        instance_version = '0.0.1'  # backward compatibility
                    versioned_template_dir = TemplateVersioning.get_versioned_template_dir(
                        self.template_dir, instance_version
                    )
                    template_file = versioned_template_dir / instance_file_name

                if instance_version not in all_versioned_templates.keys():
                    templates = list(filter(lambda p: fs.local_and_visible(p), versioned_template_dir.iterdir()))
                    if not readme_validate:
                        templates = list(filter(lambda p: p.name.lower() != 'readme.md', templates))

                    all_versioned_templates[instance_version] = dict.fromkeys(
                        [t.relative_to(versioned_template_dir) for t in templates], False
                    )

                if instance_file_name in all_versioned_templates[instance_version]:
                    # validate
                    md_api.load_validator_with_template(
                        template_file, validate_header, not validate_only_header, governed_heading
                    )
                    status = md_api.validate_instance(instance_file)
                    if not status:
                        logger.error(f'Markdown file {instance_file} failed validation against' + f' {template_file}')
                        logger.info(f'INVALID: {instance_file}')
                        return False
                    else:
                        logger.info(f'VALID: {instance_file}')
                    # mark template as present
                    all_versioned_templates[instance_version][instance_file_name] = True

            elif instance_file.suffix == '.drawio':
                drawio = draw_io.DrawIO(instance_file)
                metadata = drawio.get_metadata()[0]
                versioned_template_dir = None
                if template_version != '':
                    template_file = self.template_dir / instance_file_name
                    versioned_template_dir = self.template_dir
                else:
                    if author_const.TEMPLATE_VERSION_HEADER in metadata.keys():
                        instance_version = metadata[author_const.TEMPLATE_VERSION_HEADER]
                    else:
                        instance_version = '0.0.1'  # backward compatibility

                    versioned_template_dir = TemplateVersioning.get_versioned_template_dir(
                        self.template_dir, instance_version
                    )
                    template_file = versioned_template_dir / instance_file_name

                if instance_version not in all_versioned_templates.keys():
                    templates = list(filter(lambda p: fs.local_and_visible(p), versioned_template_dir.iterdir()))
                    if not readme_validate:
                        templates = list(filter(lambda p: p.name.lower() != 'readme.md', templates))

                    all_versioned_templates[instance_version] = dict.fromkeys(
                        [t.relative_to(versioned_template_dir) for t in templates], False
                    )

                if instance_file_name in all_versioned_templates[instance_version]:
                    # validate
                    drawio_validator = draw_io.DrawIOMetadataValidator(template_file)
                    status = drawio_validator.validate(instance_file)
                    if not status:
                        logger.error(f'Drawio file {instance_file} failed validation against' + f' {template_file}')
                        logger.info(f'INVALID: {instance_file}')
                        return False
                    else:
                        logger.info(f'VALID: {instance_file}')
                    # mark template as present
                    all_versioned_templates[instance_version][instance_file_name] = True

            else:
                logger.debug(f'Unsupported extension of the instance file: {instance_file}, will not be validated.')

        # Check that all template files are present
        for version in all_versioned_templates.keys():
            for template in all_versioned_templates[version]:
                if not all_versioned_templates[version][template]:
                    logger.error(
                        f'Required template file {template} does not exist in measured instance' + f'{instance_dir}'
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
            return CmdReturnCodes.SUCCESS.value

    def validate(
        self,
        validate_header: bool,
        validate_only_header: bool,
        governed_heading: str,
        readme_validate: bool,
        template_version: str,
        ignore: str
    ) -> int:
        """Validate task."""
        if not self.task_path.is_dir():
            logger.error(f'Task directory {self.task_path} does not exist. Exiting validate.')
            return CmdReturnCodes.COMMAND_ERROR.value

        for task_instance in self.task_path.iterdir():
            if task_instance.is_dir():
                if fs.is_symlink(task_instance):
                    continue
                result = self._measure_template_folder(
                    task_instance,
                    validate_header,
                    validate_only_header,
                    governed_heading,
                    readme_validate,
                    template_version,
                    ignore
                )
                if not result:
                    logger.error(
                        'Governed-folder validation failed for task'
                        + f'{self.task_name} on directory {self.rel_dir(task_instance)}'
                    )
                    return CmdReturnCodes.COMMAND_ERROR.value
            else:
                logger.warning(
                    f'Unexpected file {self.rel_dir(task_instance)} identified in {self.task_name}'
                    + ' directory, ignoring.'
                )
        return CmdReturnCodes.SUCCESS.value
