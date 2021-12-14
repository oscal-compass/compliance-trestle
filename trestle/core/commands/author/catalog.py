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

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.const as const
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError, TrestleNotFoundError
from trestle.utils.load_distributed import load_distributed

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
            '-phv',
            '--preserve-header-values',
            help=const.HELP_PRESERVE_HEADER_VALUES,
            required=False,
            action='store_true',
            default=False
        )

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root
        if not fs.allowed_task_name(args.output):
            logger.warning(f'{args.output} is not an allowed directory name')
            return CmdReturnCodes.COMMAND_ERROR.value

        yaml_header: dict = {}
        if 'yaml_header' in args and args.yaml_header is not None:
            try:
                logging.debug(f'Loading yaml header file {args.yaml_header}')
                yaml = YAML(typ='safe')
                yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
            except YAMLError as e:
                logging.warning(f'YAML error loading yaml header {args.yaml_header} for ssp generation: {e}')
                return CmdReturnCodes.COMMAND_ERROR.value

        catalog_path = trestle_root / f'catalogs/{args.name}/catalog.json'

        markdown_path = trestle_root / args.output

        return self.generate_markdown(
            trestle_root, catalog_path, markdown_path, yaml_header, args.preserve_header_values
        )

    def generate_markdown(
        self,
        trestle_root: pathlib.Path,
        catalog_path: pathlib.Path,
        markdown_path: pathlib.Path,
        yaml_header: dict,
        preserve_header_values: bool
    ) -> int:
        """Generate markdown for the controls in the catalog."""
        try:
            _, _, catalog = load_distributed(catalog_path, trestle_root)
            catalog_interface = CatalogInterface(catalog)
            catalog_interface.write_catalog_as_markdown(
                markdown_path,
                yaml_header,
                sections=None,
                responses=False,
                additional_content=True,
                profile=None,
                preserve_header_values=preserve_header_values
            )
        except TrestleNotFoundError as e:
            logger.warning(f'Catalog {catalog_path} not found for load {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:
            raise TrestleError(f'Error generating markdown for controls in {catalog_path}: {e}')
        return CmdReturnCodes.SUCCESS.value


class CatalogAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Catalog json file."""

    name = 'catalog-assemble'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Catalog'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = pathlib.Path(args.trestle_root)
        return CatalogAssemble.assemble_catalog(trestle_root, args.markdown, args.output)

    @staticmethod
    def assemble_catalog(trestle_root: pathlib.Path, md_name: str, catalog_name: str) -> int:
        """
        Assemble the markdown directory into a json catalog model file.

        Args:
            trestle_root: The trestle root directory
            md_name: The name of the directory containing the markdown control files for the ssp
            catalog_name: The output name of the catalog json file to be created from the assembly

        Returns:
            0 on success, 1 otherwise

        """
        md_dir = trestle_root / md_name
        if not md_dir.exists():
            logger.warning(f'Markdown directory {md_name} does not exist.')
            return CmdReturnCodes.COMMAND_ERROR.value
        catalog_interface = CatalogInterface()
        try:
            catalog = catalog_interface.read_catalog_from_markdown(md_dir)
        except Exception as e:
            raise TrestleError(f'Error reading catalog from markdown {md_dir}: {e}')
        if catalog_interface.get_count_of_controls_in_catalog(True) == 0:
            logger.warning(f'No controls were loaded from markdown {md_dir}.  No catalog.json created.')
            return CmdReturnCodes.COMMAND_ERROR.value
        new_cat_dir = trestle_root / f'catalogs/{catalog_name}'
        if new_cat_dir.exists():
            logger.info('Creating catalog from markdown and destination catalog directory exists, so updating.')
            try:
                shutil.rmtree(str(new_cat_dir))
            except OSError as e:
                raise TrestleError(f'OSError deleting existing catalog directory with rmtree {new_cat_dir}: {e}')
        try:
            new_cat_dir.mkdir()
            catalog.oscal_write(new_cat_dir / 'catalog.json')
        except OSError as e:
            raise TrestleError(f'OSError writing catalog from markdown to {new_cat_dir}: {e}')
        return CmdReturnCodes.SUCCESS.value
