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
"""Capabilities to allow the generation of various oscal objects."""
import logging
import math
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Type, TypeVar, Union, cast

import pydantic.networks
from pydantic import ConstrainedStr

import trestle.core.err as err
import trestle.core.utils as utils
from trestle.core.base_model import OscalBaseModel
from trestle.oscal import OSCAL_VERSION

logger = logging.getLogger(__name__)

TG = TypeVar('TG', bound=OscalBaseModel)


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
    elif type_ is bool:
        return False
    elif type_ is int:
        return 0
    elif type_ is str:
        if field_name == 'oscal_version':
            return OSCAL_VERSION
        return 'REPLACE_ME'
    elif type_ is float:
        return 0.00
    elif issubclass(type_, ConstrainedStr) or 'ConstrainedStr' in type_.__name__:
        # This code here is messy. we need to meet a set of constraints. If we do
        # TODO: handle regex directly
        if 'uuid' == field_name:
            return str(uuid.uuid4())
        elif field_name == 'date_authorized':
            return str(date.today().isoformat())
        elif field_name == 'oscal_version':
            return OSCAL_VERSION
        return '00000000-0000-4000-8000-000000000000'
    elif 'ConstrainedIntValue' in type_.__name__:
        # create an int value as close to the floor as possible does not test upper bound
        multiple = type_.multiple_of or 1  # default to every integer
        floor = type_.ge or type_.gt + 1 or 0  # default to 0
        if math.remainder(floor, multiple) == 0:
            return floor
        else:
            return (floor + 1) * multiple
    elif issubclass(type_, Enum):
        # keys and values diverge due to hypens in oscal names
        return type_(list(type_.__members__.values())[0])
    elif type_ is pydantic.networks.EmailStr:
        return pydantic.networks.EmailStr('dummy@sample.com')
    elif type_ is pydantic.networks.AnyUrl:
        # TODO: Cleanup: this should be usable from a url.. but it's not inuitive.
        return pydantic.networks.AnyUrl('https://sample.com/replaceme.html', scheme='http', host='sample.com')
    else:
        raise err.TrestleError(f'Fatal: Bad type in model {type_}')


def generate_sample_model(model: Union[Type[TG], List[TG], Dict[str, TG]]) -> TG:
    """Given a model class, generate an object of that class with sample values."""
    # FIXME: Typing is wrong.
    # TODO: The typing here is very generic - which may cause some pain. It may be more appropriate to create a wrapper
    # Function for the to level execution. This would imply restructuring some other parts of the code.

    model_type = model
    # This block normalizes model type down to
    if utils.is_collection_field_type(model):  # type: ignore
        model_type = utils.get_origin(model)  # type: ignore
        model = utils.get_inner_type(model)  # type: ignore
    model = cast(TG, model)  # type: ignore

    model_dict = {}
    # this block is needed to avoid situations where an inbuilt is inside a list / dict.
    if issubclass(model, OscalBaseModel):
        for field in model.__fields__:
            outer_type = model.__fields__[field].outer_type_
            # Check for unions. This is awkward due to allow support for python 3.7
            # It also does not inspect for which union we want. Should be removable with oscal 1.0.0
            if utils.get_origin(outer_type) == Union:
                outer_type = outer_type.__args__[0]
            if model.__fields__[field].required:
                """ FIXME: This type_ could be a List or a Dict """
                if utils.is_collection_field_type(outer_type) or issubclass(outer_type, OscalBaseModel):
                    model_dict[field] = generate_sample_model(outer_type)
                else:
                    # Hacking here:
                    # Root models should ideally not exist, however, sometimes we are stuck with them.
                    # If that is the case we need sufficient information on the type in order to generate a model.
                    # E.g. we need the type of the container.
                    if field == '__root__':
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
        elif model_type is dict:
            return {'REPLACE_ME': generate_sample_value_by_type(model, '')}
        err.TrestleError('Unhandled collection type.')
    if model_type is list:
        return [model(**model_dict)]
    elif model_type is dict:
        return {'REPLACE_ME': model(**model_dict)}
    return model(**model_dict)
