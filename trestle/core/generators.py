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
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Type, Union

import pydantic.networks
from pydantic import BaseModel
from pydantic import ConstrainedStr

import trestle.core.err as err
import trestle.core.utils as utils
import trestle.oscal.ssp
import trestle.utils.log as log
from trestle.core.base_model import OscalBaseModel

logger = log.get_logger()


def generate_sample_value_by_type(
    type_: type,
    field_name: str,
    parent_model: Optional[Type[OscalBaseModel]] = None
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
        return 'REPLACE_ME'
    elif type_ is float:
        return 0.00
    elif issubclass(type_, ConstrainedStr) or 'ConstrainedStr' in str(type):
        # This code here is messy. we need to meet a set of constraints. If we do
        # not do so it fails to generate.
        if 'uuid' == field_name:
            return str(uuid.uuid4())
        elif parent_model == trestle.oscal.ssp.DateAuthorized:
            return date.today().isoformat()
        return '00000000-0000-4000-8000-000000000000'
    elif issubclass(type_, Enum):
        # keys and values diverge due to hypens in oscal names
        return type_(list(type_.__members__.values())[0])
    elif type_ is pydantic.networks.EmailStr:
        return pydantic.networks.EmailStr('dummy@sample.com')
    elif type_ is pydantic.networks.AnyUrl:
        # TODO: Cleanup: this should be usable from a url.. but it's not inuitive.
        return pydantic.networks.AnyUrl('https://sample.com/replaceme.html', scheme='http', host='sample.com')
    else:
        raise err.TrestleError('Fatal: Bad type in model')


def generate_sample_model(model: Type[Any]) -> OscalBaseModel:
    """Given a model class, generate an object of that class with sample values."""
    # FIXME: Should be in separate generator module as it inherits EVERYTHING
    model_type = model
    if utils.is_collection_field_type(model):
        model_type = model.__origin__
        model = utils.get_inner_type(model)
    else:
        model = model

    model_dict = {}

    for field in model.__fields__:
        try:

            outer_type = model.__fields__[field].outer_type_
            # Check for unions. This is awkward due to allow support for python 3.7
            # It also does not inspect for which union we want. Should be removable with oscal 1.0.0
            if getattr(outer_type, '__origin__', None) == Union:
                outer_type = outer_type.__args__[0]
            if model.__fields__[field].required:
                """ FIXME: This type_ could be a List or a Dict """
                if utils.is_collection_field_type(outer_type) or issubclass(outer_type, BaseModel):
                    model_dict[field] = generate_sample_model(outer_type)
                else:
                    model_dict[field] = generate_sample_value_by_type(outer_type, field, model)
        except Exception as e:
            raise err.TrestleError(f'Hit error of type {e} where outer_type_ is: {outer_type} for field {field}')
    if model_type is list:
        return [model(**model_dict)]
    elif model_type is dict:
        return {'REPLACE_ME': model(**model_dict)}
    return model(**model_dict)
