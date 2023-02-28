# Tutorial: Setup for and use of standard format csv-file to OSCAL Component Definition json-file transformer

Here are step by step instructions for setup and transformation of [trestle standard format csv-file](ocp4-sample-input.csv) into OSCAL Component Definition [json-file](component-definition.json) using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) tool.

## *Objective*

How to transform trestle standard format csv-file into a `component-definition.json` file.

There are 2 short steps shown below.
The first is a one-time check/set-up of your environment.
The second is a one-command transformation from `.csv` to `component-definition.json`.

<details markdown>

<summary>Table: expected .csv content</summary>

The below table represents the expectations of trestle task `csv-to-oscal-cd` for the contents of the input csv-file for synthesis of the output OSCAL Component Definition json-file.

`Column Name` is the name of the expected column in the input csv-file. Any additional columns not identified here, for example foobar, are also extracted and placed into the output json-file as component.control-implementation.prop\["foobar"\].

`Component Definition Locale` is the `path` within the output json-file into witch the value is stashed.

<table>

<tr style="text-align:left;vertical-align:top">
<th>Column Name
<th>Value Type
<th>Specification
<th>Value Description
<th>Component Definition Locale
<th>Example Value

<tr style="text-align:left;vertical-align:top">
<td>Rule_Id
<td>String
<td>required
<td>A textual label that uniquely identifies a policy (desired state) that can be used to reference it elsewhere in this or other documents.
<td>component.control-implementation.prop["Rule_Id"]
<td>password_policy_min_length_characters

<tr style="text-align:left;vertical-align:top">
<td>Rule_Description
<td>String
<td>required
<td>A description of the policy (desired state) including information about its purpose and scope.
<td>component.control-implementation.prop["Rule_Description"]
<td>Ensure password policy requires minimum length of 12 characters

<tr style="text-align:left;vertical-align:top">
<td>Profile_Reference_URL
<td>String
<td>required
<td>A URL reference to the source catalog or profile for which this component is implementing controls for. A profile designates a selection and configuration of controls from one or more catalogs
<td>component.control-implementation.source
<td>https://github.com/usnistgov/oscal-content/blob/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_HIGH-baseline_profile.json

<tr style="text-align:left;vertical-align:top">
<td>Profile_Description
<td>String
<td>required
<td>A description of the profile.
<td>component.control-implementation.description
<td>NIST Special Publication 800-53 Revision 5 HIGH IMPACT BASELINE

<tr style="text-align:left;vertical-align:top">
<td>Component_Type
<td>String
<td>required
<td>A category describing the purpose of the component.
<td>component.type
<td>Validation

<tr style="text-align:left;vertical-align:top">
<td>Control_Mappings
<td>String List (blank separated)
<td>required
<td>A list of textual labels that uniquely identify the controls or statements that the component implements.
<td>component.control-implementation.implemented-requirement.statement.statement-id<br>*and*<br>component.control-implementation.implemented-requirement.control-id
<td>ia-5.1_smt.a ia-5.1

<tr style="text-align:left;vertical-align:top">
<td>Resource
<td>String
<td>required
<td>A human readable name for the component.
<td>component.title
<td>Compliance Center

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Id
<td>String
<td>optional
<td>A textual label that uniquely identifies the parameter associated with that policy (desired state) or controls implemented by the policy (desired state).	A description of the parameter including the purpose and use of the parameter.
<td>component.control-implementation.prop["Parameter_Id"]<br>*and*<br>component.control-implementation.set-parameter.param-id
<td>minimum_password_length

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Description
<td>String
<td>optional
<td>A description of the parameter including the purpose and use of the parameter.
<td>component.control-implementation.prop["Parameter_Description"]
<td>Minimum Password

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Default_Value
<td>String
<td>optional
<td>A value recommended in this profile for the parameter of the control or policy (desired state).
<td>component.control-implementation.set-parameter.values
<td>12

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Value_Alternatives
<td>String List (blank separated)
<td>optional
<td>ONLY for the policy (desired state) parameters: A value or set of values the parameter can take.
<td>component.control-implementation.prop["Parameter_Value_Alternatives"]
<td>12 8

<tr style="text-align:left;vertical-align:top">
<td>Check_Id
<td>String
<td>optional
<td>A textual label that uniquely identifies a check of the policy (desired state) that can be used to reference it elsewhere in this or other documents.
<td>component.control-implementation.prop["Check_Id"]
<td>check_password_policy_min_length_characters

<tr style="text-align:left;vertical-align:top">
<td>Check_Description
<td>String
<td>optional
<td>A description of the check of the policy (desired state) including the method (interview or examine or test) and procedure details.
<td>component.control-implementation.prop["Check_Description"]
<td>Check whether password policy requires minimum length of 12 characters

<tr style="text-align:left;vertical-align:top">
<td>Fetcher
<td>String
<td>optional
<td>A textual label that uniquely identifies a collector of the actual state (evidence) associated with the policy (desired state) that can be used to reference it elsewhere in this or other documents.
<td>component.control-implementation.prop["Fetcher"]
<td>fetch_password_policy_min_length_characters

<tr style="text-align:left;vertical-align:top">
<td>Fetcher_Description
<td>String
<td>optional
<td>A description of the collector of the actual state (evidence) associated with the policy (desired state) including the method (interview or examine or API) and questionaire
<td>component.control-implementation.prop["Fetcher_Description"]
<td>Fetch whether password policy requires minimum length of 12 characters

<tr style="text-align:left;vertical-align:top">
<td>Resource_Instance_Type
<td>String
<td>optional
<td>A textual label that uniquely identifies a resource (component) type from the resource instance id. This text is part of all instance ids of a particular resource at runtime. For example the text 'db2' is part of all instance ids of resource DB2.
<td>component.control-implementation.prop["Resource_Instance_Type"]
<td>DB2

</table>

</details>

## *Step 1: Install trestle in a Python virtual environment*

Follow the instructions [here](https://ibm.github.io/compliance-trestle/python_trestle_setup/) to install trestle in a virtual environment.

## *Step 2: Transform profile data (CIS benchmarks)*

Linux, Mac

<details markdown>

<summary>Windows</summary>

Make these changes:

<ul>
<li>use backslashes `\` for file paths
<li>use `md` instead of mkdir -p
<li>put the url in double quotes for `curl`
<li>use `more` instead of cat
</ul>
</details>

- Navigate to trestle workspace.

```
(venv.trestle)$ cd trestle.workspace
```

- View configuration information.

```
(venv.trestle)$ trestle task csv-to-oscal-cd -i
trestle.core.commands.task:101 WARNING: Config file was not configured with the appropriate section for the task: "[task.csv-to-oscal-cd]"
Help information for csv-to-oscal-cd task.

Purpose: From csv produce OSCAL component_definition file.


Configuration flags sit under [task.csv-to-oscal-cd]:
  title             = (required) the component definition title.
  version           = (required) the component definition version.
  csv-file          = (required) the path of the csv file.
  required columns:   Rule_Id
                      Rule_Description
                      Profile_Reference_URL
                      Profile_Description
                      Component_Type
                      Control_Mappings
                      Resource
  optional columns:   Parameter_Id
                      Parameter_Description
                      Parameter_Default_Value
                      Parameter_Value_Alternatives
                      Check_Id
                      Check_Description
                      Fetcher
                      Fetcher_Description
                      Resource_Instance_Type
  output-dir        = (required) the path of the output directory for synthesized OSCAL .json files.
  namespace         = (optional) the namespace for properties, e.g. https://ibm.github.io/compliance-trestle/schemas/oscal/cd
  user-namespace    = (optional) the user-namespace for properties, e.g. https://ibm.github.io/compliance-trestle/schemas/oscal/cd/user-defined
  class.column-name = (optional) the class to associate with the specified column name, e.g. class.Rule_Id = scc_class
  output-overwrite  = (optional) true [default] or false; replace existing output when true.

```

- Create data folder.

```
(venv.trestle)$ mkdir -p adjunct-data
```

- Fetch sample csv-file.

```
(venv.trestle)$ curl 'https://raw.githubusercontent.com/IBM/compliance-trestle/main/docs/tutorials/task.csv-to-oscal-cd/ocp4-sample-input.csv' > adjunct-data/ocp4-sample-input.csv

```

- Fetch trestle task file.

```
(venv.trestle)$ curl 'https://raw.githubusercontent.com/IBM/compliance-trestle/main/docs/tutorials/task.csv-to-oscal-cd/demo-csv-to-oscal-cd.config' > adjunct-data/task-files/demo-csv-to-oscal-cd.config
```

<details markdown>

<summary>demo-csv-to-oscal-cd.config</summary>

```
[task.csv-to-oscal-cd]

csv-file = adjunct-data/ocp4-sample-input.csv
output-dir = component-definitions/ocp4-sample
title = ocp4-sample
version = 1.0
```

</details>

- Perform and validate the transform.

```
(venv.trestle)$ trestle task csv-to-oscal-cd -c demo-csv-to-oscal-cd.config 
input: adjunct-data/ocp4-sample-input.csv
output: component-definitions/ocp4-sample/component-definition.json
Task: csv-to-oscal-cd executed successfully.


```

- View the generated OSCAL.

```
(venv.trestle)$ component-definitions/ocp4-sample/component-definition.json
```

<details markdown>

<summary>component-definition.json</summary>

```
{
  "component-definition": {
    "uuid": "83cc8984-b00a-4799-885c-60b689efebd0",
    "metadata": {
      "title": "ocp4-sample",
      "last-modified": "2022-11-18T17:06:49+00:00",
      "version": "1.0",
      "oscal-version": "1.0.2"
    },
    "components": [
      {
        "uuid": "c0080494-186a-421d-9afd-f51e0359cbd8",
        "type": "Service",
        "title": "OSCO",
        "description": "",
        "control-implementations": [
          {
            "uuid": "43a69f86-a3ad-40fa-ada6-2f988b951728",
            "source": "https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile",
            "description": "ocp4",
            "props": [
              {
                "name": "Rule_Id",
                "value": "content_rule_api_server_anonymous_auth",
                "remarks": "rule_set_0"
              },
              {
                "name": "Rule_Description",
                "value": "Ensure that the --anonymous-auth argument is set to false",
                "remarks": "rule_set_0"
              },
              {
                "name": "Check_Id",
                "value": "xccdf_org.ssgproject.content_rule_api_server_anonymous_auth",
                "remarks": "rule_set_0"
              },
              {
                "name": "Check_Description",
                "value": "Ensure that the --anonymous-auth argument is set to false",
                "remarks": "rule_set_0"
              },
              {
                "name": "Rule_Id",
                "value": "content_rule_api_server_basic_auth",
                "remarks": "rule_set_1"
              },
              {
                "name": "Rule_Description",
                "value": "Ensure that the --basic-auth-file argument is not set",
                "remarks": "rule_set_1"
              },
              {
                "name": "Check_Id",
                "value": "xccdf_org.ssgproject.content_rule_api_server_basic_auth",
                "remarks": "rule_set_1"
              },
              {
                "name": "Check_Description",
                "value": "Ensure that the --basic-auth-file argument is not set",
                "remarks": "rule_set_1"
              },
              {
                "name": "Rule_Id",
                "value": "content_rule_api_server_token_auth",
                "remarks": "rule_set_2"
              },
              {
                "name": "Rule_Description",
                "value": "Ensure that the --token-auth-file parameter is not set",
                "remarks": "rule_set_2"
              },
              {
                "name": "Check_Id",
                "value": "xccdf_org.ssgproject.content_rule_api_server_token_auth",
                "remarks": "rule_set_2"
              },
              {
                "name": "Check_Description",
                "value": "Ensure that the --token-auth-file parameter is not set",
                "remarks": "rule_set_2"
              },
              {
                "name": "Rule_Id",
                "value": "content_rule_api_server_https_for_kubelet_conn",
                "remarks": "rule_set_3"
              },
              {
                "name": "Rule_Description",
                "value": "Ensure that the --kubelet-https argument is set to true",
                "remarks": "rule_set_3"
              },
              {
                "name": "Check_Id",
                "value": "xccdf_org.ssgproject.content_rule_api_server_https_for_kubelet_conn",
                "remarks": "rule_set_3"
              },
              {
                "name": "Check_Description",
                "value": "Ensure that the --kubelet-https argument is set to true",
                "remarks": "rule_set_3"
              }
            ],
            "implemented-requirements": [
              {
                "uuid": "c2893d38-1be4-4b0e-a090-96e846e15a3b",
                "control-id": "CIS-1.2.1",
                "description": "",
                "props": [
                  {
                    "name": "Rule_Id",
                    "value": "content_rule_api_server_anonymous_auth"
                  }
                ]
              },
              {
                "uuid": "3c2f7129-9724-47c0-aadb-3b3c9c44995c",
                "control-id": "CIS-1.2.2",
                "description": "",
                "props": [
                  {
                    "name": "Rule_Id",
                    "value": "content_rule_api_server_basic_auth"
                  }
                ]
              },
              {
                "uuid": "a4e2862f-7a1b-4182-b827-f5e797f589db",
                "control-id": "CIS-1.2.3",
                "description": "",
                "props": [
                  {
                    "name": "Rule_Id",
                    "value": "content_rule_api_server_token_auth"
                  }
                ]
              },
              {
                "uuid": "daec13ab-829e-4dd6-a9d6-9ad18391681e",
                "control-id": "CIS-1.2.4",
                "description": "",
                "props": [
                  {
                    "name": "Rule_Id",
                    "value": "content_rule_api_server_https_for_kubelet_conn"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

</details>

<br>
<br>

<span style="color:green">
Congratulations! You have completed this tutorial.
</span>

<br>
<br>
