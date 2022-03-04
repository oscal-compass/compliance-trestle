# -*- mode:python; coding:utf-8 -*-

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
"""Trestle Add Command."""
import argparse
import logging
import pathlib
from typing import List

import trestle.common.err as err
import trestle.core.generators as gens
from trestle.common.model_utils import ModelUtils
from trestle.common.str_utils import AliasMode, classname_to_alias
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.actions import CreatePathAction, UpdateAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan

logger = logging.getLogger(__name__)


class Add():
    """
    Class supporting Add of an OSCAL object to a provided file based on element path.

    Examples of element paths:
        catalog.metadata
        catalog.controls.control
        assessment-results.results.

    The method first finds the parent model from the file and loads the file into the model.
    Then the method executes 'add' for each of the element paths specified.
    Add was originally its own command but has been incorporated into the Create command.
    """

    def add_from_args(self, args: argparse.Namespace) -> int:
        """Parse args for add element to file."""
        file_path = pathlib.Path(args.file).resolve()

        # Get parent model and then load json into parent model
        parent_model, _ = ModelUtils.get_stripped_model_type(file_path, args.trestle_root)
        parent_object = parent_model.oscal_read(file_path)
        parent_element = Element(parent_object, classname_to_alias(parent_model.__name__, AliasMode.JSON))

        add_plan = Plan()
        # Do _add for each element_path specified in args
        element_paths: List[str] = args.element.split(',')
        for elm_path_str in element_paths:
            element_path = ElementPath(elm_path_str)
            update_action, parent_element = self.add(element_path, parent_element, args.include_optional_fields)
            add_plan.add_action(update_action)

        create_action = CreatePathAction(file_path, True)
        # this will output json or yaml based on type of input file
        write_action = WriteFileAction(file_path, parent_element, FileContentType.to_content_type(file_path.suffix))

        add_plan.add_action(create_action)
        add_plan.add_action(write_action)

        add_plan.execute()
        return CmdReturnCodes.SUCCESS.value

    @staticmethod
    def add(element_path: ElementPath, parent_element: Element, include_optional: bool) -> None:
        """For a element_path, add a child model to the parent_element of a given parent_model.

        Args:
            element_path: element path of the item to create within the model
            parent_element: the parent element that will host the created element
            include_optional: whether to create optional attributes in the created element

        Notes:
            First we find the child model at the specified element path and instantiate it with default values.
            Then we check if there's already existing element at that path, in which case we append the child model
            to the existing list of dict.
            Then we set up an action plan to update the model (specified by file_path) in memory, create a file
            at the same location and write the file.
            We update the parent_element to prepare for next adds in the chain
        """
        if '*' in element_path.get_full_path_parts():
            raise err.TrestleError('trestle add does not support Wildcard element path.')
        # Get child model
        try:
            child_model = element_path.get_type(type(parent_element.get()))

            # Create child element with sample values
            child_object = gens.generate_sample_model(child_model, include_optional=include_optional)

            if parent_element.get_at(element_path) is not None:
                # The element already exists
                if type(parent_element.get_at(element_path)) is list:
                    child_object = parent_element.get_at(element_path) + child_object
                elif type(parent_element.get_at(element_path)) is dict:
                    child_object = {**parent_element.get_at(element_path), **child_object}
                else:
                    raise err.TrestleError('Already exists and is not a list or dictionary.')

        except Exception as e:
            raise err.TrestleError(f'Bad element path. {str(e)}')

        update_action = UpdateAction(
            sub_element=child_object, dest_element=parent_element, sub_element_path=element_path
        )
        parent_element = parent_element.set_at(element_path, child_object)

        return update_action, parent_element
