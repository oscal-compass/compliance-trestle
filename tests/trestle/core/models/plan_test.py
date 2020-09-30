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
"""Tests for trestle span module."""
import os

from trestle.core.models.action import FileContentType, WriteFileAction
from trestle.core.models.element import Element
from trestle.core.models.plan import Plan
from trestle.oscal import target


def test_plan_execution(tmp_dir, sample_target: target.TargetDefinition):
    """Test successful execution of a valid plan."""
    content_type = FileContentType.YAML

    base_dir = os.path.join(tmp_dir, 'mytarget')
    targets_dir = os.path.join(base_dir, 'targets')

    # hand craft a split plan
    split_plan = Plan()
    split_plan.add_action(
        WriteFileAction(os.path.join(base_dir, 'metadata.json'), Element(sample_target.metadata), content_type)
    )

    for tid, t in sample_target.targets.items():
        split_plan.add_action(WriteFileAction(os.path.join(targets_dir, tid), Element(t), content_type))

    # execute the plan
    split_plan.execute()
    split_plan.rollback()
    os.removedirs(targets_dir)


def test_plan_execution_failure():
    """Test unsuccessful execution of a valid plan."""


def test_plan_rollback():
    """Test successful rollback of a valid plan."""


def test_plan_rollback_failure():
    """Test unsuccessful rollback of a valid plan."""
