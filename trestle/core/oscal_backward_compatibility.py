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
"""Pre-parse OSCAL backward-compatibility checker.

Inspects the raw JSON dict of an OSCAL document *before* Pydantic parsing and
reports constructs that are incompatible with OSCAL 1.2.x.  This allows trestle
to emit clear, actionable error messages instead of cryptic Pydantic validation
errors when older documents are loaded.
"""

import json
import logging
import pathlib
import re
from typing import Any, Dict, List, NamedTuple

from trestle.oscal import OSCAL_VERSION, OSCAL_VERSION_REGEX

logger = logging.getLogger(__name__)

# Changed in OSCAL 1.2.0: valid values for profile/alter/remove.by-item-name
# are constrained to this enum.
_ITEM_NAME_VALID_VALUES = {'param', 'prop', 'link', 'part', 'mapping', 'map'}

# Changed in OSCAL 1.2.0: metadata datetime fields must include an explicit
# timezone offset (Z or ±HH:MM) rather than a naive local datetime.
_AWARE_DATETIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$')


class CompatIssue(NamedTuple):
    """A single backward-compatibility issue found in a raw OSCAL document."""

    field_path: str
    message: str
    severity: str  # 'ERROR' or 'WARNING'

    def __str__(self) -> str:
        return f'COMPAT {self.severity}: {self.field_path} — {self.message}'


def check_raw_oscal(raw: Dict[str, Any]) -> List[CompatIssue]:
    """Inspect a raw OSCAL JSON dict and return all backward-compatibility issues.

    Args:
        raw: The top-level parsed JSON dict of an OSCAL document.

    Returns:
        A list of CompatIssue.  Empty list means no issues detected.
    """
    issues: List[CompatIssue] = []

    # The top-level key is the document type, e.g. "profile", "catalog"
    if not raw or not isinstance(raw, dict) or len(raw) != 1:
        return issues
    doc_type = next(iter(raw))
    doc = raw[doc_type]

    # --- metadata datetime fields ---
    # Changed in OSCAL 1.2.0: these metadata timestamps require timezone-aware
    # values.
    metadata = doc.get('metadata', {})
    _check_aware_datetime(metadata, 'last-modified', f'{doc_type}.metadata.last-modified', issues)
    _check_aware_datetime(metadata, 'published', f'{doc_type}.metadata.published', issues)
    for i, rev in enumerate(metadata.get('revisions', [])):
        _check_aware_datetime(rev, 'last-modified', f'{doc_type}.metadata.revisions[{i}].last-modified', issues)
        _check_aware_datetime(rev, 'published', f'{doc_type}.metadata.revisions[{i}].published', issues)

    # --- profile-specific checks ---
    # These checks target profile constructs whose shape changed in OSCAL 1.2.0.
    if doc_type == 'profile':
        _check_profile(doc, issues)

    # --- oscal-version ---
    # Only warn about an out-of-range version when structural errors are already
    # present; a version mismatch on an otherwise-clean document is harmless.
    if any(i.severity == 'ERROR' for i in issues):
        _check_oscal_version(doc, issues)

    return issues


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _check_oscal_version(doc: Dict[str, Any], issues: List[CompatIssue]) -> None:
    metadata = doc.get('metadata', {})
    version = metadata.get('oscal-version')
    if version is None:
        return
    # Strip a leading 'v' that some older documents include
    version_str = str(version).lstrip('v')
    pattern = re.compile(OSCAL_VERSION_REGEX)
    if not pattern.match(version_str):
        issues.append(
            CompatIssue(
                field_path='metadata.oscal-version',
                message=(
                    f"'{version}' is outside the supported range {OSCAL_VERSION_REGEX}. "
                    f'Current trestle target: {OSCAL_VERSION}. '
                    'Document constructs may not parse correctly.'
                ),
                severity='WARNING',
            )
        )


def _check_aware_datetime(obj: Dict[str, Any], key: str, path: str, issues: List[CompatIssue]) -> None:
    value = obj.get(key)
    if value is None or not isinstance(value, str):
        return
    if not _AWARE_DATETIME_RE.match(value):
        issues.append(
            CompatIssue(
                field_path=path,
                message=(
                    f"'{value}' has no timezone offset. "
                    'OSCAL 1.2.0 requires AwareDatetime (e.g. 2023-01-01T00:00:00+00:00 or ...Z).'
                ),
                severity='ERROR',
            )
        )


def _check_profile(doc: Dict[str, Any], issues: List[CompatIssue]) -> None:
    # Changed in OSCAL 1.2.0: profile.merge structure became stricter, and
    # remove.by-item-name is validated against the 1.2.0 enum values.
    merge = doc.get('merge')
    if merge is not None:
        _check_merge(merge, issues)

    for i, alter in enumerate(doc.get('modify', {}).get('alters', [])):
        for j, remove in enumerate(alter.get('removes', [])):
            _check_remove(remove, f'profile.modify.alters[{i}].removes[{j}]', issues)


def _check_merge(merge: Dict[str, Any], issues: List[CompatIssue]) -> None:
    # Changed in OSCAL 1.2.0: profile.merge.combine no longer allows legacy
    # properties such as method; if present it must be an empty object.
    combine = merge.get('combine')
    if combine is not None and isinstance(combine, dict) and len(combine) > 0:
        issues.append(
            CompatIssue(
                field_path='profile.merge.combine',
                message=(
                    f'contains keys {set(combine.keys())}. '
                    'In OSCAL 1.2.0 combine is an empty object (additionalProperties: false). '
                    "The 'method' property was removed — use combine: {} or omit combine entirely."
                ),
                severity='ERROR',
            )
        )

    # Changed in OSCAL 1.2.0: merge structuring is a one-of union, so only one
    # of flat / as-is / custom may appear.
    structuring = [k for k in ('flat', 'as-is', 'custom') if k in merge]
    if len(structuring) > 1:
        issues.append(
            CompatIssue(
                field_path='profile.merge',
                message=(
                    f'contains multiple structuring keys {structuring}. '
                    'OSCAL 1.2.0 requires exactly one of: flat, as-is, custom '
                    '(enforced by additionalProperties: false on each union branch).'
                ),
                severity='ERROR',
            )
        )


def _check_remove(remove: Dict[str, Any], path: str, issues: List[CompatIssue]) -> None:
    # Changed in OSCAL 1.2.0: remove.by-item-name is restricted to the
    # ItemNameValidValues enum.
    by_item_name = remove.get('by-item-name')
    if by_item_name is not None and by_item_name not in _ITEM_NAME_VALID_VALUES:
        issues.append(
            CompatIssue(
                field_path=f'{path}.by-item-name',
                message=(
                    f"'{by_item_name}' is not a valid ItemNameValidValues. "
                    f'Allowed values in OSCAL 1.2.0: {sorted(_ITEM_NAME_VALID_VALUES)}.'
                ),
                severity='ERROR',
            )
        )


def check_file(path: pathlib.Path) -> List[CompatIssue]:
    """Load a JSON file and run the backward-compatibility checks on it.

    Args:
        path: Path to a JSON OSCAL document.

    Returns:
        A list of CompatIssue.  Empty list means no issues detected.
        Returns an empty list if the file cannot be read or is not valid JSON —
        the subsequent model load will fail and report the error.
    """
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        logger.debug(f'Skipping compatibility checks for {path}: file could not be read or parsed as JSON: {e}')
        return []
    return check_raw_oscal(raw)
