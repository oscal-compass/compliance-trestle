"""Elaborate script to fix Any's in bad files created by version 0.5.28 datamodel-code-generator."""

# This relies on datamodel-codegen 0.5.28 to create classes that work,
#   but don't do much checking.
# This is because the generated classes rely on Any - which does no checking.
# This script changes the Any's appropriately from the plural form of the needed
#   class to the singular form, with a lookup table relied on for special cases.
# It also finds all references in a class to classes it depends on, using regex.
# It then reorders the classes so there are no forwards required.
# The reordering is rigorous and checked by following all referenced classes and their dependencies.
# This script is normally called by gen_oscal.py when models are generated

import re

pattern1 = 'ies: Optional[Dict[str, Any]]'
pattern2 = 's: Optional[Dict[str, Any]]'
special_lut = {'ParameterSetting': 'SetParameter'}
# Class names with this substring are due to confusion in oscal that will go away.
# For now delete the classes and convert the corresponding unions to conlist
singleton_name = 'GroupItem'
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

    def __init__(self, first_line):
        """Construct with first line of class definition."""
        self.lines = [first_line.rstrip()]
        n = first_line.find('(')
        self.name = first_line[len(class_header):n]
        self.refs = set()
        self.full_refs = set()
        self.found_all_links = False

    def add_line(self, line):
        """Add new line to class text."""
        self.lines.append(line)

    def add_ref_if_good(self, ref_name):
        """Only add refs if the name isnt an anomolous singleton type."""
        if ref_name.find(singleton_name) == -1:
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
        p = re.compile(r'\[(?:(.*),\s*)?((?:\[??[^\[]*?))\]')
        self.add_ref_pattern(p, line)

    def get_linked_refs(self, class_text_list, known_refs):
        """Follow all refs to find their refs."""
        if self.name in known_refs:
            return set()
        refs = self.full_refs
        if self.found_all_links:
            return refs
        new_refs = refs.copy()
        for r in refs:
            i = ClassText.find_index(class_text_list, r)
            new_refs = new_refs.union(class_text_list[i].get_linked_refs(class_text_list, refs))
        self.found_all_links = True
        return new_refs

    def find_direct_refs(self, class_names_list):
        """Find direct refs without recursion."""
        for ref in self.refs:
            if ref in class_names_list:
                self.full_refs.add(ref)
        if len(self.full_refs) == 0:
            self.found_all_links = True

    def find_full_refs(self, class_text_list):
        """Find full refs with recursion."""
        sub_refs = set()
        for ref in self.full_refs:
            # find the class named ref
            i = ClassText.find_index(class_text_list, ref)
            # accumulate all references associated with each ref in that class
            sub_refs = sub_refs.union(class_text_list[i].get_linked_refs(class_text_list, sub_refs))
        return self.full_refs.union(sub_refs)

    def find_order(self, class_text_list):
        """Find latest dep and earliest reference."""
        ro = RelOrder(len(class_text_list) - 1)
        # find first class that needs this class
        for i, ct in enumerate(class_text_list):
            if self.name in ct.full_refs:
                ro.earliest_ref = i
                break
        # find last class this one needs
        for ref in self.full_refs:
            n = ClassText.find_index(class_text_list, ref)
            if n > ro.latest_dep:
                ro.latest_dep = n
        return ro


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

    # find full references for each class in list with recursion on each ref
    for n, c in enumerate(class_list):
        c.full_refs = c.find_full_refs(class_list)
        class_list[n] = c

    # with full dependency info, now reorder the classes to remove forward refs
    did_swap = True
    while did_swap:
        did_swap = False
        # find the relative placement of each class in list to its references and dependencies
        orders = []
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

    # return reordered list of classes with no forward refs
    return class_list


def get_cap_stem(s, clip):
    """Extract stem part of plural form from first word on line."""
    n = 0
    while s[n] == ' ':
        n += 1
    cap = s[n].upper()
    n += 1
    while s[n + clip] != ':':
        if s[n] == '_':
            cap += s[n + 1].upper()
            n += 2
            continue
        cap += s[n]
        n += 1
    return cap


def fix_header(header, needs_conlist):
    """Fix imports and remove timestamp from header."""
    new_header = []
    for r in header:
        # block import of Any - should not be needed
        r = re.sub(' Any, ', ' ', r)
        if r.find(' timestamp: ') >= 0:
            continue
        if needs_conlist:
            # add import of conlist for Union[A, A] case
            r = re.sub(r'^(from\s+pydantic\s+import.*)$', r'\1, conlist', r)
        new_header.append(r)
    return new_header


def fix_file(fname):
    """Fix the Anys in this file and reorder to avoid forward dependencies."""
    all_classes = []
    header = []

    class_text = None
    done_header = False
    needs_conlist = False

    # Find Any's and replace with appropriate singular class
    # Otherwise accumulate all class dependencies for reordering with no forward refs
    with open(fname, 'r') as infile:
        for r in infile.readlines():
            if r.find(class_header) == 0:  # start of new class
                done_header = True
                if class_text is not None:  # we are done with current class so add it
                    # prevent anomalous singletons from appearing in output
                    if class_text.name.find(singleton_name) == -1:
                        all_classes.append(class_text)
                class_text = ClassText(r)
            else:
                if not done_header:  # still in header
                    header.append(r.rstrip())
                else:  # in body of class looking for Any's
                    # first delete any singleton substrings if present
                    r = r.replace(singleton_name, '')
                    n1 = r.find(pattern1)
                    n2 = r.find(pattern2)
                    if n1 != -1:  # ies plural
                        tail = r[(n1 + len(pattern1)):]
                        cap_singular = get_cap_stem(r, 3) + 'y'
                        class_text.add_ref_if_good(cap_singular)
                        r = r[:(n1 + len(pattern1) - 5)] + cap_singular + ']]' + tail
                    elif n2 != -1:  # s plural
                        tail = r[(n2 + len(pattern2)):]
                        cap_singular = get_cap_stem(r, 1)
                        if cap_singular in special_lut:
                            cap_singular = special_lut[cap_singular]
                        class_text.add_ref_if_good(cap_singular)
                        r = r[:(n2 + len(pattern2) - 5)] + cap_singular + ']]' + tail
                    else:
                        # for a line that has no Any's, use regex to find referenced class names
                        class_text.add_all_refs(r)
                    # fix any line containing Union[A, A] to Union[A, conlist(A, min_items=2)]
                    # this may now include Unions that previously involved the anomalous singletons
                    r = re.sub(r'Union\[([^,]*),\s*\1\]', r'Union[\1, conlist(\1, min_items=2)]', r)
                    if r.find(', conlist(') >= 0:
                        needs_conlist = True
                    # mark regex strings as raw
                    r = re.sub(r"(\s*regex\s*=\s*)\'(.*)", r"\1r'\2", r)
                    class_text.add_line(r.rstrip())

    all_classes.append(class_text)  # don't forget final class

    # reorder the classes to remove forward references
    all_classes = reorder(all_classes)

    header = fix_header(header, needs_conlist)

    # write the classes out in the fixed order
    with open(fname, 'w') as out_file:
        out_file.write('# modified by fix_any.py\n')
        out_file.write(license_header)
        out_file.writelines('\n'.join(header) + '\n')
        for c in all_classes:
            out_file.writelines('\n'.join(c.lines) + '\n')
