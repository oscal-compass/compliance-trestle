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
"""Tests for the catalog author module."""

import pathlib
import shutil

from tests import test_utils

from trestle.core.commands.author.catalog import CatalogAssemble, CatalogGenerate, CatalogInterface
from trestle.core.control_io import ControlIo
from trestle.oscal.catalog import Catalog

markdown_name = 'my_md'


def insert_prose(trestle_dir: pathlib.Path, statement_id: str, prose: str) -> int:
    """Insert response prose in for a statement of a control."""
    control_dir = trestle_dir / markdown_name / statement_id.split('-')[0]
    md_file = control_dir / (statement_id.split('_')[0] + '.md')

    return test_utils.insert_text_in_file(md_file, statement_id, prose)


def confirm_control_contains(trestle_dir: pathlib.Path, control_id: str, part_label: str, seek_str: str) -> bool:
    """Confirm the text is present in the control markdown in the correct part."""
    control_dir = trestle_dir / markdown_name / control_id.split('-')[0]
    md_file = control_dir / f'{control_id}.md'

    responses = ControlIo.read_all_implementation_prose(md_file)
    if part_label not in responses:
        return False
    prose = '\n'.join(responses[part_label])
    return seek_str in prose


def test_catalog_generate_assemble(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the catalog markdown generator."""
    nist_catalog_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    cat_name = 'my_cat'
    md_name = 'my_md'
    assembled_cat_name = 'my_assembled_cat'
    catalog_dir = tmp_trestle_dir / f'catalogs/{cat_name}'
    catalog_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = catalog_dir / 'catalog.json'
    shutil.copy(nist_catalog_path, catalog_path)
    markdown_path = tmp_trestle_dir / md_name
    markdown_path.mkdir(parents=True, exist_ok=True)
    catalog_generate = CatalogGenerate()
    catalog_generate.generate_markdown(tmp_trestle_dir, catalog_path, markdown_path)
    assert (markdown_path / 'ac/ac-1.md').exists()

    catalog_assemble = CatalogAssemble()
    catalog_assemble.assemble_catalog(tmp_trestle_dir, md_name, assembled_cat_name)
    cat_orig = Catalog.oscal_read(catalog_path)
    cat_new = Catalog.oscal_read(tmp_trestle_dir / f'catalogs/{assembled_cat_name}/catalog.json')
    interface_orig = CatalogInterface(cat_orig)
    assert interface_orig.equivalent_to(cat_new)
