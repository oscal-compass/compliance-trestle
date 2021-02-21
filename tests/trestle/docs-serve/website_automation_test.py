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
import subprocess
import time


def _ensure_not_running() -> None:
    """Ensure test website not running."""
    response = None
    try:
        connection = http.client.HTTPConnection('localhost', 8000, timeout=60)
        connection.request('GET', '/')
        response = connection.getresponse()
    except Exception:
        pass
    if response is not None:
        raise Exception('mkdocs server running')


def test_website_automation(tmpdir) -> None:
    """Test website boot and usability."""
    _ensure_not_running()
    try:
        # launch webserver
        p = subprocess.Popen(['mkdocs', 'serve'])
        # try connect to and fetch data from webserver
        retrys_max = 90
        retrys = 0
        while retrys < retrys_max:
            retrys += 1
            try:
                connection = http.client.HTTPConnection('localhost', 8000, timeout=60)
                connection.request('GET', '/')
                response = connection.getresponse()
                break
            except Exception as e:
                if retrys >= retrys_max:
                    raise e
                time.sleep(1)
        # assure expected response
        if response.status != 200:
            raise Exception(f'status: {response.status}')
        if response.reason != 'OK':
            raise Exception(f'reason: {response.reason}')
        body = response.read().decode('utf-8')
        if '<meta name="description" content="Documentation for compliance-trestle package.">' not in body:
            raise Exception(f'body: {body}')
    # stop webserver
    finally:
        p.terminate()
        p.wait()
        _ensure_not_running()
