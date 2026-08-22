# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Testing for cache functionality."""

import datetime
import getpass
import pathlib
import random
import secrets
import string
import time
from types import SimpleNamespace
from typing import Dict, List, Tuple
from urllib import parse

from _pytest.monkeypatch import MonkeyPatch

from paramiko import SSHClient

import pytest

import trestle.common.const as const
import trestle.common.err as err
from trestle.common import file_utils
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core import generators
from trestle.core.remote import cache
from trestle.oscal.catalog import Catalog


class _HTTPSResponse:
    """Minimal streaming response used by HTTPS fetcher tests."""

    def __init__(self, status_code: int, chunks: List[bytes], headers: Dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self._chunks = chunks
        self.headers = headers or {}
        self.text = b''.join(chunks).decode(const.FILE_ENCODING)
        self.closed = False

    def iter_content(self, chunk_size: int) -> List[bytes]:
        assert chunk_size == 64 * 1024
        return self._chunks

    def close(self) -> None:
        self.closed = True


def as_file_uri(path: str) -> str:
    """Convert sample non-existent path to file:/// and add drive letter if windows."""
    # Correct usage would start with / and leaving off should cause errors with cache
    if file_utils.is_windows():
        drive = pathlib.Path.cwd().resolve().drive
        return f'file:///{drive}{path}'
    bare_path = path.lstrip('/')
    return f'file:///{bare_path}'


def get_catalog_fetcher(
    tmp_trestle_dir: pathlib.Path, in_trestle: bool = False, relative: bool = False
) -> Tuple[cache.FetcherFactory, Catalog, dict]:
    """Instantiate a catalog and fetcher."""
    rand_str = ''.join(secrets.choice(string.ascii_letters) for x in range(16))
    cat_name = f'{rand_str}.json'
    dest_dir = tmp_trestle_dir / 'catalogs' if in_trestle else tmp_trestle_dir.parent
    catalog_file = dest_dir / cat_name
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(catalog_file)
    if relative:
        catalog_str = f'./catalogs/{cat_name}' if in_trestle else f'../{cat_name}'
    else:
        catalog_str = str(catalog_file)
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, catalog_str)
    return fetcher, catalog_data


def test_time_since_modification_uses_utc(monkeypatch: MonkeyPatch) -> None:
    """Test cache age calculation uses UTC-aware datetimes."""

    class _StatResult:
        st_mtime = 1234.5

    class _FakePath:
        def stat(self) -> _StatResult:
            return _StatResult()

    expected_last_mod = datetime.datetime(2026, 3, 15, 11, 0, 0, tzinfo=datetime.UTC)
    expected_now = datetime.datetime(2026, 3, 15, 12, 30, 0, tzinfo=datetime.UTC)

    class _FakeDateTime:
        @classmethod
        def fromtimestamp(cls, ts: float, tz: datetime.tzinfo | None = None) -> datetime.datetime:
            assert ts == _StatResult.st_mtime
            assert tz == datetime.UTC
            return expected_last_mod

        @classmethod
        def now(cls, tz: datetime.tzinfo | None = None) -> datetime.datetime:
            assert tz == datetime.UTC
            return expected_now

    monkeypatch.setattr(cache.datetime, 'datetime', _FakeDateTime)
    assert cache.FetcherBase._time_since_modification(_FakePath()) == datetime.timedelta(hours=1, minutes=30)


def test_fetcher_oscal(tmp_trestle_dir: pathlib.Path) -> None:
    """Test whether fetcher can get an object from the cache as an oscal model."""
    fetcher, catalog_data = get_catalog_fetcher(tmp_trestle_dir)
    fetcher._update_cache()
    assert fetcher.get_cached_path().is_file()
    fetched_data = fetcher.get_oscal_with_model_type(Catalog)
    assert ModelUtils.models_are_equivalent(fetched_data, catalog_data)
    fetched_data, _ = fetcher.get_oscal()
    assert ModelUtils.models_are_equivalent(fetched_data, catalog_data)


def test_fetcher_cached_path_requires_file(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """The public cache path accessor should reject a missing cached object."""
    fetcher, _ = get_catalog_fetcher(tmp_trestle_dir)
    monkeypatch.setattr(fetcher, '_update_cache', lambda force_update=False: False)
    fetcher._cached_object_path = tmp_trestle_dir / 'missing.json'

    with pytest.raises(TrestleError, match='cached object is not a file'):
        fetcher.get_cached_path()


def test_fetcher_oscal_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test failed read from cache."""
    logged_error = 'oscal_fail'

    def oscal_read_mock(*args, **kwargs):
        raise err.TrestleError(logged_error)

    fetcher, _ = get_catalog_fetcher(tmp_trestle_dir)
    # mock bad read of oscal model
    monkeypatch.setattr(Catalog, 'oscal_read', oscal_read_mock)
    with pytest.raises(err.TrestleError, match='get_oscal failure'):
        fetcher.get_oscal_with_model_type(Catalog)


def test_fetcher_get_raw_fails_single_read_attempt(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Ensure get_raw does not attempt duplicate reads when file loading fails."""
    fetcher, _ = get_catalog_fetcher(tmp_trestle_dir)
    call_count = 0

    def load_file_mock(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise RuntimeError('simulated load failure')

    monkeypatch.setattr(file_utils, 'load_file', load_file_mock)

    with pytest.raises(err.TrestleError, match='Cache get failure'):
        fetcher.get_raw()

    assert call_count == 1


def test_local_fetcher_relative(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the local fetcher for an object with an aboslute path."""
    fetcher, catalog_data = get_catalog_fetcher(tmp_trestle_dir, False, True)
    fetched_data, _ = fetcher.get_oscal()
    assert ModelUtils.models_are_equivalent(fetched_data, catalog_data)


def test_https_fetcher_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the HTTPS fetcher failing."""
    monkeypatch.setenv('myusername', 'user123')
    monkeypatch.setenv('mypassword', 'somep4ss')
    # This syntactically valid uri points to localhost which is now blocked for security
    # The security validator should reject this before any connection attempt
    uri = 'https://{{myusername}}:{{mypassword}}@127.0.0.1/path/to/file.json'
    with pytest.raises(TrestleError, match='127.0.0.0/8'):
        cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)


def test_https_fetcher(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the HTTPS fetcher update, including failures."""
    # This valid uri should work:
    uri = (
        'https://raw.githubusercontent.com/oscal-compass/compliance-trestle/develop/'
        'tests/data/json/minimal_catalog.json'
    )
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    fetcher._update_cache()
    assert len(open(fetcher._cached_object_path, encoding=const.FILE_ENCODING).read()) > 0
    dummy_existing_file = fetcher._cached_object_path.__str__()
    # Now we'll get a file that does not exist:
    uri = 'https://raw.githubusercontent.com/oscal-compass/compliance-trestle/develop/tests/data/json/not_here.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    with pytest.raises(TrestleError, match='GET returned code 404'):
        fetcher._update_cache()
    # Supply CA bundle env var value pointing to no existing file:
    monkeypatch.setenv('REQUESTS_CA_BUNDLE', './no_such_bundle.crt')
    with pytest.raises(TrestleError, match='path does not exist'):
        fetcher._update_cache()
    # Supply bad CA bundle env var value pointing to a bad bundle file:
    monkeypatch.setenv('REQUESTS_CA_BUNDLE', dummy_existing_file)
    with pytest.raises(TrestleError, match='retries exceeded'):
        fetcher._update_cache()


def test_https_fetcher_rejects_redirects(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """HTTPS fetching should not follow an unvalidated redirect destination."""
    response = _HTTPSResponse(302, [])
    request_options = {}
    monkeypatch.setattr(cache.URLSecurityValidator, 'validate_url', lambda self, url: None)

    def _get(url: str, **kwargs) -> _HTTPSResponse:
        request_options.update(kwargs)
        return response

    monkeypatch.setattr(cache.requests, 'get', _get)
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, 'https://example.com/catalog.json', max_size_bytes=1024)

    with pytest.raises(TrestleError, match='GET returned code 302'):
        fetcher._update_cache()

    assert request_options['allow_redirects'] is False
    assert response.closed


@pytest.mark.parametrize('headers, chunks', [({'Content-Length': '6'}, []), ({}, [b'123', b'', b'456'])])
def test_https_fetcher_rejects_oversized_response(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch, headers: Dict[str, str], chunks: List[bytes]
) -> None:
    """HTTPS size limits should cover declared and streamed response sizes."""
    response = _HTTPSResponse(200, chunks, headers)
    monkeypatch.setattr(cache.URLSecurityValidator, 'validate_url', lambda self, url: None)
    monkeypatch.setattr(cache.requests, 'get', lambda *args, **kwargs: response)
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, 'https://example.com/catalog.json', max_size_bytes=5)

    with pytest.raises(TrestleError, match='exceeds maximum size of 5 bytes'):
        fetcher._update_cache()

    assert response.closed
    assert not fetcher._cached_object_path.exists()


def test_https_fetcher_streams_limited_response(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """A bounded HTTPS response should be atomically stored in the cache."""
    response = _HTTPSResponse(200, [b'{}'])
    monkeypatch.setattr(cache.URLSecurityValidator, 'validate_url', lambda self, url: None)
    monkeypatch.setattr(cache.requests, 'get', lambda *args, **kwargs: response)
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, 'https://example.com/catalog.json', max_size_bytes=2)

    cached_path = fetcher.get_cached_path()

    assert cached_path.read_bytes() == b'{}'
    assert response.closed


def test_https_fetcher_wraps_response_read_failure(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Unexpected HTTPS response-read failures should retain fetch context."""

    class _UnreadableResponse:
        status_code = 200

        @property
        def text(self) -> str:
            raise RuntimeError('simulated read failure')

        def close(self) -> None:
            pass

    monkeypatch.setattr(cache.URLSecurityValidator, 'validate_url', lambda self, url: None)
    monkeypatch.setattr(cache.requests, 'get', lambda *args, **kwargs: _UnreadableResponse())
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, 'https://example.com/catalog.json')

    with pytest.raises(TrestleError, match='Cache update failure reading response via HTTPS'):
        fetcher._do_fetch()


def test_fetcher_rejects_invalid_maximum_size(tmp_trestle_dir: pathlib.Path) -> None:
    """A configured fetch limit must be positive."""
    with pytest.raises(TrestleError, match='must be greater than zero'):
        cache.FetcherFactory.get_fetcher(tmp_trestle_dir, '../catalog.json', max_size_bytes=0)


@pytest.mark.parametrize('block_private_ips', [True, False])
def test_https_fetcher_private_network_override(tmp_trestle_dir: pathlib.Path, block_private_ips: bool) -> None:
    """Callers should be able to override the shared private-network policy."""
    uri = 'https://10.0.0.1/catalog.json'
    if block_private_ips:
        with pytest.raises(TrestleError, match='10.0.0.0/8'):
            cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri, block_private_ips=True)
    else:
        fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri, block_private_ips=False)
        assert not fetcher._url_validator.block_private_ips


def test_sftp_fetcher_load_system_keys_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp fetcher when SSHClient loading of system host keys fails."""

    def ssh_load_system_host_keys_mock(*args, **kwargs):
        raise OSError('stuff')

    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setattr(SSHClient, 'load_system_host_keys', ssh_load_system_host_keys_mock)
    with pytest.raises(err.TrestleError, match='Cache update failure'):
        fetcher._update_cache()


def test_sftp_fetcher_bad_ssh_key(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp fetcher when the loaded SSH_KEY env var contains a bad SSH key."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setenv('SSH_KEY', 'blah')
    with pytest.raises(err.TrestleError, match='not a valid RSA'):
        fetcher._update_cache()


def test_sftp_fetcher_open_fail(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp fetcher when failing on open_sftp."""

    def ssh_open_fail_mock(*args, **kwargs):
        raise err.TrestleError('stuff')

    def ssh_open_happy_mock(*args, **kwargs):
        return

    def ssh_connect_mock(*args, **kwargs):
        return

    monkeypatch.setattr(SSHClient, 'open_sftp', ssh_open_happy_mock)
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    with pytest.raises(err.TrestleError, match='Error getting remote'):
        fetcher._do_fetch()

    monkeypatch.setattr(SSHClient, 'open_sftp', ssh_open_fail_mock)
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    with pytest.raises(err.TrestleError, match='open sftp for'):
        fetcher._do_fetch()


@pytest.mark.parametrize('reported_size, content', [(6, b''), (3, b'123456')])
def test_sftp_fetcher_rejects_oversized_response(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch, reported_size: int, content: bytes
) -> None:
    """SFTP limits should reject an oversized stat or growing transfer."""
    monkeypatch.setattr(cache.URLSecurityValidator, 'validate_url', lambda self, url: None)
    monkeypatch.setattr(SSHClient, 'load_system_host_keys', lambda self: None)
    monkeypatch.setattr(SSHClient, 'connect', lambda self, *args, **kwargs: None)

    class _SFTPClient:
        def stat(self, remotepath: str) -> SimpleNamespace:
            return SimpleNamespace(st_size=reported_size)

        def get(self, remotepath: str, localpath: str, callback=None) -> None:
            pathlib.Path(localpath).write_bytes(content)
            if callback:
                callback(len(content), len(content))

    monkeypatch.setattr(SSHClient, 'open_sftp', lambda self: _SFTPClient())
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, 'sftp://example.com/catalog.json', max_size_bytes=5)

    with pytest.raises(TrestleError, match='exceeds maximum size of 5 bytes'):
        fetcher._update_cache()

    assert not fetcher._cached_object_path.exists()


def test_sftp_fetcher_stores_limited_response(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """A bounded SFTP response should be atomically stored in the cache."""
    monkeypatch.setattr(cache.URLSecurityValidator, 'validate_url', lambda self, url: None)
    monkeypatch.setattr(SSHClient, 'load_system_host_keys', lambda self: None)
    monkeypatch.setattr(SSHClient, 'connect', lambda self, *args, **kwargs: None)

    class _SFTPClient:
        def stat(self, remotepath: str) -> SimpleNamespace:
            return SimpleNamespace(st_size=2)

        def get(self, remotepath: str, localpath: str, callback=None) -> None:
            pathlib.Path(localpath).write_bytes(b'{}')
            if callback:
                callback(2, 2)

    monkeypatch.setattr(SSHClient, 'open_sftp', lambda self: _SFTPClient())
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, 'sftp://example.com/catalog.json', max_size_bytes=2)

    assert fetcher.get_cached_path().read_bytes() == b'{}'


def test_sftp_fetcher_connect_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test sftp during SSHClient connect failure."""

    def ssh_connect_mock(*args, **kwargs):
        raise err.TrestleError('stuff')

    def ssh_urlparse_mock(*args, **kwargs):
        raise err.TrestleError('stuff')

    # Password given:
    uri = 'sftp://username:password@some.host/path/to/file.json'
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    with pytest.raises(err.TrestleError, match='connect via SSH'):
        fetcher._update_cache()
    # Password not given (assumes attempt to use ssh-agent):
    uri = 'sftp://username@some.host/path/to/file.json'
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    with pytest.raises(err.TrestleError, match='connect via SSH'):
        fetcher._update_cache()
    # malformed uri - security validator now catches urlparse errors first
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    monkeypatch.setattr(parse, 'urlparse', ssh_urlparse_mock)
    with pytest.raises(err.TrestleError, match='Invalid URL format'):
        _ = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)


def test_sftp_fetcher_getuser_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp call to getpass.getuser."""

    def getuser_mock(*args, **kwargs):
        return

    uri = 'sftp://some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    # Force call to paramiko.SSHClient.load_host_keys
    monkeypatch.setenv('SSH_KEY', 'some_key_file')
    monkeypatch.setattr(getpass, 'getuser', getuser_mock)
    with pytest.raises(err.TrestleError, match='not a valid RSA'):
        fetcher._update_cache()
        getuser_mock.assert_called_once()


@pytest.mark.parametrize(
    'uri', ['sftp://blah.com', 'sftp:///path/to/file.json', 'sftp://user:pass@hostname.com\\path\\to\\file.json']
)
def test_sftp_fetcher_bad_uri(uri: str, tmp_trestle_dir: pathlib.Path) -> None:
    """Test get_fetcher handling of bad SFTP URI."""
    with pytest.raises(TrestleError):
        cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)


@pytest.mark.parametrize(
    'uri',
    [
        '',
        'sftp://',
        '..',
        '.json',
        'a.ym',
        'ftp://some.host/this.file',
        'https://{{9invalid}}:@github.com/oscal-compass/test/file',
        'https://{{invalid var}}:@github.com/oscal-compass/test/file',
        'https://{{invalid-var}}:@github.com/oscal-compass/test/file',
        'https://{{_}}:@github.com/oscal-compass/test/file',
        'https://{{myusername}}:@github.com/oscal-compass/test/file',
        'https://{{myusername}}:passwordstring@github.com/oscal-compass/test/file',
        'https://{{myusername_not_defined}}:passwordstring@github.com/oscal-compass/test/file',
        'https://{{myusername}}:{{password_var_not_defined}}@github.com/oscal-compass/test/file',
        'https://{{myusername}}:{{0invalid}}@github.com/oscal-compass/test/file',
        'https://{{myusername}}:{{invalid var}}@github.com/oscal-compass/test/file',
        'https://{{myusername}}:{{invalid-var}}@github.com/oscal-compass/test/file',
        'https://{{myusername}}:{{_}}@github.com/oscal-compass/test/file',
        'https://usernamestring:{{mypassword}}@github.com/oscal-compass/test/file',
        'https://:{{mypassword}}@github.com/oscal-compass/test/file',
    ],
)
def test_fetcher_bad_uri(tmp_trestle_dir: pathlib.Path, uri: str, monkeypatch: MonkeyPatch) -> None:
    """Test fetcher factory with bad URI."""
    if 'https' in uri:
        monkeypatch.setenv('myusername', 'user123')
        monkeypatch.setenv('mypassword', 'somep4ss')
    with pytest.raises(TrestleError):
        cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)


def test_fetcher_factory(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test that the fetcher factory correctly resolves functionality."""
    # basic absolute and relative file paths
    for uri in [
        as_file_uri('/home/user/oscal_file.json'),
        as_file_uri('user/oscal_file.json'),
        as_file_uri('../user/oscal_file.json'),
    ]:
        fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
        assert isinstance(fetcher, cache.LocalFetcher)

    # paths with drive letter
    for uri in ['C:\\Users\\user\\this.json', 'C:/Users/user/this.json', 'C:file.json']:
        if file_utils.is_windows():
            fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
            assert isinstance(fetcher, cache.LocalFetcher)
        else:
            with pytest.raises(TrestleError):
                cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)

    https_uri = 'https://{{myusername}}:{{mypassword}}@this.com/this.json'
    monkeypatch.setenv('myusername', 'user123')
    monkeypatch.setenv('mypassword', 'somep4ss')
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, https_uri)
    assert isinstance(fetcher, cache.HTTPSFetcher)

    # Mock DNS resolution for SFTP tests to avoid "Unable to resolve hostname" errors
    import socket

    def mock_getaddrinfo(host, port, *args, **kwargs):
        # Return a fake IP address for any hostname
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.1', 22))]

    monkeypatch.setattr(socket, 'getaddrinfo', mock_getaddrinfo)

    sftp_uri = 'sftp://user@hostname:/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, sftp_uri)
    assert isinstance(fetcher, cache.SFTPFetcher)

    sftp_uri = 'sftp://user@hostname:2000/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, sftp_uri)
    assert isinstance(fetcher, cache.SFTPFetcher)


def test_fetcher_expiration(tmp_trestle_dir: pathlib.Path) -> None:
    """Test fetcher expiration behavior."""
    uri = (
        'https://raw.githubusercontent.com/oscal-compass/compliance-trestle/develop/'
        'tests/data/json/minimal_catalog.json'
    )
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    # specify quick timeout of 5s
    fetcher._expiration_seconds = 5

    # should fetch because doesn't have it yet
    assert fetcher._update_cache()
    assert fetcher._cached_object_path.exists()

    # should not fetch since it is too soon
    assert not fetcher._update_cache()

    # wait a bit
    time.sleep(6)

    # should fetch now
    assert fetcher._update_cache()

    # should also fetch if we force it
    assert fetcher._update_cache(True)


@pytest.mark.parametrize('uri', ['C:mydir/myfile.json', 'C://mydir/myfile.json'])
def test_fetcher_failures_windows(uri: str, tmp_trestle_dir: pathlib.Path) -> None:
    """Test failures specific to Windows."""
    if file_utils.is_windows():
        fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
        with pytest.raises(TrestleError, match='No such file'):
            _ = fetcher.get_oscal()


def test_fetcher_failure_windows_wrong_drive(tmp_trestle_dir: pathlib.Path) -> None:
    """Test failures specific to Windows."""
    if file_utils.is_windows():
        rand_str = ''.join(secrets.choice(string.ascii_letters) for x in range(16))
        catalog_file = tmp_trestle_dir.parent / f'{rand_str}.json'
        catalog_data = generators.generate_sample_model(Catalog)
        catalog_data.oscal_write(catalog_file)

        drive_letter = catalog_file.drive
        path_str = str(catalog_file)[2:]
        bad_drive = 'X:' if drive_letter not in ['X', 'x'] else 'Y:'
        bad_uri = bad_drive + path_str
        fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, bad_uri)
        with pytest.raises(TrestleError, match='No such file'):
            _ = fetcher.get_oscal()
