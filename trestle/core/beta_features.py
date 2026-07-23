# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Beta feature registration and configuration support."""

import configparser
import functools
import os
import pathlib
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, TypeVar, cast

from trestle.common import const, file_utils
from trestle.common.err import TrestleError
from trestle.core.commands.common.return_codes import CmdReturnCodes

BETA_SECTION = 'beta'
ENABLED_FEATURES_KEY = 'enabled_features'
TRESTLE_BETA_FEATURES_ENV = 'TRESTLE_BETA_FEATURES'
BETA_FEATURE_ATTR = '_trestle_beta_feature'
BETA_FLAG_HELP = 'Run this beta command one time without enabling it in config.'
BetaCallable = TypeVar('BetaCallable', bound=Callable[..., int])


@dataclass(frozen=True)
class BetaFeature:
    """Definition of a beta feature."""

    name: str
    description: str
    commands: List[str]
    since_version: str
    stability: str
    documentation_url: str
    enabled_by_default: bool = False
    deprecation_version: Optional[str] = None


BETA_FEATURES: Dict[str, BetaFeature] = {
    'json-signing': BetaFeature(
        name='json-signing',
        description='Sign and verify JSON artifacts with detached DSSE envelopes.',
        commands=['trestle sign', 'trestle verify'],
        since_version='4.0.3',
        stability='beta',
        documentation_url='https://oscal-compass.github.io/compliance-trestle/tutorials/cli/#trestle-sign',
        enabled_by_default=False,
        deprecation_version=None,
    ),
    'json-manifest-signing': BetaFeature(
        name='json-manifest-signing',
        description='Sign and verify JSON package manifests for JSON artifacts with detached DSSE envelopes.',
        commands=['trestle sign-manifest', 'trestle verify-manifest'],
        since_version='4.0.3',
        stability='beta',
        documentation_url='https://oscal-compass.github.io/compliance-trestle/tutorials/cli/#trestle-sign-manifest',
        enabled_by_default=False,
        deprecation_version=None,
    ),
}


def parse_feature_names(feature_names: str) -> Set[str]:
    """Parse comma and whitespace separated beta feature names."""
    normalized_feature_names = feature_names.replace(',', ' ')
    return {name.strip() for name in normalized_feature_names.split() if name.strip()}


def get_user_beta_config_path() -> pathlib.Path:
    """Get the user-level beta feature config path."""
    if os.name == 'nt':  # pragma: no cover
        appdata = os.environ.get('APPDATA')
        config_root = pathlib.Path(appdata) if appdata else pathlib.Path.home() / 'AppData' / 'Roaming'
    else:
        config_root = pathlib.Path(os.environ.get('XDG_CONFIG_HOME', pathlib.Path.home() / '.config'))
    return config_root / 'trestle' / 'beta.ini'


def get_beta_config_path(trestle_root: pathlib.Path) -> pathlib.Path:
    """Get the beta config path for a trestle workspace path or the user fallback."""
    workspace_root = file_utils.extract_trestle_project_root(pathlib.Path(trestle_root).resolve())
    if workspace_root is not None:
        return workspace_root / const.TRESTLE_CONFIG_DIR / const.TRESTLE_CONFIG_FILE
    return get_user_beta_config_path()


def get_beta_feature(feature_name: str) -> BetaFeature:
    """Get a registered beta feature by name."""
    try:
        return BETA_FEATURES[feature_name]
    except KeyError:
        raise TrestleError(f"Beta feature '{feature_name}' not found.")


def get_registered_features() -> Dict[str, BetaFeature]:
    """Get all registered beta features."""
    return BETA_FEATURES


def get_enabled_features(trestle_root: pathlib.Path) -> Set[str]:
    """Get registered beta features enabled for the given trestle root."""
    enabled_features = _read_config_enabled_features(get_beta_config_path(trestle_root))
    enabled_features.update(_read_environment_enabled_features())

    for feature_name, feature in BETA_FEATURES.items():
        if feature.enabled_by_default:
            enabled_features.add(feature_name)

    return {feature_name for feature_name in enabled_features if feature_name in BETA_FEATURES}


def is_beta_enabled(feature_name: str, trestle_root: pathlib.Path) -> bool:
    """Return True if the beta feature is registered and enabled."""
    get_beta_feature(feature_name)
    return feature_name in get_enabled_features(trestle_root)


def enable_feature(feature_name: str, trestle_root: pathlib.Path) -> bool:
    """Enable a beta feature in the selected config file and return True if it changed."""
    get_beta_feature(feature_name)
    config_path = get_beta_config_path(trestle_root)
    enabled_features = _read_config_enabled_features(config_path)

    if feature_name in enabled_features:
        return False

    enabled_features.add(feature_name)
    _write_config_enabled_features(config_path, enabled_features)
    return True


def disable_feature(feature_name: str, trestle_root: pathlib.Path) -> bool:
    """Disable a beta feature in the selected config file and return True if it changed."""
    feature = get_beta_feature(feature_name)
    if feature.enabled_by_default:
        raise TrestleError(f"Beta feature '{feature_name}' is enabled by default and cannot be disabled.")
    if feature_name in _read_environment_enabled_features():
        raise TrestleError(
            f"Beta feature '{feature_name}' is enabled by {TRESTLE_BETA_FEATURES_ENV}. "
            f'Remove it from {TRESTLE_BETA_FEATURES_ENV} to disable it.'
        )

    config_path = get_beta_config_path(trestle_root)
    enabled_features = _read_config_enabled_features(config_path)

    if feature_name not in enabled_features:
        return False

    enabled_features.remove(feature_name)
    _write_config_enabled_features(config_path, enabled_features)
    return True


def beta_feature(feature_name: str) -> Callable[[BetaCallable], BetaCallable]:
    """Decorate a command run method so it requires an enabled beta feature."""

    def decorator(func: BetaCallable) -> BetaCallable:
        @functools.wraps(func)
        def wrapper(self: Any, args: Any, *func_args: Any, **func_kwargs: Any) -> int:
            trestle_root = pathlib.Path(getattr(args, 'trestle_root', pathlib.Path.cwd()))
            feature = get_beta_feature(feature_name)
            if getattr(args, 'beta', False) or feature_name in get_enabled_features(trestle_root):
                return func(self, args, *func_args, **func_kwargs)

            self.out(f"Error: The '{self.name}' command is a beta feature and is not enabled.")
            self.out('')
            self.out(f'Feature: {feature.name}')
            self.out(f'Description: {feature.description}')
            self.out(f'Stability: {feature.stability}')
            if feature.documentation_url:
                self.out(f'Documentation: {feature.documentation_url}')
            self.out('')
            self.out('To enable this feature, run:')
            self.out(f'  trestle beta enable {feature.name}')
            return CmdReturnCodes.COMMAND_ERROR.value

        setattr(wrapper, BETA_FEATURE_ATTR, feature_name)
        return cast(BetaCallable, wrapper)

    return decorator


def get_beta_feature_name(command_callable: Callable[..., Any]) -> Optional[str]:
    """Get the beta feature name from a decorated command callable if present."""
    feature_name = getattr(command_callable, BETA_FEATURE_ATTR, None)
    if feature_name is not None:
        return cast(str, feature_name)
    bound_function = getattr(command_callable, '__func__', None)
    return cast(Optional[str], getattr(bound_function, BETA_FEATURE_ATTR, None))


def _read_config_enabled_features(config_path: pathlib.Path) -> Set[str]:
    """Read enabled beta features from a config file."""
    config = _read_config(config_path)
    if not config.has_section(BETA_SECTION) or not config.has_option(BETA_SECTION, ENABLED_FEATURES_KEY):
        return set()
    return parse_feature_names(config.get(BETA_SECTION, ENABLED_FEATURES_KEY))


def _read_environment_enabled_features() -> Set[str]:
    """Read enabled beta features from environment."""
    return parse_feature_names(os.environ.get(TRESTLE_BETA_FEATURES_ENV, ''))


def _write_config_enabled_features(config_path: pathlib.Path, enabled_features: Iterable[str]) -> None:
    """Write enabled beta features to a config file."""
    config = _read_config(config_path)
    if not config.has_section(BETA_SECTION):
        config.add_section(BETA_SECTION)

    config.set(BETA_SECTION, ENABLED_FEATURES_KEY, ','.join(sorted(enabled_features)))
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open('w', encoding=const.FILE_ENCODING) as config_file:
        config.write(config_file)


def _read_config(config_path: pathlib.Path) -> configparser.ConfigParser:
    """Read a config file if it exists."""
    config = configparser.ConfigParser()
    if config_path.exists():
        config.read(config_path, encoding=const.FILE_ENCODING)
    return config
