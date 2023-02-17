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
"""Trestle Validate Command."""
import argparse
import logging
import pathlib

import trestle.oscal.catalog as cat
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ssp
from trestle import __version__
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.oscal import OSCAL_VERSION

logger = logging.getLogger(__name__)


class VersionCmd(CommandBase):
    """Output version info for trestle and OSCAL."""

    name = 'version'

    def _init_arguments(self) -> None:
        self.add_argument('-n', '--name', help='Name of the OSCAL object (folder name)', default=None, type=str)
        self.add_argument(
            '-t',
            '--type',
            help='Name of the OSCAL type (catalog, profile, component-definition, ssp)',
            default=None,
            type=str
        )

    def _get_version(self, type_name: str, obj_name: str, trestle_root: pathlib.Path) -> str:
        """Fetch the version of the OSCAL object from its metadata."""
        obj_type = None
        if type_name == 'profile':
            obj_type = prof.Profile
        elif type_name == 'catalog':
            obj_type = cat.Catalog
        elif type_name == 'component-definition':
            obj_type = comp.ComponentDefinition
        elif type_name == 'ssp':
            obj_type = ssp.SystemSecurityPlan
        else:
            raise TrestleError(
                f'Type is not supported {type_name}, '
                f'please select from: catalog, profile, component-definition, ssp.'
            )

        obj_path = ModelUtils.path_for_top_level_model(trestle_root, obj_name, obj_type)
        _, _, oscal_object = ModelUtils.load_distributed(obj_path, trestle_root)

        if not (oscal_object.metadata or oscal_object.metadata.version):
            raise TrestleError(
                f'Unable to determine the version. Metadata version is missing in OSCAL object: {obj_path}.'
            )

        return oscal_object.metadata.version.__root__

    def _run(self, args: argparse.Namespace) -> int:
        try:
            status = CmdReturnCodes.COMMAND_ERROR.value

            if not args.name and not args.type:
                version_string = f'Trestle version v{__version__} based on OSCAL version {OSCAL_VERSION}'
                self.out(version_string)
                status = CmdReturnCodes.SUCCESS.value

            if not (args.name and args.type) and (args.name or args.type):
                raise TrestleError('Either both arguments --name and --type should be provided or none.')

            if args.name and args.type:
                trestle_root = pathlib.Path(args.trestle_root)
                version = self._get_version(args.type, args.name, trestle_root)
                version_string = f'Version of OSCAL object of {args.name} {args.type} is: {version}.'
                self.out(version_string)
                status = CmdReturnCodes.SUCCESS.value

            return status
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error occurred when running trestle version')
