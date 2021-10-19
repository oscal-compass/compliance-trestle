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
"""Markdown Validator."""
import logging
import pathlib
from typing import Any, Dict, Optional

from trestle.core.markdown.markdown_node import MarkdownNode

logger = logging.getLogger(__name__)


class MarkdownValidator:
    """A markdown validator. Validates markdown instance against given template."""

    def __init__(
        self,
        tmp_path: str,
        template_header: Dict,
        template_tree: MarkdownNode,
        validate_yaml_header: bool,
        validate_md_body: bool,
        md_header_to_validate: Optional[str] = None
    ):
        """Initialize markdown validator."""
        self._validate_yaml_header = validate_yaml_header
        self._validate_md_body = validate_md_body
        self.md_header_to_validate = md_header_to_validate.strip(' ') if md_header_to_validate is not None else None
        self.template_header = template_header
        self.template_tree = template_tree
        self.template_path = tmp_path

    def is_valid_against_template(
        self, instance: pathlib.Path, instance_header: Dict, instance_tree: MarkdownNode
    ) -> bool:
        """
        Validate instance markdown against template.

        Instance is correct against a template iff:
            1. For YAML header keys:
                a. All keys from the template are present and not modified
            2. On the Markdown w/o YAML header:
                a. No additional headers of the level 1 were added
                b. Headers were not reordered
                c. Headers in the instance should be a superset of the template headers
                d. Headers must be in heirarchical order (i.e. # then ### then ## is not allowed)
            3. If Governed Header is given then:
                a. Governed Header is not modified
                b. All keys (i.e. key: something) inside the section are present

        Args:
            instance: a path to the markdown instance that should be validated
            instance_header: a YAML header extracted from the markdown
            instance_tree: a tree structure representing markdown contents
        Returns:
            Whether or not the the candidate is valid against the template.
        """
        if self._validate_yaml_header:
            headers_match = self.compare_keys(self.template_header, instance_header)

            if not headers_match:
                logger.info(f'YAML header mismatch between template {self.template_path} and instance {instance}')
                return False
            elif headers_match and not self._validate_md_body:
                return True

        if self.md_header_to_validate is not None:
            instance_gov_node = instance_tree.get_node_for_key(self.md_header_to_validate, False)
            template_gov_node = self.template_tree.get_node_for_key(self.md_header_to_validate, False)
            if instance_gov_node is None:
                logger.info(f'Governed document not found in instance: {instance}')
                return False
            instance_keys = instance_gov_node.content.governed_document
            template_keys = template_gov_node.content.governed_document

            if len(template_keys) > len(instance_keys):
                logger.info(f'Headings in the instance: {instance} were removed.')
                return False
            template_header_pointer = 0
            for key in instance_keys:
                if key in template_keys and key != template_keys[template_header_pointer]:
                    logger.info(f'Headers in the instance: {instance} were shuffled or modified.')
                    return False
                elif key in template_keys and key == template_keys[template_header_pointer]:
                    template_header_pointer += 1
            if template_header_pointer != len(template_keys):
                logger.info(f'Headings in the instance: {instance} were removed.')
                return False

        if self._validate_md_body:
            instance_keys = instance_tree.content.subnodes_keys
            template_keys = self.template_tree.content.subnodes_keys
            if len(template_keys) > len(instance_keys):
                logger.info(f'Headings in the instance: {instance} were removed.')
                return False
            instance_lvl1_keys = list(instance_tree.get_all_headers_for_level(1))
            template_lvl1_keys = list(self.template_tree.get_all_headers_for_level(1))
            if len(template_lvl1_keys) < len(instance_lvl1_keys):
                logger.info(f'New headers of level 1 were added to the markdown instance: {instance}. ')
                return False
            template_header_pointer = 0
            for key in instance_keys:
                if key in template_keys and key != template_keys[template_header_pointer]:
                    logger.info(f'Headers in the instance: {instance} were shuffled or modified.')
                    return False
                elif key in template_keys and key == template_keys[template_header_pointer]:
                    template_header_pointer += 1
            if template_header_pointer != len(template_keys):
                logger.info(f'Headings in the instance {instance} were removed.')
                return False

        return True

    @classmethod
    def compare_keys(cls, template: Dict[str, Any], candidate: Dict[str, Any]) -> bool:
        """
        Compare a template dictionary against a candidate as to whether key structure is maintained.

        Args:
            template: Template dict which is used as a model of key-value pairs
            candidate: Candidate dictionary to be measured
        Returns:
            Whether or not the the candidate matches the template keys.
        """
        if len(template.keys()) != len(candidate.keys()):
            return False
        for key in template.keys():
            if key in candidate.keys():
                if type(template[key]) == dict:
                    if type(candidate[key]) == dict:
                        status = cls.compare_keys(template[key], candidate[key])
                        if not status:
                            return status
                    else:
                        return False
            else:
                return False
        return True
