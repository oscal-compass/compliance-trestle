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
"""Functional tests of Jinja to understand role in trestle project."""
import pathlib

from jinja2 import Environment, FileSystemLoader

import pytest


def test_jinja_escapes(testdata_dir: pathlib.Path, tmp_empty_cwd: pathlib.Path) -> None:
    """Test that both quote types work with jinja."""
    jinja_test_dir = testdata_dir / 'jinja_l0'
    jinja_test_dir = jinja_test_dir.resolve()
    jinja_env = Environment(loader=FileSystemLoader(str(jinja_test_dir)))
    template = jinja_env.get_template('template_quotes.md.jinja')
    _ = template.render()


def test_jinja_discoverying_imports_nested_dirs(testdata_dir: pathlib.Path, tmp_empty_cwd: pathlib.Path) -> None:
    """Test that jinja FileSystemLoader can find nexted file."""
    jinja_test_dir = testdata_dir / 'jinja_l0'
    jinja_test_dir = jinja_test_dir.resolve()
    jinja_env = Environment(loader=FileSystemLoader(str(jinja_test_dir)))
    template = jinja_env.get_template('template_include_nested_dirs.md.jinja')
    _ = template.render()


def test_jinja_parent_include(testdata_dir: pathlib.Path, tmp_empty_cwd: pathlib.Path) -> None:
    """Demonstrate that jinja scope is limited to sub directories."""
    with pytest.raises(Exception):
        jinja_test_dir = testdata_dir / 'jinja_l0' / 'jinja_l1'
        jinja_test_dir = jinja_test_dir.resolve()
        jinja_env = Environment(loader=FileSystemLoader(str(jinja_test_dir)))
        template = jinja_env.get_template('template_import_parent.md.jinja')
        _ = template.render()


def test_where_are_imports_relative_to(testdata_dir: pathlib.Path, tmp_empty_cwd: pathlib.Path) -> None:
    """All imports are relative to the environment directory."""
    jinja_test_dir = testdata_dir / 'jinja_l0'
    jinja_test_dir = jinja_test_dir.resolve()
    jinja_env = Environment(loader=FileSystemLoader(str(jinja_test_dir)))
    template = jinja_env.get_template('jinja_l1/template_import_parent.md.jinja')
    _ = template.render()


def test_nested_import(testdata_dir: pathlib.Path, tmp_empty_cwd: pathlib.Path) -> None:
    """Demonstrate nested import within a flat directory structure."""
    jinja_test_dir = testdata_dir / 'jinja_l0'
    jinja_test_dir = jinja_test_dir.resolve()
    jinja_env = Environment(loader=FileSystemLoader(str(jinja_test_dir)))
    template = jinja_env.get_template('template_nest_outer.md')
    _ = template.render()
