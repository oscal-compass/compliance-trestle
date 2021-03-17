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
"""
Trestle cache operations library.

Allows for using uris to reference external directories and then expand.
"""

import getpass
import logging
import os
import pathlib
import re
import shutil
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Dict, Type
from urllib import parse

import paramiko

from trestle.core import const
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.utils import fs

logger = logging.getLogger(__name__)


class FetcherBase(ABC):
    """FetcherBase - base class for fetching remote oscal objects."""

    def __init__(self, trestle_root: pathlib.Path, uri: str, refresh: bool = False, cache_only: bool = False) -> None:
        """Intialize fetcher base.

        Args:
            trestle_root: Path of the Trestle project path, i.e., within which .trestle is to be found.
            uri: Reference to the source object to cache.
            refresh: Whether or not the cache should be refreshed.
            cache_only: Whether or not the operation should only target the cache copy
        """
        logger.debug('Initializing FetcherBase')
        self._inst_cache_path: pathlib.Path
        self._uri = uri
        self._refresh = refresh
        self._cache_only = cache_only
        self._trestle_cache_path: pathlib.Path = trestle_root / const.TRESTLE_CONFIG_DIR / 'cache'
        # ensure trestle cache directory exists.
        self._trestle_cache_path.mkdir(exist_ok=True)

    @abstractmethod
    def _sync_cache(self) -> None:
        """Fetch a object from a remote source.

        This contains the underlying logic to update the cache.
        """
        pass

    def _update_cache(self) -> None:
        """Update the cache by fetching the target remote object, if _cache_only is false.

        Actual update logic is implemented in sync_cache.
        """
        # First discover whether...
        if self._cache_only:
            # Don't update if cache only...
            return
        if not self.in_cache() or self._refresh:
            try:
                self._sync_cache()
            except Exception as e:
                logger.error(f'Unable to update cache for {self._uri}')
                logger.debug(e)
                raise TrestleError(f'Cache update failure for {self._uri}') from e

    def get_raw(self) -> Dict[str, Any]:
        """Retrieve the raw dictionary representing the underlying object."""
        try:
            self._update_cache()
        except TrestleError as e:
            logger.error(f'Cannot get_raw due to failed _update_cache for {self._uri}')
            logger.debug(e)
            raise TrestleError(f'Cache get failure for {self._uri}') from e
        # Return results in the cache, whether yaml or json, or whatever is supported by fs.load_file().
        try:
            return fs.load_file(self._inst_cache_path)
        except Exception as e:
            logger.error(f'Cannot fs.load_file {self._inst_cache_path}')
            logger.debug(e)
            raise TrestleError(f'Cache get failure for {self._uri}') from e

    def get_oscal(self, model_type: Type[OscalBaseModel]) -> OscalBaseModel:
        """Retrieve the cached file as a particular OSCAL model.

        Argument:
        ---------
        model_type: Type[OscalBaseModel]
            Identifies what OSCAL model to cast the retrieved object as.
        """
        cache_file = self._inst_cache_path
        if cache_file.exists():
            try:
                return model_type.oscal_read(cache_file)
            except Exception as e:
                logger.error(f'get_oscal failed, JSON error loading cache file for {self._uri} as {model_type}')
                logger.debug(e)
                raise TrestleError(f'get_oscal failure for {self._uri}') from e
        else:
            logger.error(f'get_oscal error, no cached file for {self._uri}')
            raise TrestleError(f'get_oscal failure for {self._uri}')

    def in_cache(self) -> bool:
        """Return whether object is contained within the cache or not."""
        return self._inst_cache_path.exists()


class LocalFetcher(FetcherBase):
    """Fetcher for local content."""

    def __init__(self, trestle_root: pathlib.Path, uri: str, refresh: bool = False, cache_only: bool = False) -> None:
        """Initialize local fetcher. Update the expected cache path as per caching specs.

        Args:
            trestle_root: Path of the Trestle project path, i.e., within which .trestle is to be found.
            uri: Reference to the file in the local filesystem to cache, which must be outside trestle_root.
            refresh: Whether or not the cache should be refreshed
            cache_only: Whether or not the operation should only target the cache copy
        """
        super().__init__(trestle_root, uri, refresh, cache_only)
        # Normalize uri to a root file.
        if 'file:///' == uri[0:8]:
            uri = uri[7:]

        # TODO (#365): Update this to allow for relative paths. Maybe.
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
        self._inst_cache_path = localhost_cached_dir / pathlib.Path(pathlib.Path(self._uri).name)

    def _sync_cache(self) -> None:
        """Copy the local resource into the cache."""
        # Do not allow remote fetch from a trestle project:
        if fs.get_trestle_project_root(self._abs_path) is not None:
            logger.error(f'Attempt to cache from location within a trestle project: {self._uri}')
            raise TrestleError(
                'Cache request for invalid input URI:'
                f'Attempt to cache from location within a trestle project {self._uri}'
            )
        shutil.copy(self._abs_path, self._inst_cache_path)


class SFTPFetcher(FetcherBase):
    """Fetcher for SFTP content."""

    def __init__(self, trestle_root: pathlib.Path, uri: str, refresh: bool = False, cache_only: bool = False) -> None:
        """Initialize SFTP fetcher. Update the expected cache path as per caching specs.

        Args:
            trestle_root: Path of the Trestle project path, i.e., within which .trestle is to be found.
            uri: Reference to the remote file to cache that can be fetched using the sftp:// scheme.
            refresh: Whether or not the cache should be refreshed
            cache_only: Whether or not the operation should only target the cache copy
        """
        super().__init__(trestle_root, uri, refresh, cache_only)
        # Is this a valid uri, however? Username and password are optional, of course.
        u = parse.urlparse(self._uri)
        if not u.hostname:
            logger.error(f'Malformed URI, cannot parse hostname in URL {self._uri}')
            raise TrestleError(f'Cache request for invalid input URI: missing hostname {self._uri}')
        if not u.path:
            logger.error(f'Malformed URI, cannot parse path in URL {self._uri}')
            raise TrestleError(f'Cache request for invalid input URI: missing file path {self._uri}')

        sftp_cached_dir = self._trestle_cache_path / u.hostname
        # Skip any number of back- or forward slashes preceding the url path (u.path)
        path_parent = pathlib.Path(u.path[re.search('[^/\\\\]', u.path).span()[0]:]).parent
        sftp_cached_dir = sftp_cached_dir / path_parent
        sftp_cached_dir.mkdir(parents=True, exist_ok=True)
        self._inst_cache_path = sftp_cached_dir / pathlib.Path(pathlib.Path(u.path).name)

    def _sync_cache(self) -> None:
        """Fetch remote object and update the cache if appropriate and possible to do so.

        Authentication relies on the user's private key being either active via ssh-agent or
        supplied via environment variable SSH_KEY. In the latter case, it must not require a passphrase prompt.
        """
        u = parse.urlparse(self._uri)
        client = paramiko.SSHClient()
        # Must pick up host keys from the default known_hosts on this environment:
        try:
            client.load_system_host_keys()
        except Exception as e:
            logger.error('Error loading system host keys.')
            logger.debug(e)
            raise TrestleError(f'Cache update failure for {self._uri}')
        # Use the supplied private key file if given, or look for keys in default path.
        if 'SSH_KEY' in os.environ:
            pkey = paramiko.RSAKey.from_private_key(StringIO(os.environ['SSH_KEY']))
            look_for_keys = False
        else:
            pkey = None
            look_for_keys = True

        username = getpass.getuser() if not u.username else u.username
        try:
            client.connect(
                u.hostname,
                username=username,
                password=u.password,
                pkey=pkey,
                look_for_keys=look_for_keys,
                port=22 if not u.port else u.port,
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

        localpath = self._inst_cache_path
        try:
            sftp_client.get(remotepath=u.path[1:], localpath=(localpath.__str__()))
        except Exception as e:
            logger.error(f'Error getting remote resource {self._uri} into cache {localpath}')
            logger.debug(e)
            raise TrestleError(f'Cache update failure for {self._uri}')


# For passing variables:
# Do https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad#gistcomment-2747872
# or https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad#gistcomment-2752081
# or https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad#gistcomment-2865053
class FetcherFactory(object):
    """Factory method for creating a fetcher."""

    def __init__(self) -> None:
        """Initialize fetcher factory."""
        pass

    @classmethod
    def get_fetcher(
        cls, trestle_root: pathlib.Path, uri: str, refresh: bool = False, cache_only: bool = False
    ) -> FetcherBase:
        """Return an instantiated fetcher object based on the uri.

        Args:
            trestle_root: Path of the Trestle project path, i.e., within which .trestle is to be found.
        uri: Reference to the remote object to cache.
        refresh: Whether or not the cache should be refreshed
        cache_only: Whether or not the operation should only target the cache copy
        """
        # Basic correctness test
        if len(uri) <= 9 or ('/' not in uri and re.match('[A-Za-z]:\\\\', uri) is None):
            raise TrestleError(f'Unable to fetch uri as it appears to be invalid {uri}')

        if uri[0] == '/' or 'file:///' == uri[0:8]:
            # Note assumption here is that relative paths are not yet supported
            # so these are not allowed for just yet: uri[0:3] == '../' or uri[0:2] == './'
            return LocalFetcher(trestle_root, uri, refresh, cache_only)
        elif 'sftp://' == uri[0:7]:
            return SFTPFetcher(trestle_root, uri, refresh, cache_only)
        elif re.match('[A-Za-z]:\\\\', uri) is not None:
            return LocalFetcher(trestle_root, uri, refresh, cache_only)
        else:
            raise TrestleError(f'Unable to fetch uri: {uri} as the uri did not match a suppported format.')
