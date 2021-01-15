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
"""Tests for trestle plans module."""
import pathlib
from typing import List

from tests import test_utils

from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal import target


def test_plan_execution(tmp_path, sample_target_def: target.TargetDefinition):
    """Test successful execution of a valid plan."""
    content_type = FileContentType.YAML

    base_dir: pathlib.Path = pathlib.Path.joinpath(tmp_path, 'mytarget')
    targets_dir: pathlib.Path = pathlib.Path.joinpath(base_dir, 'targets')
    metadata_yaml: pathlib.Path = pathlib.Path.joinpath(base_dir, 'metadata.yaml')

    test_utils.ensure_trestle_config_dir(base_dir)

    # hand craft a split plan
    split_plan = Plan()
    split_plan.add_action(CreatePathAction(metadata_yaml))
    split_plan.add_action(
        WriteFileAction(metadata_yaml, Element(sample_target_def.metadata, 'target-definition'), content_type)
    )
    # Test stringing a plan
    stringed = str(split_plan)
    assert len(stringed) > 0

    target_files: List[pathlib.Path] = []
    for tid, t in sample_target_def.targets.items():
        target_file: pathlib.Path = pathlib.Path.joinpath(targets_dir, tid + '.yaml')
        target_files.append(target_file)
        split_plan.add_action(CreatePathAction(target_file))
        split_plan.add_action(WriteFileAction(target_file, Element(t, 'target'), content_type))

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


def test_plan_execution_failure():
    """Test unsuccessful execution of a valid plan."""


def test_plan_rollback():
    """Test successful rollback of a valid plan."""


def test_plan_rollback_failure():
    """Test unsuccessful rollback of a valid plan."""
