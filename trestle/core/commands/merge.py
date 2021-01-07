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
"""Trestle Merge Command."""
import argparse
import logging
import os
from pathlib import Path

from ilcli import Command  # type: ignore

from trestle.core import const, utils
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, RemovePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs, load_distributed
from trestle.utils import log

logger = logging.getLogger(__name__)


class MergeCmd(Command):
    """Merge subcomponents on a trestle model."""

    name = 'merge'

    def _init_arguments(self) -> None:
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=f'{const.ARG_DESC_ELEMENT}(s) to be merged. The last element is merged into the second last element.',
            required=True
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Merge elements into the parent oscal model."""
        log.set_log_level_from_args(args)
        try:
            # Handle multiple element paths: element_paths = args.element.split(',')
            if len(args.element.split(',')) > 1:
                raise TrestleError('Trestle merge -e/-element currently takes only 1 element.')

            plan = self.merge(ElementPath(args.element))
            plan.simulate()
            plan.execute()
        except BaseException as err:
            logger.error(f'Merge failed: {err}')
            return 1
        return 0

    @classmethod
    def merge(cls, element_path: ElementPath) -> Plan:
        """Merge operations.

        It returns a plan for the operation
        """
        element_path_list = element_path.get_full_path_parts()
        target_model_alias = element_path_list[-1]
        """1. Load desination model into a stripped model"""
        # Load destination model
        destination_model_alias = element_path_list[-2]
        # Destination model filename
        destination_model_filename = Path(f'{utils.classname_to_alias(destination_model_alias, "json")}.json')
        destination_model_type, _ = fs.get_stripped_contextual_model(destination_model_filename.absolute())

        destination_model_object = destination_model_type.oscal_read(destination_model_filename)
        """1.5. If target is wildcard, load distributed destrination model and replace destination model."""
        # Handle WILDCARD '*' match. Return plan to load the destination model, with it's distributed attributes
        if target_model_alias == '*':
            merged_model_type, merged_model_alias, merged_model_instance = load_distributed.load_distributed(
                destination_model_filename)
            plan = Plan()
            reset_destination_action = CreatePathAction(destination_model_filename.absolute(), clear_content=True)
            write_destination_action = WriteFileAction(
                destination_model_filename, Element(merged_model_instance), content_type=FileContentType.JSON
            )
            delete_target_action = RemovePathAction(Path(merged_model_alias).absolute())
            plan: Plan = Plan()
            plan.add_action(reset_destination_action)
            plan.add_action(write_destination_action)
            plan.add_action(delete_target_action)
            return plan

        # Get destination model without the target field stripped
        merged_model_type, merged_model_alias = fs.get_stripped_contextual_model(
            destination_model_filename.absolute(),
            aliases_not_to_be_stripped=[target_model_alias])
        """2. Load Target model. Target model could be stripped"""
        try:
            target_model_type = utils.get_target_model(element_path_list, merged_model_type)
        except Exception as e:
            raise TrestleError(
                f'Target model not found. Possibly merge of the elements not allowed at this point. {str(e)}'
            )
        # target_model filename - depends whether destination model is decomposed or not
        if (Path(os.getcwd()) / destination_model_alias).exists():
            target_model_path = f'{os.getcwd()}/{destination_model_alias}/{target_model_alias}'
        else:
            target_model_path = target_model_alias

        # if target model is a file then handle file. If file doesn't exist, handle the directory,
        # but in this case it's a list or a dict collection type
        if (Path(f'{target_model_path}.json')).exists():
            target_model_filename = Path(f'{target_model_path}.json')
            _, _, target_model_object = load_distributed.load_distributed(target_model_filename)
        else:
            target_model_filename = Path(target_model_path)
            collection_type = utils.get_origin(target_model_type)
            _, _, target_model_object = load_distributed.load_distributed(target_model_filename, collection_type)

        if hasattr(target_model_object, '__dict__') and '__root__' in target_model_object.__dict__:
            target_model_object = target_model_object.__dict__['__root__']
        """3. Insert target model into destination model."""
        merged_dict = destination_model_object.__dict__
        merged_dict[target_model_alias] = target_model_object
        merged_model_object = merged_model_type(**merged_dict)  # type: ignore
        merged_destination_element = Element(merged_model_object)
        """4. Create action  plan"""
        reset_destination_action = CreatePathAction(destination_model_filename.absolute(), clear_content=True)
        write_destination_action = WriteFileAction(
            destination_model_filename, merged_destination_element, content_type=FileContentType.JSON
        )
        delete_target_action = RemovePathAction(target_model_filename)

        plan: Plan = Plan()
        plan.add_action(reset_destination_action)
        plan.add_action(write_destination_action)
        plan.add_action(delete_target_action)

        # TODO: Destination model directory is empty or already merged? Then clean up.

        return plan
