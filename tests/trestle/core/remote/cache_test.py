# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Testing for cache functionality."""

import pathlib
import platform
import random
import string
import time
from unittest.mock import patch

import pytest

from tests.test_utils import models_are_equivalent

import trestle.core.const as const
import trestle.core.err as err
from trestle.core import generators
from trestle.core.err import TrestleError
from trestle.core.remote import cache
from trestle.oscal.catalog import Catalog
from trestle.utils import fs


def as_file_uri(path: str) -> str:
    """Convert sample non-existent path to file:/// and add drive letter if windows."""
    # Correct usage would start with / and leaving off should cause errors with cache
    if platform.system() == const.WINDOWS_PLATFORM_STR:
        drive = pathlib.Path.cwd().resolve().drive
        return f'file:///{drive}{path}'
    return f'file://{path}'


def test_fetcher_oscal(tmp_trestle_dir):
    """Test whether fetcher can get an object from the cache as an oscal model."""
    # Fetch from local content, expecting it to be cached and then fetched as an oscal model.
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = pathlib.Path(tmp_trestle_dir.parent / f'{rand_str}.json').__str__()
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), catalog_file)
    # Create/update the cache copy
    fetcher._update_cache()
    fetched_data = fetcher.get_oscal(Catalog)
    assert models_are_equivalent(fetched_data, catalog_data)


def test_fetcher_oscal_fails(tmp_trestle_dir):
    """Test whether fetcher can get an object from the cache as an oscal model."""
    # Fetch from local content, expecting it to be cached and then fetched as an oscal model.
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = pathlib.Path(tmp_trestle_dir.parent / f'{rand_str}.json').__str__()
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), catalog_file)
    # mock bad read of oscal model
    with patch('trestle.oscal.catalog.Catalog.oscal_read') as oscal_read_mock:
        oscal_read_mock.side_effect = err.TrestleError
        with pytest.raises(err.TrestleError):
            fetcher.get_oscal(Catalog)
        oscal_read_mock.assert_called_once()


def test_fetcher_base(tmp_trestle_dir):
    """Test whether fetcher can get an object from the cache."""
    # Fetch from local content, expecting it to be cached and then fetched.
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = pathlib.Path(tmp_trestle_dir.parent / f'{rand_str}.json').__str__()
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    saved_data = fs.load_file(pathlib.Path(catalog_file))
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), catalog_file)
    # Create/update the cache copy
    fetched_data = fetcher.get_raw()
    assert fetched_data == saved_data


def test_github_fetcher():
    """Test the github fetcher."""
    pass


def test_local_fetcher_get_fails(tmp_trestle_dir):
    """Test the local fetcher get failure."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_dir = tmp_trestle_dir / f'catalogs/{rand_str}'
    catalog_dir.mkdir(parents=True, exist_ok=True)
    catalog_file = catalog_dir / 'catalog.json'
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(catalog_file)
    with pytest.raises(err.TrestleError):
        cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), str(catalog_file))


def test_local_fetcher_absolute(tmp_trestle_dir):
    """Test the local fetcher for an object with a non-relative path, i.e., an aboslute path."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = pathlib.Path(tmp_trestle_dir.parent / f'{rand_str}.json').__str__()
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), catalog_file)
    fetcher._update_cache()
    assert fetcher._cached_object_path.exists()


def test_https_fetcher_fails(tmp_trestle_dir, monkeypatch):
    """Test the HTTPS fetcher failing."""
    monkeypatch.setenv('myusername', 'user123')
    monkeypatch.setenv('mypassword', 'somep4ss')
    # This syntactically valid uri points to nothing and should ConnectTimeout.
    uri = 'https://{{myusername}}:{{mypassword}}@127.0.0.1/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    with pytest.raises(TrestleError):
        fetcher._update_cache()


def test_https_fetcher(tmp_trestle_dir, monkeypatch):
    """Test the HTTPS fetcher update, including failures."""
    # This valid uri should work:
    uri = 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/json/minimal_catalog.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    fetcher._update_cache()
    assert len(open(fetcher._cached_object_path, encoding=const.FILE_ENCODING).read()) > 0
    dummy_existing_file = fetcher._cached_object_path.__str__()
    # Now we'll get a file that does not exist:
    uri = 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/json/not_here.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
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


def test_sftp_fetcher(tmp_trestle_dir):
    """Test the sftp fetcher."""
    uri = 'sftp://some.host//path/to/test.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    with patch('paramiko.SSHClient.load_system_host_keys') as ssh_load_keys_mock:
        with patch('paramiko.SSHClient.connect') as ssh_connect_mock:
            with patch('paramiko.SSHClient.open_sftp') as sftp_open_mock:
                with patch('paramiko.SFTPClient.get'):
                    try:
                        fetcher._update_cache()
                    except Exception:
                        AssertionError()
                    ssh_load_keys_mock.assert_called_once()
                    ssh_connect_mock.assert_called_once()
                    sftp_open_mock.assert_called_once()


# test to do cache_only removed since no longer used


def test_sftp_fetcher_load_system_keys_fails(tmp_trestle_dir):
    """Test the sftp fetcher when SSHClient loading of system host keys fails."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    with patch('paramiko.SSHClient.load_system_host_keys') as ssh_load_system_host_keys_mock:
        ssh_load_system_host_keys_mock.side_effect = OSError('stuff')
        with pytest.raises(err.TrestleError):
            fetcher._update_cache()


def test_sftp_fetcher_bad_ssh_key(tmp_trestle_dir, monkeypatch):
    """Test the sftp fetcher when the loaded SSH_KEY env var contains a bad SSH key."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    monkeypatch.setenv('SSH_KEY', 'blah')
    with pytest.raises(err.TrestleError):
        fetcher._update_cache()


def test_sftp_fetcher_connect_fails(tmp_trestle_dir):
    """Test sftp during SSHClient connect failure."""
    # Password given:
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    with patch('paramiko.SSHClient.connect') as ssh_connect_mock:
        ssh_connect_mock.side_effect = err.TrestleError('stuff')
        with pytest.raises(err.TrestleError):
            fetcher._update_cache()
    # Password not given (assumes attempt to use ssh-agent):
    uri = 'sftp://username@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    with patch('paramiko.SSHClient.connect') as ssh_connect_mock:
        ssh_connect_mock.side_effect = err.TrestleError('stuff')
        with pytest.raises(err.TrestleError):
            fetcher._update_cache()


def test_sftp_fetcher_open_sftp_fails(tmp_trestle_dir, monkeypatch):
    """Test the exception response during open_sftp failure."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    monkeypatch.setenv('SSH_KEY', 'some_key_file')
    with patch('paramiko.SSHClient.load_host_keys') as load_host_keys_mock:
        with patch('paramiko.SSHClient.connect') as connect_mock:
            with patch('paramiko.SSHClient.open_sftp') as open_sftp_mock:
                open_sftp_mock.side_effect = err.TrestleError('stuff')
                with pytest.raises(err.TrestleError):
                    fetcher._update_cache()
                    load_host_keys_mock.assert_called_once()
                    connect_mock.assert_called_once()
                    open_sftp_mock.assert_called_once()


def test_sftp_fetcher_getuser_fails(tmp_trestle_dir, monkeypatch):
    """Test the sftp call to getpass.getuser."""
    uri = 'sftp://some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    # Force call to paramiko.SSHClient.load_host_keys
    monkeypatch.setenv('SSH_KEY', 'some_key_file')
    with patch('getpass.getuser') as getuser_mock:
        with pytest.raises(err.TrestleError):
            fetcher._update_cache()
            getuser_mock.assert_called_once()


def test_sftp_fetcher_get_fails(tmp_trestle_dir, monkeypatch):
    """Test the sftp fetcher SFTPClient.get() failing."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
    # Force call to paramiko.SSHClient.load_host_keys
    monkeypatch.setenv('SSH_KEY', 'some_key_file')
    with patch('paramiko.SSHClient.load_host_keys') as load_host_keys_mock:
        with patch('paramiko.SSHClient.connect') as connect_mock:
            with patch('paramiko.SFTPClient.get') as get_mock:
                get_mock.side_effect = err.TrestleError('get fails')
                with pytest.raises(TrestleError):
                    fetcher._update_cache()
                    load_host_keys_mock.assert_called_once()
                    connect_mock.assert_called_once()
                    get_mock.assert_called_once()


@pytest.mark.parametrize(
    'uri', ['sftp://blah.com', 'sftp:///path/to/file.json', 'sftp://user:pass@hostname.com\\path\\to\\file.json']
)
def test_sftp_fetcher_bad_uri(uri, tmp_trestle_dir):
    """Test get_fetcher handling of bad SFTP URI."""
    with pytest.raises(TrestleError):
        cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)


def test_fetcher_bad_uri(tmp_trestle_dir: pathlib.Path, monkeypatch):
    """Test fetcher factory with bad URI."""
    monkeypatch.setenv('myusername', 'user123')
    monkeypatch.setenv('mypassword', 'somep4ss')
    for uri in ['',
                'sftp://',
                '..',
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
                'https://:{{mypassword}}@github.com/IBM/test/file']:
        with pytest.raises(TrestleError):
            cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)


def test_fetcher_factory(tmp_trestle_dir: pathlib.Path, monkeypatch) -> None:
    """Test that the fetcher factory correctly resolves functionality."""
    local_uri_1 = as_file_uri('/home/user/oscal_file.json')
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_1)
    assert type(fetcher) == cache.LocalFetcher

    local_uri_2 = as_file_uri('/home/user/oscal_file.json')
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_2)
    assert type(fetcher) == cache.LocalFetcher

    # Relative paths are not yet supported, e.g., local_uri_3 = '../../file.json', but should come soon.

    local_uri_4 = 'C:\\Users\\user\\this.file'
    local_uri_5 = 'C:/Users/user/this.file'
    if platform.system() == const.WINDOWS_PLATFORM_STR:
        fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_4)
        assert type(fetcher) == cache.LocalFetcher
        fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_5)
        assert type(fetcher) == cache.LocalFetcher
    else:
        with pytest.raises(TrestleError):
            cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_4)
        with pytest.raises(TrestleError):
            cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_5)

    https_uri = 'https://{{myusername}}:{{mypassword}}@this.com/this.file'
    monkeypatch.setenv('myusername', 'user123')
    monkeypatch.setenv('mypassword', 'somep4ss')
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), https_uri)
    assert type(fetcher) == cache.HTTPSFetcher

    sftp_uri = 'sftp://user@hostname:/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), sftp_uri)
    assert type(fetcher) == cache.SFTPFetcher

    sftp_uri_2 = 'sftp://user@hostname:2000/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), sftp_uri_2)
    assert type(fetcher) == cache.SFTPFetcher


def test_fetcher_expiration(tmp_trestle_dir: pathlib.Path):
    """Test fetcher expiration behavior."""
    uri = 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/json/minimal_catalog.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)
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
def test_fetcher_failures_windows(uri, tmp_trestle_dir: pathlib.Path) -> None:
    """Test failures specific to Windows."""
    if platform.system == const.WINDOWS_PLATFORM_STR:
        with pytest.raises(TrestleError):
            cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri)


def test_fetcher_failure_windows_wrong_drive(tmp_trestle_dir: pathlib.Path) -> None:
    """Test failures specific to Windows."""
    if platform.system == const.WINDOWS_PLATFORM_STR:
        rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
        catalog_file = pathlib.Path(tmp_trestle_dir.parent / f'{rand_str}.json').__str__()
        catalog_data = generators.generate_sample_model(Catalog)
        catalog_data.oscal_write(pathlib.Path(catalog_file))

        drive_letter, path_str = fs.strip_drive_letter(catalog_file)
        bad_drive = 'X:' if drive_letter not in ['X', 'x'] else 'Y:'
        bad_uri = bad_drive + path_str
        with pytest.raises(TrestleError):
            cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), bad_uri)
