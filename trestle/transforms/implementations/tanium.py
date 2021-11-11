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
from typing import Any, Dict, List

from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer
from trestle.transforms.utils.tanium_helper import OscalFactory
from trestle.transforms.utils.tanium_helper import RuleUseFactory

logger = logging.getLogger(__name__)


class TaniumTransformer(ResultsTransformer):
    """Interface for Tanium transformer."""

    def __init__(self) -> None:
        """Initialize."""
        self._modes = {}

    @property
    def analysis(self) -> List[str]:
        """Return analysis info."""
        return self._analysis

    @property
    def blocksize(self):
        """Return blocksize."""
        return self._modes.get('blocksize', None)

    @property
    def cpus_max(self):
        """Return cpus_max."""
        return self._modes.get('cpus_max', None)

    @property
    def cpus_min(self):
        """Return cpus_min."""
        return self._modes.get('cpus_min', None)

    @property
    def checking(self):
        """Return checking."""
        return self._modes.get('checking', False)

    def set_modes(self, modes: Dict[str, Any]) -> None:
        """Keep modes info."""
        if modes is not None:
            self._modes = modes

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results."""
        ts0 = datetime.datetime.now()
        results = Results()
        ru_factory = RuleUseFactory(self.get_timestamp())
        ru_list = ru_factory.make_list(blob)
        oscal_factory = OscalFactory(
            self.get_timestamp(), ru_list, self.blocksize, self.cpus_max, self.cpus_min, self.checking
        )
        results.__root__.append(oscal_factory.result)
        ts1 = datetime.datetime.now()
        self._analysis = oscal_factory.analysis
        self._analysis.append(f'transform time: {ts1-ts0}')
        return results
