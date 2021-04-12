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
"""Trestle Add Command."""
import argparse
import logging
import pathlib
from typing import List

import trestle.core.const as const
import trestle.core.err as err
import trestle.core.generators as gens
from trestle.core import utils
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.models.actions import CreatePathAction, UpdateAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log

logger = logging.getLogger(__name__)


class AddCmd(CommandPlusDocs):
    """Add a subcomponent to an existing model."""

    name = 'add'

    def _init_arguments(self) -> None:
        self.add_argument(
            f'-{const.ARG_FILE_SHORT}',
            f'--{const.ARG_FILE}',
            help=const.ARG_DESC_FILE + ' to add component/subcomponent to.',
            required=True
        )
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=const.ARG_DESC_ELEMENT + ' to add.',
            required=True
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Add an OSCAL component/subcomponent to the specified component.

        This method takes input a filename and a list of comma-seperated element path. Element paths are field aliases.
        The method first finds the parent model from the file and loads the file into the model.
        Then the method executes 'add' for each of the element paths specified.
        """
        log.set_log_level_from_args(args)
        try:
            args_dict = args.__dict__

            file_path = pathlib.Path(args_dict[const.ARG_FILE])

            # Get parent model and then load json into parent model
            parent_model, parent_alias = fs.get_stripped_contextual_model(file_path.resolve())
            parent_object = parent_model.oscal_read(file_path.resolve())
            # FIXME : handle YAML files after detecting file type
            parent_element = Element(parent_object, utils.classname_to_alias(parent_model.__name__, 'json'))

            add_plan = Plan()

            # Do _add for each element_path specified in args
            element_paths: List[str] = args_dict[const.ARG_ELEMENT].split(',')
            for elm_path_str in element_paths:
                element_path = ElementPath(elm_path_str)
                update_action, parent_element = self.add(element_path, parent_model, parent_element)
                add_plan.add_action(update_action)

            create_action = CreatePathAction(file_path.resolve(), True)
            write_action = WriteFileAction(
                file_path.resolve(), parent_element, FileContentType.to_content_type(file_path.suffix)
            )

            add_plan.add_action(create_action)
            add_plan.add_action(write_action)

            add_plan.simulate()
            add_plan.execute()

        except BaseException as err:
            logger.error(f'Add failed: {err}')
            return 1
        return 0

    @classmethod
    def add(cls, element_path, parent_model, parent_element):
        """For a element_path, add a child model to the parent_element of a given parent_model.

        First we find the child model at the specified element path and instantiate it with default values.
        Then we check if there's already existing element at that path, in which case we append the child model
        to the existing list of dict.
        Then we set up an action plan to update the model (specified by file_path) in memory, create a file
        at the same location and write the file.
        We update the parent_element to prepare for next adds in the chain
        """
        element_path_list = element_path.get_full_path_parts()
        if '*' in element_path_list:
            raise err.TrestleError('trestle add does not support Wildcard element path.')
        # Get child model
        try:
            child_model = utils.get_target_model(element_path_list, parent_model)
            # Create child element with sample values
            child_object = gens.generate_sample_model(child_model)

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
