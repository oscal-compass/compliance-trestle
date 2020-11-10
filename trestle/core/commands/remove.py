# -*- mode:python; coding:utf-8 -*-

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
"""Trestle Remove Command."""

import pathlib
import warnings

from ilcli import Command  # type: ignore

import trestle.core.const as const
import trestle.core.err as err
from trestle.core import utils
from trestle.core.models.actions import CreatePathAction, RemoveAction, RemovePathAction, UpdateAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs


class RemoveCmd(Command):
    """Remove a subcomponent to an existing model."""

    name = 'remove'

    def _init_arguments(self):
        self.add_argument(
            f'-{const.ARG_FILE_SHORT}',
            f'--{const.ARG_FILE}',
            help=const.ARG_DESC_FILE + ' to remove component/subcomponent to.',
        )
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=const.ARG_DESC_ELEMENT + ' to remove.',
        )

    def _run(self, args):
        """Remove an OSCAL component/subcomponent to the specified component.

        This method takes input a filename and a list of comma-seperated element path. Element paths are field aliases.
        The method first finds the parent model from the file and loads the file into the model.
        Then the method executes 'remove' for each of the element paths specified.
        """
        args = args.__dict__
        if args[const.ARG_FILE] is None:
            raise err.TrestleError(f'Argument "-{const.ARG_FILE_SHORT}" is required')
        if args[const.ARG_ELEMENT] is None:
            raise err.TrestleError(f'Argument "-{const.ARG_ELEMENT}" is required')

        file_path = pathlib.Path(args[const.ARG_FILE])

        # Get parent model and then load json into parent model
        parent_model, parent_alias = fs.get_contextual_model_type(file_path.absolute())
        parent_object = parent_model.oscal_read(file_path.absolute())
        parent_element = Element(parent_object, utils.classname_to_alias(parent_model.__name__, 'json'))

        # Do _remove for each element_path specified in args
        element_paths: list[str] = args[const.ARG_ELEMENT].split(',')
        for elm_path_str in element_paths:
            element_path = ElementPath(elm_path_str)
            self.remove(file_path, element_path, parent_model, parent_element)

    @classmethod
    def remove(cls, file_path, element_path, parent_model, parent_element):
        """For a file_path and, at the element_path, remove a model from the parent_element of a given parent_model.

        First we check if there is an existing element at that path
        If not, we complain.
        Then we set up an action plan to update the model (specified by file_path) in memory, create a file
        at the same location and write the file.

        LIMITATIONS:
        1. This does not remove elements of a list or dict. Instead, the entire list or dict is removed.
        2. This cannot remove arbitrarily named elements that are not specified in the schema.
        For example, "responsible-parties" contains named elements, e.g., "organisation". The tool will not
        remove the "organisation" as it is not in the schema, but one can remove its elements, e.g., "party-uuids".
        """
        element_path_list = element_path.get_full_path_parts()
        if '*' in element_path_list:
            raise err.TrestleError('trestle add does not support Wildcard element path.')

        try:
            deleting_element = parent_element.get_at(element_path)

            if deleting_element is not None:
                # The element already exists
                if type(deleting_element) is list:
                    pass
                    warnings.warn(
                        'trestle remove does not support removing elements of a list -- this removes the entire list',
                        Warning
                    )
                elif type(deleting_element) is dict:
                    pass
                    warnings.warn(
                        'trestle remove does not support removing dict elements -- this removes the entire dict',
                        Warning
                    )
            else:
                raise err.TrestleError(f'Bad element path. {str(element_path)}')

        except Exception as e:
            raise err.TrestleError(f'Bad element path. {str(e)}')

        update_action = UpdateAction(
            sub_element=deleting_element, dest_element=parent_element, sub_element_path=element_path
        )
        remove_path_action = RemovePathAction(file_path.absolute())
        remove_action = RemoveAction(parent_element, element_path)
        create_action = CreatePathAction(file_path.absolute(), True)
        write_action = WriteFileAction(
            file_path.absolute(), parent_element, FileContentType.to_content_type(file_path.suffix)
        )

        add_plan = Plan()
        add_plan.add_action(update_action)
        add_plan.add_action(remove_action)
        add_plan.add_action(remove_path_action)
        add_plan.add_action(create_action)
        add_plan.add_action(write_action)
        add_plan.simulate()

        add_plan.execute()
