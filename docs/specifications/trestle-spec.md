# Trestle CLI Specifications (v0.1.0)

## Table of Contents

- [Purpose](#purpose)
- [Users](#users)
- [Scope](#scope)
- [Trestle commands](#trestle-commands)
  - [Draft commands](#draft-commands)
- [Future work](#future-work)
  - [Deploy commands](#deploy-commands)
  - [Monitor commands](#monitor-commands)
  - [Reporting commands](#reporting-commands)

## Purpose

This document contains detail specifications of the Trestle CLI commands.

Trestle offers various commands to simplify operations at different steps in compliance management and reporting.

Trestle assumes all security and compliance specifications and requirements are expressed in OSCAL format.

## Users

Trestle aims at compliance engineers who are familiar with various software development tools such as Git, CI/CD and command line tools.

Users of Trestle are also expected to be comfortable with editing OSCAL files in YAML/JSON/XML format.

## Scope

The scope of this document is to describe the purpose and expected behaviour of various trestle commands for manipulating OSCAL documents ONLY. This will not be all of trestle. Workflow commands will be subsequent / expanded on this.

## Definitions

- **trestle project directory**: directory containing a `.trestle` folder as the result of `trestle init`. Also referred as `$TRESTLE_BASEDIR` in this document.
- **trestle model directory**: directory representing the source folder for manipulating an OSCAL model in a trestle project. This type of directory is usually created by commands such as `trestle create` and `trestle import`. Examples of a trestle model directory named `mymodel` under different types of models are:
  - `$TRESTLE_BASEDIR/catalogs/mymodel`
  - `$TRESTLE_BASEDIR/profiles/mymodel`
  - `$TRESTLE_BASEDIR/target-definitions/mymodel`
  - `$TRESTLE_BASEDIR/component-definitions/mymodel`
  - `$TRESTLE_BASEDIR/system-security-plans/mymodel`
  - `$TRESTLE_BASEDIR/assessment-plans/mymodel`
  - `$TRESTLE_BASEDIR/assessment-results/mymodel`
  - `$TRESTLE_BASEDIR/plan-of-action-and-milestones/mymodel`

## Trestle Commands

### Draft Commands

For the draft phase of compliance engineering, trestle provides the following commands to facilitate various draft related operations.

#### `trestle init`

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

#### `trestle create`

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

#### *Catalog default decomposition*

For `catalog`, the inital sample content is broken down as shown below:

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
                ├── 00001__group.json                
                └── 00001__group
                    └── controls
                        ├── 00000__control.json
                        └── 00001__control.json
...
```

- a `catalog.json` file containing a catalog JSON object without the `catalog.groups` property. Also, because the catalog is decomposed, there's a subdirectory called `catalog` at the same level as `catalog.json`.
- `catalog.groups` property is broken down into a subdirectory called `groups` under `catalog`.
- For each group in the `catalog.groups` array list, an indexed json file is created containing a group JSON object without the `group.controls` property. Also, because each group is further decomposed, an indexed subdirectory is created at the same level as the indexed file.
- `catalog.groups[i].controls` property in each group is broken down into subdirectories called `controls` under each indexed group subdirectory.
- For each control in a `catalog.groups[i].controls` array list, an indexed JSON file is created representing the contents of a control.

#### *Profile default decomposition*

For `profile`, the initial sample content is not broken down by default as shown below.

```
.
├── .trestle
├── dist
│   └── profiles
│       └── profile-myprofile.json
└── profiles
    └── profile-myprofile
        └── profile.json
...
```

- `profile.json` file has the content of the OSCAL profile.

#### *Target-definition default decomposition*

For `target-definition`, the initial sample content is broken down as shown below:

```
.
├── .trestle
├── dist
│   └── target-definitions
│       └── mycloudservices-example.json
└── target-definitions
    └── mycloudservices-example
        ├── target-definition.json
        ├── target-definition
            └── targets
                ├── 74ccb93f-07d1-422a-a43d-3c97bae4c514__target.json
                ├── 74ccb93f-07d1-422a-a43d-3c97bae4c514__target
                │   └── target-control-implementations
                │       ├── 00000__target-control-implementation.json
                │       └── 00001__target-control-implementation.json
                ├── 953a2878-2a21-4a0f-a9fa-3a37b61b9df8__target.json
                └── 953a2878-2a21-4a0f-a9fa-3a37b61b9df8__target
                    └── target-control-implementations
                        ├── 00000__target-control-implementation.json
                        └── 00001__target-control-implementation.json
...
```

- a `target-definition.json` file containing a target definition JSON object except for the `target-definition.targets` property. Also, because the target definition is decomposed, there's a subdirectory called `target-definition` at the same level as `target-definition.json`.
- `target-definition.targets` property is broken down into a subdirectory named `targets` under `target-definition`.
- For each target in the `target-definition.targets` uniquely identified by a property labelled with the target's uuid, a filename named after `{{uuid}}__target` us created containing a target JSON object without the `target.target-control-implementations` property. Also, because each target is further decomposed, a subdirectory named after  `{{uuid}}__target` is created at the same level as its corresponding file.
- `target-definition.components.{{uuid}}.target-control-implementations` property is broken down into subdirectories called `target-control-implementations` under each `{{uuid}}__target` folder.
- For each target control implementation in a `target-definition.components.{{uuid}}.target-control-implementations` array list, an indexed JSON file is created representing the contents of a target control implementation.

At the moment, the initial sample content for the other model types (`component-definition`, `system-security-plan`, `assessment-plan`, `assessment-result` and `plan-of-action-and-milestone`) is TBD.

The user can increase the level of decomposition by using `trestle split` command.

#### `trestle import`

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

#### `trestle replicate`

This command allows users to replicate a certain OSCAL model (file and directory structure). For example `trestle replicate catalog -i cat1 -o cat11` will replicate the Catalog cat1 into `cat11` directory. It can also regenerate all the UUIDs as required.

#### `trestle split`

This command allows users to further decompose a trestle model into additional subcomponents.

The following options are currently supported:

- `-f or --file`: this option specifies the file path of the json/yaml file containing the elements that will be split.
- `-e or --elements`: specifies the model subcomponent element(s) (JSON/YAML property path) that is/are going to be split. Multiple elements can be specified at once using a comma-separated value. If the element is of JSON/YAML type array list and you want trestle to create a separate subcomponent file per array item, the element needs to be suffixed with `.*`. If the suffix is not specified, split will place all array items in only one separate subcomponent file. If the element is a collection of JSON Schema additionalProperties and you want trestle to create a separate subcomponent file per additionalProperties item, the element also needs to be suffixed with `.*`. Similarly, not adding the suffix will place all additionalProperties items in only one separate subcomponent file.

In the near future, `trestle split` should be smart enough to figure out which json/yaml files contain the elemenets you want to split. In that case, the `-f` option would be deprecated and only the `-e` option will be required. In order to determine which elements the user can split at the level the command is being executed, the following command can be used:
`trestle split -l` which would be the same as `trestle split --list-available-elements`

#### Example

To illustrate how this command could be used consider a catalog model named `nist800-53` that was created via `trestle create catalog -o nist800-53` or imported via `trestle import -f nist800-53.json`.

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
...
```

**Step 1**: A user might want to decompose the `metadata` property from `catalog.json`. The command to achieve that would be:

`$TRESTLE_BASEDIR/catalogs/nist800-53$ trestle split -f catalog.json -e 'catalog.metadata'`.

This would create a `metadata.json` file under `catalog` subdirectory and move the whole `metadata` property/section from `catalog.json` to `catalog/metadata.json` as below:

```
.
├── .trestle
├── dist 
│   └── catalogs
│       └── nist800-53.json 
└── catalogs
    └── nist800-53
        ├── catalog.json      #removed metadata property from this file
        └── catalog
            ├── metadata.json     #contains the metadata JSON object        
            └── groups        
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

The future version of this command would be:

> `$TRESTLE_BASEDIR/catalogs/nist800-53$ trestle split -e 'catalog.metadata'`

**Step 2**: Suppose now the user wants to further break down the `revision-history` property under the `metadata` subcomponent. The command to achieve that would be:

> `$TRESTLE_BASEDIR/catalogs/nist800-53/catalog$ trestle split -f metadata.json -e 'metadata.revision-history'`

The result would be the creation of a `metadata` subdirectory under `catalog` and the creation of a `revision-history.json` file under `metadata` as shown below:

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
            ├── metadata.json  #metadata JSON value without revision-history property        
            ├── metadata
            │   └── revision-history.json
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

The future version of this command would be:

> `$TRESTLE_BASEDIR/catalogs/nist800-53/catalog$ trestle split -e 'metadata.revision-history'`

**Step 3**: Knowing that `revision-history` is an array list, suppose the user wants to edit each item in that array list as a separate subcomponent or file. That can be achieved by running:

> `$TRESTLE_BASEDIR/catalogs/nist800-53/catalog/metadata$ trestle split -f revision-history.json -e 'revision-history.*'`

Notice the `.*` referring to each element in the array.
The command would replace the `revision-history.json` file by a `revision-history` directory containing multiple files prefixed with a 5 digit number representing the index of the array element followed by two underscores and the string `revision-history.json` as shown below:

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
            │   └── revision-history
            │       ├── 00000__revision-history.json
            │       ├── 00001__revision-history.json
            │       └── 00002__revision-history.json
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

The future version of this command would be:

> `$TRESTLE_BASEDIR/catalogs/nist800-53/catalog/metadata$ trestle split -e 'revision-history.*'`

OSCAL also makes use of named fields by leveraging`additionalProperties` supported by JSON Schema which behaves as a map or dict. OSCAL normally uses this feature as a way to assign multiple objects to a property without necessarily having to enforce a specific order as is the case with JSON array properties. It is like assigning a map/dict to a property. An example of such property in the catalog schema is the `responsible-parties` under `metadata`. One example of contents for a `responsible-parties` property is:

```
"responsible-parties": {
  "creator": {
    "party-uuids": [
      "4ae7292e-6d8e-4735-86ea-11047c575e87"
    ]
  },
  "contact": {
    "party-uuids": [
      "4ae7292e-6d8e-4735-86ea-11047c575e87"
    ]
  }
}
```

A more evident example of this type of property is in the `targets` property under the `target-definition` schema.

**Step 4**: Suppose the user wants to split the `responsible-parties` property in order to be able to edit each arbitrary key/value object under it as a separate file. The command to achieve that would be:

`$TRESTLE_BASEDIR/catalogs/nist800-53/catalog$ trestle split -f metadata.json -e metadata.responsible-parties.*`

Notice the `.*` at the end referring to each key/value pair in the map).
The command would result in creating a directory called `responsible-parties` under `metadata` and multiple JSON files under it, one for each named field using the key of the named field as the name of the JSON file. The result is shown below:

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

The future version of this command would be:

> `$TRESTLE_BASEDIR/catalogs/nist800-53/catalog$ trestle split -e 'metadata.responsible-parties.*'`

An example of a sequence of trestle split and merge commands and the corresponding states of the files/directories structures can be found in `test/data/split_merge` folder in this repo.

#### `trestle merge`

The trestle merge command is the reversal of `trestle split`. This command allows users to reverse the decomposition of a trestle model by aggregating subcomponents scattered across multiple files or directories into the parent JSON/YAML file.
To merge a model, you have to first change working directory to the root model component directory that you want to merge a sub-component model into.
The following option is required:

- `-e or --elements`: specifies the properties (JSON/YAML path) that will be merged, relative to the current working directory. This must contain at least 2 elements, where the last element is the model/sub-component to be merged into the second from last component.

For example, in the command `trestle merge -e catalog.metadata`, executed in the same directory where `catalog.json` or splitted `catalog` directory exists, the property `metadata` from `metadata.json` or `metadata.yaml` would be moved/merged into `catalog.json`. If the `metadata` model has already been split into smaller sub-component models previously, those smaller sub-components are first recusively merged into `metadata`, before merging `metadata` subcomponent into `catalog.json`. To specify merging every sub-component split from a component, `.*` can be used. For example, `trestle merge -e catalog.*` command, issued from the directory where `catalog.json` or`catalog` directory exists, will merge every single sub-component of that catalog back into the `catalog.json`.

#### `trestle assemble`

This command assembles all contents (files and directories) representing a specific model into a single OSCAL file located under `dist` folder. For example,

> `$TRESTLE_BASEDIR$ trestle assemble catalog -n nist800-53 -x json`

will traverse the `catalogs/nist800-53` directory and its children and combine all data into a OSCAL file that will be written to `dist/catalogs/nist800-53.json`. Note that the parts of catalog `nist800-53` can be written in either YAML/JSON/XML (e.g. based on the file extension), however, the output will be generated as YAML/JSON/XML as desired, based on the file extension argument provided 'json', 'yml' or 'yaml'. Trestle will infer the content type from the file extension and create the model representation appropriately in memory and then output in the desired format. Trestle assemble will also validate content as it assembles the files and make sure the contents are syntactically correct.

#### `trestle add`

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

#### `trestle remove`

The trestle remove command is the reversal of `trestle add`.

#### `trestle validate`

This command will validate the content of the specified file by combining all its children. For example, `trestle validate -f cat1yaml` will create the cat1 catalog in the model and make sure it is is a valid Catalog. By default this command do a "shallow validation" where it just checks for syntax error and makes sure the model can be generated from the file content. For extensive validation, `trestle validate` supports "deep validation" like cross-linking ids when additional parameters(e.g. `--mode deep-validation`) are passed. We envision that users will run this command occassionally to make sure the contents are valid.

## Future work

#### `trestle generate`

This command will allow generating default values such as UUID

### Deploy Commands

For the deploy phase of compliance engineering, trestle provides the following commands to facilitate various operations.

- `trestle plan`: Fetch current deployed controls and check what needes to be updated. This is like `terraform plan`.

- `trestle apply`: Apply the diffs or output of the `trestle plan` command in order to deploy the controls or other desired state. This is like `terraform apply`.

- `trestle ci init`: Initialize CI/CD pipeline for this project. It may create artefacts in `.trestle` directory.

- `trestle ci run`: Run the CI/CD pipeline. If a pipeline name is not provided, it will run all piplelines for this project.

- `trestle ci stop`: Stop the CI/CD pipleline. If a pipeline name is not provided, it will run all piplelines for this project.

### Monitoring Commands

Trestle provides the following commands to facilitate various monitoring operations.

*TBD*

- `trestle fetch`: This command will fetch facts about a control

### Reporting Commands

Trestle provides the following commands to facilitate various reporting operations.
