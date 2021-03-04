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
Script to allow comparison of files before and after applying fix_any.py.

Load every class in a file as lines of text and output them sorted by class name.
This allows a standard diff to reveal changes in class content without regard to order.
Missing classes are also revealed.
"""
import operator
import sys

from fix_any import ClassText

all_classes = []
header = []
forward_refs = []
class_header = 'class '
class_text = None
done_header = False

if len(sys.argv) < 2:
    exit()

fname = sys.argv[1]
with open(fname, 'r') as infile:
    for r in infile.readlines():
        if r.find('.update_forward_refs()') >= 0:
            forward_refs.append(r)
        elif r.find(class_header) == 0:  # start of new class
            done_header = True
            if class_text is not None:  # we are done with current class so add it
                all_classes.append(class_text)
            class_text = ClassText(r)
        else:
            if not done_header:  # still in header
                header.append(r.rstrip())
            else:
                class_text.add_line(r.rstrip())

all_classes.append(class_text)  # don't forget final class

sorted_classes = sorted(all_classes, key=operator.attrgetter('name'))

sorted_forwards = sorted(forward_refs)

outname = fname.replace('.py', '_sorted.py')

with open(outname, 'w') as f:
    for c in sorted_classes:
        f.writelines('\n'.join(c.lines) + '\n')
    f.writelines(sorted_forwards)
