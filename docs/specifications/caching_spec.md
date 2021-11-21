# Trestle caching architecture

## Purpose

This document describes the caching strategy and behaviour that is supported by trestle for 3rd party artifacts that are
external to the core repo. A principle that trestle is expected to uphold is that documents, unless the user explicitly
contradicts, are referred to by reference.

For example the user should *not* be expected to manually copy NIST 800-53 into their working directory (although they may). They would refer to the source document such that integrity is maintained. Given this a caching strategy is required to manage these documents - especially when operating in a CICD world.

## Users

The scope of this document is for developers. Once implemented additional documentation should be created for end users.

## Scope

This document is only concerned with links which refer to other OSCAL schema objects. External references (say to an xccdf document) are not considered.

## Cache update behaviour.

When a user requests an external resource the cache MUST be used unless the user provides a cache update flag `--update-cache`. If the cache cannot update
the default behaviour of `--update-cache` is failure. If `--update-cache-opportunistic` is enabled instead the cache will be updated where possible.

Note: Documents MUST only be committed to the cache if and only if they are valid OSCAL. Note that OSCAL validation in this context is defined ONLY as
meeting the minimum requirements of the json schema.

## Types of external references.

NIST defines many types of referential links within the OSCAL schema. Here trestle is interested in supporting a subset of these links. In particular these links are characterized specifically by the fact that they refer to 'upstream' OSCAL
artifacts. The table below identifies the references covered by this document.

| Schema               | Json path ( represents array or named keys)                               | Refers to            |
| -------------------- | ------------------------------------------------------------------------- | -------------------- |
| profile              | profile.imports\[\*\].href                                                | catalog or profile   |
| SSP                  | system-security-plan.import-profile.href                                  | profile              |
| component-definition | component-definition.import-component-definition\[\*\].href               | component-definition |
| component-definition | component-definition.component\[\*\].control-implementations\[\*\].source | catalog or profile   |
| target-definition    | target-definition.import-target-definition\[\*\].href                     | target-definition    |
| target-definition    | target-definition.component\[\*\].control-implementations\[\*\].source    | catalog or profile   |
| assessment-plan      | assessment-plan.import-ssp.href                                           | ssp                  |
| assessment-results   | assessment-results.import-ap.href                                         | assessment-plan      |

It is worth noting that the profile definition is recursive. In some of the OSCAL schemas these objects are optional. For the purposes of trestle these references are considered mandatory and it is expected that trestle will error if fields
are missing.

In particular while (say as an example) import-ssp is optional in assessment-plan, without it we cannot validate if the control ids provided by the user make sense.

## Trestle cache dir.

The trestle cache will be located within the `.trestle` project. Files are organised within that directory by hostname
irrespective of protocol.

The resulting structure is shown below.

```text
.
├── .trestle
│   └──cache
│       ├── localhost (./ or file)
│       │   ├── __rel__
│       |   |   └── __parent__/__parent__/catalog.json
│       │   └── __abs__
│       |       └── /__root__/home/username/oscal/catalog.jon
│       └── hostname.com
│              └── path/to/file.json
│
|         
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

Note that `localhost` has special treatment to manage relative file references.

The cache *MAY* live within version control system depending on desired behaviour. It is recommended that caches live
within the VCS to allow end to end tracking. Keeping the cache within the VCS implies that callers of trestle MUST
explicitly ask for the cache to be refreshed if required.

The cache MUST NOT reference files within the current trestle context.

The cache MUST NOT support 'distributed OSCAL files'. All files MUST be a valid OSCAL schema in a single document.

## Supported protocols / methods

### Local file system (aka localhost)

The local file system MAY be used as a storage mechanism other files. Local storage is unique in that references may be
relative at all times (i.e. it does not make sense to expand the directory path). Given this localhost has two sub directories:

`__abs__` for absolute paths,

`__rel__` for relative paths.

In addition to this relative paths MAY contain `../` references to the parent directory. This is represented by
`__parent__` /

Local storage may be referred to by the following mechanisms:

`file://path/to/file.json`  => `.trestle/cache/localhost/__rel__/path/to/file.json`

`file:///abspath/to/file.json` => `.trestle/cache/localhost/__abs__/abspath/to/file.json`

`/root/file/path.json` => `.trestle/cache/localhost/__abs__/root/file/path.json`

`../relative/path/to/file.json` => `.trestle/cache/localhost/__rel__/__parent__/relative/path/to/file.json`

`http(s)://localhost/path/to/file.json` => `.trestle/cache/localhost/__abs__/path/to/file.json`

References MUST NOT address the local trestle context. References outside of the local trestle context WILL NOT be tested
for whether they are in the trestle context. For localhost both absolute and relative references are supported. All calls
over http(s) are treated as absolute paths. Authorization / authentication is as in the following section.

#### Relative path reference root

Relative paths are setup assuming the they are with respect to the editing directory. Relative paths in the `dist` directory
should be reworked to include `dist`.

### HTTPS ONLY

HTTPS endpoints are supported for trestle. Unencrypted HTTP endpoints are not.

The simplest case is similar to this:
`https://sample.com/path/to/file.json` => `.trestle/cache/sample.com/path/to/file.json`

For all workloads the http header application type *SHOULD* match the file type provided. Trestle *MAY* warn on inconsistencies,
however, the file extension takes precedence.

For endpoints where an extension is NOT provided
`https://sample.com/path/to/file`
or
`https://sample.com/path/to/file/`
Trestle will:

1. Infer file type from http headers
1. write out the file to object.{filetype} file.
1. If a user requests `https://sample.com/path/to/file/object.json` trestle MUST warn the user of the risk of conflicts
   with automatically generated names.

### Authentication:

As the caching supports HTTPS ONLY, there is support for HTTP basic authentication. Attempting HTTP based authentication MUST cause errors, as would attempting HTTP fetching in any case.

Credentials MUST NOT be stored in cleartext.

NOT ALLOWED: `https://username:password@sample.com/path/to/file/`

Credentials MUST be referred to by moustache templates e.g.:

`https://{{username_var}}:{{password_var}}@sample.com/path/to/file/`

where the "moustache" templated variables refer to environmental variables in the user's environment.

Support for non standard behaviour is supported on specific domains (see below).

### Specific domains over https

Given the requirement for raw source files users *may* have issues accurately accessing a resource on many domains for
which they can get the raw form. This is also true on environments where 2-Factor Authentication may protect accessing
user facing sites. Specific site support is expected to expand based on user's requirements.

#### Github.com / github.enterprisename.com

Support in this section is intended to cover both github.com and github enterprise deployed at github.{business url}.com.

The first scenario is for unauthenticated access. Unauthenticated access may be addressed through either the 'UI' form
URL e.g.:

https://github.com/IBM/compliance-trestle/blob/develop/LICENSE

OR

the raw form URL:
https://raw.githubusercontent.com/IBM/compliance-trestle/develop/LICENSE

Both URLs would map to the following path in trestle cache:
`.trestle/cache/github.com/IBM/compliance-trestle/develop/LICENSE`

For authenticated scenarios both domains are supported, however, tokens provided to the raw website e.g.:
https://raw.githubusercontent.com/IBM/compliance-trestle/develop/LICENSE?token=TOKEN

are ignored. Trestle MUST warn users when github tokens are included.

To support authentication with github username / password authentication MUST NOT be supported. API authentication through
personal access tokens is supported. API tokens will be read from the environment with the following patterns:

github.com: `GITHUB_API_TOKEN`

github.business.com: `GITHUB_BUSINESS_API_TOKEN`

In the future `ssh` based authentication may be supported.

### SFTP

SFTP support may be supported. The URI takes the following form:

`sftp://{{username}}:{{password}}@sftp.com:/path/to/file.json`
OR
`sftp://username:{{password}}@sftp.com:/path/to/file.json`
OR
`sftp://username@sftp.com:/path/to/file.json`

All user provided paths WILL be expanded to the full path. (e.g. if `~` is used to represent the home directory.) a SSH key
may be provided by environmental variable `SSH_KEY`.

## Potential future supported methods.

It is anticipated that some applications may be provided with specialised support from the trestle framework. The current
list being considered includes:

- git (over https or ssh)
- TBA

## 
