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

from typing import Any, List, Type, TypeVar

import pydantic

# Generic type var
TG = TypeVar('TG')


# TODO: Improve typing - this could potentially be done through type vars
def find_values_by_name_generic(object_of_interest: Any, var_name: str) -> List[str]:
    """Traverse object and return list of the values in dicts, tuples associated with variable name."""
    loe = []
    # looking for a dict or 2-element tuple containing specified variable name
    if type(object_of_interest) == dict:
        for key, value in object_of_interest.items():
            if (key == var_name) and value:
                # found one so append its value to list
                loe.append(value)
            else:
                new_list = find_values_by_name_generic(value, var_name)
                if new_list:
                    loe.extend(new_list)
    elif type(object_of_interest) == tuple and len(object_of_interest) == 2 and object_of_interest[0] == var_name:
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
                new_list = find_values_by_name_generic(next_item, var_name)
                if new_list:
                    loe.extend(new_list)
                next_item = next(o_iter, None)
            return loe
    return loe


def has_no_duplicate_values_generic(object_of_interest: Any, var_name: str) -> bool:
    """Determine if duplicate values of variable exist in object."""
    loe = find_values_by_name_generic(object_of_interest, var_name)
    return len(loe) == len(set(loe))


def find_values_by_type(object_of_interest: Any, type_of_interest: Type[TG]) -> List[TG]:
    """Traverse object and return list of values of specified type."""
    loe = []
    # looking for a dict or 2-element tuple containing specified variable name
    if type(object_of_interest) == type_of_interest:
        loe.append(object_of_interest)
        return loe
    if type(object_of_interest) == dict:
        for value in object_of_interest.values():
            new_list = find_values_by_type(value, type_of_interest)
            if new_list:
                loe.extend(new_list)
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
                new_list = find_values_by_type(next_item, type_of_interest)
                if new_list:
                    loe.extend(new_list)
                next_item = next(o_iter, None)
            return loe
    return loe


def has_no_duplicate_values_by_type(object_of_interest: Any, type_of_interest: Type[TG]) -> bool:
    """Determine if duplicate values of type exist in object."""
    loe = find_values_by_type(object_of_interest, type_of_interest)
    n = len(loe)
    if n > 1:
        for i in range(n - 1):
            for j in range(i + 1, n):
                if loe[i] == loe[j]:
                    return False
    return True


def find_values_by_name(object_of_interest: Any, name_of_interest: str) -> List[Any]:
    """Traverse object and return list of values of specified name."""
    loe = []
    if isinstance(object_of_interest, pydantic.BaseModel):
        value = getattr(object_of_interest, name_of_interest, None)
        if value is not None:
            loe.append(value)
        fields = getattr(object_of_interest, '__fields_set__', None)
        if fields is not None:
            for field in fields:
                loe.extend(find_values_by_name(getattr(object_of_interest, field, None), name_of_interest))
    elif type(object_of_interest) is list:
        for item in object_of_interest:
            loe.extend(find_values_by_name(item, name_of_interest))
    elif type(object_of_interest) is dict:
        for item in object_of_interest.values():
            loe.extend(find_values_by_name(item, name_of_interest))
    return loe


def has_no_duplicate_values_by_name(object_of_interest: Any, name_of_interest: str) -> bool:
    """Determine if duplicate values of type exist in object."""
    loe = find_values_by_name(object_of_interest, name_of_interest)
    return len(loe) == len(set(loe))
