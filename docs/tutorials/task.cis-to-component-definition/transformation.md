# Tutorial: Setup for and use of ComplianceAsCode profile to OSCAL Component Definition transformer

Here are step by step instructions for setup and transformation of [ComplianceAsCode](https://github.com/ComplianceAsCode/content) profile data files into [NIST](https://www.nist.gov/) standard [OSCAL](https://pages.nist.gov/OSCAL/) [Component Definition](https://pages.nist.gov/OSCAL/reference/latest/component-definition/json-outline/) using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) tool.

## *Objective*

How to transform one or more `.profile` compliance files into a standardized `OSCAL.json` file.

There are 2 short steps shown below.
The first is a one-time check/set-up of your environment.
The second is a one-command transformation from `.profile` to `OSCAL.json`.

## *Step 1: Environment setup*

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

- Insure you have a modern [Python](https://www.python.org/downloads/) (3.7, 3.8, 3.9).

```
$ python -V
Python 3.8.7
```

- Setup a virtual environment.

```
$ cd
$ python -m venv venv.trestle
$ source venv.trestle/bin/activate
(venv.trestle)$

```

- Insure you have a modern [pip](https://pip.pypa.io/en/stable/installation/) (19.x or greater).

```
(venv.trestle)$ pip --version
pip 21.2.4 from /home...
```

- Install [compliance-trestle](https://ibm.github.io/compliance-trestle/).

```
(venv.trestle)$ pip install compliance-trestle
Looking in indexes: https://pypi.org/simple,...

```

- Check trestle viability (and view help).

```
(venv.trestle)$ trestle -h
usage: trestle [-h] 
{add,assemble,author,create,describe,href,import,init,merge,partial-object-validate,remove,replicate,split,task,validate,version} ...

```

- Create trestle workspace.

```
(venv.trestle)$ mkdir trestle.workspace
(venv.trestle)$ cd trestle.workspace
(venv.trestle)$ trestle init
Initialized trestle project successfully in /home/<user>/trestle.workspace
```

- View configuration information.

```
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

## *Step 2: Transform profile data (CIS benchmarks)*

- Create data folders.

```
(venv.trestle)$ mkdir -p adjunct-data/cis-benchmarks
(venv.trestle)$ mkdir -p adjunct-data/trestle-configs
```

- Fetch ComplianceAsCode profile data.

```
(venv.trestle)$ curl 'https://raw.githubusercontent.com/ComplianceAsCode/content/master/products/ocp4/profiles/cis-node.profile' > adjunct-data/cis-benchmarks/cis-node.profile
(venv.trestle)$ curl 'https://raw.githubusercontent.com/ComplianceAsCode/content/master/products/ocp4/profiles/cis-node.profile' > adjunct-data/cis-benchmarks/cis.profile

```

- Fetch trestle task files.

```
(venv.trestle)$ curl 'https://https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-component-definition/demo-cis-to-component-definition.config' > adjunct-data/task-files/demo-cis-to-component-definition.config
(venv.trestle)$ curl 'https://https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-component-definition/selected_rules.json' > adjunct-data/task-files/selected_rules.json
(venv.trestle)$ curl 'https://https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-component-definition/enabled_rules.json' > adjunct-data/task-files/enabled_rules.json
```

<details>
<summary>demo-cis-to-component-definition.config</summary>

```
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

```
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
    "file_permissions_etcd_member",
    "file_owner_etcd_member",
    "file_groupowner_etcd_member",
    "file_permissions_cni_conf",
    "file_permissions_multus_conf",
    "file_permissions_ip_allocations",
    "file_perms_openshift_sdn_cniserver_config",
    "kubelet_eviction_thresholds_set_soft_memory_available",
    "kubelet_eviction_thresholds_set_soft_nodefs_available",
    "kubelet_eviction_thresholds_set_soft_nodefs_inodesfree",
    "kubelet_eviction_thresholds_set_soft_imagefs_available",
    "kubelet_eviction_thresholds_set_soft_imagefs_inodesfree",
    "kubelet_eviction_thresholds_set_hard_memory_available",
    "kubelet_eviction_thresholds_set_hard_nodefs_available",
    "kubelet_eviction_thresholds_set_hard_nodefs_inodesfree",
    "kubelet_eviction_thresholds_set_hard_imagefs_available",
    "kubelet_eviction_thresholds_set_hard_imagefs_inodesfree",
    "etcd_unique_ca"
  ]
}

```

</details>

<details>
<summary>enabled_rules.json</summary>
```
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
    "file_permissions_etcd_member",
    "file_owner_etcd_member",
    "file_groupowner_etcd_member",
    "file_permissions_cni_conf",
    "file_permissions_multus_conf",
    "file_permissions_ip_allocations",
    "file_perms_openshift_sdn_cniserver_config",
    "kubelet_eviction_thresholds_set_soft_memory_available",
    "kubelet_eviction_thresholds_set_soft_nodefs_available",
    "kubelet_eviction_thresholds_set_soft_nodefs_inodesfree",
    "kubelet_eviction_thresholds_set_soft_imagefs_available",
    "kubelet_eviction_thresholds_set_soft_imagefs_inodesfree",
    "kubelet_eviction_thresholds_set_hard_memory_available",
    "kubelet_eviction_thresholds_set_hard_nodefs_available",
    "kubelet_eviction_thresholds_set_hard_nodefs_inodesfree",
    "kubelet_eviction_thresholds_set_hard_imagefs_available",
    "kubelet_eviction_thresholds_set_hard_imagefs_inodesfree",
    "etcd_unique_ca"
  ]
}
```

</details>


- Perform and validate the transform.

```
(venv.trestle)$ trestle task cis-to-component-definition -c adjunct-data/task-files/demo-cis-to-component-definition.config
output: component-definitions/cis/component-definition.json
Task: cis-to-component-definition executed successfully.

(venv.trestle)$ trestle validate --all
VALID: Model /home/<user>/trestle.workspace/component-definitions/cis/component-definition.json passed the Validator to confirm the model passes all registered validation tests.

```

- View the generated OSCAL.

```
(venv.trestle)$ cat component-definitions/cis/component-definition.json
```

<details>
<summary>component-definition.json</summary>

```
{
  "component-definition": {
    "uuid": "801a494c-995c-47e6-b260-0b6c74c69c33",
    "metadata": {
      "title": "Component definition for OCP4 profiles",
      "last-modified": "2021-11-17T13:00:44+00:00",
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
          "title": "Indicates the organization responsible for all content represented in the \"document\"."
        }
      ],
      "parties": [
        {
          "uuid": "5984fa8a-d834-4b44-9b86-1cb139baf16b",
          "type": "organization",
          "name": "International Business Machines",
          "remarks": "IBM"
        },
        {
          "uuid": "ef42b0ee-46ea-4af0-908f-a497ce348e72",
          "type": "organization",
          "name": "Customer",
          "remarks": "organization to be customized at account creation only for their Component Definition"
        },
        {
          "uuid": "62eff0cc-a97a-45a8-80a0-17c106cc4eff",
          "type": "organization",
          "name": "ISV",
          "remarks": "organization to be customized at ISV subscription only for their Component Definition"
        }
      ],
      "responsible-parties": [
        {
          "role-id": "prepared-by",
          "party-uuids": [
            "5984fa8a-d834-4b44-9b86-1cb139baf16b"
          ]
        },
        {
          "role-id": "prepared-for",
          "party-uuids": [
            "ef42b0ee-46ea-4af0-908f-a497ce348e72",
            "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
          ]
        },
        {
          "role-id": "content-approver",
          "party-uuids": [
            "5984fa8a-d834-4b44-9b86-1cb139baf16b"
          ]
        }
      ]
    },
    "components": [
      {
        "uuid": "b504fe1c-abb1-4bec-bf38-bdddd73f34f6",
        "type": "Service",
        "title": "OSCO",
        "description": "OSCO",
        "control-implementations": [
          {
            "uuid": "cdb45880-f5ab-4415-8f3b-012cfa82d3ca",
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
                "uuid": "7c073d0e-0670-4a30-8a65-10ae43a83815",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "35d7922e-2794-4cfc-9715-b953366a270a",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "1cb19b3e-e402-45c3-8ded-f47bfd783e62",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "799568f6-b25b-415a-84f2-41c0702edaa8",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "af2e9a66-c490-4d2a-ab0b-b61f3fe155a9",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "7c267f4e-5b34-4086-9dde-45ec792326e5",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "db1f7ec4-0de3-41a0-b815-aeba1291753d",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "7e6109a8-ab1f-4599-9acb-990376948b16",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "fc8f09a8-43a3-4b8e-811b-a1c25a5efb86",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "f2af22b6-4a2c-484e-9930-c363fd7bd52d",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "8cb1fe31-605d-46cb-9aa5-5f69f92b6c0a",
                "control-id": "CIS-1.1.8",
                "description": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "74a0274a-c409-4fbe-81b9-d638a130f660",
                "control-id": "CIS-1.1.8",
                "description": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "36d679f3-bd20-4cac-acac-a561d769f13d",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_cni_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "090c2587-ef48-4ab6-b3d1-5187b5951e6e",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_multus_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "f7aca68c-54df-43e1-8319-722b1c3bc75f",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_ip_allocations",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "2cf5f1fc-c67b-425a-80a9-abf0bdc5e9bf",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_perms_openshift_sdn_cniserver_config",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "15f24146-e258-4934-8a8e-a7e5654ff108",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_memory_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "8ed03260-0101-4ee8-8a5c-d901be0f8100",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_nodefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "88f3db3f-dd48-4925-8b9c-04b65cf07743",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_nodefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "c30637f6-c333-4532-8314-ffce33f075a6",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_imagefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "a8e2a409-6ef6-4030-b95d-0c924910759b",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_imagefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "521a4f71-6fbf-41dd-b0e4-e9955bfd5daa",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_memory_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "ae7714a7-e435-4130-8b4c-9f5f92a873a8",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_nodefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "1aef5512-af43-4e0d-bf90-50cdfbfee29b",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_nodefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "58f502bf-4680-4bb1-b6e6-1839bd04c7de",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_imagefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "79b4541f-05c5-4bf0-a315-74f4eb0891ba",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_imagefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "1c60e94b-a755-4856-a57c-fe99506ee41d",
                "control-id": "CIS-2.7",
                "description": "Ensure that a unique Certificate Authority is used for etcd",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_etcd_unique_ca",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that a unique Certificate Authority is used for etcd"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              }
            ]
          },
          {
            "uuid": "d77d736c-9d4f-4518-b5dc-cada20abe005",
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
                "uuid": "f2f68f7c-b926-40e3-a36e-c82cf0281506",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "d7a7947e-1be2-4b13-865e-313a8a310a2e",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "57e0683f-f4a1-4c4c-ac2d-cf58507becf9",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "b497deaf-7dbf-4bf7-944b-899e9b6b4ce4",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "e7a74fa5-036e-4437-8b62-98012677ad12",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "ab529cc7-7319-44d4-ab70-402a4b31b920",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "b42fad4c-1599-4b7f-8d5d-c0a33a340be3",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "616c95af-ed6e-4e07-bd93-2a8007233da6",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "9ddcd998-4f32-4015-a8c2-4c0b42df7432",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "9795434c-f16c-444d-b569-7ff40913a385",
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
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "da0d0035-89e2-417b-92bb-c0c46e860057",
                "control-id": "CIS-1.1.8",
                "description": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "935c4456-130d-4cdf-acd6-6b42ea9eb3d7",
                "control-id": "CIS-1.1.8",
                "description": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "7acef902-420f-488e-8c65-1f0bfcc0a0cc",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_cni_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "03e31bb7-0392-418d-9e31-af157cbd18e6",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_multus_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "ab2d6e0c-ce93-43b1-abaa-e7b224f6547f",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_ip_allocations",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "653d080c-ee8a-466f-9eca-7edfe1034a0f",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_file_perms_openshift_sdn_cniserver_config",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "b26fcd6c-0aad-4550-93bf-818fd2445489",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_memory_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "7da94d7a-a9c7-4432-927d-35a178a616b7",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_nodefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "b7adf41a-ac28-4ba4-bf85-a8555335cfdf",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_nodefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "e731367e-1820-4666-894b-759de7f674ae",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_imagefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "e1a86160-f228-468c-8adc-2fe54ec8336c",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_imagefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "9ea15f05-ffdf-428b-8db5-1f1f082520f6",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_memory_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "446ec3da-78a8-4a21-ba2c-fc20d404c1ac",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_nodefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "3cb915c3-d7a9-4a48-9927-1f63e8c74bc8",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_nodefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "1d26f20f-5553-4d55-8f82-3522a1e522cf",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_imagefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "0fc2dd39-5917-4099-be36-41c7122e9672",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_imagefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that garbage collection is configured as appropriate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  }
                ]
              },
              {
                "uuid": "468a48bf-6ca7-4aa1-8c0e-89cb6d450aa7",
                "control-id": "CIS-2.7",
                "description": "Ensure that a unique Certificate Authority is used for etcd",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://github.com/ComplianceAsCode/content/tree/master/ocp4",
                    "value": "xccdf_org.ssgproject.content_rule_etcd_unique_ca",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that a unique Certificate Authority is used for etcd"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "ef42b0ee-46ea-4af0-908f-a497ce348e72",
                      "62eff0cc-a97a-45a8-80a0-17c106cc4eff"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "5984fa8a-d834-4b44-9b86-1cb139baf16b"
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
