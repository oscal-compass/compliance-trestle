# Trestle demonstration projects and content

Trestle has a number of demonstrations setup in the [IBM/compliance-trestle-demos](https://github.com/IBM/compliance-trestle-demos)
repository which is intended to be a single point of call for demonstrations and content.

If you are interested in contributing a demonstration / content open a PR to the demonstration repo and a PR to
[this page](https://github.com/IBM/compliance-trestle/blob/develop/docs/demonstrations-content.md).

Demonstrations, where practical, should include instructions on how they were created.

## Current demonstrations

## Simple sdk examples.

[This folder](https://github.com/IBM/compliance-trestle-demos/tree/develop/trestle_sdk_examples) contains a number of small examples for using the trestle OSCAL sdks.

## Australian government Information Security Manual (ISM)

This demonstration uses trestle as an SDK for generating OSCAL files. This demonstration downloads all currently available versions of the Australian Government ISM from [ACSC](https://www.acsc.gov.au) and converts those documents to a set of OSCAL catalogs and profiles. [Read more about the demo here](https://github.com/IBM/compliance-trestle-demos/tree/develop/ISM_catalog_profile).

## arc42 architectural template enforcement using trestle author.

[arc42](https://arc42.org/) have created a set open-source architecture documentation templates. This [demonstration](https://github.com/IBM/compliance-trestle-demos/tree/develop/arc42-author-demo)
uses `trestle author` to enforce use of the (modified) arc42 templates.

A CICD pipeline (using github actions) is used for this demonstration. The full repository, including working CICD is [here](https://github.com/IBM/compliance-trestle-arc42-demo). Read more about the demo [here](https://github.com/IBM/compliance-trestle-arc42-demo).

## Trestle flask microservice demonstration.

`trestle` uses a python library called [pydantic](https://pydantic-docs.helpmanual.io/) to form the underlying OSCAL object models. [flask-pydantic](https://github.com/bauerji/flask_pydantic) introduces a mechanism which integrates pydantic models into flask, providing automated user input validation in one line of code. This demo accepts a catalog as a POSTed object, throwing errors if the catalog does not meet the schema, and returns the catalog in the response. Find the demonstration [here](https://github.com/IBM/compliance-trestle-demos/tree/develop/trestle_flask_api).

## Creating a CIS controls catalog from an excel spreadsheet.

The Centre for Internet Security (CIS) produce a number of cross industry standards for IT security including their [platform specific benchmarks](https://www.cisecurity.org/cis-benchmarks/) and a suite of [controls](https://www.cisecurity.org/controls/). [This demo](https://github.com/IBM/compliance-trestle-demos/tree/develop/CIS_controls) converts a spreadsheet of those controls into a a catalog and three profiles.

## Creating an SSP using trestle author.

`trestle author ssp-generate` and `trestle author ssp-author` allow users to generate first a set of markdown documents to allow easy editing of control responses and second to reassemble that information up into an OSCAL ssp document. [This is a 'baseline' demonstration](https://github.com/IBM/compliance-trestle-demos/tree/develop/ssp_author_demo) with more sophisticated updates expected in the near term.

## Trestle repository api (`trestle.core.repository`)

`trestle.core.repository` is an API which abstracts users from the file system of a trestle repository. It provides a way for external developers to access a trestle repository without relying on presumptions (such as cwd being within the repository). Find the demo [here](https://github.com/IBM/compliance-trestle-demos/tree/develop/trestle_repo_api_examples).

## Converting a spreadsheet into a `component-definition`

Plenty of compliance content exists today in spreadsheets. This [demonstration](https://github.com/IBM/compliance-trestle-demos/tree/develop/trestle_task_spread_sheet_to_component_definition) show how to use the xlsx-to-oscal-component-definition MVP functionality.

## Task examples

### Spreadsheet to component definition
