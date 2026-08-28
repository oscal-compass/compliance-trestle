# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Tests for trestle.core.oscal_backward_compatibility pre-parse backward-compatibility checker."""

import pathlib

import pytest

from trestle.core.oscal_backward_compatibility import CompatIssue, check_file, check_raw_oscal

COMPAT_DIR = pathlib.Path(__file__).parent.parent.parent / 'data/json/compat'


# ---------------------------------------------------------------------------
# check_raw_oscal — unit tests on raw dicts
# ---------------------------------------------------------------------------


class TestCheckRawOscal:
    """Tests for check_raw_oscal()."""

    def test_clean_120_profile_no_issues(self) -> None:
        """A well-formed OSCAL 1.2.0 profile returns no issues."""
        raw = {
            'profile': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000001',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00+00:00',
                    'version': '1.0',
                    'oscal-version': '1.2.0',
                },
                'imports': [{'href': 'x.json', 'include-all': {}}],
                'merge': {'flat': {}},
            }
        }
        assert check_raw_oscal(raw) == []

    def test_empty_combine_no_issues(self) -> None:
        """combine: {} (OSCAL 1.2.0 shape) is not flagged."""
        raw = {
            'profile': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000002',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00Z',
                    'version': '1.0',
                    'oscal-version': '1.2.0',
                },
                'imports': [{'href': 'x.json', 'include-all': {}}],
                'merge': {'combine': {}, 'flat': {}},
            }
        }
        assert check_raw_oscal(raw) == []

    def test_combine_with_method_is_error(self) -> None:
        """combine: {method: use-first} triggers ERROR."""
        raw = {
            'profile': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000003',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00+00:00',
                    'version': '1.0',
                    'oscal-version': '1.0.4',
                },
                'imports': [{'href': 'x.json', 'include-all': {}}],
                'merge': {'combine': {'method': 'use-first'}, 'flat': {}},
            }
        }
        issues = check_raw_oscal(raw)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert len(errors) == 1
        assert 'profile.merge.combine' == errors[0].field_path
        assert 'method' in errors[0].message

    def test_naive_datetime_last_modified_is_error(self) -> None:
        """last-modified without timezone offset triggers ERROR."""
        raw = {
            'catalog': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000004',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2022-06-01T00:00:00',
                    'version': '1.0',
                    'oscal-version': '1.0.4',
                },
                'groups': [],
            }
        }
        issues = check_raw_oscal(raw)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert any('last-modified' in i.field_path for i in errors)

    def test_aware_datetime_z_suffix_is_valid(self) -> None:
        """Datetime ending in Z is valid (UTC shorthand)."""
        raw = {
            'catalog': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000005',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T12:30:00.000Z',
                    'version': '1.0',
                    'oscal-version': '1.2.0',
                },
                'groups': [],
            }
        }
        assert check_raw_oscal(raw) == []

    def test_multiple_structuring_keys_is_error(self) -> None:
        """merge with both flat and as-is triggers ERROR."""
        raw = {
            'profile': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000006',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00+00:00',
                    'version': '1.0',
                    'oscal-version': '1.0.4',
                },
                'imports': [{'href': 'x.json', 'include-all': {}}],
                'merge': {'flat': {}, 'as-is': True},
            }
        }
        issues = check_raw_oscal(raw)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert any('profile.merge' == i.field_path for i in errors)

    def test_invalid_by_item_name_is_error(self) -> None:
        """by-item-name with a value not in ItemNameValidValues triggers ERROR."""
        raw = {
            'profile': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000007',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00+00:00',
                    'version': '1.0',
                    'oscal-version': '1.0.4',
                },
                'imports': [{'href': 'x.json', 'include-all': {}}],
                'merge': {'flat': {}},
                'modify': {'alters': [{'control-id': 'ac-1', 'removes': [{'by-item-name': 'assessment-objective'}]}]},
            }
        }
        issues = check_raw_oscal(raw)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert len(errors) == 1
        assert 'by-item-name' in errors[0].field_path
        assert 'assessment-objective' in errors[0].message

    def test_valid_by_item_name_no_error(self) -> None:
        """by-item-name with a valid value (e.g. 'prop') is not flagged."""
        raw = {
            'profile': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000008',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00+00:00',
                    'version': '1.0',
                    'oscal-version': '1.2.0',
                },
                'imports': [{'href': 'x.json', 'include-all': {}}],
                'merge': {'flat': {}},
                'modify': {'alters': [{'control-id': 'ac-1', 'removes': [{'by-item-name': 'prop'}]}]},
            }
        }
        assert check_raw_oscal(raw) == []

    def test_unsupported_oscal_version_no_structural_errors_is_clean(self) -> None:
        """oscal-version outside supported range with no structural errors produces no issues.

        A version mismatch alone is not actionable — the document parses fine.
        The version warning is only emitted when structural errors are also present.
        """
        raw = {
            'catalog': {
                'uuid': 'aaaaaaaa-0000-4000-8000-000000000009',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00+00:00',
                    'version': '1.0',
                    'oscal-version': '1.0.4',
                },
                'groups': [],
            }
        }
        assert check_raw_oscal(raw) == []

    def test_version_with_v_prefix_is_warning_not_error(self) -> None:
        """oscal-version 'v1.2.0' (with v prefix) is treated as 1.2.0 — no warning."""
        raw = {
            'catalog': {
                'uuid': 'aaaaaaaa-0000-4000-8000-00000000000a',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2023-01-01T00:00:00+00:00',
                    'version': '1.0',
                    'oscal-version': 'v1.2.0',
                },
                'groups': [],
            }
        }
        issues = check_raw_oscal(raw)
        version_warnings = [i for i in issues if 'oscal-version' in i.field_path]
        assert not version_warnings

    def test_unsupported_oscal_version_with_structural_errors_emits_warning(self) -> None:
        """oscal-version outside supported range AND structural errors emits both ERROR and WARNING."""
        raw = {
            'catalog': {
                'uuid': 'aaaaaaaa-0000-4000-8000-00000000000b',
                'metadata': {
                    'title': 'Test',
                    'last-modified': '2022-06-01T00:00:00',  # naive datetime → ERROR
                    'version': '1.0',
                    'oscal-version': '1.0.4',  # old version → WARNING (only because error exists)
                },
                'groups': [],
            }
        }
        issues = check_raw_oscal(raw)
        errors = [i for i in issues if i.severity == 'ERROR']
        warnings = [i for i in issues if i.severity == 'WARNING']
        assert any('last-modified' in i.field_path for i in errors)
        assert any('oscal-version' in i.field_path for i in warnings)

    def test_invalid_raw_structure_returns_empty(self) -> None:
        """Non-OSCAL dict returns no issues rather than crashing."""
        assert check_raw_oscal({}) == []
        assert check_raw_oscal({'a': 1, 'b': 2}) == []  # type: ignore

    def test_compat_issue_str(self) -> None:
        """CompatIssue __str__ format is correct."""
        issue = CompatIssue(field_path='a.b', message='something bad', severity='ERROR')
        assert str(issue) == 'COMPAT ERROR: a.b — something bad'


# ---------------------------------------------------------------------------
# check_file — integration tests on fixture files
# ---------------------------------------------------------------------------


class TestCheckFile:
    """Tests for check_file() reading from fixture JSON files."""

    def test_old_combine_method_file(self) -> None:
        """Fixture with combine.method produces an ERROR."""
        path = COMPAT_DIR / 'profile_old_combine_method.json'
        issues = check_file(path)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert any('combine' in i.field_path for i in errors)

    def test_naive_datetime_file(self) -> None:
        """Fixture with naive datetime produces an ERROR."""
        path = COMPAT_DIR / 'catalog_naive_datetime.json'
        issues = check_file(path)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert any('last-modified' in i.field_path for i in errors)

    def test_multiple_structuring_keys_file(self) -> None:
        """Fixture with flat + as-is together produces an ERROR."""
        path = COMPAT_DIR / 'profile_multiple_structuring.json'
        issues = check_file(path)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert any('merge' in i.field_path for i in errors)

    def test_invalid_by_item_name_file(self) -> None:
        """Fixture with invalid by-item-name produces an ERROR."""
        path = COMPAT_DIR / 'profile_invalid_by_item_name.json'
        issues = check_file(path)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert any('by-item-name' in i.field_path for i in errors)

    def test_clean_120_file_no_issues(self) -> None:
        """Fixture that is a valid OSCAL 1.2.0 profile returns no issues."""
        path = COMPAT_DIR / 'profile_clean_120.json'
        issues = check_file(path)
        errors = [i for i in issues if i.severity == 'ERROR']
        assert not errors

    def test_nonexistent_file_returns_empty(self) -> None:
        """A file that does not exist returns no issues — the model load will report the error."""
        path = COMPAT_DIR / 'does_not_exist.json'
        assert check_file(path) == []
