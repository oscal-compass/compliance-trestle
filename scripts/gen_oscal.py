"""Script to generate python models from oscal using datamodel-code-generator."""

# Execute this script from the parent directory using:
# python scripts/gen_oscal.py

import re
import sys
from pathlib import Path
from subprocess import CalledProcessError, check_call

from fix_any import fix_file


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
    print(f'generate model {full_name} -> {out_full_name}')
    args = ['datamodel-codegen', '--input-file-type', 'jsonschema', '--input', full_name, '--base-class',
            'trestle.core.base_model.OscalBaseModel', '--output', out_full_name]
    try:
        check_call(args)
    except CalledProcessError as error:
        print(f'Error calling datamodel-codegen for file {full_name} error {error}')
    else:
        fix_file(out_full_name)


def generate_models():
    """Generate all models including 3rd party."""
    print('generating models')
    out_dir = Path('trestle/oscal')
    out_dir.mkdir(exist_ok=True, parents=True)
    out_dir.touch('__init__.py', exist_ok=True)

    in_dir = Path('nist-source/json/schema')
    for full_name in in_dir.glob('oscal_*_schema.json'):
        file_name = str(full_name.name)
        try:
            obj = re.search('oscal_(.+?)_schema.json', file_name).group(1)
        except AttributeError:
            print(f'Warning: filename did not parse properly: {file_name}')
            obj = None
            continue
        out_fname = obj.replace('-', '_') + '.py'
        out_full_name = out_dir / out_fname
        generate_model(str(full_name), str(out_full_name))
    generate_model('3rd-party-schema-documents/IBM_target_schema.json', str(out_dir / 'target.py'))


def main():
    """Load git and generate models."""
    load_git()
    generate_models()


if __name__ == '__main__':
    sys.exit(main())
