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
"""XLSX utilities."""

import logging
import string
from typing import Any, Dict, Iterator, List

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)


def is_sublist(needle: List[str], haystack: List[str]) -> bool:
    """Determine if needle is exactly contained in haystack."""
    list1 = [element for element in needle if element in haystack]
    list2 = [element for element in haystack if element in needle]
    return list1 == list2 and len(needle) == len(list1)


class Column():
    """Spread sheet columns."""

    control_id = 'ControlId'
    control_text = 'ControlText'
    version = 'Version'
    goal_name_id = 'goal_name_id'
    nist_mappings = 'NIST Mappings'
    resource_title = 'ResourceTitle'
    parameter_opt_parm = 'Parameter [optional parameter]'
    values_alternatives = 'Values default , [alternatives]'

    tokens_nist_mappings = nist_mappings.split()

    tokens_parameter_opt_parm = parameter_opt_parm.split()
    rename_parameter_opt_parm = 'ParameterName'

    tokens_values_alternatives = values_alternatives.split()
    rename_values_alternatives = 'ParameterValue'

    help_list = []
    text1 = '                      '
    text2 = f'column "{control_id}" contains goal ID.'
    help_list.append(text1 + text2)
    text2 = f'column "{control_text}" contains goal text.'
    help_list.append(text1 + text2)
    text2 = f'column "{version}" contains version.'
    help_list.append(text1 + text2)
    text2 = f'columns "{nist_mappings}" contain controls.'
    help_list.append(text1 + text2)
    text2 = f'column "{resource_title}" contains component name.'
    help_list.append(text1 + text2)
    text2 = f'column "{goal_name_id}" contains goal name.'
    help_list.append(text1 + text2)
    text2 = f'column "{parameter_opt_parm}" contains parameter name + description, separated by newline.'
    help_list.append(text1 + text2)
    text2 = f'column "{values_alternatives}" contains parameter values.'
    help_list.append(text1 + text2)


class XlsxHelper:
    """Xlsx Helper common functions and assistance navigating spread sheet."""

    def _print_info(self, name, oscal_name) -> None:
        """Print the help string."""
        logger.info(f'Help information for {name} task.')
        logger.info('')
        logger.info(f'Purpose: From spread sheet and catalog produce OSCAL {oscal_name} file.')
        logger.info('')
        logger.info(f'Configuration flags sit under [task.{name}]:')
        if oscal_name == 'component_definition':
            text1 = '  catalog-file      = '
            text2 = '(required) the path of the OSCAL catalog file.'
            logger.info(text1 + text2)
        text1 = '  spread-sheet-file = '
        text2 = '(required) the path of the spread sheet file.'
        logger.info(text1 + text2)
        text1 = '  work-sheet-name   = '
        text2 = '(required) the name of the work sheet in the spread sheet file.'
        logger.info(text1 + text2)
        for line in Column.help_list:
            logger.info(line)
        text1 = '  output-dir        = '
        text2 = '(required) the path of the output directory for synthesized OSCAL .json files.'
        logger.info(text1 + text2)
        text1 = '  output-overwrite  = '
        text2 = '(optional) true [default] or false; replace existing output when true.'
        logger.info(text1 + text2)

    def load(self, spread_sheet: str, sheet_name: str) -> None:
        """Initialize."""
        self._spread_sheet = spread_sheet
        self._sheet_name = sheet_name
        self._wb = load_workbook(self._spread_sheet)
        self._work_sheet = self._wb[self._sheet_name]
        self._map_name_to_letters = {}
        # accumulators
        self.rows_missing_goal_name_id = []
        self.rows_invalid_goal_name_id = []
        self.rows_invalid_parameter_name = []
        self.rows_missing_controls = []
        # map columns
        self._map_columns()

    def row_generator(self) -> Iterator[int]:
        """Generate rows until goal_id is None."""
        row = 1
        while True:
            row = row + 1
            goal_id = self._get_goal_id(row)
            if goal_id is None:
                break
            yield row

    def get_goal_name_id(self, row: int) -> str:
        """Get goal_name_id from work_sheet."""
        col = self._get_column_letter(Column.goal_name_id)
        value = self._work_sheet[col + str(row)].value
        if value is None:
            self.rows_missing_goal_name_id.append(row)
            value = self._get_goal_id(row)
        value = str(value).strip()
        return value

    def get_goal_name_id_strict(self, row: int) -> str:
        """Get goal_name_id from work_sheet."""
        col = self._get_column_letter(Column.goal_name_id)
        value = self._work_sheet[col + str(row)].value
        if value is None:
            self.rows_missing_goal_name_id.append(row)
        else:
            svalue = str(value).strip()
            value = ''.join(str(svalue).split())
            if value != svalue:
                self.rows_invalid_goal_name_id.append(row)
        return value

    def get_parameter_usage(self, row: int) -> str:
        """Get parameter_usage from work_sheet."""
        return self.get_goal_remarks(row)

    def get_parameter_value_default(self, row: int) -> str:
        """Get parameter_value_default from work_sheet."""
        col = self._get_column_letter(Column.rename_values_alternatives)
        value = self._work_sheet[col + str(row)].value
        if value is not None:
            value = str(value).split(',')[0].strip()
        return value

    def get_parameter_values(self, row: int) -> str:
        """Get parameter_values from work_sheet."""
        col = self._get_column_letter(Column.rename_values_alternatives)
        value = self._work_sheet[col + str(row)].value
        if value is None:
            logger.debug(f'row {row} col {col} missing value')
        # massage into comma separated list of values
        else:
            value = str(value).strip().replace(' ', '')
            value = value.replace(',[]', '')
            value = value.replace('[', '')
            value = value.replace(']', '')
        return value

    def _get_goal_text(self, row: int) -> str:
        """Get goal_text from work_sheet."""
        col = self._get_column_letter(Column.control_text)
        goal_text = self._work_sheet[col + str(row)].value
        # normalize & tokenize
        value = goal_text.replace('\t', ' ')
        return value

    def _get_goal_text_tokens(self, row: int) -> List[str]:
        """Get goal_text tokens from work_sheet."""
        goal_text = self._get_goal_text(row)
        tokens = goal_text.split()
        return tokens

    def get_goal_remarks(self, row: int) -> str:
        """Get goal_remarks from work_sheet."""
        tokens = self._get_goal_text_tokens(row)
        # replace "Check whether" with "Ensure", if present
        if len(tokens) > 0:
            if tokens[0] == 'Check':
                if len(tokens) > 1:
                    if tokens[1] == 'whether':
                        tokens.pop(0)
                tokens[0] = 'Ensure'
        value = ' '.join(tokens)
        return value

    def get_controls(self, row: int) -> Dict[str, List[str]]:
        """Produce dict of controls mapped to statements.

        Example: {'au-2': ['(a)', '(d)'], 'au-12': [], 'si-4': ['(a)', '(b)', '(c)']}
        """
        value = {}
        for col in self._get_column_letter(Column.nist_mappings):
            control = self._work_sheet[col + str(row)].value
            if control is None:
                continue
            # remove blanks
            control = ''.join(control.split())
            if len(control) < 1 or control.lower() == 'none':
                continue
            # remove rhs of : inclusive
            if ':' in control:
                control = control.split(':')[0]
            # remove alphabet parts of control & accumulate in statements
            control, statements = self._normalize_control(control)
            # skip bogus control made up if dashes only
            if len(control.replace('-', '')) == 0:
                continue
            if control not in value.keys():
                value[control] = statements
        if len(value.keys()) == 0:
            self.rows_missing_controls.append(row)
        logger.debug(f'row: {row} controls {value}')
        return value

    def get_component_name(self, row: int) -> str:
        """Get component_name from work_sheet."""
        col = self._get_column_letter(Column.resource_title)
        value = self._work_sheet[col + str(row)].value
        if value is None:
            raise RuntimeError(f'row {row} col {col} missing component name')
        return value

    def get_parameter_name_and_description(self, row: int) -> (str, str):
        """Get parameter_name and description from work_sheet."""
        name = None
        description = None
        col = self._get_column_letter(Column.rename_parameter_opt_parm)
        combined_values = self._work_sheet[col + str(row)].value
        if combined_values is not None:
            if '\n' in combined_values:
                parameter_parts = combined_values.split('\n')
            elif ' ' in combined_values:
                parameter_parts = combined_values.split(' ', 1)
            else:
                parameter_parts = combined_values
            if len(parameter_parts) == 2:
                name = parameter_parts[1].strip()
                description = parameter_parts[0].strip()
                sname = str(name).strip()
                name = sname.replace(' ', '_')
                if name != sname:
                    self.rows_invalid_parameter_name.append(row)
            else:
                logger.info(f'row {row} col {col} invalid value')
        value = name, description
        return value

    def _get_goal_id(self, row: int) -> int:
        """Get goal_id from work_sheet."""
        col = self._get_column_letter(Column.control_id)
        value = self._work_sheet[col + str(row)].value
        return value

    def _get_column_letter(self, name: str) -> str:
        """Get column letter."""
        value = self.map_name_to_letters[name]
        if len(value) == 1:
            value = value[0]
        return value

    def _map_columns(self) -> None:
        """Map columns."""
        self.map_name_to_letters = {}
        columns = self._work_sheet.max_column
        for column in range(1, columns + 1):
            cell_value = self._cell_value(1, column)
            if cell_value is None:
                continue
            cell_tokens = cell_value.split()
            logger.debug(f'{cell_tokens}')
            # find columns of interest
            if cell_tokens in [[Column.control_id], [Column.control_text], [Column.version], [Column.goal_name_id]]:
                self._add_column(cell_tokens[0], column, 1)
            elif cell_tokens == Column.tokens_parameter_opt_parm:
                self._add_column(Column.rename_parameter_opt_parm, column, 1)
            elif cell_tokens == Column.tokens_values_alternatives:
                self._add_column(Column.rename_values_alternatives, column, 1)
            elif is_sublist(Column.tokens_nist_mappings, cell_tokens):
                self._add_column(Column.nist_mappings, column, 0)
            elif Column.resource_title in cell_tokens:
                self._add_column(Column.resource_title, column, 0)
        # insure expected columns found
        for name in [Column.control_id,
                     Column.control_text,
                     Column.version,
                     Column.goal_name_id,
                     Column.nist_mappings,
                     Column.resource_title,
                     Column.rename_parameter_opt_parm,
                     Column.rename_values_alternatives]:
            if name not in self.map_name_to_letters.keys():
                raise RuntimeError(f'missing column {name}')

    def _add_column(self, name: str, column: int, limit: int) -> None:
        """Add column."""
        if name not in self.map_name_to_letters:
            self.map_name_to_letters[name] = []
        if limit > 0 and len(self.map_name_to_letters[name]) == limit:
            raise RuntimeError(f'duplicate column {name} {get_column_letter(column)}')
        self.map_name_to_letters[name].append(get_column_letter(column))

    def _cell_value(self, row: int, col: int) -> Any:
        """Get value for cell, adjusting for merged cells."""
        cell = self._work_sheet.cell(row, col)
        retval = cell.value
        if isinstance(cell, MergedCell):
            # cell is merged
            for mc_range in self._work_sheet.merged_cells.ranges:
                coord = get_column_letter(col) + str(row)
                if coord in mc_range:
                    retval = mc_range.start_cell.value
        return retval

    def _normalize_control(self, control: str) -> (str, List[str]):
        """Remove parenthesized characters from controls."""
        statements = []
        for i in string.ascii_lowercase:
            needle = '(' + i + ')'
            if needle in control:
                statements.append(needle)
                control = control.replace(needle, '')
        control = control.lower()
        return control, statements

    def report_issues(self) -> None:
        """Report issues."""
        if len(self.rows_missing_goal_name_id) > 0:
            logger.info(f'rows missing goal_name_id: {self.rows_missing_goal_name_id}')
        if len(self.rows_invalid_goal_name_id) > 0:
            logger.info(f'rows invalid goal_name_id: {self.rows_invalid_goal_name_id}')
        if len(self.rows_invalid_parameter_name) > 0:
            logger.info(f'rows invalid parameter_name: {self.rows_invalid_parameter_name}')
        if len(self.rows_missing_controls) > 0:
            logger.info(f'rows missing controls: {self.rows_missing_controls}')
