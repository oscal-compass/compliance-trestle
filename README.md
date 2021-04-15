# Compliance-trestle a.k.a. `trestle`

[![OS Compatibility][platform-badge]](#prerequisites)
[![Python Compatibility][python-badge]][python]
[![pre-commit][pre-commit-badge]][pre-commit]
[![code-coverage][coverage-badge]][coverage]
[![pypi-downloads][pypi-downloads-badge]][pypi]

Trestle is a ensemble of tools that enables the creation and validation of documentation artifacts for compliance requirements. It leverages NIST's [OSCAL](https://pages.nist.gov/OSCAL/documentation/) as a standard data format for interchange between tools and people, and provides an opinionated approach to OSCAL adoption.

By design Trestle runs as a CICD pipeline running on top of compliance artifacts in `git` to provide transparency to the state of compliance across multiple stakeholders in an environment friendly to developers.

Trestle provides tooling to help orchestrate the compliance process across a number of dimensions:

- Tooling to manage OSCAL in a more human-friendly manner. By expanding the large OSCAL data structures into smaller and easier to edit sub-structures.
- Transformation workflows that allow existing information from tools which do not support OSCAL into OSCAL.
- Tooling to manage markdown documents for compliance, including transformation to OSCAL.
- Support within trestle to streamline management within a managed git environment.
- An underlying object model which supports developers interacting with OSCAL artefacts.

## Why Trestle

Compliance suffers from being a complex problem that is hard to articulate simply. It requires complete and accurate execution of multiple procedures across many disciplines (e.g. IT, HR, management) with periodic verification and audit of those procedures against controls.

While it is possible to manage the description of controls and how an organisation implements them in ad hoc ways with general tools (spreadsheets, documents), this is hard to maintain for multiple accreditations and, in the IT domain at least, creates a barrier between the compliance efforts and the people doing daily work (DevOps staff).

Trestle aims to reduce or remove this barrier by bringing the maintenance of control descriptions into the DevOps domain. The goal is to have changes to the system (for example, updates to configuration management) easily related to the controls impacted, and to enable modification of those controls as required in concert with the system changes.

Trestle implicitly provides a core opinionated workflow driven by its pipeline steps to allow standardized interlocks with other compliance tooling platforms.

## Development status

Compliance trestle is currently alpha. The expectation is that throughout the remainder of 2020 there may be unannounced changes that are breaking within the trestle codebase. If you are using trestle please contact us so we are aware your usecase.

The underlying OSCAL schema is also currently changing. The current approach until the formal release of OSCAL 1.0.0 is for compliance trestle to regularly update our models to reflect NIST's changes.

### Machine readable compliance format

Compliance activities at scale, whether size of estate or number of accreditations, require automation to be successful and repeatable. OSCAL as a standard allows teams to bridge between the "Governance" layer and operational tools.

By building human managed artifacts into OSCAL, Trestle is not only able to validate the integrity of the artifacts that people generate - it also enables reuse and sharing of artifacts, and furthermore can provide suitable input into tools that automate operational compliance.

## Using Trestle

Trestle converts complex schema/data structures into simple files in a directory structure. The aim of this is to make it easier to manage for humans: Individual objects can be versioned & reviewed, then 'compiled' into the larger structure of a Catalog, SSP or Assessment Plan.

### Install and Run

Install from PYPI and run:

```shell
# Setup virtual environement
python3 -m venv venv
. ./venv/bin/activate

# Install trestle from PYPI
pip install compliance-trestle

# Run Trestle CLI
trestle -h # For command line help
```

In order to install Trestle from source, run the following command:

```shell
# Clone
git clone https://github.com/IBM/compliance-trestle.git
cd compliance-trestle

# Setup
python3 -m venv venv
. ./venv/bin/activate
pip install -q -e ".[dev]" --upgrade --upgrade-strategy eager

# Run Trestle CLI
trestle -h
```

## Supported OSCAL elements and extensions

`trestle` implicitly supports all OSCAL schemas for use within the object model. The development roadmap for `trestle` includes adding workflow around specific elements / objects that is opinionated.

`trestle` supports OSCAL version `1.0.0-rc2` only at this stage. NIST, in pre-1.0.0 [continuously updating
](https://github.com/usnistgov/OSCAL/issues/846) their current posture. Trestle will be periodically updating to meet NIST's baseline. On the formal release of OSCAL `1.0.0` the strategy for trestle will be revaluated.

In addition to the core OSCAL objects, trestle supports the definition of a `target`. The `target` (and its container
`target-definition`) is a generalization of the `component` model that is designed specifically to support configuration.

`catalog` and `profile` objects can define parameters. However, by their nature the parameter definitions are at the
regulatory level. The `trestle` team has seen a need for an object that can define parameters at the `control-implemenation`
level, e.g. `component` is an implementation and `target` is the definition of capabilities of the component.

### 3rd party supported elements.

In addition to the core OSCAL models and the `target-definition` trestle provides support for 3rd party schemas for `tasks` and for use as an object model layer. By design these will not be supported by core trestle editing commands (e.g. split / merge).

## Supported file formats for OSCAL objects.

OSCAL supports `xml`, `json` and `yaml` with their [metaschema](https://github.com/usnistgov/metaschema) tooling. Trestle
natively supports only `json` and `yaml` formats at this time.

Future roadmap anticipates that support for xml [import](https://github.com/IBM/compliance-trestle/issues/177) and [upstream references](https://github.com/IBM/compliance-trestle/issues/178) will be enabled. However, it is expected
that full support will remain only for `json` and  `yaml`.

Users needing to import XML OSCAL artifacts are recommended to look at NIST's XML to json conversion page [here](https://github.com/usnistgov/OSCAL/tree/master/json#oscal-xml-to-json-converters).

## Tutorials

List of tutorials [here](https://ibm.github.io/compliance-trestle/tutorials/tutorials/).

## Contributing to Trestle

Our project welcomes external contributions. Please consult [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## License & Authors

If you would like to see the detailed LICENSE click [here](LICENSE).
Consult [contributors](https://github.com/IBM/compliance-trestle/graphs/contributors) for a list of authors and [maintainers](MAINTAINERS.md) for the core team.

```text
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

```

[coverage]: https://codecov.io/gh/IBM/compliance-trestle
[coverage-badge]: https://codecov.io/gh/IBM/compliance-trestle/branch/develop/graph/badge.svg?token=1AUXDAF3OB
[platform-badge]: https://img.shields.io/badge/platform-osx%20%7C%20linux-orange.svg
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pypi]: https://pypi.org/project/compliance-trestle/
[pypi-downloads-badge]: https://img.shields.io/pypi/dm/compliance-trestle
[python]: https://www.python.org/downloads/
[python-badge]: https://img.shields.io/badge/python-v3.6+-blue.svg
