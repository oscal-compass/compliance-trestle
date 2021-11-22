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
"""Tests for control_io module."""

import pathlib

import pytest

import tests.test_utils as test_utils

import trestle.oscal.catalog as cat
from trestle.core.control_io import ControlIOReader, ControlIOWriter
from trestle.core.err import TrestleError
from trestle.oscal import common

case_1 = 'indent_normal'
case_2 = 'indent jump back 2'
case_3 = 'indent end abrupt'
case_4 = 'no items'

control_text = """# xy-9 - \[XY\] Fancy Control

## Control Statement

The org:

- \[a\] Creates:

  - \[1\] Good stuff; and
  - \[2\] Other good stuff; and

- \[b\] Checks for:

  - \[1\] Quality of the stuff; and
  - \[2\] Confirms all is good.

## Control Objective

Confirm the org:

- \[a_obj\]

  - \[1_obj\]

    - \[1\] stays focused on:

      - \[a\] weather;
      - \[b\] comfort;
      - \[c\] heart rate;

    - \[2\] makes sure all are well-behaved;
    - \[3\] keeps them up to date;

  - \[2_obj\]

    - \[1\] facilitates ease of consumption;
    - \[2\] establishes dietary requirements;

- \[b_obj\]

  - \[1_obj\]

    - \[1\] sets times for meals;
    - \[2\] confirms adequate calorie intake;

  - \[2_obj\]

    - \[1\] serves dessert; and
    - \[2\] keeps the wine list up to date.

## Control guidance

This is a fancy control and should be used with care.
"""


@pytest.mark.parametrize('sections', [True, False])
@pytest.mark.parametrize('control_prose', [True, False])
@pytest.mark.parametrize('case', [case_1, case_2, case_3])
@pytest.mark.parametrize('additional_content', [True, False])
def test_read_write_controls(
    sections, control_prose, case, additional_content, tmp_path: pathlib.Path, keep_cwd: pathlib.Path
) -> None:
    """Test read and write of controls via markdown."""
    dummy_title = 'dummy title'
    control = cat.Control(id='ac-1', title=dummy_title)
    statement_part = common.Part(id='ac-1_smt', name='statement')
    prop = common.Property(name='label', value='a')
    part_a = common.Part(id='ac-1_smt.a', name='item', prose='a prose', props=[prop])
    prop.value = 'b'
    part_b = common.Part(id='ac-1_smt.b', name='item', prose='b prose', props=[prop])
    prop.value = '1'
    part_b1 = common.Part(id='ac-1_smt.b.1', name='item', prose='b.1 prose', props=[prop])
    prop.value = '2'
    part_b2 = common.Part(id='ac-1_smt.b.2', name='item', prose='b.2 prose', props=[prop])
    prop.value = 'i'
    part_b2i = common.Part(id='ac-1_smt.b.2.i', name='item', prose='b.2.i prose', props=[prop])
    prop.value = '3'
    part_b3 = common.Part(id='ac-1_smt.b.3', name='item', prose='b.3 prose', props=[prop])
    prop.value = 'c'
    part_c = common.Part(id='ac-1_smt.c', name='item', prose='c prose', props=[prop])
    sec_1_text = """
General comment
on separate lines

### header line

- \[a\] list 1
- \[b\] list 2
    - \[1\] sublist 1
    - \[2\] sublist 2

end of text
"""

    sec_2_text = 'Simple line of prose'
    sec_1 = common.Part(id='ac-1_smt.guidance', name='guidance', prose=sec_1_text.strip('\n'))
    sec_2 = common.Part(id='ac-1_smt.extra', name='extra', prose=sec_2_text.strip('\n'))

    if control_prose:
        statement_part.prose = 'ac-1_smt prose'

    if case == case_1:
        part_b2.parts = [part_b2i]
        part_b.parts = [part_b1, part_b2, part_b3]
        parts = [part_a, part_b, part_c]
    elif case == case_2:
        part_b2.parts = [part_b2i]
        part_b.parts = [part_b1, part_b2]
        parts = [part_a, part_b, part_c]
    elif case == case_3:
        part_b2.parts = [part_b2i]
        part_b.parts = [part_b1, part_b2]
        parts = [part_a, part_b]
    else:
        parts = None

    statement_part.parts = parts
    control.parts = [statement_part]
    if sections:
        control.parts.extend([sec_1, sec_2])

    writer = ControlIOWriter()
    writer.write_control(tmp_path, control, '', None, None, additional_content, False, None, False)

    md_path = tmp_path / f'{control.id}.md'
    reader = ControlIOReader()
    new_control = reader.read_control(md_path)
    new_control.title = dummy_title
    assert len(new_control.parts) == len(control.parts)
    assert control.parts[0].prose == new_control.parts[0].prose
    assert control.parts[0].parts == new_control.parts[0].parts
    assert control == new_control


def test_control_objective(tmp_path: pathlib.Path) -> None:
    """Test read and write of control with objective."""
    # write the control directly as raw markdown text
    md_path = tmp_path / 'xy-9.md'
    with open(md_path, 'w') as f:
        f.write(control_text)
    # read it in as markdown to an OSCAL control in memory
    control = ControlIOReader.read_control(md_path)
    sub_dir = tmp_path / 'sub_dir'
    sub_dir.mkdir(exist_ok=True)
    # write it out as markdown in a separate directory to avoid name clash
    control_writer = ControlIOWriter()
    control_writer.write_control(sub_dir, control, 'XY', None, None, False, False, None, False)
    # confirm the newly written markdown text is identical to what was read originally
    assert test_utils.text_files_equal(md_path, sub_dir / 'xy-9.md')


def test_read_control_no_label(testdata_dir: pathlib.Path) -> None:
    """Test reading a control that doesn't have a part label in statement."""
    md_file = testdata_dir / 'author/controls/control_no_labels.md'
    control = ControlIOReader.read_control(md_file)
    assert control.parts[0].parts[2].props[0].value == 'c'
    assert control.parts[0].parts[2].parts[0].props[0].value == '1'
    md_file = testdata_dir / 'author/controls/control_some_labels.md'
    control = ControlIOReader.read_control(md_file)
    assert control.parts[0].parts[2].props[0].value == 'aa'
    assert control.parts[0].parts[2].parts[1].props[0].value == 'abc13'
    assert control.parts[0].parts[3].props[0].value == 'ab'


@pytest.mark.parametrize(
    ['prev_label', 'bumped_label'],
    [['', 'a'], ['a', 'b'], ['z', 'aa'], ['aa', 'ab'], ['9', '10'], ['99', '100'], ['zz', 'aaa']]
)
def test_bump_label(prev_label, bumped_label) -> None:
    """Test bumping of label strings."""
    assert ControlIOReader._bump_label(prev_label) == bumped_label


@pytest.mark.parametrize(
    ['prev_label', 'next_label', 'indent'], [
        ['', 'a', 0],
        ['', '1', 2],
        ['1z', '1aa', 0],
        ['1a9', '1a10', 0],
        ['a_4.99', 'a_4.100', 0],
    ]
)
def test_create_next_label(prev_label, next_label, indent) -> None:
    """Test bumping of label strings."""
    assert ControlIOReader._create_next_label(prev_label, indent) == next_label


def test_control_failures(tmp_path: pathlib.Path) -> None:
    """Test various failure modes."""
    part = common.Part(name='foo')
    assert ControlIOWriter._get_label(part) == ''

    assert ControlIOReader._strip_to_make_ncname('1a@foo') == 'afoo'
    with pytest.raises(TrestleError):
        ControlIOReader._strip_to_make_ncname('1@')

    with pytest.raises(TrestleError):
        ControlIOReader._indent('')

    with pytest.raises(TrestleError):
        ControlIOReader._indent('  foo')


def test_bad_unicode_in_file(tmp_path: pathlib.Path) -> None:
    """Test error on read of bad unicode in control markdown."""
    bad_file = tmp_path / 'bad_unicode.md'
    with open(bad_file, 'wb') as f:
        f.write(b'\x81')
    with pytest.raises(TrestleError):
        ControlIOReader._load_control_lines(bad_file)


def test_broken_yaml_header(testdata_dir: pathlib.Path) -> None:
    """Test for a bad markdown header."""
    bad_file = testdata_dir / 'author' / 'bad_md_header.md'
    with pytest.raises(TrestleError):
        ControlIOReader._load_control_lines(bad_file)


def test_merge_dicts_deep() -> None:
    """Test deep merge of dicts."""
    dest = {'a': {'b': 1}, 'x': [5, 6], 'q': 99}
    src = {'a': {'b': [2, 3]}, 'x': 7, 'z': 'foo', 'q': 88}
    ControlIOWriter.merge_dicts_deep(dest, src)
    assert dest['a'] == {'b': [1, 2, 3]}
    assert dest['x'] == [5, 6, 7]
    assert dest['z'] == 'foo'
    assert dest['q'] == 99


def test_read_label_prose_failures(tmp_path: pathlib.Path) -> None:
    """Test read_label_prose failures."""
    lines = ['', '## Implementation my_label', 'bad line']
    with pytest.raises(TrestleError):
        ControlIOReader._read_label_prose(1, lines)

    bad_header = ['', '# bad header']
    with pytest.raises(TrestleError):
        ControlIOReader._read_label_prose(1, bad_header)

    no_label = ['', '## Implementation']
    with pytest.raises(TrestleError):
        ControlIOReader._read_label_prose(1, no_label)


def test_read_label_prose_special_cases(tmp_path: pathlib.Path) -> None:
    """Test special cases for read label prose."""
    added_text = """
# What is the solution and how is it implemented?

Top level description text

"""
    full_control_text = control_text + added_text
    lines = full_control_text.split('\n')
    _, label, prose_lines = ControlIOReader._read_label_prose(0, lines)
    assert label == 'top_level_description'
    assert prose_lines[0] == 'Top level description text'
