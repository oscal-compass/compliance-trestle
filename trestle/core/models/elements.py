# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Element wrapper of an OSCAL model element."""

import logging
import pathlib
from typing import Any, List, Optional, Type, Union, cast

from pydantic import Field, create_model
from pydantic.error_wrappers import ValidationError

from ruamel.yaml import YAML

import trestle.core.const as const
from trestle.core import common_types, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError, TrestleNotFoundError
from trestle.core.models.file_content_type import FileContentType

logger = logging.getLogger(__name__)


class ElementPath:
    """Element path wrapper of an element.

    This only allows a single wildcard '*' at the end to denote elements of an array or dict
    """

    PATH_SEPARATOR: str = const.ALIAS_PATH_SEPARATOR

    WILDCARD: str = '*'

    def __init__(self, element_path: str, parent_path: Optional['ElementPath'] = None) -> None:
        """Initialize an element wrapper.

        It assumes the element path contains oscal field alias with hyphens only
        """
        self._parent_path = parent_path

        self._path: List[str] = self._parse(element_path)

        # Initialize private variables for lazy processing and caching
        self._element_name: Optional[str] = None
        self._preceding_path: Optional['ElementPath'] = None

    def _parse(self, element_path: str) -> List[str]:
        """Parse the element path and validate."""
        parts: List[str] = element_path.split(self.PATH_SEPARATOR)

        for part in parts:
            if part == '':
                raise TrestleError(
                    f'Invalid path "{element_path}" because there are empty path parts between "{self.PATH_SEPARATOR}" '
                    'or in the beginning'
                )

        if parts[0] == self.WILDCARD:
            raise TrestleError(f'Invalid path {element_path} with wildcard.')
        return parts

    def get(self) -> List[str]:
        """Return the path parts as a list."""
        return self._path

    def get_type(self, root_model: Optional[Type[Any]] = None, use_parent: bool = False) -> Type[Any]:
        """Get the type of an element.

        If possible the model type will be derived from one of the top level models,
        otherwise a 'root model' can be passed for situations where this is not possible.

        This type path should *NOT* have wild cards in it. It *may* have* indices.
        Valid Examples:
            catalog.metadata
            catalog.groups
            catalog.groups.group
            catalog
            catalog.groups.0

        Args:
            root_model: An OscalBaseModel Type from which to base the approach on.
            use_parent: Whether or not to normalise the full path across parent ElementPaths, default to not.

        Returns:
            The type of the model whether or not it is an OscalBaseModel or not.
        """
        effective_path: List[str]
        if use_parent:
            effective_path = self.get_full_path_parts()
        else:
            effective_path = self._path

        if not root_model:
            # lookup root model from top level oscal models or fail
            prev_model = self._top_level_type_lookup(effective_path[0])
        else:
            prev_model = root_model
        if len(effective_path) == 1:
            return prev_model
        # variables
        # for current_element_str in effective_path[1:]:
        for current_element_str in effective_path[1:]:
            # Determine if the parent model is a collection.
            if utils.is_collection_field_type(prev_model):
                inner_model = utils.get_inner_type(prev_model)
                inner_class_name = utils.classname_to_alias(inner_model.__name__, 'json')
                # Assert that the current name fits an expected form.
                # Valid choices here are *, integer (for arrays) and the inner model alias
                if (inner_class_name == current_element_str or current_element_str == self.WILDCARD
                        or current_element_str.isnumeric()):
                    prev_model = inner_model

                else:
                    raise TrestleError('Unexpected key in element path when finding type.')

            else:
                # Indices, * are not allowed on non-collection types
                if current_element_str == self.WILDCARD:
                    logger.error('Cannot get the type of an element path where wild cards do not match a  ')
                    raise TrestleError(
                        'Wild card in unexpected position when trying to find class type.'
                        + ' Element path type lookup can only occur where a single type can be identified.'
                    )
                prev_model = prev_model.alias_to_field_map()[current_element_str].outer_type_
        return prev_model

    def get_obm_wrapped_type(self,
                             root_model: Optional[Type[Any]] = None,
                             use_parent: bool = False) -> Type[OscalBaseModel]:
        """Get the type of the element. If the type is a collection wrap the type in an OscalBaseModel as a __root__ element.

        This should principally be used for validating content.

        Args:
            root_model: An OscalBaseModel Type from which to base the approach on.
            use_parent: Whether or not to normalise the full path across parent ElementPaths, default to not.

        Returns:
            The type of the model whether wrapped or not as an OscalBaseModel.
        """
        base_type = self.get_type(root_model, use_parent)
        # Get an outer model type.
        origin_type = utils.get_origin(base_type)

        if origin_type in [list, dict]:
            # OSCAL does not support collections of collections directly. We should not hit this scenario
            collection_name = self.get_last()
            if collection_name == self.WILDCARD:
                logger.critical('Unexpected error in type system when inferring type from element path.')
                logger.critical('Please report this issue.')
                raise TrestleError('Unknown error inferring type from element path.')
            # Final path must be the alias

            new_base_type = create_model(
                utils.alias_to_classname(collection_name, 'json'), __base__=OscalBaseModel, __root__=(base_type, ...)
            )
            return new_base_type
        return base_type

    def _top_level_type_lookup(self, element_str: str) -> Type[common_types.TopLevelOscalModel]:
        """From an individual element tag, induce the type of the model.

        Args:
            element_str: individual element as text such as 'catalog' or 'profile'

        Returns:
            Top level object model such as catalog, profile etc.
        """
        # Even though awkward use chain of models.
        if element_str not in const.MODEL_TYPE_LIST:
            raise TrestleError(f'{element_str} is not a top level model (e.g. catalog, profile)')
        model_package = const.MODEL_TYPE_TO_MODEL_MODULE[element_str]
        object_type, _ = utils.get_root_model(model_package)
        object_type = cast(Type[common_types.TopLevelOscalModel], object_type)
        return object_type

    def is_multipart(self) -> bool:
        """Assert whether or not an element path is multiple parts.

        Originally element paths had to have multiple paths.
        This provides a check for higher level code that still has that requirement.

        Single part:
            catalog
            control
            assessment-results

        Multipart:
            catalog.metadata
            catalog.controls.control
        """
        return len(self._path) > 1

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
                self._preceding_path = ElementPath(self.PATH_SEPARATOR.join(prec_path_parts))

        return self._preceding_path

    def find_last_file_in_path(self, content_type: FileContentType, model_dir: pathlib.Path) -> pathlib.Path:
        """Find the last (nearest) existing file in the element path leading to this element."""
        # model dir is the top level dir for this model, e.g. catalogs/mycat
        path = model_dir
        extension = FileContentType.to_file_extension(content_type)
        good_model: pathlib.Path = None
        for element in self._path:
            if element == '*':
                break
            model_file = (path / element).with_suffix(extension)
            if not model_file.exists():
                break
            path = path / element
            good_model = model_file
        return good_model

    def make_absolute(self, model_dir: pathlib.Path, reference_dir: pathlib.Path):
        """Make the parts absolute from the top model dir."""
        # Match the current relative element path to the model directory and reference directory
        # If the element path is partial and doesn't connect to the top of the model,
        # need to deduce absolute element path from the model_dir and the reference directory
        # that corresponds to the root of the element path

        # if first element is a model type it is already absolute
        if self._path[0] not in const.MODEL_TYPE_LIST:
            rel_path = list(reference_dir.relative_to(model_dir).parts)
            rel_path.extend(self._path)
            self._path = rel_path

    def make_relative(self, model_relative_path: pathlib.Path) -> int:
        """Make the parts relative to the model path."""
        # The element path should currently be absolute
        # The model relative path should be relative to the top leve of the model
        # Change the element path to be relative to the model being loaded
        # Returns 0 on success and 1 on failur
        rel_path_parts = model_relative_path.parts[:-1]
        n_rel_parts = len(rel_path_parts)
        # the element path can't start above the model path
        if n_rel_parts >= len(self._path):
            return 1
        # confirm the leading parts match
        for ii in range(n_rel_parts):
            if rel_path_parts[ii] != self._path[ii]:
                return 1
        # chop off the leading parts of the absolute element path
        self._path = self._path[n_rel_parts:]
        return 0

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

        wrapper_alias is deduced for collection type object

        if wrapper_alias = IGNORE_WRAPPER_ALIAS, then it is ignored and assumed to be json-serializable during to_json()
        """
        # FIXME: There are instances where elem is a list.
        self._elem: OscalBaseModel = elem

        if wrapper_alias == '' and wrapper_alias != self.IGNORE_WRAPPER_ALIAS:
            class_name = elem.__class__.__name__
            if utils.is_collection_field_type(elem):
                class_name = self._get_singular_classname()
                if class_name is None:
                    raise TrestleError(
                        f'wrapper_alias not found for a collection type object: {elem.__class__.__name__}'
                    )
            wrapper_alias = utils.classname_to_alias(class_name, 'json')

        self._wrapper_alias: str = wrapper_alias

    def _get_singular_classname(self) -> str:
        """Get the inner class name for list or dict objects."""
        # this assumes all items in list and all values in dict are same type
        class_name = None
        root = getattr(self._elem, '__root__', None)
        if root is not None:
            type_str = root.__class__.__name__
            if type_str == 'list':
                class_name = self._elem.__root__[0].__class__.__name__
            elif type_str == 'dict':
                class_name = list(self._elem.__root__.values())[0].__class__.__name__
        return class_name

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
               check_parent: bool = True) -> Union[OscalBaseModel, List[OscalBaseModel]]:
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
        yaml = YAML(typ='safe')
        yaml.default_flow_style = False
        from io import StringIO
        string_stream = StringIO()
        yaml.dump(yaml.load(self.to_json(pretty=False)), string_stream)
        yaml_data = string_stream.getvalue()
        string_stream.close()

        return yaml_data

    def to_json(self, pretty: bool = True) -> str:
        """Convert into JSON string."""
        if self._wrapper_alias == self.IGNORE_WRAPPER_ALIAS:
            json_data = self._elem.oscal_serialize_json(pretty=pretty, wrapped=False)

        else:
            # Note before trying to edit this
            # This transient model allows self._elem not be an OscalBaseModel (e.g. a DICT or LIST)
            # typing need to be clarified.
            if isinstance(self._elem, OscalBaseModel):
                json_data = self._elem.oscal_serialize_json(pretty=pretty)
            else:
                dynamic_passer = {}
                dynamic_passer['TransientField'] = (self._elem.__class__, Field(self, alias=self._wrapper_alias))
                wrapper_model = create_model(
                    'TransientModel', __base__=OscalBaseModel, **dynamic_passer
                )  # type: ignore
                wrapped_model = wrapper_model.construct(**{self._wrapper_alias: self._elem})
                json_data = wrapped_model.oscal_serialize_json(pretty=pretty, wrapped=False)
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
