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
import argparse
import logging
import pathlib
from typing import List, Tuple, Type

import trestle.core.const as const
import trestle.core.err as err
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, RemoveAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log

logger = logging.getLogger(__name__)


class RemoveCmd(CommandPlusDocs):
    """Remove a subcomponent to an existing model."""

    name = 'remove'

    def _init_arguments(self) -> None:
        self.add_argument(
            f'-{const.ARG_FILE_SHORT}',
            f'--{const.ARG_FILE}',
            help=const.ARG_DESC_FILE + ' to remove component/subcomponent to.',
            required=True
        )
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=const.ARG_DESC_ELEMENT + ' to remove.',
            required=True
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Remove an OSCAL component/subcomponent to the specified component.

        This method takes input a filename and a list of comma-seperated element path. Element paths are field aliases.
        The method first finds the parent model from the file and loads the file into the model.
        Then the method executes 'remove' for each of the element paths specified.
        """
        log.set_log_level_from_args(args)
        args_dict = args.__dict__

        file_path = pathlib.Path(args_dict[const.ARG_FILE])

        # Get parent model and then load json into parent model
        try:
            parent_model, parent_alias = fs.get_contextual_model_type(file_path.resolve())
        except Exception as err:
            logger.debug(f'fs.get_contextual_model_type() failed: {err}')
            logger.error(f'Remove failed (fs.get_contextual_model_type()): {err}')
            return 1

        try:
            parent_object = parent_model.oscal_read(file_path.resolve())
        except Exception as err:
            logger.debug(f'parent_model.oscal_read() failed: {err}')
            logger.error(f'Remove failed (parent_model.oscal_read()): {err}')
            return 1

        parent_element = Element(parent_object, utils.classname_to_alias(parent_model.__name__, 'json'))

        add_plan = Plan()

        # Do _remove for each element_path specified in args
        element_paths: List[str] = str(args_dict[const.ARG_ELEMENT]).split(',')
        for elm_path_str in element_paths:
            element_path = ElementPath(elm_path_str)
            try:
                remove_action, parent_element = self.remove(element_path, parent_model, parent_element)
            except TrestleError as err:
                logger.debug(f'self.remove() failed: {err}')
                logger.error(f'Remove failed (self.remove()): {err}')
                return 1
            add_plan.add_action(remove_action)

        create_action = CreatePathAction(file_path.resolve(), True)
        write_action = WriteFileAction(
            file_path.resolve(), parent_element, FileContentType.to_content_type(file_path.suffix)
        )
        add_plan.add_action(remove_action)
        add_plan.add_action(create_action)
        add_plan.add_action(write_action)

        try:
            add_plan.simulate()
        except TrestleError as err:
            logger.debug(f'Remove failed at simulate(): {err}')
            logger.error(f'Remove failed (simulate()): {err}')
            return 1

        try:
            add_plan.execute()
        except TrestleError as err:
            logger.debug(f'Remove failed at execute(): {err}')
            logger.error(f'Remove failed (execute()): {err}')
            return 1

        return 0

    @classmethod
    def remove(cls, element_path: ElementPath, parent_model: Type[OscalBaseModel],
               parent_element: Element) -> Tuple[RemoveAction, Element]:
        """For the element_path, remove a model from the parent_element of a given parent_model.

        First we check if there is an existing element at that path
        If not, we complain.
        Then we set up an action plan to update the model (specified by file_path) in memory,
        return the action and return the parent_element.

        LIMITATIONS:
        1. This does not remove elements of a list or dict. Instead, the entire list or dict is removed.
        2. This cannot remove arbitrarily named elements that are not specified in the schema.
        For example, "responsible-parties" contains named elements, e.g., "organisation". The tool will not
        remove the "organisation" as it is not in the schema, but one can remove its elements, e.g., "party-uuids".
        """
        element_path_list = element_path.get_full_path_parts()
        if '*' in element_path_list:
            raise err.TrestleError('trestle remove does not support Wildcard element path.')

        deleting_element = parent_element.get_at(element_path)

        if deleting_element is not None:
            # The element already exists
            if type(deleting_element) is list:
                logger.warning(
                    'Warning: trestle remove does not support removing elements of a list: '
                    'this removes the entire list'
                )
            elif type(deleting_element) is dict:
                logger.warning(
                    'Warning: trestle remove does not support removing dict elements: '
                    'this removes the entire dict element'
                )
        else:
            raise err.TrestleError(f'Bad element path: {str(element_path)}')

        remove_action = RemoveAction(parent_element, element_path)

        return remove_action, parent_element
