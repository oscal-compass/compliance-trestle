# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Basic script to show the use of the transformer factory."""

import logging
import pathlib

from trestle.core import const
from trestle.transforms.transformer_singleton import transformer_factory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

sample_data_f = pathlib.Path('small_sample_tanium.json')

if __name__ == '__main__':
    stringed = sample_data_f.open('r', encoding=const.FILE_ENCODING).read()
    tanium_tf = transformer_factory.get('tanium')
    output_oscal = tanium_tf.transform(stringed)
    json_str = output_oscal.oscal_serialize_json()
    logger.info(json_str)
