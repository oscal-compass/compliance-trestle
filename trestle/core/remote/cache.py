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

Allows for using URI's to reference external directories and then expand.
"""

import datetime
import getpass
import logging
import os
import pathlib
import platform
import re
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Dict, Type
from urllib import parse

import paramiko

import requests
from requests.auth import HTTPBasicAuth

from trestle.core import const
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.utils import fs

logger = logging.getLogger(__name__)


class FetcherBase(ABC):
    """FetcherBase - base class for caching and fetching remote oscal objects."""

    def __init__(self, trestle_root: pathlib.Path, uri: str) -> None:
        """Intialize fetcher base.

        Args:
            trestle_root: Path of the Trestle project path, i.e., within which .trestle is to be found.
            uri: Reference to the source object to cache.
        """
        logger.debug('Initializing FetcherBase')
        self._cached_object_path: pathlib.Path
        self._uri = uri
        self._trestle_root = trestle_root.resolve()
        self._trestle_cache_path: pathlib.Path = self._trestle_root / const.TRESTLE_CACHE_DIR
        # ensure trestle cache directory exists.
        self._trestle_cache_path.mkdir(exist_ok=True)
        self._expiration_seconds = const.DAY_SECONDS
        self._in_trestle = False

    @staticmethod
    def _time_since_modification(file_path: pathlib.Path) -> datetime.timedelta:
        """Get time since last modification."""
        last_modification = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
        return datetime.datetime.now() - last_modification

    @abstractmethod
    def _do_fetch(self) -> None:
        """Fetch the object from a remote source."""
        pass

    def _in_cache(self) -> bool:
        """Return whether object is present in the cache or not."""
        return self._cached_object_path.exists()

    def _is_stale(self) -> bool:
        # Either cache empty or cached item is too old
        if not self._in_cache():
            return True
        return FetcherBase._time_since_modification(self._cached_object_path
                                                    ) > datetime.timedelta(seconds=self._expiration_seconds)

    def _update_cache(self, force_update: bool = False) -> bool:
        """Update the cache by fetching the target remote object, if stale or forced.

        Args:
            force_update: force the fetch regardless of staleness.

        Returns:
            True if update occurred
        """
        if self._is_stale() or force_update:
            try:
                self._do_fetch()
                return True
            except Exception as e:
                logger.error(f'Unable to update cache for {self._uri}')
                logger.debug(e)
                raise TrestleError(f'Cache update failure for {self._uri}') from e
        return False

    def get_raw(self, force_update=False) -> Dict[str, Any]:
        """Retrieve the raw dictionary representing the underlying object."""
        self._update_cache(force_update)
        # Return results in the cache, whether yaml or json, or whatever is supported by fs.load_file().
        try:
            return fs.load_file(self._cached_object_path)
        except Exception as e:
            logger.error(f'Cannot fs.load_file {self._cached_object_path}')
            logger.debug(e)
            raise TrestleError(f'Cache get failure for {self._uri}') from e

    def get_oscal(self, model_type: Type[OscalBaseModel], force_update=False) -> OscalBaseModel:
        """Retrieve the cached file as a particular OSCAL model.

        Arguments:
            model_type: Type[OscalBaseModel] Specifies the OSCAL model type of the fetched object.
        """
        self._update_cache(force_update)
        cache_file = self._cached_object_path
        if cache_file.exists():
            try:
                return model_type.oscal_read(cache_file)
            except Exception as e:
                logger.error(f'get_oscal failed, error loading cache file for {self._uri} as {model_type}')
                logger.debug(e)
                raise TrestleError(f'get_oscal failure for {self._uri}') from e
        else:
            logger.error(f'get_oscal error, no cached file for {self._uri}')
            raise TrestleError(f'get_oscal failure for {self._uri}')


class LocalFetcher(FetcherBase):
    r"""Fetcher for local content.

    Used for both file:/// and C:\\ or C:/ type paths, but the path must be absolute.
    Also used for trestle:// files present in the current trestle root.

    If file:/// is used on a Windows system, it must be followed by C:/ or other drive letter
    to be sure it is an absolute path, e.g. file:///C:/Users/Default/Documents/profile.json.
    The drive letter may be lowercase.
    LocalFetcher does not do any caching and assumes the file is quickly accessible.
    """

    def __init__(self, trestle_root: pathlib.Path, uri: str) -> None:
        """Initialize local fetcher.

        Args:
            trestle_root: trestle root path
            uri: Reference to the file in the local filesystem to cache, which must be outside trestle_root.
        """
        super().__init__(trestle_root, uri)

        # Handle as file:/// form
        if uri.startswith(const.FILE_URI):
            # strip off entire header including /
            uri = uri[len(const.FILE_URI):]

            # if it has a drive letter don't add / to front
            uri = uri if re.match(const.WINDOWS_DRIVE_LETTER_REGEX, uri) else '/' + uri
        elif uri.startswith(const.TRESTLE_HREF_HEADING):
            self._in_trestle = True
            uri = str(trestle_root / uri[len(const.TRESTLE_HREF_HEADING):])
            self._abs_path = pathlib.Path(uri).resolve()
            self._cached_object_path = self._abs_path
            return

        # now the URI should be either unix / style or windows C:/ style.  Neither can be relative

        # if it has a drive letter but no / after it, it is not absolute
        if re.match(const.WINDOWS_DRIVE_LETTER_REGEX, uri):
            if platform.system() != const.WINDOWS_PLATFORM_STR:
                raise TrestleError(f'Cannot cache Windows paths on non-Windows system. {uri}')
            if not re.match(const.WINDOWS_DRIVE_URI_REGEX, uri):
                raise TrestleError(f'Windows URI must include DriveLetter: followed by one slash: {uri}')

        # store the abs path to the file for fetching
        # if this is a windows file it will have a drive letter at start after resolve
        self._abs_path = pathlib.Path(uri).resolve()

        if fs.has_parent_path(self._abs_path, trestle_root):
            raise TrestleError(f'Cannot use cache for trestle in current project directory {self._abs_path}')

        # set the cached path to be the actual file path
        self._cached_object_path = self._abs_path

    def _is_stale(self):
        # Local file is always stale.
        return True

    def _do_fetch(self) -> None:
        """No need to fetch since using actual file path."""
        pass


class HTTPSFetcher(FetcherBase):
    """Fetcher for https content."""

    # Use request: https://requests.readthedocs.io/en/master/
    def __init__(self, trestle_root: pathlib.Path, uri: str) -> None:
        """Initialize HTTPS fetcher."""
        logger.debug('Initializing HTTPSFetcher')
        super().__init__(trestle_root, uri)
        self._username = None
        self._password = None
        u = parse.urlparse(self._uri)
        self._url = uri
        # If the either the username or password is omitted in the URI, then the other becomes ''
        # so we test for either None or ''.
        if u.username != '' and u.username is not None:
            # This also checks for invalid environment variable name (IEEE 1003.1)
            if not re.match('{{[a-zA-Z_][a-zA-Z0-9_]*}}', u.username) or u.username == '{{_}}':
                logger.error(
                    'Malformed URI, '
                    f'username must refer to an environment variable using moustache {self._uri}'
                )
                raise TrestleError(
                    'Cache request for invalid input URI: '
                    f'username must refer to an environment variable using moustache {self._uri}'
                )
            username_var = u.username[2:-2]
            if username_var not in os.environ:
                logger.error(f'Malformed URI, username not found in the environment {self._uri}')
                raise TrestleError(
                    f'Cache request for invalid input URI: username not found in the environment {self._uri}'
                )
            self._username = os.environ[username_var]
        if u.password != '' and u.password is not None:
            if not re.match('{{[a-zA-Z_][a-zA-Z0-9_]*}}', u.password) or u.password == '{{_}}':
                logger.error(
                    f'Malformed URI, password must refer to an environment variable using moustache {self._uri}'
                )
                raise TrestleError(
                    'Cache request for invalid input URI: '
                    f'password must refer to an environment variable using moustache {self._uri}'
                )
            password_var = u.password[2:-2]
            if password_var not in os.environ:
                logger.error(f'Malformed URI, password not found in the environment {self._uri}')
                raise TrestleError(
                    'Cache request for invalid input URI: '
                    f'password not found in the environment {self._uri}'
                )
            self._password = os.environ[password_var]
        if self._username and (self._password == '' or self._password is None):
            logger.error(
                'Malformed URI, username found but valid password not found '
                f'via environment variable in URI {self._uri}'
            )
            raise TrestleError(
                f'Cache request for invalid input URI: username found '
                f'but password not found via environment variable {self._uri}'
            )
        if self._password and not self._username:
            logger.error(
                f'Malformed URI, password found '
                f'but valid username environment variable missing in URI {self._uri}'
            )
            raise TrestleError(
                f'Cache request for invalid input URI: password found '
                f'but username not found via environment variable {self._uri}'
            )
        https_cached_dir = self._trestle_cache_path / u.hostname
        # Skip any number of back- or forward slashes preceding the URI path (u.path)
        path_parent = pathlib.Path(u.path[re.search('[^/\\\\]', u.path).span()[0]:]).parent
        https_cached_dir = https_cached_dir / path_parent
        https_cached_dir.mkdir(parents=True, exist_ok=True)
        self._cached_object_path = https_cached_dir / pathlib.Path(pathlib.Path(u.path).name)

    def _do_fetch(self) -> None:
        auth = None
        verify = None
        # This order reflects requests library behavior: REQUESTS_CA_BUNDLE comes first.
        for env_var_name in ['REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']:
            if env_var_name in os.environ:
                if pathlib.Path(os.environ[env_var_name]).exists():
                    verify = os.environ[env_var_name]
                    break
                else:
                    err_str = f'Env var ${env_var_name} found but path does not exist: {os.environ[env_var_name]}'
                    logger.warning(err_str)
                    raise TrestleError(f'Cache update failure with bad inputenv var: {err_str}')
        if self._username is not None and self._password is not None:
            auth = HTTPBasicAuth(self._username, self._password)
        try:
            response = requests.get(self._url, auth=auth, verify=verify)
        except Exception as e:
            logger.error(f'Error connecting to {self._url}: {e}')
            raise TrestleError(f'Cache update failure to connect via HTTPS: {self._url} ({e})')

        if response.status_code == 200:
            try:
                result = response.text
            except Exception as err:
                raise TrestleError(f'Cache update failure reading response via HTTPS: {self._url} ({err})')
            else:
                self._cached_object_path.write_text(result)
        else:
            raise TrestleError(f'GET returned code {response.status_code}: {self._uri}')


class SFTPFetcher(FetcherBase):
    """Fetcher for SFTP content."""

    def __init__(self, trestle_root: pathlib.Path, uri: str) -> None:
        """Initialize SFTP fetcher. Update the expected cache path as per caching specs.

        Args:
            trestle_root: Path of the Trestle project path, i.e., within which .trestle is to be found.
            uri: Reference to the remote file to cache that can be fetched using the sftp:// scheme.
        """
        super().__init__(trestle_root, uri)
        # Is this a valid URI, however? Username and password are optional, of course.
        u = parse.urlparse(self._uri)
        if not u.hostname:
            logger.error(f'Malformed URI, cannot parse hostname in URL {self._uri}')
            raise TrestleError(f'Cache request for invalid input URI: missing hostname {self._uri}')
        if not u.path:
            logger.error(f'Malformed URI, cannot parse path in URL {self._uri}')
            raise TrestleError(f'Cache request for invalid input URI: missing file path {self._uri}')

        sftp_cached_dir = self._trestle_cache_path / u.hostname
        # Skip any number of back- or forward slashes preceding the URL path (u.path)
        path_parent = pathlib.Path(u.path[re.search('[^/\\\\]', u.path).span()[0]:]).parent
        sftp_cached_dir = sftp_cached_dir / path_parent
        sftp_cached_dir.mkdir(parents=True, exist_ok=True)
        self._cached_object_path = sftp_cached_dir / pathlib.Path(pathlib.Path(u.path).name)

    def _do_fetch(self) -> None:
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

        localpath = self._cached_object_path
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
class FetcherFactory:
    """Factory method for creating a fetcher."""

    @classmethod
    def get_fetcher(cls, trestle_root: pathlib.Path, uri: str) -> FetcherBase:
        """Return an instantiated fetcher object based on the URI.

        Args:
            trestle_root: Path of the Trestle project path, i.e., within which .trestle is to be found.
            uri: Reference to the remote object to cache.

        Returns:
            fetcher object for the given URI.
        """
        # Basic correctness test
        if len(uri) <= 9 or ('/' not in uri and re.match(const.WINDOWS_DRIVE_URI_REGEX, uri) is None):
            raise TrestleError(f'Unable to fetch uri as it appears to be invalid {uri}')

        if uri[0] == '/' or uri.startswith(const.FILE_URI):
            # Note assumption here is that relative paths are not yet supported
            # so these are not allowed for just yet: uri[0:3] == '../' or uri[0:2] == './'
            return LocalFetcher(trestle_root, uri)
        elif uri.startswith(const.SFTP_URI):
            return SFTPFetcher(trestle_root, uri)
        elif uri.startswith(const.HTTPS_URI):
            return HTTPSFetcher(trestle_root, uri)
        elif uri.startswith(const.TRESTLE_HREF_HEADING):
            return LocalFetcher(trestle_root, uri)
        elif re.match(const.WINDOWS_DRIVE_URI_REGEX, uri) is not None:
            return LocalFetcher(trestle_root, uri)
        else:
            raise TrestleError(f'Unable to fetch URI: {uri} as the uri did not match a suppported format.')
