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
"""Model parsing for use when models themselves must be inferred and are not known.

Under most use cases trestle.core.base_model.OscalBaseModel provides functionality for loading Oscal models from files.
However, under some circumstances the model internals are unknown.  Use of this module should be avoided unless
the BaseModel functionality is inadequate.
"""

import importlib
import logging
from typing import Any, Dict

from trestle.common import const
from trestle.common.err import TrestleError
from trestle.common.str_utils import AliasMode, alias_to_classname
from trestle.core.base_model import OscalBaseModel

logger = logging.getLogger(__name__)


def parse_dict(data: Dict[str, Any], model_name: str) -> OscalBaseModel:
    """Load a model from the data dict.

    This functionality is provided for situations when the OSCAL data type is not known ahead of time. Here the model
    has been loaded into memory using json loads or similar and passed as a dict.

    Args:
        data: Oscal data loaded into memory as a dictionary with the `root key` removed.
        model_name: should be of the form 'module.class' from trestle.oscal.* modules

    Returns:
        The oscal model of the desired model.
    """
    if data is None:
        raise TrestleError('data name is required')

    if model_name is None:
        raise TrestleError('model_name is required')

    parts = model_name.split('.')
    class_name = parts.pop()
    module_name = '.'.join(parts)

    logger.debug(f'Loading class "{class_name}" from "{module_name}"')
    module = importlib.import_module(module_name)
    mclass: OscalBaseModel = getattr(module, class_name)
    if mclass is None:
        raise TrestleError(f'class "{class_name}" could not be found in "{module_name}"')

    instance = mclass.parse_obj(data)
    return instance


def root_key(data: Dict[str, Any]) -> str:
    """Find root model name in the data."""
    if len(data.items()) == 1:
        return next(iter(data))

    raise TrestleError('data does not contain a root key')


def to_full_model_name(root_key: str) -> str:
    """
    Find model name from the root_key in the file.

    Args:
        root_key: root key such as 'system-security-plan' from a top level OSCAL model.
    """
    if root_key not in const.MODEL_TYPE_LIST:
        raise TrestleError(f'{root_key} is not a top level model name.')

    module = const.MODEL_TYPE_TO_MODEL_MODULE[root_key]
    class_name = alias_to_classname(root_key, AliasMode.JSON)
    return f'{module}.{class_name}'
