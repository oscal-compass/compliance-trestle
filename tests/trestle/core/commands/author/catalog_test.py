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
"""Tests for the catalog author module."""

import pathlib
import shutil
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from tests import test_utils

from trestle.cli import Trestle
from trestle.core.commands.author.catalog import CatalogAssemble, CatalogGenerate, CatalogInterface
from trestle.core.err import TrestleError
from trestle.oscal import catalog as cat
from trestle.oscal.common import Part, Property

markdown_name = 'my_md'


@pytest.mark.parametrize('use_cli', [True, False])
@pytest.mark.parametrize('dir_exists', [True, False])
def test_catalog_generate_assemble(
    use_cli: bool, dir_exists: bool, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
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
    ac1_path = markdown_path / 'ac/ac-1.md'
    new_prose = 'My added item'
    assembled_cat_dir = tmp_trestle_dir / f'catalogs/{assembled_cat_name}'
    # convert catalog to markdown then assemble it after adding an item to a control
    if use_cli:
        test_args = f'trestle author catalog-generate -n {cat_name} -o {md_name}'.split()
        monkeypatch.setattr(sys, 'argv', test_args)
        assert Trestle().run() == 0
        assert ac1_path.exists()
        test_utils.insert_text_in_file(ac1_path, 'ac-1_prm_6', f'- \\[d\\] {new_prose}')
        test_args = f'trestle author catalog-assemble -m {md_name} -o {assembled_cat_name}'.split()
        if dir_exists:
            assembled_cat_dir.mkdir()
        monkeypatch.setattr(sys, 'argv', test_args)
        assert Trestle().run() == 0
    else:
        catalog_generate = CatalogGenerate()
        catalog_generate.generate_markdown(tmp_trestle_dir, catalog_path, markdown_path)
        assert (markdown_path / 'ac/ac-1.md').exists()
        test_utils.insert_text_in_file(ac1_path, 'ac-1_prm_6', f'- \\[d\\] {new_prose}')
        if dir_exists:
            assembled_cat_dir.mkdir()
        CatalogAssemble.assemble_catalog(tmp_trestle_dir, md_name, assembled_cat_name)

    cat_orig = cat.Catalog.oscal_read(catalog_path)
    cat_new = cat.Catalog.oscal_read(assembled_cat_dir / 'catalog.json')
    interface_orig = CatalogInterface(cat_orig)
    # add the item manually to the original catalog so we can confirm the item was loaded correctly
    ac1 = interface_orig.get_control('ac-1')
    prop = Property(name='label', value='d.')
    new_part = Part(id='ac-1_smt.d', name='item', props=[prop], prose=new_prose)
    ac1.parts[0].parts.append(new_part)
    interface_orig.replace_control(ac1)
    interface_orig.update_catalog_controls()
    assert interface_orig.equivalent_to(cat_new)


def test_catalog_interface(sample_catalog_rich_controls: cat.Catalog) -> None:
    """Test the catalog interface with complex controls."""
    interface = CatalogInterface(sample_catalog_rich_controls)
    n_controls = interface.get_count_of_controls(True)
    assert n_controls == 5

    control = interface.get_control('control_d1')
    new_title = 'updated d1'
    control.title = new_title
    interface.replace_control(control)
    interface.update_catalog_controls()
    assert interface._catalog.controls[1].controls[0].title == new_title


def test_catalog_failures(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test failures of author catalog."""
    test_args = 'trestle author catalog-generate -n foo -o profiles'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    assert Trestle().run() == 1

    test_args = 'trestle author catalog-generate -n foo -o my_md'.split()
    with pytest.raises(TrestleError):
        monkeypatch.setattr(sys, 'argv', test_args)
        Trestle().run()
