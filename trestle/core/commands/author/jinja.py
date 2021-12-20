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
import uuid
from typing import Any, Dict, Optional

from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader

from ruamel.yaml import YAML

from trestle.core import const
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.jinja import MDCleanInclude, MDSectionInclude
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.ssp_io import SSPMarkdownWriter
from trestle.oscal.profile import Profile
from trestle.oscal.ssp import SystemSecurityPlan
from trestle.utils import fs, log

logger = logging.getLogger(__name__)


class JinjaCmd(CommandPlusDocs):
    """Transform an input template to an output document using jinja templating."""

    max_recursion_depth = 2

    name = 'jinja'

    def _init_arguments(self):
        self.add_argument('-i', '--input', help='Input jinja template, relative to trestle root', required=True)
        self.add_argument('-o', '--output', help='Output template, relative to trestle root.', required=True)
        self.add_argument(
            '-lut',
            '--look-up-table',
            help='Key-value pair table, stored as yaml, to be passed to jinja as variables',
            required=False
        )
        self.add_argument(
            '-elp',
            '--external-lut-prefix',
            help='Prefix paths for LUT, to maintain compatibility with other templating systems',
            required=False
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

        if args.look_up_table:
            lut_table = pathlib.Path(args.look_up_table)
            lookup_table_path = pathlib.Path.cwd() / lut_table
            lut = JinjaCmd.load_LUT(lookup_table_path, args.external_lut_prefix)
            status = JinjaCmd.jinja_ify(
                pathlib.Path(args.trestle_root), input_path, output_path, args.system_security_plan, args.profile, lut
            )
        else:
            status = JinjaCmd.jinja_ify(
                pathlib.Path(args.trestle_root), input_path, output_path, args.system_security_plan, args.profile
            )
        logger.debug(f'Done {self.name} command')
        return status

    @staticmethod
    def load_LUT(path: pathlib.Path, prefix: Optional[str]) -> Dict[str, Any]:  # noqa: N802
        """Load a Yaml lookup table from file."""
        yaml = YAML()
        lut = yaml.load(path.open('r', encoding=const.FILE_ENCODING))
        if prefix:
            prefixes = prefix.split('.')
            while prefixes:
                old_lut = lut
                lut[prefixes.pop(-1)] = old_lut

        return lut

    @staticmethod
    def jinja_ify(
        trestle_root: pathlib.Path,
        r_input_file: pathlib.Path,
        r_output_file: pathlib.Path,
        ssp: Optional[str],
        profile: Optional[str],
        lut: Optional[Dict[str, Any]] = None
    ) -> int:
        """Run jinja over an input file with additional booleans."""
        try:
            if lut is None:
                lut = {}
            template_folder = pathlib.Path.cwd()
            jinja_env = Environment(
                loader=FileSystemLoader(template_folder),
                extensions=[MDSectionInclude, MDCleanInclude],
                trim_blocks=True,
                autoescape=True
            )
            template = jinja_env.get_template(str(r_input_file))
            # create boolean dict
            if operator.xor(bool(ssp), bool(profile)):
                logger.error('Both SSP and profile should be provided or not at all')
                return 2
            if ssp:
                # name lookup
                ssp_data, _ = fs.load_top_level_model(trestle_root, ssp, SystemSecurityPlan)
                lut['ssp'] = ssp_data
                _, profile_path = fs.load_top_level_model(trestle_root, profile, Profile)
                profile_resolver = ProfileResolver()
                resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)

                ssp_writer = SSPMarkdownWriter(trestle_root)
                ssp_writer.set_ssp(ssp_data)
                ssp_writer.set_catalog(resolved_catalog)
                lut['catalog'] = resolved_catalog
                lut['catalog_interface'] = CatalogInterface(resolved_catalog)
                lut['ssp_md_writer'] = ssp_writer

            new_output = template.render(**lut)
            output = ''
            # This recursion allows nesting within expressions (e.g. an expression can contain jinja templates).
            error_countdown = JinjaCmd.max_recursion_depth
            while new_output != output and error_countdown > 0:
                error_countdown = error_countdown - 1
                output = new_output
                random_name = uuid.uuid4()  # Should be random and not used.
                dict_loader = DictLoader({str(random_name): new_output})
                jinja_env = Environment(
                    loader=ChoiceLoader([dict_loader, FileSystemLoader(template_folder)]),
                    extensions=[MDCleanInclude, MDSectionInclude],
                    autoescape=True,
                    trim_blocks=True
                )
                template = jinja_env.get_template(str(random_name))
                new_output = template.render(**lut)

            output_file = trestle_root / r_output_file
            output_file.open('w', encoding=const.FILE_ENCODING).write(output)

        except Exception as e:  # pragma: no cover
            logger.error(f'Unknown exception {str(e)} occured.')
            logger.debug(traceback.format_exc())
            return 1
        return 0
