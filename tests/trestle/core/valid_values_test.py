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
"""Testing of valid values."""

import trestle.oscal.profile as prof


def test_position_valid(tmp_path) -> None:
    """Testing position valid."""
    try:
        # ending
        val = 'ending'
        obj = prof.Add(position=val)
        assert isinstance(obj.position, prof.PositionValidValues)
        assert obj.position == prof.PositionValidValues.ending
        assert obj.position.value == 'ending'
        # after
        val = prof.PositionValidValues.after
        obj = prof.Add(position=val)
        assert isinstance(obj.position, prof.PositionValidValues)
        assert obj.position == prof.PositionValidValues.after
        assert obj.position.value == 'after'
        # starting
        obj.position = prof.PositionValidValues.starting
        assert obj.position == prof.PositionValidValues.starting
        assert obj.position.value == 'starting'
        # before
        obj.position = 'before'
        assert obj.position == prof.PositionValidValues.before
        assert obj.position.value == 'before'
    except Exception as e:
        raise RuntimeError(e)


def test_position_invalid(tmp_path) -> None:
    """Testing position invalid."""
    try:
        val = 'foobar'
        prof.Add(position=val)
        raise RuntimeError(f'position={val} incorrectly allowed')
    except Exception:
        pass
