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
"""Trestle task command."""
import argparse
import configparser
import inspect
import pathlib
import pkgutil
import sys
from typing import Dict, Type

from ilcli import Command  # type: ignore

import trestle.core.const
import trestle.tasks
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.tasks.base_task import TaskBase, TaskOutcome

logger = log.get_logger()


class TaskCmd(Command):
    """Run arbitrary trestle tasks in a templated method."""

    def _init_arguments(self) -> None:
        self.add_argument(
            'task',
            nargs=1,
            type=str,
            help='The name of the task to be run, trestle task -l will list available tasks.'
        )
        self.add_argument('-l', '--list', action='store_true', help='List the available tasks')
        self.add_argument(
            '-c', '--config', type=pathlib.Path, help='Pass a customized configuration file specifically for a task'
        )
        self.add_argument('-i', '--info', action='store_true', help='Print information about a particular task.')

    def _run(self, args: argparse.Namespace) -> int:
        # TOD
        # Initial logic for conflicting args
        if len(args.task) > 0 and args.list:
            logger.error('Incorrect use of trestle tasks')
            logger.error('')
            return 1
        elif len(args.task) == 0 and not args.list:
            logger.error('Insufficient arguments passed to trestle task')
            logger.error('Either a trestle task or "-l/--list" shoudl be passed as input arguments.')
            return 1
        # Ensure trestle directory (must be true)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.error(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1
        config_path = trestle_root / trestle.core.const.TRESTLE_CONFIG_DIR / trestle.core.const.TRESTLE_CONFIG_FILE

        global_config = configparser.ConfigParser()
        global_config.read_file(config_path.open('r'))

        if args.config:
            config_path = pathlib.Path(args.config)
        if not config_path.exists():
            logger.error(f'Config file at {config_path} does not exist.')
            return 1
        # run setup
        task_index = self.__build_task_index()

        # Clean to run
        if args.list:
            self._list_tasks(task_index)
            return 0
        # run the task
        if args.name not in task_index.keys():
            logger.error(f'Unknown trestle task: {args.name}')
            return 1
        # Generic try catch around execution
        try:
            logger.debug(f'Loading task: {args.task}')
            config_section = global_config['task-' + args.name]
            task = task_index[args.task](config_section)
            if args.info:
                task.print_info()
                return 0
            simulate_result = task.simulate()
            if not simulate_result == TaskOutcome.SIM_SUCCESS:
                logger.error(f'Task {args.name} reported a {simulate_result}')
                return 1
            actual_result = task.simulate()
            if not actual_result == TaskOutcome.SUCCESS:
                logger.error(f'Task {args.name} reported a {actual_result}')
                return 1
            logger.info(f'Task: {args.name} executed successfully.')
            return 0
        except Exception as e:
            logger.error(f'Trestle task {args.name} failed unexpectedly')
            logger.debug(e)
            return 1

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
