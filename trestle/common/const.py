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
"""Core constants module containing all constants."""

import string

FIELDS_SET = '__fields_set__'

ROOT = '__root__'

PACKAGE_OSCAL = 'trestle.oscal'

TRESTLE_CONFIG_DIR = '.trestle'
TRESTLE_DIST_DIR = 'dist'
TRESTLE_CONFIG_FILE = 'config.ini'
TRESTLE_KEEP_FILE = '.keep'
DRAWIO_FILE_EXT = '.drawio'
MARKDOWN_FILE_EXT = '.md'

ALLOWED_EXTENSIONS_IN_DIRS = {'.json', '.xml', '.yaml', '.yml', '.md'}

# these are hyphenated - no underscore - and mixed singular and plural
MODEL_TYPE_A_PLAN = 'assessment-plan'
MODEL_TYPE_A_RESULT = 'assessment-results'
MODEL_TYPE_CATALOG = 'catalog'
MODEL_TYPE_COMPDEF = 'component-definition'
MODEL_TYPE_POAM = 'plan-of-action-and-milestones'
MODEL_TYPE_PROFILE = 'profile'
MODEL_TYPE_SSP = 'system-security-plan'

# these are all plural and hyphenated - no underscore
MODEL_DIR_A_PLAN = 'assessment-plans'
MODEL_DIR_A_RESULT = 'assessment-results'
MODEL_DIR_CATALOG = 'catalogs'
MODEL_DIR_COMPDEF = 'component-definitions'
MODEL_DIR_POAM = 'plan-of-action-and-milestones'
MODEL_DIR_PROFILE = 'profiles'
MODEL_DIR_SSP = 'system-security-plans'

# these are singular except for assessment_results - and component, poam, and ssp are all abbreviated
# underscores here instead of hyphens
MODULE_NAME_A_PLAN = 'assessment_plan'
MODULE_NAME_A_RESULT = 'assessment_results'
MODULE_NAME_CATALOG = 'catalog'
MODULE_NAME_COMPDEF = 'component'
MODULE_NAME_POAM = 'poam'
MODULE_NAME_PROFILE = 'profile'
MODULE_NAME_SSP = 'ssp'

MODEL_MODULE_A_PLAN = f'{PACKAGE_OSCAL}.{MODULE_NAME_A_PLAN}'
MODEL_MODULE_A_RESULT = f'{PACKAGE_OSCAL}.{MODULE_NAME_A_RESULT}'
MODEL_MODULE_CATALOG = f'{PACKAGE_OSCAL}.{MODULE_NAME_CATALOG}'
MODEL_MODULE_COMPDEF = f'{PACKAGE_OSCAL}.{MODULE_NAME_COMPDEF}'
MODEL_MODULE_POAM = f'{PACKAGE_OSCAL}.{MODULE_NAME_POAM}'
MODEL_MODULE_PROFILE = f'{PACKAGE_OSCAL}.{MODULE_NAME_PROFILE}'
MODEL_MODULE_SSP = f'{PACKAGE_OSCAL}.{MODULE_NAME_SSP}'

MODEL_TYPE_LIST = [
    MODEL_TYPE_A_PLAN,
    MODEL_TYPE_A_RESULT,
    MODEL_TYPE_CATALOG,
    MODEL_TYPE_COMPDEF,
    MODEL_TYPE_POAM,
    MODEL_TYPE_PROFILE,
    MODEL_TYPE_SSP
]

MODEL_DIR_LIST = [
    MODEL_DIR_A_PLAN,
    MODEL_DIR_A_RESULT,
    MODEL_DIR_CATALOG,
    MODEL_DIR_COMPDEF,
    MODEL_DIR_POAM,
    MODEL_DIR_PROFILE,
    MODEL_DIR_SSP
]

MODEL_MODULE_LIST = [
    MODEL_MODULE_A_PLAN,
    MODEL_MODULE_A_RESULT,
    MODEL_MODULE_CATALOG,
    MODEL_MODULE_COMPDEF,
    MODEL_MODULE_POAM,
    MODEL_MODULE_PROFILE,
    MODEL_MODULE_SSP
]
"""Map of plural form of a model type to the oscal module that contains the classes related to it."""
MODEL_DIR_TO_MODEL_MODULE = {
    MODEL_DIR_A_PLAN: MODEL_MODULE_A_PLAN,
    MODEL_DIR_A_RESULT: MODEL_MODULE_A_RESULT,
    MODEL_DIR_CATALOG: MODEL_MODULE_CATALOG,
    MODEL_DIR_COMPDEF: MODEL_MODULE_COMPDEF,
    MODEL_DIR_POAM: MODEL_MODULE_POAM,
    MODEL_DIR_PROFILE: MODEL_MODULE_PROFILE,
    MODEL_DIR_SSP: MODEL_MODULE_SSP
}
"""Map of model type to oscal module."""
MODEL_TYPE_TO_MODEL_MODULE = {
    MODEL_TYPE_A_PLAN: MODEL_MODULE_A_PLAN,
    MODEL_TYPE_A_RESULT: MODEL_MODULE_A_RESULT,
    MODEL_TYPE_CATALOG: MODEL_MODULE_CATALOG,
    MODEL_TYPE_COMPDEF: MODEL_MODULE_COMPDEF,
    MODEL_TYPE_POAM: MODEL_MODULE_POAM,
    MODEL_TYPE_PROFILE: MODEL_MODULE_PROFILE,
    MODEL_TYPE_SSP: MODEL_MODULE_SSP
}
"""Map of model module to model type."""
MODEL_MODULE_TO_MODEL_TYPE = {
    MODEL_MODULE_A_PLAN: MODEL_TYPE_A_PLAN,
    MODEL_MODULE_A_RESULT: MODEL_TYPE_A_RESULT,
    MODEL_MODULE_CATALOG: MODEL_TYPE_CATALOG,
    MODEL_MODULE_COMPDEF: MODEL_TYPE_COMPDEF,
    MODEL_MODULE_POAM: MODEL_TYPE_POAM,
    MODEL_MODULE_PROFILE: MODEL_TYPE_PROFILE,
    MODEL_MODULE_SSP: MODEL_TYPE_SSP
}
"""Map of model type to model directory."""
MODEL_TYPE_TO_MODEL_DIR = {
    MODEL_TYPE_A_PLAN: MODEL_DIR_A_PLAN,
    MODEL_TYPE_A_RESULT: MODEL_DIR_A_RESULT,
    MODEL_TYPE_CATALOG: MODEL_DIR_CATALOG,
    MODEL_TYPE_COMPDEF: MODEL_DIR_COMPDEF,
    MODEL_TYPE_POAM: MODEL_DIR_POAM,
    MODEL_TYPE_PROFILE: MODEL_DIR_PROFILE,
    MODEL_TYPE_SSP: MODEL_DIR_SSP
}
"""Element path separator"""
ALIAS_PATH_SEPARATOR: str = '.'

# argument names
ARG_FILE = 'file'
ARG_FILE_SHORT = 'f'

ARG_ELEMENT = 'element'
ARG_ELEMENT_SHORT = 'e'

# argument descriptions
ARG_DESC_FILE = 'Path of the file'
ARG_DESC_ELEMENT = 'Path of the element in the OSCAL model'

# Index separater for naming directories representing collection properties
IDX_SEP = '__'

# Digit prefix for split files
FILE_DIGIT_PREFIX_LENGTH = 5

# Wildcard that can be used in the element path to represent all elements
ELEMENT_WILDCARD = '*'
ARG_VALIDATE = 'validate'
ARG_VALIDATE_SHORT = 'v'

ARG_MODE = 'mode'
ARG_MODE_SHORT = 'm'
ARG_DESC_MODE = 'Mode of the operation'

ITEM = 'item'

VAL_MODE_CATALOG = 'catalog'
VAL_MODE_DUPLICATES = 'duplicates'
VAL_MODE_LINKS = 'links'
VAL_MODE_REFS = 'refs'
VAL_MODE_RULES = 'rules'
VAL_MODE_ALL = 'all'

IOF_SHORT = '-iof'
IOF_LONG = '--include-optional-fields'
IOF_HELP = 'Include fields that are optional in the OSCAL model when generating the new object.'

INIT_FULL_SHORT = '-fl'
INIT_FULL_LONG = '--full'
INIT_FULL_HELP = 'Initializes Trestle workspace for local, API and governed documents usage.'

INIT_GOVDOCS_SHORT = '-gd'
INIT_GOVDOCS_LONG = '--govdocs'
INIT_GOVDOCS_HELP = 'Initializes Trestle workspace for governed documents usage only.'

INIT_LOCAL_SHORT = '-loc'
INIT_LOCAL_LONG = '--local'
INIT_LOCAL_HELP = 'Initializes Trestle workspace for local management of OSCAL models.'

FILE_ENCODING = 'utf8'

# Trestle documentation

WEBSITE_ROOT = 'https://ibm.github.io/compliance-trestle'

BUG_REPORT = 'https://github.com/IBM/compliance-trestle/issues/new/choose'

# Sample objects
SAMPLE_UUID_STR = 'A0000000-0000-4000-8000-000000000000'

WINDOWS_PLATFORM_STR = 'Windows'

# constants related to cache

TRESTLE_CACHE_DIR = TRESTLE_CONFIG_DIR + '/cache'

HOUR_SECONDS: int = 3600

DAY_SECONDS: int = 24 * HOUR_SECONDS

FILE_URI = 'file:///'

SFTP_URI = 'sftp://'

HTTPS_URI = 'https://'

# extracts letter, colon and single slash
WINDOWS_DRIVE_URI_REGEX = r'([A-Za-z]:[\\/]?)[^\\/]'

WINDOWS_DRIVE_LETTER_REGEX = r'[A-Za-z]:'

# extract two groups corresponding to prop name and value
# need to strip white space from end of value
PROPERTY_REGEX = r'(?:###\s+Property\s+)([^\s]*)\s*:\s+(.*)'

PART_REGEX = r'(?i)(?:##\s+part\s+)(.*)'

CONTROL_REGEX = r'(?i)(?:##\s+Control\s+)(.*)'

AFTER_HASHES_REGEX = r'(?:##*\s+)(.*)'

CACHE_ABS_DIR = '__abs__'

UNIX_CACHE_ROOT = '__root__'

TRESTLE_HREF_HEADING = 'trestle://'

TRESTLE_HREF_REGEX = '^trestle://[^/]'

MATCH_ALL_EXCEPT_LETTERS_UNDERSCORE_SPACE_REGEX = '[^a-zA-Z0-9-_ \n]'

# extracts foo and bar from ...[foo](bar)...
MARKDOWN_URL_REGEX = r'\[([^\]]+)\]\(([^)]+)\)'

# Governed header template version
TEMPLATE_VERSION_REGEX = r'[0-9]+.[0-9]+.[0-9]+'

OBJECTIVE_PART = 'objective'
ASSESMENT_OBJECTIVE_PART = 'assessment-objective'
TABLE_OF_PARAMS_PART = 'table_of_parameters'

# extracts standalone uuid's from anywhere in string
UUID_REGEX = r'(?:^|[0-9A-Za-f])([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12})(?:$|[^0-9A-Za-z])'  # noqa FS003 E501

SSP_MAIN_COMP_NAME = 'This System'

THIS_SYSTEM_AS_KEY = 'this-system'

SSP_MD_HRULE_LINE = '______________________________________________________________________'

SSP_MD_IMPLEMENTATION_QUESTION = 'What is the solution and how is it implemented?'

SSP_MD_LEAVE_BLANK_TEXT = '<!-- Please leave this section blank and enter implementation details in the parts below. -->'  # noqa E501

SSP_ADD_IMPLEMENTATION_PREFIX = '<!-- Add control implementation description here for '

STATEMENT = 'statement'

CLOSE_COMMENT = ' -->'

SSP_ADD_IMPLEMENTATION_FOR_STATEMENT_TEXT = SSP_ADD_IMPLEMENTATION_PREFIX + STATEMENT + CLOSE_COMMENT

SSP_ADD_IMPLEMENTATION_FOR_ITEM_TEXT = SSP_ADD_IMPLEMENTATION_PREFIX + ITEM

SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT = SSP_ADD_IMPLEMENTATION_PREFIX + 'control'

SSP_ADD_THIS_SYSTEM_IMPLEMENTATION_FOR_CONTROL_TEXT = f'<!-- Add implementation prose for the main {SSP_MAIN_COMP_NAME} component for control'  # noqa E501

SSP_SYSTEM_CONTROL_IMPLEMENTATION_TEXT = 'This is the control implementation for the system.'

SSP_VALUES = 'ssp-values'

PROFILE_ADD_REQUIRED_SECTION_FOR_CONTROL_TEXT = '<!-- Add prose here for required Section'

PROFILE = 'profile'

TITLE = 'title'

NAME = 'name'

HREF = 'href'

NCNAME_REGEX = r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'  # noqa FS003 E501

NCNAME_UTF8_FIRST_CHAR_OPTIONS = string.ascii_letters + '_'

NCNAME_UTF8_OTHER_CHAR_OPTIONS = string.ascii_letters + string.digits + '_.-'

DISPLAY_VERBOSE_OUTPUT = 'Display verbose output'

HELP_YAML_PATH = 'Path to the optional yaml header file'
HELP_FO_OUTPUT = 'Overwrites the content of all markdowns in the output folder.'

HELP_OVERWRITE_HEADER_VALUES = (
    'Flag to overwrite values in a markdown control header.'
    + ' If a separate yaml header is passed in with -y, any items in the markdown header that are common with the'
    + ' provided header will be overwritten by the new values.  But new items passed in will always be added to the'
    + ' markdown header.'
)

HELP_REGENERATE = 'Flag to force generation of new uuids in the model'

HELP_VERSION = 'New version for the assembled model'

HELP_SECTIONS = 'Comma-separated list of sections as short_name_no_spaces:long name with spaces'

HELP_REQUIRED_SECTIONS = 'Short names of sections that must be in the assembled model, comma-separated'

HELP_ALLOWED_SECTIONS = 'Short names of sections that are allowed to be in the assembled model, comma-separated'

HELP_MARKDOWN_NAME = 'Name of the output generated profile markdown folder'

HELP_COMPDEFS = 'Comma-separated list of component-definitions for the ssp.'

FILTER_BY_PROFILE = 'filter-by-profile'

FILTER_BY_COMPONENTS = 'filter-by-components'

FILTER_EXCLUDE_COMPONENTS = 'filter-exclude-components'

GENERATE_RESOLVED_CATALOG = 'generate-resolved-catalog'

TRANSFORM_TYPES = [FILTER_BY_PROFILE, FILTER_BY_COMPONENTS, FILTER_EXCLUDE_COMPONENTS, GENERATE_RESOLVED_CATALOG]

TRESTLE_TAG = 'x-trestle-'

TRESTLE_PROPS_TAG = TRESTLE_TAG + 'props'

NAMESPACE_NIST = 'https://csrc.nist.gov/ns/oscal'

SSP_FEDRAMP_TAG = TRESTLE_TAG + 'fedramp-props'

TRESTLE_GLOBAL_TAG = TRESTLE_TAG + 'global'

NAMESPACE_FEDRAMP = 'https://fedramp.gov/ns/oscal'

LEV_AUTH_UUID = 'leveraged-authorization-uuid'

STATUS_INHERITED = 'inherited'

STATUS_PARTIALLY_IMPLEMENTED = 'partially-implemented'

STATUS_PLANNED_COMPLETION_DATE = 'planned-completion-date'

STATUS_COMPLETION_DATE = 'completion-date'

CONTROL_ORIGINATION = 'control-origination'

IMPLEMENTATION_STATUS = 'implementation-status'

IMPLEMENTATION_STATUS_HEADER = 'Implementation Status'

IMPLEMENTATION_STATUS_REMARKS_HEADER = 'Implementation Status Remarks'

REMARKS = 'Remarks'

STATUS_REMARKS = 'status-remarks'

PROVIDED_STATEMENT_DESCRIPTION = 'Provided Statement Description'

RESPONSIBILITY_STATEMENT_DESCRIPTION = 'Responsibility Statement Description'

# Following 5 are allowed state tokens for
# SSP -> ControlImplementation -> ImplementedRequirements -> ByComponents -> common.ImplementationStatus -> State
# Also                         -> ImplementedRequirements -> Statements -> ByComponents ...
# But NIST says they may also be locally defined
STATUS_IMPLEMENTED = 'implemented'

STATUS_PARTIAL = 'partial'

STATUS_PARTIALLY_IMPLEMENTED = 'partially-implemented'

STATUS_PLANNED = 'planned'

STATUS_ALTERNATIVE = 'alternative'

STATUS_NOT_APPLICABLE = 'not-applicable'

# Following 4 needed by SSP -> SystemImplementation -> SystemComponent -> Status -> State1
# and by SSP -> SystemCharacteristics -> Status1 -> State
STATUS_OPERATIONAL = 'operational'

STATUS_UNDER_DEVELOPMENT = 'under-development'

STATUS_DISPOSITION = 'disposition'

STATUS_OTHER = 'other'

# Needed only by SystemCharacteristics
STATUS_UNDER_MAJOR_MODIFICATION = 'under-major-modification'

STATUS_ALL = [
    STATUS_IMPLEMENTED,
    STATUS_PARTIAL,
    STATUS_PARTIALLY_IMPLEMENTED,
    STATUS_PLANNED,
    STATUS_ALTERNATIVE,
    STATUS_NOT_APPLICABLE,
    STATUS_OPERATIONAL,
    STATUS_UNDER_DEVELOPMENT,
    STATUS_DISPOSITION,
    STATUS_OTHER,
    STATUS_UNDER_MAJOR_MODIFICATION
]

STATUS_PROMPT = f'<!-- For implementation status enter one of: {STATUS_IMPLEMENTED}, {STATUS_PARTIAL}, {STATUS_PLANNED}, {STATUS_ALTERNATIVE}, {STATUS_NOT_APPLICABLE} -->'  # noqa E501

RULES_WARNING = '<!-- Note that the list of rules under ### Rules: is read-only and changes will not be captured after assembly to JSON -->'  # noqa E501

SATISFIED_STATEMENT_COMMENT = (
    '<!-- Use this section to explain how'
    ' the inherited responsibility is being satisfied. -->'
)

THIS_SYSTEM_PROMPT = '### ' + SSP_MAIN_COMP_NAME

RESPONSIBLE_ROLE = 'responsible-role'

RESPONSIBLE_ROLES = 'responsible-roles'

HELP_SET_PARAMS = 'set parameters and properties based on the yaml header in control markdown'

SET_PARAMS_TAG = TRESTLE_TAG + 'set-params'

RULES_PARAMS_TAG = TRESTLE_TAG + 'rules-params'

COMP_DEF_RULES_PARAM_VALS_TAG = TRESTLE_TAG + 'comp-def-rules-param-vals'

TRESTLE_LEVERAGING_COMP_TAG = TRESTLE_TAG + 'leveraging-comp'

TRESTLE_STATEMENT_TAG = TRESTLE_TAG + 'statement'

PARAM_VALUES_TAG = TRESTLE_TAG + 'param-values'

COMP_DEF_RULES_TAG = TRESTLE_TAG + 'comp-def-rules'

PROFILE_VALUES = 'profile-values'

COMPONENT_VALUES = 'component-values'

VALUES = 'values'

GUIDELINES = 'guidelines'

LABEL = 'label'

SECTIONS_TAG = TRESTLE_TAG + 'sections'

EDITABLE_CONTENT = 'Editable Content'

SORT_ID = 'sort-id'

TRESTLE_IMP_STATUS_TAG = 'trestle-imp-status'

TRESTLE_ADD_PROPS_TAG = TRESTLE_TAG + 'add-props'

TRESTLE_INHERITED_PROPS_TAG = TRESTLE_TAG + 'inherited-props'

CONTROL_OBJECTIVE_HEADER = '## Control Objective'

CONTROL_STATEMENT_HEADER = '## Control Statement'

CONTROL_HEADER = '## Control'

REPLACE_ME = 'REPLACE_ME'

PROVIDED_UUID = 'provided-uuid'

RESPONSIBILITY_UUID = 'responsibility-uuid'

YAML_PROPS_COMMENT = """  # Add or modify control properties here
  # Properties may be at the control or part level
  # Add control level properties like this:
  #   - name: ac1_new_prop
  #     value: new property value
  #
  # Add properties to a statement part like this, where "b." is the label of the target statement part
  #   - name: ac1_new_prop
  #     value: new property value
  #     smt-part: b.
  #
"""

YAML_SSP_VALUES_COMMENT = """  # You may set values for parameters in the assembled SSP by adding
  #
  # ssp-values:
  #   - value 1
  #   - value 2
  #
  # below a section of values:
  # The values list refers to the values in the resolved profile catalog, and the ssp-values represent new values
  # to be placed in SetParameters of the SSP.
  #
"""

YAML_PROFILE_VALUES_COMMENT = """  # You may set values for parameters in the assembled Profile by adding
  #
  # profile-values:
  #   - value 1
  #   - value 2
  #
  # below a section of values:
  # The values list refers to the values in the catalog, and the profile-values represent values
  # in SetParameters of the Profile.
  #
"""

YAML_RULE_PARAM_VALUES_SSP_COMMENT = """  # You may set new values for rule parameters by adding
  #
  # ssp-values:
  #   - value 1
  #   - value 2
  #
  # below a section of values:
  # The values list refers to the values as set by the components, and the ssp-values are the new values
  # to be placed in SetParameters of the SSP.
  #
"""

YAML_RULE_PARAM_VALUES_COMPONENT_COMMENT = """  # You may set new values for rule parameters by adding
  #
  # component-values:
  #   - value 1
  #   - value 2
  #
  # below a section of values:
  # The values list refers to the values as set by the components, and the component-values are the new values
  # to be placed in SetParameters of the component definition.
  #
"""

YAML_LEVERAGED_COMMENT = """  # Add or modify leveraged SSP Statements here.
"""

YAML_LEVERAGING_COMP_COMMENT = """  # Leveraged statements can be optionally associated with components in this system.
  # Associate leveraged statements to Components of this system here:
"""

DISPLAY_NAME = 'display-name'

TRESTLE_GENERIC_NS = 'https://ibm.github.io/compliance-trestle/schemas/oscal'

RESOLUTION_SOURCE = 'resolution-source'

# call it tracker to distinguish from the externally visible TRESTLE_INHERITED_PROPS_TAG
TRESTLE_INHERITED_PROPS_TRACKER = 'trestle_inherited_props_tracker'

RULE_ID = 'Rule_Id'

HEADER_RULE_ID = 'rule-id'

RULE_DESCRIPTION = 'Rule_Description'

PARAMETER_ID = 'Parameter_Id'

PARAMETER_DESCRIPTION = 'Parameter_Description'

PARAMETER_VALUE_ALTERNATIVES = 'Parameter_Value_Alternatives'

ONE = 'one'

ONE_OR_MORE_HYPHENED = 'one-or-more'

ONE_OR_MORE_SPACED = 'one or more'

VALUE_ASSIGNED_PREFIX = 'value-assigned-prefix'

VALUE_NOT_ASSIGNED_PREFIX = 'value-not-assigned-prefix'

CONTROL_IMPLEMENTATION = 'control-implementation'

AGGREGATES = 'aggregates'

ALT_IDENTIFIER = 'alt-identifier'

IMPLEMENTED_REQUIREMENT = 'implemented-requirement'

# Following 5 are allowed control origination values for
# SSP -> ControlImplementation -> ImplementedRequirements -> prop[@name='control-origination']/@value
ORIGINATION_ORGANIZATION = 'organization'

ORIGINATION_SYSTEM_SPECIFIC = 'system-specific'

ORIGINATION_CUSTOMER_CONFIGURED = 'customer-configured'

ORIGINATION_CUSTOMER_PROVIDED = 'customer-provided'

ORIGINATION_INHERITED = 'inherited'

# Constant relation to the inheritance view Markdown

INHERITANCE_VIEW_DIR = 'inheritance'

HELP_LEVERAGED = 'Name of the SSP to be leveraged.'

SATISFIED_STATEMENT_DESCRIPTION = 'Satisfied Statement Description'
