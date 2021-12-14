# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Trestle Split Command."""
import argparse
import logging
import pathlib
import traceback
from typing import Dict, List, Tuple

import trestle.utils.log as log
from trestle.core import const
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common import cmd_utils
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError
from trestle.core.models.actions import Action, CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.core.trestle_base_model import TrestleBaseModel
from trestle.utils import fs, trash

logger = logging.getLogger(__name__)


class AliasTracker(TrestleBaseModel):
    """Convenience class to track writing out of models."""

    # This tracks the parts that need to be split from each element
    # and makes sure it is written out once

    aliases: List[str]
    written: bool = False

    def add_alias(self, alias: str) -> None:
        """Add alias."""
        if alias not in self.aliases:
            self.aliases.append(alias)

    def get_aliases(self) -> List[str]:
        """Get the list of aliases."""
        return self.aliases

    def needs_writing(self) -> bool:
        """Need to write the model."""
        return not self.written

    def mark_written(self) -> None:
        """Mark this model as written."""
        self.written = True


class SplitCmd(CommandPlusDocs):
    """Split subcomponents on a trestle model."""

    name = 'split'

    def _init_arguments(self) -> None:
        self.add_argument(
            f'-{const.ARG_FILE_SHORT}', f'--{const.ARG_FILE}', help=const.ARG_DESC_FILE + ' to split.', required=False
        )
        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=const.ARG_DESC_ELEMENT + ' to split.',
            required=False
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Split an OSCAL file into elements."""
        try:
            log.set_log_level_from_args(args)
            logger.debug('Entering trestle split.')
            # get the Model
            args_raw: Dict[str, str] = args.__dict__

            # remove any quotes passed in as on windows platforms
            elements_clean: str = args_raw[const.ARG_ELEMENT].strip("'")

            file_name = ''
            file_name = '' if const.ARG_FILE not in args_raw or args_raw[const.ARG_FILE] is None else args_raw[
                const.ARG_FILE]
            # cwd must be in the model directory if file to split is not specified
            effective_cwd = pathlib.Path.cwd()

            return self.perform_split(effective_cwd, file_name, elements_clean, args.trestle_root)
        except TrestleError as e:
            logger.debug(traceback.format_exc())
            logger.error(f'Error while performing a split operation: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            logger.debug(traceback.format_exc())
            logger.error(f'Unexpected error while performing a split operation: {e}')
            return CmdReturnCodes.UNKNOWN_ERROR.value

    @classmethod
    def perform_split(
        cls, effective_cwd: pathlib.Path, file_name: str, elements: str, trestle_root: pathlib.Path
    ) -> int:
        """Perform the split operation.

        Args:
            effective_cwd: effective directory in which the the split operation is performed
            file_name: file name of model to split, or '' if deduced from elements and cwd
            elements: comma separated list of paths to strip from the file, with quotes removed

        Returns:
            0 on success and 1 on failure
        """
        file_path_list: List[Tuple[str, str]] = []

        if file_name:
            file_path_list.append((file_name, elements))
        else:
            # cwd must be in the model directory if file to split is not specified
            # find top directory for this model based on trestle root and cwd
            model_dir = fs.get_project_model_path(effective_cwd)
            if model_dir is None:
                logger.warning('Current directory must be within a model directory if file is not specified')
                return CmdReturnCodes.COMMAND_ERROR.value

            content_type: FileContentType = FileContentType.dir_to_content_type(model_dir)

            # determine the file needed for each split path
            element_paths = elements.split(',')
            for path in element_paths:
                element_path = ElementPath(path)
                # if element path is relative use directory context to determine absolute path
                element_path.make_absolute(model_dir, effective_cwd)
                file_path = element_path.find_last_file_in_path(content_type, model_dir)
                # now make the element path relative to the model file to be loaded
                if file_path is None or element_path.make_relative(file_path.relative_to(model_dir)) != 0:
                    logger.warning(f'Unable to match element path with files in model directory {element_path}')
                    return CmdReturnCodes.COMMAND_ERROR.value
                file_path_list.append((file_path, element_path.to_string()))

        # match paths to corresponding files since several paths may be split from the same file
        file_path_dict: Dict[str, str] = {}
        for file_path in file_path_list:
            key = file_path[0]
            path = file_path[1]
            if key not in file_path_dict:
                file_path_dict[key] = path
            else:
                current_path = file_path_dict[key]
                file_path_dict[key] = f'{current_path},{path}'

        for raw_file_name, element_path in file_path_dict.items():
            file_path = fs.relative_resolve(pathlib.Path(raw_file_name), effective_cwd)
            # this makes assumptions that the path is relative.
            if not file_path.exists():
                logger.error(f'File {file_path} does not exist.')
                return CmdReturnCodes.COMMAND_ERROR.value
            content_type = FileContentType.to_content_type(file_path.suffix)

            # find the base directory of the file
            base_dir = file_path.parent
            model_type, _ = fs.get_stripped_model_type(file_path, trestle_root)

            model: OscalBaseModel = model_type.oscal_read(file_path)

            if cmd_utils.split_is_too_fine(element_path, model):
                logger.warning('Cannot split the model to the level of uuids, strings, etc.')
                return CmdReturnCodes.COMMAND_ERROR.value

            # use the model itself to resolve any wildcards and create list of element paths
            logger.debug(f'split calling parse_element_args on {element_path}')
            # use contextual mode to parse

            element_paths: List[ElementPath] = cmd_utils.parse_element_args(
                model, element_path.split(','), base_dir.relative_to(trestle_root)
            )

            # analyze the split tree and determine which aliases should be stripped from each file
            aliases_to_strip = cls.find_aliases_to_strip(element_paths)

            # need the file name relative to the base directory
            file_name_no_path = str(file_path.name)

            split_plan = cls.split_model(
                model, element_paths, base_dir, content_type, file_name_no_path, aliases_to_strip
            )
            trash.store(file_path, True)

            try:
                split_plan.execute()
            except Exception as e:
                logger.error(f'Split has failed with error: {e}.')
                trash.recover(file_path, True)
                return CmdReturnCodes.COMMAND_ERROR.value

        return CmdReturnCodes.SUCCESS.value

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
        file_name = cmd_utils.to_model_file_name(sub_model_item, file_prefix, content_type)
        model_type = utils.classname_to_alias(type(sub_model_item).__name__, 'json')
        sub_model_file = sub_model_dir / file_name
        actions.append(CreatePathAction(sub_model_file))
        actions.append(WriteFileAction(sub_model_file, Element(sub_model_item, model_type), content_type))
        return actions

    @classmethod
    def split_model_at_path_chain(
        cls,
        model_obj: OscalBaseModel,
        element_paths: List[ElementPath],
        base_dir: pathlib.Path,
        content_type: FileContentType,
        cur_path_index: int,
        split_plan: Plan,
        strip_root: bool,
        root_file_name: str,
        aliases_to_strip: Dict[str, AliasTracker],
        last_one: bool = True
    ) -> int:
        """Recursively split the model at the provided chain of element paths.

        It assumes that a chain of element paths starts at the cur_path_index with the first path ending
        with a wildcard (*)

        If the wildcard follows an element that is inherently a list of items, the list of items is extracted.
        But if the wildcard follows a generic model than members of that model class found in the model will be
        split off.  But only the non-trivial elements are removed, i.e. not str, int, datetime, etc.

        Args:
            model_obj: The OscalBaseModel to be split
            element_paths: The List[ElementPath] of elements to split, including embedded wildcards
            base_dir: pathlib.Path of the file being split
            content_type: json or yaml files
            cur_path_index: Index into the list of element paths for the current split operation
            split_plan: The accumulated plan of actions needed to perform the split
            strip_root: Whether to strip elements from the root object
            root_file_name: Filename of root file that gets split into a list of items
            aliases_to_strip: AliasTracker previously loaded with aliases that need to be split from each element
            last_one: bool indicating last item in array has been split and stripped model can now be written

        Returns:
            int representing the index where the chain of the path ends.

        Examples:
            For example, element paths could have a list of paths as below for a `ComponentDefinition` model where
            the first path is the start of the chain.

            For each of the sub model described by the first element path (e.g component-defintion.components.*) in the
            chain, the subsequent paths (e.g component.control-implementations.*) will be applied recursively
            to retrieve the sub-sub models:
            [
                'component-definition.component.*',
                'component.control-implementations.*'
            ]
            for a command like below:
            trestle split -f component.yaml -e component-definition.components.*.control-implementations.*
        """
        if split_plan is None:
            raise TrestleError('Split plan must have been initialized')

        if cur_path_index < 0:
            raise TrestleError('Current index of the chain of paths cannot be less than 0')

        # if there are no more element_paths, return the current plan
        if cur_path_index >= len(element_paths):
            return cur_path_index

        # initialize local variables
        element = Element(model_obj)
        stripped_field_alias: List[str] = []

        # get the sub_model specified by the element_path of this round
        element_path = element_paths[cur_path_index]

        # does the next element_path point back at me
        is_parent = cur_path_index + 1 < len(element_paths) and element_paths[cur_path_index
                                                                              + 1].get_parent() == element_path

        # root dir name for sub models dir
        # 00000__group.json will have the root_dir name as 00000__group for sub models of group
        # catalog.json will have the root_dir name as catalog
        root_dir = ''
        if root_file_name != '':
            root_dir = str(pathlib.Path(root_file_name).with_suffix(''))

        sub_models = element.get_at(element_path, False)  # we call sub_models as in plural, but it can be just one

        # assume cur_path_index is the end of the chain
        # value of this variable may change during recursive split of the sub-models below
        path_chain_end = cur_path_index

        # if wildcard is present in the element_path and the next path in the chain has current path as the parent,
        # Then deal with case of list, or split of arbitrary oscalbasemodel
        if is_parent and element_path.get_last() is not ElementPath.WILDCARD:
            # create dir for all sub model items
            sub_models_dir = base_dir / element_path.to_root_path()
            sub_model_plan = Plan()
            path_chain_end = cls.split_model_at_path_chain(
                sub_models,
                element_paths,
                sub_models_dir,
                content_type,
                cur_path_index + 1,
                sub_model_plan,
                True,
                '',
                aliases_to_strip
            )
            sub_model_actions = sub_model_plan.get_actions()
            split_plan.add_actions(sub_model_actions)
        elif element_path.get_last() == ElementPath.WILDCARD:
            # extract sub-models into a dict with appropriate prefix
            sub_model_items: Dict[str, OscalBaseModel] = {}
            sub_models_dir = base_dir / element_path.to_file_path(root_dir=root_dir)
            if isinstance(sub_models, list):
                for i, sub_model_item in enumerate(sub_models):
                    # e.g. `groups/00000_groups/`
                    prefix = str(i).zfill(const.FILE_DIGIT_PREFIX_LENGTH)
                    sub_model_items[prefix] = sub_model_item

            # process list sub model items
            count = 0
            for key, sub_model_item in sub_model_items.items():
                count += 1
                # recursively split the sub-model if there are more element paths to traverse
                # e.g. split component.control-implementations.*
                require_recursive_split = cur_path_index + 1 < len(element_paths) and element_paths[
                    cur_path_index + 1].get_parent() == element_path

                if require_recursive_split:
                    # prepare individual directory for each sub-model
                    sub_root_file_name = cmd_utils.to_model_file_name(sub_model_item, key, content_type)
                    sub_model_plan = Plan()

                    last_one: bool = count == len(sub_model_items)
                    path_chain_end = cls.split_model_at_path_chain(
                        sub_model_item,
                        element_paths,
                        sub_models_dir,
                        content_type,
                        cur_path_index + 1,
                        sub_model_plan,
                        True,
                        sub_root_file_name,
                        aliases_to_strip,
                        last_one
                    )
                    sub_model_actions = sub_model_plan.get_actions()
                else:
                    sub_model_actions = cls.prepare_sub_model_split_actions(
                        sub_model_item, sub_models_dir, key, content_type
                    )

                split_plan.add_actions(sub_model_actions)
        else:
            # the chain of path ends at the current index.
            # so no recursive call. Let's just write the sub model to the file and get out
            if sub_models is not None:
                sub_model_file = base_dir / element_path.to_file_path(content_type, root_dir=root_dir)
                split_plan.add_action(CreatePathAction(sub_model_file))
                split_plan.add_action(
                    WriteFileAction(sub_model_file, Element(sub_models, element_path.get_element_name()), content_type)
                )

        # Strip the root model and add a WriteAction for the updated model object in the plan
        if strip_root:
            full_path = element_path.get_full()
            path = '.'.join(full_path.split('.')[:-1])
            aliases = [element_path.get_element_name()]
            need_to_write = True
            use_alias_dict = aliases_to_strip is not None and path in aliases_to_strip
            if use_alias_dict:
                aliases = aliases_to_strip[path].get_aliases()
                need_to_write = aliases_to_strip[path].needs_writing()

            stripped_model = model_obj.stripped_instance(stripped_fields_aliases=aliases)
            # can mark it written even if it doesn't need writing since it is empty
            # but if an array only mark it written if it's the last one
            if last_one and use_alias_dict:
                aliases_to_strip[path].mark_written()
            # If it's an empty model after stripping the fields, don't create path and don't write
            field_list = [x for x in model_obj.__fields__.keys() if model_obj.__fields__[x] is not None]
            if set(field_list) == set(stripped_field_alias):
                return path_chain_end

            if need_to_write:
                if root_file_name != '':
                    root_file = base_dir / root_file_name
                else:
                    root_file = base_dir / element_path.to_root_path(content_type)

                split_plan.add_action(CreatePathAction(root_file))
                wrapper_alias = utils.classname_to_alias(stripped_model.__class__.__name__, 'json')
                split_plan.add_action(WriteFileAction(root_file, Element(stripped_model, wrapper_alias), content_type))

        # return the end of the current path chain
        return path_chain_end

    @classmethod
    def split_model(
        cls,
        model_obj: OscalBaseModel,
        element_paths: List[ElementPath],
        base_dir: pathlib.Path,
        content_type: FileContentType,
        root_file_name: str,
        aliases_to_strip: Dict[str, AliasTracker]
    ) -> Plan:
        """Split the model at the provided element paths.

        It returns a plan for the operation
        """
        # initialize plan
        split_plan = Plan()

        # loop through the element path list and update the split_plan
        stripped_field_alias = []
        cur_path_index = 0
        while cur_path_index < len(element_paths):
            # extract the sub element name for each of the root path of the path chain
            element_path = element_paths[cur_path_index]

            if element_path.get_parent() is None and len(element_path.get()) > 1:
                stripped_part = element_path.get()[1]
                if stripped_part == ElementPath.WILDCARD:
                    stripped_field_alias.append('__root__')
                else:
                    if stripped_part not in stripped_field_alias:
                        stripped_field_alias.append(stripped_part)

            # split model at the path chain
            cur_path_index = cls.split_model_at_path_chain(
                model_obj,
                element_paths,
                base_dir,
                content_type,
                cur_path_index,
                split_plan,
                False,
                root_file_name,
                aliases_to_strip
            )

            cur_path_index += 1

        # strip the root model object and add a WriteAction
        stripped_root = model_obj.stripped_instance(stripped_fields_aliases=stripped_field_alias)
        # If it's an empty model after stripping the fields, don't create path and don't write
        if set(model_obj.__fields__.keys()) == set(stripped_field_alias):
            return split_plan
        if root_file_name != '':
            root_file = base_dir / root_file_name
        else:
            root_file = base_dir / element_paths[0].to_root_path(content_type)
        split_plan.add_action(CreatePathAction(root_file, True))
        wrapper_alias = utils.classname_to_alias(stripped_root.__class__.__name__, 'json')
        split_plan.add_action(WriteFileAction(root_file, Element(stripped_root, wrapper_alias), content_type))

        return split_plan

    @classmethod
    def find_aliases_to_strip(cls, element_paths: List[ElementPath]) -> Dict[str, AliasTracker]:
        """Find list of aliases that need to be stripped as each element written out."""
        # A given path may be present in several split actions
        # Need to determine all parts stripped at each node in order to strip them all and
        # write the stripped model only once
        tracker_map: Dict[str, AliasTracker] = {}
        for element_path in element_paths:
            path = element_path.get_full()
            path_parts = path.split('.')
            alias = path_parts[-1]
            if len(path_parts) > 2 and alias != '*':
                root_path = '.'.join(path_parts[:-1])
                if root_path in tracker_map:
                    tracker_map[root_path].add_alias(alias)
                else:
                    tracker_map[root_path] = AliasTracker(aliases=[alias])
        return tracker_map
