# Trestle CLI

## Overview & Usecases

The trestle CLI has two primary use cases by design:

- Serve as tooling to generate and manipulate OSCAL files directly by an end user. The objective is to reduce the complexity of creating and editing workflows. Example commands are: `trestle import`, `trestle create`, `trestle add`, `trestle split`, `trestle merge`.
- Act as an automation tool that, by design, can be an integral part of a CI/CD pipeline e.g. `trestle validate`, `trestle tasks`.

To support each of these use cases trestle creates an opinionated directory structure to manage OSCAL documents.

## Opinionated directory structure

Trestle relies on an opinionated directory structure, similar to `git`, `go`, or `auditree`, to manage the workflow. Unlike git commands, trestle commands are not restricted to working within an initialized directory tree - but that is the most likely use case.

The directory structure setup by trestle has three major elements:

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

`.trestle` directory is a special directory containing various trestle artefacts to help run various other commands. Examples include configuration files, caches and templates.

The bulk of the folder structure is used to represent each of the *top level schemas* or *top level models* such as `catalogs` and `profiles`. For each of these directories the following root structure is maintained:

```

├── .trestle
└── TOP_LEVEL_MODEL_PLURAL
    └── NAME_OF_MODEL_INSTANCE
        └── TOP_LEVEL_MODEL_NAME.{json,yaml,yml}

```

which appears, for a catalog a user decides is titled nist-800-53, as:

```
├── .trestle
└── catalogs
    └── nist-800-53
        └── catalog.json

```

`dist` directory will contain the assembled version of the models located on the source model directories (at the project root level) which are: `catalogs`, `profiles`, `target-definitions`, `component-definitions`, `system-security-plans`, `assessment-plans`, `assessment-results` and `plan-of-action-and-milestones`. The assumption is that each of the OSCAL files within this folder is ready to be read by external 3rd party tools.

### Support for subdivided document structures

The files constructed by OSCAL can run into the tens of thousands of lines of yaml or formatted json. At this size the
files become completely unmanageable for users. To combat this, trestle can `trestle split` a file into many smaller files and later merge those split files together.

Directory structures such as the one below can represent OSCAL document structures. Users are strongly encourage to rely on split and merge to code these structures.

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

This command will create a trestle project in the current directory with the necessary directory structure and trestle artefacts. For example, if we run `trestle init` in a directory, it will create the directory structure below for different artefacts:

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

Trestle validate is designed to perform a function to ensure integrity of a set of OSCAL files. This can be as simple as
a schema validation within a single file or as complex as ensuring the integrity of a 'stack' of OSCAL files including potentially
remote system state.

Trestle validate the form \`trestle validate -f FILE -i SPECIFIC_ITEM_OR_VALUE, --mode {duplicate or similar}

and returns a non-zero return code on a validation failure. Mode is a list of validation modes that will be implemented as shown in the table below.

| Mode       | Purpose                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------- |
| duplicates | Identify if duplicate values exist for a given json key for example `trestle validate -f catalog.json -i uuid --mode duplicate` |

## `trestle tasks`

Open Shift Compliance Operator and Tanium are supported as 3rd party tools.

## `trestle task osco-to-oscal`

The *trestle task osco-to-oscal* command facilitates transformation of OpenShift Compliance Operator (OSCO) scan results *.yaml* files into OSCAL partial results *.json* files. Specify required config parameters to indicate the location of the input and the output. Specify optional config parameters to indicate the name of the oscal-metadata.yaml file, if any, and whether overwriting of existing output is permitted.

<span style="color:green">
Example command invocation:
</span>

> `$TRESTLE_BASEDIR$ trestle task osco-to-oscal -c /home/user/task.config`

<span style="color:green">
Example config:
</span>

*/home/user/task.config*

```
[task.osco-to-oscal]

input-dir =  /home/user/git/evidence/osco/input
output-dir = /home/user/git/evidence/oscal/output
oscal-metadata = oscal-metadata.yaml
output-overwrite = true
```

**input**

<span style="color:green">
Example input directory contents listing:
</span>

*/home/user/git/evidence/osco/input*

```
-rw-rw-r--. 1 user user  3832 Feb  2 09:36 oscal-metadata.yaml
-rw-rw-r--. 1 user user 49132 Feb  2 06:12 ssg-ocp4-ds-cis-111.222.333.444-pod.yaml
-rw-rw-r--. 1 user user 52747 Feb  2 06:41 ssg-ocp4-ds-cis-111.222.333.555-pod.yaml

```

<span style="color:green">
Example input OSCO scan result file contents (snippet):
</span>

*ssg-ocp4-ds-cis-111.222.333.444-pod.yaml*

<details>
<summary>display sample</summary>

```
apiVersion: v1
data:
  exit-code: "2"
  results: |
    <?xml version="1.0" encoding="UTF-8"?>
    <TestResult xmlns="http://checklists.nist.gov/xccdf/1.2" 
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
              <target-id-ref system="http://scap.nist.gov/schema/asset-identification/1.1" name="asset0" href=""/>
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
    compliance-remediations/processed: ""
    compliance.openshift.io/scan-error-msg: ""
    compliance.openshift.io/scan-result: NON-COMPLIANT
    openscap-scan-result/node: 111.222.333.444
  creationTimestamp: "2020-08-03T02:26:34Z"
  labels:
    compliance-scan: ssg-ocp4-ds-cis
  name: ssg-ocp4-ds-cis-111.222.333.444-pod
  namespace: openshift-compliance
  resourceVersion: "22693328"
  selfLink: /api/v1/namespaces/openshift-compliance/configmaps/ssg-ocp4-ds-cis-111.222.333.444-pod
  uid: 1da3ea81-0a25-4512-ad86-7ac360246b5d
  
```

</details>
<br>

<span style="color:green">
Example input OSCAL metadata file contents:
</span>

*oscal-metadata.yaml*

<details>
<summary>display sample</summary>

```
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
            target: kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.mycorp
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
            target: kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.mycorp
            target-ip: 111.222.333.444
            cluster-name: ROKS-OpenSCAP-1
            cluster-type: openshift
            cluster-region: us-south
```

</details>

**metadata format**

The *oscal_metadata.yaml* file comprises one or more mappings. Below is shown the
format of a single mapping. The items in angle brackets are to be replaced with
desired values for augmenting the produced OSCAL.

The mapping whose *<name>* matches the *\[metadata\]\[name\]* in the evidence for the
corresponding embedded XML, if any, will be used for augmenting the produced
OSCAL.

```
<name>:
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

```
-rw-rw-r--. 1 user user 49132 Feb  3 10:59 ssg-ocp4-ds-cis-111.222.333.444-pod.json
-rw-rw-r--. 1 user user 52747 Feb  3 10:59 ssg-ocp4-ds-cis-111.222.333.555-pod.json

```

<span style="color:green">
Example output OSCAL Observations file contents (snippet):
</span>

*ssg-ocp4-ds-cis-111.222.333.444-pod.json*

<details>
<summary>display sample</summary>

```
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
    },
    ...
```

</details>

## `trestle task tanium-to-oscal`

The *trestle task tanium-to-oscal* command facilitates transformation of Tanuim reports, each
input file comprising individual lines consumable as *json*, into OSCAL partial results *.json* files.
Specify required config parameters to indicate the location of the input and the output.
Specify optional config parameter *output-overwrite* to indicate whether overwriting of existing output is permitted.
Specify optional config parameter *timestamp* as ISO 8601 formated string (e.g., 2021-02-24T19:31:13+00:00) to override the timestamp attached to each Observation.

<span style="color:green">
Example command invocation:
</span>

> `$TRESTLE_BASEDIR$ trestle task tanium-to-oscal -c /home/user/task.config`

<span style="color:green">
Example config:
</span>

*/home/user/task.config*

```
[task.tanium-to-oscal]

input-dir =  /home/user/git/compliance/tanium/input
output-dir = /home/user/git/compliance/oscal/output
output-overwrite = true
```

**input**

<span style="color:green">
Example input directory contents listing:
</span>

*/home/user/git/compliance/tanium/input*

```
-rw-rw-r--. 1 degenaro degenaro 1830 Mar  7 08:23 Tanium.comply-nist-results

```

*Tanium.comply-nist-results*

<details>
<summary>display sample</summary>

```
{"IP Address":"fe80::3cd5:564b:940e:49ab","Computer Name":"cmp-wn-2106.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.11","Computer Name":"","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.11","Computer Name":"cmp-wn-2106.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days","Result":"fail","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.11","Computer Name":"cmp-wn-2106.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.4_L1_Ensure_Minimum_password_length_is_set_to_14_or_more_characters","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}


```

</details>

**output**

<span style="color:green">
Example output directory contents listing:
</span>

*/home/user/git/compliance/oscal/output*

```
-rw-rw-r--. 1 degenaro degenaro 6479 Mar  7 08:25 Tanium.oscal.json

```

*Tanium.oscal.json*

<details>
<summary>display sample</summary>

```
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
