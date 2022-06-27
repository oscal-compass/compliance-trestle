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
from typing import Dict, List, Optional

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.common.const as const
import trestle.common.log as log
import trestle.oscal.common as com
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
from trestle.common import file_utils
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.author.profile import sections_to_dict
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

logger = logging.getLogger(__name__)


class ComponentGenerate(AuthorCommonCommand):
    """Generate component in markdown form from a component in the trestle workspace."""

    name = 'component-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source component model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        profile_help_str = 'Name of the profile model in the trestle workspace'
        self.add_argument('-p', '--profile', help=profile_help_str, required=True, type=str)
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
            trestle_root = args.trestle_root
            markdown_dir_name = args.output
            profile_name = args.profile
            component_name = args.name
            sections_dict = sections_to_dict(args.sections)
            yaml_header: dict = {}
            if args.yaml_header:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML()
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    raise TrestleError(f'YAML error loading yaml header for ssp generation: {e}')

            return self.component_generate(
                trestle_root,
                component_name,
                profile_name,
                markdown_dir_name,
                yaml_header,
                sections_dict,
                args.overwrite_header_values
            )

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Generation of the component markdown failed')

    def component_generate(
        self,
        trestle_root: pathlib.Path,
        component_name: str,
        profile_name: str,
        markdown_dir_name: str,
        yaml_header: dict,
        sections_dict: Optional[Dict[str, str]],
        overwrite_header_values: bool
    ) -> int:
        """Create markdown based on the component and profile."""
        if not file_utils.is_directory_name_allowed(markdown_dir_name):
            raise TrestleError(f'{markdown_dir_name} is not an allowed directory name')

        markdown_path = trestle_root / markdown_dir_name
        profile_path = ModelUtils.full_path_for_top_level_model(trestle_root, profile_name, prof.Profile)
        profile_resolver = ProfileResolver()
        resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
        catalog_interface = CatalogInterface(resolved_catalog)
        component, _ = load_validate_model_name(trestle_root, component_name, comp.ComponentDefinition)

        catalog_interface.write_catalog_as_markdown(
            md_path=markdown_path,
            yaml_header=yaml_header,
            sections_dict=sections_dict,
            prompt_responses=True,
            additional_content=False,
            profile=None,
            overwrite_header_values=overwrite_header_values,
            set_parameters=False,
            required_sections=None,
            allowed_sections=None,
            component=component
        )
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

        if version:
            parent_comp.metadata.version = com.Version(__root__=version)

        assem_comp_path = ModelUtils.path_for_top_level_model(
            trestle_root, assem_comp_name, comp.ComponentDefinition, new_content_type
        )

        if assem_comp_path.exists():
            _, _, existing_comp = ModelUtils.load_distributed(assem_comp_path, trestle_root)
            if ModelUtils.models_are_equivalent(existing_comp, parent_comp):
                logger.info('Assembled component is no different from existing version, so no update.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            parent_comp, _, _ = ModelUtils.regenerate_uuids(parent_comp)
        ModelUtils.update_last_modified(parent_comp)

        if assem_comp_path.parent.exists():
            logger.info('Creating component from markdown and destination component exists, so updating.')
            shutil.rmtree(str(assem_comp_path.parent))

        assem_comp_path.parent.mkdir(parents=True, exist_ok=True)
        parent_comp.oscal_write(assem_comp_path)
        return CmdReturnCodes.SUCCESS.value
