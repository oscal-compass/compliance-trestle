# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Tests for json and yaml manipulations of oscal files."""

import datetime
import pathlib

import pytest

import trestle.oscal.target as ostarget

import yaml

yaml_path = pathlib.Path('tests/data/yaml/')
json_path = pathlib.Path('tests/data/json/')
encoding = 'utf8'
loader = yaml.Loader


def test_yaml_load() -> None:
    """Test yaml load."""
    # happy path
    read_file = (yaml_path / 'good_simple.yaml').open('r', encoding=encoding)
    obj = yaml.load(read_file, Loader=loader)
    assert obj is not None

    # unhappy path
    with pytest.raises(yaml.parser.ParserError):
        read_file = (yaml_path / 'bad_simple.yaml').open('r', encoding=encoding)
        obj = yaml.load(read_file, Loader=loader)


def test_yaml_dump(tmp_path: pathlib.Path) -> None:
    """Test yaml load and dump."""
    target_name = 'good_target.yaml'
    tmp_path = pathlib.Path(tmp_path)

    # happy path
    read_file = (yaml_path / target_name).open('r', encoding=encoding)
    target = yaml.load(read_file, Loader=loader)
    assert target is not None

    dump_name = tmp_path / target_name
    write_file = dump_name.open('w', encoding=encoding)
    yaml.dump(target, write_file)
    read_file = dump_name.open('r', encoding=encoding)
    saved_target = yaml.load(read_file, Loader=loader)
    assert saved_target is not None

    assert saved_target == target


def test_oscal_model(tmp_path: pathlib.Path) -> None:
    """Test pydantic oscal model."""
    good_target_name = 'good_target.yaml'
    tmp_path = pathlib.Path(tmp_path)

    tmp_path = pathlib.Path(tmp_path)

    # load good target
    read_file = yaml_path / good_target_name
    assert read_file.exists()
    target = ostarget.TargetDefinition.oscal_read(read_file)
    assert target is not None

    # write the oscal target def out as yaml
    dump_name = tmp_path / good_target_name
    target.oscal_write(dump_name)

    # read it back in
    target_reload = ostarget.TargetDefinition.oscal_read(dump_name)
    assert target_reload is not None

    # confirm same
    assert target == target_reload

    # confirm it really is checking the time
    target_reload.metadata.last_modified = datetime.datetime.now()
    assert target != target_reload

    # load good target with different timezone
    read_file = yaml_path / 'good_target_diff_tz.yaml'
    target_diff_tz = ostarget.TargetDefinition.oscal_read(read_file)
    assert target_diff_tz is not None

    # confirm same since different timezones but same utc time
    assert target == target_diff_tz

    # try to load file with no timezone specified
    read_file = yaml_path / 'bad_target_no_tz.yaml'

    # confirm the load fails because it is invalid without timezone specified
    try:
        _ = ostarget.TargetDefinition.oscal_read(read_file)
    except Exception:
        assert True
    else:
        assert AssertionError()
