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
"""Tests for the drawio model."""

import pathlib
import shutil
from uuid import uuid4

import pytest

from trestle.core.draw_io import DrawIO, DrawIOMetadataValidator
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_validator import MarkdownValidator


def test_directory_instead_file(tmp_path) -> None:
    """Test that exceptions are raised on a bad file."""
    with pytest.raises(TrestleError):
        _ = DrawIO(tmp_path)


def test_missing_file(tmp_path) -> None:
    """Test that exceptions are raised on a missing file."""
    non_file = tmp_path / (str(uuid4()) + '.drawio')
    with pytest.raises(TrestleError):
        _ = DrawIO(non_file)


@pytest.mark.parametrize(
    'file_path, metadata_exists, metadata_valid',
    [
        (
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_bad_metadata_extra_fields_compressed.drawio'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_bad_metadata_missing_fields_compressed.drawio'),
            True,
            False
        ), (pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'), True, True),
        (pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_no_metadata_compressed.drawio'), False, False),
        (pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_no_metadata_uncompressed.drawio'), False, False),
        (pathlib.Path('tests/data/author/0.0.1/drawio/two_tabs_metadata_compressed.drawio'), True, True),
        (pathlib.Path('tests/data/author/0.0.1/drawio/two_tabs_metadata_second_tab_compressed.drawio'), True, False)
    ]
)
def test_valid_drawio(file_path: pathlib.Path, metadata_exists: bool, metadata_valid: bool) -> None:
    """Run various scenarios with a valid drawio and various metadata status."""
    expected_metadata_flat = {
        'test': 'value', 'nested.test': 'value', 'nested.nested.test': 'value', 'nested.extra': 'value'
    }
    draw_io = DrawIO(file_path)
    metadata = draw_io.get_metadata()
    md = False
    for tab_md in metadata:
        if not tab_md == {}:
            md = True
    assert metadata_exists == md
    md_first = metadata[0]
    val_status = MarkdownValidator.compare_keys(expected_metadata_flat, md_first)
    assert val_status == metadata_valid


@pytest.mark.parametrize(
    'bad_file_name',
    [
        (pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_no_metadata_uncompressed_mangled.drawio')),
        (pathlib.Path('tests/data/author/0.0.1/drawio/not_mxfile.drawio')),
        (pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_no_metadata_bad_internal_structure.drawio'))
    ]
)
def test_bad_drawio_files(bad_file_name: pathlib.Path) -> None:
    """This tests that exceptions are properly thrown on bad drawio files."""
    with pytest.raises(TrestleError):
        _ = DrawIO(bad_file_name)


@pytest.mark.parametrize(
    'template_file, sample_file, must_be_first_tab, metadata_valid',
    [
        (
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'),
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'),
            True,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'),
            pathlib.Path('tests/data/author/0.0.1/drawio/two_tabs_metadata_compressed.drawio'),
            True,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'),
            pathlib.Path('tests/data/author/0.0.1/drawio/two_tabs_metadata_second_tab_compressed.drawio'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'),
            pathlib.Path('tests/data/author/0.0.1/drawio/two_tabs_metadata_second_tab_compressed.drawio'),
            False,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'),
            pathlib.Path('tests/data/author/0.0.1/drawio/two_tabs_metadata_second_tab_bad_md.drawio'),
            False,
            False
        )
    ]
)
def test_valid_drawio_second_tab(
    template_file: pathlib.Path, sample_file: pathlib.Path, must_be_first_tab: bool, metadata_valid: bool
) -> None:
    """Run various scenarios with a valid drawio and various metadata status."""
    draw_io = DrawIOMetadataValidator(template_file, must_be_first_tab)
    status = draw_io.validate(sample_file)
    assert metadata_valid == status


def test_restructure_metadata():
    """Test Restructuring metadata."""
    drawio_file = pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio')
    comparison_metadata = {'test': 'value', 'nested': {'test': 'value', 'extra': 'value', 'nested': {'test': 'value'}}}
    draw_io = DrawIO(drawio_file)
    metadata_flat = draw_io.get_metadata()[0]
    metadata_structured = draw_io.restructure_metadata(metadata_flat)
    assert comparison_metadata == metadata_structured


def test_write_metadata_compressed(tmp_path):
    """Test writing modified metadata to drawio file."""
    tmp_drawio_file = tmp_path / 'test.drawio'
    shutil.copyfile(
        pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_compressed.drawio'), tmp_drawio_file
    )
    draw_io = DrawIO(tmp_drawio_file)

    diagram_idx = 0
    metadata_flat = draw_io.get_metadata()[diagram_idx]
    metadata_structured = draw_io.restructure_metadata(metadata_flat)

    metadata_structured['test'] = 'modified value'
    metadata_structured['nested']['nested']['test'] = 'deep modification'

    draw_io.write_drawio_with_metadata(tmp_drawio_file, metadata_structured, diagram_idx)

    draw_io_mod = DrawIO(tmp_drawio_file)
    mod_metadata = draw_io_mod.get_metadata()[diagram_idx]
    mod_metadata = draw_io.restructure_metadata(mod_metadata)

    assert mod_metadata['test'] == 'modified value'
    assert mod_metadata['nested']['nested']['test'] == 'deep modification'


def test_write_metadata_uncompressed(tmp_path):
    """Test writing modified metadata to drawio file."""
    tmp_drawio_file = tmp_path / 'test.drawio'
    shutil.copyfile(
        pathlib.Path('tests/data/author/0.0.1/drawio/single_tab_metadata_uncompressed.drawio'), tmp_drawio_file
    )
    draw_io = DrawIO(tmp_drawio_file)

    diagram_idx = 0
    metadata_flat = draw_io.get_metadata()[diagram_idx]
    metadata_structured = draw_io.restructure_metadata(metadata_flat)

    metadata_structured['status'] = 'modified status'
    metadata_structured['abc']['bcd']['name'] = 'modified name'

    draw_io.write_drawio_with_metadata(tmp_drawio_file, metadata_structured, diagram_idx)

    draw_io_mod = DrawIO(tmp_drawio_file)
    mod_metadata = draw_io_mod.get_metadata()[diagram_idx]
    mod_metadata = draw_io.restructure_metadata(mod_metadata)

    assert mod_metadata['status'] == 'modified status'
    assert mod_metadata['abc']['bcd']['name'] == 'modified name'
