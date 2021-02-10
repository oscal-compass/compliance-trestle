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
"""Trestle settings functionality."""

from typing import Dict, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings class."""

    tmp_dir: str = './tmp'
    GITHUB_TOKENS: Optional[Dict[str, str]] = {}

    class Config:
        """Loads the dotenv file."""

        env_file: str = '.env'
        env_file_encoding: str = 'utf-8'
        env_prefix: str = 'TRESTLE_'
