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

import logging
import sys
import timeit
from pathlib import Path

from trestle.core.base_model import OscalBaseModel
from trestle.transforms.transformer_singleton import transformer_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
with_json_ser = True


def tanium_wrapper(data: str) -> str:
    """Convert input tanium data (in string format) to OSCAL result (json serlaized as string)."""
    # process
    tanium_tf = transformer_factory.get('tanium')
    output_oscal = tanium_tf.transform(data)
    json_str = output_oscal.oscal_serialize_json()
    return json_str


def tanium_wrapper_oscal(data: str) -> OscalBaseModel:
    """Convert input tanium data (in string format) to OSCAL result."""
    # process
    tanium_tf = transformer_factory.get('tanium')
    output_oscal = tanium_tf.transform(data)
    return output_oscal


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

    for n in range(num_exp):
        logger.info('*****Experiment: ' + str(n + 1) + ', Num input records: ' + str(records * (n + 1)))
        data = orig_data * (n + 1)  # with json ser and deser

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
    input_file = 'tests/data/tasks/tanium/benchmark/Tanium-comply-nist-results.txt'
    outout_file = ''
    sys.exit(main(input_file, outout_file))
