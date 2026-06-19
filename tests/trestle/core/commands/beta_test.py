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
"""Tests for trestle beta command."""

import pathlib
import sys

from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

import pytest
from tests.test_utils import execute_command_and_assert

from trestle.cli import Trestle
from trestle.core import beta_features
from trestle.core.beta_features import BetaFeature
from trestle.core.commands.common.return_codes import CmdReturnCodes


def sample_feature(name: str = 'sample', deprecation_version: str | None = None) -> BetaFeature:
    """Create a sample beta feature for tests."""
    return BetaFeature(
        name=name,
        description='Sample beta feature',
        commands=[f'trestle {name}'],
        since_version='4.0.0',
        stability='beta',
        documentation_url='https://example.com/beta/sample',
        enabled_by_default=False,
        deprecation_version=deprecation_version,
    )


def patch_beta_features(monkeypatch: MonkeyPatch, *features: BetaFeature) -> None:
    """Patch the beta registry with sample features."""
    monkeypatch.setattr(beta_features, 'BETA_FEATURES', {feature.name: feature for feature in features})
    monkeypatch.delenv(beta_features.TRESTLE_BETA_FEATURES_ENV, raising=False)


def test_beta_help(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test trestle beta help output."""
    execute_command_and_assert('trestle beta help', CmdReturnCodes.SUCCESS.value, monkeypatch)

    output, _ = capsys.readouterr()
    assert 'Trestle Beta Feature Management' in output
    assert 'trestle beta enable <feature>' in output


def test_beta_query_no_features(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test query when no beta features are registered."""
    patch_beta_features(monkeypatch)

    execute_command_and_assert('trestle beta query', CmdReturnCodes.SUCCESS.value, monkeypatch)

    output, _ = capsys.readouterr()
    assert 'No beta features are registered.' in output


def test_beta_enable_query_disable_feature(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    """Test enabling, querying, and disabling a beta feature."""
    patch_beta_features(monkeypatch, sample_feature())

    execute_command_and_assert('trestle beta enable sample', CmdReturnCodes.SUCCESS.value, monkeypatch)
    output, _ = capsys.readouterr()
    assert "Beta feature 'sample' has been enabled." in output
    assert beta_features.is_beta_enabled('sample', tmp_trestle_dir)

    execute_command_and_assert('trestle beta query', CmdReturnCodes.SUCCESS.value, monkeypatch)
    output, _ = capsys.readouterr()
    assert '[enabled] sample' in output

    execute_command_and_assert('trestle beta disable sample', CmdReturnCodes.SUCCESS.value, monkeypatch)
    output, _ = capsys.readouterr()
    assert "Beta feature 'sample' has been disabled." in output
    assert not beta_features.is_beta_enabled('sample', tmp_trestle_dir)


def test_beta_query_verbose(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test verbose beta query output."""
    patch_beta_features(monkeypatch, sample_feature())

    execute_command_and_assert('trestle beta query --verbose', CmdReturnCodes.SUCCESS.value, monkeypatch)

    output, _ = capsys.readouterr()
    assert 'Description: Sample beta feature' in output
    assert 'Commands: trestle sample' in output
    assert 'Documentation: https://example.com/beta/sample' in output


def test_beta_query_verbose_shows_deprecation(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test verbose beta query output includes deprecation version."""
    patch_beta_features(monkeypatch, sample_feature(deprecation_version='5.0.0'))

    execute_command_and_assert('trestle beta query --verbose', CmdReturnCodes.SUCCESS.value, monkeypatch)

    output, _ = capsys.readouterr()
    assert 'Deprecated in: 5.0.0' in output


def test_beta_query_global_verbose_does_not_show_details(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test global verbose does not trigger verbose beta query output."""
    patch_beta_features(monkeypatch, sample_feature())

    execute_command_and_assert('trestle beta -v query', CmdReturnCodes.SUCCESS.value, monkeypatch)

    output, _ = capsys.readouterr()
    assert '[disabled] sample' in output
    assert 'Description: Sample beta feature' not in output


def test_beta_unknown_feature(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test enabling an unknown beta feature fails."""
    patch_beta_features(monkeypatch, sample_feature())

    execute_command_and_assert('trestle beta enable unknown', CmdReturnCodes.COMMAND_ERROR.value, monkeypatch)
    output, _ = capsys.readouterr()
    assert "Error: Beta feature 'unknown' not found." in output
    assert 'Available beta features:' in output
    assert '  - sample' in output


def test_beta_enable_already_enabled(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    """Test enabling an already-enabled beta feature reports no change."""
    patch_beta_features(monkeypatch, sample_feature())
    assert beta_features.enable_feature('sample', tmp_trestle_dir)

    execute_command_and_assert('trestle beta enable sample', CmdReturnCodes.SUCCESS.value, monkeypatch)

    output, _ = capsys.readouterr()
    assert "Beta feature 'sample' is already enabled." in output


def test_beta_disable_already_disabled(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test disabling an already-disabled beta feature reports no change."""
    patch_beta_features(monkeypatch, sample_feature())

    execute_command_and_assert('trestle beta disable sample', CmdReturnCodes.SUCCESS.value, monkeypatch)

    output, _ = capsys.readouterr()
    assert "Beta feature 'sample' is already disabled." in output


def test_beta_disable_environment_enabled_feature(monkeypatch: MonkeyPatch) -> None:
    """Test disabling an environment-enabled beta feature fails clearly."""
    patch_beta_features(monkeypatch, sample_feature())
    monkeypatch.setenv(beta_features.TRESTLE_BETA_FEATURES_ENV, 'sample')

    execute_command_and_assert('trestle beta disable sample', CmdReturnCodes.COMMAND_ERROR.value, monkeypatch)


def test_normal_command_rejects_beta_flag(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test non-beta commands reject the one-time beta flag."""
    execute_command_and_assert('trestle version --beta', CmdReturnCodes.INCORRECT_ARGS.value, monkeypatch)

    _, error = capsys.readouterr()
    assert '--beta can only be used with beta commands' in error


def test_normal_command_help_hides_beta_flag(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    """Test non-beta command help does not show the one-time beta flag."""
    monkeypatch.setattr(sys, 'argv', ['trestle', 'version', '--help'])

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        Trestle().run()

    assert pytest_wrapped_e.value.code == 0
    output, _ = capsys.readouterr()
    assert '--beta' not in output


def test_beta_missing_feature_name(monkeypatch: MonkeyPatch) -> None:
    """Test enable requires a feature name."""
    execute_command_and_assert('trestle beta enable', CmdReturnCodes.INCORRECT_ARGS.value, monkeypatch)


def test_beta_disable_missing_feature_name(monkeypatch: MonkeyPatch) -> None:
    """Test disable requires a feature name."""
    execute_command_and_assert('trestle beta disable', CmdReturnCodes.INCORRECT_ARGS.value, monkeypatch)
