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
import trestle.core.const as const
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.actions import UpdateAction
from trestle.core.models.plans import Plan
from trestle.core.commands import cmd_utils

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
        element_path = ElementPath()

        # get parent model type from args.file . trestle.core.parser.root_key
        # then load the data into parent model using trestle.core.parser.to_full_model_name() and create parent element
        parent_element = Element()
        # new element path is args.element
        # check parent element allows the path args.element
        # 
        sub_element = Element()

        update_action = UpdateAction(sub_element=sub_element, dest_element=parent_element, sub_element_path= element_path)

        add_plan = Plan()
        add_plan.add_action(
            UpdateAction(
                pathlib.Path.joinpath(base_dir, 'metadata.json'), Element(sample_target.metadata), content_type
            )
        )

if __name__ == '__main__':
    import os
    os.chdir('tmp/tmp/catalogs')
    AddCmd()._run(args=None)