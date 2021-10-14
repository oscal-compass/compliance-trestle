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
"""JSON to XML conversion."""

import base64
import logging
import pathlib
import sys

from pkg_resources import resource_filename

import saxonc

import trestle.core.const as const
from trestle.core.err import TrestleError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class JsonXmlConverter:
    """Converter for converting OSCAL JSON to XML format."""

    def __init__(self):
        """Initialize JSON to XML converter."""
        self.ssp_j_x_xsl_path = pathlib.Path(resource_filename('trestle.resources',
                                                               const.NIST_SSP_JSON_XML_XSL)).resolve()
        logger.info(f'SSP converter from JSON to XML: {self.ssp_j_x_xsl_path}')

        self.initial_template = const.NIST_INITIAL_TEMPLATE
        self.file_param_name = const.NIST_FILE_PARAM_NAME

    def json2xml(self, model: str, json_content: str) -> str:
        """Convert given model (as string) from JSON to XML (as string)."""
        logger.info(f'Converting {model} from JSON to XML')

        if model == 'ssp':
            xsl_path = self.ssp_j_x_xsl_path
        else:
            raise TrestleError(f'Invalid model name: {model}')

        if not xsl_path.exists():
            raise TrestleError(f'xslt converter {xsl_path} does not exist')

        saxon_proc = saxonc.PySaxonProcessor(license=False)
        xslt_proc = saxon_proc.new_xslt30_processor()

        # set initial template name in XSL file
        xslt_proc.set_property('it', self.initial_template)

        # Create data URI from JSON SSP content
        content_base64_encoded = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
        data_uri = f'data:application/json;base64,{content_base64_encoded}'

        # Set the input json file parameter for conversion
        xslt_proc.set_parameter(
            # Pass data URI to process in-memory json content
            self.file_param_name,
            saxon_proc.make_string_value(data_uri)

            # To use file instead of content - self.file_param_name, saxon_proc.make_string_value(str(file_path))
        )

        # Convert the model to XML as a string
        xml_str = xslt_proc.transform_to_string(source_file=str(xsl_path), stylesheet_file=str(xsl_path))

        return xml_str
