# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Element wrapper of an OSCAL model element."""

from typing import List

from pydantic import Field, create_model
from pydantic.error_wrappers import ValidationError

import trestle.core.utils as utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError

import yaml


class ElementPath:
    """Element path wrapper of an element.

    This only allows a single wildcard '*' at the end to denote elements of an array of dict
    """

    PATH_SEPARATOR: str = '.'

    WILDCARD: str = '*'

    def __init__(self, element_path: str):
        """Initialize an element wrapper."""
        self._path: List[str] = self._parse(element_path)

        # Initialize variables for lazy processing and caching
        # This will be processed and cached
        self._element_name = None
        self._parent_element_path = None

    def _parse(self, element_path) -> List[str]:
        """Parse the element path and validate."""
        parts: List[str] = element_path.split(self.PATH_SEPARATOR)

        for i, part in enumerate(parts):
            if part == '':
                raise TrestleError(
                    f'Invalid path "{element_path}" because having empty path parts between "{self.PATH_SEPARATOR}" \
                        or in the beginning'
                )
            elif part == self.WILDCARD and i != len(parts) - 1:
                raise TrestleError(f'Invalid path. Wildcard "{self.WILDCARD}" can only be at the end')

        if parts[-1] == self.WILDCARD and len(parts) == 1:
            raise TrestleError(f'Invalid path {element_path}')

        return parts

    def get(self) -> List[str]:
        """Return the path components as a list."""
        return self._path

    def get_first(self) -> str:
        """Return the first part of the path."""
        return self._path[0]

    def get_last(self) -> str:
        """Return the last part of the path."""
        return self._path[-1]

    def get_element_name(self):
        """Return the element name from the path."""
        # if it is available then return otherwise compute
        if self._element_name is None:
            element_name = self.get_last()
            if element_name == self.WILDCARD:
                element_name = self._path[-2]

            self._element_name = element_name

        return self._element_name

    def get_parent_path(self):
        """Return the path to the parent element."""
        # if it is available then return otherwise compute
        if self._parent_element_path is None:
            if len(self._path) > 1:
                parent_path_parts = self._path[:-1]
                self._parent_element_path = ElementPath(self.PATH_SEPARATOR.join(parent_path_parts))

        return self._parent_element_path

    def __str__(self):
        """Return string representation of element path."""
        return self.PATH_SEPARATOR.join(self._path)

    def __eq__(self, other):
        """Override equality method."""
        if not isinstance(other, ElementPath):
            return False

        return self._path == other.get()


class Element:
    """Element wrapper of an OSCAL model."""

    _allowed_sub_element_types = [OscalBaseModel.__class__, list.__class__, None.__class__]

    def __init__(self, elem: OscalBaseModel):
        """Initialize an element wrapper."""
        self._elem: OscalBaseModel = elem

    def get(self) -> OscalBaseModel:
        """Return the model object."""
        return self._elem

    def get_at(self, element_path: ElementPath = None):
        """Get the element at the specified element path.

        it will return the sub-model object at the path. Sub-model object
        can be of type OscalBaseModel or List
        """
        if element_path is None:
            return self._elem

        # return the sub-element at the specified path
        elm = self._elem
        for attr in element_path.get():
            # process for wildcard and array indexes
            if attr == ElementPath.WILDCARD:
                break
            elif attr.isnumeric():
                if isinstance(elm, list):
                    elm = elm[int(attr)]
                else:
                    elm = None
                    break
            else:
                elm = getattr(elm, attr, None)

        return elm

    def get_parent(self, element_path: ElementPath):
        """Get the parent element of the element specified by the path."""
        # get the parent element
        parent_path = element_path.get_parent_path()
        if parent_path is None:
            parent_elm = self.get()
        else:
            parent_elm = self.get_at(parent_path)

        return parent_elm

    def _get_sub_element_obj(self, sub_element):
        """Convert sub element into allowed model obj."""
        if not self.is_allowed_sub_element_type(sub_element):
            raise TrestleError(
                f'Sub element must be one of "{self.get_allowed_sub_element_types()}", found "{sub_element.__class__}"'
            )

        model_obj = sub_element
        if isinstance(sub_element, Element):
            model_obj = sub_element.get()

        return model_obj

    def set_at(self, element_path, sub_element):
        """Set a sub_element at the path in the current element.

        Sub element can be Element, OscalBaseModel, list or None type
        It returns the element itself so that chaining operation can be done such as element.set_at(path, sub-element).get().
        """
        # convert the element_path to ElementPath if needed
        if isinstance(element_path, str):
            element_path = ElementPath(element_path)

        # convert sub-element to OscalBaseModel if needed
        model_obj = self._get_sub_element_obj(sub_element)

        # If wildcard is present, check the input type and determine the parent element
        if element_path.get_last() == ElementPath.WILDCARD:
            # validate the type is either list or OscalBaseModel
            if not isinstance(model_obj, list) and not isinstance(model_obj, OscalBaseModel):
                raise TrestleError(
                    f'The model object needs to be a List or OscalBaseModel for path with "{ElementPath.WILDCARD}"'
                )

            # since wildcard * is there, we need to go one level up for parent element
            parent_elm = self.get_parent(element_path.get_parent_path())
        else:
            # get the parent element
            parent_elm = self.get_parent(element_path)

        if parent_elm is None:
            raise TrestleError(f'Invalid sub element path {element_path} with no parent element')

        # check if it can be a valid sub_element of the parent
        sub_element_name = element_path.get_element_name()
        if hasattr(parent_elm, sub_element_name) is False:
            raise TrestleError(
                f'Element "{parent_elm.__class__}" does not have the attribute "{sub_element_name}" \
                    of type "{model_obj.__class__}"'
            )

        # set the sub-element
        try:
            setattr(parent_elm, sub_element_name, model_obj)
        except ValidationError:
            sub_element_class = self.get_sub_element_class(parent_elm, sub_element_name)
            raise TrestleError(
                f'Validation error: {sub_element_name} is expected to be "{sub_element_class}", \
                    but found "{model_obj.__class__}"'
            )

        # returning self will allow to do 'chaining' of commands after set
        return self

    def to_yaml(self):
        """Convert into YAML string."""
        wrapped_model = self.oscal_wrapper()
        return yaml.dump(yaml.safe_load(wrapped_model.json(exclude_none=True, by_alias=True)))

    def to_json(self):
        """Convert into JSON string."""
        wrapped_model = self.oscal_wrapper()
        json_data = wrapped_model.json(exclude_none=True, by_alias=True, indent=4)
        return json_data

    def oscal_wrapper(self):
        """Create OSCAL wrapper model for read and write."""
        class_name = self._elem.__class__.__name__
        # It would be nice to pass through the description but I can't seem to and
        # it does not affect the output
        dynamic_passer = {}
        dynamic_passer[utils.class_to_oscal(class_name, 'field')] = (
            self._elem.__class__,
            Field(
                self, title=utils.class_to_oscal(class_name, 'field'), alias=utils.class_to_oscal(class_name, 'json')
            )
        )
        wrapper_model = create_model(class_name, __base__=OscalBaseModel, **dynamic_passer)
        # Default behaviour is strange here.
        wrapped_model = wrapper_model(**{utils.class_to_oscal(class_name, 'json'): self._elem})

        return wrapped_model

    @classmethod
    def get_sub_element_class(cls, parent_elm: OscalBaseModel, sub_element_name: str):
        """Get the class of the sub-element."""
        sub_element_class = parent_elm.__fields__.get(sub_element_name).outer_type_
        return sub_element_class

    @classmethod
    def get_allowed_sub_element_types(cls) -> List[str]:
        """Get the list of allowed sub element types."""
        return cls._allowed_sub_element_types.append(Element.__class__)

    @classmethod
    def is_allowed_sub_element_type(cls, elm) -> bool:
        """Check if is of allowed sub element type."""
        if (isinstance(elm, Element) or isinstance(elm, OscalBaseModel) or isinstance(elm, list) or elm is None):
            return True

        return False

    def __str__(self):
        """Return string representation of element."""
        return type(self._elem).__name__

    def __eq__(self, other):
        """Override equality method."""
        if not isinstance(other, Element):
            return False

        self_json = self.to_json()
        other_json = other.to_json()
        return self_json == other_json
