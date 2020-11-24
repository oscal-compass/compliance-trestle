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
"""Dynamic Model Parser."""

import importlib
import pathlib
import warnings
from typing import Any, Dict, List, Optional, Type, cast

from pydantic import Field, create_model

from trestle.core import const
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.utils import fs
from trestle.utils import log

logger = log.get_logger()


def parse_dict(data: Dict[str, Any], model_name: str) -> OscalBaseModel:
    """Load a model from the data dict.

    Argument:
        model_name: it should be of the form <module>.<class>
                    <class> should be a Pydantic class that supports `parse_obj` method
    """
    warnings.warn('trestle.parser functions are deprecated', DeprecationWarning)
    if data is None:
        raise TrestleError('data name is required')

    if model_name is None:
        raise TrestleError('model_name is required')

    parts = model_name.split('.')
    class_name = parts.pop()
    module_name = '.'.join(parts)

    logger.debug(f'Loading class "{class_name}" from "{module_name}"')
    module = importlib.import_module(module_name)
    mclass = getattr(module, class_name)
    if mclass is None:
        raise TrestleError(f'class "{class_name}" could not be found in "{module_name}"')

    instance = mclass.parse_obj(data)
    return instance


def root_key(data: Dict[str, Any]) -> str:
    """Find root model name in the data."""
    if len(data.items()) == 1:
        return next(iter(data))

    raise TrestleError('data does not contain a root key')


def to_class_name(name: str) -> str:
    """Convert to pascal class name."""
    warnings.warn('trestle.parser functions are deprecated', DeprecationWarning)
    if name.find('-') != -1:
        parts = name.split('-')

        for i, part in enumerate(parts):
            parts[i] = part.capitalize()

        name = ''.join(parts)
        return name

    chars = list(name)
    chars[0] = chars[0].upper()
    return ''.join(chars)


def to_full_model_name(root_key: str, name: str = None) -> Optional[str]:
    """Find model name from the root_key in the file."""
    warnings.warn('trestle.parser functions are deprecated', DeprecationWarning)
    try:
        # process root key and extract model name
        module_name = root_key.lower()
        if root_key.find('-') != -1:
            parts = root_key.split('-')
            module_name = parts[0]

            for i, part in enumerate(parts):
                parts[i] = part.capitalize()

            name = ''.join(parts)

        # check for module with the root-key
        module = importlib.import_module(f'{const.PACKAGE_OSCAL}.{module_name}')

        # prepare class name
        if name is None:
            name = module_name
        class_name = to_class_name(name)

        # check if class exists in the module or not
        if getattr(module, class_name) is not None:
            return f'{const.PACKAGE_OSCAL}.{module_name}.{class_name}'
    except ModuleNotFoundError as ex:
        logger.error(f'Module {module_name} not found: {ex}')
        pass

    return None


def parse_file(file_name: pathlib.Path, model_name: str) -> OscalBaseModel:
    """Load a model from the file.

    Argument:
        model_name: it should be of the form <module>.<class>
                    <class> should be a Pydantic class that supports `parse_obj` method
    """
    warnings.warn('trestle.parser functions are deprecated', DeprecationWarning)
    if file_name is None:
        raise TrestleError('file_name is required')

    data = fs.load_file(file_name)
    rkey = root_key(data)
    if model_name is None:
        model_name = to_full_model_name(rkey)
    return parse_dict(data[rkey], model_name)


def wrap_for_output(model: OscalBaseModel) -> OscalBaseModel:
    """Dynamically wrap for output a class such that the correct string is provided."""
    warnings.warn(
        'trestle.parser functions are deprecated. wrap_for_output built into OSCALBaseModel.', DeprecationWarning
    )
    # TODO: Refactor based on next method.
    class_name = model.__class__.__name__
    # It would be nice to pass through the description but I can't seem to and
    # it does not affect the output
    dynamic_passer = {}
    dynamic_passer[class_to_oscal(class_name, 'field')] = (
        model.__class__,
        Field(model, title=class_to_oscal(class_name, 'field'), alias=class_to_oscal(class_name, 'json'))
    )
    wrapper_model = create_model(class_name, __base__=OscalBaseModel, **dynamic_passer)  # type: ignore
    # Default behaviour is strange here.
    wrapped_model = wrapper_model(**{class_to_oscal(class_name, 'json'): model})
    wrapped_model = cast(OscalBaseModel, wrapped_model)
    return wrapped_model


def wrap_for_input(raw_class: Type[OscalBaseModel]) -> Type[OscalBaseModel]:
    """In this instance we are wrapping an actual OSCAL class not an instance."""
    warnings.warn(
        'trestle.parser functions are deprecated. wrap_for_input built ito OscalBaseModel', DeprecationWarning
    )
    # TODO: Check behaviour is fine when no
    class_name = raw_class.__name__
    dynamic_passer = {}
    dynamic_passer[class_to_oscal(
        class_name, 'field'
    )] = (raw_class, Field(..., title=class_to_oscal(class_name, 'json'), alias=class_to_oscal(class_name, 'json')))
    wrapper_model = create_model('Wrapped' + class_name, __base__=OscalBaseModel, **dynamic_passer)  # type: ignore
    wrapper_model = cast(Type[OscalBaseModel], wrapper_model)
    return wrapper_model


def class_to_oscal(class_name: str, mode: str) -> str:
    """
    Return oscal json or field element name based on class name.

    This is applicable when asking for a singular element.
    """
    warnings.warn('trestle.parser functions are deprecated. class_to_oscal now contained in utils', DeprecationWarning)
    parts = pascal_case_split(class_name)
    if mode == 'json':
        return '-'.join(map(str.lower, parts))
    elif mode == 'field':
        return '_'.join(map(str.lower, parts))
    else:
        raise TrestleError('Bad option')


def pascal_case_split(pascal_str: str) -> List[str]:
    """Parse a pascal case string (e.g. a ClassName) and return a list of strings."""
    warnings.warn(
        'trestle.parser functions are deprecated. pascal_case_split now contained in utils', DeprecationWarning
    )
    start_idx = [i for i, e in enumerate(pascal_str) if e.isupper()] + [len(pascal_str)]
    return [pascal_str[x:y] for x, y in zip(start_idx, start_idx[1:])]
