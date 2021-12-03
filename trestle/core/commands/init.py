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
"""Trestle Init Command."""
import argparse
import logging
import pathlib
import shutil
from shutil import copyfile

from pkg_resources import resource_filename

import trestle.core.const as const
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError

logger = logging.getLogger(__name__)


class InitCmd(CommandBase):
    """Initialize a trestle working directory."""

    name = 'init'

    def _run(self, args: argparse.Namespace) -> int:
        """Create a trestle project in the current directory."""
        log.set_log_level_from_args(args)
        dir_path: pathlib.Path = args.trestle_root
        if not dir_path.exists() or not dir_path.is_dir():
            logger.error(f'Initialization failed. Given directory {dir_path} does not exist or is not a directory.')
            return CmdReturnCodes.TRESTLE_ROOT_ERROR.value

        try:
            # Create directories
            self._create_directories(dir_path)

            # Create config file
            self._copy_config_file(dir_path)

            logger.info(f'Initialized trestle project successfully in {dir_path}')

        except TrestleError as err:
            logger.warning(f'Initialization failed: {err}')
            return CmdReturnCodes.COMMAND_ERROR.value
        return CmdReturnCodes.SUCCESS.value

    def _create_directories(self, root: pathlib.Path) -> None:
        """Create the directory tree if it does not exist."""
        # Prepare directory list to be created
        try:
            directory_list = [root / pathlib.Path(const.TRESTLE_CONFIG_DIR)]
            for model_dir in const.MODEL_DIR_LIST:
                directory_list.append(root / pathlib.Path(model_dir))
                directory_list.append(root / pathlib.Path(const.TRESTLE_DIST_DIR) / model_dir)

            # Create directories
            for directory in directory_list:
                directory.mkdir(parents=True, exist_ok=True)
                file_path = pathlib.Path(directory) / const.TRESTLE_KEEP_FILE
                file_path.touch()
        except OSError as e:
            raise TrestleError(f'Error while creating directories: {e}')
        except Exception as e:
            raise TrestleError(f'Unexpected error while creating directories: {e}')

    def _copy_config_file(self, root: pathlib.Path) -> None:
        """Copy the initial config.ini file to .trestle directory."""
        try:
            source_path = pathlib.Path(resource_filename('trestle.resources', const.TRESTLE_CONFIG_FILE)).resolve()
            destination_path = (root / pathlib.Path(const.TRESTLE_CONFIG_DIR) / const.TRESTLE_CONFIG_FILE).resolve()
            copyfile(source_path, destination_path)

        except (shutil.SameFileError, OSError) as e:
            raise TrestleError(f'Error while copying config file: {e}')
        except Exception as e:
            raise TrestleError(f'Unexpected error while copying config file: {e}')
