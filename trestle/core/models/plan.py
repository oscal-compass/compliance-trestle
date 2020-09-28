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

    def __init__(self, action_list: list(Action)):
        """Initialize a plan."""
        self._action_orders: list = []
        self._actions: dict = {}
        for action in action_list:
            self.add_action(action)

    def _action_key(self, action: Action):
        return hash(action)

    def __str__(self):
        """Print the plan."""
        list_actions = []
        index = 0
        for action_key in self._action_orders:
            ac: Action = Action(self._actions[action_key])
            list_actions.append(f'{index}. {ac}')
            index = index + 1
        return list_actions

    def add_action(self, action: Action):
        """Add a new action."""
        key = self._action_key(action)
        if self._actions[key] is not None:
            self.remove_action(action)

        self._action_orders.append(key)
        self._actions[key] = action

    def remove_action(self, action: Action):
        """Add a new action."""
        key = self._action_key(action)
        if self._actions[key] is not None:
            self._actions.pop(key, None)
            self._action_orders.remove(key)

    def simulate(self):
        """Simulate execution of the plan."""
        # Check if all of the actions support rollback or not
        for action_key in self._action_orders:
            ac: Action = Action(self._actions[action_key])
            if ac.has_rollback() is False:
                raise UnsupportedOperation(f'{ac.get_type()} does not support rollback')

        self.execute()
        self.rollback()

    def execute(self):
        """Execute the actions in the plan."""
        for action_key in self._action_orders:
            ac: Action = Action(self._actions[action_key])
            ac.execute()

    def rollback(self):
        """Rollback the actions in the plan."""
        for action_key in self._action_orders.reverse():
            ac: Action = Action(self._actions[action_key])
            if ac.has_rollback() is False:
                raise UnsupportedOperation(f'{ac.get_type()} does not support rollback')

            ac.rollback()
