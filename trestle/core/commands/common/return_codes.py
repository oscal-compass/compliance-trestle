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
"""Trestle command return codes."""
import enum


class CmdReturnCodes(enum.Enum):
    """
    Trestle CLI return codes.

    SUCCESS - Operation/validation completed successfully
    COMMAND_ERROR - Generic expected error while executing command (handled by command)
    INCORRECT_ARGS - Provided arguments were incorrect/incomplete
    DOCUMENTS_VALIDATION_ERROR - Validation of the markdown or drawio files failed
    MODEL_VALIDATION_ERROR - Validation of OSCAL model failed
    TRESTLE_ROOT_ERROR - Trestle project setup has failed, the root is not trestle directory
    IO_ERROR - IO related errors, i.e. permission issue, non-existing file, etc
    AUTH_ERROR - Authenication error while accessing/storing cache
    UNKNOWN_ERROR - Unexpected error (unhandled by command)
    """

    SUCCESS = 0
    COMMAND_ERROR = 1
    INCORRECT_ARGS = 2
    DOCUMENTS_VALIDATION_ERROR = 3
    OSCAL_VALIDATION_ERROR = 4
    TRESTLE_ROOT_ERROR = 5
    IO_ERROR = 6
    AUTH_ERROR = 7
    UNKNOWN_ERROR = 8
