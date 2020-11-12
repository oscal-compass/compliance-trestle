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

from abc import ABC, abstractmethod
from enum import Enum


class TaskOutcome(Enum):
    """Enum describing possible task outcomes."""

    SUCCESS = 'success'
    FAILURE = 'failure'
    ROLLEDBACK = 'rolledback'
    SIM_SUCCESS = 'simulated-success'
    SIM_FAILURE = 'simulated-failure'


class TasksBase(ABC):
    """Abstract base class for tasks."""

    def __init__(self, config_object):
        """Initialize task base."""

    @abstractmethod
    def print_help(self) -> str:
        """Print the help string."""
        pass

    @abstractmethod
    def execute() -> TaskOutcome:
        """Execute the task including potential rollback."""
        pass

    @abstractmethod
    def simulate() -> TaskOutcome:
        """Simulate the task and report task outcome."""
        pass
