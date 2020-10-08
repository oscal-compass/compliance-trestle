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

from ilcli import Command

import trestle.core.const as const
import trestle.core.utils as utils


class MergeCmd(Command):
    """Merge subcomponents on a trestle model."""

    name = 'merge'

    def _init_arguments(self):
        self.add_argument('-e', '--elements', help='Comma-separated list of paths of properties to be merged.')
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

    def _list_available_elements(self):
        """List element paths that can be merged from the current context."""
        contextual_path = utils.get_contextual_path(Path.cwd())
        if len(contextual_path) < 3:
            self.err('Error: Not in a source directory of a model type')
            return 1
        current_working_module_name = utils.get_cwm(contextual_path)
        root_model, root_alias = utils.get_root_model(current_working_module_name)

        # user is in the base folder of the model type
        current_model = root_model
        current_alias = root_alias

        current_model, current_alias = utils.get_contextual_model(contextual_path)

        current_filename = f'{current_alias}.json'

        initial_depth = len(Path.cwd().parts)
        visited_elements = set()
        self._list_options_for_merge(
            initial_depth, visited_elements, Path.cwd(), current_alias, current_model, current_filename
        )

    def _list_options_for_merge(
        self, initial_depth, visited_elements, cwd, current_alias, current_model, current_filename
    ):
        """List paths that can be used in the -e option for the merge operation."""
        cwdpath = Path(cwd)
        path_sep = '.' if current_alias else ''

        # List options for merge
        if not utils.is_collection_model(current_model):
            # Go through each file or subdirectory in the cwd
            fields_by_alias = current_model.get_fields_by_alias()
            for filename in Path.iterdir(cwdpath):
                # Skip if suffix of file is not json
                if filename.suffix and filename.suffix.lower() != '.json':
                    continue
                # Merge only applies to files and subdirectories other than the parent file
                if filename.name != current_filename:
                    alias = filename.with_suffix('').name
                    if alias in fields_by_alias:
                        visited_element = f'{current_alias}{path_sep}{alias}'
                        if visited_element not in visited_elements:
                            visited_elements.add(visited_element)
                            self.out(
                                f"{visited_element} (merges \'{filename.name}\' into \'{cwdpath / current_filename}\')"
                            )

                        # If it is subdirectory, call this function recursively
                        if Path.is_dir(filename):
                            self._list_options_for_merge(
                                initial_depth,
                                visited_elements,
                                filename,
                                f'{current_alias}{path_sep}{alias}',
                                fields_by_alias[alias].outer_type_,
                                f'{alias}.json'
                            )
        else:
            # List merge option for collection at the base level
            destination_dir = cwdpath.parent if initial_depth < len(cwdpath.parts) else cwdpath
            destination = destination_dir / current_filename
            visited_element = f'{current_alias}{path_sep}{const.ELEMENT_WILDCARD}'
            if visited_element not in visited_elements:
                visited_elements.add(visited_element)
                self.out(f"{visited_element} (merges all files/subdirectories under {cwd} into \'{destination}\')")

            # Go through each subdirectory in the collection and look for nested merge options
            singular_alias = utils.get_singular_alias_from_collection_model(current_model)
            singular_model = utils.get_inner_model(current_model)
            for filename in sorted(cwdpath.glob(f'*{const.IDX_SEP}{singular_alias}')):
                if Path.is_dir(filename):
                    self._list_options_for_merge(
                        initial_depth,
                        visited_elements,
                        filename,
                        f'{current_alias}{path_sep}*',
                        singular_model,
                        f'{singular_alias}.json'
                    )

    def _print_merge_option(self, visited_elements, element, source_path, destination_path):
        if element not in visited_elements:
            visited_elements.add(element)
            self.out(f"{element} (merges all files/subdirectories under {source_path} into \'{destination_path}\')")


if __name__ == '__main__':
    os.chdir('tmp/catalogs/mycatalog/groups')
    MergeCmd()._list_available_elements()
