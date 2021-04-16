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

import json
import pathlib
from typing import Dict, List, Optional, Union

from pydantic import Field, create_model
from pydantic.error_wrappers import ValidationError

import trestle.core.const as const
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError, TrestleNotFoundError
from trestle.core.models.file_content_type import FileContentType

import yaml


class ElementPath:
    """Element path wrapper of an element.

    This only allows a single wildcard '*' at the end to denote elements of an array of dict
    """

    PATH_SEPARATOR: str = const.ALIAS_PATH_SEPARATOR

    WILDCARD: str = '*'

    def __init__(self, element_path: str, parent_path: Optional['ElementPath'] = None) -> None:
        """Initialize an element wrapper.

        It assumes the element path contains oscal field alias with hyphens only
        """
        if isinstance(parent_path, str):
            parent_path = ElementPath(parent_path)
        self._parent_path = parent_path

        self._path: List[str] = self._parse(element_path)

        # Initialize private variables for lazy processing and caching
        self._element_name: Optional[str] = None
        self._preceding_path: Optional['ElementPath'] = None

    def _parse(self, element_path: str) -> List[str]:
        """Parse the element path and validate."""
        parts: List[str] = element_path.split(self.PATH_SEPARATOR)

        for i, part in enumerate(parts):
            if part == '':
                raise TrestleError(
                    f'Invalid path "{element_path}" because having empty path parts between "{self.PATH_SEPARATOR}" '
                    'or in the beginning'
                )
            elif part == self.WILDCARD and i != len(parts) - 1:
                raise TrestleError(f'Invalid path. Wildcard "{self.WILDCARD}" can only be at the end')

        if parts[-1] == self.WILDCARD:
            if len(parts) == 1:
                raise TrestleError(f'Invalid path {element_path} with wildcard.')

        if len(parts) <= 1:
            raise TrestleError(
                'Element path must have at least two parts with the first part being the model root name, '
                'like "target-definition.metadata"'
            )

        return parts

    def get(self) -> List[str]:
        """Return the path parts as a list."""
        return self._path

    def to_string(self) -> str:
        """Return the path parts as a dot-separated string."""
        return self.PATH_SEPARATOR.join(self.get())

    def get_parent(self) -> 'ElementPath':
        """Return the parent path.

        It can be None or a valid ElementPath
        """
        return self._parent_path

    def get_first(self) -> str:
        """Return the first part of the path."""
        return self._path[0]

    def get_last(self) -> str:
        """Return the last part of the path."""
        return self._path[-1]

    def get_full(self) -> str:
        """Return the full path including parent path parts as a dot separated str."""
        all_parts = self.get_full_path_parts()
        return self.PATH_SEPARATOR.join(all_parts)

    def get_element_name(self) -> str:
        """Return the element alias name from the path.

        Essentailly this the last part of the element path
        """
        # if it is available then return otherwise compute
        if self._element_name is None:
            element_name = self.get_last()
            if element_name == self.WILDCARD:
                element_name = self._path[-2]

            self._element_name = element_name

        return self._element_name

    def get_full_path_parts(self) -> List[str]:
        """Get full path parts to the element including parent path parts as a list."""
        path_parts = []
        if self.get_parent() is not None:
            parent_path_parts = self.get_parent().get_full_path_parts()
            path_parts.extend(parent_path_parts)
            path_parts.extend(self.get()[1:])  # don't use the first part
        else:
            path_parts.extend(self.get())

        return path_parts

    def get_preceding_path(self) -> 'ElementPath':
        """Return the element path to the preceding element in the path."""
        # if it is available then return otherwise compute
        if self._preceding_path is None:
            path_parts = self.get_full_path_parts()

            if len(path_parts) > 1:
                prec_path_parts = path_parts[:-1]

                # prec_path_parts must have at least two parts
                if len(prec_path_parts) > 1:
                    self._preceding_path = ElementPath(self.PATH_SEPARATOR.join(prec_path_parts))

        return self._preceding_path

    def to_file_path(self, content_type: FileContentType = None, root_dir: str = '') -> pathlib.Path:
        """Convert to a file or directory path for the element path.

        if content_type is not passed, it will return a path for directory
        """
        path_parts = self.get()

        # skip wildcard
        if path_parts[-1] == ElementPath.WILDCARD:
            path_parts = path_parts[:-1]

        if root_dir != '':
            path_parts[0] = root_dir

        path_str = '/'.join(path_parts)

        # add file extension if required
        # this will be omitted if it is a dir path
        if content_type is not None:
            file_extension = FileContentType.to_file_extension(content_type)
            path_str = path_str + file_extension

        # prepare the path
        file_path: pathlib.Path = pathlib.Path(f'./{path_str}')

        return file_path

    def to_root_path(self, content_type: FileContentType = None) -> pathlib.Path:
        """Convert to a file path for the element root."""
        path_str = f'./{self.get_first()}'
        if content_type is not None:
            file_extension = FileContentType.to_file_extension(content_type)
            path_str = path_str + file_extension

        file_path: pathlib.Path = pathlib.Path(path_str)
        return file_path

    def __str__(self) -> str:
        """Return string representation of element path."""
        return self.to_string()

    def __eq__(self, other) -> bool:
        """Override equality method."""
        if not isinstance(other, ElementPath):
            return False

        return self.get() == other.get()


class Element:
    """Element wrapper of an OSCAL model."""

    IGNORE_WRAPPER_ALIAS = '__'

    _allowed_sub_element_types: List[str] = ['Element', 'OscalBaseModel', 'list', 'None', 'dict']

    def __init__(self, elem: OscalBaseModel, wrapper_alias: str = ''):
        """Initialize an element wrapper.

        wrapper_alias is the OSCAL alias for the given elem object and used for seriazation in to_json() method.

        For example,
         - List[Catalog.Group] element should have wrapper alias 'groups'
         - Catalog element should have wrapper alias 'catalog'

        wrapper_alias is mandatory for collection type object

        if wrapper_alias = IGNORE_WRAPPER_ALIAS, then it is ignored and assumed to be json-serializable during to_json()
        """
        self._elem: OscalBaseModel = elem

        if wrapper_alias == '' and wrapper_alias != self.IGNORE_WRAPPER_ALIAS:
            if utils.is_collection_field_type(elem):
                raise TrestleError('wrapper_alias is required for a collection type object')
            else:
                wrapper_alias = utils.classname_to_alias(elem.__class__.__name__, 'json')

        self._wrapper_alias: str = wrapper_alias

    def get(self) -> OscalBaseModel:
        """Return the model object."""
        return self._elem

    def _split_element_path(self, element_path: ElementPath):
        """Split the element path into root_model and remaing attr names."""
        path_parts = element_path.get()
        root_model = path_parts[0]
        path_parts = path_parts[1:]

        return root_model, path_parts

    def get_at(self,
               element_path: ElementPath = None,
               check_parent: bool = True) -> Union[OscalBaseModel, List[OscalBaseModel], Dict[str, OscalBaseModel]]:
        """Get the element at the specified element path.

        it will return the sub-model object at the path. Sub-model object
        can be of type OscalBaseModel or List
        """
        if element_path is None:
            return self._elem

        # find the root-model and element path parts
        _, path_parts = self._split_element_path(element_path)

        # TODO validate that self._elem is of same type as root_model

        # initialize the starting element for search
        elm = self._elem
        if hasattr(elm, '__root__') and (isinstance(elm.__root__, dict) or isinstance(elm.__root__, list)):
            elm = elm.__root__

        # if parent exists and does not end with wildcard, use the parent as the starting element for search
        if check_parent and element_path.get_parent(
        ) is not None and element_path.get_parent().get_last() != ElementPath.WILDCARD:
            elm_at = self.get_at(element_path.get_parent())
            if elm_at is None:
                raise TrestleNotFoundError(f'Invalid parent path {element_path.get_parent()}')
            elm = elm_at

        # return the sub-element at the specified path
        for attr in path_parts:
            if elm is None:
                break

            # process for wildcard and array indexes

            if attr == ElementPath.WILDCARD:
                break
            elif attr.isnumeric():
                if isinstance(elm, list):
                    elm = elm[int(attr)]
                else:
                    # index to a non list type should return None
                    return None
            elif isinstance(elm, dict):
                elm = elm.get(attr, None)
            else:
                elm = elm.get_field_value_by_alias(attr)

        return elm

    def get_preceding_element(self, element_path: ElementPath) -> Optional[OscalBaseModel]:
        """Get the preceding element in the path."""
        preceding_path = element_path.get_preceding_path()
        preceding_elm: Optional[OscalBaseModel] = self.get_at(preceding_path)
        return preceding_elm

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

    def set_at(self, element_path: ElementPath, sub_element: OscalBaseModel) -> 'Element':
        """Set a sub_element at the path in the current element.

        Sub element can be Element, OscalBaseModel, list or None type
        It returns the element itself so that chaining operation can be done such as
            `element.set_at(path, sub-element).get()`.
        """
        # convert the element_path to ElementPath if needed
        if isinstance(element_path, str):
            element_path = ElementPath(element_path)

        # convert sub-element to OscalBaseModel if needed
        model_obj = self._get_sub_element_obj(sub_element)

        # find the root-model and element path parts
        _, path_parts = self._split_element_path(element_path)

        # TODO validate that self._elem is of same type as root_model

        # If wildcard is present, check the input type and determine the preceding element
        if element_path.get_last() == ElementPath.WILDCARD:
            # validate the type is either list or OscalBaseModel
            if not isinstance(model_obj, list) and not isinstance(model_obj, OscalBaseModel):
                raise TrestleError(
                    f'The model object needs to be a List or OscalBaseModel for path with "{ElementPath.WILDCARD}"'
                )

            # since wildcard * is there, we need to go one level up for preceding element in the path
            preceding_elm = self.get_preceding_element(element_path.get_preceding_path())
        else:
            # get the preceding element in the path
            preceding_elm = self.get_preceding_element(element_path)

        if preceding_elm is None:
            raise TrestleError(f'Invalid sub element path {element_path} with no valid preceding element')

        # check if it can be a valid sub_element of the parent
        sub_element_name = element_path.get_element_name().replace('-', '_')
        if hasattr(preceding_elm, sub_element_name) is False:
            raise TrestleError(
                f'Element "{preceding_elm.__class__}" does not have the attribute "{sub_element_name}" '
                f'of type "{model_obj.__class__}"'
            )

        # set the sub-element
        try:
            setattr(preceding_elm, sub_element_name, model_obj)
        except ValidationError:
            sub_element_class = self.get_sub_element_class(preceding_elm, sub_element_name)
            raise TrestleError(
                f'Validation error: {sub_element_name} is expected to be "{sub_element_class}", '
                f'but found "{model_obj.__class__}"'
            )

        # returning self will allow to do 'chaining' of commands after set
        return self

    def to_yaml(self) -> str:
        """Convert into YAML string."""
        yaml_data = yaml.dump(yaml.safe_load(self.to_json()))
        return yaml_data

    def to_json(self) -> str:
        """Convert into JSON string."""
        if self._wrapper_alias == self.IGNORE_WRAPPER_ALIAS:
            json_data = json.dumps(self._elem, sort_keys=False, indent=4)
        else:
            dynamic_passer = {}
            dynamic_passer['TransientField'] = (self._elem.__class__, Field(self, alias=self._wrapper_alias))
            wrapper_model = create_model('TransientModel', __base__=OscalBaseModel, **dynamic_passer)  # type: ignore
            wrapped_model = wrapper_model(**{self._wrapper_alias: self._elem})
            json_data = wrapped_model.json(exclude_none=True, by_alias=True, indent=4)

        return json_data

    @classmethod
    def get_sub_element_class(cls, parent_elm: OscalBaseModel, sub_element_name: str):
        """Get the class of the sub-element."""
        sub_element_class = parent_elm.__fields__[sub_element_name].outer_type_
        return sub_element_class

    @classmethod
    def get_allowed_sub_element_types(cls) -> List[str]:
        """Get the list of allowed sub element types."""
        return cls._allowed_sub_element_types

    @classmethod
    def is_allowed_sub_element_type(cls, elm) -> bool:
        """Check if is of allowed sub element type."""
        # FIXME: The following logic does not use the _allowed_sub_element_types being defined for the class
        if (isinstance(elm, Element) or isinstance(elm, OscalBaseModel) or isinstance(elm, list)
                or isinstance(elm, dict) or elm is None):
            return True

        return False

    def __str__(self) -> str:
        """Return string representation of element."""
        return type(self._elem).__name__

    def __eq__(self, other: object) -> bool:
        """Check that two elements are equal."""
        if not isinstance(other, Element):
            return False

        return self.get() == other.get()
