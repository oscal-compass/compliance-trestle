# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Trestle Validate Command."""

import argparse
import logging
import traceback

import trestle.core.validator_factory as vfact
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.const import VAL_MODE_ALL
from trestle.core.err import TrestleError

logger = logging.getLogger(__name__)


class ValidateCmd(CommandPlusDocs):
    """Validate contents of a trestle model in different modes."""

    name = 'validate'

    def _init_arguments(self) -> None:
        vfact.init_arguments(self)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            logger.debug('Entering trestle validate.')

            log.set_log_level_from_args(args)

            mode_args = argparse.Namespace(mode=VAL_MODE_ALL)
            validator = vfact.validator_factory.get(mode_args)

            return validator.validate(args)
        except TrestleError as e:
            logger.debug(traceback.format_exc())
            logger.error(f'Error while validating contents of a trestle model: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            logger.debug(traceback.format_exc())
            logger.error(f'Unexpected error while validating contents of a trestle model: {e}')
            return CmdReturnCodes.UNKNOWN_ERROR.value
