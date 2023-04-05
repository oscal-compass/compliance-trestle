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
from typing import Dict, Optional, Tuple
from uuid import uuid4

import trestle.common.const as const
import trestle.common.log as log
import trestle.oscal.component as comp
from trestle.common import file_utils
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.common.list_utils import as_list, deep_get
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_api import CatalogAPI
from trestle.core.catalog.catalog_reader import CatalogReader
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.cmd_utils import clear_folder
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import ControlInterface
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.remote.cache import FetcherFactory

logger = logging.getLogger(__name__)


class ComponentGenerate(AuthorCommonCommand):
    """Generate component in markdown form from a component in the trestle workspace."""

    name = 'component-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source component model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        self.add_argument(
            '-o', '--output', help='Name of the output generated component markdown folder', required=True, type=str
        )  # noqa E501
        self.add_argument('-fo', '--force-overwrite', help=const.HELP_FO_OUTPUT, required=False, action='store_true')

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)

            if args.force_overwrite:
                try:
                    logger.info(f'Overwriting the content in {args.output} folder.')
                    clear_folder(pathlib.Path(args.output))
                except TrestleError as e:  # pragma: no cover
                    raise TrestleError(f'Unable to overwrite contents in {args.output} folder: {e}')

            return self.component_generate_all(args.trestle_root, args.name, args.output)

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Generation of the component markdown failed')

    def component_generate_all(self, trestle_root: pathlib.Path, comp_def_name: str, markdown_dir_name: str) -> int:
        """Generate markdown for all components in comp def."""
        if not file_utils.is_directory_name_allowed(markdown_dir_name):
            raise TrestleError(f'{markdown_dir_name} is not an allowed directory name')
        md_path = trestle_root / markdown_dir_name
        md_path.mkdir(parents=True, exist_ok=True)
        component_def, _ = load_validate_model_name(trestle_root, comp_def_name, comp.ComponentDefinition)

        context = ControlContext.generate(ContextPurpose.COMPONENT, True, trestle_root, md_path)
        context.prompt_responses = True
        context.comp_def = component_def

        rc = CmdReturnCodes.SUCCESS.value
        for component in as_list(component_def.components):
            rc = self.component_generate_by_name(context, component, md_path / component.title)
            if rc != CmdReturnCodes.SUCCESS.value:
                break
        return rc

    @staticmethod
    def _get_name_from_uri(source_uri: str) -> str:
        """Get the name from a source profile or catalog source uri."""
        uri_type = FetcherFactory.get_uri_type(source_uri)
        if uri_type == FetcherFactory.UriType.TRESTLE:
            return source_uri.split('/')[-2]
        return ''

    def component_generate_by_name(
        self, context: ControlContext, component: comp.DefinedComponent, markdown_dir_path: pathlib.Path
    ) -> int:
        """Create markdown for the component using its source profiles."""
        logger.info(f'Generating markdown for component {component.title}')
        context.comp_name = component.title
        context.component = component
        context.uri_name_map = {}
        cat_api_dict: Dict[str, CatalogAPI] = {}
        name_index = 1
        for control_imp in as_list(component.control_implementations):
            context.control_implementation = control_imp
            source_profile_uri = control_imp.source
            # get the resolved profile catalog for this source, generating it if not already created
            if source_profile_uri not in cat_api_dict:
                name = ComponentGenerate._get_name_from_uri(source_profile_uri)
                if not name:
                    name = f'source_{name_index:03d}'
                    name_index += 1
                context.uri_name_map[source_profile_uri] = name
                resolved_catalog = ProfileResolver.get_resolved_profile_catalog(
                    context.trestle_root, source_profile_uri
                )
                local_catalog_api = CatalogAPI(resolved_catalog)
                cat_api_dict[source_profile_uri] = local_catalog_api
            else:
                local_catalog_api = cat_api_dict[source_profile_uri]
            # insert the profile title (from title of resolved catalog) into the yaml header so it appears in md
            # different controls in the final catalog may have different profile titles if from different control_imps
            context.cli_yaml_header = {}
            context.cli_yaml_header[const.TRESTLE_GLOBAL_TAG] = {}

            profile_title = local_catalog_api._catalog_interface.get_catalog_title()
            profile_header = {'title': profile_title, 'href': source_profile_uri}
            context.cli_yaml_header[const.TRESTLE_GLOBAL_TAG][const.PROFILE] = profile_header

            sub_dir_name = context.uri_name_map[source_profile_uri]
            context.md_root = markdown_dir_path / sub_dir_name
            # write controls corresponding to this source catalog
            # if two controlimps load the same control, the second one will merge into the first
            # otherwise the full catalog will be written in subsets by control_imp
            # if an imp_req has a set param also in the control_imp. the imp_req value is used for the control
            cat_api_dict[source_profile_uri].update_context(context)
            cat_api_dict[source_profile_uri].write_catalog_as_markdown()
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
            return self.assemble_component(
                trestle_root=args.trestle_root,
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
        parent_comp, parent_comp_path = ModelUtils.load_model_for_class(
            trestle_root,
            parent_comp_name,
            comp.ComponentDefinition
        )
        new_content_type = FileContentType.path_to_content_type(parent_comp_path)

        context = ControlContext.generate(ContextPurpose.COMPONENT, False, trestle_root, md_dir)

        ComponentAssemble.assemble_comp_def_into_parent(parent_comp, md_dir, context)

        if version:
            parent_comp.metadata.version = version

        assem_comp_path = ModelUtils.get_model_path_for_name_and_class(
            trestle_root, assem_comp_name, comp.ComponentDefinition, new_content_type
        )

        if not version and assem_comp_path.exists():
            _, _, existing_comp = ModelUtils.load_distributed(assem_comp_path, trestle_root)
            # comp def will change statement uuids so need to ignore them in comparison
            if ModelUtils.models_are_equivalent(existing_comp, parent_comp, True):
                logger.info('Assembled component definition is no different from existing version, so no update.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            parent_comp, _, _ = ModelUtils.regenerate_uuids(parent_comp)
        ModelUtils.update_last_modified(parent_comp)

        if assem_comp_path.parent.exists():
            logger.info(
                'Creating component definition from markdown and destination component definition exists, so updating.'
            )  # noqa E501
            shutil.rmtree(str(assem_comp_path.parent))

        assem_comp_path.parent.mkdir(parents=True, exist_ok=True)
        parent_comp.oscal_write(assem_comp_path)
        return CmdReturnCodes.SUCCESS.value

    @staticmethod
    def assemble_comp_def_into_parent(
        parent_comp: comp.ComponentDefinition, md_dir: pathlib.Path, context: ControlContext
    ) -> None:
        """Assemble markdown content into provided component-definition model."""
        # find the needed list of comps
        sub_dirs = file_utils.iterdir_without_hidden_files(md_dir)
        comp_names = [sub_dir.name for sub_dir in sub_dirs if sub_dir.is_dir()]

        # make sure parent has list of comps to work with - possibly empty
        if not parent_comp.components:
            parent_comp.components = []

        parent_comp.components[:] = [comp for comp in parent_comp.components if comp.title in comp_names]

        # create new comps if needed
        existing_comp_names = [component.title for component in parent_comp.components]
        for comp_name in comp_names:
            if comp_name not in existing_comp_names:
                parent_comp.components.append(
                    comp.DefinedComponent(
                        uuid=str(uuid4()), title=comp_name, type=const.REPLACE_ME, description=const.REPLACE_ME
                    )
                )

        for component in parent_comp.components:
            context.comp_name = component.title
            context.comp_def = parent_comp
            context.component = component
            logger.info(f'Assembling markdown for component {component.title}')
            ComponentAssemble._update_component_with_markdown(md_dir, component, context)

    @staticmethod
    def _get_profile_title_and_href_from_dir(md_dir: pathlib.Path) -> Tuple[str, str]:
        """Get profile title and href from yaml header of first md file found in dir that has info."""
        md_files = md_dir.rglob('*.md')
        markdown_api = MarkdownAPI()
        for md_file in md_files:
            header, _ = markdown_api.processor.read_markdown_wo_processing(md_file)
            prof_title = deep_get(header, [const.TRESTLE_GLOBAL_TAG, const.PROFILE, const.TITLE])
            profile_href = deep_get(header, [const.TRESTLE_GLOBAL_TAG, const.PROFILE, const.HREF], 'unknown_href')
            # return first one found
            if prof_title:
                return prof_title, profile_href
        logger.warning(f'Cannot find profile title and href in markdown headers of directory {md_dir}')
        return 'unknown_title', 'unknown_href'

    @staticmethod
    def _update_component_with_markdown(
        md_dir: pathlib.Path, component: comp.DefinedComponent, context: ControlContext
    ) -> None:
        md_path = md_dir / component.title
        sub_dirs = file_utils.iterdir_without_hidden_files(md_path)
        source_dirs = [sub_dir.name for sub_dir in sub_dirs if sub_dir.is_dir()]
        for source_dir in source_dirs:
            profile_title, _ = ComponentAssemble._get_profile_title_and_href_from_dir(md_path / source_dir)
            # context has defined component and comp_name
            imp_reqs = CatalogReader.read_catalog_imp_reqs(md_path / source_dir, context)
            # the imp_reqs need to be inserted into the correct control_implementation
            for imp_req in imp_reqs:
                ControlInterface.insert_imp_req_into_component(component, imp_req, profile_title, context.trestle_root)
