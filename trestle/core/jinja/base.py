# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2024 The OSCAL Compass Authors.
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
"""Trestle core.jinja base class."""
from jinja2 import lexer, nodes
from jinja2.environment import Environment
from jinja2.ext import Extension


class TrestleJinjaExtension(Extension):
    """Class to define common methods to be inherited from for use in trestle."""

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
