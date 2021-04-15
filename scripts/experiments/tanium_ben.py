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
"""Script to benchmark tanium to OSCAL conversion."""

import io
import json
import logging
import sys
import timeit
from pathlib import Path

from trestle.oscal.assessment_results import Result
from trestle.utils import tanium

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
with_json_ser = True


def tanium_wrapper(data: str) -> str:
    """Convert input tanium data (in string format) to OSCAL result (json serlaized as string)."""
    # process
    results_mgr = tanium.ResultsMgr()
    stream = io.StringIO(data)
    line = stream.readline()
    while line:
        jdata = json.loads(line.strip())
        results_mgr.ingest(jdata)
        line = stream.readline()
    json_str = results_mgr.json
    return json_str


def tanium_wrapper_oscal(data: list) -> Result:
    """Convert input tanium data (in json format) to OSCAL result."""
    # process
    results_mgr = tanium.ResultsMgr()
    for line in data:
        results_mgr.ingest(line)

    return results_mgr.result


def read_file(in_file: str):
    """Read input file."""
    file_path = Path(in_file)
    data = []
    count = 0
    with open(file_path) as fp:
        for line in fp:
            data.append(line)
            count = count + 1
    return ''.join(data), count


def main(in_file: str, out_file: str):
    """Run the experiment."""
    logger.info('Reading input file...')
    orig_data, records = read_file(in_file)
    logger.info('Starting experiments...')
    num_exp = 10
    logger.info('Num experiments with different input file sizes: ' + str(num_exp))
    num_iter = 10
    repeat = 3
    logger.info('Num Iter per exp: ' + str(num_iter) + ', Repeat: ' + str(repeat))

    # create json array for input
    json_data = []
    stream = io.StringIO(orig_data)
    line = stream.readline()
    while line:
        jdata = json.loads(line.strip())
        json_data.append(jdata)
        line = stream.readline()

    for n in range(num_exp):
        logger.info('*****Experiment: ' + str(n + 1) + ', Num input records: ' + str(records * (n + 1)))
        if with_json_ser:
            data = orig_data * (n + 1)  # with json ser and deser
        else:
            data = json_data * (n + 1)  # without json ser and deser

        total_time = 0
        for _i in range(repeat):
            start = timeit.default_timer()
            for _j in range(num_iter):
                if with_json_ser:
                    tanium_wrapper(data)  # with json ser and deser
                else:
                    tanium_wrapper_oscal(data)  # without json ser and deser

            end = timeit.default_timer()
            delta = end - start
            time_per_iter = delta / num_iter
            total_time = total_time + time_per_iter
            logger.info('Total time: ' + str(delta) + ', Per iteration time: ' + str(time_per_iter))
        avg = total_time / repeat
        logger.info('Avg time per iter: ' + str(avg))

    logger.info('Done.')


if __name__ == '__main__':
    input_file = 'tests/data/tasks/tanium/input/Tanium.comply-nist-results'
    outout_file = ''
    sys.exit(main(input_file, outout_file))
