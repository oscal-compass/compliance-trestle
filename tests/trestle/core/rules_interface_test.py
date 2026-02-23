# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Tests for RulesInterface."""

from dataclasses import dataclass
from typing import List, Optional

import pytest

from trestle.common import const
from trestle.common.err import TrestleError
from trestle.core.rules import RulesInterface
from trestle.oscal import common


def _prop(name: str, value: str, remarks: Optional[str] = None) -> common.Property:
    """Create a property with minimal required fields."""
    return common.Property(name=name, value=value, remarks=remarks)


@dataclass
class DummyItem:
    """Minimal item with props for rules parsing."""

    props: Optional[List[common.Property]] = None


@dataclass
class DummyImpReq:
    """Minimal implemented requirement with props and statements."""

    props: Optional[List[common.Property]] = None
    statements: Optional[List[DummyItem]] = None


def test_get_rules_dict_from_item_multiple_and_missing() -> None:
    """Test rules dict extraction with missing pair."""
    props = [
        _prop(const.RULE_ID, 'rule-a', 'rule-a-id'),
        _prop(const.RULE_DESCRIPTION, 'desc-a'),
        _prop(const.RULE_ID, 'rule-b', 'rule-b-id'),
        _prop('other-prop', 'other'),
    ]
    rules_dict, rules_props = RulesInterface.get_rules_dict_from_item(DummyItem(props))
    assert rules_dict == {'rule-a-id': {'name': 'rule-a', 'description': 'desc-a'}}
    assert rules_props == props[:3]


def test_item_has_rules_true_false() -> None:
    """Test item_has_rules true and false paths."""
    assert RulesInterface.item_has_rules(DummyItem([_prop(const.RULE_ID, 'rule-a', 'rule-a-id')]))
    assert not RulesInterface.item_has_rules(DummyItem([_prop('other-prop', 'other')]))


def test_get_rule_list_for_item() -> None:
    """Test rule list extraction from item."""
    props = [
        _prop(const.RULE_ID, 'rule-a', 'rule-a-id'),
        _prop(const.RULE_DESCRIPTION, 'desc-a'),
        _prop('other-prop', 'other'),
    ]
    rule_list, rule_props = RulesInterface.get_rule_list_for_item(DummyItem(props))
    assert rule_list == ['rule-a']
    assert rule_props == [props[0]]


def test_get_rule_list_for_imp_req() -> None:
    """Test rule list extraction from implemented requirement."""
    imp_req = DummyImpReq(
        props=[_prop(const.RULE_ID, 'rule-a', 'rule-a-id')],
        statements=[
            DummyItem([_prop(const.RULE_ID, 'rule-b', 'rule-b-id')]),
            DummyItem([_prop(const.RULE_ID, 'rule-c', 'rule-c-id')]),
            DummyItem([_prop(const.RULE_ID, 'rule-b', 'rule-b-id')]),
        ],
    )
    comp_rules, statement_rules, rule_props = RulesInterface.get_rule_list_for_imp_req(imp_req)
    assert comp_rules == ['rule-a']
    assert statement_rules == ['rule-b', 'rule-c']
    assert len(rule_props) == 4


def test_get_params_dict_from_item_normal_and_remarks_none() -> None:
    """Test parameter parsing with valid rule id and ignored None remarks."""
    props = [
        _prop(const.PARAMETER_ID, 'param-1', 'rule-a-id'),
        _prop(const.PARAMETER_DESCRIPTION, 'param-1 desc', 'rule-a-id'),
        _prop(const.PARAMETER_VALUE_ALTERNATIVES, 'opt-1', 'rule-a-id'),
        _prop(const.PARAMETER_ID, 'param-ignored', None),
    ]
    params_dict, params_props = RulesInterface.get_params_dict_from_item(DummyItem(props))
    assert params_dict == {'rule-a-id': [{'name': 'param-1', 'description': 'param-1 desc', 'options': 'opt-1'}]}
    assert params_props == props[:3]


def test_get_params_dict_from_item_duplicate_param_id_raises() -> None:
    """Test duplicate parameter id for same rule raises error."""
    props = [_prop(const.PARAMETER_ID, 'param-1', 'rule-a-id'), _prop(const.PARAMETER_ID, 'param-1', 'rule-a-id')]
    with pytest.raises(TrestleError):
        _ = RulesInterface.get_params_dict_from_item(DummyItem(props))


def test_get_params_dict_from_item_description_without_param_raises() -> None:
    """Test description without matching param id raises error."""
    props = [
        _prop(const.PARAMETER_ID, 'param-1', 'rule-a-id'),
        _prop(const.PARAMETER_ID, 'param-2', 'rule-b-id'),
        _prop(const.PARAMETER_DESCRIPTION, 'param-1 desc', 'rule-a-id'),
    ]
    with pytest.raises(TrestleError):
        _ = RulesInterface.get_params_dict_from_item(DummyItem(props))


def test_get_params_dict_from_item_options_without_param_raises() -> None:
    """Test options without matching param id raises error."""
    props = [
        _prop(const.PARAMETER_ID, 'param-1', 'rule-a-id'),
        _prop(const.PARAMETER_ID, 'param-2', 'rule-b-id'),
        _prop(const.PARAMETER_VALUE_ALTERNATIVES, 'opt-1', 'rule-a-id'),
    ]
    with pytest.raises(TrestleError):
        _ = RulesInterface.get_params_dict_from_item(DummyItem(props))


def test_get_rules_and_params_dict_from_item() -> None:
    """Test combined rule and param parsing."""
    props = [
        _prop(const.RULE_ID, 'rule-a', 'rule-a-id'),
        _prop(const.RULE_DESCRIPTION, 'desc-a'),
        _prop(const.PARAMETER_ID, 'param-1', 'rule-a-id'),
        _prop(const.PARAMETER_DESCRIPTION, 'param-1 desc', 'rule-a-id'),
    ]
    rules_dict, params_dict, rules_props = RulesInterface.get_rules_and_params_dict_from_item(DummyItem(props))
    assert rules_dict == {'rule-a-id': {'name': 'rule-a', 'description': 'desc-a'}}
    assert params_dict == {'rule-a-id': [{'name': 'param-1', 'description': 'param-1 desc', 'options': ''}]}
    assert rules_props == props


def test_cull_props_by_rules() -> None:
    """Test culling properties by rule list."""
    props = [
        _prop(const.RULE_ID, 'rule-a', 'rule-a-id'),
        _prop(const.RULE_DESCRIPTION, 'desc-a', 'rule-a-id'),
        _prop('other-prop', 'other', 'rule-a-id'),
        _prop('unrelated-prop', 'unrelated'),
    ]
    culled = RulesInterface.cull_props_by_rules(props, ['rule-a'])
    assert culled == props[:3]
