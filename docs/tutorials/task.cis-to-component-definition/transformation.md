# Tutorial: Setup for and use of ComplianceAsCode profile to OSCAL Component Definition transformer

Here are step by step instructions for setup and transformation of [ComplianceAsCode](https://github.com/ComplianceAsCode/content) profile data files into [NIST](https://www.nist.gov/) standard [OSCAL](https://pages.nist.gov/OSCAL/) [Component Definition](https://pages.nist.gov/OSCAL/reference/latest/component-definition/json-outline/) using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) tool.

## *Objective*

How to transform one or more `.profile` compliance files into a standardized `OSCAL.json` file.

There are 2 short steps shown below.
The first is a one-time check/set-up of your environment.
The second is a one-command transformation from `.profile` to `OSCAL.json`.

## *Step 1: Install trestle in a Python virtual environment*

Follow the instructions [here](https://ibm.github.io/compliance-trestle/python_trestle_setup/) to install trestle in a virtual environment.

## *Step 2: Transform profile data (CIS benchmarks)*

Linux, Mac

<details>
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

```shell
(venv.trestle)$ cd trestle.workspace
```

- View configuration information.

```shell
(venv.trestle)$ trestle task cis-to-component-definition -i
trestle.core.commands.task:99 WARNING: Config file was not configured with the appropriate section for the task: "[task.cis-to-component-definition]"
Help information for cis-to-component-definition task.

Purpose: Create component definition from from standard (e.g. CIS benchmark).

Configuration flags sit under [task.cis-to-component-definition]:
  component-name         = component name, e.g. OSCO.
  org-name               = organization name, e.g. International Business Machines.
  org-remarks            = organization remarks, e.g. IBM.
  output-dir             = location to write the generated component-definition.json file.
  profile-name           = profile name, e.g. OCP4 CIS-benchmark v4.
  profile-mnemonic       = profile mnemonic, e.g. ocp4-cis-node.
  profile-ns             = profile ns, e.g. https://github.com/ComplianceAsCode/content/tree/master/ocp4.
  profile-version        = profile version, e.g. 1.1.
  profile-check-version  = profile check version, e.g. 0.1.58.
  profile-type           = profile type, e.g. OCP4.
  profile-list           = profile list is blank separated list of "<suffix>" for config entries: 
                           profile-file.<suffix>, profile-title.<suffix>, profile-url.<suffix>, e.g. cis cis-node.
  profile-file.<suffix>  = path of the profile file to ingest, e.g. /home/degenaro/git/compliance-as-code.content/products/ocp4/profiles/cis-node.profile.
  profile-title.<suffix> = title of the profile, e.g. CIS Red Hat OpenShift Container Platform 4 Benchmark.
  profile-url.<suffix>   = URL of the profile, e.g. https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile.
  rule-to-parameters-map = map file for set-parameters, e.g. /home/degenaro/git/shared-trestle-workspace.oscal-for-osco/component-definitions/osco/rule2var.json.
  selected-rules         = file with list of selected rules, e.g. /home/degenaro/git/shared-trestle-workspace.oscal-for-osco/component-definitions/osco/selected_rules.json.
  enabled-rules          = file with list of enabled rules, e.g. /home/degenaro/git/shared-trestle-workspace.oscal-for-osco/component-definitions/osco/enabled_rules.json.

Notes:
1. If a control has selected rules but no enabled rules, then all those selected are included.
2. If a control has selected and enabled rules, then only those enabled are included.
3. If a control has no selected rules, then none are included regardless of enabled.
```

- Create data folders.

```shell
(venv.trestle)$ mkdir -p adjunct-data/cis-benchmarks
(venv.trestle)$ mkdir -p adjunct-data/trestle-configs
```

- Fetch ComplianceAsCode profile data.

```shell
(venv.trestle)$ curl 'https://raw.githubusercontent.com/ComplianceAsCode/content/master/products/ocp4/profiles/cis-node.profile' > adjunct-data/cis-benchmarks/cis-node.profile
(venv.trestle)$ curl 'https://raw.githubusercontent.com/ComplianceAsCode/content/master/products/ocp4/profiles/cis-node.profile' > adjunct-data/cis-benchmarks/cis.profile

```

- Fetch trestle task files.

```shell
(venv.trestle)$ curl 'https://https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-component-definition/demo-cis-to-component-definition.config' > adjunct-data/task-files/demo-cis-to-component-definition.config
(venv.trestle)$ curl 'https://https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-component-definition/selected_rules.json' > adjunct-data/task-files/selected_rules.json
(venv.trestle)$ curl 'https://https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-component-definition/enabled_rules.json' > adjunct-data/task-files/enabled_rules.json
```

<details>
<summary>demo-cis-to-component-definition.config</summary>

```shell
[task.cis-to-component-definition]

output-dir = component-definitions/cis

org-name = International Business Machines
org-remarks = IBM

component-name = OSCO

profile-name = OCP4 CIS-benchmark v4
profile-mnemonic = ocp4-cis-node
profile-ns = https://github.com/ComplianceAsCode/content/tree/master/ocp4
profile-version = 1.1
profile-check-version = 0.1.58

profile-type = OCP4
profile-list = cis-node cis

profile-file.cis-node = adjunct-data/cis-benchmarks/cis-node.profile
profile-url.cis-node = https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis-node.profile
profile-title.cis-node = CIS Red Hat OpenShift Container Platform 4 Benchmark

profile-file.cis = adjunct-data/cis-benchmarks/cis.profile
profile-url.cis = https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile
profile-title.cis = CIS Red Hat OpenShift Container Platform 4 Benchmark

selected-rules  = adjunct-data/task-files/selected_rules.json
enabled-rules  = adjunct-data/task-files/enabled_rules.json
```

</details>

<details>
<summary>selected_rules.json</summary>

```json
{
  "selected": [
    "file_permissions_kube_apiserver",
    "file_owner_kube_apiserver",
    "file_groupowner_kube_apiserver",
    "file_permissions_kube_controller_manager",
    "file_owner_kube_controller_manager",
    "file_groupowner_kube_controller_manager",
    "file_permissions_scheduler",
    "file_owner_kube_scheduler",
    "file_groupowner_kube_scheduler",
    "file_permissions_etcd_member"
  ]
}
```

</details>

<details>
<summary>enabled_rules.json</summary>

```json
{
  "enabled": [
    "file_permissions_kube_apiserver",
    "file_owner_kube_apiserver",
    "file_groupowner_kube_apiserver",
    "file_permissions_kube_controller_manager",
    "file_owner_kube_controller_manager",
    "file_groupowner_kube_controller_manager",
    "file_permissions_scheduler",
    "file_owner_kube_scheduler",
    "file_groupowner_kube_scheduler",
    "file_permissions_etcd_member"
  ]
}
```

</details>

- Perform and validate the transform.

```shell
(venv.trestle)$ trestle task cis-to-component-definition -c adjunct-data/task-files/demo-cis-to-component-definition.config
output: component-definitions/cis/component-definition.json
Task: cis-to-component-definition executed successfully.

(venv.trestle)$ trestle validate --all
VALID: Model /home/<user>/trestle.workspace/component-definitions/cis/component-definition.json passed the Validator to confirm the model passes all registered validation tests.

```

- View the generated OSCAL.

```shell
(venv.trestle)$ cat component-definitions/cis/component-definition.json
```

<details>
<summary>component-definition.json</summary>

```json
{
  "component-definition": {
    "uuid": "c08f1c4d-fc9e-4fa9-a6bd-8b4e20422ae0",
    "metadata": {
      "title": "Component definition for OCP4 profiles",
      "last-modified": "2021-11-17T14:27:27+00:00",
      "version": "0.28.1",
      "oscal-version": "1.0.0",
      "roles": [
        {
          "id": "prepared-by",
          "title": "Indicates the organization that created this content."
        },
        {
          "id": "prepared-for",
          "title": "Indicates the organization for which this content was created.."
        },
        {
          "id": "content-approver",
          "title": "Indicates the organization responsible for all content represented in the 'document'."
        }
      ],
      "parties": [
        {
          "uuid": "741d5f7e-2296-4224-ad75-5a60bb30a826",
          "type": "organization",
          "name": "International Business Machines",
          "remarks": "IBM"
        },
        {
          "uuid": "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
          "type": "organization",
          "name": "Customer",
          "remarks": "organization to be customized at account creation only for their Component Definition"
        },
        {
          "uuid": "813451c9-5265-447d-b39e-4fbcac440888",
          "type": "organization",
          "name": "ISV",
          "remarks": "organization to be customized at ISV subscription only for their Component Definition"
        }
      ],
      "responsible-parties": [
        {
          "role-id": "prepared-by",
          "party-uuids": [
            "741d5f7e-2296-4224-ad75-5a60bb30a826"
          ]
        },
        {
          "role-id": "prepared-for",
          "party-uuids": [
            "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
            "813451c9-5265-447d-b39e-4fbcac440888"
          ]
        },
        {
          "role-id": "content-approver",
          "party-uuids": [
            "741d5f7e-2296-4224-ad75-5a60bb30a826"
          ]
        }
      ]
    },
    "components": [
      {
        "uuid": "944e20f9-6a7d-4af0-9066-911cfbeb3d9a",
        "type": "Service",
        "title": "OSCO",
        "description": "OSCO",
        "control-implementations": [
          {
            "uuid": "51ce9ce9-c455-4124-a189-22f84301723d",
            "source": "https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis-node.profile",
            "description": "OSCO implemented controls for CIS Red Hat OpenShift Container Platform 4 Benchmark.",
            "props": [
              {
                "name": "profile_name",
                "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                "value": "OCP4 CIS-benchmark v4",
                "class": "scc_profile_name"
              },
              {
                "name": "profile_mnemonic",
                "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                "value": "ocp4-cis-node",
                "class": "scc_profile_mnemonic"
              },
              {
                "name": "profile_version",
                "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                "value": "1.1",
                "class": "scc_profile_version"
              },
              {
                "name": "profile_check_version",
                "value": "0.1.58"
              }
            ],
            "implemented-requirements": [
              {
                "uuid": "fd024a93-cbc2-40da-b43b-8d972a089dfc",
                "control-id": "CIS-1.1.1",
                "description": "Ensure that the API server pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the API server pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "b64e6a80-2d6e-4c38-9c03-f479b782d406",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the API server pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "966d4e45-f3bc-4abd-84a9-48a7351c3a15",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the API server pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "82b8964f-b878-4e80-ae18-d0eb423dfdcf",
                "control-id": "CIS-1.1.3",
                "description": "Ensure that the controller manager pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the controller manager pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "9690ee49-11a9-4e31-93a0-f46a5f69c5dd",
                "control-id": "CIS-1.1.4",
                "description": "Ensure that the controller manager pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the controller manager pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "6f3b4689-0166-4d31-83ae-4d82ac6697eb",
                "control-id": "CIS-1.1.4",
                "description": "Ensure that the controller manager pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the controller manager pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "9d4f32ed-8305-4dbf-8ba1-7a82b7b5156f",
                "control-id": "CIS-1.1.5",
                "description": "Ensure that the scheduler pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the scheduler pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "84210a78-491c-4c85-8587-df51ed67ca28",
                "control-id": "CIS-1.1.6",
                "description": "Ensure that the scheduler pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the scheduler pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "85bcd145-2d04-49bc-bc53-0aa7dc39c34b",
                "control-id": "CIS-1.1.6",
                "description": "Ensure that the scheduler pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the scheduler pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "6cf649b3-2fec-42a1-ada8-fb971648cfb6",
                "control-id": "CIS-1.1.7",
                "description": "Ensure that the etcd pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the etcd pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              }
            ]
          },
          {
            "uuid": "02798083-2376-4ab6-a1d7-846a82ed4ecb",
            "source": "https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile",
            "description": "OSCO implemented controls for CIS Red Hat OpenShift Container Platform 4 Benchmark.",
            "props": [
              {
                "name": "profile_name",
                "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                "value": "OCP4 CIS-benchmark v4",
                "class": "scc_profile_name"
              },
              {
                "name": "profile_mnemonic",
                "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                "value": "ocp4-cis-node",
                "class": "scc_profile_mnemonic"
              },
              {
                "name": "profile_version",
                "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                "value": "1.1",
                "class": "scc_profile_version"
              },
              {
                "name": "profile_check_version",
                "value": "0.1.58"
              }
            ],
            "implemented-requirements": [
              {
                "uuid": "202478c7-e5a2-4aaf-a218-4485c4117e9c",
                "control-id": "CIS-1.1.1",
                "description": "Ensure that the API server pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the API server pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "287593de-8c05-4d50-9d30-1b078563a071",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the API server pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "3e5dbc64-b426-4134-b9a1-33eba02633bb",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the API server pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "aeb6f0a4-6ce8-4e13-a0d8-189309db535c",
                "control-id": "CIS-1.1.3",
                "description": "Ensure that the controller manager pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the controller manager pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "b736f9d5-69fe-4b73-9f27-bd3af16e375e",
                "control-id": "CIS-1.1.4",
                "description": "Ensure that the controller manager pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the controller manager pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "7442edce-c31a-42e6-a69c-9064f61954a9",
                "control-id": "CIS-1.1.4",
                "description": "Ensure that the controller manager pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the controller manager pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "ed20fe11-158c-441f-aef8-5cb936f3e92a",
                "control-id": "CIS-1.1.5",
                "description": "Ensure that the scheduler pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the scheduler pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "849a350c-020a-43ac-9204-46f28fe4b08c",
                "control-id": "CIS-1.1.6",
                "description": "Ensure that the scheduler pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the scheduler pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "1a4ff758-fe3f-4ebd-a7af-755e5ce35050",
                "control-id": "CIS-1.1.6",
                "description": "Ensure that the scheduler pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the scheduler pod specification file ownership is set to root:root"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  }
                ]
              },
              {
                "uuid": "574a6c2c-6dc3-4251-9ed2-484784c827ec",
                "control-id": "CIS-1.1.7",
                "description": "Ensure that the etcd pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the etcd pod specification file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "8572bffc-8cd0-46f8-84aa-f4e9ff952a7f",
                      "813451c9-5265-447d-b39e-4fbcac440888"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "741d5f7e-2296-4224-ad75-5a60bb30a826"
                    ]
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
