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
import base64
import inspect
import logging
import math
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Type, TypeVar, Union, cast, get_args, get_origin

from pydantic import Field, StringConstraints
from pydantic.networks import AnyUrl as PydanticAnyUrl, EmailStr as PydanticEmailStr

import trestle.common.const as const
import trestle.common.err as err
import trestle.common.type_utils as utils
from trestle.common import str_utils
from trestle.common.str_utils import AliasMode
from trestle.core.base_model import OscalBaseModel
from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Base64
from trestle.oscal.common import Base64Datatype
from trestle.oscal.common import Methods
from trestle.oscal.common import ObservationTypeValidValues
from trestle.oscal.common import OscalVersion
from trestle.oscal.common import TaskValidValues
from trestle.oscal.ssp import DateDatatype

from typing_extensions import Annotated

logger = logging.getLogger(__name__)

TG = TypeVar('TG', bound=OscalBaseModel)

# Create a valid base64 encoded string for the sample
sample_base64_str = base64.b64encode(b'sample').decode('ascii')

# Sample values for different types
SAMPLE_VALUES = {
    Base64: Base64(filename=const.REPLACE_ME, media_type='text/plain', value=sample_base64_str),
    datetime: lambda: datetime.now().astimezone(),
    bool: False,
    int: 0,
    float: 0.00,
    str: const.REPLACE_ME,
    PydanticEmailStr: 'dummy@sample.com',  # Just a string for EmailStr
    PydanticAnyUrl: 'https://sample.com/replaceme.html',  # Just a string for AnyUrl
}

# Enum type mappings
ENUM_MAPPINGS = {
    Methods: Methods.EXAMINE,
    TaskValidValues: TaskValidValues.milestone,
    ObservationTypeValidValues: ObservationTypeValidValues.historic,
}

# Field-specific overrides
FIELD_OVERRIDES = {
    'oscal_version': OSCAL_VERSION,
    'date_authorized': lambda: str(date.today().isoformat()),
}


class TypeHandler:
    """Centralized type handling for sample generation."""

    @staticmethod
    def is_enum_type(type_: type) -> bool:
        """Check if type is one of the known enums in a Union."""
        origin = get_origin(type_)
        if origin != Union:
            return False

        for arg in get_args(type_):
            # Check if arg is an enum type
            if inspect.isclass(arg) and issubclass(arg, Enum):
                return True
        return False

    @staticmethod
    def get_enum_value(type_: type) -> Enum:
        """Get sample value for enum type."""
        for arg in get_args(type_):
            if inspect.isclass(arg) and issubclass(arg, Enum):
                # Get the first enum value
                return list(arg.__members__.values())[0]

        # Check if it's a direct enum type
        if inspect.isclass(type_) and issubclass(type_, Enum):
            return list(type_.__members__.values())[0]

        raise ValueError(f'No enum value found for type: {type_}')

    @staticmethod
    def is_special_oscal_type(type_: type) -> bool:
        """Check if type is a special OSCAL type that needs custom handling."""
        special_types = {
            Base64,
            Base64Datatype,
            DateDatatype,
            OscalVersion,
        }
        return type_ in special_types

    @staticmethod
    def handle_special_type(type_: type, field_name: str) -> Any:
        """Handle special OSCAL types."""
        if type_ == Base64:
            return SAMPLE_VALUES[Base64]
        elif type_ == Base64Datatype:
            return sample_base64_str
        elif type_ == DateDatatype:
            return '2400-02-29'
        elif type_ == OscalVersion:
            return OSCAL_VERSION
        return None

    @staticmethod
    def is_string_constraint_type(type_: type) -> bool:
        """Check if type is a StringConstraints type."""
        origin = get_origin(type_)
        if origin is Annotated:
            args = get_args(type_)
            if len(args) > 1:
                # Check if any of the args are StringConstraints
                for arg in args[1:]:
                    if isinstance(arg, StringConstraints):
                        return True
        return False

    @staticmethod
    def get_string_constraints(type_: type) -> StringConstraints:
        """Get StringConstraints from Annotated type."""
        args = get_args(type_)
        for arg in args[1:]:
            if isinstance(arg, StringConstraints):
                return arg
        return None

    @staticmethod
    def is_pydantic_special_type(type_: type) -> bool:
        """Check if type is a Pydantic special type like EmailStr, AnyUrl."""
        return type_ in [PydanticEmailStr, PydanticAnyUrl]


class ConstrainedTypeHandler:
    """Handler for constrained types."""

    @staticmethod
    def handle_string_constraint(type_: type, field_name: str) -> str:
        """Generate value for StringConstraints types."""
        constraints = TypeHandler.get_string_constraints(type_)

        # Handle regex patterns
        if constraints and hasattr(constraints, 'pattern'):
            pattern = constraints.pattern
            if pattern and isinstance(pattern, str):
                if pattern.startswith('^[0-9A-Fa-f]{8}'):
                    return const.SAMPLE_UUID_STR

        # Field-specific handling
        if field_name in FIELD_OVERRIDES:
            value = FIELD_OVERRIDES[field_name]
            return value() if callable(value) else value

        if 'uuid' in field_name or field_name == 'uuid':
            return str(uuid.uuid4())

        if field_name.rstrip('s') == 'member_of_organization':
            return const.SAMPLE_UUID_STR

        return const.REPLACE_ME

    @staticmethod
    def handle_constrained_int(field_info: Field) -> int:
        """Generate value for constrained integer fields."""
        ge_value = field_info.ge
        gt_value = field_info.gt
        multiple_of = field_info.multiple_of

        multiple = multiple_of if multiple_of is not None else 1
        floor = ge_value if ge_value is not None else 0

        if gt_value is not None:
            floor = gt_value + 1

        if math.remainder(floor, multiple) == 0:
            return floor
        return (floor + 1) * multiple


def generate_sample_value_by_type(
    type_: type,
    field_name: str,
) -> Union[datetime, bool, int, str, float, Enum, Any]:
    """Given a type, return sample value."""
    # Handle NoneType
    if type_ is type(None):
        return None

    # Handle enum types in Union
    if TypeHandler.is_enum_type(type_):
        return TypeHandler.get_enum_value(type_)

    # Handle direct enum types
    if inspect.isclass(type_) and issubclass(type_, Enum):
        return list(type_.__members__.values())[0]

    # Handle special OSCAL types
    if TypeHandler.is_special_oscal_type(type_):
        result = TypeHandler.handle_special_type(type_, field_name)
        if result is not None:
            return result

    # Handle Pydantic special types
    if TypeHandler.is_pydantic_special_type(type_):
        return SAMPLE_VALUES[type_]

    # Handle string constraints
    if TypeHandler.is_string_constraint_type(type_):
        return ConstrainedTypeHandler.handle_string_constraint(type_, field_name)

    # Handle regular types
    if type_ in SAMPLE_VALUES:
        value = SAMPLE_VALUES[type_]
        return value() if callable(value) else value

    # Handle list type
    if type_ is list:
        raise err.TrestleError(f'Unable to generate sample for type {type_}')

    # Default to empty string for unknown string-like types
    if type_ is str:
        return const.REPLACE_ME

    # Default to empty dict for complex types
    return {}


def generate_sample_model(
    model: Union[Type[TG], List[TG], Dict[str, TG]], include_optional: bool = False, depth: int = -1
) -> TG:
    """Given a model class, generate an object of that class with sample values."""
    effective_optional = include_optional and not depth == 0

    # Handle collection types
    if utils.is_collection_field_type(model):
        model_type = utils.get_origin(model)
        inner_type = utils.get_inner_type(model)

        if model_type is list:
            # Generate a list with one element
            element = generate_sample_model(inner_type, include_optional=include_optional, depth=depth - 1)
            return cast(TG, [element])

        elif model_type is dict:
            # Generate a dict with one key-value pair
            key = const.REPLACE_ME
            value = generate_sample_model(inner_type, include_optional=include_optional, depth=depth - 1)
            return cast(TG, {key: value})

        else:
            raise err.TrestleError(f'Unhandled collection type: {model_type}')

    # Now handle the actual model type
    model = cast(Type[TG], model)

    # Check if this is an OscalBaseModel subclass
    if not (inspect.isclass(model) and issubclass(model, OscalBaseModel)):
        # For non-model types, generate a sample value
        return generate_sample_value_by_type(model, '')

    model_dict = {}

    # Use model_fields for Pydantic v2
    if hasattr(model, 'model_fields'):
        for field_name, field_info in model.model_fields.items():
            # Handle special model types
            if model is OscalVersion:
                model_dict[field_name] = OSCAL_VERSION
                break

            if field_name == 'include_all':
                if include_optional:
                    model_dict[field_name] = {}
                continue

            # Get field type annotation
            field_type = field_info.annotation

            # Skip if annotation is missing
            if field_type is None:
                continue

            # Handle Optional types (Union with None)
            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                # Find the non-None type
                non_none_args = [arg for arg in args if arg is not type(None)]
                if non_none_args:
                    field_type = non_none_args[0]
                else:
                    # All args are None, skip this field
                    continue

            # Check if field should be included
            # In Pydantic v2, we check if field has a default value
            field_has_default = field_info.default is not None or field_info.default_factory is not None

            if not field_has_default and not effective_optional:
                # Field is required, include it
                pass
            elif field_has_default and not effective_optional:
                # Field has default and we're not including optional, skip it
                continue

            # Handle collection types
            if utils.is_collection_field_type(field_type):
                model_dict[field_name] = generate_sample_model(
                    field_type, include_optional=include_optional, depth=depth - 1
                )

            # Handle OscalBaseModel subclasses
            elif inspect.isclass(field_type) and issubclass(field_type, OscalBaseModel):
                # Check for recursion
                if field_type == model:
                    continue
                model_dict[field_name] = generate_sample_model(
                    field_type, include_optional=include_optional, depth=depth - 1
                )

            # Handle special OSCAL types
            elif TypeHandler.is_special_oscal_type(field_type):
                result = TypeHandler.handle_special_type(field_type, field_name)
                if result is not None:
                    model_dict[field_name] = result
                else:
                    model_dict[field_name] = generate_sample_value_by_type(field_type, field_name)

            # Handle Pydantic special types
            elif TypeHandler.is_pydantic_special_type(field_type):
                model_dict[field_name] = SAMPLE_VALUES[field_type]

            # Handle root models
            elif field_name == '__root__':
                model_dict[field_name] = generate_sample_value_by_type(
                    field_type, str_utils.classname_to_alias(model.__name__, AliasMode.FIELD)
                )

            else:
                # Handle constrained integer fields
                if field_type is int and (field_info.ge is not None or field_info.gt is not None
                                          or field_info.multiple_of is not None):
                    model_dict[field_name] = ConstrainedTypeHandler.handle_constrained_int(field_info)
                else:
                    model_dict[field_name] = generate_sample_value_by_type(field_type, field_name)

    else:
        # Fallback for non-Pydantic models
        raise err.TrestleError(f'Model {model} does not have model_fields attribute')

    # Create and return the model instance
    try:
        return model(**model_dict)
    except Exception as e:
        raise err.TrestleError(f'Failed to create model {model}: {e}')


# Legacy function for backward compatibility
def safe_is_sub(sub: Any, parent: Any) -> bool:
    """Is this a subclass of parent."""
    is_class = inspect.isclass(sub)
    return is_class and issubclass(sub, parent)


# Legacy functions for backward compatibility
def is_enum_method(type_: type) -> bool:
    """Test for method."""
    if get_origin(type_) == Union:
        args = get_args(type_)
        for arg in args:
            if arg == Methods:
                return True
    return False


def is_enum_task_valid_value(type_: type) -> bool:
    """Test for task valid value."""
    if get_origin(type_) == Union:
        args = get_args(type_)
        for arg in args:
            if arg == TaskValidValues:
                return True
    return False


def is_enum_observation_type_valid_value(type_: type) -> bool:
    """Test for observation type valid value."""
    if get_origin(type_) == Union:
        args = get_args(type_)
        for arg in args:
            if arg == ObservationTypeValidValues:
                return True
    return False


def is_by_type(model_type: Union[Type[TG], List[TG], Dict[str, TG]]) -> bool:
    """Check for by type."""
    return model_type == Base64
