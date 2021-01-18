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
"""
Trestle cache operations library.

Allows for using uris to reference external directories and then expand.
"""

import getpass
import logging
import os
import paramiko
import pathlib
import re
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from urllib import parse
from trestle.core import const
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError

logger = logging.getLogger(__name__)


class FetcherBase(ABC):
    """FetcherBase - base class for fetching remote oscal objects."""

    def __init__(
        self,
        trestle_root: pathlib.Path,
        uri: str,
        refresh: bool = False,
        fail_hard: bool = True,
        cache_only: bool = False
    ) -> None:
        """Intialize fetcher base.

        Refresh: whether or not the cache should be refreshed
        """
        logger.debug('Initializing FetcherBase')
        self._inst_cache_path: pathlib.Path
        self._uri = uri
        self._refresh = refresh
        self._fail_hard = fail_hard
        self._cache_only = cache_only
        self._trestle_cache_path: pathlib.Path = trestle_root / const.TRESTLE_CONFIG_DIR / 'cache'

        # ensure trestle cache directory exists.
        self._trestle_cache_path.mkdir(exist_ok=True)

    @abstractmethod
    def _update_cache(self) -> None:
        """Fetch a object from a remote source.

        This contains the underlying logic to update the cache.
        """

    def get_raw(self) -> Dict[str, Any]:
        """Get the raw dictionary representing the underlying object."""
        self._update_cache()
        # Results are now in the cache.
        pass

    def get_oscal(self, model_type: Type[OscalBaseModel]) -> OscalBaseModel:
        """Retrieve the cached file as a particular OSCAL model."""
        pass

    def in_cache(self) -> bool:
        """Return whether object is contained within the cache or not."""
        return self._inst_cache_path.exists()


class LocalFetcher(FetcherBase):
    """Fetcher for local content."""

    def __init__(
        self,
        trestle_root: pathlib.Path,
        uri: str,
        refresh: bool = False,
        fail_hard: bool = True,
        cache_only: bool = False
    ) -> None:
        """Initialize local fetcher."""
        super().__init__(trestle_root, uri, refresh, fail_hard, cache_only)
        # Normalize uri to a root file.
        if 'file:///' == uri[0:8]:
            uri = uri[7:]
        path = pathlib.Path(uri).absolute()
        self._abs_path = path
        localhost_cached_dir = self._trestle_cache_path / 'localhost'
        localhost_cached_dir = localhost_cached_dir / '__abs__' / '__root__'
        # Use the uri's path.parent to set a cache location
        cache_location_string = path.parent.__str__()
        # Remove the drive letter for Windows/DOS paths:
        if re.match('[a-zA-Z]:', uri):
            cache_location_string = re.sub('[a-zA-Z]:', '', path.parent.__str__())
        # Locte first non-slash character as the root subdirectory to start with:
        non_slash_start = re.search('[a-z-A-Z0-9]', cache_location_string).span()[0]
        cache_location_string_relative = cache_location_string[non_slash_start:]
        localhost_cached_dir = localhost_cached_dir / pathlib.Path(cache_location_string_relative)
        localhost_cached_dir.mkdir(parents=True, exist_ok=True)
        self._inst_cache_path = localhost_cached_dir

    def _update_cache(self) -> None:
        # Step one discover whether
        if self._cache_only:
            # Don't update if cache only.
            return
        if self._inst_cache_path.exists() and self._refresh:
            try:
                shutil.copy(self._abs_path, self._inst_cache_path)
            except Exception as e:
                logger.error(f'Unable to update cache for {self._uri}')
                logger.debug(e)
                raise TrestleError(f'Cache update failure for {self._uri}')


class HTTPSFetcher(FetcherBase):
    """Fetcher for https content."""

    # Use request: https://requests.readthedocs.io/en/master/
    def __init__(
        self,
        trestle_root: pathlib.Path,
        uri: str,
        refresh: bool = False,
        fail_hard: bool = False,
        cache_only: bool = False
    ) -> None:
        """Initialize HTTPS fetcher."""
        super().__init__(trestle_root, uri, refresh, fail_hard, cache_only)

    def _update_cache(self) -> None:
        pass


class SFTPFetcher(FetcherBase):
    """Fetcher for https content."""

    # STFP method: https://stackoverflow.com/questions/7563496/open-a-remote-file-using-paramiko-in-python-slow#7563551
    # For SFTP fetch into memory.
    def __init__(
        self,
        trestle_root: pathlib.Path,
        uri: str,
        refresh: bool = False,
        fail_hard: bool = False,
        cache_only: bool = False
    ) -> None:
        """Initialize STFP fetcher."""
        super().__init__(trestle_root, uri, refresh, fail_hard, cache_only)
        # Is this a valid uri, however? Username and password are optional, of course.
        u = parse.urlparse(self._uri)
        if not u.hostname:
            logger.error(f'Malformed URI, cannot parse hostname in URL {self._uri}')
            raise TrestleError(f'Cache request for invalid input URI: missing hostname {self._uri}')
        if not u.path:
            logger.error(f'Malformed URI, cannot parse path in URL {self._uri}')
            raise TrestleError(f'Cache request for invalid input URI: missing file path {self._uri}')
        if u.password and not u.username:
            logger.error(f'Malformed URI, password found but username missing in URL {self._uri}')
            raise TrestleError(f'Cache request for invalid input URI: password found but username missing {self._uri}')

        localhost_cached_dir = self._trestle_cache_path / u.hostname
        # Skip any number of back- or forward slashes preceding the url path (u.path)
        localhost_cached_dir = localhost_cached_dir / pathlib.Path(u.path[re.search('[^/\\\\]', u.path).span()[0]:]).parent
        try:
            localhost_cached_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
                logger.error(f'Error creating cache directory {localhost_cached_dir} for {self._uri}')
                logger.debug(e)
                raise TrestleError(f'Cache update failure for {self._uri}')
        self._inst_cache_path = localhost_cached_dir

    def _update_cache(self) -> None:
        if self._cache_only:
            # Don't update if cache only.
            return

        u = parse.urlparse(self._uri)
        client = paramiko.SSHClient()

        if 'SSH_KEY' in os.environ and self._refresh:
            ssh_key_file = os.environ['SSH_KEY']
            try:
                client.load_host_keys(ssh_key_file)
            except Exception as e:
                logger.error(f'Error loading host keys from {ssh_key_file}.')
                logger.debug(e)
                raise TrestleError(f'Cache update failure for {self._uri}')

        elif self._inst_cache_path.exists() and self._refresh:
            try:
                client.load_system_host_keys()
            except Exception as e:
                logger.error(f'Error loading system host keys.')
                logger.debug(e)
                raise TrestleError(f'Cache update failure for {self._uri}')
               
        username = getpass.getuser() if not u.username else u.username
        if u.password:
            try:
                client.connect(
                    u.hostname,
                    username = username,
                    password = u.password,
                    port = 22 if not u.port else u.port,
                )
            except Exception as e:
                logger.error(f'Error connecting SSH for {username}@{u.hostname}')
                logger.debug(e)
                raise TrestleError(f'Cache update failure to connect via SSH: {username}@{u.hostname}')
        else:
            try:
                client.connect(
                    u.hostname,
                    username = username,
                    port = 22 if not u.port else u.port,
                    allow_agent = True
                )
            except Exception as e:
                logger.error(f'Error connecting SSH for {username}@{u.hostname}')
                logger.debug(e)
                raise TrestleError(f'Cache update failure to connect via SSH: {username}@{u.hostname}')

        try:
            sftp_client = client.open_sftp()
        except Exception as e:
            logger.error(f'Error opening sftp session for {username}@{u.hostname}')
            logger.debug(e)
            raise TrestleError(f'Cache update failure to open sftp for {username}@{u.hostname}')

        localpath = self._inst_cache_path / pathlib.Path(u.path).name
        try:
            sftp_client.get(remotepath=u.path[1:], localpath=(localpath.__str__()))
        except Exception as e:
            logger.error(f'Error getting remote resource {self._uri} into cache {localpath}')
            logger.debug(e)
            raise TrestleError(f'Cache update failure for {self._uri}')


class GithubFetcher(HTTPSFetcher):
    """Github fetcher which supports both github and GHE URLs."""

    def __init__(
        self,
        trestle_root: pathlib.Path,
        uri: str,
        refresh: bool = False,
        fail_hard: bool = False,
        cache_only: bool = False
    ) -> None:
        """Initialize github specific fetcher."""
        super().__init__(trestle_root, uri, refresh, fail_hard, cache_only)

    def _update_cache(self) -> None:
        pass


class FetcherFactory(object):
    """Factory method for creating a fetcher."""

    def __init__(self) -> None:
        """Initialize fetcher factory."""
        pass

    @classmethod
    def get_fetcher(
        cls,
        trestle_root: pathlib.Path,
        uri: str,
        refresh: bool = False,
        fail_hard: bool = False,
        cache_only: bool = False
    ) -> FetcherBase:
        """Return an instantiated fetcher object based on the uri."""
        # Basic correctness test
        if len(uri) <= 9 or ('/' not in uri and 'C:\\' not in uri):
            raise TrestleError(f'Unable to fetch uri as it appears to be invalid {uri}')

        if uri[0] == '/' or uri[0:3] == '../' or uri[0:2] == './' or 'file:///' == uri[0:8]:
            # Note assumption here is that relative paths are only supported within
            # trestle directories. This simplification is to ensure
            return LocalFetcher(trestle_root, uri, refresh, fail_hard, cache_only)
        elif 'sftp://' == uri[0:7]:
            return SFTPFetcher(trestle_root, uri, refresh, fail_hard, cache_only)
        elif 'https://' == uri[0:8]:
            # Check for valid URL:
            u = parse.urlparse(uri)
            if u.hostname:
                # Test for github uri assumption - must be first after basic auth (if it exists)
                cleaned = uri[8:]
                # tests for special scenarios
                if cleaned.split('@')[-1][0:7] == 'github.':
                    return GithubFetcher(trestle_root, uri, refresh, fail_hard, cache_only)
                else:
                    return HTTPSFetcher(trestle_root, uri, refresh, fail_hard, cache_only)
            else:
                logger.error(f'Malformed URI, cannot parse hostname in URL {uri}')
                raise TrestleError(f'Cache request for input URI: cannot find hostname {uri}')
        elif 'C:\\' == uri[0:3]:
            return LocalFetcher(trestle_root, uri, refresh, fail_hard, cache_only)
        else:
            raise TrestleError(f'Unable to fetch uri: {uri} as the uri did not match a suppported format.')
