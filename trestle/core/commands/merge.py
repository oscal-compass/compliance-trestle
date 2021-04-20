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

from trestle.core import const, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, RemovePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs, load_distributed
from trestle.utils import log

logger = logging.getLogger(__name__)


class MergeCmd(CommandPlusDocs):
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

        # remove any quotes passed in as on windows platforms
        elements_clean = args.element.strip("'")

        element_paths = elements_clean.split(',')
        logger.debug(f'merge _run element paths {element_paths}')
        try:
            for element_path in element_paths:
                logger.debug(f'merge {element_path}')
                plan = self.merge(ElementPath(element_path))
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
        logger.debug(f'merge element path list: {element_path_list} target model alias {target_model_alias}')
        """1. Load desination model into a stripped model"""
        # Load destination model
        destination_model_alias = element_path_list[-2]
        # Destination model filetype
        try:
            logger.debug(f'merge destination model alias: {destination_model_alias}')
            logger.debug('merge getting contextual file type from cwd')
            file_type = fs.get_contextual_file_type(Path(os.getcwd()))
            logger.debug(f'contextual file type is {file_type}')
        except Exception as e:
            raise TrestleError(str(e))
        file_ext = FileContentType.to_file_extension(file_type)
        # Destination model filename
        destination_model_filename = Path(f'{utils.classname_to_alias(destination_model_alias, "json")}{file_ext}')
        destination_model_filename = destination_model_filename.resolve()
        logger.debug(f'destination model filename is {destination_model_filename}')
        destination_model_type, _ = fs.get_stripped_contextual_model(destination_model_filename)

        # if there is no .json file then there is no destination model object at this point, so create empty one
        destination_model_object: OscalBaseModel = None
        if destination_model_filename.exists():
            logger.debug('dest filename exists so read it')
            destination_model_object = destination_model_type.oscal_read(destination_model_filename)
        else:
            logger.debug('dest filename does not exist')
        """1.5. If target is wildcard, load distributed destrination model and replace destination model."""
        # Handle WILDCARD '*' match. Return plan to load the destination model, with it's distributed attributes
        if target_model_alias == '*':
            logger.debug('handle target model alias wildcard')
            collection_type = None
            if destination_model_type.is_collection_container():
                collection_type = destination_model_type.get_collection_type()

            merged_model_type, merged_model_alias, merged_model_instance = load_distributed.load_distributed(
                destination_model_filename, collection_type)
            plan = Plan()
            reset_destination_action = CreatePathAction(destination_model_filename.resolve(), clear_content=True)
            wrapper_alias = destination_model_alias
            write_destination_action = WriteFileAction(
                destination_model_filename, Element(merged_model_instance, wrapper_alias), content_type=file_type
            )
            delete_target_action = RemovePathAction(Path(destination_model_alias).resolve())
            plan: Plan = Plan()
            plan.add_action(reset_destination_action)
            plan.add_action(write_destination_action)
            plan.add_action(delete_target_action)
            return plan

        logger.debug(f'get dest model with fields stripped: {target_model_alias}')
        # Get destination model without the target field stripped
        merged_model_type, merged_model_alias = fs.get_stripped_contextual_model(
            destination_model_filename,
            aliases_not_to_be_stripped=[target_model_alias])
        """2. Load Target model. Target model could be stripped"""
        try:
            target_model_type = utils.get_target_model(element_path_list, merged_model_type)
        except Exception as e:
            logger.debug(f'target model not found, element path list {element_path_list} type {merged_model_type}')
            raise TrestleError(
                f'Target model not found. Possibly merge of the elements not allowed at this point. {str(e)}'
            )
        target_model_path = Path(os.getcwd()) / destination_model_alias
        logger.debug(
            f'look for target model path {target_model_path} at dest alias {destination_model_alias} rel to cwd'
        )
        # target_model filename - depends whether destination model is decomposed or not
        if target_model_path.exists():
            logger.debug(
                f'target model path does exist so target path is subdir with target alias {target_model_alias}'
            )
            target_model_path = target_model_path / target_model_alias
        else:
            logger.debug(f'target model filename does not exist so target path is target alias {target_model_alias}')
            target_model_path = target_model_path / target_model_alias  # FIXME this is same as above
        logger.debug(f'final target model path is {target_model_path}')

        # if target model is a file then handle file. If file doesn't exist, handle the directory,
        # but in this case it's a list or a dict collection type
        target_model_filename = target_model_path.with_suffix(file_ext)
        if target_model_filename.exists():
            logger.debug(f'target model path with extension does exist so load distrib {target_model_filename}')
            _, _, target_model_object = load_distributed.load_distributed(target_model_filename)
        else:
            target_model_filename = Path(target_model_path)
            logger.debug(f'target model path plus extension does not exist so load distrib {target_model_filename}')
            logger.debug(f'get collection type for model type {target_model_type}')
            collection_type = utils.get_origin(target_model_type)
            logger.debug(f'load {target_model_filename} as collection type {collection_type}')
            _, _, target_model_object = load_distributed.load_distributed(target_model_filename, collection_type)

        if hasattr(target_model_object, '__dict__') and '__root__' in target_model_object.__dict__:
            logger.debug('loaded object has dict and root so set target model object to root contents')
            target_model_object = target_model_object.__dict__['__root__']
        else:
            logger.debug('loaded object has no dict and root so use it as-is')
        """3. Insert target model into destination model."""
        merged_dict = {}
        if destination_model_object is not None:
            merged_dict = destination_model_object.__dict__
        merged_dict[target_model_alias] = target_model_object
        merged_model_object = merged_model_type(**merged_dict)  # type: ignore
        merged_destination_element = Element(merged_model_object)
        """4. Create action  plan"""
        logger.debug(f'create path action clear content: {destination_model_filename}')
        reset_destination_action = CreatePathAction(destination_model_filename, clear_content=True)
        logger.debug(f'write file action {destination_model_filename}')
        write_destination_action = WriteFileAction(
            destination_model_filename, merged_destination_element, content_type=file_type
        )
        # FIXME this will delete metadata.json but it will leave metadata/roles/roles.*
        # need to clean up all lower dirs
        logger.debug(f'remove path action {target_model_filename}')
        delete_target_action = RemovePathAction(target_model_filename)

        plan: Plan = Plan()
        plan.add_action(reset_destination_action)
        plan.add_action(write_destination_action)
        plan.add_action(delete_target_action)

        # TODO: Destination model directory is empty or already merged? Then clean up.

        return plan
