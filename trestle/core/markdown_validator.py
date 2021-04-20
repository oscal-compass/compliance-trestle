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
"""Markdown validator - provides functionality for operating on markdown files including template validation."""
import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import frontmatter

import mistune

from trestle.core import const
from trestle.core import err

logger = logging.getLogger(__name__)


def partition_ast(content: List[Dict[str, Any]], ref_level: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """
    Partition AST, recursive function to create a hierarchial tree out of a stream of markdown elements.

    Markdown elements are typically treated as a flat stream of tokens - which is sufficient for most needs.
    For this project and understanding of heading hierarchy.


    Args:
        content: List of AST parsing elements as from mistune
        ref_level: The markdown heading level expected. Set to 0 when starting naively
    Returns:
        List containing a tree of elements
        Number of elements parsed in within the sub-list

    """
    new_content = []
    ii = 0
    while ii < len(content):
        if content[ii]['type'] == 'heading':
            if content[ii]['level'] <= ref_level:
                break
            if ii + 1 == len(content):
                new_content.append(content[ii])
                ii = ii + 1
                break
            else:
                sub_content, jj = partition_ast(content[ii + 1:], content[ii]['level'])
                fixed_header = content[ii]
                fixed_header['children'].extend(sub_content)
                new_content.append(fixed_header)
                ii = ii + jj + 1
        else:
            new_content.append(content[ii])
            ii = ii + 1
    return new_content, ii


def compare_tree(template: Dict[str, Any], content: Dict[str, Any]) -> bool:
    """
    Compare whether a content parse tree is a superset of the template tree.

    The fundamental assumption here is anchored on the nesting of markdown headings.

    Assumptions:
    - Users of a template cannot create headers at the same level as a template only below that level.
    - Template levels cannot be changed.
    - Headers are the only element measured in the template.

    Args:
        template: The dictionary containing a hierarchy where all keys are enforced.
        content: The dictionary to be measured:

    Returns:
        Whether the content conforms to the template expectations.
    """
    # TODO: Add logging statements to this context.
    if not (template['type'] == 'heading'):
        # It's okay as we should not be here:
        return True
    template_heading_level = template['level']
    template_header_name = template['children'][0]['text'].strip()
    content_heading_level = content['level']
    content_header_name = content['children'][0]['text'].strip()
    if not template_heading_level == content_heading_level:
        logger.error('Unexpected trestle error in parsing markdown.')
        return False
    # ESCAPE title if required
    if not (template_header_name.strip()[0] == const.HEADER_L_ESCAPE
            and template_header_name.strip()[-1] == const.HEADER_R_ESCAPE):
        if not template_header_name == content_header_name:
            logger.info(
                f'Markdown templating failed due to mismatch between expected heading {template_header_name} and current heading {content_header_name}.'  # noqa: E501
            )
            return False
    template_sub_headers = []
    content_sub_headers = []
    for ii in range(len(template['children'])):
        if template['children'][ii]['type'] == 'heading':
            template_sub_headers.append(template['children'][ii])
    # IF there is no template headers we are good
    if len(template_sub_headers) == 0:
        return True

    for ii in range(len(content['children'])):
        if content['children'][ii]['type'] == 'heading':
            content_sub_headers.append(content['children'][ii])

    if not len(template_sub_headers) == len(content_sub_headers):
        # Deal with condition where extra headings are at a lower level than the first heading.
        logger.info(f'Number of expected sub-headings is wrong for heading {template_header_name}')
        logger.info(f'Expected {len(template_sub_headers)}, got {len(content_sub_headers)}')
        logger.info('Expected headings:')
        for template_header in template_sub_headers:
            logger.info(template_header['children'][0]['text'].strip())
        logger.info('Actual headings:')
        for content_heading in content_sub_headers:
            logger.info(content_heading['children'][0]['text'].strip())
        return False
    for ii in range(len(template_sub_headers)):
        status = compare_tree(template_sub_headers[ii], content_sub_headers[ii])
        if not status:
            return False
    return True


class MarkdownValidator:
    """Markdown validator to meet conformance expectations."""

    def __init__(
        self,
        template_path: pathlib.Path,
        yaml_header_validate: bool,
        strict_heading_validate: Optional[str] = None
    ) -> None:
        """
        Initialize markdown validator.

        Args:
            template_path: path to markdown template.
            yaml_header_validate: whether to validate a yaml header for conformance or not
            strict_heading_validate: Whether a heading, provided in the template, is to have line-by-line matching.
        """
        self._yaml_header_validate = yaml_header_validate
        self.template_path = template_path
        if not self.template_path.is_file():
            logger.error(f'Provided template {self.template_path.resolve()} is not a file')
            raise err.TrestleError(f'Unable to find markdown template {self.template_path.resolve()}')
        template_header, template_parse = self.load_markdown_parsetree(self.template_path)
        self._template_header = template_header
        self._template_parse = template_parse
        self._strict_heading_validate = strict_heading_validate
        self.template_tree, _ = partition_ast(self._template_parse)
        self.w_template_tree = self.wrap_content(self.template_tree)

    @classmethod
    def load_markdown_parsetree(cls, path: pathlib.Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load markdown file including yaml frontmatter.

        Args:
            path: File system path of the markdown.

        Returns:
            Yaml header which has been parsed or an empty dict.
            List of AST tokens in the flat structure provided by mistune.

        """
        try:
            content = path.open('r').read()
        except UnicodeDecodeError as e:
            logger.error('utf-8 decoding failed.')
            logger.error(f'See: {const.WEBSITE_ROOT}/errors/#utf-8-encoding-only')
            logger.debug(f'Underlying exception {e}')
            raise err.TrestleError('Unable to load file due to utf-8 encoding issues.')
        fm = frontmatter.loads(content)
        header_dict = fm.metadata
        md_no_header = fm.content
        mistune_ast_parser = mistune.create_markdown(renderer=mistune.AstRenderer())
        mistune_parse = mistune_ast_parser(md_no_header)
        return header_dict, mistune_parse

    @classmethod
    def wrap_content(cls, original: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Wrap an array of list into a pseudo-top level element to make it easier to handle.

        Warning: Not designed for rendering as it will produce extra text
        args:
            original: List of AST parse elements, likely normalized into a tree
        Returns:
            One pseudo element to make it easier to parse with a consistent name.
        """
        structure = {'type': 'heading', 'level': 0, 'children': [{'type': 'text', 'text': 'wrapping header'}]}
        structure['children'].extend(original)
        return structure

    def validate(self, candidate: pathlib.Path) -> bool:
        """
        Run the validation against a candidate file.

        Args:
            candidate: The path to a candidate markdown file to be validated.

        Returns:
            Whether or not the validation passes.
        """
        logger.info(f'Validating {candidate} against{self.template_path}')
        header_content, mistune_parse_content = self.load_markdown_parsetree(candidate)
        if self._yaml_header_validate:
            header_status = self.compare_keys(self._template_header, header_content)
            if not header_status:
                logger.warning(f'YAML header mismatch between template {self.template_path} and instance {candidate}')
                return False
        candidate_tree, _ = partition_ast(mistune_parse_content)
        w_candidate_tree = self.wrap_content(candidate_tree)
        if self._strict_heading_validate is not None:
            status = self._template_heading_validate(
                self.w_template_tree, w_candidate_tree, self._strict_heading_validate
            )
            if not status:
                logger.error(f'Heading {self._strict_heading_validate} did not meet templating requirements.')
                return False
        return compare_tree(self.w_template_tree, w_candidate_tree)

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
        for key in template.keys():
            if key in candidate.keys():
                if type(template[key]) == dict:
                    status = cls.compare_keys(template[key], candidate[key])
                    if not status:
                        return status
            else:
                return False
        return True

    def search_for_heading(self, candidate_tree: Dict[str, Any], heading: str) -> Dict[str, Any]:
        """
        Recursively search for a heading within a document and return the children.

        Args:
            candidate_tree: An AST parse tree that has been normalized by partition_ast
            heading: The string content for a markdown heading.

        Returns:
            The heading AST token if it exists, or an empty ast token.
        """
        answer = {}
        for candidate in candidate_tree['children']:
            if candidate['type'] == 'heading':
                if candidate['children'][0]['text'].strip() == heading.strip():
                    answer = candidate
                    break
                else:
                    answer = self.search_for_heading(candidate, heading)
        return answer

    def clean_content(self, parse_tree: Dict[str, Any]) -> List[str]:
        """
        Clean a set of content for measurement of header cleanliness.

        Args:
            parse_tree: AST parse normalized into a hierarchial tree.
        Returns:
            List of strings for each line of paragraph content.
        Raises:
            TrestleError: when unhandled object types are present.
        Assumptions:
            - Multiple paragraphs
            - no sub-headings
            - tables unhandled

        """
        items = parse_tree['children']
        clean_text_lines: List[str] = []

        for index in range(len(items)):
            # first item is the header title text which we will ignore.
            if index == 0:
                continue
            item = items[index]
            if item['type'] == 'block_html':
                # ignore all block HTML
                continue
            elif item['type'] == 'paragraph':
                line_content = ''
                for child in item['children']:
                    if child['type'] == 'linebreak':
                        clean_text_lines.extend(line_content.splitlines())
                        line_content = ''
                    elif 'html' in child['type']:
                        # ignore HTML comment presuming a commment
                        continue
                    elif 'strong' in child['type']:
                        line_content = line_content + child['children'][0]['text']
                    elif 'text' in child['type']:
                        line_content = line_content + child['text']
                    else:
                        msg = f'Unexpected element type {item["type"]} when flattening a governed header.'
                        logger.error(msg)
                        raise err.TrestleError(msg)
                # handle EoParagraph condition
                clean_text_lines.extend(line_content.splitlines())
            else:
                msg = f'Unexpected element type {item["type"]} when flattening a governed header.'
                logger.error(msg)
                raise err.TrestleError(msg)
        return clean_text_lines

    def _template_heading_validate(
        self, wrapped_template: Dict[str, Any], wrapped_candidate: Dict[str, Any], title_tag: str
    ) -> bool:
        """
        Validate a markdown document containing a structured header based on a title tag.

        This is an experimental capability which is relatively constrained.

        Args:
            wrapped_template: AST parse tree, of a template md document, normalized and wrapped into a single parent.
            wrapped_candidate: AST parse tree, of a validation candidate md document, normalized and wrapped.
            title_tag: String content of the markdown title for validation
        Returns:
            Status of whether or not heading validation passed.

        Assumptions:
            Header is determined the name of a heading block.
            Within the header no table exists (e.g. plain paragraphs)
            Header is valid if the header, excluding inline html comments, is characters 0-M of N in the content.
            Comparison removes formatting.
            All inline HTML is presumed to be comments (for now).
            Header is at the top level (e.g. heading level 1).
        """
        # Find the correct header
        template_heading = self.search_for_heading(wrapped_template, title_tag)
        if template_heading == {}:
            logger.error('Governed header tag provided but not found in the template - failing validation')
            return False
        candidate_heading = self.search_for_heading(wrapped_candidate, title_tag)
        if candidate_heading == {}:
            logger.error('Governed header tag provided but not found in the content - failing validation')
            return False
        template_lines = self.clean_content(template_heading)
        content_lines = self.clean_content(candidate_heading)
        if not len(template_lines) == len(content_lines):
            logger.error(
                'Governed heading has inconsistent number of content lines between the template and measured file.'
            )
            return False
        # Strict parsing
        for index in range(len(template_lines)):
            if not content_lines[index][0:len(template_lines[index])] == template_lines[index]:
                logger.warning('Mismatch in governed heading')
                logger.warning(f'Between template {template_lines[index]} and instance {content_lines[index]}')
                return False
        # Okay
        return True
