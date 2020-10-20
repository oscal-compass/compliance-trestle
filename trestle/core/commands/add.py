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

from ilcli import Command
import json
import pathlib

import trestle.core.const as const
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.actions import UpdateAction, WriteFileAction, CreatePathAction
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.core.commands import cmd_utils
from trestle.core import utils
from trestle.utils import fs
import trestle.core.err as err

class AddCmd(Command):
    """Add a subcomponent to an existing model."""

    name = 'add'

    def _init_arguments(self):
        self.add_argument(
            '-f',
            '--file',
            help=const.ARG_DESC_FILE + ' to add component/subcomponent to.',
        )
        self.add_argument(
            '-e',
            '--element',
            help=const.ARG_DESC_ELEMENT + ' to add.',
        )

    def _run(self, args):
        """Add an OSCAL component/subcomponent to the specified component."""

        elements = "catalog.metadata.responsible-parties"
        file = "./catalog.json"
        # TODO: what happens during cases like "metadata.responsible-parties.creator"?
        #       what about "metadata.groups."?

        # Get parent model and then load json into parent model
        file_path = pathlib.Path(file)
        parent_model, parent_alias = fs.get_contextual_model_type(file_path.absolute())
        parent_object = parent_model.oscal_read(file_path.absolute())
        parent_element = Element(parent_object, utils.classname_to_alias(parent_model.__name__, 'json'))

        # Get child model
        element_path = ElementPath(elements)
        element_path_list = element_path.get_full_path_parts()

        try:
            child_model = utils.get_target_model(element_path_list, parent_model)
            # Create child element with sample values
            child_object = utils.get_sample_model(child_model)

            if parent_element.get_at(element_path) is not None:
                # The element already exists
                if type(parent_element.get_at(element_path)) is list:
                    child_object = parent_element.get_at(element_path) + child_object
                elif type(parent_element.get_at(element_path)) is dict:
                    child_object = {** parent_element.get_at(element_path), ** child_object}
                else:
                    raise err.TrestleError('Already exists and is not a list or dictionary.')
            
        except Exception as e:
            raise err.TrestleError('Bad element path')

        

        update_action = UpdateAction(sub_element=child_object, dest_element=parent_element, sub_element_path= element_path)
        create_action = CreatePathAction(file_path.absolute())
        write_action = WriteFileAction(file_path.absolute(), parent_element, FileContentType.to_content_type(file_path.suffix))

        add_plan = Plan()
        add_plan.add_action(update_action)
        add_plan.add_action(create_action)
        add_plan.add_action(write_action)
        add_plan.simulate()

        cmd_utils.move_to_trash(file_path)
        
        add_plan.execute()

if __name__ == '__main__':
    import os
    os.chdir('tmp/tmp/catalogs/mycatalog')
    AddCmd()._run(args=None)