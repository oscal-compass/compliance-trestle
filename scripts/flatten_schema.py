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
"""Script to remove references in json schema to simplify work done by datamodel-generator."""
import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class FlattenSchema():
    """Flatten the schema by resolving references as much as possible."""

    _ref_str = '$ref'
    _refd = set()
    _def_list = []

    def _find_ref(self, name):
        """Find the full definition of the given reference name from the list of definitions."""
        for (key, value) in self._def_list:
            if key == name:
                return value
        raise AssertionError()

    @staticmethod
    def _get_ref_name(s):
        """Extract the name from the ref definition value."""
        pref_string = '#/definitions/'
        assert s.find(pref_string) == 0
        return s[len(pref_string):]

    def _replace_ref(self, d, ref_set):
        """Input is known to be ref: /definitions/bar so just return replacement def from def_list."""
        ref_name = FlattenSchema._get_ref_name(d[self._ref_str])
        if ref_name in ref_set:  # name is already on the stack so stop now and don't recurse
            return d, ref_set, False
        # this is a new reference so return the body of the definition and add its name as a reference
        self._refd.add(ref_name)
        ref_set.add(ref_name)
        return self._find_ref(ref_name), ref_set, True

    def _replace_refs(self, obj, ref_set):
        """Given an object recurse into it replacing any found ref: defs with what is in def_list."""
        if type(obj) == dict:
            # first check if it is a simple $ref line and replace it directly
            if len(obj.items()) == 1 and obj.get(self._ref_str, None) is not None:
                return self._replace_ref(obj, ref_set)
            new_dict = {}
            dirty = False
            for key, val in obj.items():
                if key in ref_set:
                    new_dict[key] = val
                else:
                    ref_set.add(key)
                    new_dict[key], ref_set, changed = self._replace_refs(val, ref_set)
                    if changed:
                        dirty = True
            return new_dict, ref_set, dirty
        elif type(obj) == str:
            return obj, ref_set, False
        elif type(obj) == list:
            n_list = len(obj)
            changed = False
            dirty = False
            for i in range(n_list):
                obj[i], ref_set, changed = self._replace_refs(obj[i], ref_set)
                if changed:
                    dirty = True
            return obj, ref_set, dirty
        elif type(obj) == tuple:
            new_val, ref_set, changed = self._replace_refs(obj[1], ref_set)
            return (obj[0], new_val), ref_set, changed
        if hasattr(obj, '__iter__'):
            logger.info('missed iterable type: ', type(obj))
        return obj, ref_set, False

    def _replace_schema_refs(self, schema):
        """Expand each definition with repeated iterations over the list with recursion into each."""
        self._def_list = list(schema['definitions'].items())
        n_defs = len(self._def_list)
        fixed = [False] * n_defs
        dirty = True
        while dirty:
            dirty = False
            for i in range(n_defs):
                changed = False
                if not fixed[i]:
                    self._def_list[i], _, changed = self._replace_refs(self._def_list[i], {self._def_list[i][0]})
                    if not changed:  # mark it fixed and don't revisit
                        fixed[i] = True
            if changed:
                dirty = True
        new_dict = {}
        for tup in self._def_list:
            new_dict[tup[0]] = tup[1]
        schema['definitions'] = new_dict
        return schema

    def replace_refs(self, schema_file_name, output_file_name):
        """Replace all refs in schema file name and output with refs removed except for cyclic ones."""
        with open(schema_file_name) as f:
            schema = json.load(f)

        flat_schema = self._replace_schema_refs(schema)

        tmp_name = output_file_name + '.tmp'
        with open(tmp_name, 'w') as f:
            json.dump(flat_schema, f, indent=4)

        needed_refs = set()
        ref_str = '"$ref": "#/definitions/'
        with open(tmp_name, 'r') as fin:
            for line in fin.readlines():
                nref = line.find(ref_str)
                if nref >= 0:
                    new_ref = line[(nref + len(ref_str)):].strip()
                    needed_refs.add(new_ref)

        out_lines = []
        with open(tmp_name, 'r') as fin:
            for line in fin.readlines():
                skipit = False
                if line.find('"$id": "#/definitions/') >= 0:
                    skipit = True
                    for cname in needed_refs:
                        # skip any definitions
                        if line.find(f'"$id": "#/definitions/{cname}') >= 0:
                            skipit = False
                            break
                if not skipit:
                    out_lines.append(line)

        with open(output_file_name, 'w') as fout:
            fout.writelines(out_lines)

        os.remove(tmp_name)
