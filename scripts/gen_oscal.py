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
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError, check_call

from oscal_normalize import normalize_files

from schema_preprocess import fixup_models, get_oscal_release

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def load_git():
    """Load git submodule for oscal."""
    # NOTE: this should only be done if the latest nist content is desired
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


def generate_oscal_init(src_dir, out_dir):
    """Generate OSCAL init."""
    init_file = out_dir / '__init__.py'
    # release
    year = str(datetime.today().year)
    release = get_oscal_release(src_dir)
    rela = release.split('.')[0]
    relb = release.split('.')[1]
    relc = release.split('.')[2]
    # read and modify lines
    lines = []
    with open(init_file, 'r') as f:
        for line in f:
            parts = line.split(' ')
            if len(parts) > 3:
                if parts[1] == 'Copyright':
                    parts[3] = year
                    line = ' '.join(parts)
            if len(parts) > 2:
                if parts[0] == 'OSCAL_VERSION':
                    line = f"OSCAL_VERSION = '{release}'\n"
                if parts[0] == 'OSCAL_VERSION_REGEX':
                    line = f"OSCAL_VERSION_REGEX = r'^{rela}\.{relb}\.[0-{relc}]$'\n"
            lines.append(line)

    # write lines
    with open(init_file, 'w') as f:
        f.writelines(lines)


def generate_models():
    """
    Generate all models including 3rd party.

    IMPORTANT NOTE: This script will leave the temporary classes in oscal/tmp for reference, but they should be deleted
    when no longer needed because some of the operations in the build will seek all .py files, and will try to act
    on these temporary files - giving an error.  So be sure to delete the oscal/tmp directory when done generating
    new classes.
    """
    logger.info('generating models')
    out_dir = Path('trestle/oscal')
    out_dir.mkdir(exist_ok=True, parents=True)
    tmp_dir = out_dir / 'tmp'
    tmp_dir.mkdir(exist_ok=True, parents=True)
    src_dir = 'release-schemas'
    generate_oscal_init(src_dir, out_dir)
    in_dir = fixup_models(src_dir)
    for full_name in in_dir.glob('oscal_*_schema.json'):
        if 'complete' in str(full_name):
            continue
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
    # at this point should load_git() if latest oscal schemas are needed
    generate_models()
    logger.info('DONE')


if __name__ == '__main__':
    sys.exit(main())
