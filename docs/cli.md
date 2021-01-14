# Trestle CLI

## Overview & Usecases

The trestle CLI has two primary usecases by design:

- Tooling to generate and manipulate OSCAL files when used directly by and end user. The objective here is to reduce the complexity of creating and editing workflows. E.g. commands such as: `trestle import`, `trestle create`, `trestle add`, `trestle split`, `trestle merge`.
- The trestle CLI as an automation tool, which, by design is likely to occur as part of a CI-CD pipeline e.g. `trestle validate`, `trestle tasks`.

To support each of these usecases trestle, inspired by programming languages such as `python` and `go` as well as projects such as `auditree` has created an opinionated directory structure to manage OSCAL documents.

## Opinionated directory structure

Trestle relies on an opinionated directory structure, similar to `git` or `go`, to manage the workflow. Unlike git commands are not solely restricted to working within an initialized directory tree, however, it is most likely.

The directory structure setup by trestle has three major elements

- A `.trestle` hidden folder.
- A `dist` folder.
- Folders for each of the OSCAL schemas.

The outline of the schema is below:

```
.
├── .trestle
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

`.trestle` directory is a special directory containing various trestle artefacts to help run various other commands. Examples include configuation files, caches and templates.

The bulk of the folder structure is used to represent each of the *top level schemas* or *top level models* such as `catalogs` and `profiles`. For each of these directories the following root structure is maintained.

```

├── .trestle
└── TOP_LEVEL_MODEL_PLURAL
    └── NAME_OF_MODEL_INSTANCE
        └── TOP_LEVEL_MODEL_NAME.{json,yaml,yml}

```

which appears, for a catalog a user decides is titled nist-800-53 as:

```
├── .trestle
└── catalogs
    └── nist-800-53
        └── catalog.json

```

`dist` directory will contain the assembled version of the models located on the source model directories (at the project root level) which are: `catalogs`, `profiles`, `target-definitions`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` and `plan-of-action-and-milestones`. The assumption is that each of the OSCAL files within this folder are ready to be read by external 3rd party tools.

### Support for subdivided document structures

The files constructed by oscal can run into the tens of thousands of lines of yaml or formated json. At this size the
files become completely unmanageable for users. To combat this trestle can `trestle split` file in the file system and merge those split files together.

Directory structures such as the one below can represent oscal document structures. Users are strongly encourage to rely on split and merge to code these structures.

```
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

## `trestle init`

This command will create a trestle project in the current directory with necessary directory structure and trestle artefacts. For example, if we run `trestle init` in a directory, it will create a directory structure like below for different artefacts:

```
.
├── .trestle
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

`.trestle` directory is a special directory containing various trestle artefacts to help run various other commands.

`dist` directory will contain the merged or assembled version of the models located on the source model directories (at the project root level) which are: `catalogs`, `profiles`, `target-definitions`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` and `plan-of-action-and-milestones`.

Notice that trestle is a highly opinionated tool and, therefore, the names of the files and directories that are created by any of the `trestle` commands and subcommands MUST NOT be changed manually.

## `trestle create`

This command will create an initial directory structure for various OSCAL models including sample JSON files and subdirectories representing parts of the model. For example, `trestle create catalog -o nist800-53` will create a directory structure of a sample catalog like below.

```
.
├── .trestle
├── dist 
│   └── catalogs
│       └── nist800-53.json
└── catalogs
    └── nist800-53
        ├── catalog.json
        └── catalog        
            └── groups
                ├── 00000__group.json            
                ├── 00000__group
                │   └── controls
                │       ├── 00000__control.json
                │       └── 00001__control.json
                ├── 00001__group
                └── 00001__group
                    └── controls
                        ├── 00000__control.json
                        ├── 00001__control.json
                        └── 00002__control.json
...
```

Notice that subdirectories under a trestle directory model such as `$TRESTLE_BASEDIR/catalogs/nist800-53/catalog` and `$TRESTLE_BASEDIR/catalogs/nist800-53/catalog/groups` represent a decomposition of the original file. The subdirectory `catalog` means that the original `catalog.json` was split and the split parts are inside the `catalog` directory (in this case `groups`).
Every subdirectory in a trestle directory model should have a corresponding `.json` or `.yaml` file with the same name. Exceptions to that rule are named fields (dicts) such as `catalog.metadata.responsible-parties` and array fields such as `catalog.groups`. When those subcomponents are split/expanded each file or subdirectory under them represents an item of the collection. Because of that, if a corresponding `groups.json | groups.yaml` file were to exist, its contents would just be an empty representation of that collection and the user would need to be careful never to edit that file. Therefore, we decided not to create that corresponding file in those cases. Following the same logic, another exception is when all the fields from a `.json | .yaml` file are split, leaving the original file as an empty object. In that case, the file would be deleted as well.

The following subcommands are currently supported:

- `trestle create catalog`: creates a directory structure of a sample OSCAL catalog model under the `catalogs` folder. This folder can contain multiple catalogs.
- `trestle create profile`: creates a directory structure of a sample OSCAL profile model under the `profiles` folder. This folder can contain multiple profiles.
- `trestle create target-definition`: creates a directory structure of a sample target-definition model under the `target-definitions` folder. This folder can contain multiple target-definitions.
- `trestle create component-definition`: creates a directory structure of a sample component-definition model under the `component-definitions` folder. This folder can contain multiple component-definitions.
- `trestle create system-security-plan`: creates a directory structure of a sample system-security-plan model under the `system-security-plans` folder. This folder can contain multiple system-security-plans.
- `trestle create assessment-plan`: creates a directory structure of a sample assessment-plan under the `assessment-plans` folder. This folder can contain multiple assessment-plans.
- `trestle create assessment-result`: creates a directory structure of a sample assessment-result under the `assessment-results` folder. This folder can contain multiple assessment-results.
- `trestle create plan-of-action-and-milestone`: creates a directory structure of a sample plan-of-action-and-milestone under the `plan-of-action-and-milestones` folder. This folder can contain multiple plan-of-action-and-milestones.

The following options are supported:

- `-o or --output`: specifies the name/alias of a model. It is used as the prefix for the output filename under the `dist` directory and for naming the source subdirectories under  `catalogs`, `profiles`, `target-definitions`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` or `plan-of-action-and-milestones`.

The user can edit the parts of the generated OSCAL model by modifying the sample content in those directories.

The initial level of decomposition of each type of model varies according to the model type.
This default or reference decomposition behaviour can be changed by modifying the rules in a `.trestle/config file`. These rules can be written as a sequence of `trestle split` commands.

## `trestle import`

This command allows users to import existing OSCAL files so that they can be managed using trestle. For example `trestle import -f existing_catalog.json -o my_existing_catalog` will import `existing_catalog.json` into a new folder under `catalogs` as shown below:

```
.
├── .trestle
├── dist 
│   └── catalogs
│       ├── my_existing_catalog.json 
│       └── nist800-53.json 
└── catalogs
    ├── my_existing_catalog
    │   ├── catalog.json
    │   └── catalog
    │       └── groups
    │           ├── 00000__group.json
    │           └── 00000__group
    │               └── controls
    │                   ├── 00000__control.json
    │                   └── 00001__control.json
    └── nist800-53
        ├── catalog.json
        └── catalog        
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
                        ├── 00001__control.json
...
```

The following options are supported:

- `-f or --file`: specifies the path of an existing OSCAL file.
- `-o or --output`: specifies the name/alias of a model. It is used as the prefix for the output filename under the `dist` directory and for naming the source subdirectories under  `catalogs`, `profiles`, `target-definitions`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` or `plan-of-action-and-milestones`.

The import subcommand can determine the type of the model that is to be imported by the contents of the file.

Note that the import command will decompose the file according to the default decomposing rules already mentioned in the `trestle create` section. Similarly to `trestle create`, the user can increase the level of decomposition by using `trestle split` command.

## `trestle replicate`

This command allows users to replicate a certain OSCAL model (file and directory structure). For example `trestle replicate catalog -i cat1 -o cat11` will replicate the Catalog cat1 into `cat11` directory. It can also regenerate all the UUIDs as required.

## `trestle split`

This command allows users to further decompose a trestle model into additional subcomponents.

The following options are currently supported:

- `-f or --file`: this option specifies the file path of the json/yaml file containing the elements that will be split.
- `-e or --elements`: specifies the model subcomponent element(s) (JSON/YAML property path) that is/are going to be split. Multiple elements can be specified at once using a comma-separated value. If the element is of JSON/YAML type array list and you want trestle to create a separate subcomponent file per array item, the element needs to be suffixed with `.*`. If the suffix is not specified, split will place all array items in only one separate subcomponent file. If the element is a collection of JSON Schema additionalProperties and you want trestle to create a separate subcomponent file per additionalProperties item, the element also needs to be suffixed with `.*`. Similarly, not adding the suffix will place all additionalProperties items in only one separate subcomponent file.

In the near future, `trestle split` should be smart enough to figure out which json/yaml files contain the elemenets you want to split. In that case, the `-f` option would be deprecated and only the `-e` option will be required. In order to determine which elements the user can split at the level the command is being executed, the following command can be used:
`trestle split -l` which would be the same as `trestle split --list-available-elements`

## `trestle merge`

The trestle merge command is the reversal of `trestle split`. This command allows users to reverse the decomposition of a trestle model by aggregating subcomponents scattered across multiple files or directories into the parent JSON/YAML file.
To merge a model, you have to first change working directory to the root model component directory that you want to merge a sub-component model into.
The following option is required:

- `-e or --elements`: specifies the properties (JSON/YAML path) that will be merged, relative to the current working directory. This must contain at least 2 elements, where the last element is the model/sub-component to be merged into the second from last component.

For example, in the command `trestle merge -e catalog.metadata`, executed in the same directory where `catalog.json` or splitted `catalog` directory exists, the property `metadata` from `metadata.json` or `metadata.yaml` would be moved/merged into `catalog.json`. If the `metadata` model has already been split into smaller sub-component models previously, those smaller sub-components are first recusively merged into `metadata`, before merging `metadata` subcomponent into `catalog.json`. To specify merging every sub-component split from a component, `.*` can be used. For example, `trestle merge -e catalog.*` command, issued from the directory where `catalog.json` or`catalog` directory exists, will merge every single sub-component of that catalog back into the `catalog.json`. 

## `trestle assemble`

This command assembles all contents (files and directories) representing a specific model into a single OSCAL file located under `dist` folder. For example,

> `$TRESTLE_BASEDIR$ trestle assemble catalog -i nist800-53`

will traverse the `catalogs/nist800-53` directory and its children and combine all data into a OSCAL file that will be written to `dist/catalogs/nist800-53.json`. Note that the parts of catalog `nist800-53` can be written in either YAML/JSON/XML (e.g. based on the file extension), however, the output will be generated as YAML/JSON/XML as desired. Trestle will infer the content type from the file extension and create the model representation appropriately in memory and then output in the desired format. Trestle assemble will also validate content as it assembles the files and make sure the contents are syntactically correct.

## `trestle add`

This command allows users to add an OSCAL model to a subcomponent in source directory structure of the model. For example,

> `$TRESTLE_BASEDIR/catalogs/nist800-53$ trestle add -f ./catalog.json -e catalog.metadata.roles `

will add the following property under the `metadata` property for a catalog that will be written to the appropriate file under `catalogs/nist800-53` directory:

```
"roles": [
  {
    "id": "REPLACE_ME",
    "title": "REPLACE_ME"
  }
```

Default values for mandatory datatypes will be like below. All UUID's will be populated by default whether or not they are mandatory.

```
- DateTime: <Current date-time>
- Boolean: False
- Integer: 0 
- String: REPLACE_ME
- Float/Double: 0.00
- Id field: Auto generated UUID
```

## `trestle remove`

The trestle remove command is the reversal of `trestle add`.

## `trestle validate`

Trestle validate is designed to perform a function to ensure integrity of a set of oscal files. This can be as simple as
a schema validation within a single file or as complex as ensuring the integrity of a 'stack' of oscal files including potentially
remote system state.

Trestle validate the form \`trestle validate -f FILE -i SPECIFIC\_ITEM\_OR\_VALUE, --mode {duplicate or similar}

and returns a non-zero return code on a validation failure. Mode is a list of validation modes that will be implemented as shown in the table below.

| Mode       | Purpose                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------- |
| duplicates | Identify if duplicate values exist for a given json key for example `trestle validate -f catalog.json -i uuid --mode duplicate` |

## `trestle tasks`
