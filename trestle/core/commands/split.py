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
from typing import Dict, List

from ilcli import Command

from trestle.core import const
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.actions import Action, CreatePathAction, WriteFileAction
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

        # FIXME: Handle list/dicts
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
    def prepare_sub_model_split_actions(
        cls,
        sub_model_item: OscalBaseModel,
        sub_model_dir: pathlib.Path,
        file_prefix: str,
        content_type: FileContentType
    ) -> List[Action]:
        """Create split actions of sub model."""
        actions: List[Action] = []
        file_ext = FileContentType.to_file_extension(content_type)
        model_type = utils.classname_to_alias(type(sub_model_item).__name__, 'json')
        file_name = f'{file_prefix}{const.IDX_SEP}{model_type}{file_ext}'
        sub_model_file = sub_model_dir / file_name
        actions.append(CreatePathAction(sub_model_file))
        actions.append(WriteFileAction(sub_model_file, Element(sub_model_item), content_type))
        return actions

    @classmethod
    def get_sub_model_dir(cls, base_dir: pathlib.Path, sub_model: OscalBaseModel, dir_prefix: str) -> pathlib.Path:
        """Get the directory path for the given model."""
        model_type = utils.classname_to_alias(type(sub_model).__name__, 'json')
        dir_name = f'{dir_prefix}{const.IDX_SEP}{model_type}'
        sub_model_dir = base_dir / dir_name

        return sub_model_dir

    @classmethod
    def split_model(
        cls,
        model: OscalBaseModel,
        element_paths: List[ElementPath],
        base_dir: pathlib.Path,
        content_type: FileContentType,
        cur_path_index: int = 0,
        split_plan: Plan = None
    ) -> Plan:
        """Split the model at the provided element paths.

        It returns a plan for the operation
        """
        # For clarity of the code and to be able to follow the logi, let's assume the split command is as below:
        # trestle split -f target.yaml -e target-definition.targets.*.target-control-implementations.*

        # initialize plan
        if split_plan is None:
            split_plan = Plan()

        # if there are no more element_paths, return the current plan
        if cur_path_index >= len(element_paths):
            return split_plan

        # initialize local variables
        element = Element(model)
        stripped_field_alias = []
        file_ext = FileContentType.to_file_extension(content_type)

        # get the sub_model specified by the element_path of this round
        element_path = element_paths[cur_path_index]
        sub_models = element.get_at(element_path)  # we call is sub_models as in plural, but it can be just one
        if sub_models is None:
            return split_plan

        # if wildard is present in the element_path, create separate file for each sub item
        # for example, in the first round we get the `targets` using the path `target-definition.targets.*`
        # so, now we need to split each of the target recursively. Note that target is an instance of dict
        if element_path.get_last() == ElementPath.WILDCARD:
            # create dir for all sub model items. e.g. `targets` or `groups`
            sub_models_dir = base_dir / element_path.to_file_path()

            # write stripped sub models file in the directory
            # e.g. targets/targets.yaml
            element_name = element_path.get_element_name()
            base_element = cmd_utils.get_dir_base_file_element(sub_models, element_name)
            dir_base_file = sub_models_dir / f'{element_name}{file_ext}'
            split_plan.add_action(CreatePathAction(dir_base_file))
            split_plan.add_action(WriteFileAction(dir_base_file, base_element, content_type))

            # extract sub-models into a dict with appropriate prefix
            sub_model_items: Dict[str, OscalBaseModel] = {}
            if isinstance(sub_models, list):
                for i, sub_model_item in enumerate(sub_models):
                    # e.g. `groups/0000_groups/`
                    prefix = str(i).zfill(4)
                    sub_model_items[prefix] = sub_model_item
            elif isinstance(sub_models, dict):
                # prefix is the key of the dict
                sub_model_items = sub_models
            else:
                # unexpected sub model type for multi-level split with wildcard
                raise TrestleError(f'Sub element at {element_path} is not of type list or dict for further split')

            # process list sub model items
            for key in sub_model_items:
                prefix = key
                sub_model_item = sub_model_items[key]

                # recursively split the sub-model if there are more element paths to traverse
                # e.g. split target.target-control-implementations.*
                if cur_path_index + 1 < len(element_paths):
                    # prepare individual directory for each sub-model
                    # e.g. `targets/<UUID>__target/`
                    sub_model_dir = cls.get_sub_model_dir(sub_models_dir, sub_model_item, prefix)

                    sub_model_plan = cls.split_model(
                        sub_model_item, element_paths, sub_model_dir, content_type, cur_path_index + 1
                    )

                    sub_model_actions = sub_model_plan.get_actions()

                else:
                    sub_model_actions = cls.prepare_sub_model_split_actions(
                        sub_model_item, sub_models_dir, prefix, content_type
                    )

                split_plan.add_actions(sub_model_actions)
        else:
            sub_model_file = base_dir / element_path.to_file_path(content_type)
            split_plan.add_action(CreatePathAction(sub_model_file))
            split_plan.add_action(WriteFileAction(sub_model_file, Element(sub_models), content_type))

        # WriteAction for the stripped root model object
        stripped_field_alias.append(element_path.get_element_name())
        stripped_root = model.stripped_instance(stripped_fields_aliases=stripped_field_alias)
        root_file = base_dir / element_path.to_root_path(content_type)
        split_plan.add_action(CreatePathAction(root_file))
        split_plan.add_action(WriteFileAction(root_file, Element(stripped_root), content_type))

        return cls.split_model(model, element_paths, base_dir, content_type, cur_path_index + 1, split_plan)
