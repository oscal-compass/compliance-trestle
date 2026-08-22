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
"""Canonical JSON helpers for reproducible OSCAL artifact digests."""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any, Dict, List, Tuple

import rfc8785

from trestle.common import const
from trestle.common.err import TrestleError


def load_canonical_json_file(path: pathlib.Path) -> Tuple[Any, bytes]:
    """Load a JSON document and return its parsed object and canonical bytes."""
    if not path.exists() or not path.is_file():
        raise TrestleError(f'JSON path does not exist or is not a file: {path}')

    return canonicalize_json_text(path.read_text(encoding=const.FILE_ENCODING))


def canonicalize_json_text(json_text: str) -> Tuple[Any, bytes]:
    """Parse JSON text and return its parsed object and canonical bytes."""
    try:
        json_obj = json.loads(
            json_text, object_pairs_hook=_object_pairs_without_duplicates, parse_constant=_reject_json_constant
        )
    except json.JSONDecodeError as error:
        raise TrestleError(f'Input is not valid JSON: {error}')

    return json_obj, canonicalize_json_object(json_obj)


def canonicalize_json_object(json_obj: Any) -> bytes:
    """Return RFC 8785 canonical UTF-8 bytes for a parsed JSON-compatible object."""
    try:
        return rfc8785.dumps(json_obj)
    except rfc8785.CanonicalizationError as error:
        raise TrestleError(f'Unable to canonicalize JSON object according to RFC 8785: {error}')


def sha256_digest_hex(data: bytes) -> str:
    """Return a SHA-256 digest for canonical bytes."""
    return hashlib.sha256(data).hexdigest()


def _object_pairs_without_duplicates(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    output: Dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise TrestleError(f'Duplicate JSON object key is not supported for canonicalization: {key}')
        output[key] = value
    return output


def _reject_json_constant(value: str) -> None:
    raise TrestleError(f'Non-finite JSON number is not supported for canonicalization: {value}')
