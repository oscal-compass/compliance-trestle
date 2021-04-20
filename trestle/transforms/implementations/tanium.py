# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Facilitate Tanium report to NIST OSCAL transformation."""

import datetime
import json
import logging
from typing import List

from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer
from trestle.transforms.utils.tanium_helper import ResultsMgr

logger = logging.getLogger(__name__)


class TaniumTransformer(ResultsTransformer):
    """Interface for Tanium transformer."""

    # the current time for consistent timestamping
    _timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()

    @staticmethod
    def set_timestamp(value: str) -> None:
        """Set the default timestamp value."""
        datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        TaniumTransformer._timestamp = value

    @staticmethod
    def get_timestamp() -> str:
        """Get the default timestamp value."""
        return TaniumTransformer._timestamp

    def __init__(self):
        """Initialize."""
        self._results_mgr = ResultsMgr()
        self._results_mgr.set_timestamp(self.get_timestamp())
        self._results_mgr.get_timestamp()

    @property
    def analysis(self) -> List[str]:
        """Analysis."""
        return self._results_mgr.analysis

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results."""
        """
        The expected Tanuim blob is a string that contains embedded lines, each ending with line-end.
        Each embedded line is a json string.
        """
        results = Results()
        lines = blob.splitlines()
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                jdata = json.loads(line)
                self._results_mgr.ingest(jdata)
        results.__root__.append(self._results_mgr.result)
        return results
