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
"""OSCAL utilities."""

import logging
import pathlib
import uuid
from typing import Any, Dict

from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Link
from trestle.oscal.common import Metadata
from trestle.oscal.common import Parameter
from trestle.oscal.common import ParameterGuideline
from trestle.oscal.common import ParameterValue

logger = logging.getLogger(__name__)

t_guidelines = str
t_href = str
t_id = str
t_label = str
t_ofile = str
t_oscal_version = str
t_parameters = Dict[str, Parameter]
t_timestamp = str
t_usage = str
t_values = Any
t_verbose = bool
t_version = str


class ParameterHelper():
    """Parameter Helper class is a temporary hack because Component Definition does not support Parameters."""

    def __init__(
        self, values: t_values, id_: t_id, label: t_label, href: t_href, usage: t_usage, guidelines: t_guidelines
    ) -> None:
        """Initialize."""
        self._parameter_values = ParameterValue(__root__=str(values))
        self._id = id_
        self._label = label
        self._links = [Link(href=href)]
        self._usage = usage
        self._guidelines = ParameterGuideline(prose=guidelines)

    def get_parameter(self) -> Parameter:
        """Get parameter."""
        parameter = Parameter(
            id=self._id,
            label=self._label,
            links=self._links,
            usage=self._usage,
            guidelines=[self._guidelines],
            values=[self._parameter_values]
        )
        return parameter

    def write_parameters_catalog(
        self,
        parameters: t_parameters,
        timestamp: t_timestamp,
        oscal_version: t_oscal_version,
        version: t_version,
        ofile: t_ofile,
        verbose: t_verbose,
    ) -> None:
        """Write parameters catalog."""
        parameter_metadata = Metadata(
            title='Component Parameters',
            last_modified=timestamp,
            oscal_version=oscal_version,
            version=version,
        )
        parameter_catalog = Catalog(
            uuid=str(uuid.uuid4()),
            metadata=parameter_metadata,
            params=list(parameters.values()),
        )
        if verbose:
            logger.info(f'output: {ofile}')
        parameter_catalog.oscal_write(pathlib.Path(ofile))
