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
import shutil

import pytest

import tests.test_utils as test_utils

import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.common import const
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.control_io import ControlIOReader, ControlIOWriter, ParameterRep
from trestle.core.markdown.markdown_processor import MarkdownProcessor
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal import common

case_1 = 'indent_normal'
case_2 = 'indent jump back 2'
case_3 = 'indent end abrupt'
case_4 = 'no items'

control_text = """---
sort-id: xy-09
---

# xy-9 - \[My Group Title\] Fancy Control

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
    control = cat.Control(id='ac-1', title=dummy_title, props=[common.Property(name=const.SORT_ID, value='ac-01')])
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
    sec_1 = common.Part(id='ac-1_gdn', name='guidance', prose=sec_1_text.strip('\n'))
    sec_2 = common.Part(id='ac-1_extra', name='extra', prose=sec_2_text.strip('\n'))

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
    writer.write_control_for_editing(
        tmp_path, control, 'My Group Title', None, None, additional_content, False, None, False, None, None
    )

    md_path = tmp_path / f'{control.id}.md'
    reader = ControlIOReader()
    new_control, group_title = reader.read_control(md_path, False)
    new_control.title = dummy_title
    assert group_title == 'My Group Title'
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
    control, group_title = ControlIOReader.read_control(md_path, True)
    assert group_title == 'My Group Title'
    sub_dir = tmp_path / 'sub_dir'
    sub_dir.mkdir(exist_ok=True)
    # write it out as markdown in a separate directory to avoid name clash
    control_writer = ControlIOWriter()
    control_writer.write_control_for_editing(
        sub_dir, control, 'My Group Title', None, None, False, False, None, False, None, None
    )
    # confirm the newly written markdown text is identical to what was read originally
    assert test_utils.text_files_equal(md_path, sub_dir / 'xy-9.md')


def test_read_control_no_label(testdata_dir: pathlib.Path) -> None:
    """Test reading a control that doesn't have a part label in statement."""
    md_file = testdata_dir / 'author/controls/control_no_labels.md'
    control, group_title = ControlIOReader.read_control(md_file, True)
    assert group_title == 'My Group Title'
    assert control.parts[0].parts[2].props[0].value == 'c'
    assert control.parts[0].parts[2].parts[0].props[0].value == '1'
    md_file = testdata_dir / 'author/controls/control_some_labels.md'
    control, group_title = ControlIOReader.read_control(md_file, True)
    assert group_title == 'My Group Title'
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
    assert ControlIOWriter.get_label(part) == ''

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
        ControlIOReader._load_control_lines_and_header(bad_file)


def test_broken_yaml_header(testdata_dir: pathlib.Path) -> None:
    """Test for a bad markdown header."""
    bad_file = testdata_dir / 'author' / 'bad_md_header.md'
    with pytest.raises(TrestleError):
        ControlIOReader._load_control_lines_and_header(bad_file)


@pytest.mark.parametrize('overwrite_header_values', [True, False])
def test_merge_dicts_deep(overwrite_header_values) -> None:
    """Test deep merge of dicts."""
    dest = {'trestle': {'foo': {'hello': 1}}, 'fedramp': {'roles': [5, 6], 'values': 8}, 'orig': 11}
    src = {'trestle': {'foo': {'hello': 3}, 'bar': 4}, 'fedramp': {'roles': 7, 'values': 10}, 'extra': 12}
    ControlIOWriter.merge_dicts_deep(dest, src, overwrite_header_values)
    if not overwrite_header_values:
        assert dest['trestle'] == {'foo': {'hello': 1}, 'bar': 4}
        assert dest['fedramp'] == {'roles': [5, 6], 'values': 8}
        assert dest['orig'] == 11
        assert dest['extra'] == 12
    else:
        assert dest['trestle'] == {'foo': {'hello': 3}, 'bar': 4}
        assert dest['fedramp'] == {'roles': 7, 'values': 10}
        assert dest['orig'] == 11
        assert dest['extra'] == 12


def test_merge_dicts_deep_empty() -> None:
    """Test that empty items are left alone."""
    dest = {'foo': ''}
    src = {'foo': 'fancy value'}
    ControlIOWriter.merge_dicts_deep(dest, src, False)
    assert dest['foo'] == ''
    dest['foo'] = None
    ControlIOWriter.merge_dicts_deep(dest, src, False)
    assert dest['foo'] is None
    ControlIOWriter.merge_dicts_deep(dest, src, True)
    assert dest['foo'] == 'fancy value'


def test_control_with_components() -> None:
    """Test loading and parsing of implementated reqs with components."""
    control_path = pathlib.Path('tests/data/author/controls/control_with_components.md').resolve()
    comp_prose_dict, _ = ControlIOReader.read_all_implementation_prose_and_header(control_path)
    assert len(comp_prose_dict.keys()) == 3
    assert len(comp_prose_dict['This System'].keys()) == 3
    assert len(comp_prose_dict['Trestle Component'].keys()) == 1
    assert len(comp_prose_dict['Fancy Thing'].keys()) == 2
    assert comp_prose_dict['Fancy Thing']['a.'] == ['Text for fancy thing component']

    # need to build the needed components so they can be referenced
    comp_dict = {}
    for comp_name in comp_prose_dict.keys():
        comp = gens.generate_sample_model(ossp.SystemComponent)
        comp.title = comp_name
        comp_dict[comp_name] = comp

    # confirm that the header content was inserted into the props of the imp_req
    sort_id, imp_req = ControlIOReader.read_implemented_requirement(control_path, comp_dict)
    assert len(imp_req.props) == 12
    assert len(imp_req.statements) == 3
    assert len(imp_req.statements[0].by_components) == 3


@pytest.mark.parametrize('md_file', ['control_with_bad_system_comp.md', 'control_with_double_comp.md'])
def test_control_bad_components(md_file: str) -> None:
    """Test loading of imp reqs for control with bad components."""
    control_path = pathlib.Path('tests/data/author/controls/') / md_file
    with pytest.raises(TrestleError):
        ControlIOReader.read_all_implementation_prose_and_header(control_path)


def test_get_control_param_dict(tmp_trestle_dir: pathlib.Path) -> None:
    """Test getting the param dict of a control."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    prof_a_path = ModelUtils.path_for_top_level_model(
        tmp_trestle_dir, 'test_profile_a', prof.Profile, FileContentType.JSON
    )
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_a_path)
    catalog_interface = CatalogInterface(catalog)
    control = catalog_interface.get_control('ac-1')
    param_dict = ControlIOReader.get_control_param_dict(control, False)
    # confirm profile value is used
    assert ControlIOReader.param_values_as_str(param_dict['ac-1_prm_1']) == 'all alert personnel'
    # confirm original param label is used since no value was assigned
    assert ControlIOReader.param_to_str(
        param_dict['ac-1_prm_7'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'organization-defined events'
    param = control.params[0]
    param.values = None
    param.select = common.ParameterSelection(how_many=common.HowMany.one_or_more, choice=['choice 1', 'choice 2'])
    param_dict = ControlIOReader.get_control_param_dict(control, False)
    assert ControlIOReader.param_to_str(
        param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'choice 1; choice 2'
    assert ControlIOReader.param_to_str(
        param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES, True
    ) == 'Choose one or more: choice 1; choice 2'
    assert ControlIOReader.param_to_str(
        param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES, True, True
    ) == 'Choose one or more: [choice 1; choice 2]'


@pytest.mark.parametrize('overwrite_header_values', [True, False])
def test_write_control_header_params(overwrite_header_values, tmp_path: pathlib.Path) -> None:
    """Test write/read of control header params."""
    # orig file just has one param ac-1_prm_3
    src_control_path = pathlib.Path('tests/data/author/controls/control_with_components_and_params.md')
    # header has two params - 3 and 4
    header = {
        const.SET_PARAMS_TAG: {
            'ac-1_prm_3': {
                'values': 'new prm_3 val from input header'
            },
            'ac-1_prm_4': {
                'values': 'new prm_4 val from input header'
            }
        },
        'foo': 'new bar',
        'new-reviewer': 'James',
        'special': 'new value to ignore',
        'none-thing': 'none value to ignore'
    }
    control_path = tmp_path / 'ac-1.md'
    shutil.copyfile(src_control_path, control_path)
    markdown_processor = MarkdownProcessor()
    # header_1 should have one param: 3
    header_1, _ = markdown_processor.read_markdown_wo_processing(control_path)
    assert len(header_1.keys()) == 8
    orig_control_read, group_title = ControlIOReader.read_control(control_path, True)
    assert group_title == 'Access Control'
    control_writer = ControlIOWriter()
    # write the control back out with the test header
    control_writer.write_control_for_editing(
        tmp_path, orig_control_read, group_title, header, None, False, False, None, overwrite_header_values, None, None
    )
    # header_2 should have 2 params: 3 and 4
    header_2, _ = markdown_processor.read_markdown_wo_processing(control_path)
    assert len(header_2.keys()) == 9
    assert header_2['new-reviewer'] == 'James'
    assert len(header_2[const.SET_PARAMS_TAG]) == 2
    assert 'new' in header_2[const.SET_PARAMS_TAG]['ac-1_prm_4']['values']
    if not overwrite_header_values:
        assert 'orig' in header_2[const.SET_PARAMS_TAG]['ac-1_prm_3']['values']
        assert header_2['foo'] == 'bar'
        assert header_2['special'] == ''
        assert header_2['none-thing'] is None
    else:
        assert 'new' in header_2[const.SET_PARAMS_TAG]['ac-1_prm_3']['values']
        assert header_2['foo'] == 'new bar'
        assert header_2['special'] == 'new value to ignore'
        assert header_2['none-thing'] == 'none value to ignore'
        assert 'orig' in orig_control_read.params[0].values[0].__root__
    new_control_read, _ = ControlIOReader.read_control(control_path, True)
    # insert the new param in the orig control so we can compare the two controls
    orig_control_read.params.append(new_control_read.params[1])
    if overwrite_header_values:
        orig_control_read.params[0] = new_control_read.params[0]
    assert test_utils.controls_equivalent(orig_control_read, new_control_read)


statement_text = """


# xy-9 - \[My Group Title\] Fancy Control

## Control Statement

  The org:

- \[a\] Creates:

  - \[1\] Good stuff; and
  - \[2\] Other good stuff; and


## Control Objective

  Confirm the org:

- \[a_obj\]

  - \[1_obj\]

"""


def test_read_control_statement():
    """Test read control statement."""
    _, part = ControlIOReader._read_control_statement(0, statement_text.split('\n'), 'xy-9')
    assert part.prose == 'The org:'


def test_read_control_objective():
    """Test read control objective."""
    _, part = ControlIOReader._read_control_objective(13, statement_text.split('\n'), 'xy-9')
    assert part.prose == 'Confirm the org:'

    _, part = ControlIOReader._read_control_objective(16, statement_text.split('\n'), 'xy-9')
    assert part is None


section_text = """
## What is the solution

foo
"""


def test_read_sections():
    """Test read control sections."""
    _, parts = ControlIOReader._read_sections(0, section_text.split('\n'), 'xy-9', [])
    assert parts is None


indent_text = """
    -   Hello

"""


def test_indent_label():
    """Test indent and label routines."""
    _, b, _ = ControlIOReader._get_next_indent(0, indent_text.split('\n'))
    assert b == 4

    with pytest.raises(TrestleError):
        ControlIOReader._get_next_indent(0, ['    -'])

    assert ControlIOReader._create_next_label('foo-', 0) == 'foo-a'
    assert ControlIOReader._create_next_label('foo-a', 0) == 'foo-b'


def test_parse_control_title_failures():
    """Test parse control title failures."""
    with pytest.raises(TrestleError):
        ControlIOReader._parse_control_title_line('')

    with pytest.raises(TrestleError):
        ControlIOReader._parse_control_title_line('foo - bar')

    with pytest.raises(TrestleError):
        ControlIOReader._parse_control_title_line('foo-1 and - bar')
