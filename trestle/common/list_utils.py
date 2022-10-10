# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Trestle List Utils."""
from typing import Any, Callable, Dict, List, Optional

from trestle.common.common_types import TG, TG2


def as_list(list_or_none: Optional[List[TG]]) -> List[TG]:
    """Convert list or None object to itself or an empty list if none."""
    return list_or_none if list_or_none else []


def as_filtered_list(list_or_none: Optional[List[TG]], filter_condition: Callable[[TG], bool]) -> List[TG]:
    """Convert to list and filter based on the condition."""
    result_list = as_list(list_or_none)
    result_list = list(filter(filter_condition, result_list))
    return result_list


def as_dict(dict_or_none: Optional[Dict[TG, TG2]]) -> Dict[TG, TG2]:
    """Convert dict or None object to itself or an empty dict if none."""
    return dict_or_none if dict_or_none else {}


def none_if_empty(list_: List[TG]) -> Optional[List[TG]]:
    """Convert to None if empty list."""
    return list_ if list_ else None


def get_default(item: TG, default: TG) -> TG:
    """Return the default value for the item if it is not set."""
    return item if item else default


def is_ordered_sublist(needle: List[str], haystack: List[str]) -> bool:
    """Determine if needle is exactly contained in haystack.

    The needle list comprises an ordered list of strings.
    The haystack list comprises an ordered list of strings that is to be searched.
    If the strings in the needle appear in the haystack in that exact order then
    return true, else false.

    Examples:
    needle=['a','b','c'], haystack=['x','y','a','b','c','z'], result = True
    needle=['a','b','c'], haystack=['x','y','a','b','z','c'], result = False
    """
    return ' '.join(needle) in ' '.join(haystack)


def join_key_to_list_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Join two dicts of str to List."""
    # merge like keys
    dict3 = {key: dict1[key] + dict2.get(key, []) for key in dict1}
    # merge unlike keys
    dict3.update({key: dict2[key] for key in dict2 if key not in dict3})
    return dict3


def delete_item_from_list(item_list: List[Any], value: Any, key: Callable[[Any], Any]) -> List[Any]:
    """Remove an item if it is present in a list based on the key."""
    keys = [key(item) for item in item_list]
    if value in keys:
        index = keys.index(value)
        del item_list[index]
    return item_list


def pop_item_from_list(item_list: Optional[List[Any]], value: Any, key: Callable[[Any], Any]) -> List[Any]:
    """Pop an item from a list if it is present based on the key."""
    if not item_list:
        return None
    keys = [key(item) for item in item_list]
    item = None
    if value in keys:
        index = keys.index(value)
        item = item_list[index]
        del item_list[index]
    return item


def get_item_from_list(item_list: Optional[List[Any]], value: Any, key: Callable[[Any], Any]) -> Any:
    """Get item from list if present."""
    if not item_list:
        return None
    keys = [key(item) for item in item_list]
    item = None
    if value in keys:
        index = keys.index(value)
        item = item_list[index]
    return item


def delete_list_from_list(item_list: List[Any], indices: List[int]) -> None:
    """Delete a list of items from a list based on indices."""
    for index in sorted(indices, reverse=True):
        del item_list[index]


def merge_dicts(dest: Optional[Dict[str, str]], src: Optional[Dict[str, str]]) -> Dict[str, str]:
    """Merge the two dicts with priority to src."""
    return {**as_dict(dest), **as_dict(src)}
