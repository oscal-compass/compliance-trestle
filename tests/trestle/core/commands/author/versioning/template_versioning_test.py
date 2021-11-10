# -*- mode:python; coding:utf-8 -*-

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
"""A Template Versioning tests."""
import pathlib

import pytest

from trestle.core.commands.author.consts import START_TEMPLATE_VERSION, TEMPLATE_VERSION_HEADER
from trestle.core.commands.author.versioning.template_versioning import TemplateVersioning
from trestle.core.draw_io import DrawIO
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_api import MarkdownAPI


def test_template_version_folder_update(tmp_path: pathlib.Path) -> None:
    """Test template folder update from old structure to new."""
    task_path = tmp_path.joinpath('trestle/author/sample_task/')
    task_path.mkdir(parents=True)

    old_template = task_path.joinpath('template.md')
    old_template.touch()

    with pytest.raises(TrestleError):
        TemplateVersioning.update_template_folder_structure(old_template)

    # make sure file gets put to first version
    TemplateVersioning.update_template_folder_structure(task_path)

    assert task_path.joinpath('0.0.1/').joinpath('template.md').exists()
    assert not old_template.exists()

    # make sure new file also gets put to the first version
    another_template = task_path.joinpath('missplaced_template.md')
    another_template.touch()

    TemplateVersioning.update_template_folder_structure(task_path)
    assert task_path.joinpath('0.0.1/').joinpath('template.md').exists()
    assert task_path.joinpath('0.0.1/').joinpath('missplaced_template.md').exists()
    assert not another_template.exists()

    # make sure other versions get no modifications
    v2_dir = task_path.joinpath('11.12.113')
    v2_dir.mkdir()

    yet_another_template = task_path.joinpath('new_template.md')
    yet_another_template.touch()
    TemplateVersioning.update_template_folder_structure(task_path)

    assert len(list(v2_dir.iterdir())) == 0
    assert task_path.joinpath('0.0.1/').joinpath('template.md').exists()
    assert task_path.joinpath('0.0.1/').joinpath('missplaced_template.md').exists()
    assert task_path.joinpath('0.0.1/').joinpath('new_template.md').exists()
    assert not yet_another_template.exists()


def test_get_latest_version(tmp_path: pathlib.Path) -> None:
    """Test get latest version of template."""
    task_path = tmp_path.joinpath('trestle/author/sample_task/')

    with pytest.raises(TrestleError):
        TemplateVersioning.get_latest_version_for_task(task_path)

    task_path.mkdir(parents=True)

    latest_path, version = TemplateVersioning.get_latest_version_for_task(task_path)
    assert latest_path == task_path.joinpath('0.0.1')
    assert version == '0.0.1'

    v1_dir = task_path.joinpath('0.0.1/')
    v2_dir = task_path.joinpath('11.10.1234/')
    v1_dir.mkdir(parents=True)
    v2_dir.mkdir(parents=True)

    latest_path, version = TemplateVersioning.get_latest_version_for_task(task_path)
    assert latest_path == v2_dir
    assert version == '11.10.1234'

    template_v1 = v1_dir.joinpath('template.md')
    template_v2 = v2_dir.joinpath('template.md')
    template_v1.touch()
    template_v2.touch()

    latest_path, version = TemplateVersioning.get_latest_version_for_task(task_path)
    assert latest_path == v2_dir
    assert version == '11.10.1234'

    with pytest.raises(TrestleError):
        TemplateVersioning.get_latest_version_for_task(template_v1)


def test_get_versioned_template(tmp_path: pathlib.Path) -> None:
    """Test get template of the specified version."""
    task_path = tmp_path.joinpath('trestle/author/sample_task/')

    with pytest.raises(TrestleError):
        TemplateVersioning.get_versioned_template_dir(task_path)

    task_path.mkdir(parents=True)

    with pytest.raises(TrestleError):
        TemplateVersioning.get_versioned_template_dir(task_path)

    v1_dir = task_path.joinpath(START_TEMPLATE_VERSION)
    v2_dir = task_path.joinpath('0.1.5/')
    v3_dir = task_path.joinpath('10.02.1/')
    v1_dir.mkdir(parents=True)
    v2_dir.mkdir(parents=True)
    v3_dir.mkdir(parents=True)

    first_version = TemplateVersioning.get_versioned_template_dir(task_path, START_TEMPLATE_VERSION)
    assert first_version == v1_dir

    latest_version = TemplateVersioning.get_versioned_template_dir(task_path)
    assert latest_version == v3_dir

    second_version = TemplateVersioning.get_versioned_template_dir(task_path, '0.1.5')
    assert second_version == v2_dir

    with pytest.raises(TrestleError):
        TemplateVersioning.get_versioned_template_dir(task_path, '6.7.8')


def test_write_versioned_template(tmp_path: pathlib.Path) -> None:
    """Test writing a template to the folder."""
    task_path = tmp_path.joinpath('trestle/author/sample_task/')

    with pytest.raises(TrestleError):
        TemplateVersioning.get_versioned_template_dir(task_path)

    task_path.mkdir(parents=True)
    tmp_path_01 = task_path.joinpath('0.0.1')
    tmp_path_02 = task_path.joinpath('0.0.2')
    tmp_path_01.mkdir(parents=True)
    tmp_path_02.mkdir(parents=True)
    template = tmp_path_01.joinpath('template.md')

    TemplateVersioning.write_versioned_template('template.md', tmp_path_01, template, None)

    assert task_path.joinpath(START_TEMPLATE_VERSION).joinpath('template.md').exists()
    assert template.exists()

    template2 = tmp_path_01.joinpath('template2.md')
    template3 = tmp_path_02.joinpath('template3.md')
    template4 = tmp_path_02.joinpath('template4.md')
    TemplateVersioning.write_versioned_template('template.md', tmp_path_01, template2, '0.0.1')
    TemplateVersioning.write_versioned_template('template.md', tmp_path_02, template3, '0.0.2')
    TemplateVersioning.write_versioned_template('template.md', tmp_path_02, template4, None)

    assert tmp_path_01.joinpath('template.md').exists()
    assert tmp_path_01.joinpath('template2.md').exists()
    assert tmp_path_02.joinpath('template3.md').exists()
    assert tmp_path_02.joinpath('template4.md').exists()
    assert template.exists()

    md_api = MarkdownAPI()
    header, _ = md_api.processor.read_markdown_wo_processing(tmp_path_02.joinpath('template3.md'))

    assert header[TEMPLATE_VERSION_HEADER] == '0.0.2'

    template_drawio = tmp_path_02.joinpath('template.drawio')
    TemplateVersioning.write_versioned_template('template.drawio', tmp_path_02, template_drawio, '0.0.2')

    drawio = DrawIO(template_drawio)
    metadata = drawio.get_metadata()[0]

    assert metadata[TEMPLATE_VERSION_HEADER] == '0.0.2'


def test_template_versioning(tmp_path: pathlib.Path) -> None:
    """Full on testing of updating the template folder structure and retrieving it back."""
    task_path = tmp_path.joinpath('trestle/author/sample_task/')

    task_path.mkdir(parents=True)
    task_path.joinpath('0.0.1').mkdir(parents=True)
    task_path.joinpath('0.0.2').mkdir(parents=True)
    template = task_path.joinpath('0.0.2/template.md')
    template2 = task_path.joinpath('0.0.2/template2.md')

    old_template = task_path.joinpath('old_template.md')
    old_template.touch()

    TemplateVersioning.update_template_folder_structure(task_path)
    TemplateVersioning.write_versioned_template('template.md', task_path.joinpath('0.0.2'), template, '0.0.2')
    TemplateVersioning.write_versioned_template('template.md', task_path.joinpath('0.0.2'), template2, None)

    v1_dir = TemplateVersioning.get_versioned_template_dir(task_path, START_TEMPLATE_VERSION)
    latest_dir, version = TemplateVersioning.get_latest_version_for_task(task_path)
    v2_dir = TemplateVersioning.get_versioned_template_dir(task_path, '0.0.2')

    assert not old_template.exists()
    assert task_path.joinpath(START_TEMPLATE_VERSION).joinpath('old_template.md').exists()
    assert task_path.joinpath('0.0.2').joinpath('template.md').exists()
    assert task_path.joinpath('0.0.2').joinpath('template2.md').exists()
    assert v1_dir.exists()
    assert v2_dir == latest_dir
    assert version == '0.0.2'


def test_valid_version() -> None:
    """Test is valid verion."""
    assert TemplateVersioning.is_valid_version('0.0.1')
    assert not TemplateVersioning.is_valid_version("'0.0.1'")
    assert not TemplateVersioning.is_valid_version('not_valid.0.0.1')
    assert not TemplateVersioning.is_valid_version('0.1')
    assert not TemplateVersioning.is_valid_version('1')
    assert not TemplateVersioning.is_valid_version('0.0.0.1')
