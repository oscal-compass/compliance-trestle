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
"""A markdown API."""
import logging
import pathlib
from typing import Dict, Optional

from trestle.common import const
from trestle.common.err import TrestleError
from trestle.core.markdown.markdown_processor import MarkdownProcessor
from trestle.core.markdown.markdown_validator import MarkdownValidator

import yaml

logger = logging.getLogger(__name__)


class MarkdownAPI:
    """A common API that wraps around the existing markdown functionality."""

    def __init__(self):
        """Initialize markdown API."""
        self.processor = MarkdownProcessor()
        self.validator = None

    def load_validator_with_template(
        self,
        md_template_path: pathlib.Path,
        validate_yaml_header: bool,
        validate_md_body: bool,
        governed_section: Optional[str] = None,
        validate_template: bool = False
    ) -> None:
        """Load and initialize markdown validator."""
        try:
            self.processor.governed_header = governed_section
            if validate_template:
                template_header, template_tree = self.processor.process_markdown(md_template_path, validate_yaml_header,
                                                                                 validate_md_body or governed_section is
                                                                                 not None)
            else:
                template_header, template_tree = self.processor.process_markdown(md_template_path)

            if not template_header and validate_yaml_header:
                raise TrestleError(f'Expected yaml header for markdown template where none exists {md_template_path}')

            self.validator = MarkdownValidator(
                md_template_path,
                template_header,
                template_tree,
                validate_yaml_header,
                validate_md_body,
                governed_section
            )
        except TrestleError as e:
            raise TrestleError(f'Error while loading markdown template {md_template_path}: {e}.')

    def validate_instance(self, md_instance_path: pathlib.Path) -> bool:
        """Validate a given markdown instance against a template."""
        if self.validator is None:
            raise TrestleError('Markdown validator is not initialized, load template first.')
        instance_header, instance_tree = self.processor.process_markdown(md_instance_path)
        return self.validator.is_valid_against_template(md_instance_path, instance_header, instance_tree)

    def write_markdown_with_header(self, path: pathlib.Path, header: Dict[str, str], md_body: str) -> None:
        """Write markdown with the YAML header."""
        try:
            # use encoding to handle character sets as well as possible
            with open(path, 'w', encoding=const.FILE_ENCODING, errors='replace') as md_file:
                md_file.write('---\n')
                yaml.safe_dump(header, md_file, sort_keys=False)
                md_file.write('---\n\n')
                md_file.write(md_body)
        except IOError as e:
            raise TrestleError(f'Error while writing markdown file: {e}')
