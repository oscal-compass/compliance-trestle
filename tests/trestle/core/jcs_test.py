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
"""Tests for trestle.common.jcs (RFC 8785 JSON Canonicalization Scheme)."""

import json
import math

import pytest

from trestle.common.jcs import canonicalize


# ---------------------------------------------------------------------------
# Basic type serialization
# ---------------------------------------------------------------------------

def test_null() -> None:
    assert canonicalize(None) == b'null'


def test_booleans() -> None:
    assert canonicalize(True) == b'true'
    assert canonicalize(False) == b'false'


def test_integers() -> None:
    assert canonicalize(0) == b'0'
    assert canonicalize(42) == b'42'
    assert canonicalize(-7) == b'-7'


def test_floats() -> None:
    # Integer-valued float → no decimal point
    assert canonicalize(1.0) == b'1'
    assert canonicalize(-0.0) == b'0'
    # Non-integer float round-trips via json.dumps
    result = canonicalize(1.5)
    assert result == json.dumps(1.5).encode('utf-8')


def test_non_finite_float_raises() -> None:
    with pytest.raises(ValueError):
        canonicalize(math.nan)
    with pytest.raises(ValueError):
        canonicalize(math.inf)


def test_string_plain() -> None:
    assert canonicalize('hello') == b'"hello"'


def test_string_escaping() -> None:
    # Backslash and double-quote must be escaped
    assert canonicalize('a\\b') == b'"a\\\\b"'
    assert canonicalize('say "hi"') == b'"say \\"hi\\""'
    # Tab, newline, carriage return, backspace, formfeed
    assert canonicalize('\t') == b'"\\t"'
    assert canonicalize('\n') == b'"\\n"'
    assert canonicalize('\r') == b'"\\r"'
    assert canonicalize('\b') == b'"\\b"'
    assert canonicalize('\f') == b'"\\f"'
    # Control characters < 0x20
    assert canonicalize('\x00') == b'"\\u0000"'
    assert canonicalize('\x1f') == b'"\\u001f"'


def test_string_unicode() -> None:
    # Non-ASCII characters pass through unescaped in UTF-8
    result = canonicalize('caf\u00e9')
    assert result == '"café"'.encode('utf-8')


def test_empty_list() -> None:
    assert canonicalize([]) == b'[]'


def test_list() -> None:
    assert canonicalize([1, 'a', None]) == b'[1,"a",null]'


def test_empty_dict() -> None:
    assert canonicalize({}) == b'{}'


def test_dict_key_sorting() -> None:
    # Keys must be sorted by their UTF-16BE byte sequence (per RFC 8785 §3.2.3)
    # For ASCII keys this is the same as Unicode code point order
    data = {'b': 2, 'a': 1, 'c': 3}
    result = canonicalize(data)
    assert result == b'{"a":1,"b":2,"c":3}'


def test_dict_key_sorting_utf16() -> None:
    # Unicode keys: sort by UTF-16 code units, not UTF-8 bytes
    # '\u00e9' (é) has UTF-16BE bytes 0x00 0xe9
    # 'z' has UTF-16BE bytes 0x00 0x7a
    # 0x7a < 0xe9 so 'z' sorts before 'é'
    data = {'\u00e9': 1, 'z': 2}
    result = canonicalize(data)
    assert result == '{"z":2,"\u00e9":1}'.encode('utf-8')


def test_nested_structure() -> None:
    data = {'z': [3, 1], 'a': {'y': False, 'x': None}}
    result = canonicalize(data)
    # Keys must be sorted at every level
    assert result == b'{"a":{"x":null,"y":false},"z":[3,1]}'


def test_determinism() -> None:
    """Same input always produces identical output."""
    data = {'beta': [1, 2], 'alpha': {'val': True}}
    assert canonicalize(data) == canonicalize(data)


def test_unsupported_type_raises() -> None:
    with pytest.raises(TypeError):
        canonicalize(object())  # type: ignore
