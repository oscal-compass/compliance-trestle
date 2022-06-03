# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""OSCAL REST API."""

import logging
import logging.config
import sys
import traceback

from fastapi import FastAPI, HTTPException, UploadFile

from helper import helper

from trestle_helper import trestle_helper

logging.getLogger('uvicorn.error').propagate = False
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='Compliance Trestle Transformation REST API',
    description='Compliance Trestle Transformation REST API',
    version=helper.get_version(),
    license_info={
        'name': 'Apache 2.0',
        'url': 'https://www.apache.org/licenses/LICENSE-2.0.html',
    },
)


# Transform


@app.post(
    '/transform/osco/to/oscal/json',
    tags=['Transform to OSCAL'],
    response_model=str,
    name='Transform OSCO data into OSCAL assessment-results in json format',
    description='Transform OSCO data into OSCAL assessment-results in json format.'
)
async def transform_osco(file_raw_data: UploadFile):
    """Transform raw OSCO data into OSCAL assessment-results."""
    try:
        bytestring = await file_raw_data.read()
        results = trestle_helper.transform(bytestring)
    except Exception:
        logger.info(traceback.format_exc())
        raise HTTPException(status_code=400, detail='Error creating assessment-results.')
    # success!
    return results
