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
import typing
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Annotated, Any, Dict, ForwardRef, List, Type, TypeVar, Union, cast, get_args, get_origin

from pydantic import EmailStr, AnyUrl, AwareDatetime, RootModel
from pydantic_core import PydanticUndefined

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
from trestle.oscal.common import TaskValidValues
from trestle.oscal.ssp import DateDatatype, DateAuthorized

logger = logging.getLogger(__name__)

TG = TypeVar('TG', bound=OscalBaseModel)

sample_base64_value = '00000000'
sample_base64 = Base64(filename=const.REPLACE_ME, **{'media-type': const.REPLACE_ME}, value=sample_base64_value)
type_base64 = type(sample_base64)

sample_date_value = '2400-02-29'

sample_task_valid_value = TaskValidValues.milestone
sample_method = Methods.EXAMINE

sample_observation_type_valid_value = ObservationTypeValidValues.historic


def safe_is_sub(sub: Any, parent: Any) -> bool:
    """Is this a subclass of parent."""
    # Handle Python 3.10+ generic types (e.g., dict[str, Any])
    # These are types.GenericAlias and cannot be used with issubclass()
    if hasattr(sub, '__origin__'):
        # For generic types like dict[str, Any], check the origin (dict)
        sub = typing.get_origin(sub)
    is_class = inspect.isclass(sub)
    return is_class and issubclass(sub, parent)


def is_enum_method(type_: type) -> bool:
    """Test for method."""
    rval = False
    if utils.get_origin(type_) == Union:
        args = typing.get_args(type_)
        for arg in args:
            if "<enum 'Methods'>" == f'{arg}':
                rval = True
                break
    return rval


def is_enum_task_valid_value(type_: type) -> bool:
    """Test for task valid value."""
    rval = False
    if utils.get_origin(type_) == Union:
        args = typing.get_args(type_)
        for arg in args:
            if "<enum 'TaskValidValues'>" == f'{arg}':
                rval = True
                break
    return rval


def is_enum_observation_type_valid_value(type_: type) -> bool:
    """Test for observation type valid value."""
    rval = False
    if utils.get_origin(type_) == Union:
        args = typing.get_args(type_)
        for arg in args:
            if "<enum 'ObservationTypeValidValues'>" == f'{arg}':
                rval = True
                break
    return rval


def _handle_enum_types(type_: Any) -> Union[Methods, TaskValidValues, ObservationTypeValidValues, None]:
    """Check and return sample value for enum types."""
    if is_enum_method(type_):
        return sample_method
    if is_enum_task_valid_value(type_):
        return sample_task_valid_value
    if is_enum_observation_type_valid_value(type_):
        return sample_observation_type_valid_value
    return None


def _handle_simple_types(type_: Any) -> Base64 | datetime | bool | None:
    """Check and return sample value for simple types."""
    if type_ is Base64:
        return sample_base64
    if type_ is datetime or type_ is AwareDatetime:
        return datetime.now().astimezone()
    if type_ is bool:
        return False
    return None


def _extract_int_constraints(metadata: tuple) -> tuple[int, int]:
    """Extract constraints from int metadata and return floor and multiple_of."""
    ge_val = None
    gt_val = None
    multiple_of = 1

    for constraint in metadata:
        if hasattr(constraint, 'ge') and constraint.ge is not None:
            ge_val = constraint.ge
        if hasattr(constraint, 'gt') and constraint.gt is not None:
            gt_val = constraint.gt
        if hasattr(constraint, 'multiple_of') and constraint.multiple_of is not None:
            multiple_of = constraint.multiple_of

    floor = ge_val if ge_val is not None else 0
    floor = gt_val + 1 if gt_val is not None else floor
    return floor, multiple_of


def _handle_annotated_int(type_: Any) -> int | None:
    """Handle Annotated[int, ...] types with constraints."""
    from typing import Annotated

    origin = utils.get_origin(type_)
    if origin is not Annotated:
        return None

    args = typing.get_args(type_)
    if not args or args[0] is not int:
        return None

    metadata = getattr(type_, '__metadata__', ())
    floor, multiple_of = _extract_int_constraints(metadata)

    if math.remainder(floor, multiple_of) == 0:
        return int(floor)
    return int((floor + 1) * multiple_of)


def _check_uuid_pattern(type_: Any) -> bool:
    """Check if type has UUID pattern in metadata."""
    if not hasattr(type_, '__metadata__'):
        return False

    for constraint in type_.__metadata__:
        if hasattr(constraint, 'pattern') and constraint.pattern and constraint.pattern.startswith('^[0-9A-Fa-f]{8}'):
            return True
    return False


def _handle_constrained_string(type_: Any, field_name: str) -> str:
    """Handle constrained string types and return appropriate sample value."""
    if 'uuid' == field_name:
        return str(uuid.uuid4())

    if _check_uuid_pattern(type_):
        return const.SAMPLE_UUID_STR

    if field_name == 'date_authorized':
        return str(date.today().isoformat())

    if field_name == 'oscal_version':
        return OSCAL_VERSION

    if 'uuid' in field_name:
        return const.SAMPLE_UUID_STR

    if field_name.rstrip('s') == 'member_of_organization':
        return const.SAMPLE_UUID_STR

    return const.REPLACE_ME


def _is_constrained_string(type_: Any) -> bool:
    """Return True if *type_* is a constrained string (Annotated[str, StringConstraints(...)]).

    In Pydantic v2, ``constr(pattern=...)`` expands to ``Annotated[str, StringConstraints(...)]``.
    We identify this by checking that the type's origin is ``Annotated`` and its first argument
    is ``str`` — no fragile string-repr matching required.
    """
    if type_ is str:
        return True
    # Annotated[str, ...] — the form produced by constr() in Pydantic v2
    if get_origin(type_) is Annotated:
        args = get_args(type_)
        return bool(args) and args[0] is str
    return False


def _handle_special_types(type_: Any, field_name: str) -> str | dict | None:
    """Handle special types like EmailStr, AnyUrl, dict.

    Args:
        type_: The type to check
        field_name: Field name (unused, kept for API compatibility)
    """
    type_name = getattr(type_, '__name__', str(type_))

    if type_ is EmailStr or 'EmailStr' in type_name:
        return 'dummy@sample.com'

    if type_ is AnyUrl or 'AnyUrl' in type_name:
        return 'https://sample.com/replaceme.html'

    if type_ is dict or (hasattr(type_, '__origin__') and type_.__origin__ is dict):
        return {}  # type: ignore[return-value]

    return None


def generate_sample_value_by_type(type_: Any, field_name: str) -> datetime | bool | int | str | float | Enum | Base64:
    """Given a type, return sample value."""
    # Check enum types
    enum_result = _handle_enum_types(type_)
    if enum_result is not None:
        return enum_result

    # Check simple types
    simple_result = _handle_simple_types(type_)
    if simple_result is not None:
        return simple_result

    # Check annotated int types
    origin = utils.get_origin(type_)
    if origin is not None:
        annotated_int = _handle_annotated_int(type_)
        if annotated_int is not None:
            return annotated_int

    # Check plain numeric types
    if type_ is int:
        return 0
    if type_ is float:
        return 0.00

    # Check constrained strings
    if _is_constrained_string(type_):
        return _handle_constrained_string(type_, field_name)

    # Check enum subclasses
    if safe_is_sub(type_, Enum):
        return type_(list(type_.__members__.values())[0])

    # Check plain string
    if type_ is str:
        if field_name == 'oscal_version':
            return OSCAL_VERSION
        return const.REPLACE_ME

    # Check special types
    special_result = _handle_special_types(type_, field_name)
    if special_result is not None:
        return special_result

    # Check list type
    if type_ is list:
        raise err.TrestleError(f'Unable to generate sample for type {type_}')

    return const.REPLACE_ME


def _get_constrained_int_value(metadata: list) -> int:
    """Return a valid int value satisfying the constraints in field metadata.

    Args:
        metadata: List of constraint objects from field_info.metadata

    Returns:
        An integer value that satisfies all constraints (ge, gt, multiple_of)
    """
    floor, multiple_of = _extract_int_constraints(metadata)
    if math.remainder(floor, multiple_of) == 0:
        return int(floor)
    return int((floor + 1) * multiple_of)


def _handle_special_field_types(model_type: Type, outer_type: Type, field: str, field_info: Any, model: Type) -> Any:
    """Handle special field types (Base64, DateDatatype, DateAuthorized, etc.).

    Args:
        model_type: The type of the model being generated
        outer_type: The type of the field
        field: The field name
        field_info: Field information from model_fields
        model: The model class

    Returns:
        The generated value for the special field type
    """
    if model_type in [Base64Datatype]:
        return sample_base64_value
    elif model_type in [Base64]:
        # Use dictionary lookup for Base64 field mapping
        base64_fields = {
            'filename': sample_base64.filename,
            'media_type': sample_base64.media_type,
            'value': sample_base64.value,
        }
        return base64_fields.get(field)
    elif model_type in [DateDatatype]:
        return sample_date_value
    elif outer_type in [DateAuthorized] or (
        utils.get_origin(outer_type) == Union and DateAuthorized in typing.get_args(outer_type)
    ):
        # Handle DateAuthorized type (which is a RootModel wrapping DateDatatype)
        # DateAuthorized expects a date string that matches the DateDatatype pattern
        return DateAuthorized(root=sample_date_value)
    elif model_type in [DateAuthorized]:
        # When generating DateAuthorized itself, populate its root field
        return sample_date_value
    # Hacking here:
    # Root models should ideally not exist, however, sometimes we are stuck with them.
    # If that is the case we need sufficient information on the type in order to generate a model.
    # E.g. we need the type of the container.
    # In Pydantic v2, RootModel uses 'root' field instead of v1's '__root__' field
    elif field == 'root' and hasattr(model, '__name__'):
        return generate_sample_value_by_type(outer_type, str_utils.classname_to_alias(model.__name__, AliasMode.FIELD))
    else:
        # For int types, check if there are constraints in field metadata
        if outer_type is int and field_info.metadata:
            return _get_constrained_int_value(field_info.metadata)
        else:
            return generate_sample_value_by_type(outer_type, field)


def is_by_type(model_type: Union[Type[TG], List[TG], Dict[str, TG]]) -> bool:
    """Check for by type."""
    rval = False
    if model_type == type_base64:
        rval = True
    return rval


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
    original_model = model  # Preserve the original parameterized type
    # This block normalizes model type down to
    if utils.is_collection_field_type(model):
        model_type = utils.get_origin(model)
        model = utils.get_inner_type(model)

    # Handle Union types at the top level (e.g., when model is Union[Parameter1, Parameter2])
    # This can happen when get_inner_type returns a Union from a list[Union[...]]
    origin = utils.get_origin(model)
    is_union = origin == Union or str(origin) == "<class 'types.UnionType'>"
    if is_union:
        union_args = typing.get_args(model)
        # Find first non-None OscalBaseModel type in the union
        for arg in union_args:
            if arg is not type(None) and safe_is_sub(arg, OscalBaseModel):
                model = arg
                break
        else:
            # If no OscalBaseModel found, use first non-None type
            model = next((arg for arg in union_args if arg is not type(None)), union_args[0])

    model = cast(TG, model)

    # Special handling for RootModel types
    # Check if model is a RootModel subclass by checking if it has 'root' field and RootModel in MRO
    # Only handle RootModel directly if we're not in a collection context (model_type is not list/dict)
    if hasattr(model, 'model_fields') and 'root' in model.model_fields and model_type not in [list, dict]:
        # Check if it's actually a RootModel by checking the base classes
        is_root_model = any(base.__name__ == 'RootModel' for base in model.__mro__)
        if is_root_model:
            # Get the root field type
            root_field_info = model.model_fields['root']
            root_type = root_field_info.annotation

            # Special handling for DateAuthorized RootModel
            if model_type in [DateAuthorized]:
                return DateAuthorized(root=sample_date_value)  # type: ignore

            # Handle Union types in root field
            root_origin = utils.get_origin(root_type)
            is_root_union = root_origin == Union or str(root_origin) == "<class 'types.UnionType'>"
            if is_root_union:
                union_args = typing.get_args(root_type)
                # Find first non-None OscalBaseModel type in the union
                for arg in union_args:
                    if arg is not type(None) and safe_is_sub(arg, OscalBaseModel):
                        # Generate sample for this variant and wrap in RootModel
                        sample_value = generate_sample_model(arg, include_optional=include_optional, depth=depth - 1)
                        return model(root=sample_value)  # type: ignore
                # If no OscalBaseModel found, use first non-None type
                first_type = next((arg for arg in union_args if arg is not type(None)), union_args[0])
                sample_value = generate_sample_model(first_type, include_optional=include_optional, depth=depth - 1)
                return model(root=sample_value)  # type: ignore
            else:
                # Non-union root type.
                # Derive a field-name context from the current model's class name so that
                # field-name-sensitive handlers (e.g. oscal_version → OSCAL_VERSION) fire
                # correctly even when the value is buried inside a chain of RootModels.
                field_name_ctx = str_utils.classname_to_alias(model.__name__, AliasMode.FIELD)

                if safe_is_sub(root_type, OscalBaseModel):
                    sample_value = generate_sample_model(root_type, include_optional=include_optional, depth=depth - 1)
                    return model(root=sample_value)  # type: ignore
                elif hasattr(root_type, 'model_fields') and 'root' in root_type.model_fields:
                    # Nested RootModel (e.g. OscalVersion → StringDatatype → constr).
                    # Resolve the leaf value directly using our field-name context so the
                    # context is not lost through another recursive call.
                    leaf_fi = root_type.model_fields['root']
                    leaf_type = leaf_fi.annotation
                    leaf_value = generate_sample_value_by_type(leaf_type, field_name_ctx)
                    sample_value = root_type(root=leaf_value)
                    return model(root=sample_value)  # type: ignore
                else:
                    # For all other types (including simple types), generate a sample value.
                    sample_value = generate_sample_value_by_type(root_type, field_name_ctx)
                    return model(root=sample_value)  # type: ignore

    model_dict = {}
    # this block is needed to avoid situations where an inbuilt is inside a list / dict.
    # the only time dict ever appears is with include_all, which is handled specially
    # the only type of collection possible after OSCAL 1.0.0 is list
    if safe_is_sub(model, OscalBaseModel):
        for field in model.model_fields:
            # Special handling for include_all field - only skip if it's optional
            field_info = model.model_fields[field]
            if field == 'include_all':
                if field_info.is_required():
                    # Field is required, generate it
                    model_dict[field] = {}
                elif include_optional:
                    # Field is optional and we want to include optional fields
                    model_dict[field] = {}
                continue
            outer_type = field_info.annotation

            # Skip fields with unresolved ForwardRefs, but if required, provide empty list
            if isinstance(outer_type, (str, ForwardRef)):
                # If it's a required field, we need to provide something
                # Assume it's a list type and provide an empty list
                if field_info.is_required():
                    model_dict[field] = []
                continue

            # Handle both typing.Union and types.UnionType (Python 3.10+ uses | operator)
            origin = utils.get_origin(outer_type)
            is_union = origin == Union or str(origin) == "<class 'types.UnionType'>"
            if is_union:
                # For Union types, prefer Enum types over other types for sample generation
                # This handles fields like Union[ConstrainedStr, Enum, None]
                union_args = typing.get_args(outer_type)
                enum_type = None
                for arg in union_args:
                    if arg is not type(None) and safe_is_sub(arg, Enum):
                        enum_type = arg
                        break
                # Use the enum type if found, otherwise fall back to first non-None, non-ForwardRef type.
                if enum_type:
                    outer_type = enum_type
                else:
                    # Preserve a collection member if present; otherwise choose the first usable non-None member.
                    collection_member = next(
                        (arg for arg in union_args if arg is not type(None) and utils.is_collection_field_type(arg)),
                        None,
                    )
                    if collection_member is not None:
                        outer_type = collection_member
                    else:
                        outer_type = next(
                            (
                                arg
                                for arg in union_args
                                if arg is not type(None) and not isinstance(arg, (str, ForwardRef))
                            ),
                            None,
                        )
                        if outer_type is None:
                            # If all types are ForwardRefs or None, skip this field
                            continue
            if field_info.is_required() or effective_optional:
                # FIXME could be ForwardRef('SystemComponentStatus')
                outer_origin = utils.get_origin(outer_type)
                is_outer_union = outer_origin == Union or str(outer_origin) == "<class 'types.UnionType'>"
                union_collection_args = []
                if is_outer_union:
                    union_collection_args = [
                        arg
                        for arg in typing.get_args(outer_type)
                        if arg is not type(None) and utils.is_collection_field_type(arg)
                    ]

                if utils.is_collection_field_type(outer_type) or union_collection_args:
                    collection_outer_type = union_collection_args[0] if union_collection_args else outer_type
                    inner_type = utils.get_inner_type(collection_outer_type)
                    # Check for circular reference: inner_type might be a Union containing model
                    if inner_type == model:
                        continue
                    # Also check if inner_type is a Union and model is one of its variants
                    inner_origin = utils.get_origin(inner_type)
                    is_inner_union = inner_origin == Union or str(inner_origin) == "<class 'types.UnionType'>"
                    if is_inner_union:
                        union_args = typing.get_args(inner_type)
                        if model in union_args:
                            continue  # Circular reference detected
                    # Skip recursion if depth is 0 (but allow -1 for unlimited)
                    # However, if field is required and has min_length constraint, generate at least that many items
                    if depth == 0:
                        # Check if field has min_length constraint
                        min_items = 0
                        if field_info.is_required():
                            # Check field constraints for min_length
                            constraints = field_info.metadata
                            for constraint in constraints:
                                if hasattr(constraint, 'min_length') and constraint.min_length is not None:
                                    min_items = constraint.min_length
                                    break

                        if min_items > 0:
                            # Generate required minimum items
                            model_dict[field] = generate_sample_model(
                                collection_outer_type, include_optional=include_optional, depth=depth - 1
                            )
                        elif field_info.is_required():
                            # Required field with no min_length or min_length=0, assign empty list
                            model_dict[field] = []
                        # else: optional field, don't assign anything (skip it)
                    else:
                        model_dict[field] = generate_sample_model(
                            collection_outer_type, include_optional=include_optional, depth=depth - 1
                        )
                elif is_by_type(outer_type):
                    # For int types, check if there are constraints in field metadata
                    if outer_type is int and field_info.metadata:
                        model_dict[field] = _get_constrained_int_value(field_info.metadata)
                    else:
                        model_dict[field] = generate_sample_value_by_type(outer_type, field)
                elif safe_is_sub(outer_type, OscalBaseModel):
                    # Skip recursion if depth is 0 (but allow -1 for unlimited)
                    # But always generate required fields even at depth 0
                    if depth == 0 and not field_info.is_required():
                        continue  # Skip optional nested models at depth 0
                    else:
                        model_dict[field] = generate_sample_model(
                            outer_type, include_optional=include_optional, depth=depth - 1
                        )
                # Check if outer_type is a RootModel (has 'root' field and RootModel in MRO)
                elif hasattr(outer_type, 'model_fields') and 'root' in outer_type.model_fields:
                    is_root_model = any(base.__name__ == 'RootModel' for base in outer_type.__mro__)
                    if is_root_model:
                        # Generate the RootModel using generate_sample_model
                        model_dict[field] = generate_sample_model(
                            outer_type, include_optional=include_optional, depth=depth - 1
                        )
                    else:
                        # Not a RootModel, fall through to default handling
                        # Handle special cases (hacking)
                        model_dict[field] = _handle_special_field_types(
                            model_type, outer_type, field, field_info, model
                        )
                else:
                    # Handle special cases (hacking)
                    model_dict[field] = _handle_special_field_types(model_type, outer_type, field, field_info, model)
        # Note: this assumes list constrains in oscal are always 1 as a minimum size. if two this may still fail.
    else:
        # Use original_model to preserve parameterized type info (e.g., list[str] not just list)
        collection_type = original_model if 'original_model' in locals() else model_type
        collection_origin = utils.get_origin(collection_type)
        if collection_origin in (Union,) or str(collection_origin) == "<class 'types.UnionType'>":
            union_args = [arg for arg in typing.get_args(collection_type) if arg is not type(None)]
            if len(union_args) == 1:
                collection_type = union_args[0]

        collection_origin = utils.get_origin(collection_type)
        if collection_origin is list or collection_type is list:
            inner_type = utils.get_inner_type(collection_type)
            # Handle bare list without type parameters (inner_type will be Any)
            if inner_type is Any:
                return [const.REPLACE_ME]  # type: ignore
            return [generate_sample_model(inner_type, include_optional=include_optional, depth=depth - 1)]  # type: ignore
        if collection_origin is dict or collection_type is dict:
            inner_type = utils.get_inner_type(collection_type)
            # Handle bare dict without type parameters (inner_type will be Any)
            if inner_type is Any:
                return {const.REPLACE_ME: const.REPLACE_ME}  # type: ignore
            return {const.REPLACE_ME: generate_sample_value_by_type(inner_type, '')}  # type: ignore

        # Handle Union types that aren't collections (e.g., Union[Annotated[str, ...], None])
        # This must come before checking for Annotated types
        if collection_origin == Union or str(collection_origin) == "<class 'types.UnionType'>":
            union_args = typing.get_args(collection_type)
            # Filter out None and get first non-None type
            non_none_args = [arg for arg in union_args if arg is not type(None)]
            if non_none_args:
                # Recursively handle the first non-None type
                return generate_sample_model(non_none_args[0], include_optional=include_optional, depth=depth - 1)
            # If all args are None, return None (shouldn't happen in practice)
            return None  # type: ignore

        # Check if this is a basic type or Annotated type that should use generate_sample_value_by_type
        # This handles cases like Annotated[str, StringConstraints(...)]
        from typing import Annotated

        if collection_origin is Annotated:
            # Get the base type from Annotated
            args = typing.get_args(collection_type)
            if args:
                base_type = args[0]
                # Check if base type is a simple type (str, int, float, bool, etc.)
                if base_type in (str, int, float, bool, datetime):
                    return generate_sample_value_by_type(collection_type, '')

        # If it's a simple type directly
        if collection_type in (str, int, float, bool, datetime):
            return generate_sample_value_by_type(collection_type, '')

        # Check if it's a Pydantic special type (EmailStr, HttpUrl, etc.)
        # These have __get_pydantic_core_schema__ method
        if hasattr(collection_type, '__get_pydantic_core_schema__'):
            return generate_sample_value_by_type(collection_type, '')

        raise err.TrestleError(f'Unhandled collection type: {collection_type}')
    if model_type is list:
        return [model(**model_dict)]  # type: ignore
    if model_type is dict:
        return {const.REPLACE_ME: model(**model_dict)}  # type: ignore
    return model(**model_dict)  # type: ignore
