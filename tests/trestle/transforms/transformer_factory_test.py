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
"""TransformFactory and related tests."""

import pytest

import trestle.common.err as err
from trestle.core.base_model import OscalBaseModel
from trestle.oscal.assessment_results import Result
from trestle.oscal.common import RoleId
from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer, TransformerBase
from trestle.transforms.transformer_singleton import transformer_factory as tf


def _make_result() -> Result:
    """Return a minimal valid Result fixture."""
    return Result.model_validate(
        {
            'uuid': 'a1d20136-37e0-42aa-9834-4e9d8c36d798',
            'title': 'Test Result',
            'description': 'Minimal result for testing.',
            'start': '2023-06-02T08:31:20-04:00',
            'reviewed-controls': {'control-selections': [{'include-controls': [{'control-id': 'ac-6.1'}]}]},
        }
    )


class DummyTransformer(TransformerBase):
    """Example transformer."""

    def transform(self, blob: str) -> OscalBaseModel:
        """Transform the blob."""
        # This example uses RoleId because it is a simple string and is otherwise arbitrary
        # Pydantic v2: RootModel uses 'root' instead of '__root__'
        return RoleId(root='my_string')


class DummyResultsTransformer(ResultsTransformer):
    """Example results transformer."""

    def transform(self, blob: str) -> Results:
        """Transform the blob."""
        return Results(root=[_make_result()])


def test_basic_transformer_operations() -> None:
    """Test basic transformer operations."""
    tf.register_transformer('dummy', DummyTransformer)
    transformer: TransformerBase = tf.get('dummy')
    # Pydantic v2: RootModel uses 'root' instead of '__root__'
    assert transformer.transform('foo') == RoleId(root='my_string')


def test_results_transformer() -> None:
    """Test results transformer."""
    tf.register_transformer('dummy', DummyResultsTransformer)
    transformer: ResultsTransformer = tf.get('dummy')
    assert transformer.transform('foo') == Results(root=[_make_result()])


def test_transformer_not_registered() -> None:
    """Test basic transformer operations."""
    with pytest.raises(err.TrestleError):
        transformer: TransformerBase = tf.get('foo')
        assert transformer is not None
