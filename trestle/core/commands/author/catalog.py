# Copyright (c) 2021 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command to manipulate catalogs and controls."""

import argparse
import logging
import pathlib

import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.control_io import ControlIo
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


class CatalogGenerate(AuthorCommonCommand):
    """Generate Catalog controls in markdown form from a catalog in the trestle workspace."""

    name = 'catalog-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the catalog model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated catalog markdown folder'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root
        if not fs.allowed_task_name(args.output):
            logger.warning(f'{args.output} is not an allowed directory name')
            return 1

        catalog_path = trestle_root / f'catalogs/{args.name}/catalog.json'

        markdown_path = trestle_root / args.output

        return self.generate_markdown(trestle_root, catalog_path, markdown_path)

    def generate_markdown(
        self, trestle_root: pathlib.Path, catalog_path: pathlib.Path, markdown_path: pathlib.Path
    ) -> int:
        """Generate markdown for the controls in the catalog."""
        _, _, catalog = load_distributed(catalog_path, trestle_root)
        catalog_interface = CatalogInterface(catalog)
        control_io = ControlIo()
        for control in catalog_interface.get_all_controls(True):
            group_id, group_title, _ = catalog_interface.get_group_info(control.id)
            group_dir = markdown_path if group_id == 'catalog' else markdown_path / group_id
            if not group_dir.exists():
                group_dir.mkdir(parents=True, exist_ok=True)
            control_path = group_dir / f'{control.id}.md'
            control_io.write_control_full(control_path, control, group_title)


class CatalogAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Catalog json file."""

    name = 'catalog-assemble'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Catalog'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        return 0

    def assemble_catalog(self, trestle_root: pathlib.Path, md_name: str, catalog_name: str) -> int:
        """
        Assemble the markdown directory into a json catalog model file.

        In normal operation the markdown would have been edited to provide implementation responses.
        These responses are captured as prose in the ssp json file.

        Args:
            trestle_root: The trestle root directory
            md_name: The name of the directory containing the markdown control files for the ssp
            ssp_name: The output name of the ssp json file to be created from the assembly

        Returns:
            0 on success, 1 otherwise

        """
        # find all groups in the markdown dir
        group_ids = []
        # FIXME
        md_dir = trestle_root / md_name / catalog_name

        for gdir in md_dir.glob('*/'):
            group_ids.append(str(gdir.stem))

        return 0
