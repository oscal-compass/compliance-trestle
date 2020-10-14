# Trestle caching architecture

## Table of Contents

- [Purpose](<#purpose>)
- [Users](<#users>)
- [Caching Structure](<>)
- [Dist vs editable structures](<>)
- [Supported URIs](<>)
- [Git support](<>)
- [Update behaviour](<>)

## Purpose

This document describes the caching strategy and behaviour that is supported by trestle for 3rd party artifacts that are
external to the core repo. A principle that trestle is expected to uphold is that documents, unless the user explicitly
contradicts, are referred to by reference.

For example the user should *not* be expected to manually copy NIST 800-53 into their working directory (although they may). They waould refer to the source document such that integrity is maintained. Given this a caching strategy is required to manage these documents - especially when operating in a CICD world.

## Users

The scope of this document is for developers. Once implemented additional documentation should be created for end users.

## Scope

This document is only concerned with links which refer to other OSCAL schema objects. External references (say to an xccdf document) are not considered.

## Types of external references.

NIST defines many types of referential links within the OSCAL schema. Here trestle is interested in supporting a subset of these links. In particular these links are characterized specifically by the fact that they refer to 'upstream' OSCAL
artifacts. The table below identifies the references covered by this document.

| Schema               | Json path (\[*\] represents array or named keys)                      | Refers to            |
| \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-| \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-- | \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--- |
| profile              | profile.imports\[*\].href                                             | catalog or profile   |
| SSP                  | system-security-plan.import-profile.href                            | profile              |
| component-definition | component-definition.import-component-definition\[*\].href            | component-definition |
| component-definition | component-definition.component\[*\].control-implementations\[\*\].source | catalog or profile   |
| assessment-plan      | assessment-plan.import-ssp.href                                     | ssp                  |
| assessment-results   | assessment-results.import-ap.href                                   | assessment-plan      |

It is worth noting that the profile definition is recursive. In some of the OSCAL schemas these objects are optional. For the purposes of trestle these references are considered mandatory and it is expected that trestle will error if fields
are missing.

In particular while (say as an example) import-ssp is optional in assessment-plan, without it we cannot validate the control ids provided by the user are sensical.

## Cache directory

The cache directory

```
.
├── .trestle
│   └──cache
│       ├── localhost (./ or file)
│       │   ├── rel
│       |   |   └── parent/parent/catalog.json
│       │   └── abs
│       |       └── home/username/oscal/catalog.jon
│       ├── github.com # git+https / git+ssh
│       |   └── org
│       |        └── project
│       |             └── branch/tag/commit
│       |                   └── expanded/directory/path/for/asset.json
│       ├── bitbucket.com git+https / git+ssh
│       |   └── path_to
│       |        └── project # this is where .git lives
│       |             └── branch/tag/commit
│       |                   └── expanded/directory/path/for/asset.json
│       ├── arbitrary-rest-api.com (https)
│       |   └── endpoint
│       |       └── ID (by path)
│       |           └── object.json (inferred)
│       ├── arbitrary-static-file.com (https)
│           └── path
│               └── to
│                   └── catalog.json (not inferred)
├── dist
│   ├── catalogs
│   ├── profiles
│   ├── target-definitions
│   ├── system-security-plans
│   ├── assessment-plans
│   ├── assessment-results
│   └── plan-of-action-and-milestones
├── catalogs
├── profiles
├── target-definitions
├── component-definitions
├── system-security-plans
├── assessment-plans
├── assessment-results
└── plan-of-action-and-milestones
```

### Inclusion in VCS or not

### Behaviour on initialization of the cache directory.
