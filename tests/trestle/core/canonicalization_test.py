# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for canonical JSON helpers."""

import hashlib
import pathlib
from typing import Any, Callable

import pytest

import tests.test_utils as test_utils

from trestle.common.err import TrestleError
from trestle.core.canonicalization import (
    canonicalize_json_object,
    canonicalize_json_text,
    digest_algorithm_name,
    digest_hex,
    load_canonical_json_file,
    parse_digest_algorithm,
    sha256_digest_hex,
)
from trestle.oscal.common import Algorithm


@pytest.mark.parametrize(
    'algorithm, constructor',
    [
        (Algorithm.SHA_224, hashlib.sha224),
        (Algorithm.SHA_256, hashlib.sha256),
        (Algorithm.SHA_384, hashlib.sha384),
        (Algorithm.SHA_512, hashlib.sha512),
        (Algorithm.SHA3_224, hashlib.sha3_224),
        (Algorithm.SHA3_256, hashlib.sha3_256),
        (Algorithm.SHA3_384, hashlib.sha3_384),
        (Algorithm.SHA3_512, hashlib.sha3_512),
    ],
)
def test_digest_algorithms(algorithm: Algorithm, constructor: Callable[[bytes], Any]) -> None:
    """Each OSCAL algorithm should map to the correct hash and in-toto name."""
    expected = constructor(b'abc')
    assert digest_algorithm_name(algorithm) == expected.name
    assert digest_hex(b'abc', algorithm) == expected.hexdigest()
    assert parse_digest_algorithm(expected.name) == algorithm


def test_digest_algorithm_preserves_sha256() -> None:
    """The generic helper and compatibility wrapper should preserve SHA-256 output."""
    expected = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    assert digest_hex(b'abc', Algorithm.SHA_256) == expected
    assert sha256_digest_hex(b'abc') == expected


@pytest.mark.parametrize('algorithm', ['md5', 'sha1', 'SHA-256', None, []])
def test_digest_rejects_unsupported_algorithms(algorithm: Any) -> None:
    """Programmatic callers must select an approved OSCAL Algorithm enum member."""
    with pytest.raises(TrestleError, match='Unsupported digest algorithm'):
        digest_hex(b'abc', algorithm)


@pytest.mark.parametrize('name', ['md5', 'sha1', 'SHA-256', '', None, [], {}])
def test_parse_digest_algorithm_rejects_unsupported_names(name: Any) -> None:
    """Signed algorithm metadata must identify a supported in-toto digest name."""
    with pytest.raises(TrestleError, match='Unsupported digest algorithm'):
        parse_digest_algorithm(name)


def test_canonicalization_is_stable_for_equivalent_json() -> None:
    """Equivalent JSON documents should produce identical canonical bytes and digests."""
    first_json = '{"assessment-results":{"metadata":{"version":"0.1.0","title":"demo"},"results":[]}}'
    second_json = """
    {
      "assessment-results": {
        "results": [],
        "metadata": {
          "title": "demo",
          "version": "0.1.0"
        }
      }
    }
    """

    _, first_canonical = canonicalize_json_text(first_json)
    _, second_canonical = canonicalize_json_text(second_json)

    assert first_canonical == second_canonical
    assert sha256_digest_hex(first_canonical) == sha256_digest_hex(second_canonical)
    assert first_canonical == b'{"assessment-results":{"metadata":{"title":"demo","version":"0.1.0"},"results":[]}}'


def test_canonicalization_rejects_duplicate_object_keys() -> None:
    """Duplicate keys are ambiguous for signing and must fail before digesting."""
    with pytest.raises(TrestleError, match='Duplicate JSON object key'):
        canonicalize_json_text('{"metadata":{"title":"first","title":"second"}}')


def test_canonicalization_rejects_invalid_json() -> None:
    """Invalid JSON should fail before canonicalization starts."""
    with pytest.raises(TrestleError, match='Input is not valid JSON'):
        canonicalize_json_text('{"metadata":')


def test_canonicalization_rejects_non_finite_numbers() -> None:
    """Non-finite numeric values are outside valid canonical JSON."""
    with pytest.raises(TrestleError, match='Non-finite JSON number'):
        canonicalize_json_text('{"value": NaN}')


def test_canonicalization_uses_rfc8785_number_serialization() -> None:
    """Number output should match RFC 8785 / ECMAScript serialization examples."""
    _, canonical_bytes = canonicalize_json_text(
        '{"numbers":[333333333.33333329,1E30,4.50,2e-3,0.000000000000000000000000001]}'
    )

    assert canonical_bytes == b'{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27]}'


def test_canonicalization_matches_rfc8785_primitive_sample() -> None:
    """Canonical output should match the RFC 8785 primitive serialization sample."""
    _, canonical_bytes = canonicalize_json_text(
        r"""
        {
          "numbers": [333333333.33333329, 1E30, 4.50,
                      2e-3, 0.000000000000000000000000001],
          "string": "\u20ac$\u000F\u000aA'\u0042\u0022\u005c\\\"/",
          "literals": [null, true, false]
        }
        """
    )

    assert canonical_bytes == (
        b'{"literals":[null,true,false],'
        b'"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],'
        b'"string":"\xe2\x82\xac$\\u000f\\nA\'B\\"\\\\\\\\\\"/"}'
    )


def test_canonicalization_rejects_unsafe_integers() -> None:
    """Integers outside the I-JSON safe range should not be signed silently."""
    with pytest.raises(TrestleError, match='exceeds safe integer domain'):
        canonicalize_json_text('{"value": 9007199254740992}')


def test_canonicalization_rejects_number_overflow() -> None:
    """Numbers that parse to infinity should fail before signing."""
    with pytest.raises(TrestleError, match='not representable in JCS'):
        canonicalize_json_text('{"value": 1e9999}')


def test_canonicalization_uses_rfc8785_utf16_property_sorting() -> None:
    """Property sorting should follow RFC 8785 UTF-16 code unit ordering."""
    _, canonical_bytes = canonicalize_json_text(
        """
        {
          "\\u20ac": "Euro Sign",
          "\\r": "Carriage Return",
          "\\ufb33": "Hebrew Letter Dalet With Dagesh",
          "1": "One",
          "\\ud83d\\ude00": "Emoji: Grinning Face",
          "\\u0080": "Control",
          "\\u00f6": "Latin Small Letter O With Diaeresis"
        }
        """
    )

    assert canonical_bytes == (
        b'{"\\r":"Carriage Return","1":"One","\xc2\x80":"Control",'
        b'"\xc3\xb6":"Latin Small Letter O With Diaeresis",'
        b'"\xe2\x82\xac":"Euro Sign","\xf0\x9f\x98\x80":"Emoji: Grinning Face",'
        b'"\xef\xac\xb3":"Hebrew Letter Dalet With Dagesh"}'
    )


def test_canonicalization_rejects_invalid_unicode() -> None:
    """Lone surrogate code points should be rejected as invalid canonical JSON."""
    with pytest.raises(TrestleError, match='input contains non-UTF-8 codepoints'):
        canonicalize_json_text(r'{"value": "\ud800"}')


def test_canonicalization_rejects_non_json_python_values() -> None:
    """Programmatic callers should not silently canonicalize non-JSON values."""
    with pytest.raises(TrestleError, match='Unable to canonicalize JSON object according to RFC 8785'):
        canonicalize_json_object({'value': object()})


def test_load_canonical_json_file(tmp_path: pathlib.Path) -> None:
    """Files should load using the same strict canonicalization path as text."""
    json_path = tmp_path / 'catalog.json'
    json_path.write_text('{"catalog":{"uuid":"1","metadata":{"title":"demo"}}}', encoding='utf8')

    json_obj, canonical_bytes = load_canonical_json_file(json_path)

    assert json_obj['catalog']['metadata']['title'] == 'demo'
    assert canonical_bytes == b'{"catalog":{"metadata":{"title":"demo"},"uuid":"1"}}'


def test_load_canonical_json_file_handles_real_oscal_fixture() -> None:
    """Canonicalization should produce stable bytes for a real OSCAL JSON fixture."""
    json_path = test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json'

    json_obj, canonical_bytes = load_canonical_json_file(json_path)

    assert json_obj['catalog']['metadata']['title'] == 'Minimal Catalog'
    assert sha256_digest_hex(canonical_bytes) == 'a2d28078f30fd7db2a42bd02227b53881ef86647f84542e85a605075763926aa'


def test_load_canonical_json_file_rejects_missing_path(tmp_path: pathlib.Path) -> None:
    """Missing files should fail with a trestle error."""
    with pytest.raises(TrestleError, match='JSON path does not exist or is not a file'):
        load_canonical_json_file(tmp_path / 'missing.json')
