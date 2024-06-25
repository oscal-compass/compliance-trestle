# <img alt="Logo" width="50px" src="./images/compliance-trestle-800x800.png" style="vertical-align: middle;" /> Compliance-trestle (also known as `trestle`)

![[OS Compatibility](#prerequisites)](https://img.shields.io/badge/platform-osx%20%7C%20linux%20%7C%20windows-orange.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compliance-trestle)
![[Pre-commit](https://github.com/pre-commit/pre-commit)](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![[Code Coverage](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=coverage)
![[Quality gate](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=alert_status)
![[Pypi](https://pypi.org/project/compliance-trestle/)](https://img.shields.io/pypi/dm/compliance-trestle)
![GitHub Actions status](https://img.shields.io/github/workflow/status/oscal-compass/compliance-trestle/Trestle%20PR%20pipeline?event=push)

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

## Important Note:

The current trestle v3:

- supports NIST OSCAL 1.1.2 as well as previous versions
- new OSCAL json documents created will be output as OSCAL version 1.1.2
- old OSCAL json documents created using trestle v2 are supported (backwards compatibility)
- some Python module dependencies have been upgraded

OSCAL changes between 1.0.4 and 1.1.2 can be found here: [https://github.com/usnistgov/OSCAL/releases](https://github.com/usnistgov/OSCAL/releases). In short:

<details>
<summary>1.1.2</summary>
<ul>
<li>Catalog constraints added in oscal_catalog_metaschema.xml
<li>Remove with-parent-controls from implementation
<li>Bump actions/setup-java from 3 to 4
<li>CI Automation enhancements
</ul>
</details>

<details>
<summary>1.1.1</summary> 
<ul>   
<li>Allow non-FISMA/RMF use cases for SSP information type impact levels.
<li>Remove obsolete model documentation for biblio elements in back-matter/resources.
</ul>
</details>

<details>
<summary>1.1.0</summary> 
<ul>   
<li>SSP: Change certain elements from required to optional for non-RMF use cases.
<li>SSP: improve constraints of links for cross-referencing components and indicating where components were imported from.
<li>POAM: add related-findings assembly.
<li>Profile: Remove with-parent-controls from the profile model.
<li>Metadata: add group attribute to props
<li>Metadata: add resource fragment to links (very useful for deep-linking into elements by UUID and point to sub-element UUID)
<li>Metadata: add actions assembly to track approvals or request for changes status.
<li>Metadata: correct how cross-references between controls and their parts are handled.
<li>Mapping: re previous discussion, mapping, by itself or within catalog, has been moved out of the v1.1.0 release.
</ul>
</details>

<details>
<summary>1.0.6, 1.0.5</summary> 
<ul>   
<li>Small bug fixes
</ul>
</details>

There was a breaking change in OSCAL moving from version 1.0.0 to 1.0.2 mainly due to `prop` becoming `props` in AssessmentResults.  Those who require strict OSCAL 1.0.0 please use trestle version 0.37.x.  That version is stable but will not have any features added, and we encourage all users to move to OSCAL 1.1.2. OSCAL version 1.0.0 files are still handled on import but any AssessmentResults must conform to the `props` in AssessmentResults OSCAL specification.

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

Compliance trestle is currently stable and is based on NIST OSCAL version 1.1.2, with active development continuing.

## Community meetings and communications

Please refer to the community [README](https://github.com/oscal-compass/community/blob/main/README.md) for communication details.

## Contributing to Trestle

Our project welcomes external contributions. Please consult [contributing](https://oscal-compass.github.io/compliance-trestle/contributing/mkdocs_contributing/) to get started.

## License & Authors

If you would like to see the detailed LICENSE click [here](LICENSE).
Consult [contributors](https://github.com/oscal-compass/compliance-trestle/graphs/contributors) for a list of authors and [maintainers](MAINTAINERS.md) for the core team.

```text
# Copyright (c) 2020 IBM Corp. All rights reserved.
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
