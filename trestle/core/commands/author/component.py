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
from uuid import uuid4

import trestle.common.const as const
import trestle.common.log as log
import trestle.oscal.common as com
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
from trestle.common import file_utils
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.common.list_utils import as_list
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_interface import ContextPurpose, ControlContext
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal import OSCAL_VERSION

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

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = args.trestle_root
            markdown_dir_name = args.output
            profile_name = args.profile
            component_name = args.name

            return self.component_generate_all(
                trestle_root, component_name, profile_name, markdown_dir_name, {}, None, False
            )

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Generation of the component markdown failed')

    def component_generate_all(
        self,
        trestle_root: pathlib.Path,
        comp_def_name: str,
        profile_name: str,
        markdown_dir_name: str,
        yaml_header: Dict[str, Any],
        sections_dict: Optional[Dict[str, str]],
        overwrite_header_values: bool
    ) -> int:
        """Generate markdown for all components in comp def."""
        if not file_utils.is_directory_name_allowed(markdown_dir_name):
            raise TrestleError(f'{markdown_dir_name} is not an allowed directory name')
        md_path = trestle_root / markdown_dir_name
        md_path.mkdir(parents=True, exist_ok=True)
        component_def, _ = load_validate_model_name(trestle_root, comp_def_name, comp.ComponentDefinition)
        for component in as_list(component_def.components):
            rc = self.component_generate_by_name(
                trestle_root,
                comp_def_name,
                component.title,
                profile_name,
                md_path / component.title,
                yaml_header,
                sections_dict,
                overwrite_header_values
            )
            if rc != CmdReturnCodes.SUCCESS.value:
                return rc
        return CmdReturnCodes.SUCCESS.value

    def component_generate_by_name(
        self,
        trestle_root: pathlib.Path,
        comp_def_name: str,
        comp_name: str,
        profile_name: str,
        markdown_dir_path: pathlib.Path,
        yaml_header: dict,
        sections_dict: Optional[Dict[str, str]],
        overwrite_header_values: bool
    ) -> int:
        """Create markdown based on the component and profile."""
        profile_path = ModelUtils.full_path_for_top_level_model(trestle_root, profile_name, prof.Profile)
        profile_resolver = ProfileResolver()
        resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
        catalog_interface = CatalogInterface(resolved_catalog)
        comp_def, _ = load_validate_model_name(trestle_root, comp_def_name, comp.ComponentDefinition)
        context = ControlContext.generate(ContextPurpose.COMPONENT, True, trestle_root, markdown_dir_path)
        context.sections_dict = sections_dict
        context.prompt_responses = True
        context.overwrite_header_values = overwrite_header_values
        context.comp_def = comp_def
        context.comp_name = comp_name
        catalog_interface.write_catalog_as_markdown(context)

        return CmdReturnCodes.SUCCESS.value


class ComponentAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Component json file."""

    name = 'component-assemble'

    def _init_arguments(self) -> None:
        name_help_str = (
            'Optional name of the component-definition model in the trestle workspace that is being modified.  '
            'If not provided the output name is used.'
        )
        self.add_argument('-n', '--name', help=name_help_str, required=False, type=str)
        file_help_str = 'Name of the source markdown directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json component-definition (ok to overwrite original)'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            return self.assemble_component(
                trestle_root=trestle_root,
                parent_comp_name=args.name,
                md_name=args.markdown,
                assem_comp_name=args.output,
                regenerate=args.regenerate,
                version=args.version,
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Assembly of markdown to component-definition failed')

    @staticmethod
    def assemble_component(
        trestle_root: pathlib.Path,
        parent_comp_name: Optional[str],
        md_name: str,
        assem_comp_name: str,
        regenerate: bool,
        version: Optional[str],
    ) -> int:
        """
        Assemble the markdown directory into a json component-definition model file.

        Args:
            trestle_root: The trestle root directory
            parent_comp_name: Optional name of component-definition used to generate markdown, default = assem_comp_name
            md_name: The name of the directory containing the markdown control files for the component
            assem_comp_name: The name of the assembled component-definiton.  Can be same as the parent to overwrite
            regenerate: Whether to regenerate the uuid's in the component
            version: Optional version for the assembled component

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

        if not parent_comp_name:
            parent_comp_name = assem_comp_name

        # load the comp-def that will be updated
        parent_comp, parent_comp_path = ModelUtils.load_top_level_model(
            trestle_root,
            parent_comp_name,
            comp.ComponentDefinition
        )
        new_content_type = FileContentType.path_to_content_type(parent_comp_path)

        context = ControlContext.generate(ContextPurpose.COMPONENT, False, trestle_root, md_dir)

        ComponentAssemble.assemble_comp_def_into_parent(trestle_root, parent_comp, md_dir, context)

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

    @staticmethod
    def assemble_comp_def_into_parent(
        trestle_root: pathlib.Path,
        parent_comp: comp.ComponentDefinition,
        md_dir: pathlib.Path,
        context: ControlContext
    ) -> None:
        """Assemble markdown content into provided component-definition model."""
        # find the needed list of comps
        sub_dirs = md_dir.glob('*')
        comp_names = [sub_dir.name for sub_dir in sub_dirs if sub_dir.is_dir()]

        # make sure parent has list of comps to work with - possibly empty
        if not parent_comp.components:
            parent_comp.components = []

        # remove any unneeded comps from parent comp_def
        kill_list: List[int] = []
        for ii, component in enumerate(parent_comp.components):
            if component.title not in comp_names:
                kill_list.append(ii)
        if kill_list:
            del parent_comp.components[kill_list]

        # create new comps if needed
        existing_comp_names = [component.title for component in parent_comp.components]
        for comp_name in comp_names:
            if comp_name not in existing_comp_names:
                metadata = com.Metadata(
                    title=comp_name, last_modified='REPLACE_ME', version='REPLACE_ME', oscal_version=OSCAL_VERSION
                )
                parent_comp.components.append(
                    comp.DefinedComponent(uuid=str(uuid4()), title=comp_name, metadata=metadata)
                )

        for component in parent_comp.components:
            ComponentAssemble._update_component_with_markdown(md_dir, component, context)

    @staticmethod
    def _update_component_with_markdown(
        md_dir: pathlib.Path, component: comp.DefinedComponent, context: ControlContext
    ) -> None:
        #
        md_path = md_dir / component.title
        avail_comps = {component.title: component}
        cat_interface = CatalogInterface()
        imp_reqs = cat_interface.read_catalog_imp_reqs(md_path, avail_comps, context)
        # FIXME next needs work
        if False:
            component.control_implementations[0].implemented_requirements = imp_reqs
