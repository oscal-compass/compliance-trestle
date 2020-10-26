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
"""Common logging utilities."""
import logging

# Singleton logger instance
# All other CLI sub module will inherit settings of this logger as long as
# sub-module instantiates a logger with a prefix 'trestle' or __name__
_logger = logging.getLogger('trestle')


def init(level: int = logging.DEBUG) -> logging.Logger:
    """Initialize the logger."""
    # create logger
    _logger.setLevel(level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s %(name)s:%(lineno)d %(levelname)s: %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    _logger.addHandler(ch)

    return _logger


def set_level(level: int = logging.DEBUG) -> logging.Logger:
    """Set log level."""
    _logger.setLevel(level)
    return _logger


def get_logger(level: int = logging.DEBUG) -> logging.Logger:
    """Get the trestle default logger."""
    return set_level(level)
