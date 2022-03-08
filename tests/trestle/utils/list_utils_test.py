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
"""Tests for list_utils module."""

from trestle.common import list_utils


def test_is_ordered_sublist() -> None:
    """Test should_ignore method."""
    assert list_utils.is_ordered_sublist(['a', 'b', 'c'], ['x', 'a', 'b', 'c', 'y', 'z']) is True
    assert list_utils.is_ordered_sublist(['a', 'b', 'c'], ['x', 'a', 'c', 'b', 'y', 'z']) is False
    assert list_utils.is_ordered_sublist(['a', 'b', 'c'], ['x', 'a', 'b', 'y', 'c', 'z']) is False
