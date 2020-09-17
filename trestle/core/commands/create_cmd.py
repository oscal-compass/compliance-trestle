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

from ilcli import Command


class Catalog(Command):
    """Create a sample catalog."""

    name = 'catalog'


class Profile(Command):
    """Create a sample profile."""

    name = 'profile'


class TargetDefinition(Command):
    """Create a sample target definition."""

    name = 'target-definition'


class ComponentDefinition(Command):
    """Create a sample component definition."""

    name = 'component-definition'


class SystemSecurityPlan(Command):
    """Create a sample system security plan."""

    name = 'system-security-plan'


class AssessmentPlan(Command):
    """Create a sample assessment plan."""

    name = 'assessment-plan'


class AssessmentResult(Command):
    """Create a sample assessment result."""

    name = 'assessment-result'


class PlanOfActionAndMilestone(Command):
    """Create a sample plan of action and milestone result."""

    name = 'plan-of-action-and-milestone'


class Create(Command):
    """Create a sample trestle model."""

    subcommands = [
        Catalog,
        Profile,
        TargetDefinition,
        ComponentDefinition,
        SystemSecurityPlan,
        AssessmentPlan,
        AssessmentResult,
        PlanOfActionAndMilestone
    ]
