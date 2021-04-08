# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Script to generate python models from oscal using datamodel-code-generator."""
import re
import sys
from pathlib import Path
from subprocess import CalledProcessError, check_call


def load_git():
    """Load git submodule for oscal."""
    print('git add and update oscal modules')
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
        print(f'Error updating the oscal git submodule {error}')
    try:
        check_call('git submodule update --remote --merge'.split())
    except CalledProcessError as error:
        print(f'Error updating the oscal git submodule {error}')


def generate_model(full_name, out_full_name):
    """Generate a single model with datamodel-codegen."""
    print(f'generate python model and apply fix_any: {str(full_name)} -> {str(out_full_name)}')
    args = [
        'datamodel-codegen',
        '--disable-timestamp',
        '--disable-appending-item-suffix',
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
        print(f'Error calling datamodel-codegen for file {full_name} error {error}')


def fix_schema(source_file, dest_file):
    "Fix recent changes to nist schema."
    kill_list = ['oscal-ap-oscal-metadata-', 'oscal-ar-oscal-metadata-', 'oscal-catalog-oscal-metadata-', 'oscal-component-definition-oscal-metadata-',
                 'oscal-poam-metadata-', 'oscal-profile-oscal-metadata-', 'oscal-ar-oscal-assessment-common-', 'oscal-ap-oscal-assessment-common-',
                 'oscal-poam-oscal-assessment-common-', 'oscal-metadata-', 'oscal-ap-', 'oscal-ar-', 'oscal-catalog-', 'oscal-poam-', 'oscal-profile-', 'oscal-ssp-', 'oscal-component-definition-']
    with open(source_file, 'r') as src:
        with open(dest_file, 'w') as dst:
            for l in src.readlines():
                for k in kill_list:
                    l = l.replace(k, '')
                dst.write(l)


def generate_models():
    """Generate all models including 3rd party."""
    print('generating models')
    out_dir = Path('trestle/oscal')
    out_dir.mkdir(exist_ok=True, parents=True)
    tmp_dir = out_dir / 'tmp'
    tmp_dir.mkdir(exist_ok=True, parents=True)
    out_init = out_dir / '__init__.py'
    out_init.touch(exist_ok=True)

    # ver_file = out_dir / 'b4_fix' / 'datamodel-codegen-version.txt'

    # try:
    #    check_call(f'datamodel-codegen --version >> {ver_file}'.split(), shell=True)
    # except CalledProcessError as error:
    #    print(f'Error calling datamodel-codegen for version: error {error}')

    in_dir = Path('nist-source/json/schema')
    for full_name in in_dir.glob('oscal_*_schema.json'):
        fixed_name = tmp_dir / full_name.name
        fix_schema(full_name, fixed_name)
        try:
            obj = re.search('oscal_(.+?)_schema.json', str(fixed_name)).group(1)
        except AttributeError:
            print(f'Warning: filename did not parse properly: {fixed_name}')
            obj = None
            continue
        oscal_name = obj.replace('-', '_')
        out_fname = oscal_name + '.py'
        out_full_name = out_dir / out_fname
        generate_model(fixed_name, out_full_name)
    generate_model('3rd-party-schema-documents/IBM_target_schema_v1.0.0.json', out_dir / 'target.py')
    # Generate model for exchange protocol.
    generate_model(
        '3rd-party-schema-documents/OSCAL-1.0.0-rc1-IBM_observations_interchange_schema.json',
        Path('trestle/third_party') / 'exchange_protocol.py'
    )


def main():
    """Load git and generate models."""
    load_git()
    generate_models()
    print('DONE')


if __name__ == '__main__':
    sys.exit(main())
