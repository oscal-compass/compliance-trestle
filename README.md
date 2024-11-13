# <img alt="Logo" width="50px" src="https://raw.githubusercontent.com/oscal-compass/compliance-trestle/main/images/compliance-trestle-800x800.png" style="vertical-align: middle;" /> Compliance-trestle (also known as `trestle`)

![[OS Compatibility](#prerequisites)](https://img.shields.io/badge/platform-osx%20%7C%20linux%20%7C%20windows-orange.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compliance-trestle)
![[Pre-commit](https://github.com/pre-commit/pre-commit)](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![[Code Coverage](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=coverage)
![[Quality gate](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=alert_status)
![[Pypi](https://pypi.org/project/compliance-trestle/)](https://img.shields.io/pypi/dm/compliance-trestle)
![GitHub Actions status](https://github.com/oscal-compass/compliance-trestle/actions/workflows/python-test.yml/badge.svg?branch=develop)
![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9408/badge)

Trestle is an ensemble of tools that enable the creation, validation, and governance of documentation artifacts for compliance needs. It leverages NIST's [OSCAL](https://pages.nist.gov/OSCAL/) as a standard data format for interchange between tools and people, and provides an opinionated approach to OSCAL adoption.

Trestle is designed to operate as a CICD pipeline running on top of compliance artifacts in `git`, to provide transparency for the state of compliance across multiple stakeholders in an environment friendly to developers. Trestle passes the generated artifacts onto tools that orchestrate the enforcement, measurement, and reporting of compliance.

It also provides tooling to manage OSCAL documents in a more human-friendly manner. By splitting large OSCAL data structures into smaller and easier to edit sub-structures, creation and maintenance of these artifacts can follow normal `git` workflows including peer review via pull request, versioning, releases/tagging.

Trestle provides three separate but related functions in the compliance space:

- Manage OSCAL documents to allow editing and manipulation while making sure the schemas are enforced
- Transform documents from other formats to OSCAL
- Provide support and governance to author compliance content as markdown and drawio.

Trestle provides tooling to help orchestrate the compliance process across a number of dimensions:

- Help manage OSCAL documents in a more human-friendly manner by expanding the large OSCAL data structures into smaller and easier to edit sub-structures while making sure the schemas are enforced.
- Transform documents from other formats to OSCAL
- Provide governance for markdown documents and enforce consistency of format and content based on specified templates
- Tooling manage authoring and governance of markdown and drawio files within a repository.
- Support within trestle to streamline management within a managed git environment.
- An underlying object model that supports developers interacting with OSCAL artifacts.

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

Users needing to import XML OSCAL artifacts are recommended to look at NIST's XML to json conversion page [here](https://github.com/usnistgov/OSCAL/blob/main/build/README.md#converters).

## Python codebase, easy installation via pip

Trestle runs on almost all Python platforms (e.g. Linux, Mac, Windows), is available on PyPi and can be easily installed via pip. It is under active development and new releases are made available regularly.\
To install run: `pip install compliance-trestle`\
See [Install trestle in a python virtual environment](https://oscal-compass.github.io/compliance-trestle/python_trestle_setup/) for the full installation guide.

## Complete documentation and tutorials

Complete documentation, tutorials, and background on compliance can be found [here](https://oscal-compass.github.io/compliance-trestle).

## Agile Authoring

A trestle-based agile authoring repository setup tool, documentation and tutorial can be found [here](https://github.com/oscal-compass/compliance-trestle-agile-authoring).

Agile authoring comprises the following beneficial features:

- based on OSCAL documents behind-the-scenes
- employs GIT for document control and access
- exposes text (markdown) and spread sheets (csv) to ease management of compliance artifacts
- implements compliance digitization for improved audit readiness and cost effectiveness

## Demos

A collection of demos utilizing trestle can be found in the related project [compliance-trestle-demos](https://github.com/oscal-compass/compliance-trestle-demos).

## Development status

### v3: stable (actively developed)

- supports NIST OSCAL 1.1.2 as well as previous versions

### v2: stable (maintenance mode)

- supports NIST OSCAL 1.0.4 as well as previous versions

## Community meetings and communications

Please refer to the community [README](https://github.com/oscal-compass/community/blob/main/README.md) for communication details.

## Contributing to Trestle

Our project welcomes external contributions. Please consult [contributing](https://oscal-compass.github.io/compliance-trestle/contributing/mkdocs_contributing/) to get started.

## Code of Conduct

Participation in the OSCAL Compass community is governed by the [Code of Conduct](https://github.com/oscal-compass/community/blob/main/CODE_OF_CONDUCT.md).

## License & Authors

If you would like to see the detailed LICENSE click [here](LICENSE).
Consult [contributors](https://github.com/oscal-compass/compliance-trestle/graphs/contributors) for a list of authors and [maintainers](MAINTAINERS.md) for the core team.

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
