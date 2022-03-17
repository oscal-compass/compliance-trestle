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
"""Author commands to generate catalog controls as markdown and assemble them back to json."""

import argparse
import logging
import pathlib
import shutil
from typing import Optional

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.common.const as const
import trestle.common.log as log
import trestle.oscal.common as com
from trestle.common import file_utils
from trestle.common.err import TrestleError, TrestleNotFoundError, handle_generic_command_exception
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.validator_helper import regenerate_uuids
from trestle.oscal.catalog import Catalog

logger = logging.getLogger(__name__)


class CatalogGenerate(AuthorCommonCommand):
    """Generate Catalog controls in markdown form from a catalog in the trestle workspace."""

    name = 'catalog-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the catalog model in the trestle workspace'
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

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = args.trestle_root
            if not file_utils.is_directory_name_allowed(args.output):
                raise TrestleError(f'{args.output} is not an allowed directory name')

            yaml_header: dict = {}
            if args.yaml_header:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML(typ='safe')
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    raise TrestleError(f'YAML error loading yaml header {args.yaml_header} for ssp generation: {e}')

            catalog_path = trestle_root / f'catalogs/{args.name}/catalog.json'

            markdown_path = trestle_root / args.output

            return self.generate_markdown(
                trestle_root, catalog_path, markdown_path, yaml_header, args.overwrite_header_values
            )
        except Exception as e:
            return handle_generic_command_exception(e, logger, 'Error occurred when generating markdown for catalog')

    def generate_markdown(
        self,
        trestle_root: pathlib.Path,
        catalog_path: pathlib.Path,
        markdown_path: pathlib.Path,
        yaml_header: dict,
        overwrite_header_values: bool
    ) -> int:
        """Generate markdown for the controls in the catalog."""
        try:
            _, _, catalog = ModelUtils.load_distributed(catalog_path, trestle_root)
            catalog_interface = CatalogInterface(catalog)
            catalog_interface.write_catalog_as_markdown(
                md_path=markdown_path,
                yaml_header=yaml_header,
                sections_dict=None,
                prompt_responses=False,
                additional_content=False,
                profile=None,
                overwrite_header_values=overwrite_header_values,
                set_parameters=True,
                required_sections=None
            )
        except TrestleNotFoundError as e:
            raise TrestleError(f'Catalog {catalog_path} not found for load: {e}')
        except Exception as e:
            raise TrestleError(f'Error generating markdown for controls in {catalog_path}: {e}')

        return CmdReturnCodes.SUCCESS.value


class CatalogAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Catalog json file."""

    name = 'catalog-assemble'

    def _init_arguments(self) -> None:
        name_help_str = (
            'Optional name of the catalog model in the trestle workspace that is being modified.  '
            'If not provided the output name is used.'
        )
        self.add_argument('-n', '--name', help=name_help_str, required=False, type=str)
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Catalog'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-sp', '--set-parameters', action='store_true', help=const.HELP_SET_PARAMS, required=False)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            return CatalogAssemble.assemble_catalog(
                trestle_root=trestle_root,
                md_name=args.markdown,
                catalog_name=args.output,
                orig_cat_name=args.name,
                set_parameters=args.set_parameters,
                regenerate=args.regenerate,
                version=args.version
            )
        except Exception as e:
            return handle_generic_command_exception(e, logger, 'Error occurred while assembling catalog')

    @staticmethod
    def assemble_catalog(
        trestle_root: pathlib.Path,
        md_name: str,
        catalog_name: str,
        orig_cat_name: Optional[str],
        set_parameters: bool,
        regenerate: bool,
        version: Optional[str]
    ) -> int:
        """
        Assemble the markdown directory into a json catalog model file.

        Args:
            trestle_root: The trestle root directory
            md_name: The name of the directory containing the markdown control files for the ssp
            catalog_name: The output name of the catalog model to be created from the assembly
            orig_cat_name: Optional name of the original json catalog that the markdown controls will replace
            set_parameters: set the parameters in the control to the values in the markdown yaml header
            regenerate: whether to regenerate the uuid's in the catalog
            version: version for the assembled catalog

        Returns:
            0 on success, 1 otherwise

        Notes:
            If the destination catalog_name model already exists in the trestle project, it is overwritten.
            If no original catalog name is provided, the catalog is created anew using only the markdown content.
        """
        md_dir = trestle_root / md_name
        if not md_dir.exists():
            raise TrestleError(f'Markdown directory {md_name} does not exist.')

        md_catalog_interface = CatalogInterface()
        try:
            md_catalog = md_catalog_interface.read_catalog_from_markdown(md_dir, set_parameters)
        except Exception as e:
            raise TrestleError(f'Error reading catalog from markdown {md_dir}: {e}')
        if md_catalog_interface.get_count_of_controls_in_catalog(True) == 0:
            raise TrestleError(f'No controls were loaded from markdown {md_dir}.  No catalog.json created.')

        # if original catalog given then merge the markdown controls into it
        if orig_cat_name:
            try:
                orig_cat, _ = ModelUtils.load_top_level_model(trestle_root, orig_cat_name, Catalog)
            except Exception as e:
                raise TrestleError(f'Error loading original catalog {orig_cat_name}: {e}')
            orig_cat_interface = CatalogInterface(orig_cat)
            # merge the just-read md catalog into the original json
            orig_cat_interface.merge_catalog(md_catalog, set_parameters)
            md_catalog = orig_cat_interface.get_catalog()

        if version:
            md_catalog.metadata.version = com.Version(__root__=version)

        new_cat_dir = trestle_root / f'catalogs/{catalog_name}'
        new_cat_path = new_cat_dir / 'catalog.json'
        if new_cat_path.exists():
            _, _, existing_cat = ModelUtils.load_distributed(new_cat_path, trestle_root)
            if existing_cat == md_catalog:
                logger.info('Assembled catalog is not different from existing version, so no update.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            md_catalog, _, _ = regenerate_uuids(md_catalog)
        ModelUtils.update_timestamp(md_catalog)

        if new_cat_dir.exists():
            logger.info('Creating catalog from markdown and destination catalog directory exists, so overwriting.')
            try:
                shutil.rmtree(str(new_cat_dir))
            except OSError as e:
                raise TrestleError(f'OSError deleting existing catalog directory with rmtree {new_cat_dir}: {e}')
        try:
            new_cat_dir.mkdir()
            md_catalog.oscal_write(new_cat_dir / 'catalog.json')
        except OSError as e:
            raise TrestleError(f'OSError writing catalog from markdown to {new_cat_dir}: {e}')
        return CmdReturnCodes.SUCCESS.value
