# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors.
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
"""
Security utilities for remote fetching operations.

Provides path validation to prevent path traversal attacks.
"""

import logging
import pathlib

from trestle.common.err import TrestleError

logger = logging.getLogger(__name__)


class PathSecurityValidator:
    """Validator for ensuring file paths remain within allowed boundaries."""

    @staticmethod
    def validate_url_path_for_cache(url_path: str) -> None:
        """
        Validate a URL path component to prevent path traversal attacks.

        Detects path traversal attempts (..) and raises an exception to block the attack.
        This prevents directory traversal attacks when constructing cache file paths.

        Args:
            url_path: The path component from a URL (e.g., from urlparse().path)

        Raises:
            TrestleError: If path contains traversal sequences (..)

        Example:
            >>> PathSecurityValidator.validate_url_path_for_cache('/normal/path.json')  # No exception
            >>> PathSecurityValidator.validate_url_path_for_cache('/../../../etc/passwd')  # Raises TrestleError
        """
        # Check for path traversal sequences
        if '..' in url_path:
            raise TrestleError(
                f'Security violation: Path traversal blocked. '
                f'URL path "{url_path}" contains ".." sequences which could '
                f'allow writing files outside the cache directory.'
            )

    @staticmethod
    def validate_cache_path(cache_path: pathlib.Path, cache_root: pathlib.Path) -> None:
        """
        Validate that a cache file path stays within the cache directory.

        Uses path resolution and relative_to() to ensure the resolved cache path
        is actually within the cache root directory, preventing path traversal attacks.

        Args:
            cache_path: The proposed cache file path to validate
            cache_root: The root cache directory that must contain the cache_path

        Raises:
            TrestleError: If cache_path resolves outside cache_root

        Example:
            >>> cache_root = pathlib.Path('/home/user/.trestle/cache')
            >>> cache_path = cache_root / 'evil.com' / '..' / '..' / 'etc' / 'passwd'
            >>> validate_cache_path(cache_path, cache_root)  # Raises TrestleError
        """
        # Resolve both paths to absolute, normalized paths
        resolved_cache = cache_path.resolve()
        resolved_root = cache_root.resolve()

        try:
            # Check if cache path is relative to (within) cache root
            resolved_cache.relative_to(resolved_root)

        except ValueError as e:
            # relative_to() raises ValueError if path is not relative to root
            raise TrestleError(
                f'Security violation: Cache path traversal blocked. '
                f'Attempted to write to "{resolved_cache}" which is outside '
                f'the cache directory "{resolved_root}"'
            ) from e
        except Exception as e:
            raise TrestleError(f'Error validating cache path "{cache_path}": {e}') from e


# Made with Bob
