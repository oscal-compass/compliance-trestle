# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Trestle Commands."""
import argparse
import logging
import operator
import pathlib
import traceback
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader

from trestle.core import const
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.jinja import MDCleanInclude, MDSectionInclude
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal.profile import Profile
from trestle.oscal.ssp import SystemSecurityPlan
from trestle.utils import fs, log

logger = logging.getLogger(__name__)


class JinjaCmd(CommandPlusDocs):
    """Transform an input template to an output document using jinja templating."""

    name = 'jinja'

    def _init_arguments(self):
        self.add_argument('-i', '--input', help='Input jinja template, relative to trestle root', required=True)
        self.add_argument('-o', '--output', help='Output template, relative to trestle root.', required=True)
        self.add_argument(
            '-jt', '--jinja-true', help='A jinja boolean var which needs to be passed as true', nargs='*', default=[]
        )
        self.add_argument(
            '-ssp', '--system-security-plan', help='An optional SSP to be passed', default=None, required=False
        )
        self.add_argument('-p', '--profile', help='An optional profile to be passed', default=None, required=False)

    def _run(self, args: argparse.Namespace):
        log.set_log_level_from_args(args)
        logger.debug(f'Starting {self.name} command')
        input_path = pathlib.Path(args.input)
        output_path = pathlib.Path(args.output)
        cwd = pathlib.Path.cwd()

        status = JinjaCmd.jinja_ify(
            cwd,
            pathlib.Path(args.trestle_root),
            input_path,
            output_path,
            args.jinja_true,
            args.system_security_plan,
            args.profile
        )
        logger.debug(f'Done {self.name} command')
        return status

    @staticmethod
    def jinja_ify(
        cwd: pathlib.Path,
        trestle_root: pathlib.Path,
        r_input_file: pathlib.Path,
        r_output_file: pathlib.Path,
        jinja_true: List[str],
        ssp: Optional[str],
        profile: Optional[str],
    ) -> int:
        """Run jinja over an input file with additional booleans."""
        try:
            jinja_env = Environment(
                loader=FileSystemLoader(cwd), extensions=[MDCleanInclude, MDSectionInclude], autoescape=True
            )
            template = jinja_env.get_template(str(r_input_file))
            # create boolean dict
            truths = {}
            if operator.xor(bool(ssp), bool(profile)):
                logger.error('Both SSP and profile should be provided or not at all')
                return 2
            if ssp:
                # name lookup
                ssp_data, _ = fs.load_top_level_model(trestle_root, ssp, SystemSecurityPlan)
                truths['ssp'] = ssp_data

            if profile:
                profile_data, profile_path = fs.load_top_level_model(trestle_root, profile, Profile)
                profile_resolver = ProfileResolver()
                resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
                truths['catalog'] = resolved_catalog
                truths['catalog_interface'] = CatalogInterface(resolved_catalog)

            for truth in jinja_true:
                truths[truth] = True
            output_content = template.render(**truths)
            output_file = trestle_root / r_output_file
            output_file.open('w', encoding=const.FILE_ENCODING).write(output_content)

        except Exception as e:
            logger.error(f'Unknown exception {str(e)} occured.')
            logger.debug(traceback.format_exc())
            return 1
        return 0
