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
"""Tests for trestle plans module."""

import pathlib
from typing import List

from tests import test_utils

from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal import component


def test_plan_execution(tmp_path, sample_nist_component_def: component.ComponentDefinition):
    """Test successful execution of a valid plan."""
    content_type = FileContentType.YAML

    base_dir: pathlib.Path = pathlib.Path.joinpath(tmp_path, 'mycomponent')
    targets_dir: pathlib.Path = pathlib.Path.joinpath(base_dir, 'components')
    metadata_yaml: pathlib.Path = pathlib.Path.joinpath(base_dir, 'metadata.yaml')

    test_utils.ensure_trestle_config_dir(base_dir)

    # hand craft a split plan
    split_plan = Plan()
    split_plan.add_action(CreatePathAction(metadata_yaml))
    split_plan.add_action(
        WriteFileAction(
            metadata_yaml, Element(sample_nist_component_def.metadata, 'component-definition'), content_type
        )
    )
    # Test stringing a plan
    stringed = str(split_plan)
    assert len(stringed) > 0

    target_files: List[pathlib.Path] = []
    for index in range(len(sample_nist_component_def.components)):
        target_file: pathlib.Path = pathlib.Path.joinpath(targets_dir, f'component_{index}.yaml')
        target_files.append(target_file)
        split_plan.add_action(CreatePathAction(target_file))
        split_plan.add_action(
            WriteFileAction(target_file, Element(sample_nist_component_def.components[index], 'target'), content_type)
        )

    # execute the plan
    split_plan.execute()
    assert base_dir.exists()
    assert targets_dir.exists()
    assert metadata_yaml.exists()
    for target_file in target_files:
        assert target_file.exists()

    split_plan.rollback()
    assert base_dir.exists() is True
    assert targets_dir.exists() is False
    assert metadata_yaml.exists() is False
    for target_file in target_files:
        target_file.exists()


def test_plan_execution_failure(tmp_path):
    """Test unsuccessful execution of a valid plan."""
    from io import UnsupportedOperation
    import pytest
    from trestle.core.models.actions import Action, ActionType

    class FailingAction(Action):
        """Action that fails on execute."""

        def __init__(self):
            super().__init__(ActionType.UPDATE, True)

        def execute(self) -> None:
            self._mark_executed()
            raise RuntimeError('Intentional failure')

        def rollback(self) -> None:
            self._mark_rollback()

    plan = Plan()
    plan.add_action(FailingAction())

    # Should raise the exception and trigger rollback
    with pytest.raises(RuntimeError, match='Intentional failure'):
        plan.execute()


def test_plan_rollback():
    """Test successful rollback of a valid plan."""
    # Already tested in test_plan_execution


def test_plan_rollback_failure(tmp_path):
    """Test unsuccessful rollback of a valid plan."""
    from io import UnsupportedOperation
    import pytest
    from trestle.core.models.actions import Action, ActionType

    class NoRollbackAction(Action):
        """Action that doesn't support rollback."""

        def __init__(self):
            super().__init__(ActionType.UPDATE, False)

        def execute(self) -> None:
            self._mark_executed()

        def rollback(self) -> None:
            raise NotImplementedError('No rollback')

    plan = Plan()
    plan.add_action(NoRollbackAction())

    # Should raise UnsupportedOperation when trying to rollback
    with pytest.raises(UnsupportedOperation):
        plan.rollback()


def test_plan_clear_actions(tmp_path):
    """Test clear_actions method."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    test_file = tmp_path / 'test.txt'

    plan = Plan()
    plan.add_action(CreatePathAction(test_file))
    assert len(plan.get_actions()) == 1

    plan.clear_actions()
    assert len(plan.get_actions()) == 0


def test_plan_equality(tmp_path):
    """Test plan equality comparison."""
    test_utils.ensure_trestle_config_dir(tmp_path)
    test_file = tmp_path / 'test.txt'

    plan1 = Plan()
    plan2 = Plan()

    # Empty plans should be equal
    assert plan1 == plan2

    # Plan should not equal non-Plan object
    assert plan1 != 'not a plan'
    assert plan1 != 123
    assert plan1 is not None

    # Plans with same actions should be equal
    action1 = CreatePathAction(test_file)
    plan1.add_action(action1)
    plan2.add_action(CreatePathAction(test_file))
    assert plan1 == plan2

    # Plans with different number of actions should not be equal
    plan3 = Plan()
    assert plan1 != plan3


def test_plan_repr():
    """Test plan __repr__ method."""
    plan = Plan()
    repr_str = repr(plan)
    assert 'Plan' in repr_str
    assert 'actions=' in repr_str


# ---------------------------------------------------------------------------
# Coverage-improvement tests for trestle/core/models/plans.py
# ---------------------------------------------------------------------------


def test_plan_equality_diff_actions_logs_debug(tmp_path):
    """Plan.__eq__: lines 92-94 — debug logging when actions differ."""
    import logging

    test_utils.ensure_trestle_config_dir(tmp_path)
    plan1 = Plan()
    plan2 = Plan()
    plan1.add_action(CreatePathAction(tmp_path / 'a.json'))
    plan2.add_action(CreatePathAction(tmp_path / 'b.json'))
    # __eq__ with differing actions hits the debug logging block (lines 92-94) and returns False
    assert plan1 != plan2
