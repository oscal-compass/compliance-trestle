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
import logging

import trestle.tasks.base_task as base_task

logger = logging.getLogger(__name__)


class ComponentsFromTargets(base_task.TaskBase):
    """
    Task which takes a list of targets and profile to produce a set of components.

    Attributes:
        name: Name of the task.
    """

    name = 'components-from-targets'

    def __init__(self, config_object: configparser.SectionProxy) -> None:
        """
        Initialize trestle task components-from-targets.

        Attributes:
            config_object: Config section associated with the task.
        """
        super.__init__(config_object)

    def print_info(self) -> None:
        """Print information on ComponentsFromTargets using logger to the CLI."""

    def execute(self) -> base_task.TaskOutcome:
        """Execute the task."""
        return base_task.TaskOutcome('not-implemented')

    def simulate(self) -> base_task.TaskOutcome:
        """Simulate task execution."""
        return base_task.TaskOutcome('not-implemented')


class SSPFromTargets(base_task.TaskBase):
    """
    Task which takes a list of targets and profile to produce a partial SSP.

    Attributes:
        name: Name of the task.
    """

    name = 'SSP-from-profile-components'

    def __init__(self, config_object: configparser.SectionProxy) -> None:
        """
        Initialise trestle task SSP-from-targets.

        Attributes:
            config_object: Config section associated with the task.
        """
        super.__init__(config_object)

    def print_info(self) -> None:
        """Print information on ComponentsFromTargets using logger to the CLI."""
        pass

    def execute(self) -> base_task.TaskOutcome:
        """Execute the task."""
        if self._config['template-ssp']:
            # load ssp
            pass
        else:
            # generate bare minimum ssp
            pass

        return base_task.TaskOutcome('not-implemented')

    def simulate(self) -> base_task.TaskOutcome:
        """Simulate task execution."""
        return base_task.TaskOutcome('not-implemented')
