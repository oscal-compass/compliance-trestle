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

# Testing of trestle split and merge manually

rm -rf test_trestle
mkdir test_trestle
cd test_trestle
trestle init
trestle import -f path_to_NIST_SP-800-53_rev5_catalog.json -o mycatalog
cd catalogs/mycatalog
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'

trestle merge -e 'catalog.metadata,catalog.groups,catalog.back-matter'
trestle merge -e 'catalog.*'
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'
trestle merge -e 'catalog.*'
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'
cd catalog
trestle split -f ./metadata.json -e 'metadata.roles,metadata.parties,metadata.responsible-parties'
cd metadata
trestle split -f ./roles.json -e 'roles.*'
trestle merge -e 'roles.*'

