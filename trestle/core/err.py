# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Trestle core errors module."""


class TrestleError(RuntimeError):
    """
    General framework (non-application) related errors.

    Args:
        msg (str): The error message
    """

    def __init__(self, msg: str):
        """Intialization for TresleError."""
        RuntimeError.__init__(self)
        self.msg = msg

    def __str__(self) -> str:
        """Return Trestle error message if asked for a string."""
        return self.msg


class TrestleNotFoundError(TrestleError):
    """
    General framwork related not found error.

    Args:
        msg (str): The error message
    """

    def __init__(self, msg: str):
        """Intialization for TresleNotFoundError."""
        super().__init__(msg)


class TrestleValidationError(TrestleError):
    """
    General framwork related validation error.

    Args:
        msg (str): The error message
    """

    def __init__(self, msg: str):
        """Intialization for TresleValidationError."""
        super().__init__(msg)
