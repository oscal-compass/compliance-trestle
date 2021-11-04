# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Script to generate python models from oscal using datamodel-code-generator."""
import logging
import re
import sys
from pathlib import Path
from subprocess import CalledProcessError, check_call

from oscal_normalize import normalize_files

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def load_git():
    """Load git submodule for oscal."""
    logger.info('git add and update oscal modules')
    try:
        check_call('git submodule add https://github.com/usnistgov/OSCAL.git nist-source'.split())
    except CalledProcessError:
        # silently ignore already existing module
        pass
    # Add second module
    try:
        check_call('git submodule add https://github.com/usnistgov/oscal-content.git nist-content'.split())
    except CalledProcessError:
        # silently ignore already existing module
        pass
    try:
        check_call('git submodule update --init'.split())
    except CalledProcessError as error:
        logger.error(f'Error updating the oscal git submodule {error}')
    try:
        check_call('git submodule update --remote --merge'.split())
    except CalledProcessError as error:
        logger.error(f'Error updating the oscal git submodule {error}')


def generate_model(full_name, out_full_name):
    """Generate a single model with datamodel-codegen."""
    logger.info(f'generate python model with datamodel-codegen: {str(full_name)} -> {str(out_full_name)}')
    args = [
        'datamodel-codegen',
        '--disable-timestamp',
        '--disable-appending-item-suffix',
        '--use-schema-description',
        '--input-file-type',
        'jsonschema',
        '--input',
        str(full_name),
        '--base-class',
        'trestle.core.base_model.OscalBaseModel',
        '--output',
        str(out_full_name)
    ]
    try:
        check_call(args)
    except CalledProcessError as error:
        logger.error(f'Error calling datamodel-codegen for file {full_name} error {error}')


def generate_models():
    """Generate all models including 3rd party."""
    logger.info('generating models')
    out_dir = Path('trestle/oscal')
    out_dir.mkdir(exist_ok=True, parents=True)
    tmp_dir = out_dir / 'tmp'
    tmp_dir.mkdir(exist_ok=True, parents=True)
    out_init = out_dir / '__init__.py'
    out_init.touch(exist_ok=True)

    in_dir = Path('nist-source/json/schema')
    for full_name in in_dir.glob('oscal_*_schema.json'):
        try:
            obj = re.search('oscal_(.+?)_schema.json', str(full_name)).group(1)
        except AttributeError:
            logger.error(f'Warning: filename did not parse properly: {full_name}')
            obj = None
            continue
        oscal_name = obj.replace('-', '_')
        out_fname = oscal_name + '.py'
        out_full_name = tmp_dir / out_fname
        generate_model(full_name, out_full_name)
    # all .py files are first generated into oscal/tmp to be normalized'
    normalize_files()


def main():
    """Load git and generate models."""
    load_git()
    generate_models()
    logger.info('DONE')


if __name__ == '__main__':
    sys.exit(main())
