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
from typing import Type

from trestle.core import const
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.common_types import TopLevelOscalModel
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


class AssembleCmd(CommandPlusDocs):
    """Assemble all subcomponents from a specified trestle model into a single JSON/YAML file under dist."""

    name = 'assemble'

    def _init_arguments(self) -> None:
        self.add_argument('model', help='', choices=const.MODEL_TYPE_LIST)
        self.add_argument('-n', '--name', help='Name of a single model to assemble.')
        self.add_argument('-t', '--type', action='store_true', help='Assemble all models of the given type.')
        self.add_argument(
            '-x', '--extension', help='Type of file output.', choices=['json', 'yaml', 'yml'], default='json'
        )

    def _run(self, args: argparse.Namespace) -> int:
        object_type = ElementPath(args.model).get_type()
        return self.assemble_model(args.model, object_type, args)

    @classmethod
    def assemble_model(cls, model_alias: str, object_type: Type[TopLevelOscalModel], args: argparse.Namespace) -> int:
        """Assemble a top level OSCAL model within the trestle dist directory."""
        log.set_log_level_from_args(args)
        logger.info(f'Assembling models of type {model_alias}.')

        trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.
        if not trestle_root or not fs.is_valid_project_root(args.trestle_root):
            logger.error(f'Given directory {trestle_root} is not a trestle project.')
            return 1

        model_names = []
        if 'name' in args and args.name:
            model_names = [args.name]
            logger.info(f'Assembling single model of type {model_alias}: {args.name}.')
        else:
            model_names = fs.get_models_of_type(model_alias, trestle_root)
            nmodels = len(model_names)
            logger.info(f'Assembling {nmodels} found models of type {model_alias}.')
        if len(model_names) == 0:
            logger.info(f'No models found to assemble of type {model_alias}.')
            return 0

        for model_name in model_names:
            # contruct path to the model file name
            root_model_dir = trestle_root / fs.model_type_to_model_dir(model_alias)
            try:
                model_file_type = fs.get_contextual_file_type(root_model_dir / model_name)
            except Exception as e:
                logger.error('No files found in the specified model directory.')
                logger.debug(e)
                return 1

            model_file_name = f'{model_alias}{FileContentType.to_file_extension(model_file_type)}'
            root_model_filepath = root_model_dir / model_name / model_file_name

            if not root_model_filepath.exists():
                logger.error(f'No top level model file at {root_model_dir}')
                return 1

            # distributed load
            _, _, assembled_model = load_distributed(root_model_filepath, args.trestle_root)
            plural_alias = fs.model_type_to_model_dir(model_alias)

            assembled_model_dir = trestle_root / const.TRESTLE_DIST_DIR / plural_alias

            assembled_model_filepath = assembled_model_dir / f'{model_name}.{args.extension}'

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
            except Exception as e:
                logger.error('Unknown error executing trestle create operations. Rolling back.')
                logger.debug(e)
                return 1
        return 0
