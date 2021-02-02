# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
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
from typing import Any, List

import yaml


def update_mkdocs_meta(path: pathlib.Path, module_list: List[Any]) -> None:
    """Update the mkdocs.yml structure file to represent the latest trestle modules."""
    yaml_structure = yaml.load(path.open('r'), yaml.FullLoader)
    nav = yaml_structure['nav']
    for index in range(len(nav)):
        if 'Reference' in nav[index].keys():
            nav[index]['Reference'] = []
            nav[index]['Reference'].append({'Overview': 'api_overview.md'})
            nav[index]['Reference'].append({'trestle': module_list})

    yaml_structure['nav'] = nav
    yaml.dump(yaml_structure, path.open('w'))


def write_module_doc_metafile(dump_location: pathlib.Path, module_name: str) -> None:
    """Create a markdown file which allows mkdocstrings to index an individual module."""
    write_file = dump_location / (module_name + '.md')
    fh = write_file.open('w')
    fh.write(f'::: {module_name}\n')
    fh.write('handler: python\n')
    fh.close()


def create_module_markdowns(base_path: pathlib.Path, base_module: str, dump_location: pathlib.Path) -> List[Any]:
    """Create markdown files for running mkdocstrings and return the desired structure for use in the ToC."""
    module_arr = []
    for path in base_path.iterdir():
        module_full_name = base_module + '.' + path.stem
        struct = None
        if path.is_dir() and path.name[0] != '_':
            struct = create_module_markdowns(path, module_full_name, dump_location)
            if len(struct) > 0:
                module_arr.append({path.stem: struct})
        elif path.suffix == '.py' and path.stem[0] != '_':
            struct = dump_location.stem + '/' + module_full_name + '.md'
            write_module_doc_metafile(dump_location, module_full_name)
            module_arr.append({path.stem: struct})
    return module_arr


def md_txt(original: pathlib.Path, md_ed_license: pathlib.Path):
    """Convert the apache license into a markdown file by wrapping the content in a text escape block."""
    assert original.exists()
    orig_data = original.open('r').read()
    md_fh = md_ed_license.open('w')
    md_fh.write('```text\n')
    md_fh.write(orig_data)
    md_fh.write('\n```\n')


if __name__ == '__main__':
    # Setup structure automatically for mkdocstrings
    structer = create_module_markdowns(pathlib.Path('trestle'), 'trestle', pathlib.Path('docs/api_reference'))
    update_mkdocs_meta(pathlib.Path('mkdocs.yml'), structer)
    # Ensure single source of truth for license file
    md_txt(pathlib.Path('LICENSE'), pathlib.Path('docs/license.md'))
    md_txt(pathlib.Path('DCO1.1.txt'), pathlib.Path('docs/contributing/DCO.md'))
