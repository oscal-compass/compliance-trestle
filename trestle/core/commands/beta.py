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
"""Trestle beta feature command."""

import argparse
import logging
import pathlib
from typing import Iterable

from trestle.common.err import TrestleError, TrestleIncorrectArgsError, handle_generic_command_exception
from trestle.core import beta_features
from trestle.core.beta_features import BetaFeature
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes

logger = logging.getLogger(__name__)


class BetaCmd(CommandBase):
    """Manage experimental trestle beta features.

    Beta features are opt-in commands or behaviors that are available for early testing but are not part of the stable
    trestle interface yet. Use this command to list available beta features, enable them for a workspace or user
    environment, and disable them when they are no longer needed.
    """

    name = 'beta'

    def _init_arguments(self) -> None:
        self.add_argument(
            'action',
            nargs='?',
            choices=['help', 'query', 'enable', 'disable'],
            default='help',
            help='Beta action to run. Use query to list feature status, enable/disable to manage a feature, or help.',
        )
        self.add_argument(
            'feature',
            nargs='?',
            help='Beta feature name to enable or disable. Use "trestle beta query" to list available features.',
        )
        self.add_argument(
            '--verbose',
            dest='beta_verbose',
            action='store_true',
            help='Show feature descriptions, commands, stability, and documentation links when querying.',
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            trestle_root = pathlib.Path(args.trestle_root)

            if args.action == 'help':
                self._show_help()
            elif args.action == 'query':
                self._show_query(trestle_root, args.beta_verbose)
            elif args.action == 'enable':
                self._enable_feature(args.feature, trestle_root)
            elif args.action == 'disable':
                self._disable_feature(args.feature, trestle_root)

            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while executing trestle beta')

    def _show_help(self) -> None:
        """Show beta command help."""
        self.out('Trestle Beta Feature Management')
        self.out('')
        self.out('The beta command manages experimental features in trestle.')
        self.out('Beta features are under active development and may change or be removed in future releases.')
        self.out('')
        self.out('Usage:')
        self.out('  trestle beta help              Show this help message')
        self.out('  trestle beta query             List beta features and their status')
        self.out('  trestle beta enable <feature>  Enable a beta feature')
        self.out('  trestle beta disable <feature> Disable a beta feature')
        self.out('  trestle beta enable all        Enable all beta features')
        self.out('  trestle beta disable all       Disable all config-enabled beta features')
        self.out('')
        self.out('Use "trestle beta query --verbose" for detailed descriptions.')

    def _show_query(self, trestle_root: pathlib.Path, verbose: bool) -> None:
        """Show beta feature status."""
        registered_features = beta_features.get_registered_features()
        if not registered_features:
            self.out('No beta features are registered.')
            return

        enabled_features = beta_features.get_enabled_features(trestle_root)
        enabled = [
            feature for feature_name, feature in sorted(registered_features.items()) if feature_name in enabled_features
        ]
        disabled = [
            feature
            for feature_name, feature in sorted(registered_features.items())
            if feature_name not in enabled_features
        ]

        self.out('Beta Features Status:')
        self.out('')
        self._show_feature_group('Enabled', enabled, enabled_features, verbose)
        self.out('')
        self._show_feature_group('Available (Disabled)', disabled, enabled_features, verbose)
        self.out('')
        self.out('Use "trestle beta enable <feature>" to enable a feature.')

    def _show_feature_group(
        self, title: str, features: Iterable[BetaFeature], enabled_features: set[str], verbose: bool
    ) -> None:
        """Show one group of beta features."""
        self.out(f'{title}:')
        feature_list = list(features)
        if not feature_list:
            self.out('  None')
            return

        name_width = max(len(feature.name) for feature in feature_list)
        for feature in feature_list:
            status = 'enabled' if feature.name in enabled_features else 'disabled'
            if not verbose:
                self.out(f'  [{status}] {feature.name:<{name_width}} {feature.description}')
            else:
                self._show_verbose_feature(feature, status)

    def _show_verbose_feature(self, feature: BetaFeature, status: str) -> None:
        """Show detailed beta feature information."""
        self.out(f'  [{status}] {feature.name}')
        self.out(f'    Description: {feature.description}')
        self.out(f'    Status: {status.capitalize()}')
        self.out(f'    Since: {feature.since_version}')
        self.out(f'    Stability: {feature.stability}')
        if feature.commands:
            self.out(f'    Commands: {", ".join(feature.commands)}')
        if feature.documentation_url:
            self.out(f'    Documentation: {feature.documentation_url}')
        if feature.deprecation_version:
            self.out(f'    Deprecated in: {feature.deprecation_version}')

    def _enable_feature(self, feature_name: str, trestle_root: pathlib.Path) -> None:
        """Enable a beta feature."""
        if not feature_name:
            raise TrestleIncorrectArgsError('A beta feature name is required.')
        if feature_name == 'all':
            changed = beta_features.enable_all_features(trestle_root)
            self.out(f'Enabled {changed} beta feature(s).')
            return

        feature = self._get_feature(feature_name)
        changed = beta_features.enable_feature(feature_name, trestle_root)
        if not changed:
            self.out(f"Beta feature '{feature_name}' is already enabled.")
            return

        self.out(f"Beta feature '{feature_name}' has been enabled.")
        self.out('')
        self.out('This feature is experimental and may change in future releases.')
        if feature.documentation_url:
            self.out(f'Documentation: {feature.documentation_url}')
        if feature.commands:
            self.out('')
            self.out('Available commands:')
            for command in feature.commands:
                self.out(f'  {command} --help')
        self.out('')
        self.out('To disable this feature, run:')
        self.out(f'  trestle beta disable {feature_name}')

    def _disable_feature(self, feature_name: str, trestle_root: pathlib.Path) -> None:
        """Disable a beta feature."""
        if not feature_name:
            raise TrestleIncorrectArgsError('A beta feature name is required.')
        if feature_name == 'all':
            changed = beta_features.disable_all_features(trestle_root)
            self.out(f'Disabled {changed} beta feature(s).')
            remaining = beta_features.get_enabled_features(trestle_root)
            if remaining:
                self.out(f'Features still enabled by environment or default: {", ".join(sorted(remaining))}')
            return

        feature = self._get_feature(feature_name)
        changed = beta_features.disable_feature(feature_name, trestle_root)
        if not changed:
            self.out(f"Beta feature '{feature_name}' is already disabled.")
            return

        self.out(f"Beta feature '{feature_name}' has been disabled.")
        if feature.commands:
            self.out('')
            self.out('The following commands are no longer enabled:')
            for command in feature.commands:
                self.out(f'  {command}')
        self.out('')
        self.out('To re-enable this feature, run:')
        self.out(f'  trestle beta enable {feature_name}')

    def _get_feature(self, feature_name: str) -> BetaFeature:
        """Get a feature and print beta-specific guidance if it is unknown."""
        try:
            return beta_features.get_beta_feature(feature_name)
        except TrestleError:
            self._show_unknown_feature(feature_name)
            raise

    def _show_unknown_feature(self, feature_name: str) -> None:
        """Show unknown beta feature guidance."""
        self.out(f"Error: Beta feature '{feature_name}' not found.")
        registered_features = sorted(beta_features.get_registered_features().keys())
        if registered_features:
            self.out('')
            self.out('Available beta features:')
            for registered_feature in registered_features:
                self.out(f'  - {registered_feature}')
        self.out('')
        self.out('Use "trestle beta query" to see all available features.')
