# Compliance-trestle (also known as `trestle`)

![[OS Compatibility](#prerequisites)](https://img.shields.io/badge/platform-osx%20%7C%20linux%20%7C%20windows-orange.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compliance-trestle)
![[Pre-commit](https://github.com/pre-commit/pre-commit)](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![[Code Coverage](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=coverage)
![[Quality gate](https://sonarcloud.io/dashboard?id=compliance-trestle)](https://sonarcloud.io/api/project_badges/measure?project=compliance-trestle&metric=alert_status)
![[Pypi](https://pypi.org/project/compliance-trestle/)](https://img.shields.io/pypi/dm/compliance-trestle)
![GitHub Actions status](https://img.shields.io/github/workflow/status/IBM/compliance-trestle/Trestle%20PR%20pipeline?event=push)

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

The current version of trestle supports NIST OSCAL 1.0.0-4.  There was a breaking change in OSCAL moving from
version 1.0.0 to 1.0.2 mainly due to `prop` becoming `props` in AssessmentResults.  As a result, the current development path of trestle requires OSCAL 1.0.4, but for those who require OSCAL 1.0.0 please use trestle version 0.37.x.  That version is stable but will not have any features added, and we encourage users to move to OSCAL 1.0.4.

OSCAL version 1.0.0 files are still handled on import but any AssessmentResults must conform to the OSCAL 1.0.4 schema, with
props instead of prop.  And all files created by trestle will be output as OSCAL version 1.0.4.

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

Future roadmap anticipates that support for xml [import](https://github.com/IBM/compliance-trestle/issues/177) and [upstream references](https://github.com/IBM/compliance-trestle/issues/178) will be enabled. However, it is expected
that full support will remain only for `json` and  `yaml`.

Users needing to import XML OSCAL artifacts are recommended to look at NIST's XML to json conversion page [here](https://github.com/usnistgov/OSCAL/tree/master/json#oscal-xml-to-json-converters).

## Python codebase, easy installation via pip

Trestle runs on almost all Python platforms (e.g. Linux, Mac, Windows), is available on PyPi and can be easily installed via pip. It is under active development and new releases are made available regularly.\
To install run: `pip install compliance-trestle`\
See [Install trestle in a python virtual environment](https://ibm.github.io/compliance-trestle/python_trestle_setup/) for the full installation guide.

## Complete documentation and tutorials

Complete documentation, tutorials, and background on compliance can be found [here](https://ibm.github.io/compliance-trestle).

## Demos

A collection of demos utilizing trestle can be found in the related project [compliance-trestle-demos](https://github.com/IBM/compliance-trestle-demos).

## Development status

Compliance trestle is currently stable and is based on NIST OSCAL version 1.0.4, with active development continuing.

## Community call

We would like to share development in progress for compliance trestle, coming soon and get feedback from community on what features would they like to see in compliance trestle.\
The community call will happen every 2 week(s) on Tuesday at 10.00am EST.\
Meeting information:

```
Compliance Trestle Community Call

Join from the meeting link
https://ibm.webex.com/ibm/j.php?MTID=m030fdef5ac2d09f46f04813bb5e9dc6b
Tuesday, September 5, 2023 10:00 AM | 30 minutes | (UTC-04:00) Eastern Time (US & Canada)
Occurs every 2 week(s) on Tuesday effective 9/5/2023 from 10:00 AM to 10:30 AM, (UTC-04:00) Eastern Time (US & Canada)
 
Join by meeting number
Meeting number (access code): 146 967 4515
 
Tap to join from a mobile device (attendees only)
1-844-531-0958,,1469674515#43533276# United States Toll Free
+1-669-234-1178,,1469674515#43533276# United States Toll
Some mobile devices may ask attendees to enter a numeric password.
 
Join by phone
1-844-531-0958 United States Toll Free
1-669-234-1178 United States Toll
Global call-in numbers  |  Toll-free calling restrictions
 
Join from a video system or application
Dial 1469674515@ibm.webex.com
You can also dial 173.243.2.68 and enter your meeting number.

```

## Contributing to Trestle

Our project welcomes external contributions. Please consult [contributing](https://ibm.github.io/compliance-trestle/contributing/mkdocs_contributing/) to get started.

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
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

```
