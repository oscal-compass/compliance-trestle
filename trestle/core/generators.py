# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Capabilities to allow the generation of various oscal objects."""
import inspect
import logging
import math
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import pydantic.networks
from pydantic import ConstrainedStr

import trestle.core.const as const
import trestle.core.err as err
import trestle.core.utils as utils
from trestle.core.base_model import OscalBaseModel
from trestle.oscal import OSCAL_VERSION

logger = logging.getLogger(__name__)

TG = TypeVar('TG', bound=OscalBaseModel)


def safe_is_sub(sub: Any, parent: Any) -> bool:
    """Is this a subclass of parent."""
    is_class = inspect.isclass(sub)
    return is_class and issubclass(sub, parent)


def generate_sample_value_by_type(
    type_: type,
    field_name: str,
) -> Union[datetime, bool, int, str, float, Enum]:
    """Given a type, return sample value.

    Includes the Optional use of passing down a parent_model
    """
    # FIXME: Should be in separate generator module as it inherits EVERYTHING
    if type_ is datetime:
        return datetime.now().astimezone()
    if type_ is bool:
        return False
    if type_ is int:
        return 0
    if type_ is str:
        if field_name == 'oscal_version':
            return OSCAL_VERSION
        return 'REPLACE_ME'
    if type_ is float:
        return 0.00
    if safe_is_sub(type_, ConstrainedStr) or (hasattr(type_, '__name__') and 'ConstrainedStr' in type_.__name__):
        # This code here is messy. we need to meet a set of constraints. If we do
        # TODO: handle regex directly
        if 'uuid' == field_name:
            return str(uuid.uuid4())
        if field_name == 'date_authorized':
            return str(date.today().isoformat())
        if field_name == 'oscal_version':
            return OSCAL_VERSION
        if 'uuid' in field_name:
            return const.SAMPLE_UUID_STR
        # Only case where are UUID is required but not in name.
        if field_name.rstrip('s') == 'member_of_organization':
            return const.SAMPLE_UUID_STR
        return 'REPLACE_ME'
    if hasattr(type_, '__name__') and 'ConstrainedIntValue' in type_.__name__:
        # create an int value as close to the floor as possible does not test upper bound
        multiple = type_.multiple_of if type_.multiple_of else 1  # default to every integer
        # this command is a bit of a problem
        floor = type_.ge if type_.ge else 0
        floor = type_.gt + 1 if type_.gt else floor
        if math.remainder(floor, multiple) == 0:
            return floor
        return (floor + 1) * multiple
    if safe_is_sub(type_, Enum):
        # keys and values diverge due to hypens in oscal names
        return type_(list(type_.__members__.values())[0])
    if type_ is pydantic.networks.EmailStr:
        return pydantic.networks.EmailStr('dummy@sample.com')
    if type_ is pydantic.networks.AnyUrl:
        # TODO: Cleanup: this should be usable from a url.. but it's not inuitive.
        return pydantic.networks.AnyUrl('https://sample.com/replaceme.html', scheme='http', host='sample.com')
    if type_ == Any:
        # Return empty dict - aka users can put whatever they want here.
        return {}
    raise err.TrestleError(f'Fatal: Bad type in model {type_}')


def generate_sample_model(
    model: Union[Type[TG], List[TG], Dict[str, TG]], include_optional: bool = False, depth: int = -1
) -> TG:
    """Given a model class, generate an object of that class with sample values.

    Can generate optional variables with an enabled flag. Any array objects will have a single entry injected into it.

    Note: Trestle generate will not activate recursive loops irrespective of the depth flag.

    Args:
        model: The model type provided. Typically for a user as an OscalBaseModel Subclass.
        include_optional: Whether or not to generate optional fields.
        depth: Depth of the tree at which optional fields are generated. Negative values (default) removes the limit.

    Returns:
        The generated instance with a pro-forma values filled out as best as possible.
    """
    effective_optional = include_optional and not depth == 0

    model_type = model
    # This block normalizes model type down to
    if utils.is_collection_field_type(model):  # type: ignore
        model_type = utils.get_origin(model)  # type: ignore
        model = utils.get_inner_type(model)  # type: ignore
    model = cast(TG, model)

    model_dict = {}
    # this block is needed to avoid situations where an inbuilt is inside a list / dict.
    if safe_is_sub(model, OscalBaseModel):
        for field in model.__fields__:
            outer_type = model.__fields__[field].outer_type_
            # Check for unions. This is awkward due to allow support for python 3.7
            # It also does not inspect for which union we want. Should be removable with oscal 1.0.0
            if utils.get_origin(outer_type) == Union:
                outer_type = outer_type.__args__[0]
            if model.__fields__[field].required or effective_optional:
                """ FIXME: This type_ could be a List or a Dict """
                # FIXME could be ForwardRef('SystemComponentStatus')
                if utils.is_collection_field_type(outer_type):
                    inner_type = utils.get_inner_type(outer_type)
                    if inner_type == model:
                        continue
                    model_dict[field] = generate_sample_model(
                        outer_type, include_optional=include_optional, depth=depth - 1
                    )
                elif safe_is_sub(outer_type, OscalBaseModel):
                    model_dict[field] = generate_sample_model(
                        outer_type, include_optional=include_optional, depth=depth - 1
                    )
                else:
                    # Hacking here:
                    # Root models should ideally not exist, however, sometimes we are stuck with them.
                    # If that is the case we need sufficient information on the type in order to generate a model.
                    # E.g. we need the type of the container.
                    if field == '__root__' and hasattr(model, '__name__'):
                        model_dict[field] = generate_sample_value_by_type(
                            outer_type, utils.classname_to_alias(model.__name__, 'field')
                        )
                    else:
                        model_dict[field] = generate_sample_value_by_type(outer_type, field)
        # Note: this assumes list constrains in oscal are always 1 as a minimum size. if two this may still fail.
    else:
        # There is set of circumstances where a m
        if model_type is list:
            return [generate_sample_value_by_type(model, '')]
        if model_type is dict:
            return {'REPLACE_ME': generate_sample_value_by_type(model, '')}
        raise err.TrestleError('Unhandled collection type.')
    if model_type is list:
        return [model(**model_dict)]
    if model_type is dict:
        return {'REPLACE_ME': model(**model_dict)}
    return model(**model_dict)
