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
"""Facilitate Tanium report to NIST OSCAL transformation."""

import datetime
import logging

from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer
from trestle.transforms.utils.tanium_helper import OscalFactory
from trestle.transforms.utils.tanium_helper import RuleUseFactory

logger = logging.getLogger(__name__)


class TaniumTransformer(ResultsTransformer):
    """Interface for Tanium transformer."""

    def __init__(
        self, blocksize: str = None, cpus_max: str = None, cpus_min: str = None, checking: bool = False
    ) -> None:
        """Initialize given specified args."""
        self._analysis = []
        self._blocksize = blocksize
        self._cpus_max = cpus_max
        self._cpus_min = cpus_min
        self._checking = checking

    @property
    def analysis(self):
        """Return analysis info."""
        return self._analysis

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results."""
        ts0 = datetime.datetime.now()
        results = Results()
        ru_factory = RuleUseFactory(self.get_timestamp())
        ru_list = ru_factory.make_list(blob)
        oscal_factory = OscalFactory(
            self.get_timestamp(), ru_list, self._blocksize, self._cpus_max, self._cpus_min, self._checking
        )
        results.__root__.append(oscal_factory.result)
        ts1 = datetime.datetime.now()
        self._analysis = oscal_factory.analysis
        self._analysis.append(f'transform time: {ts1-ts0}')
        return results
