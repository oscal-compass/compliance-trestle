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
import socket
import sys

import pytest

import tests.test_utils as test_utils

from trestle.common.err import TrestleError
from trestle.core.remote.cache import HTTPSFetcher, SFTPFetcher
from trestle.core.remote.security import PathSecurityValidator, URLSecurityValidator


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


class TestTrestleURIPathValidation:
    """Test trestle:// URI path validation."""

    def test_validate_trestle_uri_path_normal(self) -> None:
        """Test that normal trestle:// URI paths pass validation."""
        PathSecurityValidator.validate_trestle_uri_path('catalogs/nist/catalog.json')
        PathSecurityValidator.validate_trestle_uri_path('profiles/fedramp/profile.json')
        PathSecurityValidator.validate_trestle_uri_path('components/mycomp/component.json')

    def test_validate_trestle_uri_path_blocks_traversal(self) -> None:
        """Test that trestle:// URI paths with .. are blocked."""
        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked.*trestle://'):
            PathSecurityValidator.validate_trestle_uri_path('../../etc/passwd')

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked.*trestle://'):
            PathSecurityValidator.validate_trestle_uri_path('catalogs/../../../etc/shadow')

        with pytest.raises(TrestleError, match='Security violation:.*[Pp]ath traversal blocked.*trestle://'):
            PathSecurityValidator.validate_trestle_uri_path('../sensitive/file.json')


class TestLocalPathValidation:
    """Test local path validation."""

    def test_validate_local_path_within_workspace(self, tmp_path: pathlib.Path) -> None:
        """Test that valid paths within trestle workspace are accepted."""
        trestle_root = tmp_path / 'trestle-workspace'
        trestle_root.mkdir(parents=True)

        # Valid path within workspace
        valid_path = trestle_root / 'catalogs' / 'nist' / 'catalog.json'
        PathSecurityValidator.validate_local_path(valid_path, trestle_root)  # Should not raise

    def test_validate_local_path_traversal_blocked(self, tmp_path: pathlib.Path) -> None:
        """Test that path traversal outside workspace is blocked."""
        trestle_root = tmp_path / 'trestle-workspace'
        trestle_root.mkdir(parents=True)

        # Attempt to traverse outside workspace
        evil_path = trestle_root / '..' / '..' / 'etc' / 'passwd'

        with pytest.raises(TrestleError, match='Security violation.*[Pp]ath traversal blocked'):
            PathSecurityValidator.validate_local_path(evil_path, trestle_root)

    def test_validate_local_path_absolute_outside_blocked(self, tmp_path: pathlib.Path) -> None:
        """Test that absolute paths outside workspace are blocked."""
        trestle_root = tmp_path / 'trestle-workspace'
        trestle_root.mkdir(parents=True)

        # Absolute path outside workspace
        evil_path = pathlib.Path('/tmp/pwned.json')

        with pytest.raises(TrestleError, match='Security violation.*[Pp]ath traversal blocked'):
            PathSecurityValidator.validate_local_path(evil_path, trestle_root)

    def test_validate_local_path_unexpected_error(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that unexpected errors during validation are caught and wrapped."""
        trestle_root = tmp_path / 'trestle-workspace'
        trestle_root.mkdir(parents=True)

        valid_path = trestle_root / 'catalogs' / 'file.json'

        # Mock relative_to() to raise an unexpected exception (not ValueError)
        def mock_relative_to(self, other, *args, **kwargs):
            raise RuntimeError('Unexpected filesystem error')

        monkeypatch.setattr(pathlib.Path, 'relative_to', mock_relative_to)

        with pytest.raises(TrestleError, match='Error validating local path'):
            PathSecurityValidator.validate_local_path(valid_path, trestle_root)


class TestLocalFilePathValidation:
    """Test local file path validation with workspace boundaries and sensitive file checks."""

    def test_validate_local_file_path_within_workspace(self, tmp_path: pathlib.Path) -> None:
        """Test that files within workspace are allowed."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        file_path = workspace / 'catalogs' / 'catalog.json'
        PathSecurityValidator.validate_local_file_path(workspace, file_path, allow_outside_workspace=False)

    def test_validate_local_file_path_outside_workspace_blocked(self, tmp_path: pathlib.Path) -> None:
        """Test that files outside workspace are blocked when allow_outside_workspace=False."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        outside_file = tmp_path / 'outside.json'

        with pytest.raises(TrestleError, match='Access to files outside the trestle workspace is not allowed'):
            PathSecurityValidator.validate_local_file_path(workspace, outside_file, allow_outside_workspace=False)

    def test_validate_local_file_path_outside_workspace_allowed(self, tmp_path: pathlib.Path) -> None:
        """Test that non-sensitive files outside workspace are allowed when allow_outside_workspace=True."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        # Create a safe file outside workspace
        outside_file = tmp_path / 'safe_file.json'
        outside_file.touch()

        # Should not raise
        PathSecurityValidator.validate_local_file_path(workspace, outside_file, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_etc_passwd(self, tmp_path: pathlib.Path) -> None:
        """Test that /etc/passwd is blocked even with allow_outside_workspace=True."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        passwd_path = pathlib.Path('/etc/passwd')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, passwd_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_etc_shadow(self, tmp_path: pathlib.Path) -> None:
        """Test that /etc/shadow is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        shadow_path = pathlib.Path('/etc/shadow')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, shadow_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_etc_group(self, tmp_path: pathlib.Path) -> None:
        """Test that /etc/group is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        group_path = pathlib.Path('/etc/group')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, group_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_etc_sudoers(self, tmp_path: pathlib.Path) -> None:
        """Test that /etc/sudoers is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        sudoers_path = pathlib.Path('/etc/sudoers')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, sudoers_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_ssh_directory(self, tmp_path: pathlib.Path) -> None:
        """Test that .ssh directory is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        ssh_path = pathlib.Path('/home/user/.ssh/id_rsa')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, ssh_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_aws_credentials(self, tmp_path: pathlib.Path) -> None:
        """Test that .aws credentials are blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        aws_path = pathlib.Path('/home/user/.aws/credentials')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, aws_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_docker_config(self, tmp_path: pathlib.Path) -> None:
        """Test that .docker config is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        docker_path = pathlib.Path('/home/user/.docker/config.json')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, docker_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_kube_config(self, tmp_path: pathlib.Path) -> None:
        """Test that .kube config is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        kube_path = pathlib.Path('/home/user/.kube/config')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, kube_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_proc_environ(self, tmp_path: pathlib.Path) -> None:
        """Test that /proc/self/environ is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        proc_path = pathlib.Path('/proc/self/environ')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, proc_path, allow_outside_workspace=True)

    def test_validate_local_file_path_blocks_windows_system32(self, tmp_path: pathlib.Path) -> None:
        """Test that Windows System32 is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        win_path = pathlib.Path('C:\\Windows\\System32\\config\\SAM')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, win_path, allow_outside_workspace=True)

    def test_validate_local_file_path_blocks_windows_credentials(self, tmp_path: pathlib.Path) -> None:
        """Test that Windows credentials are blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        cred_path = pathlib.Path('C:\\Users\\user\\AppData\\Local\\Microsoft\\Credentials\\secret')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, cred_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_var_log(self, tmp_path: pathlib.Path) -> None:
        """Test that /var/log is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        log_path = pathlib.Path('/var/log/auth.log')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, log_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_blocks_mysql_data(self, tmp_path: pathlib.Path) -> None:
        """Test that MySQL data directory is blocked."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        mysql_path = pathlib.Path('/var/lib/mysql/users.MYD')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, mysql_path, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_case_insensitive(self, tmp_path: pathlib.Path) -> None:
        """Test that sensitive path checking is case-insensitive."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        # Test uppercase variations
        passwd_upper = pathlib.Path('/ETC/PASSWD')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, passwd_upper, allow_outside_workspace=True)

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-specific sensitive paths')
    def test_validate_local_file_path_checks_original_and_resolved(self, tmp_path: pathlib.Path) -> None:
        """Test that both original and resolved paths are checked for sensitive patterns."""
        workspace = tmp_path / 'workspace'
        workspace.mkdir(parents=True)

        # Create a path that might resolve differently
        # The validator checks both the original string and resolved path
        sensitive_path = pathlib.Path('/home/user/.ssh/authorized_keys')

        with pytest.raises(TrestleError, match='Attempt to access potentially sensitive system file'):
            PathSecurityValidator.validate_local_file_path(workspace, sensitive_path, allow_outside_workspace=True)


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


def test_https_fetcher_blocks_ssrf_aws_metadata(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher blocks AWS metadata endpoint."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    with pytest.raises(TrestleError, match='cloud metadata endpoints'):
        HTTPSFetcher(tmp_path, 'https://169.254.169.254/latest/meta-data/')


def test_https_fetcher_blocks_ssrf_gcp_metadata(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher blocks GCP metadata endpoint."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    with pytest.raises(TrestleError, match='cloud metadata endpoints'):
        HTTPSFetcher(tmp_path, 'https://metadata.google.internal/computeMetadata/v1/')


def test_https_fetcher_blocks_ssrf_localhost(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher always blocks localhost (loopback)."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    # Loopback is always blocked regardless of TRESTLE_BLOCK_PRIVATE_IPS
    with pytest.raises(TrestleError, match='127.0.0.0/8'):
        HTTPSFetcher(tmp_path, 'https://127.0.0.1:8080/')


def test_https_fetcher_blocks_ssrf_ipv6_loopback(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher always blocks IPv6 loopback."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    # IPv6 loopback is always blocked regardless of TRESTLE_BLOCK_PRIVATE_IPS
    with pytest.raises(TrestleError, match='::1/128'):
        HTTPSFetcher(tmp_path, 'https://[::1]:8080/')


def test_https_fetcher_blocks_link_local_169_254(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher always blocks link-local 169.254.x.x addresses."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    # Link-local is always blocked (includes metadata endpoints)
    with pytest.raises(TrestleError, match='169.254.0.0/16'):
        HTTPSFetcher(tmp_path, 'https://169.254.1.1/some/path')


def test_https_fetcher_allows_private_network_10_by_default(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher allows 10.x.x.x private network IPs by default."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    # RFC 1918 ranges are allowed by default to support private GitLab/internal OSCAL repos
    # This should not raise an error (though it will fail to connect in tests)
    try:
        fetcher = HTTPSFetcher(tmp_path, 'https://10.0.0.1:8500/v1/agent/self')
        # If we get here, the security validation passed (connection will fail but that's expected)
        assert fetcher is not None
    except TrestleError as e:
        # Should not be a security error about private IPs
        assert '10.0.0.0/8' not in str(e) or 'TRESTLE_BLOCK_PRIVATE_IPS' in str(e)


def test_https_fetcher_blocks_private_network_10_when_configured(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Test that HTTPSFetcher blocks 10.x.x.x when TRESTLE_BLOCK_PRIVATE_IPS is set."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    monkeypatch.setenv('TRESTLE_BLOCK_PRIVATE_IPS', 'true')
    with pytest.raises(TrestleError, match='10.0.0.0/8'):
        HTTPSFetcher(tmp_path, 'https://10.0.0.1:8500/v1/agent/self')


def test_https_fetcher_allows_private_network_192_by_default(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher allows 192.168.x.x private network IPs by default."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    try:
        fetcher = HTTPSFetcher(tmp_path, 'https://192.168.1.1/admin')
        assert fetcher is not None
    except TrestleError as e:
        assert '192.168.0.0/16' not in str(e) or 'TRESTLE_BLOCK_PRIVATE_IPS' in str(e)


def test_https_fetcher_blocks_private_network_192_when_configured(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Test that HTTPSFetcher blocks 192.168.x.x when TRESTLE_BLOCK_PRIVATE_IPS is set."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    monkeypatch.setenv('TRESTLE_BLOCK_PRIVATE_IPS', 'true')
    with pytest.raises(TrestleError, match='192.168.0.0/16'):
        HTTPSFetcher(tmp_path, 'https://192.168.1.1/admin')


def test_https_fetcher_allows_private_network_172_by_default(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher allows 172.16-31.x.x private network IPs by default."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    try:
        fetcher = HTTPSFetcher(tmp_path, 'https://172.16.0.1/admin')
        assert fetcher is not None
    except TrestleError as e:
        assert '172.16.0.0/12' not in str(e) or 'TRESTLE_BLOCK_PRIVATE_IPS' in str(e)


def test_https_fetcher_blocks_private_network_172_when_configured(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Test that HTTPSFetcher blocks 172.16-31.x.x when TRESTLE_BLOCK_PRIVATE_IPS is set."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    monkeypatch.setenv('TRESTLE_BLOCK_PRIVATE_IPS', 'true')
    with pytest.raises(TrestleError, match='172.16.0.0/12'):
        HTTPSFetcher(tmp_path, 'https://172.16.0.1/admin')


def test_sftp_fetcher_blocks_ssrf_aws_metadata(tmp_path: pathlib.Path) -> None:
    """Test that SFTPFetcher blocks AWS metadata endpoint."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    with pytest.raises(TrestleError, match='cloud metadata endpoints'):
        SFTPFetcher(tmp_path, 'sftp://169.254.169.254/latest/meta-data/')


def test_sftp_fetcher_blocks_ssrf_localhost(tmp_path: pathlib.Path) -> None:
    """Test that SFTPFetcher always blocks localhost (loopback)."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    # Loopback is always blocked regardless of TRESTLE_BLOCK_PRIVATE_IPS
    with pytest.raises(TrestleError, match='127.0.0.0/8'):
        SFTPFetcher(tmp_path, 'sftp://127.0.0.1:22/data/file.json')


def test_sftp_fetcher_blocks_link_local_169_254(tmp_path: pathlib.Path) -> None:
    """Test that SFTPFetcher always blocks link-local 169.254.x.x addresses."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    # Link-local is always blocked (includes metadata endpoints)
    with pytest.raises(TrestleError, match='169.254.0.0/16'):
        SFTPFetcher(tmp_path, 'sftp://169.254.1.1:22/some/path')


def test_https_fetcher_blocks_invalid_scheme_http(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher blocks HTTP scheme (only HTTPS allowed)."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    with pytest.raises(TrestleError, match='Only HTTPS or SFTP schemes are allowed for remote URLs'):
        HTTPSFetcher(tmp_path, 'http://example.com/data.json')


def test_https_fetcher_blocks_invalid_scheme_ftp(tmp_path: pathlib.Path) -> None:
    """Test that HTTPSFetcher blocks FTP scheme."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    with pytest.raises(TrestleError, match='Only HTTPS or SFTP schemes are allowed for remote URLs'):
        HTTPSFetcher(tmp_path, 'ftp://example.com/data.json')


def test_sftp_fetcher_blocks_invalid_scheme_http(tmp_path: pathlib.Path) -> None:
    """Test that SFTPFetcher blocks HTTP scheme (only SFTP allowed)."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    with pytest.raises(TrestleError, match='Only HTTPS or SFTP schemes are allowed for remote URLs'):
        SFTPFetcher(tmp_path, 'http://example.com/data.json')


def test_url_validator_blocks_invalid_scheme(tmp_path: pathlib.Path) -> None:
    """Test that URLSecurityValidator blocks invalid schemes."""
    from trestle.core.remote.security import URLSecurityValidator

    validator = URLSecurityValidator()

    with pytest.raises(TrestleError, match='Only HTTPS or SFTP schemes are allowed for remote URLs'):
        validator.validate_url('http://example.com/data.json')

    with pytest.raises(TrestleError, match='Only HTTPS or SFTP schemes are allowed for remote URLs'):
        validator.validate_url('ftp://example.com/data.json')

    with pytest.raises(TrestleError, match='Only HTTPS or SFTP schemes are allowed for remote URLs'):
        validator.validate_url('gopher://example.com/data')


def test_url_validator_handles_dns_resolution_failure(tmp_path: pathlib.Path, monkeypatch) -> None:
    """Test that URLSecurityValidator handles DNS resolution failures gracefully."""
    from trestle.core.remote.security import URLSecurityValidator

    # Mock socket.getaddrinfo to return empty list (no IPs resolved)
    def mock_getaddrinfo(hostname, port):
        return []  # Empty list - no IPs resolved

    monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

    validator = URLSecurityValidator()
    with pytest.raises(TrestleError, match='No IP addresses resolved for hostname'):
        validator.validate_url('https://nonexistent.example.com/data.json')


def test_url_validator_with_allowed_domains() -> None:
    """Test URL validation with domain allowlist."""
    # Test with allowed domain - should pass
    validator = URLSecurityValidator(allowed_domains={'example.com', 'test.com'})
    # This will fail DNS resolution but that's OK - we're testing the domain check happens first
    try:
        validator.validate_url('https://example.com/path')
    except TrestleError as e:
        # Should fail on DNS resolution, not domain check
        assert 'not in the allowed domains list' not in str(e)

    # Test with disallowed domain - should fail on domain check
    validator = URLSecurityValidator(allowed_domains={'example.com'})
    with pytest.raises(TrestleError, match='not in the allowed domains list'):
        validator.validate_url('https://other.com/path')


def test_url_validator_invalid_ip_address(monkeypatch) -> None:
    """Test handling of invalid IP address from getaddrinfo."""

    def mock_getaddrinfo(hostname, port):
        # Return a malformed IP that will trigger ValueError in ipaddress.ip_address()
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('not-an-ip', 0))]

    monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

    validator = URLSecurityValidator()
    with pytest.raises(TrestleError, match='Invalid IP address'):
        validator.validate_url('https://example.com/path')


class TestSSRFBypassVulnerabilities:
    """Test fixes for SSRF bypass vulnerabilities (GHSA-h47f-gmjp-m7rr)."""

    def test_blocks_ipv4_mapped_ipv6_cloud_metadata(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that IPv4-mapped IPv6 cloud metadata addresses are blocked."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS resolution to return IPv4-mapped IPv6 address
        def mock_getaddrinfo(hostname, port):
            # Return ::ffff:169.254.169.254 (IPv4-mapped IPv6 for AWS metadata)
            return [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::ffff:169.254.169.254', 443, 0, 0))]

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block IPv4-mapped IPv6 cloud metadata address
        # The metadata endpoint check catches it first with "cloud metadata endpoints" message
        with pytest.raises(TrestleError, match='cloud metadata endpoints'):
            HTTPSFetcher(tmp_path, 'https://[::ffff:169.254.169.254]/latest/meta-data/')

    def test_blocks_ipv4_mapped_ipv6_loopback(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that IPv4-mapped IPv6 loopback addresses are blocked."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS resolution to return IPv4-mapped IPv6 loopback
        def mock_getaddrinfo(hostname, port):
            # Return ::ffff:127.0.0.1 (IPv4-mapped IPv6 for loopback)
            return [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::ffff:127.0.0.1', 443, 0, 0))]

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block IPv4-mapped IPv6 loopback
        with pytest.raises(TrestleError, match='127.0.0.0/8'):
            HTTPSFetcher(tmp_path, 'https://[::ffff:127.0.0.1]/admin')

    def test_blocks_ipv4_mapped_ipv6_rfc1918(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that IPv4-mapped IPv6 RFC 1918 addresses are blocked when configured."""
        test_utils.ensure_trestle_config_dir(tmp_path)
        monkeypatch.setenv('TRESTLE_BLOCK_PRIVATE_IPS', 'true')

        # Mock DNS resolution to return IPv4-mapped IPv6 private address
        def mock_getaddrinfo(hostname, port):
            # Return ::ffff:10.0.0.1 (IPv4-mapped IPv6 for RFC 1918)
            return [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::ffff:10.0.0.1', 443, 0, 0))]

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block IPv4-mapped IPv6 private address when TRESTLE_BLOCK_PRIVATE_IPS is set
        with pytest.raises(TrestleError, match='10.0.0.0/8'):
            HTTPSFetcher(tmp_path, 'https://[::ffff:10.0.0.1]/admin')

    def test_blocks_zero_address_ipv4(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that 0.0.0.0 is blocked (reaches localhost on Linux)."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS resolution to return 0.0.0.0
        def mock_getaddrinfo(hostname, port):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('0.0.0.0', 443))]  # noqa: S104

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block 0.0.0.0
        with pytest.raises(TrestleError, match='0.0.0.0/8'):
            HTTPSFetcher(tmp_path, 'https://0.0.0.0/admin')

    def test_blocks_zero_address_ipv6(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that :: (IPv6 unspecified) is blocked."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS resolution to return ::
        def mock_getaddrinfo(hostname, port):
            return [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::', 443, 0, 0))]

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block ::
        with pytest.raises(TrestleError, match='::/128'):
            HTTPSFetcher(tmp_path, 'https://[::]/admin')

    def test_metadata_endpoint_canonicalization(self) -> None:
        """Test that metadata endpoint check canonicalizes IPv4-mapped IPv6 addresses."""
        from trestle.core.remote.security import URLSecurityValidator

        validator = URLSecurityValidator()

        # Test that bracketed IPv4-mapped IPv6 literal is canonicalized and blocked
        with pytest.raises(TrestleError, match='cloud metadata endpoints'):
            # This should be canonicalized to 169.254.169.254 and blocked
            validator._check_metadata_endpoints('::ffff:169.254.169.254')

    def test_canonicalize_ip_method(self) -> None:
        """Test the _canonicalize_ip method directly."""
        import ipaddress
        from trestle.core.remote.security import URLSecurityValidator

        validator = URLSecurityValidator()

        # Test IPv4-mapped IPv6 canonicalization
        ipv6_mapped = ipaddress.ip_address('::ffff:169.254.169.254')
        canonical = validator._canonicalize_ip(ipv6_mapped)
        assert isinstance(canonical, ipaddress.IPv4Address)
        assert str(canonical) == '169.254.169.254'

        # Test regular IPv6 is unchanged
        ipv6_regular = ipaddress.ip_address('2001:db8::1')
        canonical = validator._canonicalize_ip(ipv6_regular)
        assert isinstance(canonical, ipaddress.IPv6Address)
        assert str(canonical) == '2001:db8::1'

        # Test IPv4 is unchanged
        ipv4 = ipaddress.ip_address('192.0.2.1')
        canonical = validator._canonicalize_ip(ipv4)
        assert isinstance(canonical, ipaddress.IPv4Address)
        assert str(canonical) == '192.0.2.1'

    def test_version_check_prevents_type_error(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that version checking prevents TypeError when comparing IPv4 and IPv6."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS to return both IPv4 and IPv6 addresses
        def mock_getaddrinfo(hostname, port):
            return [
                (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443)),
                (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 443, 0, 0)),
            ]

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block both without TypeError
        with pytest.raises(TrestleError, match='127.0.0.0/8|::1/128'):
            HTTPSFetcher(tmp_path, 'https://localhost/admin')

    def test_sftp_blocks_ipv4_mapped_ipv6_cloud_metadata(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that SFTPFetcher also blocks IPv4-mapped IPv6 cloud metadata."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS resolution to return IPv4-mapped IPv6 address
        def mock_getaddrinfo(hostname, port):
            return [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::ffff:169.254.169.254', 22, 0, 0))]

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block IPv4-mapped IPv6 cloud metadata address
        # The metadata endpoint check catches it first with "cloud metadata endpoints" message
        with pytest.raises(TrestleError, match='cloud metadata endpoints'):
            SFTPFetcher(tmp_path, 'sftp://[::ffff:169.254.169.254]/data')

    def test_sftp_blocks_zero_address(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test that SFTPFetcher blocks 0.0.0.0."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS resolution to return 0.0.0.0
        def mock_getaddrinfo(hostname, port):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('0.0.0.0', 22))]  # noqa: S104

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block 0.0.0.0
        with pytest.raises(TrestleError, match='0.0.0.0/8'):
            SFTPFetcher(tmp_path, 'sftp://0.0.0.0/data')

    def test_multiple_ipv4_mapped_addresses(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        """Test handling of multiple IPv4-mapped IPv6 addresses in DNS response."""
        test_utils.ensure_trestle_config_dir(tmp_path)

        # Mock DNS to return multiple IPv4-mapped IPv6 addresses
        def mock_getaddrinfo(hostname, port):
            return [
                (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::ffff:169.254.169.254', 443, 0, 0)),
                (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::ffff:127.0.0.1', 443, 0, 0)),
            ]

        monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

        # Should block on first blocked address
        with pytest.raises(TrestleError, match='169.254.0.0/16|127.0.0.0/8'):
            HTTPSFetcher(tmp_path, 'https://evil.example.com/data')


# Made with Bob
