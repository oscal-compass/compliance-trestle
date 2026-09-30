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
"""Plan of action of a command."""

import logging
from io import UnsupportedOperation
from typing import List

from .actions import Action

logger = logging.getLogger(__name__)


class Plan:
    """Plan of action of a command."""

    def __init__(self) -> None:
        """Initialize a plan."""
        self._actions: List[Action] = []

    def _action_key(self, action: Action) -> int:
        return hash(action)

    def __str__(self) -> str:
        """Print the plan."""
        list_actions = []
        index = 1
        for action in self._actions:
            list_actions.append(f'{index}. {action}')
            index = index + 1

        list_str = '\n'.join(list_actions)
        return list_str

    def get_actions(self) -> List[Action]:
        """Get all actions."""
        return self._actions

    def add_action(self, action: Action) -> None:
        """Add a new action."""
        self._actions.append(action)

    def add_actions(self, actions: List[Action]) -> None:
        """Add actions in order."""
        self._actions.extend(actions)

    def clear_actions(self) -> None:
        """Clear all actions."""
        self._actions = []

    def execute(self) -> None:
        """Execute the actions in the plan."""
        for action in self._actions:
            try:
                action.execute()
            except Exception as e:
                logger.error(f'Failed to execute action {action} for the plan: {e}. Rolling back.')
                self.rollback()
                raise e

    def rollback(self) -> None:
        """Rollback the actions in the plan."""
        # execute in reverse order
        for action in reversed(self._actions):
            if action.has_rollback() is False:
                raise UnsupportedOperation(f'{action.get_type()} does not support rollback')
            action.rollback()

    def __eq__(self, other: object) -> bool:
        """Check that two plans are equal."""
        if not isinstance(other, Plan):
            return False

        # Compare actions by their content, not by object identity
        if len(self.get_actions()) != len(other.get_actions()):
            return False

        for i, (self_action, other_action) in enumerate(zip(self.get_actions(), other.get_actions(), strict=True)):
            if self_action != other_action:
                # Debug: print which action differs
                logger.debug(f'Action {i} differs:')
                logger.debug(f'  Self: {self_action}')
                logger.debug(f'  Other: {other_action}')
                return False

        return True

    def __repr__(self) -> str:
        """Return a detailed representation of the plan."""
        return f'Plan(actions={[str(a) for a in self._actions]})'
