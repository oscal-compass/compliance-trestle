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

[arc42](https://arc42.org/) have created a set open-source architecture documentation templates. This [demonstration](https://github.com/IBM/compliance-trestle-demos/tree/develop//arc42-author-demo)
uses `trestle author` to enforce use of the (modified) arc42 templates.

A CICD pipeline (using github actions) is used for this demonstration. The full repository, including working CICD is [here](https://github.com/IBM/compliance-trestle-arc42-demo). Read more about the demo [here](https://github.com/IBM/compliance-trestle-arc42-demo).

## Trestle flask microservice demonstation.

`trestle` uses a python library called [pydantic](https://pydantic-docs.helpmanual.io/) to form the underlying OSCAL object models. [flask-pydantic](https://github.com/bauerji/flask_pydantic) introduces a mechanism which integrates pydantic models into flask, providing automated user input validation in one line of code. This demo accepts a catalog as a POSTed object, throwing errors if the catalog does not meet the schema, and returns the catalog in the response. Find the demonstration [here](https://github.com/IBM/compliance-trestle-demos/tree/develop/trestle_flask_api).
