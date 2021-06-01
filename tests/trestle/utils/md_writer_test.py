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
"""Tests for md_writer module."""

from trestle.utils.md_writer import MDWriter


def test_md_writer() -> None:
    """Test md_writer."""
    md_file = '/tmp/test.md'
    md_writer = MDWriter(md_file)
    md_writer.new_paragraph()
    md_writer.new_header(level=2, title='Control description')
    md_writer.set_indent_level(-2)
    items = ['The organization', ['a thing', ['1. thing', '2. thing']], ['b thing', ['1. things', '2. things']]]
    md_writer.new_list(items)
    md_writer.new_paragraph()
    md_writer.write_out()
    assert True
