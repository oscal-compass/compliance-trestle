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

import getpass
import pathlib
import platform
import random
import string
import time
from typing import Tuple

from _pytest.monkeypatch import MonkeyPatch

from paramiko import SFTPClient
from paramiko import SSHClient

import pytest

from tests.test_utils import models_are_equivalent

import trestle.core.const as const
import trestle.core.err as err
from trestle.core import generators
from trestle.core.err import TrestleError
from trestle.core.remote import cache
from trestle.oscal.catalog import Catalog


def as_file_uri(path: str) -> str:
    """Convert sample non-existent path to file:/// and add drive letter if windows."""
    # Correct usage would start with / and leaving off should cause errors with cache
    if platform.system() == const.WINDOWS_PLATFORM_STR:
        drive = pathlib.Path.cwd().resolve().drive
        return f'file:///{drive}{path}'
    bare_path = path.lstrip('/')
    return f'file:///{bare_path}'


def get_catalog_fetcher(tmp_trestle_dir: pathlib.Path,
                        in_trestle: bool = False,
                        relative: bool = False) -> Tuple[cache.FetcherFactory, Catalog, dict]:
    """Instantiate a catalog and fetcher."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
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


def test_fetcher_oscal(tmp_trestle_dir: pathlib.Path) -> None:
    """Test whether fetcher can get an object from the cache as an oscal model."""
    fetcher, catalog_data = get_catalog_fetcher(tmp_trestle_dir)
    fetcher._update_cache()
    fetched_data = fetcher.get_oscal_with_model_type(Catalog)
    assert models_are_equivalent(fetched_data, catalog_data)
    fetched_data, _ = fetcher.get_oscal()
    assert models_are_equivalent(fetched_data, catalog_data)


def test_fetcher_oscal_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test failed read from cache."""
    logged_error = 'oscal_fail'

    def oscal_read_mock(*args, **kwargs):
        raise err.TrestleError(logged_error)

    fetcher, _ = get_catalog_fetcher(tmp_trestle_dir)
    # mock bad read of oscal model
    monkeypatch.setattr(Catalog, 'oscal_read', oscal_read_mock)
    with pytest.raises(err.TrestleError):
        fetcher.get_oscal_with_model_type(Catalog)


def test_github_fetcher():
    """Test the github fetcher."""
    pass


def test_local_fetcher_relative(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the local fetcher for an object with an aboslute path."""
    fetcher, catalog_data = get_catalog_fetcher(tmp_trestle_dir, False, True)
    fetched_data, _ = fetcher.get_oscal()
    assert models_are_equivalent(fetched_data, catalog_data)


def test_https_fetcher_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the HTTPS fetcher failing."""
    monkeypatch.setenv('myusername', 'user123')
    monkeypatch.setenv('mypassword', 'somep4ss')
    # This syntactically valid uri points to nothing and should ConnectTimeout.
    uri = 'https://{{myusername}}:{{mypassword}}@127.0.0.1/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    with pytest.raises(TrestleError):
        fetcher._update_cache()


def test_https_fetcher(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the HTTPS fetcher update, including failures."""
    # This valid uri should work:
    uri = 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/json/minimal_catalog.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    fetcher._update_cache()
    assert len(open(fetcher._cached_object_path, encoding=const.FILE_ENCODING).read()) > 0
    dummy_existing_file = fetcher._cached_object_path.__str__()
    # Now we'll get a file that does not exist:
    uri = 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/json/not_here.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    with pytest.raises(TrestleError):
        fetcher._update_cache()
    # Supply CA bundle env var value pointing to no existing file:
    monkeypatch.setenv('REQUESTS_CA_BUNDLE', './no_such_bundle.crt')
    with pytest.raises(TrestleError):
        fetcher._update_cache()
    # Supply bad CA bundle env var value pointing to a bad bundle file:
    monkeypatch.setenv('REQUESTS_CA_BUNDLE', dummy_existing_file)
    with pytest.raises(TrestleError):
        fetcher._update_cache()


def test_sftp_fetcher(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp fetcher."""

    def ssh_load_host_keys_mock():
        return

    def ssh_connect_mock():
        return

    def open_sftp_mock():
        return

    def sftp_get_mock():
        return

    uri = 'sftp://some.host//path/to/test.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setattr(SSHClient, 'load_system_host_keys', ssh_load_host_keys_mock)
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    monkeypatch.setattr(SSHClient, 'open_sftp', open_sftp_mock)
    monkeypatch.setattr(SFTPClient, 'get', sftp_get_mock)
    try:
        fetcher._update_cache()
    except Exception:
        AssertionError()


def test_sftp_fetcher_load_system_keys_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp fetcher when SSHClient loading of system host keys fails."""

    def ssh_load_system_host_keys_mock():
        raise OSError('stuff')

    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setattr(SSHClient, 'load_system_host_keys', ssh_load_system_host_keys_mock)
    with pytest.raises(err.TrestleError):
        fetcher._update_cache()


def test_sftp_fetcher_bad_ssh_key(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp fetcher when the loaded SSH_KEY env var contains a bad SSH key."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setenv('SSH_KEY', 'blah')
    with pytest.raises(err.TrestleError):
        fetcher._update_cache()


def test_sftp_fetcher_connect_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test sftp during SSHClient connect failure."""

    def ssh_connect_mock():
        err.TrestleError('stuff')

    # Password given:
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    with pytest.raises(err.TrestleError):
        fetcher._update_cache()
    # Password not given (assumes attempt to use ssh-agent):
    uri = 'sftp://username@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    with pytest.raises(err.TrestleError):
        fetcher._update_cache()


def test_sftp_fetcher_open_sftp_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the exception response during open_sftp failure."""

    def ssh_load_host_keys_mock():
        return

    def ssh_connect_mock():
        return

    def open_sftp_mock():
        raise err.TrestleError('stuff')

    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    monkeypatch.setenv('SSH_KEY', 'some_key_file')
    monkeypatch.setattr(SSHClient, 'load_host_keys', ssh_load_host_keys_mock)
    monkeypatch.setattr(SSHClient, 'connect', ssh_connect_mock)
    monkeypatch.setattr(SSHClient, 'open_sftp', open_sftp_mock)
    with pytest.raises(err.TrestleError):
        fetcher._update_cache()
        ssh_load_host_keys_mock.assert_called_once()
        ssh_connect_mock.assert_called_once()
        open_sftp_mock.assert_called_once()


def test_sftp_fetcher_getuser_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp call to getpass.getuser."""

    def getuser_mock(*args, **kwargs):
        return

    uri = 'sftp://some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    # Force call to paramiko.SSHClient.load_host_keys
    monkeypatch.setenv('SSH_KEY', 'some_key_file')
    monkeypatch.setattr(getpass, 'getuser', getuser_mock)
    with pytest.raises(err.TrestleError):
        fetcher._update_cache()
        getuser_mock.assert_called_once()


def test_sftp_fetcher_get_fails(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test the sftp fetcher SFTPClient.get() failing."""

    def load_host_keys_mock():
        return

    def connect_mock():
        return

    def get_mock():
        raise err.TrestleError('get fails')

    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
    # Force call to paramiko.SSHClient.load_host_keys
    monkeypatch.setenv('SSH_KEY', 'some_key_file')
    monkeypatch.setattr(SSHClient, 'load_host_keys', load_host_keys_mock)
    monkeypatch.setattr(SSHClient, 'connect', connect_mock)
    monkeypatch.setattr(SFTPClient, 'get', get_mock)
    with pytest.raises(TrestleError):
        fetcher._update_cache()
        load_host_keys_mock.assert_called_once()
        connect_mock.assert_called_once()
        get_mock.assert_called_once()


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
        'https://{{9invalid}}:@github.com/IBM/test/file',
        'https://{{invalid var}}:@github.com/IBM/test/file',
        'https://{{invalid-var}}:@github.com/IBM/test/file',
        'https://{{_}}:@github.com/IBM/test/file',
        'https://{{myusername}}:@github.com/IBM/test/file',
        'https://{{myusername}}:passwordstring@github.com/IBM/test/file',
        'https://{{myusername_not_defined}}:passwordstring@github.com/IBM/test/file',
        'https://{{myusername}}:{{password_var_not_defined}}@github.com/IBM/test/file',
        'https://{{myusername}}:{{0invalid}}@github.com/IBM/test/file',
        'https://{{myusername}}:{{invalid var}}@github.com/IBM/test/file',
        'https://{{myusername}}:{{invalid-var}}@github.com/IBM/test/file',
        'https://{{myusername}}:{{_}}@github.com/IBM/test/file',
        'https://usernamestring:{{mypassword}}@github.com/IBM/test/file',
        'https://:{{mypassword}}@github.com/IBM/test/file'
    ]
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
    for uri in [as_file_uri('/home/user/oscal_file.json'),
                as_file_uri('user/oscal_file.json'),
                as_file_uri('../user/oscal_file.json')]:
        fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
        assert type(fetcher) == cache.LocalFetcher

    # paths with drive letter
    for uri in ['C:\\Users\\user\\this.json', 'C:/Users/user/this.json', 'C:file.json']:
        if platform.system() == const.WINDOWS_PLATFORM_STR:
            fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
            assert type(fetcher) == cache.LocalFetcher
        else:
            with pytest.raises(TrestleError):
                cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)

    https_uri = 'https://{{myusername}}:{{mypassword}}@this.com/this.json'
    monkeypatch.setenv('myusername', 'user123')
    monkeypatch.setenv('mypassword', 'somep4ss')
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, https_uri)
    assert type(fetcher) == cache.HTTPSFetcher

    sftp_uri = 'sftp://user@hostname:/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, sftp_uri)
    assert type(fetcher) == cache.SFTPFetcher

    sftp_uri = 'sftp://user@hostname:2000/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, sftp_uri)
    assert type(fetcher) == cache.SFTPFetcher


def test_fetcher_expiration(tmp_trestle_dir: pathlib.Path) -> None:
    """Test fetcher expiration behavior."""
    uri = 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/json/minimal_catalog.json'
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
    if platform.system() == const.WINDOWS_PLATFORM_STR:
        fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, uri)
        with pytest.raises(TrestleError):
            _ = fetcher.get_oscal()


def test_fetcher_failure_windows_wrong_drive(tmp_trestle_dir: pathlib.Path) -> None:
    """Test failures specific to Windows."""
    if platform.system() == const.WINDOWS_PLATFORM_STR:
        rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
        catalog_file = tmp_trestle_dir.parent / f'{rand_str}.json'
        catalog_data = generators.generate_sample_model(Catalog)
        catalog_data.oscal_write(catalog_file)

        drive_letter = catalog_file.drive
        path_str = str(catalog_file)[2:]
        bad_drive = 'X:' if drive_letter not in ['X', 'x'] else 'Y:'
        bad_uri = bad_drive + path_str
        fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, bad_uri)
        with pytest.raises(TrestleError):
            _ = fetcher.get_oscal()
