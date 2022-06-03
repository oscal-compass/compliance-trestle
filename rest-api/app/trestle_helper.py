# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2022 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""OSCAL trestle helper."""

import datetime
import logging
import uuid

from trestle import __version__ as trestle_version
from trestle.common import const
from trestle.oscal import OSCAL_VERSION
from trestle.oscal.assessment_results import AssessmentResults
from trestle.oscal.assessment_results import ControlSelection
from trestle.oscal.assessment_results import ImportAp
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.common import Metadata
from trestle.transforms.implementations.osco import OscoResultToOscalARTransformer

logger = logging.getLogger(__name__)


class TrestleHelper():
    """Trestle helper functions."""

    def transform(self, bytestring):
        """Transform."""
        # timestamp
        _timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()
        # metadata
        metadata = Metadata(
            title='OSCO Assessment Results',
            oscal_version=OSCAL_VERSION,
            version=trestle_version,
            last_modified=_timestamp,
        )
        # ap
        import_ap = ImportAp(href='https://rest-api')
        # control selections
        control_selection = ControlSelection()
        control_selections = [control_selection]
        # reviewed controls
        reviewed_controls = ReviewedControls(control_selections=control_selections)
        # result, valid example
        result = Result(
            uuid=str(uuid.uuid4()),
            title='title',
            description='description',
            start=_timestamp,
            reviewed_controls=reviewed_controls
        )
        results = [result]
        # results, from transform
        blob = bytestring.decode(const.FILE_ENCODING)
        osco_transformer = OscoResultToOscalARTransformer()
        transform_results = osco_transformer.transform(blob)
        results = transform_results.__root__
        # ar
        ar = AssessmentResults(uuid=str(uuid.uuid4()), metadata=metadata, import_ap=import_ap, results=results)
        return ar.oscal_serialize_json_bytes(pretty=True)


trestle_helper = TrestleHelper()
