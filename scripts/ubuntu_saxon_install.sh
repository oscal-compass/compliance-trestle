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


echo 'Installing saxon-C'
echo 'Note this script presumes pythonpath and LD_LIBRARY_PATH are pre-configured.'
echo 'See .github/workflows/python-test.yml'
wget -O /tmp/saxon.zip https://www.saxonica.com/saxon-c/libsaxon-HEC-setup64-v1.2.1.zip \
  && unzip /tmp/saxon.zip -d /tmp \
  && (echo "/opt/saxonica" && cat) | /tmp/libsaxon-HEC-setup64-v1.2.1 \
  && ln -s /opt/saxonica/libsaxonhec.so /usr/lib/libsaxonhec.so \
  && ln -s /opt/saxonica/rt /usr/lib/rt

echo 'Building saxon python bindings'
cd /opt/saxonica/Saxon.C.API/python-saxon \
  && pip install cython \
  && python3 saxon-setup.py build_ext -if

echo 'Done'