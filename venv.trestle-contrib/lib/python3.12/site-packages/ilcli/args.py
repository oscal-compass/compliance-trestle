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

import re


def kv_args_to_dict(arg_list):
    """
    Convert a list of key-value args with the form::

      --key value

    into a dictionary. In case of parsing failure, ``cmd.parser.error``
    will be called, making the program existing with error status.

    :param arg_list: the list of arguments (typically the parameter of
      ``_validate_extra_arguments()``).
    """
    short_arg_list = [a for a in arg_list if re.match(r'^\-[^\-]', a)]
    bad_size = len(arg_list) % 2 == 1
    bad_keys = [
        k for i, k in enumerate(arg_list)
        if k.startswith('--') and i % 2 == 1
    ]
    bad_vals = [
        k for i, k in enumerate(arg_list)
        if not k.startswith('--') and i % 2 == 0
    ]
    if short_arg_list or bad_size or bad_keys or bad_vals:
        raise ValueError(
            "bad extra arguments. Pairs of '--key value' are expected. "
            "Got: {}".format(' '.join(arg_list))
        )
    extra_arg_list = [a.lstrip('-') for a in arg_list if a.startswith('--')]
    extra_values = [a for a in arg_list if not a.startswith('--')]
    return dict(zip(extra_arg_list, extra_values))
