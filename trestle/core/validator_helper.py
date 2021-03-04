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

import re
import inspect

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


def find_attribs_by_regex(object_of_interest: Any, regex_of_interest: str):
    """Find attributes of object matching regex expression."""
    matches = []
    p = re.compile(regex_of_interest)
    for i in inspect.getmembers(object_of_interest):
        if i[0].startswith('_') or inspect.ismethod(i[1]):
            continue
        hits = p.findall(i[0])
        if hits:
            matches.append(i)
    return matches


def find_all_attribs_by_regex(object_of_interest: Any, regex_of_interest: str):
    """Find all attributes in object matching regex expression."""
    all_attrs = []
    if isinstance(object_of_interest, pydantic.BaseModel):
        attrs = find_attribs_by_regex(object_of_interest, regex_of_interest)
        all_attrs.extend(attrs)
        fields = getattr(object_of_interest, '__fields_set__', None)
        if fields is not None:
            for field in fields:
                all_attrs.extend(find_attribs_by_regex(getattr(object_of_interest, field, None), regex_of_interest))
    elif type(object_of_interest) is list:
        for item in object_of_interest:
            all_attrs.extend(find_attribs_by_regex(item, regex_of_interest))
    elif type(object_of_interest) is dict:
        for item in object_of_interest.values():
            all_attrs.extend(find_attribs_by_regex(item, regex_of_interest))
    return all_attrs


def has_no_duplicate_values_by_name(object_of_interest: Any, name_of_interest: str) -> bool:
    """Determine if duplicate values of type exist in object."""
    loe = find_values_by_name(object_of_interest, name_of_interest)
    return len(loe) == len(set(loe))


def regenerate_uuids_in_place(object_of_interest: Any, uuid_lut: Any = None) -> Any:
    """Update all uuids in model that require updating."""
    if uuid_lut is None:
        uuid_lut = {}
    uuid_str = 'uuid'
    if isinstance(object_of_interest, pydantic.BaseModel):
        value = getattr(object_of_interest, uuid_str, None)
        if value is not None:
            new_uuid = uuid.uuid4()
            uuid_lut[value] = new_uuid
            object_of_interest[uuid_str] = new_uuid
            return object_of_interest, uuid_lut
        fields = getattr(object_of_interest, '__fields_set__', None)
        for field in fields:
            new_object, uuid_lut = regenerate_uuids_in_place(object_of_interest[field], uuid_lut)
            object_of_interest[field] = new_object
        return object_of_interest, uuid_lut
    elif type(object_of_interest) is list:
        new_list = []
        for item in object_of_interest:
            new_item, uuid_lut = regenerate_uuids(item, uuid_lut)
            new_list.append(new_item)
        return new_list, uuid_lut
    elif type(object_of_interest) is dict:
        new_dict = {}
        for key, value in object_of_interest.items():
            if key == uuid_str:
                new_val = uuid.uuid4()
                new_dict[uuid_str] = new_val
                uuid_lut[value] = new_val
            else:
                new_value, uuid_lut = regenerate_uuid(value, uuid_lut)
                new_dict[key] = new_value
        return new_dict, uuid_lut
    return object_of_interest, uuid_lut

def update_new_uuid_refs(object_of_interest: Any, uuid_lut: Any):
    if uuid_lut is None:
        return object_of_interest
    if isinstance(object_of_interest, pydantic.BaseModel):
        for attr, value in object_of_interest.__dict__.items():
            
        fields = getattr(object_of_interest, '__fields_set__', None)
        for field in fields:
            new_object, uuid_lut = regenerate_uuids_in_place(object_of_interest[field], uuid_lut)
            object_of_interest[field] = new_object
        return object_of_interest, uuid_lut
    elif type(object_of_interest) is list:
        new_list = []
        for item in object_of_interest:
            new_item, uuid_lut = regenerate_uuids(item, uuid_lut)
            new_list.append(new_item)
        return new_list, uuid_lut
    elif type(object_of_interest) is dict:
        new_dict = {}
        for key, value in object_of_interest.items():
            if key == uuid_str:
                new_val = uuid.uuid4()
                new_dict[uuid_str] = new_val
                uuid_lut[value] = new_val
            else:
                new_value, uuid_lut = regenerate_uuid(value, uuid_lut)
                new_dict[key] = new_value
        return new_dict, uuid_lut
    return object_of_interest, uuid_lut



