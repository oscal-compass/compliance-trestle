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
"""Tests for trestle markdown_validator module."""
import pathlib
from typing import Any, Dict

import pytest

import trestle.core.err as err
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.markdown.markdown_validator import MarkdownValidator


@pytest.mark.parametrize(
    'template_path, instance_path, status, header_validate, header_only_validate',
    [
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/correct_instance.md'),
            True,
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/correct_instance_extra_features.md'),
            True,
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_yaml_header_change.md'),
            False,
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_yaml_header_change.md'),
            True,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_reordered.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_missing_heading.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_missing_heading.md'),
            True,
            True,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_heading_wrong_type.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_bold_heading.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/bad_instance_bold_heading.md'),
            pathlib.Path('tests/data/author/0.0.1/test_1_md_format/template.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/correct_instance.md'),
            True,
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/correct_instance_extra_features.md'),
            True,
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_yaml_header_change.md'),
            False,
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_yaml_header_change.md'),
            True,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_reordered.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_missing_heading.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_missing_heading.md'),
            True,
            True,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_heading_wrong_type.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_bold_heading.md'),
            False,
            False,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/bad_instance_bold_heading.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_format_extras/template.md'),
            False,
            False,
            False
        )
    ]
)
def test_md_validator_pass(
    template_path: pathlib.Path,
    instance_path: pathlib.Path,
    status: bool,
    header_validate: bool,
    header_only_validate: bool
) -> None:
    """Run markdown validator to expected outcome."""
    md_api = MarkdownAPI()
    md_api.load_validator_with_template(template_path, header_validate, not header_only_validate)
    result = md_api.validate_instance(instance_path)
    assert result == status


def test_md_by_hand() -> None:
    """Simpler test to enable debugging."""
    template_path = pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/template.md')
    instance_path = pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/decisions_000.md')
    header_validate = False
    status = True
    md_api = MarkdownAPI()
    md_api.load_validator_with_template(template_path, header_validate, False, 'Governed Document')
    result = md_api.validate_instance(instance_path)
    assert result == status


@pytest.mark.parametrize(
    'template_path, instance_path, status, yaml_header_validate',
    [
        (
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/instance.md'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/decisions_000.md'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/decisions_001.md'),
            True,
            False
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_3_md_hand_edited/decisions_002.md'),
            True,
            False
        )
    ]
)
def test_md_validator_with_md_header(
    template_path: pathlib.Path, instance_path: pathlib.Path, status: bool, yaml_header_validate: bool
) -> None:
    """Test with validation of heading."""
    md_api = MarkdownAPI()
    md_api.load_validator_with_template(template_path, yaml_header_validate, False, 'Governed Document')
    result = md_api.validate_instance(instance_path)
    assert result == status


def test_bad_file_path(tmp_path: pathlib.Path):
    """Check errors are thrown with bad files."""
    no_file = tmp_path / 'non_existent.md'
    with pytest.raises(err.TrestleError):
        md_api = MarkdownAPI()
        md_api.load_validator_with_template(no_file, False, False)


@pytest.mark.parametrize(
    'template, candidate, expected_status',
    [
        ({
            'hello': {
                'world': 'stuff'
            }
        }, {
            'hello': {
                'world': 'banana'
            }
        }, True), ({
            'hello': {
                'world': 'stuff'
            }
        }, {
            'hello': {
                'banana': 'world'
            }
        }, False),
        ({
            'hello': {
                'world': 'stuff'
            }
        }, {
            'hello': {
                'world': ['results can be arrays with no restrictions']
            }
        }, True), ({
            'hello': 1,
            'world': 2,
        }, {
            'hello': 1,
            'my-world': 2,
        }, False), ({
            'hello': 1,
            'world': 2,
        }, {
            'hello': 1,
            'world': 2,
            'banana': 3,
        }, False),
        (
            {
                'hello': 'A simple element', 'world': {
                    'required_key': '1', 'another_required_key': '2'
                }
            }, {
                'hello': 'A simple element', 'world': {
                    'required_key': '1', 'another_required_key': '2'
                }
            },
            True
        ),
        (
            {
                'hello': 'A simple element', 'world': {
                    'required_key': '1', 'another_required_key': '2'
                }
            }, {
                'hello': 'A simple element', 'world': {
                    'required_key': 'there is a missing key',
                }
            },
            False
        )
    ]
)
def test_key_compare(template: Dict[str, Any], candidate: Dict[str, Any], expected_status):
    """Test key_compare behaves as expected."""
    status = MarkdownValidator.compare_keys(template, candidate)
    assert status == expected_status


@pytest.mark.parametrize(
    'template_path, instance_path, status, governed_header',
    [
        (
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/instance.md'),
            True,
            'Governed Document'
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/instance.md'),
            True,
            'Governed Document      '
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/instance.md'),
            False,
            'Governed Documeent'
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/bad_heading_content_changed_header.md'),
            False,
            'Governed Document'
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/bad_heading_content_extra_lines.md'),
            False,
            'Governed Document'
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_2_md_with_md_header/wrong_heading_title.md'),
            False,
            'Governed Document'
        )
    ]
)
def test_validate_for_governed_header(
    template_path: pathlib.Path, instance_path: pathlib.Path, status: bool, governed_header: str
) -> None:
    """Test scenarios for validate w.r.t the governed header."""
    md_api = MarkdownAPI()
    md_api.load_validator_with_template(template_path, False, False, governed_header)
    result = md_api.validate_instance(instance_path)
    assert result == status


def test_bad_unicode_in_parsetree(tmp_path: pathlib.Path):
    """Test error on read of bad unicode in parsetree."""
    bad_file = tmp_path / 'bad_unicode.md'
    with open(bad_file, 'wb') as f:
        f.write(b'\x81')
    with pytest.raises(err.TrestleError):
        md_api = MarkdownAPI()
        md_api.load_validator_with_template(bad_file, False, False)


def test_broken_yaml_header(testdata_dir: pathlib.Path):
    """Test for a bad markdown header."""
    bad_file = testdata_dir / 'author' / 'bad_md_header.md'
    with pytest.raises(err.TrestleError):
        md_api = MarkdownAPI()
        md_api.load_validator_with_template(bad_file, True, False)


@pytest.mark.parametrize(
    'template_path, instance_path, status, header_validate, validate_md_body',
    [
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/correct_instance.md'),
            True,
            True,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/correct_instance_empty_subs.md'),
            True,
            True,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/bad_added_header.md'),
            False,
            True,
            True
        ),
        (
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/template.md'),
            pathlib.Path('tests/data/author/0.0.1/test_4_md_substitutions/bad_modified_header_deep.md'),
            False,
            True,
            True
        )
    ]
)
def test_md_validator_substitutions(
    template_path: pathlib.Path,
    instance_path: pathlib.Path,
    status: bool,
    header_validate: bool,
    validate_md_body: bool
) -> None:
    """Run markdown validator to expected outcome."""
    md_api = MarkdownAPI()
    md_api.load_validator_with_template(template_path, header_validate, validate_md_body)
    result = md_api.validate_instance(instance_path)
    assert result == status


@pytest.mark.parametrize(
    'template_path, status',
    [
        (
            pathlib.Path('tests/data/author/versions/1.0.0/good_template.md'),
            True,
        ), (
            pathlib.Path('tests/data/author/versions/1.1.0/good_template.md'),
            True,
        )
    ]
)
def test_template_version(template_path: pathlib.Path, status: bool) -> None:
    """Test for x-trestle-template-version header in templates."""
    md_api = MarkdownAPI()
    md_api.load_validator_with_template(template_path, True, True)
    result = md_api.validate_instance(template_path)
    assert result == status


@pytest.mark.parametrize(
    'template_path, instance_path, status',
    [
        (
            pathlib.Path('tests/data/author/versions/1.1.0/good_template.md'),
            pathlib.Path('tests/data/author/versions/good_instance_with_version_outside_structure.md'),
            True,
        ),
        (
            pathlib.Path('tests/data/author/versions/1.1.0/good_template.md'),
            pathlib.Path('tests/data/author/versions/1.1.0/good_instance.md'),
            True,
        ),
        (
            pathlib.Path('tests/data/author/versions/1.1.0/good_template.md'),
            pathlib.Path('tests/data/author/versions/1.1.0/bad_instance_mismatched_versions.md'),
            False,
        )
    ]
)
def test_instance_template_version(template_path: pathlib.Path, instance_path: pathlib.Path, status: bool) -> None:
    """Test for x-trestle-template-version header in instances."""
    md_api = MarkdownAPI()
    md_api.load_validator_with_template(template_path, False, True)
    result = md_api.validate_instance(instance_path)
    assert result == status


@pytest.mark.parametrize(
    'template_path',
    [
        (pathlib.Path('tests/data/author/versions/1.0.0/bad_template_wrong_folder.md')),
        (pathlib.Path('tests/data/author/versions/1.1.0/bad_template_mismatched_versions.md'))
    ]
)
def test_template_path_mismatch(template_path: pathlib.Path) -> None:
    """Test template path and version mismatch."""
    with pytest.raises(err.TrestleError):
        md_api = MarkdownAPI()
        md_api.load_validator_with_template(template_path, False, True)
