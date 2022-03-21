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
from typing import Dict, List, Optional

from trestle.common.common_types import TG


def as_list(list_or_none: Optional[List[TG]]) -> List[TG]:
    """Convert list or None object to itself or an empty list if none."""
    return list_or_none if list_or_none else []


def none_if_empty(list_: List[TG]) -> Optional[List[TG]]:
    """Convert to None if empty list."""
    return list_ if list_ else None


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
