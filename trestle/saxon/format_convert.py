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

import configparser
import logging
import pathlib
import sys

from pkg_resources import resource_filename

import saxonc

import trestle.core.const as const

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class JsonXmlConverter:
    """Converter for converting OSCAL JSON to XML format and vice-versa."""

    def __init__(self, config_file: str = None):
        """Initialize JSON to XML converter."""
        config_path = pathlib.Path(resource_filename('trestle.resources', const.FEDRAMP_NIST_CONFIG_FILE)).resolve()
        if config_file is not None:
            config_path = pathlib.Path(config_file).resolve()
        if not config_path.exists():
            logger.error(f'Config file {config_path} does not exist.')
            raise Exception(f'Config file {config_path} does not exist.')

        config = configparser.ConfigParser()
        config.read_file(config_path.open('r'))
        if not config.has_section('NIST'):
            raise Exception('No NIST section in config file')
        nist = config['NIST']

        ssp_j_x_xsl = nist.get('ssp_json_xml_xsl')
        if ssp_j_x_xsl is None:
            self.ssp_j_x_xsl_path = None
        else:
            self.ssp_j_x_xsl_path = pathlib.Path(resource_filename('trestle.resources', ssp_j_x_xsl)).resolve()

        logger.info(f'SSP converter from JSON to XML: {self.ssp_j_x_xsl_path}')

        initial_template = nist.get('initial_template')
        if initial_template is None:
            raise Exception('No XSL initial template in config file')
        else:
            self.initial_template = initial_template

        file_param_name = nist.get('file_param_name')
        if file_param_name is None:
            raise Exception('No XSL file param name in config file')
        else:
            self.file_param_name = file_param_name

    def json2xml(self, model: str, file: str) -> pathlib.Path:
        """Convert given model file from JSON to XML."""
        logger.info(f'Converting {model} from JSON to XML')

        xsl_path = None
        if model == 'ssp':
            xsl_path = self.ssp_j_x_xsl_path
        else:
            raise Exception(f'Invalid model name: {model}')

        if xsl_path is None:
            raise Exception(f'No xslt convertor confgured for {model} convsersion from JSON to XML')

        file_path = pathlib.Path(file).resolve()
        logger.info(f'Input file: {file_path}')

        saxon_proc = saxonc.PySaxonProcessor(license=False)
        xslt_proc = saxon_proc.new_xslt30_processor()

        # set initial template name in XSL file
        logger.info(f'Setting initial template: {self.initial_template}')
        xslt_proc.set_property('it', 'from-json')

        # Set the input json file parameter for conversion
        xslt_proc.set_parameter(
            'file',
            saxon_proc.make_string_value(str(file_path)),
        )

        # Convert the model to XML, as a string
        xml_str = xslt_proc.transform_to_string(source_file=str(xsl_path), stylesheet_file=str(xsl_path))

        output = file_path.stem + '.xml'
        file_written = False
        with open(output, 'w') as f:
            f.write(str(xml_str))
            file_written = True
            logger.info(f'Output written into file: {output}')

        if file_written:
            return pathlib.Path(output).resolve()
        return None


if __name__ == '__main__':
    converter = JsonXmlConverter()

    # sample SSP OSCAL JSON file
    ssp = 'fedramp-source/dist/content/templates/ssp/json/FedRAMP-SSP-OSCAL-Template.json'
    converter.json2xml('ssp', ssp)
