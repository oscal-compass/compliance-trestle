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
"""Plan of action of a command."""

from .action import Action


class Plan:
    """Plan of action of a command."""

    def __init__(self, action_list: list(Action)):
        """Initialize a plan."""
        self._actions: list(Action) = action_list

    def add_action(self, action: Action):
        """Add a new action."""
        self._actions.append(action)

    def simulate(self):
        """Simulate execution of the plan."""

    def execute(self):
        """Execute the actions in the plan."""

    def rollback(self):
        """Rollback the actions in the plan."""
