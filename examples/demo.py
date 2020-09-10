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
from trestle.oscal.catalog import Catalog, Metadata
from datetime import datetime
from uuid import uuid4

print('> Deliberately fail to make a Catalog properly')

try:
    c = Catalog()
except Exception as e:
    print(e)

print()
print('> Make some Metadata')
m = Metadata(
    **{
        'title': 'my cool catalog',
        'last-modified': datetime.now(),
        'version': '0.0.1',
        'oscal-version': '1.0.0'
    }
)
print(m)

print()
print('> Make a Catalog')
c = Catalog(metadata=m, uuid=str(uuid4()))
print(c)
