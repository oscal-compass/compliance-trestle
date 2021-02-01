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
"""Trestle Assemble Command."""

import argparse
import logging
from pathlib import Path
from typing import Type, TypeVar

from ilcli import Command  # type: ignore

from trestle.core import const
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal import assessment_plan
from trestle.oscal import assessment_results
from trestle.oscal import catalog
from trestle.oscal import component
from trestle.oscal import poam
from trestle.oscal import profile
from trestle.oscal import ssp
from trestle.oscal import target
from trestle.utils import fs
from trestle.utils import log
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)

TLO = TypeVar(
    'TLO',
    assessment_plan.AssessmentPlan,
    assessment_results.AssessmentResults,
    catalog.Catalog,
    component.ComponentDefinition,
    poam.PlanOfActionAndMilestones,
    profile.Profile,
    ssp.SystemSecurityPlan,
    target.TargetDefinition
)


class CatalogCmd(Command):
    """Assemble a catalog."""

    name = 'catalog'

    def _run(self, args: argparse.Namespace) -> int:
        """Assemble a catalog."""
        logger.info(f'Assembling catalog titled: {args.name}')
        return AssembleCmd.assemble_model(self.name, catalog.Catalog, args)


class ProfileCmd(Command):
    """Assemble a profile."""

    name = 'profile'

    def _run(self, args: argparse.Namespace) -> int:
        logger.info(f'Assembling profile titled: {args.name}')
        return AssembleCmd.assemble_model(self.name, profile.Profile, args)


class TargetDefinitionCmd(Command):
    """Assemble a target definition."""

    name = 'target-definition'

    def _run(self, args: argparse.Namespace) -> int:
        return AssembleCmd.assemble_model(self.name, target.TargetDefinition, args)


class ComponentDefinitionCmd(Command):
    """Assemble a component definition."""

    name = 'component-definition'

    def _run(self, args: argparse.Namespace) -> int:
        return AssembleCmd.assemble_model(self.name, component.ComponentDefinition, args)


class SystemSecurityPlanCmd(Command):
    """Assemble a system security plan."""

    name = 'system-security-plan'

    def _run(self, args: argparse.Namespace) -> int:
        return AssembleCmd.assemble_model(self.name, ssp.SystemSecurityPlan, args)


class AssessmentPlanCmd(Command):
    """Assemble a  assessment plan."""

    name = 'assessment-plan'

    def _run(self, args: argparse.Namespace) -> int:
        return AssembleCmd.assemble_model(self.name, assessment_plan.AssessmentPlan, args)


class AssessmentResultCmd(Command):
    """Assemble a  assessment result."""

    name = 'assessment-results'

    def _run(self, args: argparse.Namespace) -> int:
        return AssembleCmd.assemble_model(self.name, assessment_results.AssessmentResults, args)


class PlanOfActionAndMilestonesCmd(Command):
    """Assemble a plan of action and milestones."""

    name = 'plan-of-action-and-milestones'

    def _run(self, args: argparse.Namespace) -> int:
        return AssembleCmd.assemble_model(self.name, poam.PlanOfActionAndMilestones, args)


class AssembleCmd(Command):
    """Assemble all subcomponents from a specified trestle model into a single JSON/YAML file under dist."""

    name = 'assemble'

    subcommands = [
        CatalogCmd,
        ProfileCmd,
        TargetDefinitionCmd,
        ComponentDefinitionCmd,
        SystemSecurityPlanCmd,
        AssessmentPlanCmd,
        AssessmentResultCmd,
        PlanOfActionAndMilestonesCmd
    ]

    def _init_arguments(self) -> None:
        self.add_argument('-n', '--name', help='Name of the model to assemble.', required=True)
        self.add_argument(
            '-x', '--extension', help='Type of file output.', choices=['json', 'yaml', 'yml'], default='json'
        )

    @classmethod
    def assemble_model(cls, model_alias: str, object_type: Type[TLO], args: argparse.Namespace) -> int:
        """Assemble a top level OSCAL model within the trestle dist directory."""
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(Path.cwd())
        if not trestle_root:
            logger.error(f'Current working directory {Path.cwd()} is not with a trestle project.')
            return 1
        if not trestle_root == Path.cwd():
            logger.error(f'Current working directory {Path.cwd()} is not the top level trestle project directory.')
            return 1

        # contruct path to the model file name
        root_model_dir = Path.cwd() / f'{model_alias}s'
        try:
            model_file_type = fs.get_contextual_file_type(root_model_dir / args.name)
        except Exception as e:
            logger.error('No files found in the specified model directory.')
            logger.debug(e)
            return 1

        model_file_name = f'{model_alias}{FileContentType.to_file_extension(model_file_type)}'
        root_model_filepath = root_model_dir / args.name / model_file_name

        if not root_model_filepath.exists():
            logger.error(f'No top level model file at {root_model_dir}')
            return 1

        # distributed load
        _, _, assembled_model = load_distributed(root_model_filepath)
        assembled_model_dir = trestle_root / const.TRESTLE_DIST_DIR / f'{model_alias}s'
        assembled_model_filepath = assembled_model_dir / f'{args.name}.{args.extension}'

        plan = Plan()
        plan.add_action(CreatePathAction(assembled_model_filepath, True))
        plan.add_action(
            WriteFileAction(
                assembled_model_filepath,
                Element(assembled_model),
                FileContentType.to_content_type(f'.{args.extension}')
            )
        )

        try:
            plan.simulate()
            plan.execute()
            return 0
        except Exception as e:
            logger.error('Unknown error executing trestle create operations. Rolling back.')
            logger.debug(e)
            return 1
