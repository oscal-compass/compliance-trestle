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

import configparser
import logging
import pathlib
import sys

from pkg_resources import resource_filename

import saxonc

import trestle.core.const as const
from trestle.saxon.format_convert import JsonXmlConverter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class FedrampValidator:
    """Validator for FedRAMP compliant OSCAL documents."""

    def __init__(self, config_file: str = None):
        """Intialize FedRAMP validator."""
        config_path = pathlib.Path(resource_filename('trestle.resources', const.FEDRAMP_NIST_CONFIG_FILE)).resolve()
        if config_file is not None:
            config_path = pathlib.Path(config_file).resolve()
        if not config_path.exists():
            logger.error(f'Config file {config_path} does not exist.')
            raise Exception(f'Config file {config_path} does not exist.')

        config = configparser.ConfigParser()
        config.read_file(config_path.open('r'))
        if not config.has_section('FEDRAMP'):
            raise Exception('No Fedramp section in config file')
        fedramp = config['FEDRAMP']

        baseline_dir = fedramp.get('baseline')
        if baseline_dir is None:
            raise Exception('No Fedramp baseline property in config file.')
        self.baselines_path = pathlib.Path(resource_filename('trestle.resources', baseline_dir)).resolve()

        registry_dir = fedramp.get('registry')
        if registry_dir is None:
            raise Exception('No Fedramp registry property in config file.')
        self.registry_path = pathlib.Path(resource_filename('trestle.resources', registry_dir)).resolve()

        svrl_xsl = fedramp.get('svrl_xsl')
        if svrl_xsl is None:
            self.svrl_xsl_path = None
        else:
            self.svrl_xsl_path = pathlib.Path(resource_filename('trestle.resources', svrl_xsl)).resolve()

        ssp_xsl = fedramp.get('ssp_xsl')
        if ssp_xsl is None:
            self.ssp_xsl_path = None
        else:
            self.ssp_xsl_path = pathlib.Path(resource_filename('trestle.resources', ssp_xsl)).resolve()

        logger.info(f'Baselines dir: {self.baselines_path}')
        logger.info(f'Registry dir: {self.registry_path}')
        logger.info(f'SVRL XSL file: {self.svrl_xsl_path}')
        logger.info(f'SSP XSL file: {self.ssp_xsl_path}')

    def validate_ssp(self, ssp_file: str):
        """Validate the given SSP XML file as per FedRAMP validation rules."""
        if self.ssp_xsl_path is None:
            raise Exception('No SSP validation (xsl file) has been specified in config file.')

        ssp_path = pathlib.Path(ssp_file).resolve()
        logger.info(f'SSP file: {ssp_path}')

        if ssp_path.suffix == '.json':
            convertor = JsonXmlConverter()
            ssp_path = convertor.json2xml('ssp', str(ssp_path))
            if ssp_path is None:
                raise Exception('Errpr converting JSON to XML')
            else:
                ssp_path = ssp_path.resolve()
        elif ssp_path.suffix != '.xml':
            raise Exception(f'Unknown file extension {ssp_path.suffix}')

        logger.info('Validating SSP')
        saxon_proc = saxonc.PySaxonProcessor(license=False)

        xslt_proc = saxon_proc.new_xslt30_processor()

        # Set parameters for FedRAMP baselines and fedramp-values files.
        xslt_proc.set_parameter('baselines-base-path', saxon_proc.make_string_value(str(self.baselines_path)))
        xslt_proc.set_parameter('registry-base-path', saxon_proc.make_string_value(str(self.registry_path)))

        # Validate the SSP, returning an SVRL document as a string
        svrl_str = xslt_proc.transform_to_string(source_file=str(ssp_path), stylesheet_file=str(self.ssp_xsl_path))

        svrl_node = saxon_proc.parse_xml(xml_text=svrl_str)
        xpath_proc = saxon_proc.new_xpath_processor()
        xpath_proc.set_context(xdm_item=svrl_node)

        output = 'report.xml'
        value = xpath_proc.evaluate('//*:failed-assert')
        with open(output, 'w') as f:
            f.write(str(value))
            logger.info(f'Failed assertion written into {output}')

        # transform svrl output to html
        if self.svrl_xsl_path is not None:
            html = xslt_proc.transform_to_string(xdm_node=svrl_node, stylesheet_file=str(self.svrl_xsl_path))
            output = 'report.html'
            with open(output, 'w') as f:
                f.write(html)
                logger.info(f'HTML output of Failed assertion written into {output}')


if __name__ == '__main__':
    validator = FedrampValidator()

    # sample SSP OSCAL XML file
    ssp = 'fedramp-source/dist/content/templates/ssp/json/FedRAMP-SSP-OSCAL-Template.json'
    validator.validate_ssp(ssp)
