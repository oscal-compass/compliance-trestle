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

from pkg_resources import resource_filename

import pytest

from trestle.core.commands.author.consts import LATEST_TEMPLATE_VERSION, START_TEMPLATE_VERSION, TRESTLE_RESOURCES
from trestle.core.commands.author.versioning.template_versioning import TemplateVersioning
from trestle.core.err import TrestleError


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
        TemplateVersioning.get_latest_version_path(task_path)

    task_path.mkdir(parents=True)

    pth = TemplateVersioning.get_latest_version_path(task_path)
    assert pth == task_path.joinpath(LATEST_TEMPLATE_VERSION)

    v1_dir = task_path.joinpath('0.0.1/')
    v2_dir = task_path.joinpath('11.10.1234/')
    v1_dir.mkdir(parents=True)
    v2_dir.mkdir(parents=True)

    latest_version = TemplateVersioning.get_latest_version_path(task_path)
    assert latest_version == v2_dir

    template_v1 = v1_dir.joinpath('template.md')
    template_v2 = v2_dir.joinpath('template.md')
    template_v1.touch()
    template_v2.touch()

    latest_version = TemplateVersioning.get_latest_version_path(task_path)
    assert latest_version == v2_dir

    with pytest.raises(TrestleError):
        TemplateVersioning.get_latest_version_path(template_v1)


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

    template = tmp_path.joinpath('template.md')
    template.touch()
    template2 = tmp_path.joinpath('template2.md')
    template2.touch()

    pth = TemplateVersioning.write_versioned_template(task_path, template)

    assert task_path.joinpath(LATEST_TEMPLATE_VERSION).joinpath('template.md').exists()
    assert template.exists()
    assert pth == task_path.joinpath(LATEST_TEMPLATE_VERSION)

    TemplateVersioning.write_versioned_template(task_path, template, '0.0.2')
    TemplateVersioning.write_versioned_template(task_path, template2, LATEST_TEMPLATE_VERSION)

    assert task_path.joinpath(LATEST_TEMPLATE_VERSION).joinpath('template.md').exists()
    assert task_path.joinpath(LATEST_TEMPLATE_VERSION).joinpath('template2.md').exists()
    assert task_path.joinpath('0.0.2').joinpath('template.md').exists()
    assert template.exists()


def test_template_versioning(tmp_path: pathlib.Path) -> None:
    """Full on testing of updating the template folder structure and retrieving it back."""
    task_path = tmp_path.joinpath('trestle/author/sample_task/')

    task_path.mkdir(parents=True)

    template = tmp_path.joinpath('template.md')
    template.touch()
    template2 = tmp_path.joinpath('template2.md')
    template2.touch()

    old_template = task_path.joinpath('old_template.md')
    old_template.touch()

    TemplateVersioning.update_template_folder_structure(task_path)
    TemplateVersioning.write_versioned_template(task_path, template, '0.0.2')
    TemplateVersioning.write_versioned_template(task_path, template2)

    v1_dir = TemplateVersioning.get_versioned_template_dir(task_path, START_TEMPLATE_VERSION)
    latest_dir = TemplateVersioning.get_latest_version_path(task_path)
    v2_dir = TemplateVersioning.get_versioned_template_dir(task_path, '0.0.2')

    assert not old_template.exists()
    assert task_path.joinpath(START_TEMPLATE_VERSION).joinpath('old_template.md').exists()
    assert task_path.joinpath('0.0.2').joinpath('template.md').exists()
    assert task_path.joinpath('0.0.2').joinpath('template2.md').exists()
    assert v1_dir.exists()
    assert v2_dir == latest_dir


def test_get_versioned_resource(tmp_path: pathlib.Path) -> None:
    """Test get resource for the specified version."""
    dotted_path, _ = TemplateVersioning.get_versioned_template_resource(TRESTLE_RESOURCES)
    dotted_path2, _ = TemplateVersioning.get_versioned_template_resource(TRESTLE_RESOURCES, '0.0.1')

    template = pathlib.Path(resource_filename(dotted_path, 'template.md')).resolve()
    template2 = pathlib.Path(resource_filename(dotted_path2, 'template.md')).resolve()
    assert template.exists()
    assert template == template2
