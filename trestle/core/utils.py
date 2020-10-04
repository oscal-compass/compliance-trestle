# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for dealing with models."""

from typing import List

import pydantic

import trestle.core.err as err


def get_elements_of_model_type(object_of_interest, type_of_interest):
    """
    Return a flat list of a given type of pydantic object based on a presumed encompasing root object.

    One warning. This object preserves the underlying object tree. So when you use this function do NOT recurse on the
    results or you will end up with duplication errors.
    """
    loi = []
    if type(object_of_interest) == type_of_interest:
        loi.append(object_of_interest)
        # keep going
    if type(object_of_interest) is list:
        for item in object_of_interest:
            loi.extend(get_elements_of_model_type(item, type_of_interest))

    if isinstance(object_of_interest, pydantic.BaseModel):
        for field in object_of_interest.__fields_set__:
            if field == '__root__':
                continue
            loi.extend(get_elements_of_model_type(getattr(object_of_interest, field), type_of_interest))
    return loi


def find_elements_by_name(object_of_interest, key_name):
    """Traverse entire object and return list of the values in dicts associated with key name."""
    loe = []
    # looking for a dict or 2-element tuple containing specified key name
    if type(object_of_interest) == dict:
        for key, value in object_of_interest.items():
            if (key == key_name) and value:
                # found one so append its value to list
                loe.append(value)
            else:
                new_list = find_elements_by_name(value, key_name)
                if new_list:
                    loe.extend(new_list)
    elif type(object_of_interest) == tuple and len(object_of_interest) == 2 and object_of_interest[0] == key_name:
        if object_of_interest[1]:
            loe.append(object_of_interest[1])
    elif type(object_of_interest) != str:
        try:
            # iterate over any iterable and recurse on its items
            o_iter = iter(object_of_interest)
        except Exception:
            # it is not a dict and not iterable
            pass
        else:
            next_item = next(o_iter, None)
            while next_item is not None:
                new_list = find_elements_by_name(next_item, key_name)
                if new_list:
                    loe.extend(new_list)
                next_item = next(o_iter, None)
            return loe
    return loe


def has_no_duplicate_elements(object_of_interest, element_name):
    """Determine if duplicate instances of element exist in object."""
    loe = find_elements_by_name(object_of_interest, element_name)
    return len(loe) == len(set(loe))

    
def class_to_oscal(class_name: str, mode: str) -> str:
    """
    Return oscal json or field element name based on class name.

    This is applicable when asking for a singular element.
    """
    parts = pascal_case_split(class_name)
    if mode == 'json':
        return '-'.join(map(str.lower, parts))
    elif mode == 'field':
        return '_'.join(map(str.lower, parts))
    else:
        raise err.TrestleError('Bad option')


def pascal_case_split(pascal_str: str) -> List[str]:
    """Parse a pascal case string (e.g. a ClassName) and return a list of strings."""
    start_idx = [i for i, e in enumerate(pascal_str) if e.isupper()] + [len(pascal_str)]
    return [pascal_str[x:y] for x, y in zip(start_idx, start_idx[1:])]
