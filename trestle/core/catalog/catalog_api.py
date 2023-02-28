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
"""Main entrypoint to interact with catalog in memory."""

import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import trestle.core.generators as gens
import trestle.oscal.catalog as cat
from trestle.common.err import TrestleError
from trestle.common.file_utils import prune_empty_dirs
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.catalog.catalog_merger import CatalogMerger
from trestle.core.catalog.catalog_reader import CatalogReader
from trestle.core.catalog.catalog_writer import CatalogWriter
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class CatalogAPI():
    """
    Main entrypoint to interact with catalog in memory.

    Encapsulates all necessary functionality to manipulate, read
    and write the catalog and its markdown representation.
    """

    def __init__(self, catalog: Optional[cat.Catalog], context: Optional[ControlContext] = None):
        """Initialize catalog api."""
        if not catalog:
            # catalog assemble initializes with no catalog but may merge into an existing one later
            logger.debug('No catalog was provided in CatalogAPI init, generating a new one.')
            catalog = gens.generate_sample_model(cat.Catalog)
        self._catalog = catalog
        self._catalog_interface = CatalogInterface(self._catalog)
        self._writer = CatalogWriter(self._catalog_interface)
        self._reader = CatalogReader(self._catalog_interface)
        self._merger = CatalogMerger(self._catalog_interface)
        self._context = context

    def update_context(self, context: ControlContext):
        """Update current context."""
        if not context:
            raise TrestleError('ControlContext cannot be empty.')
        self._context = context

    def write_catalog_as_markdown(self, label_as_key=False) -> None:
        """
        Write out the catalog controls from dict as markdown files to the specified directory.

        Args:
            label_as_key: Whether to use label_as_key for part_id to label map

        Returns:
            None
        """
        # create the directory in which to write the control markdown files
        self._context.md_root.mkdir(exist_ok=True, parents=True)

        part_id_map = self._catalog_interface.get_statement_part_id_map(label_as_key=label_as_key)

        if self._context.purpose == ContextPurpose.PROFILE:
            found_alters, _, _ = self.read_additional_content_from_md(label_as_key=True)
            self._writer.write_catalog_as_profile_markdown(self._context, part_id_map, found_alters)
        elif self._context.purpose == ContextPurpose.COMPONENT:
            self._writer.write_catalog_as_component_markdown(self._context, part_id_map)
        elif self._context.purpose == ContextPurpose.SSP:
            self._writer.write_catalog_as_ssp_markdown(self._context, part_id_map)
        else:
            self._writer.write_catalog_as_catalog(self._context, part_id_map)

        # prune any directories that have no markdown files
        prune_empty_dirs(self._context.md_root, '*.md')

    def read_catalog_from_markdown(self, markdown_dir: pathlib.Path, is_set_parameters: bool) -> cat.Catalog:
        """Read catalog from markdown."""
        md_catalog = self._reader.read_catalog_from_markdown(markdown_dir, is_set_parameters)
        md_catalog_interface = CatalogInterface(md_catalog)
        if md_catalog_interface.get_count_of_controls_in_catalog(True) == 0:
            raise TrestleError(f'No controls were loaded from markdown {markdown_dir}.  No catalog created.')

        return md_catalog

    def read_additional_content_from_md(self,
                                        label_as_key: bool = False
                                        ) -> Tuple[List[prof.Alter], Dict[str, Any], Dict[str, str]]:
        """Read additional content from markdown."""
        if not self._context:
            raise TrestleError('Reading content from the markdown requires context to be initialized!')
        label_map = self._catalog_interface.get_statement_part_id_map(label_as_key=label_as_key)

        return self._reader.read_additional_content(
            self._context.md_root,
            self._context.required_sections,
            label_map,
            self._context.sections_dict,
            self._context.to_markdown
        )

    def merge_catalog(self, catalog: cat.Catalog, replace_params: bool) -> None:
        """Merge one catalog into another."""
        return self._merger.merge_catalog(catalog, replace_params)
