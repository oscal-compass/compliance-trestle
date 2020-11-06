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

from pathlib import Path
from typing import List

from ilcli import Command

from trestle.core import const, utils
from trestle.core.commands import cmd_utils
from trestle.core.models.elements import ElementPath
from trestle.core.models.plans import Plan
from trestle.utils import fs


class MergeCmd(Command):
    """Merge subcomponents on a trestle model."""

    name = 'merge'

    def _init_arguments(self):
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=f'Comma-separated list of {const.ARG_DESC_ELEMENT}(s) to be merged.',
        )
        self.add_argument(
            '-l',
            '--list-available-elements',
            action='store_true',
            help='Comma-separated list of paths of properties that can be merged.'
        )

    def _run(self, args):
        """Merge elements into the parent oscal model."""
        if args.list_available_elements:
            self._list_available_elements()
        elif args.element:
            element_paths = args.element.split(',')
            self.merge(cmd_utils.parse_element_args(element_paths))

    @classmethod
    def merge(cls, element_paths: List[ElementPath]) -> Plan:
        """Merge operations.

        It returns a plan for the operation
        """
        plan: Plan = Plan()

        sorted_element_paths = _sort_element_paths(element_paths)

        if metadata_dir.exists():
            # First action: Reset the intermediate destination: metadata.json
            reset_destination_action = CreatePathAction(metadata_file, clear_content=True)
            expected_plan.add_action(reset_destination_action)

            aliases_not_to_be_stripped = []
            instances_to_be_merged: List[OscalBaseModel] = []
            for filepath in Path.iterdir(metadata_dir):
                if filepath.is_file():
                    model_type, model_alias = fs.get_stripped_contextual_model(filepath)
                    model_instance = model_type.oscal_read(filepath)

                    if hasattr(model_instance, '__root__') and (isinstance(model_instance.__root__, dict)
                                                                or isinstance(model_instance.__root__, list)):
                        model_instance = model_instance.__root__

                    instances_to_be_merged.append(model_instance)
                    aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                elif filepath.is_dir():
                    pass

            stripped_metadata_type, _ = fs.get_stripped_contextual_model(metadata_file)
            stripped_metadata = stripped_metadata_type.oscal_read(metadata_file)

            # Create merged model and instance for writeaction
            merged_metadata_type, merged_metadata_alias = fs.get_stripped_contextual_model(
                metadata_file, aliases_not_to_be_stripped=aliases_not_to_be_stripped)
            merged_dict = stripped_metadata.__dict__
            for i in range(len(aliases_not_to_be_stripped)):
                alias = aliases_not_to_be_stripped[i]
                instance = instances_to_be_merged[i]
                merged_dict[alias] = instance
            merged_metadata = merged_metadata_type(**merged_dict)
            element = Element(merged_metadata, merged_metadata_alias)

            # Second action: Write new merged contents of metadata.json
            write_destination_action = WriteFileAction(metadata_file, element, content_type=content_type)
            expected_plan.add_action(write_destination_action)

            # Third action: Delete expanded metadata folder
            delete_element_action = RemovePathAction(metadata_dir)
            expected_plan.add_action(delete_element_action)

        return plan

    def _list_available_elements(self):
        """List element paths that can be merged from the current context."""
        current_model, current_alias = fs.get_contextual_model_type(Path.cwd())

        current_filename = f'{current_alias}.json'

        self._list_options_for_merge(Path.cwd(), current_alias, current_model, current_filename)

    def _list_options_for_merge(
        self,
        cwd,
        current_alias,
        current_model,
        current_filename,
        initial_path: Path = None,
        visited_elements: set = None
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

    def _print_merge_option(self, visited_elements, element, source_path, destination_path):
        if element not in visited_elements:
            visited_elements.add(element)
            self.out(f"{element} (merges all files/subdirectories under {source_path} into \'{destination_path}\')")


def sort_element_paths(element_paths: List[ElementPath]) -> List[ElementPath]:
    """Sort list of element paths for merge purposes."""
    raise NotImplementedError()
