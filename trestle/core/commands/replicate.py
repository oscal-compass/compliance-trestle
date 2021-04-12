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
"""Trestle Replicate Command."""
import argparse
import logging
import pathlib
from json.decoder import JSONDecodeError
from typing import Type, TypeVar

from trestle.core import validator_helper
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.err import TrestleError
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


class CatalogCmd(CommandPlusDocs):
    """Replicate a catalog within the trestle directory structure."""

    name = 'catalog'

    def _run(self, args: argparse.Namespace) -> int:
        """Replicate a sample catalog in the trestle directory structure, given an OSCAL schema."""
        logger.info(f'Replicating catalog {args.name} to: {args.output}')
        return ReplicateCmd.replicate_object(self.name, catalog.Catalog, args)


class ProfileCmd(CommandPlusDocs):
    """Replicate a profile within the trestle directory structure."""

    name = 'profile'

    def _run(self, args: argparse.Namespace) -> int:
        logger.info(f'Replicating profile {args.name} to: {args.output}')
        return ReplicateCmd.replicate_object(self.name, profile.Profile, args)


class TargetDefinitionCmd(CommandPlusDocs):
    """Replicate a target within the trestle directory structure."""

    name = 'target-definition'

    def _run(self, args: argparse.Namespace) -> int:
        return ReplicateCmd.replicate_object(self.name, target.TargetDefinition, args)


class ComponentDefinitionCmd(CommandPlusDocs):
    """Replicate a component definition within the trestle directory structure."""

    name = 'component-definition'

    def _run(self, args: argparse.Namespace) -> int:
        return ReplicateCmd.replicate_object(self.name, component.ComponentDefinition, args)


class SystemSecurityPlanCmd(CommandPlusDocs):
    """Replicate a system security plan within the trestle directory structure."""

    name = 'system-security-plan'

    def _run(self, args: argparse.Namespace) -> int:
        return ReplicateCmd.replicate_object(self.name, ssp.SystemSecurityPlan, args)


class AssessmentPlanCmd(CommandPlusDocs):
    """Replicate an assessment plan within the trestle directory structure."""

    name = 'assessment-plan'

    def _run(self, args: argparse.Namespace) -> int:
        return ReplicateCmd.replicate_object(self.name, assessment_plan.AssessmentPlan, args)


class AssessmentResultCmd(CommandPlusDocs):
    """Replicate an assessment result within the trestle directory structure."""

    name = 'assessment-results'

    def _run(self, args: argparse.Namespace) -> int:
        return ReplicateCmd.replicate_object(self.name, assessment_results.AssessmentResults, args)


class PlanOfActionAndMilestonesCmd(CommandPlusDocs):
    """Replicate a plan of action and milestones within the trestle directory structure."""

    name = 'plan-of-action-and-milestones'

    def _run(self, args: argparse.Namespace) -> int:
        return ReplicateCmd.replicate_object(self.name, poam.PlanOfActionAndMilestones, args)


class ReplicateCmd(CommandPlusDocs):
    """Replicate a top level model within the trestle directory structure."""

    name = 'replicate'

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
        logger.debug('Init arguments')

        self.add_argument('-n', '--name', help='Name of model to replicate.', type=str, required=True)

        self.add_argument('-o', '--output', help='Name of replicated model.', type=str, required=True)

        self.add_argument(
            '-r', '--regenerate', action='store_true', help='Enable regeneration of uuids within the document'
        )

    @classmethod
    def replicate_object(cls, model_alias: str, object_type: Type[TLO], args: argparse.Namespace) -> int:
        """
        Core replicate routine invoked by subcommands.

        Args:
            model_alias: Name of the top level model in the trestle directory.
            object_type: Type of object as trestle model

        Returns:
            A return code that can be used as standard posix codes. 0 is success.

        """
        log.set_log_level_from_args(args)

        logger.debug('Entering replicate_object.')

        # 1.2 Bad working directory if not running from current working directory
        cwd = pathlib.Path.cwd().resolve()
        trestle_root = fs.get_trestle_project_root(cwd)
        if trestle_root is None:
            logger.error(f'Current working directory: {cwd} is not within a trestle project.')
            return 1

        trestle_root = trestle_root.resolve()

        plural_path = fs.model_type_to_model_dir(model_alias)

        # 1.1 Check that input file given exists.

        input_file_stem = trestle_root / plural_path / args.name / model_alias
        content_type = FileContentType.path_to_content_type(input_file_stem)
        if content_type == FileContentType.UNKNOWN:
            logger.error(f'Input file {args.name} has no json or yaml file at expected location {input_file_stem}.')
            return 1

        input_file = input_file_stem.with_suffix(FileContentType.to_file_extension(content_type))

        # 4. Distributed load from file

        try:
            model_type, model_alias, model_instance = load_distributed(input_file.resolve())
        except JSONDecodeError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.error(f'Replicate failed, JSON error loading file: {err}')
            return 1
        except TrestleError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.error(f'Replicate failed, error loading file: {err}')
            return 1
        except PermissionError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.error(f'Replicate failed, access permission error loading file: {err}')
            return 1

        rep_model_path = trestle_root / plural_path / args.output / (
            model_alias + FileContentType.to_file_extension(content_type)
        )

        if rep_model_path.exists():
            logger.error(f'OSCAL file to be replicated here: {rep_model_path} exists.')
            logger.error('Aborting trestle replicate.')
            return 1

        if args.regenerate:
            logger.debug(f'regenerating uuids for model {input_file}')
            model_instance, uuid_lut, n_refs_updated = validator_helper.regenerate_uuids(model_instance)
            logger.debug(f'{len(uuid_lut)} uuids generated and {n_refs_updated} references updated')

        # 6. Prepare actions and plan
        top_element = Element(model_instance)
        create_action = CreatePathAction(rep_model_path.resolve(), True)
        write_action = WriteFileAction(rep_model_path.resolve(), top_element, content_type)

        # create a plan to create the directory and imported file.
        replicate_plan = Plan()
        replicate_plan.add_action(create_action)
        replicate_plan.add_action(write_action)

        try:
            replicate_plan.simulate()
        except TrestleError as err:
            logger.debug(f'replicate_plan.simulate() failed: {err}')
            logger.error(f'Replicate failed, error in simulating replicate operation: {err}')
            return 1

        try:
            replicate_plan.execute()
        except TrestleError as err:
            logger.debug(f'replicate_plan.execute() failed: {err}')
            logger.error(f'Replicate failed, error in executing replication operation: {err}')
            return 1

        return 0
