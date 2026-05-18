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
"""Security tests for cache path traversal vulnerabilities."""

import pathlib

import pytest

import tests.test_utils as test_utils

from trestle.common.err import TrestleError
from trestle.core.remote.cache import HTTPSFetcher, SFTPFetcher
from trestle.core.remote.security import PathSecurityValidator


class TestPathValidation:
    """Test path validation functions."""

    def test_validate_url_path_normal(self) -> None:
        """Test that normal paths pass validation."""
        PathSecurityValidator.validate_url_path_for_cache('/normal/path.json')  # Should not raise
        PathSecurityValidator.validate_url_path_for_cache('/path/to/file.json')  # Should not raise
        PathSecurityValidator.validate_url_path_for_cache('/data/catalog.json')  # Should not raise

    def test_validate_url_path_blocks_traversal(self) -> None:
        """Test that paths with .. are blocked."""
        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            PathSecurityValidator.validate_url_path_for_cache('/../../../etc/passwd')

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            PathSecurityValidator.validate_url_path_for_cache('/path/../file.json')

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            PathSecurityValidator.validate_url_path_for_cache('/../file.json')

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            PathSecurityValidator.validate_url_path_for_cache('/../../../../../../tmp/pwned.json')


class TestPathSecurityValidator:
    """Test path security validation."""

    def test_validate_cache_path_within_cache(self, tmp_path: pathlib.Path) -> None:
        """Test that valid paths within cache are accepted."""
        cache_root = tmp_path / '.trestle' / 'cache'
        cache_root.mkdir(parents=True)

        # Valid path within cache
        valid_path = cache_root / 'example.com' / 'data' / 'file.json'
        PathSecurityValidator.validate_cache_path(valid_path, cache_root)  # Should not raise

    def test_validate_cache_path_traversal_blocked(self, tmp_path: pathlib.Path) -> None:
        """Test that path traversal outside cache is blocked."""
        cache_root = tmp_path / '.trestle' / 'cache'
        cache_root.mkdir(parents=True)

        # Attempt to traverse outside cache
        evil_path = cache_root / '..' / '..' / 'etc' / 'passwd'

        with pytest.raises(TrestleError, match='Security violation.*path traversal blocked'):
            PathSecurityValidator.validate_cache_path(evil_path, cache_root)

    def test_validate_cache_path_absolute_outside_blocked(self, tmp_path: pathlib.Path) -> None:
        """Test that absolute paths outside cache are blocked."""
        cache_root = tmp_path / '.trestle' / 'cache'
        cache_root.mkdir(parents=True)

        # Absolute path outside cache
        evil_path = pathlib.Path('/tmp/pwned.json')

        with pytest.raises(TrestleError, match='Security violation.*path traversal blocked'):
            PathSecurityValidator.validate_cache_path(evil_path, cache_root)

    def test_validate_cache_path_unexpected_error(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that unexpected errors during validation are caught and wrapped."""
        cache_root = tmp_path / '.trestle' / 'cache'
        cache_root.mkdir(parents=True)

        valid_path = cache_root / 'example.com' / 'file.json'

        # Mock relative_to() to raise an unexpected exception (not ValueError)
        def mock_relative_to(self, other, *args, **kwargs):
            # Raise a non-ValueError exception to trigger the generic except block
            raise RuntimeError('Unexpected filesystem error')

        monkeypatch.setattr(pathlib.Path, 'relative_to', mock_relative_to)

        with pytest.raises(TrestleError, match='Error validating cache path'):
            PathSecurityValidator.validate_cache_path(valid_path, cache_root)


class TestHTTPSFetcherPathTraversal:
    """Test HTTPSFetcher protection against path traversal attacks."""

    def test_https_fetcher_blocks_path_traversal(self, tmp_path: pathlib.Path) -> None:
        """Test that HTTPSFetcher blocks path traversal in cache paths."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Malicious URL with path traversal
        evil_url = 'https://evil.com/../../../../../../../tmp/pwned.json'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            HTTPSFetcher(tmp_path, evil_url)

    def test_https_fetcher_allows_normal_paths(self, tmp_path: pathlib.Path) -> None:
        """Test that HTTPSFetcher allows normal paths without traversal."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Normal URL without traversal
        normal_url = 'https://example.com/catalogs/nist/catalog.json'

        # Should not raise
        fetcher = HTTPSFetcher(tmp_path, normal_url)

        # Verify cache path is within cache directory
        cache_dir = tmp_path / '.trestle' / 'cache'
        assert str(fetcher._cached_object_path).startswith(str(cache_dir))

    def test_https_fetcher_blocks_embedded_traversal(self, tmp_path: pathlib.Path) -> None:
        """Test that embedded path traversal sequences are blocked."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # URL with embedded traversal should be blocked
        url = 'https://example.com/path/../data/file.json'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            HTTPSFetcher(tmp_path, url)


class TestSFTPFetcherPathTraversal:
    """Test SFTPFetcher protection against path traversal attacks."""

    def test_sftp_fetcher_blocks_path_traversal(self, tmp_path: pathlib.Path) -> None:
        """Test that SFTPFetcher blocks path traversal in cache paths."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Malicious SFTP URL with path traversal
        evil_url = 'sftp://evil.com/../../../../../../../tmp/pwned.json'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            SFTPFetcher(tmp_path, evil_url)

    def test_sftp_fetcher_allows_normal_paths(self, tmp_path: pathlib.Path) -> None:
        """Test that SFTPFetcher allows normal paths without traversal."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Normal SFTP URL without traversal
        normal_url = 'sftp://example.com/data/catalog.json'

        # Should not raise
        fetcher = SFTPFetcher(tmp_path, normal_url)

        # Verify cache path is within cache directory
        cache_dir = tmp_path / '.trestle' / 'cache'
        assert str(fetcher._cached_object_path).startswith(str(cache_dir))

    def test_sftp_fetcher_blocks_embedded_traversal(self, tmp_path: pathlib.Path) -> None:
        """Test that embedded path traversal sequences are blocked."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # SFTP URL with embedded traversal should be blocked
        url = 'sftp://example.com/path/../data/file.json'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            SFTPFetcher(tmp_path, url)


class TestRealWorldAttackVectors:
    """Test real-world attack vectors from the security advisory."""

    def test_attack_vector_cron_injection(self, tmp_path: pathlib.Path) -> None:
        """Test blocking of cron job injection attack vector."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Attack: Write to /etc/cron.d/backdoor
        evil_url = 'https://evil.com/../../../../../../../etc/cron.d/backdoor'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            HTTPSFetcher(tmp_path, evil_url)

    def test_attack_vector_ssh_keys(self, tmp_path: pathlib.Path) -> None:
        """Test blocking of SSH authorized_keys injection."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Attack: Write to ~/.ssh/authorized_keys
        evil_url = 'https://evil.com/../../../../../../../root/.ssh/authorized_keys'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            HTTPSFetcher(tmp_path, evil_url)

    def test_attack_vector_tmp_write(self, tmp_path: pathlib.Path) -> None:
        """Test blocking of arbitrary /tmp file write."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Attack: Write to /tmp/pwned.json
        evil_url = 'https://evil.com/../../../tmp/pwned.json'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            HTTPSFetcher(tmp_path, evil_url)

    def test_attack_vector_config_overwrite(self, tmp_path: pathlib.Path) -> None:
        """Test blocking of config file overwrite."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Attack: Overwrite nginx config
        evil_url = 'https://evil.com/../../../../../../../etc/nginx/conf.d/evil.conf'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            HTTPSFetcher(tmp_path, evil_url)

    def test_attack_vector_sftp_private_network(self, tmp_path: pathlib.Path) -> None:
        """Test blocking of SFTP path traversal to system files."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Attack: SFTP to internal host with path traversal
        evil_url = 'sftp://192.168.1.1/../../../../../../../etc/passwd'

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked'):
            SFTPFetcher(tmp_path, evil_url)


# Made with Bob
