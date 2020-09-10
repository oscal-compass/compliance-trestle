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
"""Tests for models util module."""

import pathlib

import trestle.core.parser as parser
import trestle.core.utils as mutils
import trestle.oscal.catalog as catalog


def load_good_catalog():
    """Load nist 800-53 as a catalog example."""
    good_sample_path = pathlib.Path('nist-source/content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')

    assert (good_sample_path.exists())
    return parser.wrap_for_input(catalog.Catalog).parse_file(good_sample_path).catalog


def test_get_elements():
    """Test getting flat list of elements."""
    good_sample = load_good_catalog()

    mdlist = mutils.get_elements_of_model_type(good_sample, catalog.Metadata)
    assert (type(mdlist) == list)
    # can only be 1 metadata
    assert (len(mdlist) == 1)
    assert (type(mdlist[0]) == catalog.Metadata)

    control_list = mutils.get_elements_of_model_type(good_sample, catalog.Control)
    assert (len(control_list) >= 1)
    group_list = mutils.get_elements_of_model_type(good_sample, catalog.Group)
    assert (len(group_list) >= 2)
