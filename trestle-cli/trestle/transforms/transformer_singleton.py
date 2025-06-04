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
"""Create the singleton transformer factory here."""

from trestle.transforms.implementations.osco import OscalProfileToOscoProfileTransformer
from trestle.transforms.implementations.osco import OscoResultToOscalARTransformer
from trestle.transforms.implementations.tanium import TaniumResultToOscalARTransformer
from trestle.transforms.transformer_factory import TransformerFactory

transformer_factory = TransformerFactory()

# results
transformer_factory.register_transformer('osco', OscoResultToOscalARTransformer)
transformer_factory.register_transformer('tanium', TaniumResultToOscalARTransformer)
# profiles
transformer_factory.register_transformer('oscal-profile-to-osco-profile', OscalProfileToOscoProfileTransformer)
