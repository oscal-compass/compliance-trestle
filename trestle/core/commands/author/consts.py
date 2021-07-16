# -*- mode:python; coding:utf-8 -*-

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
"""Constants associated with trestle author commands to decrease duplication."""

short_header_validate = '-hv'
long_header_validate = '--header-validate'
header_validate_help = 'Validate the structure of a markdown yaml header and/or drawio metadata on the first tab.'

hov_short = '-hov'
hov_long = '--header-only-validate'
hov_help = 'Only validate the header / metadata for files. Includes project structure where appropriate.'
recurse_short = '-r'
recurse_long = '--recurse'
recurse_help = """Recurse and validate any subdirectories."""
mode_arg_name = 'mode'
mode_choices = ['validate', 'template-validate', 'setup', 'create-sample']

task_name_short = '-tn'
task_name_long = '--task-name'

# Readme validate
short_readme_validate = '-rv'
long_readme_validate = '--readme-validate'
readme_validate_help = 'Enable to validate README.md files otherwise README files are excluded.'
readme_validate_folders_help = (
    'Enable to validate README.md files. Required if readme files are included in the' + 'template.'
)

# Governed heading - capability: To be removed
gh_short = '-gh'
gh_long = '--governed-heading'
gh_help = "Governed heading: Heading where for each line is a superset of the template's content"

reference_templates = {'md': 'template.md', 'drawio': 'template.drawio'}

global_short = '-g'
global_long = '--global'
global_help = (
    'Use a consistent template defined in .trestle/author/__global__,'
    + 'if used without a task name applies to all files within the repository.'
)
