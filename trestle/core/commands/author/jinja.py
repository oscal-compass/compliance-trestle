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
import re
import uuid
from typing import Any, Dict, Optional

from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader, Template

from ruamel.yaml import YAML

from trestle.common import const, log
from trestle.common.err import TrestleIncorrectArgsError, handle_generic_command_exception
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_io import ControlIOWriter
from trestle.core.jinja import MDCleanInclude, MDDatestamp, MDSectionInclude
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.ssp_io import SSPMarkdownWriter
from trestle.oscal.profile import Profile
from trestle.oscal.ssp import SystemSecurityPlan

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
            '-nc',
            '--number-captions',
            help='Add incremental numbering to table and image captions, in the form Table n - ... and Figure n - ...',
            action='store_true'
        )
        self.add_argument(
            '-pf',
            '--param-formatting',
            help='Add given text to each parameter, '
            'use dot to specify location of parameter (i.e. foo.bar will wrap param with foo and bar)',
            required=False
        )
        self.add_argument(
            '-ssp', '--system-security-plan', help='An optional SSP to be passed', default=None, required=False
        )
        self.add_argument('-p', '--profile', help='An optional profile to be passed', default=None, required=False)
        self.add_argument(
            '-dp',
            '--docs-profile',
            help='Output profile controls to separate markdown files',
            action='store_true',
            required=False
        )

    def _run(self, args: argparse.Namespace):
        try:
            log.set_log_level_from_args(args)
            logger.debug(f'Starting {self.name} command')
            input_path = pathlib.Path(args.input)
            output_path = pathlib.Path(args.output)
            if args.system_security_plan and args.docs_profile:
                raise TrestleIncorrectArgsError('Output to multiple files is possible with profile only.')

            if args.docs_profile and not args.profile:
                raise TrestleIncorrectArgsError('Profile must be provided to output to multiple files.')

            lut = {}
            if args.look_up_table:
                lut_table = pathlib.Path(args.look_up_table)
                lookup_table_path = pathlib.Path.cwd() / lut_table
                lut = JinjaCmd.load_LUT(lookup_table_path, args.external_lut_prefix)

            if args.system_security_plan:
                return JinjaCmd.jinja_ify(
                    pathlib.Path(args.trestle_root),
                    input_path,
                    output_path,
                    args.system_security_plan,
                    args.profile,
                    lut,
                    number_captions=args.number_captions,
                    parameters_formatting=args.param_formatting
                )
            elif args.profile and args.docs_profile:
                return JinjaCmd.jinja_multiple_md(
                    pathlib.Path(args.trestle_root),
                    input_path,
                    output_path,
                    args.profile,
                    lut,
                    parameters_formatting=args.param_formatting
                )

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while generating markdown via Jinja template')

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
        lut: Dict[str, Any],
        number_captions: Optional[bool] = False,
        parameters_formatting: Optional[str] = None
    ) -> int:
        """Run jinja over an input file with additional booleans."""
        template_folder = pathlib.Path.cwd()
        jinja_env = Environment(
            loader=FileSystemLoader(template_folder),
            extensions=[MDSectionInclude, MDCleanInclude, MDDatestamp],
            trim_blocks=True,
            autoescape=True
        )
        template = jinja_env.get_template(str(r_input_file))
        # create boolean dict
        if operator.xor(bool(ssp), bool(profile)):
            raise TrestleIncorrectArgsError('Both SSP and profile should be provided or not at all')

        if ssp:
            # name lookup
            ssp_data, _ = ModelUtils.load_top_level_model(trestle_root, ssp, SystemSecurityPlan)
            lut['ssp'] = ssp_data
            _, profile_path = ModelUtils.load_top_level_model(trestle_root, profile, Profile)
            profile_resolver = ProfileResolver()
            resolved_catalog = profile_resolver.get_resolved_profile_catalog(
                trestle_root, profile_path, False, False, parameters_formatting
            )

            ssp_writer = SSPMarkdownWriter(trestle_root)
            ssp_writer.set_ssp(ssp_data)
            ssp_writer.set_catalog(resolved_catalog)
            lut['catalog'] = resolved_catalog
            lut['catalog_interface'] = CatalogInterface(resolved_catalog)
            lut['control_io_writer'] = ControlIOWriter()
            lut['ssp_md_writer'] = ssp_writer

            output = JinjaCmd.render_template(template, lut, template_folder)

            output_file = trestle_root / r_output_file
            if number_captions:
                output_file.open('w', encoding=const.FILE_ENCODING).write(_number_captions(output))
            else:
                output_file.open('w', encoding=const.FILE_ENCODING).write(output)

            return CmdReturnCodes.SUCCESS.value

    @staticmethod
    def jinja_multiple_md(
        trestle_root: pathlib.Path,
        r_input_file: pathlib.Path,
        r_output_file: pathlib.Path,
        profile: Optional[str],
        lut: Dict[str, Any],
        parameters_formatting: Optional[str] = None
    ) -> int:
        """Output profile as multiple markdown files using Jinja."""
        template_folder = pathlib.Path.cwd()

        # Output to multiple markdown files
        _, profile_path = ModelUtils.load_top_level_model(trestle_root, profile, Profile)
        profile_resolver = ProfileResolver()
        resolved_catalog = profile_resolver.get_resolved_profile_catalog(
            trestle_root, profile_path, False, False, parameters_formatting
        )
        catalog_interface = CatalogInterface(resolved_catalog)

        # Generate a single markdown page for each control per each group
        for group in catalog_interface.get_all_groups_from_catalog():
            for control in catalog_interface.get_sorted_controls_in_group(group.id):
                _, group_title, _ = catalog_interface.get_group_info_by_control(control.id)
                group_dir = r_output_file
                control_path = catalog_interface.get_control_path(control.id)
                for sub_dir in control_path:
                    group_dir = group_dir / sub_dir
                    if not group_dir.exists():
                        group_dir.mkdir(parents=True, exist_ok=True)

                control_writer = ControlIOWriter()

                jinja_env = Environment(
                    loader=FileSystemLoader(template_folder),
                    extensions=[MDSectionInclude, MDCleanInclude, MDDatestamp],
                    trim_blocks=True,
                    autoescape=True
                )
                template = jinja_env.get_template(str(r_input_file))
                lut['catalog_interface'] = catalog_interface
                lut['control_writer'] = control_writer
                lut['control'] = control
                lut['profile'] = profile
                lut['group_title'] = group_title
                output = JinjaCmd.render_template(template, lut, template_folder)

                output_file = trestle_root / group_dir / pathlib.Path(control.id + '.md')
                output_file.open('w', encoding=const.FILE_ENCODING).write(output)

        return CmdReturnCodes.SUCCESS.value

    @staticmethod
    def render_template(template: Template, lut: Dict[str, Any], template_folder: pathlib.Path) -> str:
        """Render template."""
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
                extensions=[MDCleanInclude, MDSectionInclude, MDDatestamp],
                autoescape=True,
                trim_blocks=True
            )
            template = jinja_env.get_template(str(random_name))
            new_output = template.render(**lut)

        return output


def _number_captions(md_body: str) -> str:
    """Incrementally number tables and image captions."""
    images = {}
    tables = {}
    output = md_body.splitlines()

    for index, line in enumerate(output):
        if re.match(r'!\[.+\]\(.+\)', line):
            images[index] = line
        if output[index].lower().startswith('table: '):
            tables[index] = line

    for index, row in enumerate(tables):
        output[row] = f'Table: Table {index + 1} - {tables[row].split(": ")[1]}'

    for index, row in enumerate(images):
        output[row] = images[row].replace('![', f'![Figure {index + 1} - ')

    return '\n'.join(output)
