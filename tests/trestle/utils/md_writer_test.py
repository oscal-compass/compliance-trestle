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
