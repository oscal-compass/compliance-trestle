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
"""Tests for trestle custom jinja functionality."""

import pathlib
from datetime import date

from jinja2 import Environment, FileSystemLoader

import pytest

import trestle.core.jinja as tres_jinja
from trestle.core.markdown import markdown_const

JINJA_MD = 'jinja_markdown_include'


@pytest.mark.parametrize(
    'template, expected, expect_exception',
    [
        ('MDSection_include_top_level.jinja.md', 'MDSection_include_top_level.md', False),
        ('MDSection_include_top_level_adjusted.jinja.md', 'MDSection_include_top_level_adjusted.md', False),
        ('MDSection_include_nested.jinja.md', 'MDSection_include_nested.md', False),
        ('env_nested_c_c.jinja.md', 'env_nested_c_c.md', False),
        ('env_nested_c_n.jinja.md', 'env_nested_c_n.md', False), ('env_include.jinja.md', 'env_include.md', False),
        ('env_include_adjusted.jinja.md', 'env_include_adjusted.md', False),
        ('env_nested_c_c_double.jinja.md', 'env_nested_c_c_double.md', False)
    ]
)
def test_jinja_md(testdata_dir: pathlib.Path, template: str, expected: str, expect_exception: bool) -> None:
    """Test jinja markdown codes."""
    jinja_md_dir = testdata_dir / JINJA_MD
    jinja_env = Environment(
        loader=FileSystemLoader(jinja_md_dir), extensions=[tres_jinja.MDSectionInclude, tres_jinja.MDCleanInclude]
    )
    if expect_exception:
        with pytest.raises(Exception):
            _ = jinja_env.get_template(template)
        return
    template = jinja_env.get_template(template)
    output_str = template.render()
    expected_f = jinja_md_dir / expected
    expected_content = expected_f.open('r').read()
    assert output_str == expected_content


def test_jinja_datestamp_default(testdata_dir: pathlib.Path) -> None:
    """Test jinja datestamp generation, default case."""
    jinja_md_dir = testdata_dir / JINJA_MD
    jinja_env = Environment(loader=FileSystemLoader(jinja_md_dir), extensions=[tres_jinja.MDDatestamp])
    template = jinja_env.get_template('MDDatestamp_default.jinja.md')
    output_str = template.render()
    expected_content = date.today().strftime(markdown_const.JINJA_DATESTAMP_FORMAT) + '\n\n\n# Heading'
    assert output_str == expected_content


def test_jinja_datestamp_newline(testdata_dir: pathlib.Path) -> None:
    """Test jinja datestamp generation, with newline true and false."""
    jinja_md_dir = testdata_dir / JINJA_MD
    jinja_env = Environment(loader=FileSystemLoader(jinja_md_dir), extensions=[tres_jinja.MDDatestamp])
    template = jinja_env.get_template('MDDatestamp_newline.jinja.md')
    output_str = template.render()
    expected_content = date.today().strftime(markdown_const.JINJA_DATESTAMP_FORMAT) + date.today().strftime(
        markdown_const.JINJA_DATESTAMP_FORMAT
    ) + '\n\n\n# Heading'
    assert output_str == expected_content


def test_jinja_datestamp_format(testdata_dir: pathlib.Path) -> None:
    """Test jinja datestamp generation, with format string."""
    jinja_md_dir = testdata_dir / JINJA_MD
    jinja_env = Environment(loader=FileSystemLoader(jinja_md_dir), extensions=[tres_jinja.MDDatestamp])
    template = jinja_env.get_template('MDDatestamp_format.jinja.md')
    output_str = template.render()
    expected_content = date.today().strftime('%B %d, %Y') + '\n\n\n# Heading'
    assert output_str == expected_content


def test_jinja_datestamp_invalid(testdata_dir: pathlib.Path) -> None:
    """Test jinja datestamp generation, with format string."""
    jinja_md_dir = testdata_dir / JINJA_MD
    jinja_env = Environment(loader=FileSystemLoader(jinja_md_dir), extensions=[tres_jinja.MDDatestamp])
    with pytest.raises(Exception):
        _ = jinja_env.get_template('MDDatestamp_invalid.jinja.md')
