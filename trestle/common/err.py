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
"""Trestle core errors module."""
from logging import Logger

from trestle.common.log import get_current_verbosity_level
from trestle.core.commands.common.return_codes import CmdReturnCodes


class TrestleError(RuntimeError):
    """
    General framework (non-application) related errors.

    Attributes:
        msg (str): Human readable string describing the exception.
    """

    def __init__(self, msg: str):
        """Intialization for TresleError.

        Args:
            msg (str): The error message
        """
        RuntimeError.__init__(self)
        self.msg = msg

    def __str__(self) -> str:
        """Return Trestle error message if asked for a string."""
        return self.msg


class TrestleNotFoundError(TrestleError):
    """
    General framework related not found error.

    Attributes:
        msg (str): Human readable string describing the exception.
    """

    def __init__(self, msg: str):
        """
        Intialize TresleNotFoundError.

        Args:
            msg: The error message
        """
        super().__init__(msg)


class TrestleRootError(TrestleError):
    """General error for trestle workspace root/setup errors."""

    def __init__(self, msg: str):
        """
        Initialize TrestleRootError.

        Args:
            msg (str): The error message
        """
        super().__init__(msg)


class TrestleIncorrectArgsError(TrestleError):
    """General error for incorrect args passed to Trestle command."""

    def __init__(self, msg: str):
        """
        Initialize TrestleIncorrectArgsError.

        Args:
            msg (str): The error message
        """
        super().__init__(msg)


def handle_generic_command_exception(
    exception: Exception, logger: Logger, msg: str = 'Exception occured during execution'
) -> int:
    """Print out error message based on the verbosity and return appropriate status code."""
    if get_current_verbosity_level(logger) == 0:
        logger.error(msg + f': {exception}')
    else:
        logger.exception(msg + f': {exception}')

    return _exception_to_error_code(exception)


def _exception_to_error_code(exception: Exception) -> int:
    """Convert exception to the status code."""
    if isinstance(exception, TrestleRootError):
        return CmdReturnCodes.TRESTLE_ROOT_ERROR.value
    elif isinstance(exception, TrestleIncorrectArgsError):
        return CmdReturnCodes.INCORRECT_ARGS.value

    return CmdReturnCodes.COMMAND_ERROR.value
