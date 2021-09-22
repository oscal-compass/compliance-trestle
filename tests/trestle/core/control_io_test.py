# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Tests for control_io module."""

import pathlib

import pytest

import trestle.oscal.catalog as cat
from trestle.core.control_io import ControlIo
from trestle.oscal import common

case_1 = 'indent_normal'
case_2 = 'indent jump back 2'
case_3 = 'indent end abrupt'
case_4 = 'no items'


@pytest.mark.parametrize('control_prose', [True, False])
@pytest.mark.parametrize('case', [case_1, case_2, case_3])
@pytest.mark.parametrize('additional_content', [True, False])
def test_read_write_controls(
    control_prose, case, additional_content, tmp_path: pathlib.Path, keep_cwd: pathlib.Path
) -> None:
    """Test read and write of controls via markdown."""
    dummy_title = 'dummy title'
    control = cat.Control(id='ac-1', title=dummy_title)
    statement_part = common.Part(id='ac-1_smt', name='statement')
    part_a = common.Part(id='ac-1_smt.a', name='item', prose='a prose')
    part_b = common.Part(id='ac-1_smt.b', name='item', prose='b prose')
    part_b1 = common.Part(id='ac-1_smt.b.1', name='item', prose='b.1 prose')
    part_b2 = common.Part(id='ac-1_smt.b.2', name='item', prose='b.2 prose')
    part_b2i = common.Part(id='ac-1_smt.b.2.i', name='item', prose='b.2.i prose')
    part_b3 = common.Part(id='ac-1_smt.b.3', name='item', prose='b.3 prose')
    part_c = common.Part(id='ac-1_smt.c', name='item', prose='c prose')

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

    control_io = ControlIo()
    control_io.write_control(tmp_path, control, '', None, None, additional_content)

    md_path = tmp_path / f'{control.id}.md'
    new_control = control_io.read_control(md_path)
    new_control.title = dummy_title
    assert len(new_control.parts) == 1
    assert control.parts[0].prose == new_control.parts[0].prose
    assert control.parts[0].parts == new_control.parts[0].parts
    assert control == new_control
