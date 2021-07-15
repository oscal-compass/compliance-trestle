# Trestle demonstration projects and content

Trestle has a number of demonstrations setup in the [IBM/compliance-trestle-demos](https://github.com/IBM/compliance-trestle-demos)
repository which is intended to be a single point of call for demonstrations and content.

If you are interested in contributing a demonstration / content open a PR to the demonstration repo and a PR to
[this page](https://github.com/IBM/compliance-trestle/blob/develop/docs/demonstrations-content.md).

Demonstrations, where practical, should include instructions on how they were created.

## Current demonstrations

### Hand crafted content

Content that has been hand crafted in OSCAL is available [here](<>)

### Australian government Information Security Manual (ISM)

The Australian government publish the ISM in a custom XML format. This [demonstration](<>) uses trestle as an SDK for
generating OSCAL files. Specifically a script generates catalogs and profiles (for each security level) per ISM version.

### Simple OSCAL API using trestle & Flask

Pydantic, the underlying object model for trestle, integrates with flask. This [demonstration](<>) api allows users to validate
a catalog or receive the error.

### arc42 architectural template enforcement using trestle author.

[arc42](https://arc42.org/) have created a set open-source architecture documentation templates. This [demonstration](<>)
uses `trestle author` to enforce use of the (modified) arc42 templates.

A CICD pipeline (using github actions) is used for this demonstration.
