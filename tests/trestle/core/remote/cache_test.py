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

import pathlib
import random
import string

from trestle.core import generators
from trestle.core.remote import cache
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
    if 'C:\\' == tmp_trestle_dir.__str__()[0:3]:
        catalog_file = f'{tmp_trestle_dir.dirname}\{rand_str}.json'
    else:
        catalog_file = f'{tmp_trestle_dir.dirname}/{rand_str}.json'
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), catalog_file, False, False)
    fetcher._refresh = True
    fetcher._update_cache()
    assert fetcher._inst_cache_path.exists()


def test_fetcher_factory(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that the fetcher factory correctly resolves functionality."""
    local_uri_1 = 'file:///home/user/oscal_file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_1, False, False)
    assert type(fetcher) == cache.LocalFetcher

    local_uri_2 = '/home/user/oscal_file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_2, False, False)
    assert type(fetcher) == cache.LocalFetcher

    local_uri_3 = '../../file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), local_uri_3, False, False)
    assert type(fetcher) == cache.LocalFetcher

    sftp_uri = 'sftp://user@hostname:/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), sftp_uri, False, False)
    assert type(fetcher) == cache.SFTPFetcher

    sftp_uri_2 = 'sftp://user@hostname:2000/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), sftp_uri_2, False, False)
    assert type(fetcher) == cache.SFTPFetcher

    https_uri = 'https://host.com/path/to/json.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), https_uri, False, False)
    assert type(fetcher) == cache.HTTPSFetcher

    https_basic_auth = 'https://user:pass@host.com/path/to/json.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), https_basic_auth, False, False)
    assert type(fetcher) == cache.HTTPSFetcher

    github_url_1 = 'https://github.com/some/url.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), github_url_1, False, False)
    assert type(fetcher) == cache.GithubFetcher

    github_url_2 = 'https://user:auth@github.com/some/url.json'
    fetcher = cache.FetcherFactory.get_fetcher(pathlib.Path(tmp_trestle_dir), github_url_2, False, False)
    assert type(fetcher) == cache.GithubFetcher
