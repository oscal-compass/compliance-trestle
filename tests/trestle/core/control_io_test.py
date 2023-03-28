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
"""Tests for control input output methods."""

import pathlib
import shutil

import pytest

import tests.test_utils as test_utils

import trestle.oscal.catalog as cat
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
from trestle.common import const
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import ControlInterface, ParameterRep
from trestle.core.control_reader import ControlReader
from trestle.core.control_writer import ControlWriter
from trestle.core.markdown.control_markdown_node import ControlMarkdownNode, tree_context
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.markdown.markdown_processor import MarkdownProcessor
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal import common

case_1 = 'indent_normal'
case_2 = 'indent jump back 2'
case_3 = 'indent end abrupt'
case_4 = 'no items'

control_text = """---
x-trestle-global:
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
    statement_part = common.Part(id='ac-1_smt', name=const.STATEMENT)
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

    context = ControlContext.generate(ContextPurpose.CATALOG, True, tmp_path, tmp_path)
    writer = ControlWriter()
    writer.write_control_for_editing(context, control, tmp_path, 'My Group Title', {}, [])

    md_path = tmp_path / f'{control.id}.md'
    reader = ControlReader()
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
    control, group_title = ControlReader.read_control(md_path, True)
    assert group_title == 'My Group Title'
    sub_dir = tmp_path / 'sub_dir'
    sub_dir.mkdir(exist_ok=True)
    # write it out as markdown in a separate directory to avoid name clash
    context = ControlContext.generate(ContextPurpose.CATALOG, True, tmp_path, sub_dir)
    control_writer = ControlWriter()
    control_writer.write_control_for_editing(context, control, sub_dir, group_title, {}, [])
    # confirm the newly written markdown text is identical to what was read originally
    assert test_utils.text_files_equal(md_path, sub_dir / 'xy-9.md')


def test_read_control_no_label(testdata_dir: pathlib.Path) -> None:
    """Test reading a control that doesn't have a part label in statement."""
    md_file = testdata_dir / 'author/controls/control_no_labels.md'
    control, group_title = ControlReader.read_control(md_file, True)
    assert group_title == 'My Group Title'
    assert control.parts[0].parts[2].props[0].value == 'c'
    assert control.parts[0].parts[2].parts[0].props[0].value == '1'
    md_file = testdata_dir / 'author/controls/control_some_labels.md'
    control, group_title = ControlReader.read_control(md_file, True)
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
    assert ControlMarkdownNode._bump_label(prev_label) == bumped_label


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
    assert ControlMarkdownNode._create_next_label(prev_label, indent) == next_label


def test_control_failures(tmp_path: pathlib.Path) -> None:
    """Test various failure modes."""
    part = common.Part(name='foo')
    assert ControlInterface.get_label(part) == ''

    assert ControlInterface.strip_to_make_ncname('1a@foo') == 'afoo'
    with pytest.raises(TrestleError):
        ControlInterface.strip_to_make_ncname('1@')

    with pytest.raises(TrestleError):
        ControlMarkdownNode._indent('')


def test_bad_unicode_in_file(tmp_path: pathlib.Path) -> None:
    """Test error on read of bad unicode in control markdown."""
    bad_file = tmp_path / 'bad_unicode.md'
    with open(bad_file, 'wb') as f:
        f.write(b'\x81')
    md_api = MarkdownAPI()
    with pytest.raises(TrestleError):
        _, _ = md_api.processor.process_markdown(bad_file)


def test_broken_yaml_header(testdata_dir: pathlib.Path) -> None:
    """Test for a bad markdown header."""
    bad_file = testdata_dir / 'author' / 'bad_md_header.md'
    md_api = MarkdownAPI()
    with pytest.raises(TrestleError):
        _, _ = md_api.processor.process_markdown(bad_file)


@pytest.mark.parametrize('overwrite_header_values', [True, False])
def test_merge_dicts_deep(overwrite_header_values) -> None:
    """Test deep merge of dicts."""
    dest = {'trestle': {'foo': {'hello': 1}}, 'fedramp': {'roles': [5, 6], 'values': 8}, 'orig': 11}
    src = {'trestle': {'foo': {'hello': 3}, 'bar': 4}, 'fedramp': {'roles': 7, 'values': 10}, 'extra': 12}
    ControlInterface.merge_dicts_deep(dest, src, overwrite_header_values)
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
    ControlInterface.merge_dicts_deep(dest, src, False)
    assert dest['foo'] == ''
    dest['foo'] = None
    ControlInterface.merge_dicts_deep(dest, src, False)
    assert dest['foo'] is None
    ControlInterface.merge_dicts_deep(dest, src, True)
    assert dest['foo'] == 'fancy value'


def test_get_control_param_dict(tmp_trestle_dir: pathlib.Path) -> None:
    """Test getting the param dict of a control."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    prof_a_path = ModelUtils.get_model_path_for_name_and_class(
        tmp_trestle_dir, 'test_profile_a', prof.Profile, FileContentType.JSON
    )
    catalog = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_a_path)
    catalog_interface = CatalogInterface(catalog)
    control = catalog_interface.get_control('ac-1')
    param_dict = ControlInterface.get_control_param_dict(control, False)
    # confirm profile value is used
    assert ControlInterface._param_values_as_str(param_dict['ac-1_prm_1']) == 'all alert personnel'
    # confirm original param label is used since no value was assigned
    assert ControlInterface.param_to_str(
        param_dict['ac-1_prm_7'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'organization-defined events'
    param = control.params[0]
    param.values = None
    param.select = common.ParameterSelection(how_many=const.ONE_OR_MORE_HYPHENED, choice=['choice 1', 'choice 2'])
    param_dict = ControlInterface.get_control_param_dict(control, False)
    assert ControlInterface.param_to_str(
        param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) == 'choice 1; choice 2'
    assert ControlInterface.param_to_str(
        param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES, True
    ) == 'Selection (one or more): choice 1; choice 2'
    assert ControlInterface.param_to_str(
        param_dict['ac-1_prm_1'], ParameterRep.VALUE_OR_LABEL_OR_CHOICES, True, True
    ) == 'Selection (one or more): [choice 1; choice 2]'


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
    orig_control_read, group_title = ControlReader.read_control(control_path, True)
    assert group_title == 'Access Control'
    context = ControlContext.generate(ContextPurpose.CATALOG, True, tmp_path, tmp_path)
    context.cli_yaml_header = header
    context.overwrite_header_values = overwrite_header_values
    control_writer = ControlWriter()
    control_writer.write_control_for_editing(context, orig_control_read, tmp_path, group_title, {}, [])
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
        assert 'orig' in orig_control_read.params[0].values[0]
    new_control_read, _ = ControlReader.read_control(control_path, True)
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
    tree = ControlMarkdownNode.build_tree_from_markdown(statement_text.split('\n'))
    part = tree.get_control_statement().content.part
    tree_context.reset()
    assert part.prose == 'The org:'


def test_read_control_objective():
    """Test read control objective."""
    tree = ControlMarkdownNode.build_tree_from_markdown(statement_text.split('\n'))
    part = tree.get_control_objective().content.part
    tree_context.reset()
    assert part.prose == 'Confirm the org:'


section_text = """
## What is the solution

foo
"""


def test_read_sections():
    """Test read control sections."""
    tree = ControlMarkdownNode.build_tree_from_markdown(statement_text.split('\n'))
    parts = tree.get_other_control_parts()
    tree_context.reset()
    assert not parts


indent_text = """
    -   Hello

"""


def test_indent_label():
    """Test indent and label routines."""
    _, b, _ = ControlMarkdownNode._get_next_indent(0, indent_text.split('\n'))
    assert b == 4

    with pytest.raises(TrestleError):
        ControlMarkdownNode._get_next_indent(0, ['    -'])

    assert ControlMarkdownNode._create_next_label('foo-', 0) == 'foo-a'
    assert ControlMarkdownNode._create_next_label('foo-a', 0) == 'foo-b'


def test_parse_control_title_failures():
    """Test parse control title failures."""
    with pytest.raises(TrestleError):
        ControlMarkdownNode._parse_control_title_line('')

    with pytest.raises(TrestleError):
        ControlMarkdownNode._parse_control_title_line('foo - bar')

    with pytest.raises(TrestleError):
        ControlMarkdownNode._parse_control_title_line('foo-1 and - bar')


def test_bad_header():
    """Test bad header checks."""
    assert ControlInterface.bad_header('')
    assert ControlInterface.bad_header('#')
    assert ControlInterface.bad_header('##')
    assert ControlInterface.bad_header('#x')
    assert ControlInterface.bad_header('x# ')
    assert not ControlInterface.bad_header('# ')
    assert not ControlInterface.bad_header('#### ')
    assert not ControlInterface.bad_header('#### foo')


def test_get_component_by_name(sample_nist_component_def: comp.ComponentDefinition) -> None:
    """Test get component by name."""
    assert ControlInterface.get_component_by_name(sample_nist_component_def, 'test component 1')
    assert ControlInterface.get_component_by_name(sample_nist_component_def, 'foobar') is None


def test_delete_prop(sample_component_definition: comp.ComponentDefinition) -> None:
    """Teste delete prop."""
    component = sample_component_definition.components[1]
    assert len(component.props) == 2
    ControlInterface._delete_prop(component, 'prop_2')
    assert len(component.props) == 1
    assert component.props[0].name == 'prop_1'
    ControlInterface._delete_prop(component, 'prop_1')
    assert component.props is None
