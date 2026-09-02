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
"""Tests for beta feature management."""

import argparse
import configparser
import io
import os
import pathlib
from typing import List

import pytest
from _pytest.monkeypatch import MonkeyPatch

from trestle.core import beta_features
from trestle.common.err import TrestleError
from trestle.core.beta_features import BetaFeature
from trestle.core.commands.command_docs import CommandBase, CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes


def sample_feature(name: str = 'sample') -> BetaFeature:
    """Create a sample beta feature for tests."""
    return BetaFeature(
        name=name,
        description='Sample beta feature',
        commands=[f'trestle {name}'],
        since_version='4.0.0',
        stability='beta',
        documentation_url='https://example.com/beta/sample',
        enabled_by_default=False,
        deprecation_version=None,
    )


def patch_beta_features(monkeypatch: MonkeyPatch, *features: BetaFeature) -> None:
    """Patch the beta registry with sample features."""
    monkeypatch.setattr(beta_features, 'BETA_FEATURES', {feature.name: feature for feature in features})
    monkeypatch.delenv(beta_features.TRESTLE_BETA_FEATURES_ENV, raising=False)


def test_parse_feature_names_accepts_commas_and_whitespace() -> None:
    """Test parsing beta feature names."""
    assert beta_features.parse_feature_names('one,two three, four') == {'one', 'two', 'three', 'four'}


def test_enable_disable_feature_persists_to_workspace_config(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test enabling and disabling a beta feature in .trestle/config.ini."""
    patch_beta_features(monkeypatch, sample_feature())

    assert beta_features.enable_feature('sample', tmp_trestle_dir)
    assert beta_features.is_beta_enabled('sample', tmp_trestle_dir)
    assert not beta_features.enable_feature('sample', tmp_trestle_dir)

    config = configparser.ConfigParser()
    config.read(beta_features.get_beta_config_path(tmp_trestle_dir))
    assert config.get(beta_features.BETA_SECTION, beta_features.ENABLED_FEATURES_KEY) == 'sample'

    assert beta_features.disable_feature('sample', tmp_trestle_dir)
    assert not beta_features.is_beta_enabled('sample', tmp_trestle_dir)
    assert not beta_features.disable_feature('sample', tmp_trestle_dir)


def test_enable_disable_all_features_preserves_unknown_config(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test bulk beta updates preserve unregistered config entries."""
    patch_beta_features(monkeypatch, sample_feature('one'), sample_feature('two'))
    config_path = beta_features.get_beta_config_path(tmp_trestle_dir)
    config_path.write_text('[beta]\nenabled_features = legacy\n', encoding='utf-8')

    assert beta_features.enable_all_features(tmp_trestle_dir) == 2
    assert beta_features.get_enabled_features(tmp_trestle_dir) == {'one', 'two'}
    assert beta_features.enable_all_features(tmp_trestle_dir) == 0

    assert beta_features.disable_all_features(tmp_trestle_dir) == 2
    assert not beta_features.get_enabled_features(tmp_trestle_dir)
    assert beta_features.disable_all_features(tmp_trestle_dir) == 0

    config = configparser.ConfigParser()
    config.read(config_path)
    assert config.get(beta_features.BETA_SECTION, beta_features.ENABLED_FEATURES_KEY) == 'legacy'


def test_enable_feature_preserves_existing_config_sections(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test beta config updates do not erase other config sections."""
    patch_beta_features(monkeypatch, sample_feature())
    config_path = beta_features.get_beta_config_path(tmp_trestle_dir)
    config_path.write_text('[task.example]\nkey = value\n', encoding='utf-8')

    assert beta_features.enable_feature('sample', tmp_trestle_dir)

    config = configparser.ConfigParser()
    config.read(config_path)
    assert config.get('task.example', 'key') == 'value'
    assert config.get(beta_features.BETA_SECTION, beta_features.ENABLED_FEATURES_KEY) == 'sample'


def test_nested_workspace_path_uses_workspace_config(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test beta config uses workspace config from nested workspace paths."""
    patch_beta_features(monkeypatch, sample_feature())
    user_config_root = tmp_trestle_dir / 'user-config'
    monkeypatch.setenv('XDG_CONFIG_HOME', str(user_config_root))
    nested_path = tmp_trestle_dir / 'catalogs' / 'nist'
    nested_path.mkdir(parents=True)

    assert beta_features.enable_feature('sample', nested_path)

    workspace_config_path = tmp_trestle_dir / '.trestle' / 'config.ini'
    user_config_path = user_config_root / 'trestle' / 'beta.ini'
    config = configparser.ConfigParser()
    config.read(workspace_config_path)
    assert config.get(beta_features.BETA_SECTION, beta_features.ENABLED_FEATURES_KEY) == 'sample'
    assert not user_config_path.exists()
    assert beta_features.is_beta_enabled('sample', nested_path)


def test_environment_variable_enables_beta_feature(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test TRESTLE_BETA_FEATURES enables features without writing config."""
    patch_beta_features(monkeypatch, sample_feature())
    monkeypatch.setenv(beta_features.TRESTLE_BETA_FEATURES_ENV, 'sample')

    assert beta_features.is_beta_enabled('sample', tmp_trestle_dir)


def test_disable_feature_rejects_environment_enabled_feature(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test env-enabled beta features cannot be disabled through config."""
    patch_beta_features(monkeypatch, sample_feature())
    monkeypatch.setenv(beta_features.TRESTLE_BETA_FEATURES_ENV, 'sample')

    with pytest.raises(TrestleError, match='enabled by TRESTLE_BETA_FEATURES'):
        beta_features.disable_feature('sample', tmp_trestle_dir)

    assert beta_features.is_beta_enabled('sample', tmp_trestle_dir)


def test_enabled_by_default_feature_is_enabled_and_cannot_be_disabled(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test beta features enabled by default are always enabled."""
    feature = BetaFeature(
        name='default-sample',
        description='Default sample beta feature',
        commands=['trestle default-sample'],
        since_version='4.0.0',
        stability='beta',
        documentation_url='https://example.com/beta/default-sample',
        enabled_by_default=True,
    )
    patch_beta_features(monkeypatch, feature)

    assert beta_features.is_beta_enabled('default-sample', tmp_trestle_dir)
    with pytest.raises(TrestleError, match='enabled by default and cannot be disabled'):
        beta_features.disable_feature('default-sample', tmp_trestle_dir)


def test_user_config_path_is_used_without_workspace(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test user config fallback path when no .trestle directory exists."""
    if os.name == 'nt':  # pragma: no cover
        monkeypatch.setenv('APPDATA', str(tmp_path / 'appdata'))
        expected_path = tmp_path / 'appdata' / 'trestle' / 'beta.ini'
    else:
        monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg'))
        expected_path = tmp_path / 'xdg' / 'trestle' / 'beta.ini'

    assert beta_features.get_beta_config_path(tmp_path) == expected_path


def test_beta_decorator_blocks_disabled_feature(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test beta_feature decorator blocks disabled beta features."""
    patch_beta_features(monkeypatch, sample_feature())
    command = DummyBetaCommand()

    result = command.run(argparse.Namespace(trestle_root=tmp_trestle_dir))

    assert result == CmdReturnCodes.COMMAND_ERROR.value
    assert "The 'sample' command is a beta feature and is not enabled." in command.messages[0]


def test_beta_decorator_allows_enabled_feature(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test beta_feature decorator runs enabled beta features."""
    patch_beta_features(monkeypatch, sample_feature())
    assert beta_features.enable_feature('sample', tmp_trestle_dir)
    command = DummyBetaCommand()

    result = command.run(argparse.Namespace(trestle_root=tmp_trestle_dir))

    assert result == 123


def test_beta_decorator_allows_one_time_beta_flag(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test beta_feature decorator runs with one-time beta flag without persisting config."""
    patch_beta_features(monkeypatch, sample_feature())
    command = DummyBetaCommand()

    result = command.run(argparse.Namespace(trestle_root=tmp_trestle_dir, beta=True))

    assert result == 123
    assert not beta_features.is_beta_enabled('sample', tmp_trestle_dir)


def test_beta_decorator_beta_flag_requires_registered_feature(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test beta flag does not bypass beta feature registration."""
    patch_beta_features(monkeypatch)
    command = DummyBetaCommand()

    with pytest.raises(TrestleError, match="Beta feature 'sample' not found."):
        command.run(argparse.Namespace(trestle_root=tmp_trestle_dir, beta=True))


def test_get_beta_feature_name_reads_decorated_function() -> None:
    """Test beta feature name is available on a decorated function."""
    assert beta_features.get_beta_feature_name(DummyBetaCommandBase._run) == 'sample'


def test_command_base_allows_beta_flag_for_beta_command() -> None:
    """Test CommandBase accepts beta flag for beta-gated commands."""
    command = DummyBetaCommandBase()

    assert command._validate_arguments(argparse.Namespace(beta=True)) is None


def test_beta_command_help_shows_beta_flag() -> None:
    """Test beta-gated commands show the one-time beta flag in help."""
    command = DummyBetaCommandBase()

    assert beta_features.BETA_FLAG_HELP in command.parser.format_help()


def test_command_plus_docs_warns_beta_flag_for_non_beta_command(tmp_trestle_dir: pathlib.Path) -> None:
    """Test CommandPlusDocs warns but proceeds when beta flag is passed to a non-beta-gated command."""
    err_stream = io.StringIO()
    command = DummyCommandPlusDocs(err=err_stream)

    assert (
        command._validate_arguments(argparse.Namespace(beta=True, trestle_root=tmp_trestle_dir))
        == CmdReturnCodes.SUCCESS.value
    )
    assert '--beta flag is only effective for beta level commands' in err_stream.getvalue()


def test_command_plus_docs_rejects_invalid_oscal_directories(tmp_path: pathlib.Path) -> None:
    """Test CommandPlusDocs still rejects invalid trestle workspace contents."""
    workspace = tmp_path / 'workspace'
    (workspace / '.trestle').mkdir(parents=True)
    catalogs_dir = workspace / 'catalogs'
    catalogs_dir.mkdir()
    (catalogs_dir / 'bad.txt').write_text('not allowed', encoding='utf-8')
    command = DummyCommandPlusDocs()

    assert (
        command._validate_arguments(argparse.Namespace(beta=False, trestle_root=workspace))
        == CmdReturnCodes.TRESTLE_ROOT_ERROR.value
    )


class DummyBetaCommand:
    """Dummy command for beta decorator tests."""

    name = 'sample'

    def __init__(self) -> None:
        """Initialize dummy command."""
        self.messages: List[str] = []

    def out(self, message: str) -> None:
        """Capture command output."""
        self.messages.append(message)

    @beta_features.beta_feature('sample')
    def run(self, args: argparse.Namespace) -> int:
        """Run the dummy command."""
        return 123


class DummyBetaCommandBase(CommandBase):
    """Dummy CommandBase beta command for validation tests."""

    name = 'sample'

    @beta_features.beta_feature('sample')
    def _run(self, args: argparse.Namespace) -> int:
        """Run the dummy command."""
        return 123


class DummyCommandPlusDocs(CommandPlusDocs):
    """Dummy CommandPlusDocs command for validation tests."""

    name = 'sample-docs'
