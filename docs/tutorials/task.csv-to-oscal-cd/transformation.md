# Tutorial: Setup for and use of standard format csv-file to OSCAL Component Definition json-file transformer

Here are step by step instructions for setup and transformation of [trestle standard format csv-file](ocp4-sample-input.csv) into OSCAL Component Definition [json-file](component-definition.json) using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) tool.

## *Objective*

How to transform trestle standard format csv-file into a `component-definition.json` file.

There are 2 short steps shown below.
The first is a one-time check/set-up of your environment.
The second is a one-command transformation from `.csv` to `component-definition.json`.

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
