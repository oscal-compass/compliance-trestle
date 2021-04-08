# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Define and register all transformers here."""

from typing import List

from trestle.core.base_model import OscalBaseModel
from trestle.oscal.assessment_results import Result, RoleId
from trestle.transforms.transformer_factory import ResultsTransformer, TransformerBase, TransformerFactory

# create the singleton transformer factory here, then register transformers below
transformer_factory = TransformerFactory()


# these are just examples for now to be replaced by actual transformers
class DummyTransformer(TransformerBase):
    """Example transformer."""

    def transform(self, blob: str) -> OscalBaseModel:
        """Transform the blob."""
        return RoleId(__root__='my_string')


transformer_factory.register_transformer('dummy', DummyTransformer)


class DummyResultsTransformer(ResultsTransformer):
    """Example results transformer."""

    def transform(self, blob: str) -> List[Result]:
        """Transform the blob."""
        return []


transformer_factory.register_transformer('dummy_results', DummyResultsTransformer)
