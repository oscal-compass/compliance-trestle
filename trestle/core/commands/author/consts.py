# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Constants associated with trestle author commands to decrease duplication."""

SHORT_HEADER_VALIDATE = '-hv'
LONG_HEADER_VALIDATE = '--header-validate'
HEADER_VALIDATE_HELP = 'Validate the structure of a markdown yaml header and/or drawio metadata on the first tab.'

HOV_SHORT = '-hov'
HOV_LONG = '--header-only-validate'
HOV_HELP = 'Only validate the header / metadata for files. Includes project structure where appropriate.'
RECURSE_SHORT = '-r'
RECURSE_LONG = '--recurse'
RECURSE_HELP = """Recurse and validate any subdirectories."""
MODE_ARG_NAME = 'mode'
MODE_CHOICES = ['validate', 'template-validate', 'setup', 'create-sample']

TASK_NAME_SHORT = '-tn'
TASK_NAME_LONG = '--task-name'

# Readme validate
SHORT_README_VALIDATE = '-rv'
LONG_README_VALIDATE = '--readme-validate'
README_VALIDATE_HELP = 'Enable to validate README.md files otherwise README files are excluded.'
README_VALIDATE_FOLDERS_HELP = (
    'Enable to validate README.md files. Required if readme files are included in the' + 'template.'
)

# Governed heading - capability: To be removed
GH_SHORT = '-gh'
GH_LONG = '--governed-heading'
GH_HELP = "Governed heading: Heading where for each line is a superset of the template's content"

REFERENCE_TEMPLATES = {'md': 'template.md', 'drawio': 'template.drawio'}

GLOBAL_SHORT = '-g'
GLOBAL_LONG = '--global'
GLOBAL_HELP = (
    'Use a consistent template defined in .trestle/author/__global__,'
    + 'if used without a task name applies to all files within the repository.' + '\n\n'
)

EXCLUDE_SHORT = '-ex'
EXCLUDE_LONG = '--exclude'
EXCLUDE_HELP = (
    'The name of a folder, relative to the root of the trestle project,'
    + 'e.g. architecture or architecture/infrastructure.'
)
