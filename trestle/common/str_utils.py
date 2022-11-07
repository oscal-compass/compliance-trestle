# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Trestle String Utils."""
import enum
import string
from typing import Any, Optional


class AliasMode(enum.Enum):
    """
    Allowed formats for classname alias.

    Currently there are only two.  If others are added, check they get handled properly in the code.
    """

    JSON = 1
    FIELD = 2


def _camel_to_snake(camel: str) -> str:
    """Convert camel case to snake."""
    if not camel:
        return camel
    snake = camel[0].lower()
    for c in camel[1:]:
        if c.isupper():
            snake = snake + '_'
        snake = snake + c.lower()
    return snake


def _snake_to_upper_camel(snake: str) -> str:
    """Convert snake to upper camel, ignoring start/end underscores."""
    if not snake:
        return snake
    snake = snake.lower()
    camel = ''
    lift = True
    for s in snake:
        if s == '_':
            lift = True
            continue
        if lift:
            camel = camel + s.upper()
            lift = False
        else:
            camel = camel + s
    return camel


def spaces_and_caps_to_snake(spaced_str: str) -> str:
    """Convert caps and spaces to snake."""
    underscored = '_'.join(spaced_str.strip().split())
    return underscored.lower()


def spaces_and_caps_to_lower_single_spaces(spaced_str: str) -> str:
    """Convert caps and duplicate spaces to lower with single spaces."""
    single_space = ' '.join(spaced_str.strip().split())
    return single_space.lower()


def classname_to_alias(classname: str, mode: AliasMode) -> str:
    """
    Return oscal key name or field element name based on class name.

    This is applicable when asking for a singular element.
    """
    suffix = classname.split('.')[-1]

    # the alias mode is either json or field - yaml doesn't apply here
    if mode == AliasMode.JSON:
        # things like class_ should just be class
        if suffix[-1] == '_':
            suffix = suffix[:-1]
        return _camel_to_dash(suffix).rstrip(string.digits)
    # else alias mode is field
    return _camel_to_snake(suffix).rstrip(string.digits)


def alias_to_classname(alias: str, mode: AliasMode) -> str:
    """
    Return class name based dashed or snake alias.

    This is applicable creating dynamic wrapper model for a list or dict field.
    """
    if mode == AliasMode.JSON:
        return _snake_to_upper_camel(alias.replace('-', '_'))
    return _snake_to_upper_camel(alias)


def _camel_to_dash(name: str) -> str:
    """Convert camelcase to dashcase."""
    return _camel_to_snake(name).replace('_', '-')


def dash_to_underscore(name: str) -> str:
    """Convert dash to underscore."""
    return name.replace('-', '_')


def underscore_to_dash(name: str) -> str:
    """Convert underscore to dash and drop final dash if present."""
    converted = name.replace('_', '-')
    return converted if converted[-1] != '-' else converted[:-1]


def as_string(string_or_none: Optional[str]) -> str:
    """Convert string or None to itself or empty string."""
    return string_or_none if string_or_none else ''


def string_from_root(item_with_root: Optional[Any]) -> str:
    """Convert root to string if present."""
    return as_string(item_with_root.__root__) if item_with_root else ''


def strip_lower_equals(str_a: Optional[str], str_b: Optional[str]) -> bool:
    """
    Safe test of lower string equality allowing Nones.

    If either argument is None the result is False because the intent is to report if they are equal as actual strings.
    """
    if str_a is None or str_b is None:
        return False
    return str_a.strip().lower() == str_b.strip().lower()
