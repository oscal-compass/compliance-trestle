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

from io import UnsupportedOperation

from .action import Action


class Plan:
    """Plan of action of a command."""

    def __init__(self):
        """Initialize a plan."""
        self._actions: list[Action] = []

    def _action_key(self, action: Action):
        return hash(action)

    def __str__(self):
        """Print the plan."""
        list_actions = []
        index = 1
        for action in self._actions:
            list_actions.append(f'{index}. {action}')
            index = index + 1

        list_str = '\n'.join(list_actions)
        return list_str

    def add_action(self, action: Action):
        """Add a new action."""
        self._actions.append(action)

    def clear_actions(self):
        """Clear all actions."""
        self._actions = []

    def simulate(self):
        """Simulate execution of the plan."""
        # Check if all of the actions support rollback or not
        for action in self._actions.items():
            if action.has_rollback() is False:
                raise UnsupportedOperation(f'{action.get_type()} does not support rollback')

        self.execute()
        self.rollback()

    def execute(self):
        """Execute the actions in the plan."""
        for action in self._actions:
            action.execute()

    def rollback(self):
        """Rollback the actions in the plan."""
        # execute in reverse order
        for action in reversed(self._actions):
            if action.has_rollback() is False:
                raise UnsupportedOperation(f'{action.get_type()} does not support rollback')
            action.rollback()
