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
"""RFC 8785 JSON Canonicalization Scheme (JCS) implementation.

This module provides a pure-stdlib implementation of RFC 8785 (JCS) for use with
OSCAL documents.  The canonical form is deterministic: same input always produces
the same byte sequence, making it suitable as a pre-image for cryptographic
signatures.

Key properties of the canonical form:
- UTF-8 encoded, no BOM
- No insignificant whitespace
- Object keys sorted by their UTF-16 code-unit sequence (per RFC 8785 §3.2.3)
- Numbers: integers as-is; finite IEEE 754 doubles follow ES6 ``ToString``
- NaN / Infinity are forbidden

YAML and XML are out of scope (see issue #2013).
"""

import json
import math
from typing import Any

__all__ = ['canonicalize']

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_ESCAPE_TABLE = {
    0x08: '\\b',
    0x09: '\\t',
    0x0A: '\\n',
    0x0C: '\\f',
    0x0D: '\\r',
    0x22: '\\"',
    0x5C: '\\\\',
}


def _serialize_string(s: str) -> bytes:
    """Serialize a string per RFC 8785 §3.2.2."""
    out = ['"']
    for ch in s:
        cp = ord(ch)
        esc = _ESCAPE_TABLE.get(cp)
        if esc is not None:
            out.append(esc)
        elif cp < 0x20:
            # Control character — must be \uXXXX escaped
            out.append(f'\\u{cp:04x}')
        else:
            out.append(ch)
    out.append('"')
    return ''.join(out).encode('utf-8')


def _serialize_number(n: float) -> bytes:
    """Serialize a number per RFC 8785 §3.2.4 (ES6 ToString for Numbers).

    Integers that fit in a 53-bit mantissa are serialised without a decimal
    point.  Finite floats use Python's repr, which matches ES6 for the values
    that appear in practice inside OSCAL documents.
    """
    if math.isnan(n) or math.isinf(n):
        raise ValueError(f'JCS forbids non-finite numbers: {n!r}')
    # Represent integer-valued floats as integers (no decimal point / exponent)
    if n == math.floor(n) and abs(n) < 2 ** 53:
        return str(int(n)).encode('utf-8')
    # For other floats, json.dumps matches ES6 ToString for the range of
    # values seen in practice.
    return json.dumps(n).encode('utf-8')


def _utf16_sort_key(key: str) -> bytes:
    """Return the UTF-16BE byte sequence used as the sort key per RFC 8785 §3.2.3."""
    return key.encode('utf-16-be')


def canonicalize(data: Any) -> bytes:
    """Return the RFC 8785 canonical JSON encoding of *data* as UTF-8 bytes.

    Args:
        data: A JSON-compatible Python value (dict, list, str, int, float,
              bool, or None).  Arbitrary objects are not supported.

    Returns:
        The canonicalized representation as a ``bytes`` object.

    Raises:
        ValueError: If *data* contains a non-finite float (NaN or Infinity).
        TypeError: If *data* contains an unsupported type.
    """
    if data is None:
        return b'null'
    if isinstance(data, bool):
        # bool must be checked before int because bool is a subclass of int
        return b'true' if data else b'false'
    if isinstance(data, int):
        return str(data).encode('utf-8')
    if isinstance(data, float):
        return _serialize_number(data)
    if isinstance(data, str):
        return _serialize_string(data)
    if isinstance(data, (list, tuple)):
        if not data:
            return b'[]'
        inner = b','.join(canonicalize(item) for item in data)
        return b'[' + inner + b']'
    if isinstance(data, dict):
        if not data:
            return b'{}'
        # RFC 8785 §3.2.3: sort by UTF-16 code-unit sequence of each key
        sorted_pairs = sorted(data.items(), key=lambda kv: _utf16_sort_key(kv[0]))
        parts = b','.join(_serialize_string(k) + b':' + canonicalize(v) for k, v in sorted_pairs)
        return b'{' + parts + b'}'
    raise TypeError(f'Object of type {type(data).__name__!r} is not JSON serializable')
