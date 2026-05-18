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

    @staticmethod
    def validate_trestle_uri_path(uri_path: str) -> None:
        """
        Validate a trestle:// URI path component to prevent path traversal attacks.

        Detects path traversal attempts (..) in trestle:// URIs and raises an exception.
        This prevents directory traversal when resolving trestle:// references.

        Args:
            uri_path: The path component after 'trestle://' prefix

        Raises:
            TrestleError: If path contains traversal sequences (..)

        Example:
            >>> PathSecurityValidator.validate_trestle_uri_path('catalogs/nist/catalog.json')  # No exception
            >>> PathSecurityValidator.validate_trestle_uri_path('../../etc/passwd')  # Raises TrestleError
        """
        # Check for path traversal sequences
        if '..' in uri_path:
            raise TrestleError(
                f'Security violation: Path traversal blocked in trestle:// URI. '
                f'URI path "{uri_path}" contains ".." sequences which could '
                f'allow reading files outside the trestle workspace.'
            )

    @staticmethod
    def validate_local_path(local_path: pathlib.Path, trestle_root: pathlib.Path) -> None:
        """
        Validate that a local file path stays within the trestle workspace.

        Uses path resolution and is_relative_to() to ensure the resolved local path
        is actually within the trestle root directory, preventing path traversal attacks.

        Args:
            local_path: The proposed local file path to validate
            trestle_root: The trestle root directory that must contain the local_path

        Raises:
            TrestleError: If local_path resolves outside trestle_root

        Example:
            >>> trestle_root = pathlib.Path('/home/user/trestle-workspace')
            >>> local_path = trestle_root / 'catalogs' / '..' / '..' / 'etc' / 'passwd'
            >>> validate_local_path(local_path, trestle_root)  # Raises TrestleError
        """
        # Resolve both paths to absolute, normalized paths
        resolved_local = local_path.resolve()
        resolved_root = trestle_root.resolve()

        try:
            # Check if local path is relative to (within) trestle root
            resolved_local.relative_to(resolved_root)

        except ValueError as e:
            # relative_to() raises ValueError if path is not relative to root
            raise TrestleError(
                f'Security violation: Path traversal blocked. '
                f'Attempted to access "{resolved_local}" which is outside '
                f'the trestle workspace "{resolved_root}"'
            ) from e
        except Exception as e:
            raise TrestleError(f'Error validating local path "{local_path}": {e}') from e

    @staticmethod
    def validate_local_file_path(
        workspace_root: pathlib.Path, file_path: pathlib.Path, allow_outside_workspace: bool = False
    ) -> None:
        """Validate that a local file path is safe to access.

        This method provides defense-in-depth protection against arbitrary file access
        by validating both workspace boundaries and blocking known sensitive system files.

        Args:
            workspace_root: The trestle workspace root directory
            file_path: The file path to validate
            allow_outside_workspace: If True, allow access to files outside workspace (default: False)

        Raises:
            TrestleError: If the path is deemed unsafe

        Example:
            >>> workspace = pathlib.Path('/home/user/trestle-workspace')
            >>> file_path = pathlib.Path('/etc/passwd')
            >>> validate_local_file_path(workspace, file_path, allow_outside_workspace=False)
            # Raises TrestleError: Access to files outside workspace not allowed
            >>> validate_local_file_path(workspace, file_path, allow_outside_workspace=True)
            # Raises TrestleError: Attempt to access sensitive system file
        """
        resolved_workspace = workspace_root.resolve()
        resolved_file = file_path.resolve()

        try:
            if not allow_outside_workspace:
                # Ensure file is within workspace
                resolved_file.relative_to(resolved_workspace)
        except ValueError as e:
            if not allow_outside_workspace:
                raise TrestleError(
                    f'Access to files outside the trestle workspace is not allowed: {file_path}. '
                    'This is a security restriction to prevent arbitrary file access.'
                ) from e

        # Additional checks for sensitive system files
        # This provides defense-in-depth even when allow_outside_workspace=True
        # Comprehensive list covering Linux, macOS, and Windows
        sensitive_paths = [
            # Linux/Unix system files
            '/etc/passwd',
            '/etc/shadow',
            '/etc/group',
            '/etc/gshadow',
            '/etc/sudoers',
            '/etc/hosts',
            '/etc/ssh',
            '/etc/ssl',
            '/etc/pki',
            '/etc/security',
            '/proc/self/environ',
            '/proc/self/cmdline',
            '/proc/self/maps',
            '/sys/class/net',
            # User credential files (Linux/macOS)
            '/.ssh',
            '/.aws',
            '/.gnupg',
            '/.docker',
            '/.kube',
            '/.config/gcloud',
            '/root/.ssh',
            '/root/.aws',
            '/root/.gnupg',
            # macOS specific
            '/Library/Keychains',
            '/Library/',  # Broad but catches user home directories
            # Windows system directories
            'C:\\Windows\\System32',
            'C:\\Windows\\SysWOW64',
            'C:\\Windows\\System',
            'C:\\Windows\\security',
            'C:\\ProgramData\\Microsoft\\Crypto',
            # Windows credential files
            '\\AppData\\Local\\Microsoft\\Credentials',
            '\\AppData\\Roaming\\Microsoft\\Credentials',
            '\\AppData\\Local\\Microsoft\\Vault',
            # Common sensitive config locations
            '/var/log',
            '/var/run',
            'C:\\Windows\\Logs',
            # Database files
            '/var/lib/mysql',
            '/var/lib/postgresql',
            'C:\\Program Files\\MySQL',
            'C:\\Program Files\\PostgreSQL',
        ]

        # Check if the resolved path contains any sensitive patterns
        # Use both the original path and resolved path for checking
        file_str = str(resolved_file).lower()
        original_str = str(file_path).lower()

        for sensitive in sensitive_paths:
            sensitive_lower = sensitive.lower()
            # Check both original and resolved paths
            if sensitive_lower in file_str or sensitive_lower in original_str:
                raise TrestleError(
                    f'Attempt to access potentially sensitive system file: {file_path}. '
                    'This may indicate a security issue.'
                )


# Made with Bob
