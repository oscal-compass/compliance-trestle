# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Tests for json and yaml manipulations of oscal files."""

import datetime
import pathlib

import pytest

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError

import trestle.core.const as const
import trestle.oscal.component as component

yaml_path = pathlib.Path('tests/data/yaml/')
json_path = pathlib.Path('tests/data/json/')
encoding = const.FILE_ENCODING


def test_yaml_load() -> None:
    """Test yaml load."""
    # happy path
    read_file = (yaml_path / 'good_simple.yaml').open('r', encoding=encoding)
    yaml = YAML(typ='safe')
    obj = yaml.load(read_file)
    assert obj is not None

    # unhappy path
    with pytest.raises(ParserError):
        read_file = (yaml_path / 'bad_simple.yaml').open('r', encoding=encoding)
        obj = yaml.load(read_file)


def test_yaml_dump(tmp_path: pathlib.Path) -> None:
    """Test yaml load and dump."""
    component_name = 'good_component.yaml'
    tmp_path = pathlib.Path(tmp_path)
    yaml = YAML(typ='safe')
    # happy path
    read_file = (yaml_path / component_name).open('r', encoding=encoding)
    component_obj = yaml.load(read_file)
    read_file.close()
    assert component_obj is not None

    dump_name = tmp_path / component_name
    write_file = dump_name.open('w', encoding=encoding)
    yaml.dump(component_obj, write_file)
    write_file.close()
    read_file = dump_name.open('r', encoding=encoding)
    saved_component = yaml.load(read_file)
    assert saved_component is not None

    assert saved_component == component_obj


def test_oscal_model(tmp_path: pathlib.Path) -> None:
    """Test pydantic oscal model."""
    good_component_name = 'good_component.yaml'
    tmp_path = pathlib.Path(tmp_path)

    tmp_path = pathlib.Path(tmp_path)

    # load good component
    read_file = yaml_path / good_component_name
    assert read_file.exists()
    component_obj = component.ComponentDefinition.oscal_read(read_file)
    assert component_obj is not None

    # write the oscal componet def out as yaml
    dump_name = tmp_path / good_component_name
    component_obj.oscal_write(dump_name)

    # read it back in
    component_reload = component.ComponentDefinition.oscal_read(dump_name)
    assert component_reload is not None

    # confirm same
    assert component_obj == component_reload

    # confirm it really is checking the time
    component_reload.metadata.last_modified = datetime.datetime.now()
    assert component_obj != component_reload

    # load good target with different timezone
    read_file = yaml_path / 'good_component_diff_tz.yaml'
    component_diff_tz = component.ComponentDefinition.oscal_read(read_file)
    assert component_diff_tz is not None

    # confirm same since different timezones but same utc time
    assert component_obj == component_diff_tz

    # try to load file with no timezone specified
    read_file = yaml_path / 'bad_component_no_tz.yaml'

    # confirm the load fails because it is invalid without timezone specified
    try:
        _ = component.ComponentDefinition.oscal_read(read_file)
    except Exception:
        assert True
    else:
        assert AssertionError()
