# Trestle Specifications (v0.0.1)

## Table of Contents

- [Purpose](<#purpose>)
- [Users](<#users>)
- [Scope](<#scope>)
- [Trestle commands](<#trestle-commands>)
  - [Draft commands](<#draft-commands>)
- [Future work](<#future-work>)
  - [Deploy commands](<#deploy-commands>)
  - [Monitor commands](<#monitor-commands>)
  - [Reporting commands](<#reporting-commands>)

## Purpose

This document contains detail specifications of the Trestle commands.

Trestle offers various commands to simplify operations at different steps in compliance management and reporting.

Trestle assumes all security and compliance specifications and requirements are expressed in OSCAL format.

## Users

Trestle aims at compliance engineers who are familiar with various software development tools such as Git, CI/CD and command line tools.

Users of Trestle are also expected to be comfortable with editing OSCAL files in YAML/JSON/XML format.

## Scope

The scope of this document is to describe the purpose and expected behaviour of various trestle commands for manipulating OSCAL documents ONLY. This will not be all of trestle. Workflow commands will be subsequent / expanded on this.

## Trestle Commands

### Draft Commands

For the draft phase of compliance engineering, trestle provides the following commands to facilitate various draft related operations.


#### `trestle init`

This command will create a trestle project in the current directory with necessary directory structure and trestle artefacts. For example, if we run `trestle init` in a directory, it will create a directory structure like below for different artefacts as well as initiaze `git` in it:

~~~
.
├── .git
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
~~~

`.trestle` directory is a special directory containing various trestle artefacts to help run various other commands.

`dist` directory will contain the merged or assembled version of the models located on the source model directories (at the project root level) which are: `catalogs`, `profiles`, `target-definitions`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` and `plan-of-action-and-milestones`.

#### `trestle create`
  
This command will create an initial directory structure for various OSCAL models including sample JSON files and subdirectories representing parts of the model. For example, `trestle create catalog -o catalog-cat1` will create a directory structure of a sample catalog like below.

~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       └── catalog-cat1.json
└── catalogs
    └── catalog-cat1
        ├── catalog.json
        └── groups
            ├── 00000__group
            │   ├── group.json
            │   └── controls
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~

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
~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       └── catalog-cat1.json
└── catalogs
    └── catalog-cat1
        ├── catalog.json
        └── groups
            ├── groups.json        
            ├── 00000__group            
            │   ├── group.json
            │   └── controls
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~
- a `catalog.json` file containing a catalog JSON object without the `catalog.groups` property.
- `catalog.groups` property is broken down into a subdirectory called `groups`. The `groups` subdirectory has a `groups.json` file containing a JSON object named `groups` as an empty array.
- For each group in the `catalog.groups` array list, an indexed subdirectory is created containing a `group.json` with a group object as its contents without the `controls` property.
- `catalog.groups[i].controls` property in each group is broken down into subdirectories called `controls`. The `controls` subdirectory has a `controls.json` file containing a JSON object named `controls` as an empty array.
- For each control in a `catalog.groups[i].controls` array list, an indexed JSON file is created representing the contents of a control.

#### *Profile default decomposition*

For `profile`, the initial sample content is not broken down by default as shown below.
~~~
.
├── .git
├── .trestle
├── dist
│   └── profiles
│       └── profile-myprofile.json
└── profiles
    └── profile-myprofile
        └── profile.json
...
~~~
- `profile.json` file has the content of the OSCAL profile.

#### *Target-definition default decomposition*

For `target-definition`, the initial sample content is broken down as shown below:
~~~
.
├── .git
├── .trestle
├── dist
│   └── target-definitions
│       └── target-definition-mytargets.json
└── target-definitions
    └── target-definition-mytargets
        ├── target-definition.json
        └── components
            ├── components.json
            ├── 74ccb93f-07d1-422a-a43d-3c97bae4c514__component
            │   ├── component.json
            │   └── control-implementations
            │       ├── control-implementations.json
            │       ├── 00000__control-implementation.json
            │       └── 00001__control-implementation.json
            └── 953a2878-2a21-4a0f-a9fa-3a37b61b9df8__component
                ├── component.json
                └── control-implementations
                    ├── control-implementations.json
                    └── 00000__control-implementation.json
...
~~~
- a `target-definition.json` file containing a target definition JSON object except for the `target-definition.components` property.
- `target-definition.components` property is broken down into a subdirectory named `components`. The `components` subdirectory has a `components.json` file containing a JSON object named `components` as an empty object.
- For each component in the `target-definition.components` uniquely identified by a property labelled with the component's uuid, a subdirectory named after the `{{uuid}}__component` is created containing a `component.json` file. This file contains a component JSON object without the `control-implementations` property.
- `target-definition.components.{{uuid}}.control-implementations` property is broken down into subdirectories called `control-implementations`. The `control-implementations` subdirectory has a `control-implementations.json` file containing a JSON object named `control-implementations` as an empty object.
- For each control implementation in a `target-definition.components.{{uuid}}.control-implementations` array list, an indexed JSON file is created representing the contents of a control implementation.

At the moment, the initial sample content for the other model types (`component-definition`, `system-security-plan`, `assessment-plan`, `assessment-result` and `plan-of-action-and-milestone`) is TBD.

The user can increase the level of decomposition by using `trestle split` command.

#### `trestle import`

This command allows users to import existing OSCAL files so that they can be managed using trestle. For example `trestle import -f existing_catalog.json -o my_existing_catalog` will import `existing_catalog.json` into a new folder under `catalogs` as shown below:

~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       ├── my_existing_catalog.json 
│       └── catalog-cat1.json 
└── catalogs
    ├── my_existing_catalog
    │   ├── catalog.json
    │   └── groups
    │       ├── groups.json
    │       └── 00000__group
    │           ├── group.json
    │           └── controls
    │               ├── controls.json    
    │               ├── 00000__control.json
    │               └── 00001__control.json
    └── catalog-cat1
        ├── catalog.json
        └── groups
            ├── groups.json
            ├── 00000__group
            │   ├── group.json
            │   └── controls
            │       ├── controls.json                
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── controls.json                    
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~

The following options are supported:
- `-f or --file`: specifies the path of an existing OSCAL file.
- `-o or --output`: specifies the name/alias of a model. It is used as the prefix for the output filename under the `dist` directory and for naming the source subdirectories under  `catalogs`, `profiles`, `target-definitions`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` or `plan-of-action-and-milestones`.

The import subcommand can determine the type of the model that is to be imported by the contents of the file.

Note that the import command will decompose the file according to the default decomposing rules already mentioned in the `trestle create` section. Similarly to `trestle create`, the user can increase the level of decomposition by using `trestle split` command.

#### `trestle split`

This command allows users to further decompose a trestle model into additional subcomponents. 

To illustrate how this command could be used consider a catalog model named `mycatalog` that was created via `trestle create catalog -o mycatalog` or imported via `trestle import -f mycatalog.json`.

~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       └── mycatalog.json 
└── catalogs
    └── mycatalog
        ├── catalog.json
        └── groups
            ├── groups.json
            ├── 00000__group
            │   ├── group.json
            │   └── controls
            │       ├── controls.json
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── controls.json
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~

The following options are supported:
- `-i or --input`: this optional parameter can be used to specify the model instance you want to split. This can be ommitted if the `trestle split` command is executed from within a model instance directory (contextual mode) such as `catalogs/mycatalog`, for example.
- `-e or --elements`: specifies the model subcomponent element that is going to be split. Multiple elements can be specified at once using a comma-separated value. If the element is of JSON type array list and you want trestle to create a separate subcomponent file per array item, the element needs to be suffixed with `[]`. If the suffix is not specified, split will place all array items in only one separate subcomponent file. If the element is a collection of JSON Schema additionalProperties and you want trestle to create a separate subcomponent file per additionalProperties item, the element needs to be suffixed with `{}`. Similarly, not adding the suffix will place all additionalProperties items in only one separate subcomponent file. The path of a model subcomponent element is contextual if `trestle split` is executed from within a model instance subdirectory. If `trestle split` is executed from the $BASE_FOLDER, the element path needs to be an absolute full path.
  
A user might want to decompose the `metadata` property from `catalog.json`. In order to achieve that he/she would run `trestle split -i catalogs/mycatalog -e metadata`. This would create a `metadata.json` file at the same level as `catalog.json` and move the whole `metadata` property/section from `catalog.json` to `metadata.json` as below:

~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       └── mycatalog.json 
└── catalogs
    └── mycatalog
        ├── catalog.json      #removed metadata property from this file
        ├── metadata.json     #contains the metadata JSON object
        └── groups
            ├── groups.json        
            ├── 00000__group
            │   ├── group.json
            │   └── controls
            │       ├── controls.json            
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── controls.json                
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~

Suppose now the user wants to further break down the `revision-history` property under the `metadata` subcomponent. The command to achieve that would be `trestle split -i catalogs/mycatalog -e metadata.revision-history` which would result in the replacement of the `metadata.json` file by a `metadata` directory containing a `metadata.json` file and a `revision-history.json` file as shown below:

~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       └── mycatalog.json 
└── catalogs
    └── mycatalog
        ├── catalog.json
        ├── metadata
        │   ├── metadata.json  #metadata JSON value without revision-history property
        │   └── revision-history.json
        └── groups
            ├── groups.json          
            ├── 00000__group
            │   ├── group.json
            │   └── controls
            │       ├── controls.json            
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── controls.json                      
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~

Knowing that `revision-history` is an array list, suppose the user wants to edit each item in that array list as a separate subcomponent or file. That can be achieved by running: `trestle split -i catalogs/mycatalog -e metadata.revision-history[]` (notice the squared brackets at the end) which would replace the `revision-history.json` file by a `revision-history` directory containing multiple files prefixed with a 5 digit number representing the index of the array element followed by an underscore and the string `revision-history.json` as shown below:

~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       └── mycatalog.json 
└── catalogs
    └── mycatalog
        ├── catalog.json
        ├── metadata
        │   ├── metadata.json
        │   └── revision-history
        │       ├── revision-history.json        
        │       ├── 00000__revision-history.json
        │       ├── 00001__revision-history.json
        │       └── 00002__revision-history.json                
        └── groups
            ├── groups.json
            ├── 00000__group
            │   ├── group.json
            │   └── controls
            │       ├── controls.json            
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── controls.json                    
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~

OSCAL also makes use of `additionalProperties` supported by JSON Schema. OSCAL normally uses this feature as a way to assign multiple objects to a property without necessarily having to enforce a specific order as is the case with JSON array properties. It is like assigning a map/dict to a property. An example of such property in the catalog schema is the `responsible-parties` under `metadata`. One example of contents for a `responsible-parties` property is:

~~~
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
~~~

A more evident example of this type of property is in the `components` property under the `target-definition` schema.

Suppose the user wants to split the `responsible-parties` property in order to be able to edit each arbitrary key/value object under it as a separate file. The command to achieve that would be `trestle split -i catalogs/mycatalog -e metadata.responsible-parties{}` (notice the curly braces at the end) which would result in creating a directory called `responsible-parties` and multiple JSON files under it, one for each `additionalProperty` using the key of the `additional property` as the name of the JSON file. The result is shown below:

~~~
.
├── .git
├── .trestle
├── dist 
│   └── catalogs
│       └── mycatalog.json 
└── catalogs
    └── mycatalog
        ├── catalog.json
        ├── metadata
        │   ├── metadata.json
        │   ├── revision-history
        │   │   ├── revision-history.json        
        │   │   ├── 00000__revision-history.json
        │   │   ├── 00001__revision-history.json
        │   │   └── 00002__revision-history.json       
        │   └── responsible-parties
        │       ├── responsible-parties.json        
        │       ├── creator__responsible-party.json
        │       └── contact__responsible-party.json       
        └── groups
            ├── groups.json        
            ├── 00000__group
            │   ├── group.json
            │   └── controls
            │       ├── controls.json
            │       ├── 00000__control.json
            │       └── 00001__control.json
            └── 00001__group
                ├── group.json
                └── controls
                    ├── controls.json                
                    ├── 00000__control.json
                    ├── 00001__control.json
                    └── 00002__control.json
...
~~~

#### `trestle merge`

The trestle merge command is the reversal of `trestle split`.

#### `trestle build`

This command merges all contents (files and directories) representing a specific model into a single OSCAL file located under `dist` folder. For example, `trestle merge catalog -i mycatalog` will traverse the `catalogs/mycatalog` directory and its children and combine all data into a OSCAL file that will be written to `dist/catalogs/mycatalog.json`. Note that the parts of catalog `mycatalog` can be written in either YAML/JSON/XML (e.g. based on the file extension), however, the output will be generated as YAML/JSON/XML as desired. Trestle will infer the content type from the file extension and create the model representation appropriately in memory and then output in the desired format. Trestle merge will also validate content as it assembles the files and make sure the contents are syntactically correct.

#### `trestle add`

This command allows users to add an OSCAL model to a subcomponent in source directory structure of the model. For example, `trestle add -e metadata.roles -i catalogs/mycatalog` will add the following property under the `metadata` property for a catalog that will be written to the appropriate file under `catalogs/mycatalog` directory:

~~~
"roles": [
  {
    "id": "REPLACE_ME",
    "title": "REPLACE_ME"
  }
~~~

Default values for mandatory datatypes will be like below. All UUID's will be populated by default whether or not they are mandatory.

~~~
- DateTime: <Current date-time>
- Boolean: False
- Integer: 0 
- String: REPLACE_ME
- Float/Double: 0.00
- Id field: Auto generated UUID
~~~

#### `trestle validate`

This command will validate the content of the specified file by combining all its children. For example, `trestle validate -f cat1yaml` will create the cat1 catalog in the model and make sure it is is a valid Catalog. By default this command do a "shallow validation" where it just checks for syntax error and makes sure the model can be generated from the file content. For extensive validation, `trestle validate` supports "deep validation" like cross-linking ids when additional parameters(e.g. `--mode deep-validation`) are passed. We envision that users will run this command occassionally to make sure the contents are valid.

## Future work

#### `trestle duplicate`

This command allows users to duplicate a certain OSCAL model (file and directory structure). For example `trestle duplicate -s cat1 -o cat11` will duplicate the Catalog cat1 into `cat11` directory. It can also regenerate all the UUIDs as required. 

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
