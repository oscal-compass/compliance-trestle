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
"""Trestle Create Command."""

from ilcli import Command  # type: ignore


class CatalogCmd(Command):
    """Create a sample catalog."""

    name = 'catalog'


class ProfileCmd(Command):
    """Create a sample profile."""

    name = 'profile'


class TargetDefinitionCmd(Command):
    """Create a sample target definition."""

    name = 'target-definition'


class ComponentDefinitionCmd(Command):
    """Create a sample component definition."""

    name = 'component-definition'


class SystemSecurityPlanCmd(Command):
    """Create a sample system security plan."""

    name = 'system-security-plan'


class AssessmentPlanCmd(Command):
    """Create a sample assessment plan."""

    name = 'assessment-plan'


class AssessmentResultCmd(Command):
    """Create a sample assessment result."""

    name = 'assessment-result'


class PlanOfActionAndMilestoneCmd(Command):
    """Create a sample plan of action and milestone result."""

    name = 'plan-of-action-and-milestone'


class CreateCmd(Command):
    """Create a sample trestle model."""

    name = 'create'

    subcommands = [
        CatalogCmd,
        ProfileCmd,
        TargetDefinitionCmd,
        ComponentDefinitionCmd,
        SystemSecurityPlanCmd,
        AssessmentPlanCmd,
        AssessmentResultCmd,
        PlanOfActionAndMilestoneCmd
    ]

    def _init_arguments(self) -> None:
        self.add_argument('-o', '--output', help='Name of the model.', required=True)
