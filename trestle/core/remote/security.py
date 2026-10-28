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
Security validation utilities for remote fetching operations.

This module provides security controls to prevent SSRF, path traversal,
and arbitrary file access vulnerabilities.
"""

import ipaddress
import logging
import os
import pathlib
import socket
from typing import Optional, Set
from urllib import parse

from trestle.common.err import TrestleError


def get_block_private_ips_config() -> bool:
    """Get the TRESTLE_BLOCK_PRIVATE_IPS configuration from environment.

    Returns:
        True if private IPs should be blocked, False otherwise (default).

    The environment variable can be set to:
    - 'true', '1', 'yes', 'on' (case-insensitive) to enable blocking
    - Any other value or unset to disable blocking (allow private IPs)
    """
    env_value = os.environ.get('TRESTLE_BLOCK_PRIVATE_IPS', '').lower()
    return env_value in ('true', '1', 'yes', 'on')


logger = logging.getLogger(__name__)

# Always blocked - zero legitimate use for OSCAL fetching
# These ranges are blocked regardless of configuration
ALWAYS_BLOCKED_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),  # IPv4 loopback
    ipaddress.ip_network('::1/128'),  # IPv6 loopback
    ipaddress.ip_network('169.254.0.0/16'),  # IPv4 link-local (includes metadata endpoints)
    ipaddress.ip_network('fe80::/10'),  # IPv6 link-local
    ipaddress.ip_network('0.0.0.0/8'),  # IPv4 "this network", reaches localhost on Linux
    ipaddress.ip_network('::/128'),  # IPv6 unspecified address
    # Alibaba Cloud metadata endpoint. It lies in 100.64.0.0/10 (CGNAT, RFC 6598), which is not otherwise
    # blocked, so it must be blocked by resolved IP to prevent bypass via DNS pointing at it.
    ipaddress.ip_network('100.100.100.200/32'),  # NOSONAR - IP is deliberately hardcoded to block access to it
]

# RFC 1918 private ranges - optionally blocked based on configuration
# These are allowed by default to support private GitLab/internal OSCAL repositories
PRIVATE_IP_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('fc00::/7'),  # IPv6 unique local
]

# Cloud metadata endpoints that should be blocked
# These are always blocked regardless of configuration
METADATA_HOSTNAMES = {
    '169.254.169.254',  # AWS, Azure, GCP
    'metadata.google.internal',  # GCP
    'metadata.azure.com',  # Azure (alternative)
    '100.100.100.200',  # Alibaba Cloud
}


class URLSecurityValidator:
    """Validates URLs to prevent SSRF attacks.

    Implements two-tiered SSRF protection:
    1. Always blocked: loopback, link-local, and cloud metadata endpoints
    2. Optionally blocked: RFC 1918 private ranges (configurable via block_private_ips)
    """

    def __init__(self, block_private_ips: bool = False, allowed_domains: Optional[Set[str]] = None):
        """Initialize URL security validator.

        Args:
            block_private_ips: If True, block RFC 1918 private IP ranges (default: False).
                              Always-blocked ranges (loopback, link-local, metadata) are blocked regardless.
            allowed_domains: Optional set of allowed domain names. If provided, only these domains are allowed.
        """
        self.block_private_ips = block_private_ips
        self.allowed_domains = allowed_domains

    def validate_url(self, url: str) -> None:
        """Validate a URL for security issues.

        This method resolves the hostname and validates all resolved IPs to prevent SSRF attacks.

        To mitigate DNS rebinding attacks, this validation is called both at initialization and
        immediately before each fetch operation, minimizing the TOCTOU window.

        Args:
            url: The URL to validate

        Raises:
            TrestleError: If the URL is deemed unsafe
        """
        parsed = self._parse_and_validate_url(url)
        # hostname is guaranteed to be non-None by _parse_and_validate_url
        hostname = parsed.hostname.lower()  # type: ignore

        self._check_metadata_endpoints(hostname)
        self._check_domain_allowlist(hostname)

        ip_addresses = self._resolve_hostname(hostname)

        for ip_str in ip_addresses:
            parsed_ip = self._parse_ip_address(ip_str, hostname)
            # Canonicalize IPv6 transition addresses before validation
            for ip_addr in self._canonicalize_ips(parsed_ip):
                self._check_blocked_networks(ip_addr, hostname)
                self._check_private_networks(ip_addr, hostname)

        self._check_suspicious_ports(parsed, url)

    def _canonicalize_ips(
        self, ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address
    ) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
        """Unwrap IPv6 transition addresses that embed an IPv4 address.

        Handles all IPv6 forms that carry an embedded IPv4 address so that the
        blocklist and private-network checks are applied to the true IPv4 destination
        rather than the outer IPv6 literal.  Fixes CVE-2026-114511 / GHSA-jj4m-34f2-rwc9.

        Forms handled:
        - IPv4-mapped  ``::ffff:0:0/96``  (already handled pre-fix)
        - IPv4-compatible  ``::/96``       (low 32 bits are the IPv4 address)
        - NAT64 Well-Known Prefix  ``64:ff9b::/96``  (RFC 6052; low 32 bits)
        - NAT64 Local-Use Prefix  ``64:ff9b:1::/48``  (RFC 8215, RFC 6052; /48, /56, /64, /96)
        - 6to4   ``2002::/16``  (RFC 3056; bits 16-47 are the IPv4 address)
        - Teredo ``2001::/32``  (RFC 4380; client and server IPv4 addresses)

        Args:
            ip_addr: The IP address to canonicalize.

        Returns:
            A list of unwrapped candidate IPv4Address objects (or the original address
            in a single-element list if no transition form is detected).
        """
        if not isinstance(ip_addr, ipaddress.IPv6Address):
            return [ip_addr]

        # IPv4-mapped ::ffff:a.b.c.d
        if ip_addr.ipv4_mapped is not None:
            return [ip_addr.ipv4_mapped]

        packed = ip_addr.packed  # 16 bytes, big-endian

        # IPv4-compatible ::/96 — all upper 12 bytes are zero, low 4 bytes are IPv4.
        # Exclude :: (unspecified, ::/128) and ::1 (IPv6 loopback, ::1/128) — both are
        # already in ALWAYS_BLOCKED_NETWORKS and should not be re-classified as IPv4.
        if packed[:12] == b'\x00' * 12 and packed[12:] not in (b'\x00' * 4, b'\x00\x00\x00\x01'):
            return [ipaddress.IPv4Address(packed[12:])]

        # NAT64 Well-Known Prefix 64:ff9b::/96 (RFC 6052).
        # Prefix length is strictly /96; the embedded IPv4 occupies the low 32 bits.
        if ip_addr in ipaddress.ip_network('64:ff9b::/96'):
            return [ipaddress.IPv4Address(packed[12:])]

        # NAT64 Local-Use Prefix 64:ff9b:1::/48 (RFC 8215, RFC 6052).
        # Depending on deployment configuration, prefix length may be /48, /56, /64, or /96.
        # Suffix and the 'u' octet (byte 8) must be zero for /48, /56, /64 per RFC 6052 sec 2.2.
        if ip_addr in ipaddress.ip_network('64:ff9b:1::/48'):
            candidates: list[ipaddress.IPv4Address] = []
            if packed[8] == 0:
                # /48: IPv4 in bytes 6..7 and 9..10; suffix in bytes 11..15 must be zero
                if packed[11:16] == b'\x00' * 5:
                    candidates.append(ipaddress.IPv4Address(packed[6:8] + packed[9:11]))
                # /56: IPv4 in bytes 7 and 9..11; suffix in bytes 12..15 must be zero
                if packed[12:16] == b'\x00' * 4:
                    candidates.append(ipaddress.IPv4Address(packed[7:8] + packed[9:12]))
                # /64: IPv4 in bytes 9..12; suffix in bytes 13..15 must be zero
                if packed[13:16] == b'\x00' * 3:
                    candidates.append(ipaddress.IPv4Address(packed[9:13]))
            # /96: IPv4 in bytes 12..15 (no suffix)
            candidates.append(ipaddress.IPv4Address(packed[12:16]))
            return list(dict.fromkeys(candidates))

        # 6to4 2002::/16 (RFC 3056) — Python exposes this via .sixtofour
        if ip_addr.sixtofour is not None:
            return [ip_addr.sixtofour]

        # Teredo 2001::/32 (RFC 4380) — Python exposes server and client via .teredo.
        # Validate both client and server addresses so blocklist checks cover both.
        if ip_addr.teredo is not None:
            teredo_server, teredo_client = ip_addr.teredo
            return list(dict.fromkeys([teredo_client, teredo_server]))

        return [ip_addr]

    def _canonicalize_ip(
        self, ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address
    ) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        """Unwrap IPv6 transition address to its primary embedded IPv4 address.

        For single-interpretation addresses, returns the embedded IPv4Address or original address.
        For multi-prefix addresses (such as local-use NAT64), returns the first candidate.
        Use _canonicalize_ips() to inspect all candidates.
        """
        return self._canonicalize_ips(ip_addr)[0]

    def _parse_and_validate_url(self, url: str) -> parse.ParseResult:
        """Parse and validate basic URL structure."""
        try:
            parsed = parse.urlparse(url)
        except Exception as e:
            raise TrestleError(f'Invalid URL format: {url}') from e

        if not parsed.scheme or not parsed.hostname:
            raise TrestleError(f'URL must include scheme and hostname: {url}')

        if parsed.scheme not in ['https', 'sftp']:
            raise TrestleError(f'Only HTTPS or SFTP schemes are allowed for remote URLs, got: {parsed.scheme}')

        return parsed

    def _check_metadata_endpoints(self, hostname: str) -> None:
        """Check if hostname is a blocked metadata endpoint.

        Canonicalizes bracketed IPv6 literal hostnames using the shared
        _canonicalize_ips helper so that all transition forms (IPv4-mapped,
        IPv4-compatible, NAT64, 6to4, Teredo) are unwrapped before the
        comparison against METADATA_HOSTNAMES.  Previously only IPv4-mapped was
        handled here; the gap was identified in GHSA-jj4m-34f2-rwc9.

        Note: This method is for URL-literal hostnames only (i.e., when the hostname
        in the URL itself is an IPv6 literal). DNS-resolved IPs are canonicalized
        upstream in validate_url via _canonicalize_ips before hostname-level checks.
        """
        # Strip brackets from IPv6 literals, e.g. [::ffff:169.254.169.254]
        canonical = hostname.strip('[]')
        try:
            canonical_ip = ipaddress.ip_address(canonical)
            # Use the shared helper — covers all transition forms and candidate unwraps.
            canonical_ips = [str(ip) for ip in self._canonicalize_ips(canonical_ip)]
        except ValueError:
            # Not an IP literal, use original hostname
            canonical_ips = [canonical]

        for cand in canonical_ips:
            if cand in METADATA_HOSTNAMES:
                raise TrestleError(
                    f'Access to cloud metadata endpoints is not allowed: {hostname}. '
                    'This is a security restriction to prevent SSRF attacks.'
                )

    def _check_domain_allowlist(self, hostname: str) -> None:
        """Check if hostname is in the allowed domains list."""
        if self.allowed_domains is not None:
            if hostname not in self.allowed_domains:
                raise TrestleError(
                    f'Domain {hostname} is not in the allowed domains list. '
                    f'Allowed domains: {", ".join(sorted(self.allowed_domains))}'
                )

    def _resolve_hostname(self, hostname: str) -> list:
        """Resolve hostname to IP addresses."""
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            ip_addresses = [str(info[4][0]) for info in addr_info]
        except socket.gaierror as e:
            raise TrestleError(f'Unable to resolve hostname {hostname}: {e}') from e

        if not ip_addresses:
            raise TrestleError(f'No IP addresses resolved for hostname {hostname}')

        return ip_addresses

    def _parse_ip_address(self, ip_str: str, hostname: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        """Parse IP address string."""
        try:
            return ipaddress.ip_address(ip_str)
        except ValueError as e:
            raise TrestleError(f'Invalid IP address {ip_str} for hostname {hostname}: {e}') from e

    def _check_blocked_networks(self, ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address, hostname: str) -> None:
        """Check if IP is in always-blocked networks (Tier 1).

        Note: ip_addr should already be canonicalized by validate_url before calling this method.
        """
        # Defensive check: ensure IPv4-mapped IPv6 addresses are canonicalized
        # This protects against future refactoring that might skip canonicalization
        if isinstance(ip_addr, ipaddress.IPv6Address) and ip_addr.ipv4_mapped is not None:
            raise TrestleError(
                f'Internal error: IP address {ip_addr} should have been canonicalized before network checks. '
                'IPv4-mapped IPv6 addresses must be converted to IPv4 form.'
            )

        for network in ALWAYS_BLOCKED_NETWORKS:
            # Only check if IP version matches network version to avoid TypeError
            if ip_addr.version == network.version and ip_addr in network:
                raise TrestleError(
                    f'Access to {network} addresses is blocked: {hostname} resolves to {ip_addr}. '
                    f'This range includes loopback, link-local, and cloud metadata endpoints. '
                    f'This is a security restriction to prevent SSRF attacks.'
                )

    def _check_private_networks(self, ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address, hostname: str) -> None:
        """Check if IP is in private networks (Tier 2)."""
        if self.block_private_ips:
            self._block_private_ip(ip_addr, hostname)
        else:
            self._warn_private_ip(ip_addr, hostname)

    def _block_private_ip(self, ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address, hostname: str) -> None:
        """Block access to private IP addresses when configured.

        Note: ip_addr should already be canonicalized by validate_url before calling this method.
        """
        # Defensive check: ensure IPv4-mapped IPv6 addresses are canonicalized
        if isinstance(ip_addr, ipaddress.IPv6Address) and ip_addr.ipv4_mapped is not None:
            raise TrestleError(
                f'Internal error: IP address {ip_addr} should have been canonicalized before network checks. '
                'IPv4-mapped IPv6 addresses must be converted to IPv4 form.'
            )

        for network in PRIVATE_IP_NETWORKS:
            # Only check if IP version matches network version to avoid TypeError
            if ip_addr.version == network.version and ip_addr in network:
                raise TrestleError(
                    f'Access to private IP addresses is blocked: {hostname} resolves to {ip_addr} '
                    f'which is in private network {network}. '
                    f'This is blocked because TRESTLE_BLOCK_PRIVATE_IPS is enabled. '
                    f'To allow access to private networks, unset this environment variable.'
                )

    def _warn_private_ip(self, ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address, hostname: str) -> None:
        """Log warning when accessing private IP addresses.

        Note: ip_addr should already be canonicalized by validate_url before calling this method.
        """
        # Defensive check: ensure IPv4-mapped IPv6 addresses are canonicalized
        if isinstance(ip_addr, ipaddress.IPv6Address) and ip_addr.ipv4_mapped is not None:
            raise TrestleError(
                f'Internal error: IP address {ip_addr} should have been canonicalized before network checks. '
                'IPv4-mapped IPv6 addresses must be converted to IPv4 form.'
            )

        for network in PRIVATE_IP_NETWORKS:
            # Only check if IP version matches network version to avoid TypeError
            if ip_addr.version == network.version and ip_addr in network:
                logger.warning(
                    f'Accessing private IP address: {hostname} resolves to {ip_addr} in network {network}. '
                    f'This is allowed by default to support private GitLab/internal OSCAL repositories. '
                    f'To block private IPs, set TRESTLE_BLOCK_PRIVATE_IPS=true.'
                )
                break  # Only log once per IP

    def _check_suspicious_ports(self, parsed: parse.ParseResult, url: str) -> None:
        """Check for non-standard ports."""
        if parsed.port is not None:
            if (
                parsed.scheme == 'https'
                and parsed.port not in [443]
                or parsed.scheme == 'sftp'
                and parsed.port not in [22]
            ):
                logger.warning(
                    f'Non-standard port {parsed.port} detected in URL {url}. This may indicate a security risk.'
                )


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
            >>> PathSecurityValidator.validate_url_path_for_cache(
            ...     '/normal/path.json'
            ... )  # No exception
            >>> PathSecurityValidator.validate_url_path_for_cache(
            ...     '/../../../etc/passwd'
            ... )  # Raises TrestleError
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
            >>> PathSecurityValidator.validate_trestle_uri_path(
            ...     'catalogs/nist/catalog.json'
            ... )  # No exception
            >>> PathSecurityValidator.validate_trestle_uri_path(
            ...     '../../etc/passwd'
            ... )  # Raises TrestleError
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
