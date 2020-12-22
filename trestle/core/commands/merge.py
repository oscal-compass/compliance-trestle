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

import os
from pathlib import Path
from typing import Set, Type

from ilcli import Command  # type: ignore

import trestle.core.err as err
from trestle.core import const, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.models.actions import CreatePathAction, RemovePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs, load_distributed
from trestle.utils import log


class MergeCmd(Command):
    """Merge subcomponents on a trestle model."""

    name = 'merge'

    def _init_arguments(self):
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=f'{const.ARG_DESC_ELEMENT}(s) to be merged.',
        )

        self.add_argument(
            '-l',
            '--list-available-elements',
            action='store_true',
            help='Comma-separated list of paths of properties that can be merged.'
        )

    def _run(self, args) -> None:
        """Merge elements into the parent oscal model."""
        log.set_log_level_from_args(args)
        if args.list_available_elements:
            self._list_available_elements()
        elif args.element:
            # FIXME: Handle multiple element paths: element_paths = args.element.split(',')
            plan = self.merge(ElementPath(args.element))

            plan.simulate()
            plan.execute()

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
            # TODO : This will work, if RemovePathAction can take
            # directyory delete_target_action = RemovePathAction(Path(merged_model_alias))
            plan: Plan = Plan()
            plan.add_action(reset_destination_action)
            plan.add_action(write_destination_action)
            return plan

        # Get destination model without the target field stripped
        merged_model_type, merged_model_alias = fs.get_stripped_contextual_model(
            destination_model_filename.absolute(),
            aliases_not_to_be_stripped=[target_model_alias])
        """2. Load Target model. Target model could be stripped"""
        try:
            target_model_type = utils.get_target_model(element_path_list, merged_model_type)
        except Exception as e:
            raise err.TrestleError(
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
            collection_type = target_model_type.__origin__
            _, _, target_model_object = load_distributed.load_distributed(target_model_filename, collection_type)

        if hasattr(target_model_object, '__dict__') and '__root__' in target_model_object.__dict__:
            target_model_object = target_model_object.__dict__['__root__']
        """3. Insert target model into destination model."""
        merged_dict = destination_model_object.__dict__
        merged_dict[target_model_alias] = target_model_object
        merged_model_object = merged_model_type(**merged_dict)
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

    def _list_available_elements(self) -> None:
        """List element paths that can be merged from the current context."""
        current_model, current_alias = fs.get_contextual_model_type(Path.cwd())

        current_filename = f'{current_alias}.json'

        self._list_options_for_merge(Path.cwd(), current_alias, current_model, current_filename)

    def _list_options_for_merge(
        self,
        cwd: Path,
        current_alias: str,
        current_model: Type[OscalBaseModel],
        current_filename: str,
        initial_path: Path = None,
        visited_elements: Set[str] = None
    ):
        """List paths that can be used in the -e option for the merge operation."""
        if initial_path is None:
            initial_path = cwd
        if visited_elements is None:
            visited_elements = set()

        path_sep = '.' if current_alias else ''

        # List options for merge
        if not utils.is_collection_field_type(current_model):

            malias = current_alias.split('.')[-1]
            if cwd.is_dir() and malias != fs.extract_alias(cwd):
                split_subdir = cwd / malias
            else:
                split_subdir = cwd.parent / cwd.with_suffix('').name

            # Go through each file or subdirectory in the cwd
            fields_by_alias = current_model.alias_to_field_map()
            for filepath in Path.iterdir(split_subdir):
                if filepath.is_file() and cwd == initial_path:
                    continue

                alias = filepath.with_suffix('').name
                if alias in fields_by_alias:
                    visited_element = f'{current_alias}{path_sep}{alias}'
                    if visited_element not in visited_elements:
                        visited_elements.add(visited_element)
                        self.out(f"{visited_element} (merges \'{filepath.name}\' into \'{cwd / current_filename}\')")

                    # If it is subdirectory, call this function recursively
                    if Path.is_dir(filepath):
                        self._list_options_for_merge(
                            filepath,
                            f'{current_alias}{path_sep}{alias}',
                            fields_by_alias[alias].outer_type_,
                            f'{alias}.json',
                            initial_path=initial_path,
                            visited_elements=visited_elements
                        )
        else:
            # List merge option for collection at the base level
            destination_dir = cwd.parent if len(initial_path.parts) < len(cwd.parts) else cwd
            destination = destination_dir / current_filename
            visited_element = f'{current_alias}{path_sep}{const.ELEMENT_WILDCARD}'
            if visited_element not in visited_elements:
                visited_elements.add(visited_element)
                self.out(f"{visited_element} (merges all files/subdirectories under {cwd} into \'{destination}\')")

            # Go through each subdirectory in the collection and look for nested merge options
            singular_alias = fs.get_singular_alias(current_alias, False)
            singular_model = utils.get_inner_type(current_model)
            for filename in sorted(cwd.glob(f'*{const.IDX_SEP}{singular_alias}')):
                if Path.is_dir(filename):
                    self._list_options_for_merge(
                        filename,  # f'{current_alias}{path_sep}*',
                        f'{current_alias}{path_sep}{singular_alias}',
                        singular_model,
                        f'{singular_alias}.json',
                        initial_path=initial_path,
                        visited_elements=visited_elements
                    )

    def _print_merge_option(self, visited_elements, element, source_path, destination_path) -> None:
        if element not in visited_elements:
            visited_elements.add(element)
            self.out(f"{element} (merges all files/subdirectories under {source_path} into \'{destination_path}\')")
