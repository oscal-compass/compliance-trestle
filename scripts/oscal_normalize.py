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
import operator
import pathlib
import re

from trestle.oscal import OSCAL_VERSION_REGEX

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

base64_str = 'Base64'
class_header = 'class '

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
        self.parent_name = parent_name
        self.refs = set()
        self.full_refs = set()
        self.found_all_links = False
        self.is_self_ref = False

    def add_line(self, line):
        """Add new line to class text."""
        self.lines.append(line)

    def add_ref_if_good(self, ref_name):
        """Add non-empty refs."""
        if ref_name:
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


def remove_duplicate_classes(class_list):
    """Remove duplicate classes with name ending 1, 2 etc. and fix all refs to them."""
    replaced_names = {}
    new_list = []
    for c in class_list:
        if c.name == base64_str:
            continue
        if c.name[-1].isdigit():
            base_name = c.name[:-1]
            base_index = ClassText.find_index(class_list, base_name)
            c_base = class_list[base_index]
            if len(c_base.lines) != len(c.lines):
                continue
            different = False
            for i in range(1, len(c_base.lines)):
                if c_base.lines[i] != c.lines[i]:
                    different = True
                    break
            if not different:
                replaced_names[c.name] = c_base.name
    # now have list of duplicate classes that should be culled
    for c in class_list:
        if c.name in replaced_names.keys():
            continue
        new_list.append(c)
    final_list = []
    for c in new_list:
        for i in range(len(c.lines)):
            line = c.lines[i]
            for key, value in replaced_names.items():
                line = line.replace(key, value)
            c.lines[i] = line
        final_list.append(c)
    return final_list


def load_classes(fstem):
    """Load all classes from a file."""
    all_classes = []
    header = []
    forward_refs = []

    class_text = None
    done_header = False

    fname = pathlib.Path('trestle/oscal') / (fstem + '.py')

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
                    # class_text.add_all_refs(r)
                    class_text.add_line(r.rstrip())

    all_classes.append(class_text)  # don't forget final class

    # force all oscal versions to the current one
    all_classes = constrain_oscal_version(all_classes)

    return all_classes

def load_all_files():
    fstems = ['assessment_plan', 'assessment_response', 'catalog', 'component', 'poam', 'profile', 'ssp']
    all_classes = []
    for fstem in fstems:
        all_classes.extend(load_classes(fstem))
    unique_classes = []
    for a in all_classes:
        for u in unique_classes:
            if a.lines == u.lines:
                break
        unique_classes.append(a)

