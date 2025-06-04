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
"""Trestle tasks base templating."""
import configparser
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


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

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
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

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task pass-fail.

        Attributes:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('This is a template task which reports pass fail depending on the specific configuration.')
        logger.info(
            'In this case if no config section is provided the task will fail. This a a task specific behavior.'
        )
        logger.info('Configuration flags sit under [task.pass-fail]')
        logger.info('with two boolean flags')
        logger.info('execute_status = True/False with a default pass')
        logger.info('simulate_status = True/False with a default fail')
        logger.info('Note that if the config file does not have the appropriate section this should fail.')
        logger.info('The princple goal is a simple development example.')

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        if self._config:
            outcome = self._config.getboolean('simulate_status', fallback=True)
            if outcome:
                return TaskOutcome('simulated-success')
        return TaskOutcome('simulated-failure')

    def execute(self) -> TaskOutcome:
        """Provide a actual outcome."""
        if self._config:
            outcome = self._config.getboolean('execute_status', fallback=True)
            if outcome:
                return TaskOutcome('success')
        return TaskOutcome('failure')
