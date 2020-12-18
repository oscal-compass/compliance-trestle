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
import os


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

    def _replace_ref(self, d, ref_root):
        """Input is known to be ref: /definitions/bar so just return replacement def from def_list."""
        ref_name = FlattenSchema._get_ref_name(d[self._ref_str])
        if ref_name == ref_root or ref_name == 'part':  # part needs special handling for catalog and ssp
            return d, False
        self._refd.add(ref_name)
        return self._find_ref(ref_name), True

    def _replace_refs(self, obj, ref_root):
        """Given an object recurse into it replacing any found ref: defs with what is in def_list."""
        if type(obj) == dict:
            if len(obj.items()) == 1 and obj.get(self._ref_str, None) is not None:
                return self._replace_ref(obj, ref_root)
            new_dict = {}
            dirty = False
            for key, val in obj.items():
                new_dict[key], changed = self._replace_refs(val, ref_root)
                if changed:
                    dirty = True
            return new_dict, dirty
        elif type(obj) == str:
            return obj, False
        elif type(obj) == list:
            n_list = len(obj)
            changed = False
            dirty = False
            for i in range(n_list):
                obj[i], changed = self._replace_refs(obj[i], ref_root)
                if changed:
                    dirty = True
            return obj, dirty
        elif type(obj) == tuple:
            new_val, changed = self._replace_refs(obj[1], ref_root)
            if changed:
                return (obj[0], new_val), True
        return obj, False

    def _replace_schema_refs(self, schema):
        self._def_list = list(schema['definitions'].items())
        n_defs = len(self._def_list)
        dirty = True
        while dirty:
            dirty = False
            for i in range(n_defs):
                self._def_list[i], changed = self._replace_refs(self._def_list[i], self._def_list[i][0])
            if changed:
                dirty = True
        new_dict = {}
        for tup in self._def_list:
            if tup[0] not in self._refd:
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

        out_lines = []
        with open(tmp_name, 'r') as fin:
            for line in fin.readlines():
                skipit = False
                if line.find('#/definitions/') >= 0:
                    for cname in self._refd:
                        if line.find(f'#/definitions/{cname}') >= 0:
                            skipit = True
                            break
                if not skipit:
                    out_lines.append(line)

        with open(output_file_name, 'w') as fout:
            fout.writelines(out_lines)

        os.remove(tmp_name)
