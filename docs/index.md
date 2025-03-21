---
title: Overview
description: Trestle is an ensemble of tools that enable the creation, validation, and governance of documentation artifacts for compliance needs
---

# Compliance-trestle (also known as `trestle`)

![[OS Compatibility](#prerequisites)](https://img.shields.io/badge/platform-osx%20%7C%20linux%20%7C%20windows-orange.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compliance-trestle)
![[Pre-commit](https://github.com/pre-commit/pre-commit)](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![[Code Coverage](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=coverage)
![[Quality gate](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=alert_status)
![[Pypi](https://pypi.org/project/compliance-trestle/)](https://img.shields.io/pypi/dm/compliance-trestle)
![GitHub Actions status](https://github.com/oscal-compass/compliance-trestle/actions/workflows/python-test.yml/badge.svg?branch=develop)
![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9408/badge)

Trestle is an ensemble of tools that enable the creation, validation, and governance of documentation artifacts for compliance needs. It leverages NIST's [OSCAL](https://pages.nist.gov/OSCAL/documentation/) as a standard data format for interchange between tools and people, and provides an opinionated approach to OSCAL adoption.

Trestle is designed to operate as a CICD pipeline running on top of compliance artifacts in `git`, to provide transparency for the state of compliance across multiple stakeholders in an environment friendly to developers. Trestle passes the generated artifacts on to tools that orchestrate the enforcement, measurement, and reporting of compliance.

It also provides tooling to manage OSCAL documents in a more human-friendly manner. By splitting large OSCAL data structures into smaller and easier to edit sub-structures, creation and maintenance of these artifacts can follow normal `git` workflows including peer review via pull request, versioning, releases/tagging.

Trestle provides three separate but related functions in the compliance space:

- Manage OSCAL documents to allow editing and manipulation while making sure the schemas are enforced
- Transform documents from other formats to OSCAL
- Provide support and governance to author compliance content as markdown and drawio.

Trestle provides tooling to help orchestrate the compliance process across a number of dimensions:

- Help manage OSCAL documents in a more human-friendly manner by expanding the large OSCAL data structures into smaller and easier to edit sub-structures while making sure the schemas are enforced.
- Transform documents from other formats to OSCAL
- Provide governance for markdown documents and enforce consistency of format and content based on specified templates
- Tooling manage authoring and governance of markdown and drawio files withn a repository.
- Support within trestle to streamline management within a managed git environment.
- An underlying object model that supports developers interacting with OSCAL artefacts.

## Important Note:

The current version of trestle 3.x supports NIST OSCAL 1.1.2.
Below shows trestle versions correspondence with OSCAL versions:

```
trestle 3.x => OSCAL 1.1.2
trestle 2.x => OSCAL 1.0.4
trestle 1.x => OSCAL 1.0.2
trestle 0.37.x => OSCAL 1.0.0
```

Visit [pypi](https://pypi.org/project/compliance-trestle/#history) for trestle release history and downloads.

## Notes for install of current and older versions of trestle

#### Install of trestle 3.x

Use python 3.11.

```
python3.11 -m venv venv.trestle
source venv.trestle/bin/activate
pip install compliance-trestle==3.6.0
trestle version
Trestle version v3.6.0 based on OSCAL version 1.1.2
```

#### Install of trestle 2.x

Use python 3.9.

```
python3.9 -m venv venv.trestle
source venv.trestle/bin/activate
pip install compliance-trestle==2.6.0
trestle version
Trestle version v2.6.0 based on OSCAL version 1.0.4
```

#### Install of trestle 1.x

Use python 3.9.

Due to dependency updates since the release of trestle 1.2.0, perform the following in your venv:

```
python3.9 -m venv venv.trestle
source venv.trestle/bin/activate
pip install compliance-trestle==1.2.0
pip uninstall pydantic
pip uninstall pydantic_core
pip install pydantic==1.10.2
pip install requests
trestle version
Trestle version v1.2.0 based on OSCAL version 1.0.2
```

## Why Trestle

Compliance suffers from being a complex topic that is hard to articulate simply. It involves complete and accurate execution of multiple procedures across many disciplines (e.g. IT, HR, management) with periodic verification and audit of those procedures against controls.

While it is possible to manage the description of controls and how an organisation implements them in ad hoc ways with general tools (spreadsheets, documents), this is hard to maintain for multiple accreditations and, in the IT domain at least, creates a barrier between the compliance efforts and the people doing daily work (DevOps staff).

Trestle aims to reduce or remove this barrier by bringing the maintenance of control descriptions into the DevOps domain. The goal is to have changes to the system (for example, updates to configuration management) easily related to the controls impacted, and to enable modification of those controls as required in concert with the system changes.

Trestle implicitly provides a core opinionated workflow driven by its pipeline to allow standardized interlocks with other compliance tooling platforms.

## Machine readable compliance format

Compliance activities at scale, whether size of estate or number of accreditations, require automation to be successful and repeatable. OSCAL as a standard allows teams to bridge between the "Governance" layer and operational tools.

By building human managed artifacts into OSCAL, Trestle is not only able to validate the integrity of the artifacts that people generate - it also enables reuse and sharing of artifacts, and furthermore can provide suitable input into tools that automate operational compliance.

## Supported OSCAL elements and extensions

`trestle` implicitly supports all OSCAL schemas for use within the object model. The development roadmap for `trestle` includes adding workflow around specific elements / objects that is opinionated.

## Supported file formats for OSCAL objects.

OSCAL supports `xml`, `json` and `yaml` with their [metaschema](https://github.com/usnistgov/metaschema) tooling. Trestle
natively supports only `json` and `yaml` formats at this time.

Future roadmap anticipates that support for xml [import](https://github.com/oscal-compass/compliance-trestle/issues/177) and [upstream references](https://github.com/oscal-compass/compliance-trestle/issues/178) will be enabled. However, it is expected
that full support will remain only for `json` and  `yaml`.

Users needing to import XML OSCAL artifacts are recommended to look at NIST's OSCAL converters page [here](https://github.com/usnistgov/OSCAL/blob/main/build/README.md#converters).

## Python codebase, easy installation via pip

Trestle runs on most all python platforms (e.g. Linux, Mac, Windows) and is available on PyPi so it is easily installed via pip.  It is under active development and new releases are made available regularly.

## Development status

Compliance trestle is currently stable and is based on NIST OSCAL version 1.1.2, with active development continuing.

## Contributing to Trestle

Our project welcomes external contributions. Please consult [contributing](contributing/index.md) to get started.

## License & Authors

If you would like to see the detailed LICENSE click [here](license.md).
Consult [contributors](https://github.com/oscal-compass/compliance-trestle/graphs/contributors) for a list of authors and [maintainers](contributing/maintainers.md) for the core team.

```text
# Copyright (c) 2024 The OSCAL Compass Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

______________________________________________________________________

We are a Cloud Native Computing Foundation sandbox project.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://www.cncf.io/wp-content/uploads/2022/07/cncf-white-logo.svg">
  <img src="https://www.cncf.io/wp-content/uploads/2022/07/cncf-color-bg.svg" width=300 />
</picture>

The Linux Foundation® (TLF) has registered trademarks and uses trademarks. For a list of TLF trademarks, see [Trademark Usage](https://www.linuxfoundation.org/legal/trademark-usage)".

*Trestle was originally created by IBM.*
