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
"""Transformer helper tests."""
from trestle.transforms.transformer_helper import PropertyAccounting
from trestle.transforms.transformer_helper import PropertyManager


def _get_property_set(gid, pid):
    """Generate property test set."""
    return {
        'group': 'group' + str(gid),
        'name': 'name' + str(pid),
        'value': 'value' + str(pid),
        'ns': 'ns' + str(pid),
        'class': 'class' + str(pid),
    }


def _common_test(pa, pm):
    """Reuse common test sequence."""
    ps1 = _get_property_set(1, 1)
    pa.count_group(ps1['group'])
    pa.count_property(ps1['group'], ps1['name'], ps1['value'], ps1['ns'], ps1['class'])
    assert pa.is_common_property(ps1['group'], ps1['name'], ps1['value'], ps1['ns'], ps1['class'])
    ps2 = _get_property_set(1, 2)
    pa.count_group(ps2['group'])
    pa.count_property(ps2['group'], ps2['name'], ps2['value'], ps2['ns'], ps2['class'])
    assert not pa.is_common_property(ps2['group'], ps2['name'], ps2['value'], ps2['ns'], ps2['class'])
    assert not pa.is_common_property(ps1['group'], ps1['name'], ps1['value'], ps1['ns'], ps1['class'])
    pa.count_property(ps1['group'], ps1['name'], ps1['value'], ps1['ns'], ps1['class'])
    pa.count_property(ps2['group'], ps2['name'], ps2['value'], ps2['ns'], ps2['class'])
    assert pa.is_common_property(ps2['group'], ps2['name'], ps2['value'], ps2['ns'], ps2['class'])
    assert pa.is_common_property(ps1['group'], ps1['name'], ps1['value'], ps1['ns'], ps1['class'])


def test_transformer_helper() -> None:
    """Test transformer helper."""
    pa = PropertyAccounting()
    pm = PropertyManager()
    _common_test(pa, pm)


def test_transformer_helper_no_caching() -> None:
    """Test transformer helper with no caching."""
    pa = PropertyAccounting()
    pm = PropertyManager(caching=False)
    _common_test(pa, pm)


def test_transformer_helper_with_checking() -> None:
    """Test transformer with checking."""
    pa = PropertyAccounting()
    pm = PropertyManager(caching=True)
    _common_test(pa, pm)
