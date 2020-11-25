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
"""Trestle tasks base templating."""
import configparser
from abc import ABC, abstractmethod
from enum import Enum

import trestle.utils.log as log

logger = log.get_logger()


class TaskOutcome(Enum):
    """Enum describing possible task outcomes."""

    SUCCESS = 'success'
    FAILURE = 'failure'
    ROLLEDBACK = 'rolledback'
    SIM_SUCCESS = 'simulated-success'
    SIM_FAILURE = 'simulated-failure'
    NOT_IMPLEMENTED = 'not-implemented'


class TaskBase(ABC):
    """
    Abstract base class for tasks.

    Attributes:
        name: Name of the task.
    """

    name: str = 'base'

    def __init__(self, config_object: configparser.SectionProxy) -> None:
        """Initialize task base and store config."""
        self._config = config_object

    @abstractmethod
    def print_info(self) -> None:
        """Print the help string."""

    @abstractmethod
    def execute(self) -> TaskOutcome:
        """Execute the task including potential rollback."""

    @abstractmethod
    def simulate(self) -> TaskOutcome:
        """Simulate the task and report task outcome."""


class PassFail(TaskBase):
    """
    Holding pattern template for a task which does nothing and always passes.

    Attributes:
        name: Name of the task.
    """

    name = 'pass-fail'

    def __init__(self, config_object: configparser.SectionProxy) -> None:
        """
        Initialize trestle task pass-fail.

        Attributes:
            config_object: Config section associated with the task.
        """
        super.__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('This is a template task which reports pass fail depending on the specific configuration.')
        logger.info('')
        logger.info('Configuration flags sit under [tasks.pass-fail]')
        logger.info('with two boolean flags')
        logger.info('execute_status = True/False')
        logger.info('simulate_status = True/False')
        logger.info('The princple goal is a simple development example')
