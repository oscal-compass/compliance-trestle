# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Automation for documentation building.

mkdocs is a great system, however, there are a few areas where it's a bit messy.

this script is designed to close a few automation gaps for files that it is desirable
they are included and must be moved.

::: trestle.oscal.catalog
handler: python
"""
import pathlib
import shutil
from typing import Any, Dict, List


def write_module_doc_metafile(dump_location: pathlib.Path, module_name: str) -> None:
    """Create a markdown file which allows mkdocstrings to index an individual module."""
    write_file = dump_location / (module_name.replace('.', '/') + '.md')
    write_file.parent.mkdir(parents=True, exist_ok=True)
    fh = write_file.open('w', encoding='utf8')
    # yaml header
    fh.write('---\n')
    fh.write(f'title: {module_name}\n')
    fh.write(f'description: Documentation for {module_name} module\n')
    fh.write('---\n\n')
    fh.write(f'::: {module_name}\n')  # noqa: E231
    fh.write('handler: python\n')
    fh.close()


def get_key(var: Dict[str, Any]) -> str:
    """Get the first key from a dict."""
    # Dict has only one key
    return list(var.keys())[0]


def create_module_markdowns(base_path: pathlib.Path, base_module: str, dump_location: pathlib.Path) -> List[Any]:
    """Create markdown files for running mkdocstrings and return the desired structure for use in the ToC."""
    # First clean the directory
    module_arr = []
    for path in base_path.iterdir():
        module_full_name = base_module + '.' + path.stem
        struct = None
        if path.is_dir() and path.name[0] != '_':
            struct = create_module_markdowns(path, module_full_name, dump_location)
            if len(struct) > 0:
                module_arr.append({path.stem: struct})
        elif path.suffix == '.py' and path.stem[0] != '_':
            struct = dump_location.stem + '/' + module_full_name.replace('.', '/') + '.md'
            write_module_doc_metafile(dump_location, module_full_name)
            module_arr.append({path.stem: struct})
    module_arr.sort(key=get_key)
    return module_arr


def md_txt(original: pathlib.Path, md_ed_license: pathlib.Path):
    """Convert the apache license into a markdown file by wrapping the content in a text escape block."""
    assert original.exists()
    orig_data = original.open('r', encoding='utf8').read()
    md_fh = md_ed_license.open('w', encoding='utf8')
    md_fh.write('```text\n')
    md_fh.write(orig_data)
    md_fh.write('\n```\n')


def cleanup_directory(dump_location: pathlib.Path):
    """Cleanup a directory by removing all content and recreating."""
    if dump_location.is_dir():
        shutil.rmtree(dump_location)
        dump_location.mkdir()
    elif dump_location.is_file():
        raise Exception(f'{dump_location} Cannot be a file')
    else:
        dump_location.mkdir()


if __name__ == '__main__':
    # Setup structure automatically for mkdocstrings
    api_ref_location = pathlib.Path('docs/reference/API')
    cleanup_directory(api_ref_location)
    structer = create_module_markdowns(pathlib.Path('trestle'), 'trestle', api_ref_location)
    # Ensure single source of truth for license file
    md_txt(pathlib.Path('LICENSE'), pathlib.Path('docs/license.md'))
    md_txt(pathlib.Path('DCO1.1.txt'), pathlib.Path('docs/contributing/DCO.md'))
