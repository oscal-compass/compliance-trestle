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

import frontmatter

from jinja2 import lexer, nodes
from jinja2.environment import Environment
from jinja2.ext import Extension
from jinja2.parser import Parser

from trestle.core import err
from trestle.core.markdown import markdown_node

logger = logging.getLogger(__name__)


def adjust_heading_level(input_md: str, expected: int) -> str:
    """Adjust the header level of a markdown string such that the most significant header matches the expected #'s."""
    output_md = input_md
    mdn = markdown_node.MarkdownNode.build_tree_from_markdown(input_md.split('\n'))
    if mdn.subnodes:
        mdn_top_heading = mdn.subnodes[0].get_node_header_lvl()
        delta = int(expected) - mdn_top_heading
        if not delta == 0:
            mdn.change_header_level_by(delta)
            output_md = mdn.content.raw_text
    return output_md


class TrestleJinjaExtension(Extension):
    """Class to define common methods to be inherited from for use in trestle."""

    # This
    max_tag_parse = 20

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    @staticmethod
    def parse_expression(parser):
        """Safely parse jinja expression."""
        # Licensed under MIT from:
        # https://github.com/MoritzS/jinja2-django-tags/blob/master/jdj_tags/extensions.py#L424
        # Due to how the jinja2 parser works, it treats "foo" "bar" as a single
        # string literal as it is the case in python.
        # But the url tag in django supports multiple string arguments, e.g.
        # "{% url 'my_view' 'arg1' 'arg2' %}".
        # That's why we have to check if it's a string literal first.
        token = parser.stream.current
        if token.test(lexer.TOKEN_STRING):
            expr = nodes.Const(token.value, lineno=token.lineno)
            next(parser.stream)
        else:
            expr = parser.parse_expression(False)

        return expr


class MDSectionInclude(TrestleJinjaExtension):
    """Inject the parameter of the tag as the resulting content."""

    tags = {'mdsection_include'}

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    def parse(self, parser):
        """Execute parsing of md token and return nodes."""
        kwargs = None
        expected_heading_level = None
        count = 0
        while parser.stream.current.type != lexer.TOKEN_BLOCK_END:
            count = count + 1
            if count > self.max_tag_parse:
                raise err.TrestleError('Unexpected Jinja tag structure provided, please review docs.')
            token = parser.stream.current
            if token.test('name:mdsection_include'):
                parser.stream.expect(lexer.TOKEN_NAME)
                markdown_source = parser.stream.expect(lexer.TOKEN_STRING)
                section_title = parser.stream.expect(lexer.TOKEN_STRING)
            elif kwargs is not None:
                arg = token.value
                next(parser.stream)
                parser.stream.expect(lexer.TOKEN_ASSIGN)
                token = parser.stream.current
                exp = self.parse_expression(parser)
                kwargs[arg] = exp.value
            else:
                if parser.stream.look().type == lexer.TOKEN_ASSIGN:
                    kwargs = {}
                continue
        # Use the established environment to source the file
        md_content, _, _ = self.environment.loader.get_source(self.environment, markdown_source.value)
        fm = frontmatter.loads(md_content)
        if not fm.metadata == {}:
            logger.warning('Non zero metadata on MD section include - ignoring')
        full_md = markdown_node.MarkdownNode.build_tree_from_markdown(fm.content.split('\n'))
        md_section = full_md.get_node_for_key(section_title.value, strict_matching=True)
        # adjust
        if kwargs is not None:
            expected_heading_level = kwargs.get('heading_level')
        if expected_heading_level is not None:
            level = md_section.get_node_header_lvl()
            delta = int(expected_heading_level) - level
            if not delta == 0:
                md_section.change_header_level_by(delta)
        if not md_section:
            raise err.TrestleError(
                f'Unable to retrieve section "{section_title.value}"" from {markdown_source.value} jinja template.'
            )
        local_parser = Parser(self.environment, md_section.content.raw_text)
        top_level_output = local_parser.parse()

        return top_level_output.body


class MDCleanInclude(TrestleJinjaExtension):
    """Inject the parameter of the tag as the resulting content."""

    tags = {'md_clean_include'}

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    def parse(self, parser):
        """Execute parsing of md token and return nodes."""
        kwargs = None
        expected_heading_level = None
        count = 0
        while parser.stream.current.type != lexer.TOKEN_BLOCK_END:
            count = count + 1
            if count > self.max_tag_parse:
                raise err.TrestleError('Unexpected Jinja tag structure provided, please review docs.')
            token = parser.stream.current
            if token.test('name:md_clean_include'):
                parser.stream.expect(lexer.TOKEN_NAME)
                markdown_source = parser.stream.expect(lexer.TOKEN_STRING)
            elif kwargs is not None:
                arg = token.value
                next(parser.stream)
                parser.stream.expect(lexer.TOKEN_ASSIGN)
                token = parser.stream.current
                exp = self.parse_expression(parser)
                kwargs[arg] = exp.value
            else:
                if parser.stream.look().type == lexer.TOKEN_ASSIGN:
                    kwargs = {}
                continue
        md_content, _, _ = self.environment.loader.get_source(self.environment, markdown_source.value)
        fm = frontmatter.loads(md_content)
        content = fm.content
        content += '\n\n'
        if kwargs is not None:
            expected_heading_level = kwargs.get('heading_level')
        if expected_heading_level is not None:
            content = adjust_heading_level(content, expected_heading_level)

        local_parser = Parser(self.environment, content)
        top_level_output = local_parser.parse()

        return top_level_output.body
