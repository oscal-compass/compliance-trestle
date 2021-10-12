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
"""Tests for chevron."""

import pytest

chevron = pytest.importorskip('chevron')


def test_simple_substitute() -> None:
    """Test chevron behaves as expected - simple."""
    expected = 'Hello, World!'
    actual = chevron.render('Hello, {{ var }}', {'var': 'World!'})
    assert actual == expected


def test_oscal_substitute() -> None:
    """Test of chevron with oscal substitutions."""
    expected = 'Hello, World!'
    actual = chevron.render('Hello, {{ insert: param, var }}', {'insert: param, var': 'World!'})
    assert actual == expected
