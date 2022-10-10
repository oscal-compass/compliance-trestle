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
    """Test is_ordered_sublist method."""
    assert list_utils.is_ordered_sublist(['a', 'b', 'c'], ['x', 'a', 'b', 'c', 'y', 'z']) is True
    assert list_utils.is_ordered_sublist(['a', 'b', 'c'], ['x', 'a', 'c', 'b', 'y', 'z']) is False
    assert list_utils.is_ordered_sublist(['a', 'b', 'c'], ['x', 'a', 'b', 'y', 'c', 'z']) is False


def test_join_key_to_list_dicts() -> None:
    """Test join_key_to_list_dicts method."""
    d1 = {'a': [1, 2], 'b': [3, 4], 'c': [5], 'd': [8, 9]}
    d2 = {'a': [2, 1], 'b': [3], 'c': [6, 7], 'e': [0]}
    d3 = {'a': [1, 2, 2, 1], 'b': [3, 4, 3], 'c': [5, 6, 7], 'd': [8, 9], 'e': [0]}
    d4 = list_utils.join_key_to_list_dicts(d1, d2)
    assert d4 == d3
    assert d4 != d1
    d1 = {1: [1, 2], 2: [3, 4], '3': [5], 'd': [8, 9]}
    d2 = {1: [2, 1], 2: [3], '3': [6, 7], 'e': [0]}
    d3 = {1: [1, 2, 2, 1], 2: [3, 4, 3], '3': [5, 6, 7], 'd': [8, 9], 'e': [0]}
    d4 = list_utils.join_key_to_list_dicts(d1, d2)
    assert d4 == d3
    assert d4 != d1


def test_merge_dicts() -> None:
    """Test merge dicts."""
    src = {'a': 5, 'b': 8, 'c': 9}
    dest = {'a': 7, 'c': 4, 'e': 1}
    merged = list_utils.merge_dicts(dest, src)
    assert merged == {'a': 5, 'b': 8, 'c': 9, 'e': 1}
    assert list_utils.merge_dicts(dest, None) == dest
    assert list_utils.merge_dicts(None, None) == {}
    assert list_utils.merge_dicts(None, src) == src
    assert list_utils.merge_dicts({}, {}) == {}


def test_pop_item_from_list() -> None:
    """Test pop item from list."""
    items = [1, 3, 5, 7]
    item = list_utils.pop_item_from_list(items, 5, lambda x: x)
    assert item == 5
    assert items == [1, 3, 7]
    items = []
    assert list_utils.pop_item_from_list(items, 5, lambda x: x) is None
    assert items == []
    assert list_utils.pop_item_from_list(None, None, None) is None
    items = [{'a': 2}, {'b': 4}, {'c': 6}]
    item = list_utils.pop_item_from_list(items, 4, lambda x: list(x.values())[0])
    assert item == {'b': 4}
    assert items == [{'a': 2}, {'c': 6}]


def test_get_item_from_list() -> None:
    """Test get item from list."""
    items = [1, 3, 5, 7]
    item = list_utils.get_item_from_list(items, 5, lambda x: x)
    assert item == 5
    assert items == [1, 3, 5, 7]
    items = []
    assert list_utils.get_item_from_list(items, 5, lambda x: x) is None
    assert items == []
    assert list_utils.get_item_from_list(None, None, None) is None
    items = [{'a': 2}, {'b': 4}, {'c': 6}]
    item = list_utils.get_item_from_list(items, 4, lambda x: list(x.values())[0])
    assert item == {'b': 4}
    assert items == [{'a': 2}, {'b': 4}, {'c': 6}]
