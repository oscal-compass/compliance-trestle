# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Trestle command abstraction.

Improves parsing until such a point as ILCLI is fixed.
"""

import argparse
import logging
from typing import Optional, TextIO

from ilcli import Command

from trestle.common import file_utils
from trestle.core import beta_features
from trestle.core.commands.common.return_codes import CmdReturnCodes

logger = logging.getLogger(__name__)


class CommandBase(Command):
    """Linear extension to the ILCLI interface to use documentation string more.

    Trestle commands not requiring trestle-root should extend from this class.
    """

    # Example commands extedning from this class - init', 'trestle', 'version', 'partial-object-validate'
    def __init__(
        self,
        parser: Optional[argparse.ArgumentParser] = None,
        parent: Optional[Command] = None,
        name: Optional[str] = None,
        out: Optional[TextIO] = None,
        err: Optional[TextIO] = None,
    ) -> None:
        """Override default ILCLI behaviour to include class documentation in command help description."""
        super().__init__(parser, parent, name, out, err)
        self.parser.description = self.__doc__
        if beta_features.get_beta_feature_name(self._run) is not None:
            self.add_argument('--beta', help=beta_features.BETA_FLAG_HELP, action='store_true')

    def _validate_arguments(self, args: argparse.Namespace) -> Optional[int]:
        """Validate common trestle command arguments."""
        return self._validate_beta_argument(args)

    def _validate_beta_argument(self, args: argparse.Namespace) -> Optional[int]:
        """Warn if the one-time beta flag is passed to a command that is not beta-gated."""
        if self.subcommands or not getattr(args, 'beta', False):
            return None
        if beta_features.get_beta_feature_name(self._run) is not None:
            return None
        self.err('Warning: --beta flag is only effective for beta level commands.')
        return None


class CommandPlusDocs(CommandBase):
    """This class validates trestle-root argument.

    Trestle commands requiring trestle-root should extend from this class.
    All commands that extend this class will validate the state of trestle workspace.
    """

    def _validate_arguments(self, args: argparse.ArgumentParser) -> int:
        """Check trestle-root argument is a valid trestle root directory."""
        beta_validation_result = self._validate_beta_argument(args)
        if beta_validation_result is not None:
            return beta_validation_result
        root = file_utils.extract_trestle_project_root(args.trestle_root)
        if root is None:
            logger.error(f'Given directory {args.trestle_root} is not in a valid trestle root directory')
            return CmdReturnCodes.TRESTLE_ROOT_ERROR.value
        is_oscal_dir_valid = file_utils.check_oscal_directories(args.trestle_root)
        if not is_oscal_dir_valid:
            return CmdReturnCodes.TRESTLE_ROOT_ERROR.value
        args.trestle_root = root
        return CmdReturnCodes.SUCCESS.value
