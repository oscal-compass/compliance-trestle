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
"""FedRAMP Validation API."""

import logging
import pathlib
import sys

from pkg_resources import resource_filename

import saxonc

import trestle.core.const as const
from trestle.core.err import TrestleError
from trestle.saxon.format_convert import JsonXmlConverter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class FedrampValidator:
    """Validator for FedRAMP compliant OSCAL documents."""

    def __init__(self):
        """Intialize FedRAMP validator."""
        self.baselines_path = pathlib.Path(resource_filename('trestle.resources', const.FEDRAM_BASELINE)).resolve()
        if not self.baselines_path.exists():
            raise TrestleError(f'Fedramp baseline directory {self.baselines_path} does not exist')

        self.registry_path = pathlib.Path(resource_filename('trestle.resources', const.FEDRAMP_REGISTRY)).resolve()
        if not self.registry_path.exists():
            raise TrestleError(f'Fedramp registry directory {self.registry_path} does not exist')

        self.ssp_xsl_path = pathlib.Path(resource_filename('trestle.resources', const.FEDRAMP_SSP_XSL)).resolve()

        self.svrl_xsl_path = pathlib.Path(resource_filename('trestle.resources', const.FEDRAM__SVRL_XSL)).resolve()

        logger.debug(f'Baselines dir: {self.baselines_path}')
        logger.debug(f'Registry dir: {self.registry_path}')
        logger.debug(f'SSP XSL file: {self.ssp_xsl_path}')
        logger.debug(f'SVRL XSL file: {self.svrl_xsl_path}')

    def validate_ssp(self, ssp_content: str, data_format: str) -> bool:
        """Validate the given SSP content as per FedRAMP validation rules."""
        if not self.ssp_xsl_path.exists():
            raise TrestleError(f'SSP validation (xsl file) {self.ssp_xsl_path} does not exist')

        if data_format.upper() == 'JSON':
            converter = JsonXmlConverter()
            xml_content = converter.json2xml('ssp', ssp_content)
            if xml_content is None:
                raise TrestleError('Error converting JSON to XML')
        elif data_format.upper() == 'XML':
            xml_content = ssp_content
        else:
            raise TrestleError(f'Unknown SSP format {data_format}')

        logger.info('Validating SSP')
        saxon_proc = saxonc.PySaxonProcessor(license=False)
        xslt_proc = saxon_proc.new_xslt30_processor()

        # Set parameters for FedRAMP baselines and fedramp-values files
        xslt_proc.set_parameter('baselines-base-path', saxon_proc.make_string_value(str(self.baselines_path)))
        xslt_proc.set_parameter('registry-base-path', saxon_proc.make_string_value(str(self.registry_path)))
        # Set to True to validate external resource references
        xslt_proc.set_parameter('param-use-remote-resources', saxon_proc.make_boolean_value(False))

        # Validate the SSP, returning an SVRL document as a string
        node = saxon_proc.parse_xml(xml_text=xml_content)
        svrl_str = xslt_proc.transform_to_string(xdm_node=node, stylesheet_file=str(self.ssp_xsl_path))

        svrl_node = saxon_proc.parse_xml(xml_text=svrl_str)
        xpath_proc = saxon_proc.new_xpath_processor()
        xpath_proc.set_context(xdm_item=svrl_node)

        value = xpath_proc.evaluate('//*:failed-assert')
        if value is not None:
            output = 'fedramp-validation-report.xml'
            with open(output, 'w') as f:
                f.write(str(value))
                logger.info(f'Failed assertion written to file: {output}')

            # transform svrl output to html
            if self.svrl_xsl_path is not None:
                html = xslt_proc.transform_to_string(xdm_node=svrl_node, stylesheet_file=str(self.svrl_xsl_path))
                output = 'fedram-validation-report.html'
                with open(output, 'w') as f:
                    f.write(html)
                    logger.info(f'HTML output of Failed assertion written to file: {output}')
            # there are failures; validation failed
            return False

        return True
