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
"""Pytest wrapper for the atheris fuzz harness.

Requires atheris (Linux only).  The entire module is skipped automatically on
platforms where atheris is not installed — pytest.importorskip handles this.

These tests are run as part of the fuzz.yml CI workflow, which installs atheris
before invoking pytest.  They are skipped silently in the cross-platform
python-test.yml matrix.

Each parametrized case calls TestOneInput through the real atheris
FuzzedDataProvider, exercising the identical code path the fuzzer uses.
"""

import pathlib
import sys

import pytest

# Skip the entire module if atheris is not installed (macOS, Windows).
# This must come before the fuzz harness import so the path insertion below
# is also guarded — pytest.importorskip raises Skipped on missing import.
pytest.importorskip('atheris')

# Make fuzz/ importable regardless of how pytest is invoked.
_FUZZ_DIR = pathlib.Path(__file__).parents[3] / 'fuzz'
if str(_FUZZ_DIR) not in sys.path:
    sys.path.insert(0, str(_FUZZ_DIR))

from fuzz_oscal_load import TestOneInput  # noqa: E402

_JSON_DIR = pathlib.Path(__file__).parents[3] / 'tests' / 'data' / 'json'
_CORPUS_DIR = pathlib.Path(__file__).parents[3] / 'fuzz' / 'corpus' / 'oscal_load'

# ---------------------------------------------------------------------------
# Hand-crafted: valid JSON that reaches pydantic / trestle validation logic.
# Each case targets a distinct validation rule inside Catalog or its metadata.
# ---------------------------------------------------------------------------
_CASES: list[tuple[str, bytes]] = [
    # Correctly-shaped catalog — happy path must not raise at all.
    (
        'valid_minimal_catalog',
        b'{"catalog":{"uuid":"4ea13065-8cae-4dac-a0f2-a7f5e8f54c64",'
        b'"metadata":{"title":"T","last-modified":"2020-10-22T09:46:21+00:00",'
        b'"version":"1","oscal-version":"1.1.0"}}}',
    ),
    # uuid field present but not a valid UUID4 — hits pydantic UUID validator.
    (
        'bad_uuid',
        b'{"catalog":{"uuid":"not-a-uuid",'
        b'"metadata":{"title":"T","last-modified":"2020-10-22T09:46:21+00:00",'
        b'"version":"1","oscal-version":"1.1.0"}}}',
    ),
    # last-modified is not an ISO datetime — hits pydantic datetime validator.
    (
        'bad_datetime',
        b'{"catalog":{"uuid":"4ea13065-8cae-4dac-a0f2-a7f5e8f54c64",'
        b'"metadata":{"title":"T","last-modified":"yesterday",'
        b'"version":"1","oscal-version":"1.1.0"}}}',
    ),
    # Required metadata field missing entirely — pydantic required-field check.
    ('missing_metadata', b'{"catalog":{"uuid":"4ea13065-8cae-4dac-a0f2-a7f5e8f54c64"}}'),
    # Extra field on catalog — hits model_config extra='forbid'.
    (
        'extra_field_forbidden',
        b'{"catalog":{"uuid":"4ea13065-8cae-4dac-a0f2-a7f5e8f54c64",'
        b'"metadata":{"title":"T","last-modified":"2020-10-22T09:46:21+00:00",'
        b'"version":"1","oscal-version":"1.1.0"},"__injected__":true}}',
    ),
    # Wrong root key — to_full_model_name / root_key path in the parser.
    ('wrong_root_key', b'{"system-security-plan":{"uuid":"4ea13065-8cae-4dac-a0f2-a7f5e8f54c64"}}'),
    # Deeply nested groups — exercises recursive structure without OOM risk.
    (
        'nested_groups',
        b'{"catalog":{"uuid":"4ea13065-8cae-4dac-a0f2-a7f5e8f54c64",'
        b'"metadata":{"title":"T","last-modified":"2020-10-22T09:46:21+00:00",'
        b'"version":"1","oscal-version":"1.1.0"},'
        b'"groups":[{"id":"g1","title":"G1","groups":[{"id":"g2","title":"G2",'
        b'"groups":[{"id":"g3","title":"G3"}]}]}]}}',
    ),
]


@pytest.mark.parametrize('label,payload', _CASES, ids=[c[0] for c in _CASES])
def test_fuzz_harness_hand_crafted(label: str, payload: bytes) -> None:
    """TestOneInput must never raise an unexpected exception for any input."""
    TestOneInput(payload)


@pytest.mark.parametrize(
    'corpus_file',
    sorted(_CORPUS_DIR.glob('*.json')) if _CORPUS_DIR.exists() else [],
    ids=[f.name for f in sorted(_CORPUS_DIR.glob('*.json'))] if _CORPUS_DIR.exists() else [],
)
def test_fuzz_harness_corpus(corpus_file: pathlib.Path) -> None:
    """TestOneInput must silently handle every seed corpus file."""
    TestOneInput(corpus_file.read_bytes())


@pytest.mark.parametrize(
    'json_file', sorted(_JSON_DIR.glob('*.json')), ids=[f.name for f in sorted(_JSON_DIR.glob('*.json'))]
)
def test_fuzz_harness_test_data(json_file: pathlib.Path) -> None:
    """TestOneInput must silently handle every existing test-data JSON file."""
    TestOneInput(json_file.read_bytes())
