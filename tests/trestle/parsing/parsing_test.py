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

from dateutil.parser import isoparse

import dictdiffer

import pytest

import trestle.oscal.target as ostarget
from trestle.utils import fs

import yaml

yaml_path = pathlib.Path('tests/data/yaml/')
json_path = pathlib.Path('tests/data/json/')
encoding = 'utf8'
loader = yaml.Loader


def times_equal(t1, t2):
    """Test timestring equality."""
    dt1 = isoparse(t1)
    dt2 = isoparse(t2)
    assert type(dt1) == datetime.datetime
    assert type(dt2) == datetime.datetime

    return dt1 == dt2


def test_yaml_load():
    """Test yaml load."""
    # happy path
    with open(pathlib.Path.joinpath(yaml_path, 'good_simple.yaml'), 'r', encoding=encoding) as read_file:
        obj = yaml.load(read_file, Loader=loader)
    assert obj is not None

    # unhappy path
    with pytest.raises(yaml.parser.ParserError):
        with open(pathlib.Path.joinpath(yaml_path, 'bad_simple.yaml'), 'r', encoding=encoding) as read_file:
            obj = yaml.load(read_file, Loader=loader)


def test_yaml_dump(tmp_dir):
    """Test yaml load and dump."""
    target_name = 'good_target.yaml'

    # happy path
    with open(pathlib.Path.joinpath(yaml_path, target_name), 'r', encoding=encoding) as read_file:
        target = yaml.load(read_file, Loader=loader)
    assert target is not None

    fs.ensure_directory(tmp_dir)

    dump_name = pathlib.Path.joinpath(tmp_dir, target_name)

    with open(dump_name, 'w', encoding=encoding) as write_file:
        yaml.dump(target, write_file)

    with open(dump_name, 'r', encoding=encoding) as read_file:
        saved_target = yaml.load(read_file, Loader=loader)
    assert saved_target is not None

    assert saved_target == target

    # clean up
    pathlib.Path.unlink(dump_name)
    pathlib.Path.rmdir(tmp_dir)


def test_oscal_model(tmp_dir):
    """Test pydantic oscal model."""
    good_target_name = 'good_target.yaml'

    # load good target
    with open(pathlib.Path.joinpath(yaml_path, good_target_name), 'r', encoding=encoding) as read_file:
        yaml_target = yaml.load(read_file, Loader=loader)
    assert yaml_target is not None

    # represent it internally as pydantic target definition model
    oscal_target_def = ostarget.TargetDefinition.parse_obj(yaml_target['target-definition'])

    assert oscal_target_def is not None

    yaml_target_def = yaml_target['target-definition']

    fs.ensure_directory(tmp_dir)
    dump_name = pathlib.Path.joinpath(tmp_dir, good_target_name)

    # write the oscal target def out as yaml
    # exclude all None's and rename to original OSCAL form with - instead of _
    with open(dump_name, 'w', encoding=encoding) as write_file:
        yaml.dump(yaml.safe_load(oscal_target_def.json(exclude_none=True, by_alias=True)), write_file)

    # read it back in
    with open(dump_name, 'r', encoding=encoding) as read_file:
        oscal_target_def_reload = yaml.load(read_file, Loader=loader)

    # clean up
    pathlib.Path.unlink(dump_name)
    pathlib.Path.rmdir(tmp_dir)

    assert oscal_target_def_reload is not None

    # find all differences
    tdiff = dictdiffer.diff(oscal_target_def_reload, yaml_target_def)

    # allow any differences that appear to be different representations of equivalent datetime
    # only thing allowed is a change from one timestring to another one representing same global datetime
    for d in tdiff:
        assert (d[0] == 'change')
        assert (times_equal(d[2][0], d[2][1]))

    # load good target with different timezone
    with open(pathlib.Path.joinpath(yaml_path, 'good_target_diff_tz.yaml'), 'r', encoding=encoding) as read_file:
        yaml_target_diff_tz = yaml.load(read_file, Loader=loader)
    assert yaml_target_diff_tz is not None

    # represent it internally as pydantic target definition model
    oscal_target_def_diff_tz = ostarget.TargetDefinition.parse_obj(yaml_target_diff_tz['target-definition'])

    # find all differences
    tdiff = dictdiffer.diff(oscal_target_def_diff_tz, oscal_target_def)

    # allow any differences that appear to be different representations of equivalent datetime
    # only thing allowed is a change from one timestring to another one representing same global datetime
    for d in tdiff:
        assert (d[0] == 'change')
        assert (times_equal(d[2][0], d[2][1]))


"""
    # following test can be enabled when the pydantic base class checks for timezone
    # load bad target with missing timezone
    with open(yaml_path + 'bad_target_no_tz.yaml', 'r', encoding=encoding) as read_file:
        yaml_target_no_tz = yaml.load(read_file, Loader=loader)
    assert yaml_target_no_tz is not None

    # represent it internally as pydantic target definition model
    # this should fail since timzeone missing
    oscal_target_def_no_tz = None
    failed = False
    try:
        oscal_target_def_no_tz = ostarget.TargetDefinition.parse_obj(yaml_target_no_tz['target-definition'])
    except Exception:
        failed = True
    assert (failed)
    assert (oscal_target_def_no_tz is None)
"""
