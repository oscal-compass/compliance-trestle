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

SHORT_TEMPLATE_VERSION = '-tv'
LONG_TEMPLATE_VERSION = '--template-version'
TEMPLATE_VERSION_HELP = 'Specify a template version to use for the task, latest version will be used by default.'

SHORT_IGNORE = '-ig'
LONG_IGNORE = '--ignore'
IGNORE_HELP = 'Provide a regex to ignore files and folders with matching name from validation (i.e. ^_.*).'

# Readme validate
SHORT_README_VALIDATE = '-rv'
LONG_README_VALIDATE = '--readme-validate'
README_VALIDATE_HELP = 'Enable to validate README.md files otherwise README files are excluded.'
README_VALIDATE_FOLDERS_HELP = (
    'Enable to validate README.md files. Required if readme files are included in the' + 'template.'
)

START_TEMPLATE_VERSION = '0.0.1'  # first ever template version, all templates without version will be defaulted to this
TRESTLE_RESOURCES = 'trestle.resources'
TEMPLATE_VERSION_HEADER = 'x-trestle-template-version'

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
    '[DEPRECATED: use --ignore instead] The name of a folder, relative to the root of the trestle project,'
    + 'e.g. architecture or architecture/infrastructure.'
)
