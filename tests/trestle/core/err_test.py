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
"""Tests for exceptions module."""

from trestle.core.err import TrestleError, TrestleNotFoundError, TrestleValidationError


def test_trestle_error() -> None:
    """Test trestle error."""
    msg = 'Custom error'
    try:
        raise TrestleError(msg)
    except TrestleError as err:
        assert err.msg == msg


def test_trestle_not_found_error() -> None:
    """Test trestle not found error."""
    msg = 'Custom not found error'
    try:
        raise TrestleNotFoundError(msg)
    except TrestleNotFoundError as err:
        assert str(err) == msg
        assert err.msg == msg


def test_trestle_validation_error() -> None:
    """Test trestle not found error."""
    msg = 'Custom validation error'
    try:
        raise TrestleValidationError(msg)
    except TrestleValidationError as err:
        assert str(err) == msg
        assert err.msg == msg
