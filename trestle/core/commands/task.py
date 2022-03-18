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
"""Trestle task command."""
import argparse
import configparser
import inspect
import logging
import pathlib
import pkgutil
import sys
from typing import Dict, Optional, Type

import trestle.common.const as const
import trestle.common.log as log
import trestle.tasks
from trestle.common import file_utils
from trestle.common.err import TrestleError, TrestleIncorrectArgsError, handle_generic_command_exception
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.tasks.base_task import TaskBase, TaskOutcome

logger = logging.getLogger(__name__)


class TaskCmd(CommandPlusDocs):
    """Run arbitrary trestle tasks in a simple and extensible methodology."""

    name = 'task'

    def _init_arguments(self) -> None:
        self.add_argument(
            'task',
            nargs='?',
            type=str,
            help='The name of the task to be run, trestle task -l will list available tasks.'
        )
        self.add_argument('-l', '--list', action='store_true', help='List the available tasks')
        self.add_argument(
            '-c', '--config', type=pathlib.Path, help='Pass a customized configuration file specifically for a task'
        )
        self.add_argument('-i', '--info', action='store_true', help='Print information about a particular task.')

    def _run(self, args: argparse.Namespace) -> int:
        try:
            logger.debug('Entering trestle task.')
            log.set_log_level_from_args(args)
            # Initial logic for conflicting args
            if args.task and args.list:
                raise TrestleIncorrectArgsError('Task name or -l can be provided not both.')

            if not args.task and not args.list:
                raise TrestleIncorrectArgsError(
                    'Either a trestle task or "-l/--list" shoudl be passed as input arguments.'
                )

            # Ensure trestle directory (must be true)
            trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.
            if not trestle_root or not file_utils.is_valid_project_root(args.trestle_root):
                raise TrestleError(f'Given directory: {trestle_root} is not a trestle project.')

            config_path = trestle_root / const.TRESTLE_CONFIG_DIR / const.TRESTLE_CONFIG_FILE

            if args.config:
                config_path = pathlib.Path(args.config)
            if not config_path.exists():
                raise TrestleError(f'Config file at {config_path} does not exist.')

            # permit ${name} in config definitions
            global_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            global_config.read_file(config_path.open('r', encoding=const.FILE_ENCODING))
            # run setup
            task_index = self._build_task_index()

            # Clean to run
            if args.list:
                self._list_tasks(task_index)
                return CmdReturnCodes.SUCCESS.value
            # run the task
            if args.task not in task_index.keys():
                raise TrestleIncorrectArgsError(f'Unknown trestle task: {args.task}')

            logger.debug(f'Loading task: {args.task}')
            section_label = 'task.' + args.task
            config_section: Optional[configparser.SectionProxy] = None
            if section_label in global_config.sections():
                config_section = global_config[section_label]
            else:
                logger.warning(
                    f'Config file was not configured with the appropriate section for the task: "[{section_label}]"'
                )

            task = task_index[args.task](config_section)
            if args.info:
                task.print_info()
                return CmdReturnCodes.SUCCESS.value

            simulate_result = task.simulate()
            if not (simulate_result == TaskOutcome.SIM_SUCCESS):
                raise TrestleError(f'Task {args.task} reported a {simulate_result}')

            actual_result = task.execute()
            if not (actual_result == TaskOutcome.SUCCESS):
                raise TrestleError(f'Task {args.task} reported a {actual_result}')

            logger.info(f'Task: {args.task} executed successfully.')
            return CmdReturnCodes.SUCCESS.value

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while executing Trestle task')

    def _build_task_index(self) -> Dict[str, Type[TaskBase]]:
        """Build an index of all classes in which are tasks and present as a dictionary."""
        task_index: Dict[str, Type[TaskBase]] = {}
        pkgpath = str(pathlib.Path(trestle.tasks.__file__).parent)
        for _, name, _ in pkgutil.iter_modules([pkgpath]):
            __import__(f'trestle.tasks.{name}')
            clsmembers = inspect.getmembers(sys.modules[f'trestle.tasks.{name}'], inspect.isclass)
            for candidate in clsmembers:
                if issubclass(candidate[1], TaskBase):
                    task_index[candidate[1].name] = candidate[1]
        return task_index

    def _list_tasks(self, task_index: Dict[str, Type[TaskBase]]) -> None:
        logger.info('Available tasks:')
        for key in task_index.keys():
            logger.info(f'    {key}')
