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

from trestle.core.remote import cache


def test_fetcher_base():
    """Test whether fetcher can get an object from the cache."""
    pass


def test_github_fetcher():
    """Test the github fetcher."""
    pass


def test_fetcher_factory():
    """Test that the fetcher factory correctly resolves functionality."""
    local_uri_1 = 'file:///home/user/oscal_file.json'
    fetcher = cache.FetcherFactory.get_fetcher(local_uri_1, False, False)
    assert type(fetcher) == cache.LocalFetcher

    local_uri_2 = '/home/user/oscal_file.json'
    fetcher = cache.FetcherFactory.get_fetcher(local_uri_2, False, False)
    assert type(fetcher) == cache.LocalFetcher

    local_uri_3 = '../../file.json'
    fetcher = cache.FetcherFactory.get_fetcher(local_uri_3, False, False)
    assert type(fetcher) == cache.LocalFetcher

    sftp_uri = 'sftp://user@hostname:/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(sftp_uri, False, False)
    assert type(fetcher) == cache.LocalFetcher

    sftp_uri_2 = 'sftp://user@hostname:2000/path/to/file.json'
    fetcher = cache.FetcherFactory.get_fetcher(sftp_uri_2, False, False)
    assert type(fetcher) == cache.SFTPFetcher

    https_uri = 'https://host.com/path/to/json.json'
    fetcher = cache.FetcherFactory.get_fetcher(https_uri, False, False)
    assert type(fetcher) == cache.HTTPSFetcher

    https_basic_auth = 'https://user:pass@host.com/path/to/json.json'
    fetcher = cache.FetcherFactory.get_fetcher(https_basic_auth, False, False)
    assert type(fetcher) == cache.HTTPSFetcher

    github_url_1 = 'https://github.com/some/url.json'
    fetcher = cache.FetcherFactory.get_fetcher(github_url_1, False, False)
    assert type(fetcher) == cache.GithubFetcher

    github_url_2 = 'https://user:auth@github.com/some/url.json'
    fetcher = cache.FetcherFactory.get_fetcher(github_url_2, False, False)
    assert type(fetcher) == cache.GithubFetcher
