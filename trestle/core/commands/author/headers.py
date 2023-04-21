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
import re
from typing import Any, Dict, List

import trestle.core.commands.author.consts as author_const
from trestle.common import const, file_utils
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.author.versioning.template_versioning import TemplateVersioning
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.draw_io import DrawIO, DrawIOMetadataValidator
from trestle.core.markdown.markdown_api import MarkdownAPI

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
            author_const.SHORT_TEMPLATE_VERSION,
            author_const.LONG_TEMPLATE_VERSION,
            help=author_const.TEMPLATE_VERSION_HELP,
            action='store'
        )
        self.add_argument(
            author_const.SHORT_IGNORE, author_const.LONG_IGNORE, help=author_const.IGNORE_HELP, default=None, type=str
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
        try:
            status = 1
            if self._initialize(args):
                return status
            # Handle conditional requirement of args.task_name
            # global is special so we need to use get attribute.
            if not self.global_ and not self.task_name:
                logger.warning('Task name (-tn) argument is required when global is not specified')
                return status

            if args.exclude:
                logger.warning('--exclude or -e is deprecated, use --ignore instead.')

            if args.mode == 'create-sample':
                status = self.create_sample()

            elif args.mode == 'template-validate':
                status = self.template_validate()
            elif args.mode == 'setup':
                status = self.setup(args.template_version)
            elif args.mode == 'validate':
                exclusions = []
                if args.exclude:
                    exclusions = args.exclude
                # mode is validate
                status = self.validate(
                    args.recurse, args.readme_validate, exclusions, args.template_version, args.ignore
                )
            return status

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error occurred when running trestle author headers')

    def create_sample(self) -> int:
        """Create sample object, this always defaults to markdown."""
        logger.info('Header only validation does not support sample creation.')
        logger.info('Exiting')
        return CmdReturnCodes.SUCCESS.value

    def setup(self, template_version: str) -> int:
        """Create template directory and templates."""
        # Step 1 - validation

        if self.task_name and not self.task_path.exists():
            self.task_path.mkdir(exist_ok=True, parents=True)
        elif self.task_name and self.task_path.is_file():
            raise TrestleError(f'Task path: {self.rel_dir(self.task_path)} is a file not a directory.')

        if not self.template_dir.exists():
            self.template_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f'Populating template files to {self.rel_dir(self.template_dir)}')
        for template in author_const.REFERENCE_TEMPLATES.values():
            destination_path = self.template_dir / template
            TemplateVersioning.write_versioned_template(template, self.template_dir, destination_path, template_version)

            logger.info(f'Template directory populated {self.rel_dir(destination_path)}')
        return CmdReturnCodes.SUCCESS.value

    def template_validate(self) -> int:
        """Validate the integrity of the template files."""
        logger.info('Checking template file integrity')
        for template_file in self.template_dir.iterdir():
            if (template_file.name not in author_const.REFERENCE_TEMPLATES.values()
                    and template_file.name.lower() != 'readme.md'):
                raise TrestleError(f'Unexpected template file {self.rel_dir(template_file)}')

            if template_file.suffix == const.MARKDOWN_FILE_EXT:
                try:
                    md_api = MarkdownAPI()
                    md_api.load_validator_with_template(template_file, True, False)
                except Exception as ex:
                    raise TrestleError(f'Template for task {self.task_name} failed to validate due to {ex}')

            elif template_file.suffix == const.DRAWIO_FILE_EXT:
                try:
                    _ = DrawIOMetadataValidator(template_file)
                except Exception as ex:
                    raise TrestleError(f'Template for task {self.task_name} failed to validate due to {ex}')

        logger.info('Templates validated')
        return CmdReturnCodes.SUCCESS.value

    def _validate_dir(
        self,
        candidate_dir: pathlib.Path,
        recurse: bool,
        readme_validate: bool,
        relative_exclusions: List[pathlib.Path],
        template_version: str,
        ignore: str
    ) -> bool:
        """Validate a directory within the trestle workspace."""
        all_versioned_templates: Dict[str, Any] = {}
        instance_version = template_version
        instance_file_names: List[pathlib.Path] = []
        # Fetch all instances versions and build dictionary of required template files
        instances = list(candidate_dir.iterdir())
        if recurse:
            instances = candidate_dir.rglob('*')
            if ignore:
                p = re.compile(ignore)
                instances = list(
                    filter(
                        lambda f: len(list(filter(p.match, str(f.relative_to(candidate_dir)).split('/')))) == 0,
                        instances
                    )
                )
        for instance_file in instances:
            if not file_utils.is_local_and_visible(instance_file):
                continue
            if instance_file.name.lower() == 'readme.md' and not readme_validate:
                continue
            if instance_file.is_dir() and not recurse:
                continue
            if any(str(ex) in str(instance_file) for ex in relative_exclusions):
                continue
            if ignore:
                p = re.compile(ignore)
                matched = p.match(instance_file.parts[-1])
                if matched is not None:
                    logger.info(f'Ignoring file {instance_file} from validation.')
                    continue
            instance_file_name = instance_file.relative_to(candidate_dir)
            instance_file_names.append(instance_file_name)
            if instance_file.suffix == const.MARKDOWN_FILE_EXT:
                md_api = MarkdownAPI()
                versioned_template_dir = None
                if template_version != '':
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

                if instance_version not in all_versioned_templates.keys():
                    templates = list(
                        filter(lambda p: file_utils.is_local_and_visible(p), versioned_template_dir.iterdir())
                    )
                    if not readme_validate:
                        templates = list(filter(lambda p: p.name.lower() != 'readme.md', templates))
                    self._update_templates(all_versioned_templates, templates, instance_version)

                # validate
                md_api.load_validator_with_template(all_versioned_templates[instance_version]['md'], True, False)
                status = md_api.validate_instance(instance_file)
                if not status:
                    logger.info(f'INVALID: {self.rel_dir(instance_file)}')
                    return False
                else:
                    logger.info(f'VALID: {self.rel_dir(instance_file)}')

            elif instance_file.suffix == const.DRAWIO_FILE_EXT:
                drawio = DrawIO(instance_file)
                metadata = drawio.get_metadata()[0]

                versioned_template_dir = None
                if template_version != '':
                    versioned_template_dir = self.template_dir
                else:
                    if author_const.TEMPLATE_VERSION_HEADER in metadata.keys():
                        instance_version = metadata[author_const.TEMPLATE_VERSION_HEADER]
                    else:
                        instance_version = '0.0.1'  # backward compatibility

                    versioned_template_dir = TemplateVersioning.get_versioned_template_dir(
                        self.template_dir, instance_version
                    )

                if instance_version not in all_versioned_templates.keys():
                    templates = list(
                        filter(lambda p: file_utils.is_local_and_visible(p), versioned_template_dir.iterdir())
                    )
                    if not readme_validate:
                        templates = list(filter(lambda p: p.name.lower() != 'readme.md', templates))
                    self._update_templates(all_versioned_templates, templates, instance_version)

                # validate
                drawio_validator = DrawIOMetadataValidator(all_versioned_templates[instance_version]['drawio'])
                status = drawio_validator.validate(instance_file)
                if not status:
                    logger.info(f'INVALID: {self.rel_dir(instance_file)}')
                    return False
                else:
                    logger.info(f'VALID: {self.rel_dir(instance_file)}')

            else:
                logger.debug(f'Unsupported extension of the instance file: {instance_file}, will not be validated.')

        return True

    def _update_templates(
        self, all_versioned_templates: Dict[str, Dict[str, str]], templates: List[str], instance_version: str
    ) -> None:
        all_versioned_templates[instance_version] = {}
        all_drawio_templates = list(filter(lambda p: p.suffix == const.DRAWIO_FILE_EXT, templates))
        all_md_templates = list(filter(lambda p: p.suffix == const.MARKDOWN_FILE_EXT, templates))
        if all_drawio_templates:
            all_versioned_templates[instance_version]['drawio'] = all_drawio_templates[0]
        if all_md_templates:
            all_versioned_templates[instance_version]['md'] = all_md_templates[0]

    def validate(
        self,
        recurse: bool,
        readme_validate: bool,
        relative_excludes: List[pathlib.Path],
        template_version: str,
        ignore: str
    ) -> int:
        """Run validation based on available templates."""
        paths = []
        if self.task_name:
            if not self.task_path.is_dir():
                raise TrestleError(f'Task directory {self.rel_dir(self.task_path)} does not exist. Exiting validate.')

            paths = [self.task_path]
        else:
            for path in self.trestle_root.iterdir():
                relative_path = path.relative_to(self.trestle_root)
                # Files in the root directory must be exclused
                if path.is_file():
                    continue
                if not file_utils.is_directory_name_allowed(path):
                    continue
                if str(relative_path).rstrip('/') in const.MODEL_DIR_LIST:
                    continue
                if (relative_path in relative_excludes):
                    continue
                if not file_utils.is_hidden(path):
                    paths.append(path)

        for path in paths:
            try:
                valid = self._validate_dir(path, recurse, readme_validate, relative_excludes, template_version, ignore)
                if not valid:
                    logger.info(f'validation failed on {path}')
                    return CmdReturnCodes.DOCUMENTS_VALIDATION_ERROR.value
            except Exception as e:
                raise TrestleError(f'Error during header validation on {path} {e}')

        return CmdReturnCodes.SUCCESS.value
