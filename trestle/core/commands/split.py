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
"""Trestle Split Command."""
import pathlib
from typing import List

from ilcli import Command

from trestle.core import const
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs

from . import cmd_utils


class SplitCmd(Command):
    """Split subcomponents on a trestle model."""

    name = 'split'

    def _init_arguments(self):
        self.add_argument(
            f'-{const.ARG_FILE_SHORT}',
            f'--{const.ARG_FILE}',
            help=const.ARG_DESC_FILE + ' to split.',
        )
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=const.ARG_DESC_ELEMENT + ' to split.',
        )

    def _run(self, args):
        """Split an OSCAL file into elements."""
        # get the Model
        args = args.__dict__
        if args[const.ARG_FILE] is None:
            raise TrestleError(f'Argument "-{const.ARG_FILE_SHORT}" is required')

        file_path = pathlib.Path(args[const.ARG_FILE])
        content_type = FileContentType.to_content_type(file_path.suffix)

        # find the base directory of the file
        file_absolute_path = pathlib.Path(file_path.absolute())
        base_dir = file_absolute_path.parent

        model_type, model_alias = fs.get_contextual_model_type(file_absolute_path)
        model: OscalBaseModel = model_type.oscal_read(file_path)

        element_paths: List[ElementPath] = cmd_utils.parse_element_args(args[const.ARG_ELEMENT].split(','))

        split_plan = self.split_model(model, element_paths, base_dir, content_type)

        # Simulate the plan
        # if it fails, it would through errors and get out of this command
        split_plan.simulate()

        # If we are here then simulation passed
        # so move the original file to the trash
        cmd_utils.move_to_trash(file_path)

        # execute the plan
        split_plan.execute()

    @classmethod
    def split_model(
        cls,
        model: OscalBaseModel,
        element_paths: List[ElementPath],
        base_dir: pathlib.Path,
        content_type: FileContentType
    ) -> Plan:
        """Split the model at the provided element paths.

        It returns a plan for the operation
        """
        element = Element(model)
        split_plan = Plan()
        stripped_field_alias = []
        file_ext = FileContentType.to_file_extension(content_type)

        # add actions to the plan for each sub model specified by the element paths
        for element_path in element_paths:
            sub_models = element.get_at(element_path)  # we call is sub_models as in plural, but it can be just one
            if sub_models is None:
                continue

            # if wildard is present in the element_path, create separate file for each sub item
            if element_path.get_last() == ElementPath.WILDCARD:
                sub_model_dir = base_dir / element_path.get_element_name()
                if isinstance(sub_models, list):
                    for i, sub_model_item in enumerate(sub_models):
                        model_type = utils.classname_to_alias(type(sub_model_item).__name__, 'json')
                        file_index = str(i).zfill(4)
                        file_name = f'{file_index}{const.IDX_SEP}{model_type}{file_ext}'

                        sub_model_file = sub_model_dir / file_name
                        split_plan.add_action(CreatePathAction(sub_model_file))
                        split_plan.add_action(WriteFileAction(sub_model_file, Element(sub_model_item), content_type))
                elif isinstance(sub_models, dict):
                    for key in sub_models:
                        sub_model_item = sub_models[key]
                        model_type = utils.classname_to_alias(type(sub_model_item).__name__, 'json')
                        file_name = f'{key}{const.IDX_SEP}{model_type}{file_ext}'
                        sub_model_file = sub_model_dir / file_name
                        split_plan.add_action(CreatePathAction(sub_model_file))
                        split_plan.add_action(WriteFileAction(sub_model_file, Element(sub_model_item), content_type))
                else:
                    raise TrestleError(f'Sub element at {element_path} is not of type list or dict')
            else:
                sub_model_file = base_dir / element_path.to_file_path(content_type)
                split_plan.add_action(CreatePathAction(sub_model_file))
                split_plan.add_action(WriteFileAction(sub_model_file, Element(sub_models), content_type))

            stripped_field_alias.append(element_path.get_element_name())

        # WriteAction for the stripped root
        stripped_root = model.stripped_instance(stripped_field_alias)
        root_file = base_dir / element_paths[0].to_root_path(content_type)
        split_plan.add_action(CreatePathAction(root_file))
        split_plan.add_action(WriteFileAction(root_file, Element(stripped_root), content_type))

        return split_plan
