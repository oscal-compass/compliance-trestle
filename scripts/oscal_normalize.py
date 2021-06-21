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
"""
Script to noramlize oscal.

It then reorders the classes so there are minimal forwards required.
This script is normally called by gen_oscal.py when models are generated.
"""

import logging
import pathlib
import re

from trestle.oscal import OSCAL_VERSION_REGEX

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class_header = 'class '

fstems = ['assessment_plan', 'assessment_results', 'catalog', 'component', 'poam', 'profile', 'ssp']

alias_map = {
    'assessment_plan': 'assessment-plan',
    'assessment_results': 'assessment-results',
    'catalog': 'catalog',
    'component': 'component-definition',
    'poam': 'plan-of-action-and-milestones',
    'profile': 'profile',
    'ssp': 'system-security-plan'
}

camel_map = {
    'assessment_plan': 'AssessmentPlan',
    'assessment_results': 'AssessmentResults',
    'catalog': 'Catalog',
    'component': 'ComponentDefinition',
    'poam': 'PlanOfActionAndMilestones',
    'profile': 'Profile',
    'ssp': 'SystemSecurityPlan'
}


license_header = (
    '# -*- mode:python; coding:utf-8 -*-\n'
    '# Copyright (c) 2020 IBM Corp. All rights reserved.\n'
    '#\n'
    '# Licensed under the Apache License, Version 2.0 (the "License");\n'
    '# you may not use this file except in compliance with the License.\n'
    '# You may obtain a copy of the License at\n'
    '#\n'
    '#     http://www.apache.org/licenses/LICENSE-2.0\n'
    '#\n'
    '# Unless required by applicable law or agreed to in writing, software\n'
    '# distributed under the License is distributed on an "AS IS" BASIS,\n'
    '# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n'
    '# See the License for the specific language governing permissions and\n'
    '# limitations under the License.\n'
)

main_header = """
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import AnyUrl, EmailStr, Field, conint, constr

from trestle.core.base_model import OscalBaseModel
"""


class RelOrder():
    """Capture relative location of each class in list to its refs and deps."""

    def __init__(self, max_index):
        """Initialize with size of list being reordered."""
        self.latest_dep = 0
        self.earliest_ref = max_index


class ClassText():
    """Hold class text as named blocks with references to the added classes and capture its refs."""

    def __init__(self, first_line, parent_name):
        """Construct with first line of class definition and store the parent file name."""
        self.lines = [first_line.rstrip()]
        n = first_line.find('(')
        self.name = first_line[len(class_header):n]
        self.parent_names = [parent_name]
        self.orig_name = self.name
        self.refs = set()
        self.full_refs = set()
        self.found_all_links = False
        self.is_self_ref = False
        self.is_local = False

    def add_line(self, line):
        """Add new line to class text."""
        self.lines.append(line)

    def add_ref_if_good(self, ref_name):
        """Add non-empty refs."""
        if ref_name and 'common.' not in ref_name:
            self.refs.add(ref_name)

    def add_ref_pattern(self, p, line):
        """Add new class names found based on pattern."""
        new_refs = p.findall(line)
        if new_refs:
            for r in new_refs:
                if type(r) == tuple:
                    for s in r:
                        self.add_ref_if_good(s)
                else:
                    self.add_ref_if_good(r)

    @staticmethod
    def find_index(class_text_list, name):
        """Find index of class in list by name."""
        nclasses = len(class_text_list)
        for i in range(nclasses):
            if class_text_list[i].name == name:
                return i
        return -1

    def add_all_refs(self, line):
        """Find all refd class names found in line and add to references."""
        # find lone strings with no brackets
        p = re.compile(r'.*\:\s*([^\s\[\]]+).*')
        self.add_ref_pattern(p, line)
        # find objects in one or more bracket sets with possible first token and comma
        p = re.compile(r'.*\[(?:(.*),\s*)?((?:\[??[^\[]*?))\]')
        self.add_ref_pattern(p, line)
        p = re.compile(r'.*Optional\[Union\[([^,]+)')
        self.add_ref_pattern(p, line)
        return line

    def find_direct_refs(self, class_names_list):
        """Find direct refs without recursion."""
        for ref in self.refs:
            if ref == self.name:
                self.is_self_ref = True
            if ref in class_names_list and not ref == self.name:
                self.full_refs.add(ref)
        if len(self.full_refs) == 0:
            self.found_all_links = True

    def find_order(self, class_text_list):
        """Find latest dep and earliest reference."""
        ro = RelOrder(len(class_text_list) - 1)
        # find first class that needs this class
        for i, ct in enumerate(class_text_list):
            if self.name in ct.full_refs:
                ro.earliest_ref = i
                break
        # find last class this one needs
        # make sure result is deterministic and does not depend on order from set
        sorted_ref_list = sorted(self.full_refs)
        for ref in sorted_ref_list:
            n = ClassText.find_index(class_text_list, ref)
            if n > ro.latest_dep:
                ro.latest_dep = n
        return ro

    def strip_prefix(self, prefix):
        """Strip the prefix from the name only."""
        if self.name.startswith(prefix):
            self.name = self.name.replace(prefix, '', 1)


def find_forward_refs(class_list, orders):
    """Find forward references within the file."""
    forward_names = set()
    for c in class_list:
        if c.is_self_ref:
            forward_names.add(c.name)
    for i in range(len(orders)):
        if orders[i].earliest_ref < i:
            forward_names.add(class_list[i].name)

    forward_refs = []
    for c in class_list:
        if c.name in forward_names:
            forward_refs.append(f'{c.name}.update_forward_refs()')
    return forward_refs


def reorder(class_list):
    """Reorder the class list based on the location of its refs and deps."""
    # build list of all class names defined in file
    all_class_names = []
    for c in class_list:
        all_class_names.append(c.name)

    # find direct references for each class in list
    for n, c in enumerate(class_list):
        c.find_direct_refs(all_class_names)
        class_list[n] = c

    # with full dependency info, now reorder the classes to remove forward refs
    did_swap = True
    loop_num = 0
    orders = None
    while did_swap and loop_num < 1000:
        did_swap = False
        orders = []
        # find the relative placement of each class in list to its references and dependencies
        for c in class_list:
            ro = c.find_order(class_list)
            orders.append(ro)
        # find first class in list out of place and swap its dependency upwards, then break/loop to find new order
        for i, ro in enumerate(orders):
            if ro.latest_dep <= i <= ro.earliest_ref:
                continue
            # pop the out-of-place earliest ref and put it in front
            ct = class_list.pop(ro.earliest_ref)
            class_list.insert(i, ct)
            did_swap = True
            break
        loop_num += 1
    if did_swap:
        logger.info('Excess iteration in reordering!')
    forward_refs = find_forward_refs(class_list, orders)

    # return reordered list of classes with no forward refs
    return class_list, forward_refs


def constrain_oscal_version(class_list):
    """Constrain allowed oscal version."""
    for j in range(len(class_list)):
        cls = class_list[j]
        for i in range(len(cls.lines)):
            line = cls.lines[i]
            nstart = line.find('oscal_version:')
            if nstart >= 0:
                nstr = line.find('str')
                if nstr >= 0:
                    cls.lines[i] = line.replace('str', f'constr(regex={OSCAL_VERSION_REGEX})')
                    class_list[j] = cls
    return class_list


def load_classes(fstem):
    """Load all classes from a file."""
    all_classes = []
    header = []
    forward_refs = []

    class_text = None
    done_header = False

    fname = pathlib.Path('trestle/oscal/tmp') / (fstem + '.py')

    # Otherwise accumulate all class dependencies for reordering with no forward refs
    with open(fname, 'r', encoding='utf8') as infile:
        for r in infile.readlines():
            # collect forward references
            if r.find('.update_forward_refs()') >= 0:
                forward_refs.append(r)
            elif r.find(class_header) == 0:  # start of new class
                done_header = True
                if class_text is not None:  # we are done with current class so add it
                    all_classes.append(class_text)
                class_text = ClassText(r, fstem)
            else:
                if not done_header:  # still in header
                    header.append(r.rstrip())
                else:
                    # this may not be needed
                    p = re.compile(r'.*Optional\[Union\[([^,]+),.*List\[Any\]')
                    refs = p.findall(r)
                    if len(refs) == 1:
                        print(f'Replaced Any with {refs[0]} in {fstem}')
                        r_orig = r
                        r = r.replace('List[Any]', f'List[{refs[0]}]')
                        print(f'{r_orig} -> {r}')
                    class_text.add_line(r.rstrip())

    all_classes.append(class_text)  # don't forget final class

    # force all oscal versions to the current one
    all_classes = constrain_oscal_version(all_classes)

    return all_classes


def find_unique_classes():
    """Load all oscal files and find unique classes."""
    all_classes = []
    for fstem in fstems:
        all_classes.extend(load_classes(fstem))
    unique_classes = []
    for a in all_classes:
        if a.name == 'Model':
            continue
        is_unique = True
        for i, u in enumerate(unique_classes):
            if a.lines == u.lines:
                is_unique = False
                break
        if is_unique:
            unique_classes.append(a)
        else:
            unique_classes[i].parent_names.append(a.parent_names[0])
    return unique_classes


def strip_prefixes(classes):
    """Strip prefixes from class names."""
    prefixes = [
        'OscalMetadata',
        'OscalAssessmentCommon',
        'OscalImplementationCommon',
        'OscalComponentDefinition',
        'OscalCatalog',
        'OscalSsp',
        'OscalPoam',
        'OscalProfile',
        'OscalAr',
        'OscalAp',
        'Common'
    ]
    new_classes = []
    for c in classes:
        for prefix in prefixes:
            c.strip_prefix(prefix)
        new_classes.append(c)
    return new_classes


def make_special_name_changes(classes):
    """Make known special case changes."""
    new_classes = []
    changes = {
        'OscalImplementationCommonImplementationStatus': 'Ssp_ImplementationStatus',
        'OscalSspStatus': 'Ssp_SystemCharacteristicsStatus',
        'Status': 'Ssp_SystemComponentStatus'
    }
    for c in classes:
        if 'ssp' in c.parent_names and c.name in changes:
            c.name = changes[c.name]
        new_classes.append(c)
    return new_classes


def fix_clashes(classes):
    """Fix clashes in names."""
    lookup = {
        'assessment_plan': 'Ap',
        'assessment_results': 'Ar',
        'catalog': 'Cat',
        'component': 'Comp',
        'poam': 'Poam',
        'profile': 'Prof',
        'ssp': 'Ssp'
    }
    nclasses = len(classes)
    changes = []
    for i in range(nclasses):
        for j in range(i + 1, nclasses):
            if classes[i].name == classes[j].name:
                a = classes[i]
                b = classes[j]
                a_parents = a.parent_names
                b_parents = b.parent_names
                for a_parent in a_parents:
                    for b_parent in b_parents:
                        a_pre = lookup[a_parent]
                        a_new = a.name if a.name.startswith(a_pre) else a_pre + '_' + a.name
                        b_pre = lookup[b_parent]
                        b_new = b.name if b.name.startswith(b_pre) else b_pre + '_' + b.name
                        if a.name != a_new:
                            changes.append((a_parent, a.name, a_new))
                        if b.name != b_new:
                            changes.append((b_parent, b.name, b_new))

    # now make the actual class name changes
    new_classes = []
    for c in classes:
        for change in changes:
            for parent_name in c.parent_names:
                if parent_name == change[0] and c.name == change[1]:
                    c.name = change[2]
                    # this will need to be present in all parent classes
                    c.is_local = True
                    break
        new_classes.append(c)
    return new_classes


def check_ok(classes):
    """Confirm no name or content matches across classes."""
    nclasses = len(classes)
    for i in range(nclasses):
        for j in range(i + 1, nclasses):
            if classes[i].name == classes[j].name:
                print(f'Name clash with {classes[i].name}')
                return False
            if classes[i].lines == classes[j].lines:
                print(f'Body clash of {classes[i].name} with {classes[j].name}')
                return False
    return True


def find_str(classes, s):
    """Find string somewhere in class text."""
    for i, c in enumerate(classes):
        for line in c.lines:
            if s in line:
                return i
    return -1


def token_in_line(line, token):
    """Find if token is present in string."""
    pattern = r'(^|[^a-zA-Z_]+)' + token + r'($|[^a-zA-Z_]+)'
    p = re.compile(pattern)
    hits = p.findall(line)
    return len(hits) > 0


def replace_token(line, str1, str2):
    """Replace token str1 with new str2 in line."""
    # pull out what you want to keep on left and right
    # rather than capture what you want and replace it
    if str1 not in line:
        return line
    pattern = r'(^|.*[^a-zA-Z_]+)' + str1 + r'($|[^a-zA-Z0-9_]+.*)'
    line = re.sub(pattern, r'\1' + str2 + r'\2', line)
    return line


def is_common(cls):
    if '_' in cls.name:
        return False
    if len(cls.parent_names) == 1:
        return False
    return True


def refine_split(com, file_classes):
    """Make sure no references in common link to the other files."""
    # get list of original names in current common file
    common_names = []
    for c in com:
        common_names.append(c.orig_name)

    # find all original names of classes in other files that shouldn't be refd by common
    names = set()
    for stem in fstems:
        for c in file_classes[stem]:
            if (c.is_local) or (c.orig_name not in common_names):
                names.add(c.orig_name)
    names = list(names)

    # if any common classes references outside common - exclude it from common
    not_com = []
    for c in com:
        excluded = False
        for line in c.lines:
            if excluded:
                break
            if '"' not in line and "'" not in line:
                for name in names:
                    if token_in_line(line, name):
                        not_com.append(c.name)
                        excluded = True
                        break

    # remove all not_com from com and add to other files as needed by parents
    new_com = []
    for c in com:
        if c.name in not_com:
            for parent in c.parent_names:
                file_classes[parent].append(c)
        else:
            new_com.append(c)
    return new_com, file_classes


def find_in_classes(name, com, file_classes):
    found = []
    for c in com:
        if name in c.name:
            found.append(('com', name))
    for stem in fstems:
        for c in file_classes[stem]:
            if name in c.name:
                found.append((stem, name))
    return found
        

def split_classes(classes):
    """Split into separate common and other files."""
    com = []
    file_classes = {}
    for stem in fstems:
        file_classes[stem] = []

    for c in classes:
        if is_common(c):
            com.append(c)
        else:
            c.name = c.name.split('_')[-1]
            for parent in c.parent_names:
                # the class carries with it that it is local and bound to the parent
                file_classes[parent].append(c)

    # keep removing classes in com that have external dependencies until it is clean
    new_ncom = 0
    while new_ncom != len(com):
        new_ncom = len(com)
        com, file_classes = refine_split(com, file_classes)
    return com, file_classes


def reorder_classes(classes):
    """Reorder the classes to minimize needed forwards."""
    new_classes = []
    for c in classes:
        for line in c.lines:
            _ = c.add_all_refs(line)
        new_classes.append(c)
    reordered, forward_refs = reorder(new_classes)
    return reordered, forward_refs


def write_oscal(classes, forward_refs, fstem):
    """Write out oscal.py with all classes in it."""
    with open(f'trestle/oscal/{fstem}.py', 'w', encoding='utf8') as out_file:
        is_common = fstem == 'common'

        out_file.write(license_header)
        out_file.write('\n')
        out_file.write(main_header)

        if not is_common:
            out_file.write('import trestle.oscal.common as common\n')
        out_file.write('\n\n')

        for c in classes:
            out_file.writelines('\n'.join(c.lines) + '\n')

        if not is_common:
            out_file.writelines('class Model(OscalBaseModel):\n')
            alias = alias_map[fstem]
            snake = alias.replace('-', '_')
            class_name = camel_map[fstem]
            if '-' in alias:
                out_file.writelines(f"    {snake}: {class_name} = Field(..., alias='{alias}')\n")
            else:
                out_file.writelines(f'    {snake}: {class_name}\n')

        if forward_refs:
            if not is_common:
                out_file.writelines('\n\n')
            out_file.writelines('\n'.join(forward_refs) + '\n')


def dump_classes_as_python(classes, stem, changes, com_names):
    """Find changes within the names and apply to all refs."""
    # then reorder and dump
    for i, c in enumerate(classes):
        lines = []
        for line in c.lines:
            if 'title=' not in line and 'description=' not in line:
                for item in changes.items():
                    new_name = item[1]
                    # if not in common then need to add common. to common names
                    if stem != 'common' and new_name in com_names:
                        tentative_name = 'common.' + new_name
                        if tentative_name not in line:
                            new_name = tentative_name
                    line = replace_token(line, item[0], new_name)
            lines.append(line)
        classes[i].lines = lines

        # class name may have been replaced by change - so update with new name
        paren = lines[0].find('(')
        class_name = classes[i].name
        if paren > 0:
            class_name = lines[0][len('class '): paren]
        classes[i].name = class_name
    ordered, forward_refs = reorder_classes(classes)
    write_oscal(ordered, forward_refs, stem)


def find_full_changes(com, file_classes):
    ###Find all name changes and what files made them."""
    changes = {}
    com_names = []
    for c in com:
        changes[c.orig_name] = c.name
        com_names.append(c.name)
    for fstem in fstems:
        for c in file_classes[fstem]:
            changes[c.orig_name] = c.name
    return changes, com_names


def kill_min_items(classes):
    for i, c in enumerate(classes):
        for j, line in enumerate(c.lines):
            c.lines[j] = line.replace(', min_items=1', '')
        classes[i] = c
    return classes


if __name__ == '__main__':
    """Main invocation."""
    # find all unique classes
    uc = find_unique_classes()

    # make early substitutions of known special cases
    uc = make_special_name_changes(uc)

    # strip prefixes in names only
    uc = strip_prefixes(uc)

    # find clashes in names and add short prefix to name
    uc = fix_clashes(uc)

    uc = kill_min_items(uc)

    com, file_classes = split_classes(uc)

    changes, com_names = find_full_changes(com, file_classes)

    dump_classes_as_python(com, 'common', changes, com_names)
    for item in file_classes.items():
        dump_classes_as_python(item[1], item[0], changes, com_names)
