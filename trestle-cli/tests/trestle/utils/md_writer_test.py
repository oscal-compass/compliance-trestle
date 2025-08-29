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
"""Tests for md_writer module."""

import pathlib

from tests.test_utils import confirm_text_in_file

from trestle.core.markdown.md_writer import MDWriter


def test_md_writer(tmp_path: pathlib.Path) -> None:
    """Test md_writer."""
    md_file = tmp_path / 'md_file.md'
    md_writer = MDWriter(md_file)
    md_writer.set_indent_step_size(2)
    md_writer.new_paragraph()
    md_writer.new_header(level=2, title='Control Statement')
    md_writer.set_indent_level(-2)
    items = [
        'The organization', ['a thing', ['1. thing', '2. thing']], ['b thing'], ['c thing', ['1. things', '2. things']],
        ['d thing']
    ]
    md_writer.new_list(items)
    md_writer.new_paragraph()
    md_writer.new_hr()
    md_writer.new_line('my line')
    header = {'a': 1, 'b': {'x': 2, 'y': 3}, 'c': 4}
    md_writer.add_yaml_header(header)
    md_writer.new_paragraph()
    md_writer.write_out()

    desired_result = """---
a: 1
b:
  x: 2
  y: 3
c: 4
---

## Control Statement

- The organization

- a thing

  - 1. thing
  - 2. thing

- b thing

- c thing

  - 1. things
  - 2. things

- d thing

______________________________________________________________________

my line
"""

    with open(md_file) as f:
        md_result = f.read()
    assert desired_result == md_result


def test_cull_headings(testdata_dir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Test culling of headings from md tree."""
    markdown_file = testdata_dir / 'markdown/valid_complex_md.md'
    strict_cull_list = ['## 1.2 MD Subheader 1.2', '### 1.3.1 Valid header <!-- ### some comment here -->']
    # make sure the headers are present in the original
    for item in strict_cull_list:
        assert confirm_text_in_file(markdown_file, '', item)
    strict_path = tmp_path / 'strict.md'
    md_writer = MDWriter(strict_path)
    md_writer.cull_headings(markdown_file, strict_cull_list, True)
    # make sure headers are gone now
    for item in strict_cull_list:
        assert not confirm_text_in_file(strict_path, '', item)
    non_strict_path = tmp_path / 'non_strict.md'
    md_writer = MDWriter(non_strict_path)
    non_strict_cull_list = ['Subheader', 'Header']
    md_writer.cull_headings(markdown_file, non_strict_cull_list, False)
    for item in strict_cull_list:
        assert not confirm_text_in_file(non_strict_path, '', item)
    ignore_path = tmp_path / 'ignore.md'
    md_writer = MDWriter(ignore_path)
    ignore_list = ['IgnoreIt']
    md_writer.cull_headings(markdown_file, ignore_list, False)
    for letter in 'ABCDEFG':
        assert confirm_text_in_file(ignore_path, '', f'IgnoreIt {letter}')
