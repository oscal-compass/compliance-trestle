# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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

import os
import pathlib
import random
import string
from unittest import mock
from unittest.mock import patch

import pytest

import trestle.core.err as err
from trestle.core import generators
from trestle.core.err import TrestleError
from trestle.core.remote import cache
from trestle.core.settings import Settings
from trestle.oscal.catalog import Catalog


def test_fetcher_base():
    """Test whether fetcher can get an object from the cache."""
    pass


def test_github_fetcher():
    """Test the github fetcher."""
    pass


def test_local_fetcher(tmp_trestle_dir):
    """Test the local fetcher."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = pathlib.Path(tmp_trestle_dir / f'{rand_str}.json').__str__()
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), catalog_file, False, False)
    fetcher._refresh = True
    fetcher._update_cache()
    assert fetcher._inst_cache_path.exists()


def test_sftp_fetcher(tmp_trestle_dir):
    """Test the sftp fetcher."""
    uri = 'sftp://some.host//path/to/test.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)
    fetcher._refresh = True
    fetcher._cache_only = False
    with patch('paramiko.SSHClient.load_system_host_keys') as ssh_load_keys_mock:
        ssh_load_keys_mock.return_value = None
        with patch('paramiko.SSHClient.connect') as ssh_connect_mock:
            ssh_connect_mock.return_value = None
            with patch('paramiko.SSHClient.open_sftp') as sftp_open_mock:
                sftp_open_mock.return_value = None
                with patch('paramiko.sftp_client.SFTPClient.get') as sftp_get_mock:
                    sftp_get_mock.return_value = None
                    try:
                        fetcher._update_cache()
                    except Exception:
                        AssertionError()
                    else:
                        assert True


def test_sftp_fetcher_cache_only(tmp_trestle_dir):
    """Test sftp fetcher should not update, cache only."""
    uri = 'sftp://some.host//path/to/test.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)
    fetcher._refresh = True
    fetcher._cache_only = True
    try:
        fetcher._update_cache()
    except Exception:
        AssertionError()
    else:
        assert True


def test_sftp_fetcher_load_system_keys_fails(tmp_trestle_dir):
    """Test the sftp fetcher, SSHClient load system host keys should fail."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)
    fetcher._refresh = True
    fetcher._cache_only = False
    with patch('paramiko.SSHClient.load_system_host_keys') as ssh_load_system_host_keys_mock:
        ssh_load_system_host_keys_mock.side_effect = OSError('stuff')
        with pytest.raises(err.TrestleError):
            fetcher._update_cache()


@mock.patch.dict(os.environ, {'SSH_KEY': '/tmp/no_ssh_key_here'})
def test_sftp_fetcher_load_keys_fails(tmp_trestle_dir):
    """Test the sftp fetcher, SSHClient load host keys specified in env var should fail."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)
    fetcher._refresh = True
    fetcher._cache_only = False
    with patch('paramiko.SSHClient.load_host_keys') as ssh_load_host_keys_mock:
        ssh_load_host_keys_mock.side_effect = OSError('stuff')
        with pytest.raises(err.TrestleError):
            fetcher._update_cache()


def test_sftp_fetcher_connect_fails(tmp_trestle_dir):
    """Test the sftp fetcher, SSHClient connect should fail."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)
    fetcher._refresh = True
    fetcher._cache_only = False
    with patch('paramiko.SSHClient.connect') as ssh_connect_mock:
        ssh_connect_mock.side_effect = err.TrestleError('stuff')
        try:
            fetcher._update_cache()
        except Exception:
            assert True
        else:
            AssertionError


def test_sftp_fetcher_open_sftp_fails(tmp_trestle_dir):
    """Test the local fetcher."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)
    fetcher._refresh = True
    fetcher._cache_only = False
    with patch('paramiko.SSHClient.open_sftp') as sftp_open_mock:
        sftp_open_mock.side_effect = err.TrestleError('stuff')
        try:
            fetcher._update_cache()
        except Exception:
            assert True
        else:
            AssertionError


def test_sftp_fetcher_get_fails(tmp_trestle_dir):
    """Test the local fetcher."""
    uri = 'sftp://username:password@some.host/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)
    fetcher._refresh = True
    fetcher._cache_only = False
    with patch('paramiko.sftp_client.SFTPClient.get') as sftp_get_mock:
        sftp_get_mock.side_effect = err.TrestleError('stuff')
        try:
            fetcher._update_cache()
        except Exception:
            assert True
        else:
            AssertionError


def test_fetcher_bad_uri(tmp_trestle_dir):
    """Test fetcher factory with bad URI."""
    for uri in ['',
                'https://',
                'https:///blah.com',
                'sftp://',
                '..',
                'sftp://blah.com',
                'sftp:///path/to/file.json',
                'sftp://user:pass@hostname.com\\path\\to\\file.json',
                'sftp://:pass@hostname.com/path/to/file.json']:
        with pytest.raises(TrestleError):
            cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), uri, False, False)


def test_fetcher_factory(tmp_trestle_dir: pathlib.Path) -> None:
    settings = Settings()

    """Test that the fetcher factory correctly resolves functionality."""
    local_uri_1 = 'file:///home/user/oscal_file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_1, settings, False, False)
    assert type(fetcher) == cache.LocalFetcher

    local_uri_2 = '/home/user/oscal_file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_2, settings, False, False)
    assert type(fetcher) == cache.LocalFetcher

    local_uri_3 = '../../file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_3, settings, False, False)
    assert type(fetcher) == cache.LocalFetcher

    sftp_uri = 'sftp://user@hostname:/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), sftp_uri, settings, False, False)
    assert type(fetcher) == cache.SFTPFetcher

    sftp_uri_2 = 'sftp://user@hostname:2000/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), sftp_uri_2, settings, False, False)
    assert type(fetcher) == cache.SFTPFetcher

    # https_uri = 'https://placekitten.com/200/300'
    # fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), https_uri, settings, False, False)
    # assert type(fetcher) == cache.HTTPSFetcher

    https_basic_auth = 'https://{{USERNAME}}:{{PASSWORD}}@placekitten.com/200/300'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), https_basic_auth, settings, False, False)
    assert type(fetcher) == cache.HTTPSFetcher

    # github_url_1 = 'https://github.com/DrJohnWagner/recipes/blob/master/README.md'
    # fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), github_url_1, settings, False, False)
    # assert type(fetcher) == cache.GithubFetcher
    # fetcher._sync_cache()

    # github_url_2 = 'https://github.ibm.com/aur-mma/ai-for-the-eye/blob/master/README.md'
    # fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), github_url_2, settings, False, False)
    # assert type(fetcher) == cache.GithubFetcher
    # fetcher._sync_cache()
