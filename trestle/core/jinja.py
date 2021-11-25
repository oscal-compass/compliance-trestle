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
"""Trestle utilities to customize ."""
import logging
import re
import typing as t

import frontmatter

from jinja2 import lexer
from jinja2.environment import Environment
from jinja2.ext import Extension
from jinja2.parser import Parser

from trestle.core import err
from trestle.core.markdown import markdown_node

logger = logging.getLogger(__name__)


class OSCALTags(Extension):
    """
    This adds a pre-proccessing step to eliminate badly behaving OSCAL statements.

    Currently covering:
    {{ insert: param, param_id }} -> {{ param_id }}
    """

    priority = 1

    def preprocess(self, source: str, name: t.Optional[str], filename: t.Optional[str] = None) -> str:
        """Preprocess files with jinja eliminating OSCAL substitution structures."""
        staches = re.findall(r'{{.*?}}', source)
        if not staches:
            return source
        new_staches = []
        # clean the staches so they just have the param text
        for stache in staches:
            stache = stache.replace('insert: param,', '').strip()
            new_staches.append(stache)
        for i, _ in enumerate(staches):
            source = source.replace(staches[i], new_staches[i], 1)
        return source


class MDSectionInclude(Extension):
    """Inject the parameter of the tag as the resulting content."""

    tags = {'mdsection_include'}

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    def parse(self, parser):
        """Execute parsing of md token and return nodes."""
        kwargs = None
        while parser.stream.current.type != lexer.TOKEN_BLOCK_END:
            token = parser.stream.current
            if token.test('name:mdsection_include'):
                parser.stream.expect(lexer.TOKEN_NAME)
                markdown_source = parser.stream.expect(lexer.TOKEN_STRING)
                section_title = parser.stream.expect(lexer.TOKEN_STRING)
            elif kwargs is not None:
                kwargs.append(self.parse_expression(parser))
            elif parser.stream.look().type == lexer.TOKEN_ASSIGN:
                kwargs = {}
        # Use the established environment to source the file
        md_content, _, _ = self.environment.loader.get_source(self.environment, markdown_source.value)
        fm = frontmatter.loads(md_content)
        if not fm.metadata == {}:
            logger.warning('Non zero metadata on MD section include - ignoring')
        full_md = markdown_node.MarkdownNode.build_tree_from_markdown(fm.content.split('\n'))
        md_section = full_md.get_node_for_key(section_title.value, strict_matching=True)
        if not md_section:
            raise err.TrestleError(
                f'Unable to retrieve section "{section_title.value}"" from {markdown_source.value} jinja template.'
            )
        local_parser = Parser(self.environment, md_section.content.raw_text)
        top_level_output = local_parser.parse()

        return top_level_output.body


class MDCleanInclude(Extension):
    """Inject the parameter of the tag as the resulting content."""

    tags = {'md_clean_include'}

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    def parse(self, parser):
        """Execute parsing of md token and return nodes."""
        parser.stream.expect('name:md_clean_include')
        component = parser.parse_expression()
        # Use the established environment to source the file
        md_content, _, _ = self.environment.loader.get_source(self.environment, component.value)
        fm = frontmatter.loads(md_content)
        local_parser = Parser(self.environment, fm.content)
        top_level_output = local_parser.parse()

        return top_level_output.body
