# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Author commands to generate component definition as markdown and assemble to json after edit."""

import argparse
import logging
import pathlib
import shutil
from typing import Any, Dict, List, Optional

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.common.const as const
import trestle.common.log as log
import trestle.oscal.common as com
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
from trestle.common import file_utils
from trestle.common.err import TrestleError, TrestleNotFoundError, handle_generic_command_exception
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.author.profile import sections_to_dict
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_io import ParameterRep
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

logger = logging.getLogger(__name__)


class ComponentGenerate(AuthorCommonCommand):
    """Generate component in markdown form from a component in the trestle workspace."""

    name = 'component-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source component model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        self.add_argument('-o', '--output', help=const.HELP_MARKDOWN_NAME, required=True, type=str)
        self.add_argument('-y', '--yaml-header', help=const.HELP_YAML_PATH, required=False, type=str)
        self.add_argument(
            '-ohv',
            '--overwrite-header-values',
            help=const.HELP_OVERWRITE_HEADER_VALUES,
            required=False,
            action='store_true',
            default=False
        )
        self.add_argument('-s', '--sections', help=const.HELP_SECTIONS, required=False, type=str)
        self.add_argument('-rs', '--required-sections', help=const.HELP_REQUIRED_SECTIONS, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root: pathlib.Path = args.trestle_root
            if not file_utils.is_directory_name_allowed(args.output):
                raise TrestleError(f'{args.output} is not an allowed directory name')

            yaml_header: dict = {}
            if args.yaml_header:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML()
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    raise TrestleError(f'YAML error loading yaml header for ssp generation: {e}')

            # combine command line sections with any in the yaml header, with priority to command line
            sections_dict: Optional[Dict[str, str]] = None
            if args.sections:
                sections_dict = sections_to_dict(args.sections)

            component_path = trestle_root / f'components/{args.name}/component.json'

            markdown_path = trestle_root / args.output

            return self.generate_markdown(
                trestle_root,
                component_path,
                markdown_path,
                yaml_header,
                args.overwrite_header_values,
                sections_dict,
                args.required_sections
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Generation of the component markdown failed')

    def generate_markdown(
        self,
        trestle_root: pathlib.Path,
        component_path: pathlib.Path,
        markdown_path: pathlib.Path,
        yaml_header: dict,
        overwrite_header_values: bool,
        sections_dict: Optional[Dict[str, str]],
        required_sections: Optional[str]
    ) -> int:
        """Generate markdown for the controls in the component.

        Args:
            trestle_root: Root directory of the trestle workspace
            component_path: Path of the component json file
            markdown_path: Path to the directory into which the markdown will be written
            yaml_header: Dict to merge into the yaml header of the control markdown
            overwrite_header_values: Overwrite values in the markdown header but allow new items to be added
            sections_dict: Optional dict mapping section short names to long
            required_sections: Optional comma-sep list of sections that get prompted for prose if not in the component

        Returns:
            0 on success, 1 on error
        """
        try:
            if sections_dict and 'statement' in sections_dict:
                logger.warning('statement is not allowed as a section name.')
                return CmdReturnCodes.COMMAND_ERROR.value
            _, _, component = ModelUtils.load_distributed(component_path, trestle_root)
            catalog = ProfileResolver().get_resolved_profile_catalog(
                trestle_root, component_path, True, True, None, ParameterRep.LEAVE_MOUSTACHE
            )
            catalog_interface = CatalogInterface(catalog)
            catalog_interface.write_catalog_as_markdown(
                md_path=markdown_path,
                yaml_header=yaml_header,
                sections_dict=sections_dict,
                prompt_responses=False,
                additional_content=True,
                component=component,
                overwrite_header_values=overwrite_header_values,
                set_parameters=True,
                required_sections=required_sections,
                allowed_sections=None
            )
        except TrestleNotFoundError as e:
            raise TrestleError(f'Component {component_path} not found, error {e}')
        except TrestleError as e:
            raise TrestleError(f'Error generating the catalog as markdown: {e}')
        return CmdReturnCodes.SUCCESS.value


class ComponentAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Component json file."""

    name = 'component-assemble'

    def _init_arguments(self) -> None:
        name_help_str = (
            'Optional name of the component model in the trestle workspace that is being modified.  '
            'If not provided the output name is used.'
        )
        self.add_argument('-n', '--name', help=name_help_str, required=False, type=str)
        file_help_str = 'Name of the source markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Component (ok to overwrite original)'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-sp', '--set-parameters', action='store_true', help=const.HELP_SET_PARAMS, required=False)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)
        self.add_argument('-rs', '--required-sections', help=const.HELP_REQUIRED_SECTIONS, required=False, type=str)
        self.add_argument('-as', '--allowed-sections', help=const.HELP_ALLOWED_SECTIONS, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            return self.assemble_component(
                trestle_root=trestle_root,
                parent_prof_name=args.name,
                md_name=args.markdown,
                assem_comp_name=args.output,
                set_parameters=args.set_parameters,
                regenerate=args.regenerate,
                version=args.version,
                required_sections=args.required_sections,
                allowed_sections=args.allowed_sections
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Assembly of markdown to component failed')


    @staticmethod
    def assemble_component(
        trestle_root: pathlib.Path,
        parent_prof_name: str,
        md_name: str,
        assem_comp_name: str,
        set_parameters: bool,
        regenerate: bool,
        version: Optional[str],
        required_sections: Optional[str],
        allowed_sections: Optional[List[str]]
    ) -> int:
        """
        Assemble the markdown directory into a json component model file.

        Args:
            trestle_root: The trestle root directory
            parent_prof_name: Optional name of component used to generate the markdown (default is assem_comp_name)
            md_name: The name of the directory containing the markdown control files for the component
            assem_comp_name: The name of the assembled component.  It can be the same as the parent to overwrite
            set_parameters: Use the parameters in the yaml header to specify values for setparameters in the component
            regenerate: Whether to regenerate the uuid's in the component
            version: Optional version for the assembled component
            required_sections: Optional List of required sections in assembled component, as comma-separated short names
            allowed_sections: Optional list of section short names that are allowed, as comma-separated short names

        Returns:
            0 on success, 1 otherwise

        Notes:
            There must already be a component model and it will either be updated or a new json component created.
            The generated markdown has the current values for parameters of controls being imported, as set by
            the original catalog and any intermediate components.  It also shows the current SetParameters being applied
            by this component.  That list of SetParameters can be edited by changing the assigned values and adding or
            removing SetParameters from that list.  During assembly that list will be used to create the SetParameters
            in the assembled component if the --set-parameters option is specified.
        """
        md_dir = trestle_root / md_name
        if not md_dir.exists():
            raise TrestleError(f'Markdown directory {md_name} does not exist.')

        if not parent_prof_name:
            parent_prof_name = assem_comp_name

        parent_comp, parent_comp_path = ModelUtils.load_top_level_model(
            trestle_root,
            parent_prof_name,
            comp.ComponentDefinition
        )
        new_content_type = FileContentType.path_to_content_type(parent_comp_path)

        required_sections_list = required_sections.split(',') if required_sections else []

        if version:
            parent_comp.metadata.version = com.Version(__root__=version)

        assem_comp_path = ModelUtils.path_for_top_level_model(
            trestle_root, assem_comp_name, comp.ComponentDefinition, new_content_type
        )

        if assem_comp_path.exists():
            _, _, existing_prof = ModelUtils.load_distributed(assem_comp_path, trestle_root)
            if ModelUtils.models_are_equivalent(existing_prof, parent_prof):
                logger.info('Assembled component is no different from existing version, so no update.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            parent_prof, _, _ = ModelUtils.regenerate_uuids(parent_prof)
        ModelUtils.update_last_modified(parent_prof)

        if assem_comp_path.parent.exists():
            logger.info('Creating component from markdown and destination component exists, so updating.')
            shutil.rmtree(str(assem_comp_path.parent))

        assem_comp_path.parent.mkdir(parents=True, exist_ok=True)
        parent_comp.oscal_write(assem_comp_path)
        return CmdReturnCodes.SUCCESS.value
