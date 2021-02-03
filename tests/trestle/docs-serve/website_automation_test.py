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
"""website automation tests."""

import http.client
import multiprocessing
import time

from click.testing import CliRunner

from mkdocs import __main__ as cli

def _webserver():
    CliRunner().invoke(cli.cli, ["serve"], catch_exceptions=False)
    
def test_website_automation(tmpdir):
    p = multiprocessing.Process(target=_webserver)
    p.start()
    try:
        retrys_max = 90
        retrys = 0
        while retrys < retrys_max:
            retrys += 1
            try:
                connection = http.client.HTTPConnection('localhost', 8000, timeout=60)
                connection.request("GET", "/")
                response = connection.getresponse()
                break
            except Exception as e:
                if retrys >= retrys_max:
                    raise e
                time.sleep(1)
        if response.status != 200:
            raise Exception(f'status: {response.status}')
        if response.reason != 'OK':
            raise Exception(f'reason: {response.reason}')
        body = response.read().decode("utf-8") 
        if '<meta name="description" content="Documentation for compliance-trestle package.">' not in body:
            raise Exception(f'body: {body}')
    finally:
        p.terminate()
    