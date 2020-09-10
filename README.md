# Trestle

Trestle is a tool to which enables the creation and validation of documentation artifacts for compliance requirements. It leverages NIST's [OSCAL](<https://pages.nist.gov/OSCAL/documentation/>) as a standard data format for interchange between tools & people and provides an opinionated approach to OSCAL adoption.

By design Trestle runs as a CICD pipeline running on top of compliance artifacts in `git` to provide transparency to the state of compliance across multiple stakeholders in an environment friendly to developers. Trestle passes the artifacts generated on to tools to orchestrate the enforcement, measurement and reporting of compliance.

It also provides tooling to manage OSCAL in a more human-friendly manner. By expanding the large OSCAL data structures into smaller, easier to edit, sub-structures, creation and maintenance of these artifacts can follow normal `git` workflows (peer review via pull request, versioning, releases/tagging).

## Why Trestle?

Compliance suffers from being a complex problem that is hard to articulate simply. It requires complete & accurate execution of multiple procedures, across many disciplines (IT, HR, management), with periodic verification and audit of said procedures against controls.

While its possible to manage the description of controls & how an organisation implements them in ad hoc ways, with general tools (spreadsheets, documents), this is hard to maintain for multiple accreditations and, in the IT domain at least, creates a barrier between the compliance efforts and people doing daily work (DevOps staff).

Trestle aims to reduce or remove this barrier by bringing the maintenance of control descriptions into the DevOps domain. The aim is to have changes to the system (for example, updates to configuration management) easily related to the controls impacted & those controls be modified if required in concert with the system change.

Trestle implicitly provides an core opinionated workflow driven by it's pipeline steps to allow standardized interlocks with other compliance tooling platforms.

### Machine readable compliance format

Compliance activities at scale, be that size of estate, or number of accreditations, require automation to be successful & repeatable. OSCAL as a standard allows teams to bridge between the "Governance" layer and operational tools.

By building human managed artifacts into OSCAL, Trestle is not only able to validate the integrity of the artifacts that people generate, it also enables reuse and sharing of artifacts and can also provide suitable input into tools which automate operational compliance.

## Using Trestle

Trestle converts complex schema/data structures into simple files in a directory structure. The aim of this is to make it easier to manage for humans - individual objects can be versioned & reviewed, then 'compiled' into the larger structure of a Catalog, SSP or Assessment Plan.

### Install and Run:

Install from PYPI and run:
~~~shell
# Setup virtual environement
python3 -m venv venv
. ./venv/bin/activate

# Install trestle from PYPI
pip install compliance-trestle

# Run Trestle CLI
trestle -h # For command line help
~~~

In order to install Trestle from source, run the following command:
~~~shell
# Clone
git clone https://github.com/IBM/compliance-trestle.git
cd compliance-trestle

# Setup
python3 -m venv venv
. ./venv/bin/activate
pip install -q -e ".[dev]" --upgrade --upgrade-strategy eager

# Run Trestle CLI
trestle -h
~~~

## Contributing to Trestle
Our project welcomes external contributions. Please checkout [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## License & Authors
If you would like to see the detailed LICENSE click [here](LICENSE).
Check out [MAINTAINERS](MAINTAINERS.md) for list of authors.

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