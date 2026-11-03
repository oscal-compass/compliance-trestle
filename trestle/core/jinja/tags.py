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
"""Trestle utilities to customize jinja tags."""

import logging
from datetime import date
from typing import List

import frontmatter

from jinja2 import lexer, nodes
from jinja2.environment import Environment
from jinja2.parser import Parser
from jinja2.sandbox import SandboxedEnvironment

from trestle.common import err
from trestle.core.jinja.base import TrestleJinjaExtension
from trestle.core.markdown import docs_markdown_node, markdown_const

logger = logging.getLogger(__name__)


def adjust_heading_level(input_md: str, expected: int) -> str:
    """Adjust the header level of a markdown string such that the most significant header matches the expected #'s."""
    output_md = input_md
    mdn = docs_markdown_node.DocsMarkdownNode.build_tree_from_markdown(input_md.split('\n'))
    if mdn.subnodes:
        mdn_top_heading = mdn.subnodes[0].get_node_header_lvl()
        delta = int(expected) - mdn_top_heading
        if not delta == 0:
            mdn.change_header_level_by(delta)
            output_md = mdn.content.raw_text
    return output_md


def _parse_included_markdown(parse_env: Environment, content: str, source: str) -> List[nodes.Node]:
    """Parse included markdown as a template, permitting only literal text and {{ }} expressions.

    Included markdown may originate from untrusted data (e.g. OSCAL prose written to markdown), and a sandboxed
    environment still permits statement tags such as include, for and nested trestle include tags.  Those allow
    arbitrary in-tree file disclosure and output amplification, so any statement tag in included content is rejected.
    This is checked on the raw token stream because a nested include tag would otherwise expand into plain output nodes.
    Statement tags remain available to the (trusted) top level template.
    """
    for lineno, token_type, _ in parse_env.lex(content):
        if token_type == lexer.TOKEN_BLOCK_BEGIN:
            raise err.TrestleError(
                f'Statement tag "{{% ... %}}" found at line {lineno} of included markdown "{source}". '
                'Statement tags (include, for, nested md_clean_include, etc.) are not permitted in included '
                'markdown; use them in the top level template instead.'
            )
    return Parser(parse_env, content).parse().body


class MDSectionInclude(TrestleJinjaExtension):
    """Inject the parameter of the tag as the resulting content."""

    tags = {'mdsection_include'}

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    def parse(self, parser):
        """Execute parsing of md token and return nodes.

        Security Note: This method re-parses included markdown content using a
        SandboxedEnvironment to prevent Server-Side Template Injection (SSTI) attacks.
        The sandbox restricts access to unsafe Python attributes, preventing arbitrary
        code execution even if untrusted OSCAL data contains Jinja syntax.
        """
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
        full_md = docs_markdown_node.DocsMarkdownNode.build_tree_from_markdown(fm.content.split('\n'))
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

        # SECURITY FIX: Use sandboxed environment for re-parsing to prevent SSTI
        # Create a sandboxed environment if the current one isn't already sandboxed
        parse_env = self.environment
        if not isinstance(self.environment, SandboxedEnvironment):
            parse_env = SandboxedEnvironment(
                loader=self.environment.loader,
                extensions=self.environment.extensions,
                trim_blocks=self.environment.trim_blocks,
                autoescape=self.environment.autoescape,
            )

        return _parse_included_markdown(parse_env, md_section.content.raw_text, markdown_source.value)


class MDCleanInclude(TrestleJinjaExtension):
    """Inject the parameter of the tag as the resulting content."""

    tags = {'md_clean_include'}

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    def parse(self, parser):
        """Execute parsing of md token and return nodes.

        Security Note: This method re-parses included markdown content using a
        SandboxedEnvironment to prevent Server-Side Template Injection (SSTI) attacks.
        The sandbox restricts access to unsafe Python attributes, preventing arbitrary
        code execution even if untrusted OSCAL data contains Jinja syntax.
        """
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

        # SECURITY FIX: Use sandboxed environment for re-parsing to prevent SSTI
        # Create a sandboxed environment if the current one isn't already sandboxed
        parse_env = self.environment
        if not isinstance(self.environment, SandboxedEnvironment):
            parse_env = SandboxedEnvironment(
                loader=self.environment.loader,
                extensions=self.environment.extensions,
                trim_blocks=self.environment.trim_blocks,
                autoescape=self.environment.autoescape,
            )

        return _parse_included_markdown(parse_env, content, markdown_source.value)


class MDDatestamp(TrestleJinjaExtension):
    """Inject the parameter of the tag as the resulting content."""

    tags = {'md_datestamp'}

    def __init__(self, environment: Environment) -> None:
        """Ensure enviroment is set and carried into class vars."""
        super().__init__(environment)

    def parse(self, parser):
        """Execute parsing of md token and return nodes.

        Security Note: This method re-parses the datestamp using a SandboxedEnvironment
        to prevent potential SSTI attacks, though the risk is minimal for date strings.
        """
        kwargs = None
        count = 0
        while parser.stream.current.type != lexer.TOKEN_BLOCK_END:
            count = count + 1
            token = parser.stream.current
            if count > self.max_tag_parse:
                raise err.TrestleError(f'Unexpected Jinja tag structure provided at token {token.value}')
            if token.test('name:md_datestamp'):
                parser.stream.expect(lexer.TOKEN_NAME)
            elif kwargs is not None:
                arg = token.value
                next(parser.stream)
                parser.stream.expect(lexer.TOKEN_ASSIGN)
                token = parser.stream.current
                exp = self.parse_expression(parser)
                kwargs[arg] = exp.value
            else:
                if parser.stream.look().type == lexer.TOKEN_ASSIGN or parser.stream.look().type == lexer.TOKEN_STRING:
                    kwargs = {}
                continue

        if kwargs is not None:
            if 'format' in kwargs and isinstance(kwargs['format'], str):
                date_string = date.today().strftime(kwargs['format'])
            else:
                date_string = date.today().strftime(markdown_const.JINJA_DATESTAMP_FORMAT)
            if 'newline' in kwargs and kwargs['newline'] is False:
                pass
            else:
                date_string += '\n\n'
        else:
            date_string = date.today().strftime(markdown_const.JINJA_DATESTAMP_FORMAT) + '\n\n'

        # SECURITY FIX: Use sandboxed environment for re-parsing to prevent SSTI
        # Create a sandboxed environment if the current one isn't already sandboxed
        parse_env = self.environment
        if not isinstance(self.environment, SandboxedEnvironment):
            parse_env = SandboxedEnvironment(
                loader=self.environment.loader,
                extensions=self.environment.extensions,
                trim_blocks=self.environment.trim_blocks,
                autoescape=self.environment.autoescape,
            )

        local_parser = Parser(parse_env, date_string)
        datestamp_output = local_parser.parse()

        return datestamp_output.body
