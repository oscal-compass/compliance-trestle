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
(venv.trestle)$ trestle task ocp4-cis-profile-to-oscal-cd -i
trestle.core.commands.task:99 WARNING: Config file was not configured with the appropriate section for the task: "[task.ocp4-cis-profile-to-oscal-cd]"
Help information for ocp4-cis-profile-to-oscal-cd task.

Purpose: Create component definition from standard (e.g. CIS benchmark).

Configuration flags sit under [task.ocp4-cis-profile-to-oscal-cd]:
  component-name         = component name, e.g. OSCO.
  org-name               = organization name, e.g. International Business Machines.
  org-remarks            = organization remarks, e.g. IBM.
  folder-cac             = folder containing compliance-as-code artifacts, e.g adjunct-data/cis-benchmarks/content.
  output-dir             = location to write the generated component-definition.json file.
  profile-name           = profile name, e.g. OCP4 CIS-benchmark v4.
  profile-mnemonic       = profile mnemonic, e.g. ocp4-cis-node.
  profile-ns             = profile ns, e.g. http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud.
  profile-version        = profile version, e.g. 1.1.
  profile-check-version  = profile check version, e.g. 0.1.58.
  profile-type           = profile type, e.g. OCP4.
  profile-list           = profile list is blank separated list of "<suffix>" for config entries: 
                           profile-file.<suffix>, profile-title.<suffix>, profile-url.<suffix>, e.g. cis cis-node.
  profile-file.<suffix>  = path of the profile file to ingest, e.g. ${folder-cac}/products/ocp4/profiles/cis-node.profile.
  profile-title.<suffix> = title of the profile, e.g. CIS Red Hat OpenShift Container Platform 4 Benchmark.
  profile-url.<suffix>   = URL of the profile, e.g. https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile.
  rule-to-parameters-map = map file for set-parameters, e.g. adjunct-data/task-files/rule2var.json.
  selected-rules         = file with list of selected rules, e.g. adjunct-data/task-files/selected_rules.json.
  enabled-rules          = file with list of enabled rules, e.g. adjunct-data/task-files/enabled_rules.json.

Notes:
1. If a control has selected rules but no enabled rules, then all those selected are included.
2. If a control has selected and enabled rules, then only those enabled are included.
3. If a control has no selected rules, then none are included regardless of enabled.
```

- Create data folders.

```shell
(venv.trestle)$ mkdir -p adjunct-data/cis-benchmarks
(venv.trestle)$ mkdir -p adjunct-data/config-files
(venv.trestle)$ mkdir -p adjunct-data/task-files
```

- Fetch ComplianceAsCode data.

```shell
(venv.trestle)$ cd adjunct-data/cis-benchmarks/
(venv.trestle)$ git clone https://github.com/ComplianceAsCode/content.git
(venv.trestle)$ cd -

```

- Fetch trestle config and task files.

```shell
(venv.trestle)$ curl 'https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.ocp4-cis-profile-to-oscal-cd/demo-ocp4-cis-profile-to-oscal-cd.config' > adjunct-data/config-files/demo-ocp4-cis-profile-to-oscal-cd.config
(venv.trestle)$ curl 'https://github.com/IBM/compliance-trestle/blob/main/docs/tutorials/task.ocp4-cis-profile-to-oscal-cd/selected_rules.json' > adjunct-data/task-files/selected_rules.json
(venv.trestle)$ curl 'https://github.com/IBM/compliance-trestle/blob/main/docs/tutorials/task.ocp4-cis-profile-to-oscal-cd/enabled_rules.json' > adjunct-data/task-files/enabled_rules.json
```

<details>
<summary>demo-ocp4-cis-profile-to-oscal-cd.config</summary>

```shell
[task.ocp4-cis-profile-to-oscal-cd]

component-name = OSCO

folder-cac = adjunct-data/cis-benchmarks/content

org-name = International Business Machines
org-remarks = IBM

output-dir = component-definitions/ocp4-cis

profile-name = OCP4 CIS-benchmark v4
profile-mnemonic = ocp4-cis-node
profile-ns = http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud
profile-version = 1.1
profile-check-version = 0.1.58

profile-type = OCP4
profile-list = cis-node cis

profile-file.cis-node = ${folder-cac}/products/ocp4/profiles/cis-node.profile
profile-url.cis-node = https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis-node.profile
profile-title.cis-node = CIS Red Hat OpenShift Container Platform 4 Benchmark

profile-file.cis = ${folder-cac}/products/ocp4/profiles/cis.profile
profile-url.cis = https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile
profile-title.cis = CIS Red Hat OpenShift Container Platform 4 Benchmark

selected-rules  = adjunct-data/task-files/selected_rules.json
enabled-rules  = adjunct-data/task-files/enabled_rules.json
```

</details>

<details>
<summary>selected_rules.json</summary>

```json
[
  "file_permissions_kube_apiserver",
  "file_owner_kube_apiserver",
  "file_groupowner_kube_apiserver"
]
```

</details>

<details>
<summary>enabled_rules.json</summary>

```json
[
  "file_permissions_cni_conf",
  "file_permissions_multus_conf",
  "file_owner_cni_conf",
  "file_groupowner_cni_conf",
  "file_owner_multus_conf",
  "file_groupowner_multus_conf",
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
  "etcd_unique_ca",
  "file_permissions_kubelet_conf",
  "file_groupowner_kubelet_conf",
  "file_owner_kubelet_conf",
  "file_permissions_worker_ca",
  "file_owner_worker_ca",
  "file_groupowner_worker_ca",
  "kubelet_anonymous_auth",
  "kubelet_configure_client_ca",
  "kubelet_enable_streaming_connections",
  "kubelet_enable_iptables_util_chains",
  "kubelet_disable_hostname_override",
  "kubelet_configure_event_creation",
  "kubelet_configure_tls_cipher_suites"
]
```

</details>

- Perform and validate the transform.

```shell
(venv.trestle)$ trestle task ocp4-cis-profile-to-oscal-cd -c adjunct-data/config-files/demo-ocp4-cis-profile-to-oscal-cd.config
output: component-definitions/ocp4-cis/component-definition.json
Task: ocp4-cis-profile-to-oscal-cd executed successfully.

(venv.trestle)$ trestle validate --all
VALID: Model /home/<user>/trestle.workspace/component-definitions/ocp4-cis/component-definition.json passed the Validator to confirm the model passes all registered validation tests.

```

- View the generated OSCAL.

```shell
(venv.trestle)$ cat component-definitions/ocp4-cis/component-definition.json
```

<details>
<summary>component-definition.json</summary>

```json
{
  "component-definition": {
    "uuid": "d1b961ee-188b-42b9-943d-e11dc260f9dc",
    "metadata": {
      "title": "Component definition for OCP4 profiles",
      "last-modified": "2022-01-06T22:43:59+00:00",
      "version": "0.33.0",
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
          "uuid": "d00dff65-e4ae-4344-a206-1e298eff9066",
          "type": "organization",
          "name": "International Business Machines",
          "remarks": "IBM"
        },
        {
          "uuid": "851b55f0-5ba6-4684-8a48-5dad22ba2625",
          "type": "organization",
          "name": "Customer",
          "remarks": "organization to be customized at account creation only for their Component Definition"
        },
        {
          "uuid": "150f9eb7-7fa5-4989-b9be-bc3cba220354",
          "type": "organization",
          "name": "ISV",
          "remarks": "organization to be customized at ISV subscription only for their Component Definition"
        }
      ],
      "responsible-parties": [
        {
          "role-id": "prepared-by",
          "party-uuids": [
            "d00dff65-e4ae-4344-a206-1e298eff9066"
          ]
        },
        {
          "role-id": "prepared-for",
          "party-uuids": [
            "851b55f0-5ba6-4684-8a48-5dad22ba2625",
            "150f9eb7-7fa5-4989-b9be-bc3cba220354"
          ]
        },
        {
          "role-id": "content-approver",
          "party-uuids": [
            "d00dff65-e4ae-4344-a206-1e298eff9066"
          ]
        }
      ]
    },
    "components": [
      {
        "uuid": "e2ee2b93-6103-42de-b615-65b0b3ff2dc4",
        "type": "Service",
        "title": "OSCO",
        "description": "OSCO",
        "control-implementations": [
          {
            "uuid": "f9c2699a-2d2c-4ee2-87f3-042d1a9b3a79",
            "source": "https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis-node.profile",
            "description": "OSCO implemented controls for CIS Red Hat OpenShift Container Platform 4 Benchmark.",
            "props": [
              {
                "name": "profile_name",
                "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                "value": "OCP4 CIS-benchmark v4",
                "class": "scc_profile_name"
              },
              {
                "name": "profile_mnemonic",
                "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                "value": "ocp4-cis-node",
                "class": "scc_profile_mnemonic"
              },
              {
                "name": "profile_version",
                "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
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
                "uuid": "97142b13-bc30-4e72-be7f-36de9149a679",
                "control-id": "CIS-1.1.1",
                "description": "Ensure that the API server pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Kubernetes API Server Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "d00dff65-e4ae-4344-a206-1e298eff9066"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "851b55f0-5ba6-4684-8a48-5dad22ba2625",
                      "150f9eb7-7fa5-4989-b9be-bc3cba220354"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "d00dff65-e4ae-4344-a206-1e298eff9066"
                    ]
                  }
                ]
              },
              {
                "uuid": "0690e2a7-b228-4954-93fe-c1d55936cfa8",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Kubernetes API Server Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "d00dff65-e4ae-4344-a206-1e298eff9066"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "851b55f0-5ba6-4684-8a48-5dad22ba2625",
                      "150f9eb7-7fa5-4989-b9be-bc3cba220354"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "d00dff65-e4ae-4344-a206-1e298eff9066"
                    ]
                  }
                ]
              },
              {
                "uuid": "18c61fb2-8603-440d-9d9a-8d6d1e232cd3",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Kubernetes API Server Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "d00dff65-e4ae-4344-a206-1e298eff9066"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "851b55f0-5ba6-4684-8a48-5dad22ba2625",
                      "150f9eb7-7fa5-4989-b9be-bc3cba220354"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "d00dff65-e4ae-4344-a206-1e298eff9066"
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
