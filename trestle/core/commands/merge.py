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
from typing import Set, Type

from ilcli import Command  # type: ignore

from trestle.core import const, utils
from trestle.core.base_model import OscalBaseModel
from trestle.utils import fs


class MergeCmd(Command):
    """Merge subcomponents on a trestle model."""

    name = 'merge'

    def _init_arguments(self) -> None:
        self.add_argument('-e', '--elements', help='Comma-separated list of paths of properties to be merged.')
        self.add_argument(
            '-l',
            '--list-available-elements',
            action='store_true',
            help='Comma-separated list of paths of properties that can be merged.'
        )

    def _run(self, args) -> None:
        """Merge elements into the parent oscal model."""
        if args.list_available_elements:
            self._list_available_elements()

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
