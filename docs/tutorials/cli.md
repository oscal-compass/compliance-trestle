---
title: trestle CLI Overview
description: An introductory tutorial into trestle's CLI and OSCAL use cases
---

# trestle CLI Overview and OSCAL usecases

The trestle CLI has three primary use cases:

- Serve as tooling to generate and manipulate OSCAL files directly by an end user. The objective is to reduce the complexity of creating and editing workflows. Example commands are: `trestle import`, `trestle create`, `trestle split`, `trestle merge`.
- Act as an automation tool that, by design, can be an integral part of a CI/CD pipeline e.g. `trestle validate`, `trestle tasks`.
- Allow governance of markdown documents so they conform to specific style or structure requirements.

To support each of these use cases trestle creates an opinionated directory structure to manage governed documents.

## Opinionated directory structure

Trestle relies on an opinionated directory structure (trestle workspace), similar to `git`, `go`, or `auditree`, to manage the workflow. Most trestle commands are restricted to working within an initialized directory tree.

The directory structure setup by trestle has three major elements:

- A `.trestle` hidden folder.
- A `dist` folder.
- Folders for each of the top level OSCAL models.

The outline of the schema is below:

```text
.
├── .trestle
├── dist
│   ├── catalogs
│   ├── profiles
│   ├── component-definitions
│   ├── system-security-plans
│   ├── assessment-plans
│   ├── assessment-results
│   └── plan-of-action-and-milestones
├── catalogs
├── profiles
├── component-definitions
├── system-security-plans
├── assessment-plans
├── assessment-results
└── plan-of-action-and-milestones
```

`.trestle` directory is a special directory containing various trestle artefacts to help run various other commands. Examples include configuration files, caches and templates.

`dist` directory will contain the assembled version of the top level models located on the source model directories.

The bulk of the folder structure is used to represent each of the *top level schemas* or *top level models* such as `catalogs` and `profiles`. For each of these directories the following root structure is maintained:

```text

├── .trestle
└── TOP_LEVEL_MODEL_PLURAL
    └── NAME_OF_MODEL_INSTANCE
        └── TOP_LEVEL_MODEL_NAME.{json,yaml,yml}

```

which appears, for a catalog a user decides is titled nist-800-53, as:

```text
├── .trestle
└── catalogs
    └── nist-800-53
        └── catalog.json

```

In most of the places in the documentation we use `json` format for specifying model files, but they are equally applicable to `yaml` format also. The default format is `json`, and `yaml` is supported on best effort basis. Within one model directory the two different formats should not be mixed.

### Support for subdivided document structures

The files constructed by OSCAL can run into tens of thousands of lines of yaml or formatted json. At this size the
files become completely unmanageable for users. To combat this, trestle can `trestle split` a file into many smaller files and later merge those split files together.

Directory structures such as the one below can represent OSCAL document structures. Users are strongly encourage to rely on split and merge to code these structures.

Users can query the contents of files using `trestle describe`, and probe the contents more deeply using it in combination with element paths.

```text
.
├── .trestle
├── dist 
│   └── catalogs
│       └── nist800-53.json 
└── catalogs
    └── nist800-53
        ├── catalog.json
        └── catalog
            ├── metadata.json
            ├── metadata
            │   ├── revision-history
            │   │   ├── 00000__revision-history.json
            │   │   ├── 00001__revision-history.json
            │   │   └── 00002__revision-history.json   
            │   └── responsible-parties
            │       ├── creator__responsible-party.json
            │       └── contact__responsible-party.json       
            └── groups
                ├── 00000__group.json        
                ├── 00000__group
                │   └── controls
                │       ├── 00000__control.json
                │       └── 00001__control.json
                ├── 00001__group.json 
                └── 00001__group
                    └── controls
                        ├── 00000__control.json
                        └── 00001__control.json
...
```

## Specifying attributes / elements within trestle commands.

OSCAL models are rich and contain multiple nested data structures. Given this, a mechanism is required to address _elements_ /_attributes_ within an oscal object.

This accessing method is called 'element path' and is similar to _jsonPath_. Commands provide element path by a `-e` argument where available, e.g. trestle split -f catalog.json -e 'catalog.metadata.\*'. This path is used whenever specifying an attribute or model, rather than exposing trestle's underlying object model name. Users can refer to [NIST's json outline](https://pages.nist.gov/OSCAL-Reference/models/latest/complete/json-outline/) to understand object names in trestle.

### Rules for element path

1. Element path is an expression of the attribute names, [in json form](https://pages.nist.gov/OSCAL-Reference/models/latest/complete/json-outline/) , concatenated by a period (`.`).
   1. E.g. The metadata in a catalog is referred to as `catalog.metadata`
1. Element paths are relative to the file.
   1. e.g. For `metadata.json` roles would be referred to as `metadata.roles`, from the catalog file that would be `catalog.metadata.roles`
1. Arrays can be handled by a wild card `*` or a numerical index for a specific index.
   1. `catalog.groups.*` to refer to each group in a catalog
   1. `catalog.groups.*.controls.*` to refer to 'for each control under a top level group'
   1. For NIST 800-53 `catalog.groups.0.controls.0.`
1. On \*nix platforms if using the wildcard the element path argument should be wrapped in quotes to prevent problems with the shell interpreting the wild card before trestle can
1. When dealing with an array based object, the array syntax may be skipped when passing a model
   1. e.g. a control could be `catalog.controls.control` or `catalog.groups.controls.control`
   1. This syntax is required as OSCAL, across the schema, has conflicting element definitions.

### A note for software developers using trestle.

Trestle provides utilities for converting from element path to trestle's python object model. The (slightly simplified) model is:

1. Class attributes are converted from `dash-case` to `dash_case` (aka snake_case)
1. Class names are converted from `dash-case` to `DashCase` (aka CamelCase)

## `trestle version`

This command will return the current version of Trestle and OSCAL it is using.

Running `trestle version` will return:

> Trestle version v3.x.x based on OSCAL version 1.1.2

It can also be used to retrieve the metadata version of the OSCAL object:

```json
"catalog": {

    "uuid": "fa3f44a8-25cd-4f6a-8175-7afe647df7ed",

    "metadata": {

      "title": "Catalog1",

      "last-modified": "2023-01-11T17:04:02.840910+00:00",

      "version": "0.1.10", <<< this version here

      "oscal-version": "1.1.2"

    },
...
```

- `-t or --type` - a type of the OSCAL object (can be either catalog, profile, component-definition, system-security-plan, etc)
- `-n or --name` - a name of the OSCAL object

Running `trestle version -n nist -t catalog` will return:

> Version of OSCAL object of nist catalog is: 1.1.2

## `trestle init`

This command will create (initialize) a trestle workspace in the current directory with the necessary directory structure and trestle artefacts.
This command has multiple modes that it can run in:

- `--full`
- `--local`
- `--govdocs`

By default `trestle init` will run in the `--full` mode.

`--full` mode is meant to be used when full functionality of Trestle is used i.e. managing OSCAL models locally, govern documents or using Trestle for API purposes.
`dist` repository will be used when `trestle assemble` command is used.
Running `trestle init --full` will create the directory structure below for different artefacts:

```text
.
├── .trestle
├── dist
│   ├── catalogs
│   ├── profiles
│   ├── component-definitions
│   ├── system-security-plans
│   ├── assessment-plans
│   ├── assessment-results
│   └── plan-of-action-and-milestones
├── catalogs
├── profiles
├── component-definitions
├── system-security-plans
├── assessment-plans
├── assessment-results
└── plan-of-action-and-milestones
```

`--local` mode is meant to be used when Trestle is used to only manage OSCAL models locally. Running `trestle init --local` will create the directory structure below for different artefacts:

```text
.
├── .trestle
├── catalogs
├── profiles
├── component-definitions
├── system-security-plans
├── assessment-plans
├── assessment-results
└── plan-of-action-and-milestones
```

`--govdocs` mode is meant to be used when Trestle is only used to govern documents. Running `trestle init --govdocs` will create the directory structure below:

```text
.
├── .trestle
```

`.trestle` directory is a special directory containing various trestle artefacts to help run various other commands.

`dist` directory will contain the merged or assembled version of the top level models located on the source model directories which are: `catalogs`, `profiles`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` and `plan-of-action-and-milestones`.

Notice that trestle is a highly opinionated tool and, therefore, the names of the files and directories that are created by any of the `trestle` commands and subcommands MUST NOT be changed manually.

## `trestle create`

This command will create a bare-bones sample file for one of the top level OSCAL models, and it can also create new elements within an existing file.  For example, `trestle create -t catalog -o nist800-53` will create a sample catalog file, `catalog.json` in the catalog subdirectory, `nist800-53` as shown below:

```text
.
├── .trestle
└── catalogs
    └── nist800-53
        └── catalog.json
...
```

The `-t` specifies the type of the model to create, which can be one of catalog, profile, component-definition, system-security-plan, assessment-plan, assessment-results, plan-of-action-and-milestones.  Each type will be created in its corresponding directory, such as catalogs, profiles, etc.

The following additional options are supported:

- `-o or --output`: specifies the name/alias of a model. It is used as the prefix for the output filename under the `dist` directory and for naming the source subdirectories under  `catalogs`, `profiles`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` or `plan-of-action-and-milestones`.

The user can edit the parts of the generated OSCAL model by modifying the sample content in those directories.

Passing `-iof` or `--include-optional-fields` will make `trestle create` generate a richer model containing all optional fields until finding recursion in the model (e.g controls within control).

In addition, `trestle create` can create new components within an existing file by specifying the existing file name and the corresponding element path to create within that file.

For example,

`$TRESTLE_BASEDIR/catalogs/nist800-53$ trestle create -f ./catalog.json -e catalog.metadata.roles `

will add the following property under the `metadata` property for a catalog that will be written to the appropriate file under `catalogs/nist800-53` directory:

```json
{
  "roles": [
    {
      "id": "REPLACE_ME",
      "title": "REPLACE_ME"
    }
  ]
}
```

Default values for mandatory datatypes will be like below. All UUID's will be populated by default whether or not they are mandatory.

```yaml
  - DateTime: <Current date-time>
  - Boolean: false
  - Integer: 0
  - String: REPLACE_ME
  - Float/Double: 0.00
  - Id field: Auto generated UUID
```

Again, passing `-iof` or `--include-optional-fields` will make `trestle create` generate a richer version of the element being created, by including optional fields.

## `trestle import`

This command allows users to import existing OSCAL files so that they can be managed using trestle. For example `trestle import -f /local_dir/existing_catalog.json -o my_existing_catalog` will import `existing_catalog.json` into a new folder under `catalogs` as shown below:

```text
.
├── .trestle
└── catalogs
    └── my_existing_catalog
        └── catalog.json
...
```

The following options are supported:

- `-f or --file`: specifies the path of an existing OSCAL file or URL to a remote file.
- `-o or --output`: specifies the name/alias of a model. It is used as the prefix for the output filename under the `dist` directory and for naming the source subdirectories under  `catalogs`, `profiles`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` or `plan-of-action-and-milestones`.

The `--file` option may be an absolute or relative path, and it may be a URL.  For details on allowed formats please see the documentation for the `href` command.  The file must be imported from outside the current trestle directory or an error will result.

The import subcommand can determine the type of the model that is to be imported by the contents of the file.  But the file name must end with an allowed json or yaml extension: `.json, .yaml, .yml`

During the import process the file must pass the `validate` test described below for the command, `validate`.  If the file does not pass validation a warning will be given describing the nature of the problem and the import will fail.

Once a file has been imported it can be split into a rich tree of sub-components as shown at the top of this document.  But the file must be imported first.

## `trestle replicate`

This command allows users to replicate a certain OSCAL model (file and directory structure). For example `trestle replicate catalog -n cat1 -o cat11` will replicate the Catalog cat1 into `cat11` directory. It can also regenerate all the UUIDs as required.

## `trestle split`

This command allows users to further decompose a trestle model into additional subcomponents.

The following options are currently supported:

- `-f or --file`: this is optional and specifies the file path of the json/yaml file containing the elements that will be split.
- `-e or --elements`: specifies the model subcomponent element(s) (JSON/YAML property path) that is/are going to be split. Multiple elements can be specified at once using a comma-separated value, e.g `-e 'catalog.metadata,catalog.groups'`.  Make sure to include the quotes that enclose the comma-separated paths.

If the element is of JSON/YAML type array list and you want trestle to create a separate subcomponent file per array item, the element needs to be suffixed with `.*`, e.g. `-e 'catalog.groups.*'`. If the suffix is not specified, split will place all array items in only one separate subcomponent file, e.g. `'groups.json'`.  Again, make sure to include the quotes around the elements.

If you just want to split a file into all its constituent parts and the file does not contain a simple list of objects, you can still use `*` and the file will be split into all its non-trivial elements.  Thus if you split a catalog with `-e catalog.*` the result will be a new directory, `catalog`, containing files representing the large items, `back-matter.json, groups.json and metadata.json`, but there will still be a `catalog.json` file containing just the catalog's `uuid`.  Small items such as strings and dates cannot be split off and will remain in the original model file that is being split.

Here are some examples.  Starting with a single catalog file, `my_catalog/catalog.json`, if you do `trestle split -f catalog.json -e 'catalog.*'` you end up with:

```text
catalogs
 ┗ my_catalog
 ┃ ┣ catalog
 ┃ ┃ ┣ back-matter.json
 ┃ ┃ ┣ groups.json
 ┃ ┃ ┗ metadata.json
 ┃ ┗ catalog.json
```

If you then split roles out of metadata as a single file containing a list of roles, `trestle split -f catalog/metadata.json -e 'metadata.roles'` you would end up with:

```text
catalogs
 ┗ my_catalog
 ┃ ┣ catalog
 ┃ ┃ ┣ metadata
 ┃ ┃ ┃ ┗ roles.json
 ┃ ┃ ┣ back-matter.json
 ┃ ┃ ┣ groups.json
 ┃ ┃ ┗ metadata.json
 ┃ ┗ catalog.json
```

If instead you had specified `-e 'metadata.roles.*'` you would get:

```text
my_catalog
 ┣ catalog
 ┃ ┣ metadata
 ┃ ┃ ┗ roles
 ┃ ┃ ┃ ┣ 00000__role.json
 ┃ ┃ ┃ ┗ 00001__role.json
 ┃ ┣ back-matter.json
 ┃ ┣ groups.json
 ┃ ┗ metadata.json
 ┗ catalog.json
```

You can see there is no `roles.json` file anymore and instead there is a subdirectory, `roles` containing a list of files, one for each `role`.

If the `-f or --file` option is not specified, the file to split will be determined from the elements specified, in the context of the current working directory.  The current directory must be
within a specific model (e.g. `catalog` or `profile`), and the element paths must either be absolute (e.g. `catalog.metadata.roles`) or relative to the current working directory.  For example, if you are in `catalogs/mycat/catalog/groups` and you want to split the file `00000__group.json`, you must use `-f` to specify the filename, and the element path can either be absolute, as `catalog.group.*`, or you can set the current working directory to where the file is and use element path `group.*`.  This makes it easier to specify splits when deep in a directory structure.

Every subdirectory in a trestle directory model should have a corresponding `.json` or `.yaml` file with the same name, except when that subdirectory corresponds to a list of items, such as `catalog.groups`. When those subcomponents are split/expanded each file or subdirectory under them represents an item of the collection. Because of that, if a corresponding `groups.json | groups.yaml` file were to exist, its contents would just be an empty representation of that collection and the user would need to be careful never to edit that file. Therefore, we decided not to create that corresponding file in those cases. Following the same logic, another exception is when all the fields from a `.json | .yaml` file are split, leaving the original file as an empty object. In that case, the file would be deleted as well.

To inspect a file to see what elements can be split from it, use the `describe` command described below.  It is also useful for inspection of files created by the split operation.

## `trestle merge`

The trestle merge command is the reversal of `trestle split`. This command allows users to reverse the decomposition of a trestle model by aggregating subcomponents scattered across multiple files or directories into the parent JSON/YAML file.
To merge a model, you have to first change working directory to the root model component directory that you want to merge a sub-component model into.
The following option is required:

- `-e or --elements`: specifies the properties (JSON/YAML path) that will be merged, relative to the current working directory. This must contain at least 2 elements, where the last element is the model/sub-component to be merged into the second from last component.

For example, in the command `trestle merge -e 'catalog.metadata'`, executed in the same directory where `catalog.json` or the split `catalog` directory exists, the property `metadata` from `metadata.json` would be moved/merged into `catalog.json`. If the `metadata` model has already been split into smaller sub-component models previously, those smaller sub-components are first recusively merged into `metadata`, before merging `metadata` subcomponent into `catalog`. To specify merging every sub-component split from a component, `.*` can be used. For example, `trestle merge -e 'catalog.*'` command, issued from the directory where `catalog.json` or`catalog` directory exists, will merge every single sub-component of that catalog back into the `catalog.json`.

## `trestle describe`

This command lets users inspect model files to explore contents using an optional element path.  The command can work well in concert with `split` to show what each file contains, and probe within the contents to determine sub-components that can be extracted as separate files.

Unlike split, describe only describes the contents of a single item, so the element path may not contain wildcards (`*`) or commas.

For example, if a catalog file has been imported to `catalogs/my_catalog/catalog.json` then the commmand, `trestle describe -f catalog.json` might yield:

```yaml
#Model file catalog.json is of type catalog.Catalog and contains
uuid: 613fca2d-704a-42e7-8e2b-b206fb92b456
metadata: common.Metadata
params: None
controls: None
groups: list of 20 items of type catalog.Group
back_matter: common.BackMatter
```

Note that contents are listed even when they are empty (and therefore optional) so the full potential contents can be seen.  Also note that if an item corresponds to a list of elements, the number and type of elements is provided.  Finally, if an item is a simple string such as `id`, `uuid` or `title`, the string is shown directly up to a maximum of 100 characters.  If the string is clipped it will be indicated by `[truncated]` at the end of the string.

An element path can be specified to probe the contents, as in `trestle describe -f catalog.json -e 'catalog.metadata.roles'`.  A possible response is:

```text
Model file catalog.json at element path catalog.metadata.roles is a list of 2 items of type common.Role
```

You can also query individual elements, and elements of an element, e.g. `trestle describe -f catalog.json -e 'catalog.groups.5.controls.3'`

```yaml
# Model file catalog.json at element path catalog.groups.5.controls.3 is of type catalog.Control and contains:
id: cp-4
class_: SP800-53
title: Contingency Plan Testing
params: list of 2 items of type common.Parameter
props: list of 2 items of type common.Property
links: list of 14 items of type common.Link
parts: list of 2 items of type common.Part
controls: list of 5 items of type catalog.Control
```

(Note that the numbering starts at 0, so the `.3` corresponds to the 4th element.)

In all output from `describe` the type of the item shown corresponds to the python file and class of the corresponding OSCAL model in trestle.

If you split items off a model so they end up in a subdirectory, the original file is referred to as a "stripped" model, with parts of it stripped off and only some elements remaining.  For example, if you do `trestle split -f catalog.json -e 'catalog.metadata'` it will split off metadata from the original `catalog.json` file and place it in `catalog/metadata.json`.  If you then do `trestle describe -f catalog.json` on the new file, it will say something like:

```yaml
# Model file catalog.json is of type stripped.Catalog and contains:
uuid: 613fca2d-704a-42e7-8e2b-b206fb92b456
params: None
controls: None
groups: list of 20 items of type catalog.Group
back_matter: common.BackMatter
```

Note that the type of the file is now `stripped.Catalog` and it no longer contains `metadata`.  Even though metadata is no longer in the original `.json` file, trestle is still aware it is present in the model since it is properly placed as its own file in the subdirectory, `catalog`.

## `trestle partial-object-validate`

OSCAL objects may be extremely large. Some systems may only be able to produce partial OSCAL objects. For example, the tanium-result-to-oscal-ar task produces the `results` attribute of an `assessment-results` object.

`trestle partial-object-validate` allows the validation of any sub-element/attribute using element path.

Using the example above `trestle partial-object-validate -f results.json -e assessment-results.results`.

The file is not required to be in the trestle directory or required to be a specific file name.

### Example valid element-paths

All element paths must be absolute e.g.:
`catalog.metadata`
`catalog`
`catalog.groups`
`catalog.groups.group.controls.control.controls.control`
Remembering in the end you only care about the end type. So in this scenario `catalog.groups.group.controls.control.controls.control` is equivalent to `catalog.controls.control`.

## `trestle href`

This command changes the href of an Import in a profile and is needed when generating an SSP (system security plan) with the author tool, `ssp-generate`.
The Imports in a profile are used to load associated catalogs of controls and profiles, and must be available at the corresponding href uri.  If an imported catalog is in the trestle directory then the href should be changed with a command of the form:

```bash
trestle href -n my_profile -hr trestle://catalogs/my_catalog/catalog.json
```

Similarly, if the item imported is a profile, a corresponding href should point to a json file in the `profiles` directory.

Note that catalogs or profiles in the trestle directory are indicated by the `trestle://` prefix, followed by the path from the top level models directory to the actual
catalog file.  The profile itself, which is having its imports modified, is just indicated by its name with the `-n` option.

If the profile has more than one import, you can display the corresponding hrefs with:

```bash
trestle href -n my_profile
```

This will give a numbered list of the hrefs.  You can then change them individually by providing the corresponding item number:

```bash
trestle href -n my_profile -i 1 -hr trestle://catalogs/my_catalog/catalog.json
```

This will change the href indexed as `1` when the list was displayed.  The href's are indexed starting from 0.

The `trestle href` command can also be used to change the value back to the intended one prior to distribution of the profile.

The provided href can be of form `trestle://`, `https://`, `sftp://`, or `file:///`.  If `file:///` is used, the path provided must be absolute - and on Windows
it must include the drive letter followed by a slash.  The only time a relative path is allowed is with the `trestle://` heading.

A username and password may be embedded in the url for `https://`, and a CA certificate path will be searched from environment variables `REQUESTS_CA_BUNDLE` and `CURL_CA_BUNDLE` in that order.

Authorization for `sftp://` access relies on the user's private key being either active via `ssh-agent` or supplied via the environment variable `SSH_KEY`. In the latter case it must not require a passphrase prompt.

## `trestle assemble`

This command assembles all contents (files and directories) representing a specific model into a single OSCAL file located under `dist` folder. For example,

`$TRESTLE_BASEDIR$ trestle assemble catalog -n nist800-53`

will traverse the `catalogs/nist800-53` directory and its children and combine all data into a OSCAL file that will be written to `dist/catalogs/nist800-53.json`. Note that the parts of catalog `nist800-53` can be written in either YAML/JSON (e.g. based on the file extension), however, the output will be generated as YAML/JSON as desired. Trestle will infer the content type from the file extension and create the model representation appropriately in memory and then output in the desired format. Trestle assemble will also validate content as it assembles the files and make sure the contents are syntactically correct.

## `trestle remove`

The trestle remove command is the reversal of `trestle create -f filename.json -e element_path`, as it will remove the corresponding element from the specified file.

## `trestle validate`

Trestle validate checks the integrity of one or more OSCAL files in a number of ways.

`validate` returns a non-zero return code if there is any validation problem detected in a file.

The current list of validation modes that get checked internally are:

| Mode          | Purpose                                                               |
| ------------- | --------------------------------------------------------------------- |
| duplicates    | Detect whether disallowed duplicate uuid's are present                |
| oscal_version | Confirm that the oscal version of the file is supported               |
| refs          | Confirm that all references in responsible parties are found in roles |
| catalog       | Confirm all parameter ids in a catalog are unique                     |
| links         | Confirm referenced resources are 1:1 with resources in backmatter     |

You can validate a single model file by specifying its full path:

`trestle validate -f catalogs/my_cat/catalog.json`

or by specifying its model name and type:

`trestle validate -t catalog -n my_cat`

In addition to validating a single file you can validate all files of a given type with the `-t` option and no file name:

`trestle validate -t catalog`

And you can validate all models with the `-a` option:

`trestle validate -a`

Note that when you `Import` a file it will perform a full validation on it first, and if it does not pass validation the file cannot be imported.

By default validate will display warning messages and a message indicating the file is valid, but you can suppress those messages with the `-q --quiet` option.

The links validator is special because it always returns success that the file is valid - but it will list any inconsistencies it finds between the
references to links, and corresponding links in the backmatter.

## `trestle tasks`

Open Shift Compliance Operator and Tanium are supported as 3rd party tools.

## `trestle task xccdf-result-to-oscal-ar`

The *trestle task xccdf-result-to-oscal-ar* command facilitates transformation of XCCDF results, e.g. OpenShift Compliance Operator (OSCO) scan results, *.yaml* files into OSCAL partial results *.json* files. Specify required config parameters to indicate the location of the input and the output. Specify optional config parameters to indicate the name of the oscal-metadata.yaml file, if any, and whether overwriting of existing output is permitted.

<span style="color:green">
Example command invocation:
</span>

`$TRESTLE_BASEDIR$ trestle task xccdf-result-to-oscal-ar -c /home/user/task.config`

<span style="color:green">
Example config:
</span>

*/home/user/task.config*

```conf
[task.xccdf-result-to-oscal-ar]

input-dir =  /home/user/git/evidence/xccdf/input
output-dir = /home/user/git/evidence/oscal/output
oscal-metadata = oscal-metadata.yaml
output-overwrite = true
```

**input**

<span style="color:green">
Example input directory contents listing:
</span>

*/home/user/git/evidence/xccdf/input*

```bash
-rw-rw-r--. 1 user user  3832 Feb  2 09:36 oscal-metadata.yaml
-rw-rw-r--. 1 user user 49132 Feb  2 06:12 ssg-ocp4-ds-cis-111.222.333.444-pod.yaml
-rw-rw-r--. 1 user user 52747 Feb  2 06:41 ssg-ocp4-ds-cis-111.222.333.555-pod.yaml

```

<span style="color:green">
Example input OSCO scan result file contents (snippet):
</span>

*ssg-ocp4-ds-cis-111.222.333.444-pod.yaml*

<details markdown>

<summary>display sample</summary>

```yaml
apiVersion: v1
data:
  exit-code: '2'
  results: |
    <?xml version="1.0" encoding="UTF-8"?>
    <TestResult xmlns="https://checklists.nist.gov/xccdf/1.2" 
                id="xccdf_org.open-scap_testresult_xccdf_org.ssgproject.content_profile_cis"
                start-time="2020-08-03T02:26:26+00:00" end-time="2020-08-03T02:26:26+00:00"
                version="0.1.52"
                test-system="cpe:/a:redhat:openscap:1.3.3">
              <benchmark href="/content/ssg-ocp4-ds.xml" id="xccdf_org.ssgproject.content_benchmark_OCP-4"/>
              <title>OSCAP Scan Result</title>
              <profile idref="xccdf_org.ssgproject.content_profile_cis"/>
              <target>kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.mycorp</target>
              <target-facts>
                <fact name="urn:xccdf:fact:identifier" type="string">chroot:///host</fact>
                <fact name="urn:xccdf:fact:scanner:name" type="string">OpenSCAP</fact>
                <fact name="urn:xccdf:fact:scanner:version" type="string">1.3.3</fact>
              </target-facts>
              <target-id-ref system="https://scap.nist.gov/schema/asset-identification/1.1" name="asset0" href=""/>
              <platform idref="cpe:/a:redhat:openshift_container_platform:4.1"/>
              <platform idref="cpe:/a:machine"/>
              <set-value idref="xccdf_org.ssgproject.content_value_ocp_data_root">/kubernetes-api-resources</set-value>
              <set-value idref="xccdf_org.ssgproject.content_value_var_kube_authorization_mode">Webhook</set-value>
              <set-value idref="xccdf_org.ssgproject.content_value_var_streaming_connection_timeouts">5m</set-value>
              <rule-result idref="xccdf_org.ssgproject.content_rule_ocp_idp_no_htpasswd" time="2020-08-03T02:26:26+00:00" severity="medium" weight="1.000000">
                <result>notselected</result>
                <ident system="https://nvd.nist.gov/cce/index.cfm">CCE-84209-6</ident>
              </rule-result>
              <rule-result idref="xccdf_org.ssgproject.content_rule_accounts_restrict_service_account_tokens" time="2020-08-03T02:26:26+00:00" severity="medium" weight="1.000000">
                <result>notchecked</result>
                <message severity="info">No candidate or applicable check found.</message>
              </rule-result>
              <rule-result idref="xccdf_org.ssgproject.content_rule_accounts_unique_service_account" time="2020-08-03T02:26:26+00:00" severity="medium" weight="1.000000">
                <result>notchecked</result>
                <message severity="info">No candidate or applicable check found.</message>
              </rule-result>
              
              ...
              
           </TestResult>
kind: ConfigMap
metadata:
  annotations:
    compliance-remediations/processed: ''
    compliance.openshift.io/scan-error-msg: ''
    compliance.openshift.io/scan-result: NON-COMPLIANT
    openscap-scan-result/node: 111.222.333.444
  creationTimestamp: '2020-08-03T02:26:34Z'
  labels:
    compliance-scan: ssg-ocp4-ds-cis
  name: ssg-ocp4-ds-cis-111.222.333.444-pod
  namespace: openshift-compliance
  resourceVersion: '22693328'
  selfLink: 
    /api/v1/namespaces/openshift-compliance/configmaps/ssg-ocp4-ds-cis-111.222.333.444-pod
  uid: 1da3ea81-0a25-4512-ad86-7ac360246b5d

```

</details>
<br>

<span style="color:green">
Example input OSCAL metadata file contents:
</span>

*oscal-metadata.yaml*

<details markdown>

<summary>display sample</summary>

```yaml
ssg-ocp4-ds-cis-111.222.333.444-pod:
  locker: https://github.mycorp.com/degenaro/evidence-locker
  namespace: xccdf
  benchmark: CIS Kubernetes Benchmark
  subject-references:
    component:
      uuid-ref: 56666738-0f9a-4e38-9aac-c0fad00a5821
      type: component
      title: Red Hat OpenShift Kubernetes
    inventory-item:
      uuid-ref: 46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e
      type: inventory-item
      title: Pod
      properties:
        target: 
          kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.mycorp
        target-ip: 111.222.333.444
        cluster-name: ROKS-OpenSCAP-1
        cluster-type: openshift
        cluster-region: us-south

ssg-rhel7-ds-cis-111.222.333.444-pod:
  locker: https://github.mycorp.com/degenaro/evidence-locker
  namespace: xccdf
  benchmark: CIS Kubernetes Benchmark
  subject-references:
    component:
      uuid-ref: 89cfe7a7-ce6b-4699-aa7b-2f5739c72001
      type: component
      title: RedHat Enterprise Linux 7.8
    inventory-item:
      uuid-ref: 46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e
      type: inventory-item
      title: VM
      properties:
        target: 
          kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.mycorp
        target-ip: 111.222.333.444
        cluster-name: ROKS-OpenSCAP-1
        cluster-type: openshift
        cluster-region: us-south
```

</details>

**metadata format**

The *oscal-metadata.yaml* file comprises one or more mappings. Below is shown the
format of a single mapping. The items in angle brackets are to be replaced with
desired values for augmenting the produced OSCAL.

The mapping whose *name* matches the `[metadata][name]` in the evidence for the
corresponding embedded XML, if any, will be used for augmenting the produced
OSCAL.

```yaml
name:
  locker: <locker>
  namespace: <namespace>
  benchmark: <benchmark>
  subject-references:
    component:
      uuid-ref: <uuid-ref-component>
      type: <component-type>
      title: <component-title>
    inventory-item:
      uuid-ref: <uuid-ref-inventory-item>
      type: <inventory-item-type>
      title: <inventory-item-title>
      properties:
        target: <target>
        cluster-name: <cluster-name>
        cluster-type: <cluster-type>
        cluster-region: <cluster-region>
```

**output**

<span style="color:green">
Example output directory contents listing:
</span>

*/home/user/git/evidence/oscal/output*

```bash
-rw-rw-r--. 1 user user 49132 Feb  3 10:59 ssg-ocp4-ds-cis-111.222.333.444-pod.json
-rw-rw-r--. 1 user user 52747 Feb  3 10:59 ssg-ocp4-ds-cis-111.222.333.555-pod.json

```

<span style="color:green">
Example output OSCAL Observations file contents (snippet):
</span>

*ssg-ocp4-ds-cis-111.222.333.444-pod.json*

<details markdown>

<summary>display sample</summary>

```json
{
  "observations": [
    {
      "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
      "title": "xccdf_org.ssgproject.content_rule_ocp_idp_no_htpasswd",
      "description": "xccdf_org.ssgproject.content_rule_ocp_idp_no_htpasswd",
      "props": [
        {
          "name": "benchmark",
          "ns": "dns://osco",
          "class": "source",
          "value": "CIS Kubernetes Benchmark"
        }
      ],
      "methods": [
        "TEST-AUTOMATED"
      ],
      "subjects": [
        {
          "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "type": "component",
          "title": "Red Hat OpenShift Kubernetes"
        },
        {
          "uuid-ref": "46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e",
          "type": "inventory-item",
          "title": "Pod",
          "props": [
            {
              "name": "target",
              "ns": "dns://osco",
              "class": "inventory-item",
              "value": "kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.mycorp"
            },
            {
              "name": "target-ip",
              "ns": "dns://osco",
              "class": "inventory-item",
              "value": "111.222.333.444"
            },
            {
              "name": "cluster-name",
              "ns": "dns://osco",
              "class": "inventory-item",
              "value": "ROKS-OpenSCAP-1"
            },
            {
              "name": "cluster-type",
              "ns": "dns://osco",
              "class": "inventory-item",
              "value": "openshift"
            },
            {
              "name": "cluster-region",
              "ns": "dns://osco",
              "class": "inventory-item",
              "value": "us-south"
            }
          ]
        }
      ],
      "relevant-evidence": [
        {
          "href": "https://github.mycorp.com/degenaro/evidence-locker",
          "description": "Evidence location.",
          "props": [
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.ssgproject.content_rule_ocp_idp_no_htpasswd"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2020-08-03T02:26:26+00:00"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "notselected"
            }
          ]
        }
      ]
    }
  ]
}
```

</details>

## `trestle task tanium-result-to-oscal-ar`

The *trestle task tanium-result-to-oscal-ar* command facilitates transformation of Tanuim reports, each
input file comprising individual lines consumable as *json*, into OSCAL partial results *.json* files.
Specify required config parameters to indicate the location of the input and the output.
Specify optional config parameter *output-overwrite* to indicate whether overwriting of existing output is permitted.
Specify optional config parameter *timestamp* as ISO 8601 formated string (e.g., 2021-02-24T19:31:13+00:00) to override the timestamp attached to each Observation.

<span style="color:green">
Example command invocation:
</span>

`$TRESTLE_BASEDIR$ trestle task tanium-result-to-oscal-ar -c /home/user/task.config`

<span style="color:green">
Example config:
</span>

*/home/user/task.config*

```conf
[task.tanium-result-to-oscal-ar]

input-dir =  /home/user/git/compliance/tanium/input
output-dir = /home/user/git/compliance/oscal/output
output-overwrite = true
```

**input**

<span style="color:green">
Example input directory contents listing:
</span>

*/home/user/git/compliance/tanium/input*

```bash
-rw-rw-r--. 1 degenaro degenaro 1830 Mar  7 08:23 Tanium.comply-nist-results

```

*Tanium.comply-nist-results*

<details markdown>

<summary>display sample</summary>

```json
{
  "IP Address": "fe80::3cd5:564b:940e:49ab",
  "Computer Name": "cmp-wn-2106.demo.tanium.local",
  "Comply - JovalCM Results[c2dc8749]": [
    {
      "Benchmark": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
      "Benchmark Version": "1.5.0.1",
      "Profile": "Windows 10 - NIST 800-53",
      "ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
      "Result": "pass",
      "Custom ID": "800-53: IA-5",
      "Version": "version: 1"
    }
  ],
  "Count": "1",
  "Age": "600"
}
```

```json
{
  "IP Address": "10.8.69.11",
  "Computer Name": "",
  "Comply - JovalCM Results[c2dc8749]": [
    {
      "Benchmark": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
      "Benchmark Version": "1.5.0.1",
      "Profile": "Windows 10 - NIST 800-53",
      "ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
      "Result": "pass",
      "Custom ID": "800-53: IA-5",
      "Version": "version: 1"
    }
  ],
  "Count": "1",
  "Age": "600"
}
```

```json
{
  "IP Address": "10.8.69.11",
  "Computer Name": "cmp-wn-2106.demo.tanium.local",
  "Comply - JovalCM Results[c2dc8749]": [
    {
      "Benchmark": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
      "Benchmark Version": "1.5.0.1",
      "Profile": "Windows 10 - NIST 800-53",
      "ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
      "Result": "fail",
      "Custom ID": "800-53: IA-5",
      "Version": "version: 1"
    }
  ],
  "Count": "1",
  "Age": "600"
}
```

```json
{
  "IP Address": "10.8.69.11",
  "Computer Name": "cmp-wn-2106.demo.tanium.local",
  "Comply - JovalCM Results[c2dc8749]": [
    {
      "Benchmark": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
      "Benchmark Version": "1.5.0.1",
      "Profile": "Windows 10 - NIST 800-53",
      "ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.4_L1_Ensure_Minimum_password_length_is_set_to_14_or_more_characters",
      "Result": "pass",
      "Custom ID": "800-53: IA-5",
      "Version": "version: 1"
    }
  ],
  "Count": "1",
  "Age": "600"
}
```

</details>

**output**

<span style="color:green">
Example output directory contents listing:
</span>

*/home/user/git/compliance/oscal/output*

```bash
-rw-rw-r--. 1 degenaro degenaro 6479 Mar  7 08:25 Tanium.oscal.json

```

*Tanium.oscal.json*

<details markdown>

<summary>display sample</summary>

```json
{
  "results": [
    {
      "uuid": "0ed0791e-5454-4d07-919f-15a0d806a5a8",
      "title": "Tanium",
      "description": "Tanium",
      "start": "2021-04-13T00:16:20.000+00:00",
      "local-definitions": {
        "inventory-items": [
          {
            "uuid": "da8b87f6-2068-415f-94bb-e14e31b4f5c2",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2106.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "fe80::3cd5:564b:940e:49ab",
                "class": " inventory-item"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "value": "Windows 10",
                "class": " inventory-item"
              }
            ]
          },
          {
            "uuid": "f3ab87b2-70c1-4332-991e-c003d4314c0b",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "10.8.69.11",
                "class": " inventory-item"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "value": "Windows 10",
                "class": " inventory-item"
              }
            ]
          }
        ]
      },
      "reviewed-controls": {
        "control-selections": [
          {}
        ]
      },
      "observations": [
        {
          "uuid": "b3250b66-fe6f-4ac0-be99-cb4ff093dc31",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "da8b87f6-2068-415f-94bb-e14e31b4f5c2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-13T00:16:20.000+00:00"
        },
        {
          "uuid": "5ae9c133-c32d-44c5-b52e-5af4513cb94a",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f3ab87b2-70c1-4332-991e-c003d4314c0b",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-13T00:16:20.000+00:00"
        },
        {
          "uuid": "8d021edc-176e-4373-a3c4-a19e954c1e4d",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "value": "fail",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f3ab87b2-70c1-4332-991e-c003d4314c0b",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-13T00:16:20.000+00:00"
        },
        {
          "uuid": "36aa7551-d047-4f4a-9853-6ac63cfc9e48",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.4_L1_Ensure_Minimum_password_length_is_set_to_14_or_more_characters",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.4_L1_Ensure_Minimum_password_length_is_set_to_14_or_more_characters",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f3ab87b2-70c1-4332-991e-c003d4314c0b",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-13T00:16:20.000+00:00"
        }
      ],
      "findings": [
        {
          "uuid": "ba4e264f-0aee-4ead-9ee3-6161c5cc4ecb",
          "title": "800-53: IA-5",
          "description": "800-53: IA-5",
          "target": {
            "type": "objective-id",
            "id-ref": "800-53: IA-5",
            "props": [
              {
                "name": "profile",
                "ns": "dns://tanium",
                "value": "NIST 800-53",
                "class": "source"
              },
              {
                "name": "id-ref",
                "ns": "dns://tanium",
                "value": "800-53: IA-5",
                "class": "source"
              },
              {
                "name": "result",
                "ns": "dns://xccdf",
                "value": "FAIL",
                "class": "STRVALUE"
              }
            ],
            "status": "not-satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "b3250b66-fe6f-4ac0-be99-cb4ff093dc31"
            },
            {
              "observation-uuid": "5ae9c133-c32d-44c5-b52e-5af4513cb94a"
            },
            {
              "observation-uuid": "8d021edc-176e-4373-a3c4-a19e954c1e4d"
            },
            {
              "observation-uuid": "36aa7551-d047-4f4a-9853-6ac63cfc9e48"
            }
          ]
        }
      ]
    }
  ]
}
```

</details>

## `trestle task xlsx-to-oscal-cd`

The *trestle task xlsx-to-oscal-cd* command facilitates transformation of an excel spreadsheet into an OSCAL component-definition.json file.
Specify in the config:

<ul>
<li> location of catalog file
<li> location of spreadsheet file
<li> work sheet name in the spreadsheet file
<li> output directory to write the component-definition.json file
<li> whether or not to overwrite an existing component-definition.json file
<li> the organization name
<li> the organization remarks
<li> the namespace
<li> comma separated mappings from name to class
<li> the catalog URL
<li> the catalog title
</ul>

<span style="color:green">
Example command invocation:
</span>

`$TRESTLE_BASEDIR$ trestle task xlsx-to-oscal-cd -c /home/user/task-xlsx-to-oscal-cd.config`

<span style="color:green">
Example config:
</span>

*/home/user/task-xlsx-to-oscal-cd.config*

```conf
[task.xlsx-to-oscal-cd]

catalog-file = nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json
spread-sheet-file = /home/user/compliance/data/spread-sheet/good.xlsx
work-sheet-name = example_best_practices_controls
output-dir = /home/user/compliance/data/tasks/xlsx/output
output-overwrite = true

org-name = International Business Machines
org-remarks = IBM
namespace = https://oscal-compass.github.io/compliance-trestle/schemas/oscal/cd/ibm-cloud
property-name-to-class = goal_name_id:scc_goal_name_id, goal_version:scc_goal_version
catalog-url = https://github.com/usnistgov/oscal-content/blob/master/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json
catalog-title = NIST Special Publication 800-53 Revision 4
```

**catalog-file**

<span style="color:green">
Example catalog-file:
</span>

[nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json](https://github.com/usnistgov/oscal-content/blob/58af5c83ad7ab5620809c5701877a4b959516d25/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json)

**spread-sheet-file**

<span style="color:green">
Example spread-sheet-file:
</span>

[/home/user/compliance/data/spread-sheet/good.xlsx](https://github.com/oscal-compass/compliance-trestle/tree/main/tests/data/spread-sheet/good.xlsx)

**output**

<span style="color:green">
Example component-definition.json:
</span>

[/home/user/compliance/data/tasks/xlsx/output/component-definition.json](https://github.com/oscal-compass/compliance-trestle/tree/main/tests/data/tasks/xlsx/output/component-definition.json)

### spreadsheet to component definition mapping

<details markdown>

<summary>display mapping table</summary>

<style>
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
th, td {
  padding: 5px;
}
</style>

<table>
<tr>
<th>spreadsheet column name
<th>component definition path
<th>comments
<tr>
<td>ControlId
<td><ul>
    <li>implemented_requirement.property[name='goal_name_id'].value
    </ul>
<td><ul>
    <li>only used if column 'goal_name_id' is empty
    </ul>
<tr>
<td>ControlText
<td><ul>
    <li>implemented_requirement.property[name='goal_name_id'].remarks
    </ul>
<td><ul>
    <li>transformation code replaces "Check whether" with "Ensure" in text
    </ul>
<tr>
<td>Nist Mappings
<td><ul>
    <li>implemented_requirement.description
    </ul>
<td><ul>
    <li>heading may span multiple columns
    <li>one value expected per column
    <li>each entry is separated into control + statements (if any)
    </ul>
<tr>
<td>ResourceTitle
<td><ul>
    <li>component.title    
    <li>component.description
    <li>component.control-implementation.description + {text}
    </ul>
<td><ul>
    </ul>
<tr>
<td>goal_name_id
<td><ul>
    <li>implemented_requirement.property[name='goal_name_id'].value
    </ul>
<td><ul>
    </ul>
<tr>
<td>Version
<td><ul>
    <li>implemented_requirement.property[name='goal_version'].value
    </ul>
<td><ul>
    <li>Value from spreadsheet is not currently used. 
    <li>Value '1.0' is hard coded.
    </ul>
<tr>
<td>Parameter [optional parameter]
<td><ul>
    <li>implemented_requirement.set_parameter.param_id
    </ul>
<td><ul>
    <li>The expected text is in two parts separated by '\n'.
    <li>The text following the '\n' is the value used.
    </ul>
<tr>
<td>Values [alternatives]
<td><ul>
    <li>implemented_requirement.set_parameter.values
    </ul>
<td><ul>
    <li>The expected text is of the following format: 
    <li>v0, [v1, v2...]
    <li>The value v0 is used.
    </ul>
</table>
</details>

## `trestle task xlsx-to-oscal-profile`

The *trestle task xlsx-to-oscal-profile* command facilitates transformation of an excel spreadsheet into an OSCAL profile.json file.
Specify in the config:

<ul>
<li> the href URL of the spreadsheet
<li> file system location of spreadsheet file
<li> work sheet name in the spreadsheet file
<li> output directory to write the profile.json file
<li> whether or not to overwrite an existing profile.json file
<li> the profile title
</ul>

<span style="color:green">
Example command invocation:
</span>

`$TRESTLE_BASEDIR$ trestle task xlsx-to-oscal-profile -c /home/user/task-xlsx-to-oscal-profile.config`

<span style="color:green">
Example config:
</span>

*/home/user/task-xlsx-to-oscal-profile.config*

```conf
[task.xlsx-to-oscal-profile]

spread-sheet-url = https://github.mycorp.com/spread-sheets/good.xlsx
spread-sheet-file = /home/user/compliance/data/spread-sheet/good.xlsx
work-sheet-name = example_best_practices_controls
output-dir = /home/user/compliance/data/tasks/xlsx/output
output-overwrite = true

profile-title = IBM Best Practices SCC GOALS
```

**spread-sheet-file**

<span style="color:green">
Example spread-sheet-file:
</span>

[/home/user/compliance/data/spread-sheet/good.xlsx](https://github.com/oscal-compass/compliance-trestle/tree/main/tests/data/spread-sheet/good.xlsx)

**output**

<span style="color:green">
Example profile.json:
</span>

[/home/user/compliance/data/tasks/xlsx/output/profile.json](https://github.com/oscal-compass/compliance-trestle/tree/main/tests/data/tasks/xlsx/output/profile.json)
