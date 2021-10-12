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
    General framwork related not found error.

    Attributes:
        msg (str): Human readable string describing the exception.
    """

    def __init__(self, msg: str):
        """
        Intialization for TresleNotFoundError.

        Args:
            msg: The error message
        """
        super().__init__(msg)


class TrestleValidationError(TrestleError):
    """
    General framwork related validation error.

    Attributes:
        msg (str): Human readable string describing the exception.
    """

    def __init__(self, msg: str):
        """
        Intialization for TresleValidationError.

        Args:
            msg (str): The error message
        """
        super().__init__(msg)
