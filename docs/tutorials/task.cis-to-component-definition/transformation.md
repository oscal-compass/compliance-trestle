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

Purpose: Create component definition from standard (e.g. CIS benchmark).

Configuration flags sit under [task.cis-to-component-definition]:
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
(venv.trestle)$ curl 'https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-component-definition/demo-cis-to-component-definition.config' > adjunct-data/config-files/demo-cis-to-component-definition.config
(venv.trestle)$ curl 'https://github.com/IBM/compliance-trestle/blob/main/docs/tutorials/task.cis-to-component-definition/selected_rules.json' > adjunct-data/task-files/selected_rules.json
(venv.trestle)$ curl 'https://github.com/IBM/compliance-trestle/blob/main/docs/tutorials/task.cis-to-component-definition/enabled_rules.json' > adjunct-data/task-files/enabled_rules.json
```

<details>
<summary>demo-cis-to-component-definition.config</summary>

```shell
[task.cis-to-component-definition]

component-name = OSCO

folder-cac = adjunct-data/cis-benchmarks/content

org-name = International Business Machines
org-remarks = IBM

output-dir = component-definitions/cis

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
  "file_permissions_ovs_pid",
  "file_permissions_ovs_conf_db",
  "file_permissions_ovs_sys_id_conf",
  "file_permissions_ovs_conf_db_lock",
  "file_permissions_ovs_vswitchd_pid",
  "file_permissions_ovsdb_server_pid",
  "file_owner_cni_conf",
  "file_groupowner_cni_conf",
  "file_owner_multus_conf",
  "file_groupowner_multus_conf",
  "file_owner_ip_allocations",
  "file_groupowner_ip_allocations",
  "file_owner_openshift_sdn_cniserver_config",
  "file_groupowner_openshift_sdn_cniserver_config",
  "file_owner_ovs_pid",
  "file_groupowner_ovs_pid",
  "file_owner_ovs_conf_db",
  "file_groupowner_ovs_conf_db",
  "file_owner_ovs_sys_id_conf",
  "file_groupowner_ovs_sys_id_conf",
  "file_owner_ovs_conf_db_lock",
  "file_groupowner_ovs_conf_db_lock",
  "file_owner_ovs_vswitchd_pid",
  "file_groupowner_ovs_vswitchd_pid",
  "file_owner_ovsdb_server_pid",
  "file_groupowner_ovsdb_server_pid",
  "file_permissions_etcd_data_dir",
  "file_permissions_etcd_data_files",
  "file_owner_etcd_data_dir",
  "file_groupowner_etcd_data_dir",
  "file_owner_etcd_data_files",
  "file_groupowner_etcd_data_files",
  "file_permissions_master_admin_kubeconfigs",
  "file_owner_master_admin_kubeconfigs",
  "file_groupowner_master_admin_kubeconfigs",
  "file_permissions_scheduler_kubeconfig",
  "file_owner_scheduler_kubeconfig",
  "file_groupowner_scheduler_kubeconfig",
  "file_permissions_controller_manager_kubeconfig",
  "file_owner_controller_manager_kubeconfig",
  "file_groupowner_controller_manager_kubeconfig",
  "file_owner_openshift_pki_key_files",
  "file_groupowner_openshift_pki_key_files",
  "file_owner_openshift_pki_cert_files",
  "file_groupowner_openshift_pki_cert_files",
  "file_owner_etcd_pki_cert_files",
  "file_groupowner_etcd_pki_cert_files",
  "file_permissions_openshift_pki_cert_files",
  "file_permissions_etcd_pki_cert_files",
  "file_permissions_openshift_pki_key_files",
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
  "file_permissions_worker_service",
  "file_owner_worker_service",
  "file_groupowner_worker_service",
  "file_permissions_kubelet_conf",
  "file_groupowner_kubelet_conf",
  "file_owner_kubelet_conf",
  "file_permissions_worker_ca",
  "file_owner_worker_ca",
  "file_groupowner_worker_ca",
  "file_permissions_worker_kubeconfig",
  "file_owner_worker_kubeconfig",
  "file_groupowner_worker_kubeconfig",
  "kubelet_anonymous_auth",
  "kubelet_authorization_mode",
  "kubelet_configure_client_ca",
  "kubelet_enable_streaming_connections",
  "kubelet_enable_protect_kernel_defaults",
  "kubelet_enable_iptables_util_chains",
  "kubelet_disable_hostname_override",
  "kubelet_configure_event_creation",
  "kubelet_enable_client_cert_rotation",
  "kubelet_enable_cert_rotation",
  "kubelet_enable_server_cert_rotation",
  "kubelet_configure_tls_cipher_suites"
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
(venv.trestle)$ trestle task cis-to-component-definition -c adjunct-data/config-files/demo-cis-to-component-definition.config
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
    "uuid": "06a6c4df-8be1-4636-8a2e-d7bc2409f99b",
    "metadata": {
      "title": "Component definition for OCP4 profiles",
      "last-modified": "2022-01-05T16:19:12+00:00",
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
          "uuid": "9013501d-5788-4c00-822d-117969d239d6",
          "type": "organization",
          "name": "International Business Machines",
          "remarks": "IBM"
        },
        {
          "uuid": "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
          "type": "organization",
          "name": "Customer",
          "remarks": "organization to be customized at account creation only for their Component Definition"
        },
        {
          "uuid": "c96d2ad1-04a9-4323-ba2a-9f9794ac5724",
          "type": "organization",
          "name": "ISV",
          "remarks": "organization to be customized at ISV subscription only for their Component Definition"
        }
      ],
      "responsible-parties": [
        {
          "role-id": "prepared-by",
          "party-uuids": [
            "9013501d-5788-4c00-822d-117969d239d6"
          ]
        },
        {
          "role-id": "prepared-for",
          "party-uuids": [
            "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
            "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
          ]
        },
        {
          "role-id": "content-approver",
          "party-uuids": [
            "9013501d-5788-4c00-822d-117969d239d6"
          ]
        }
      ]
    },
    "components": [
      {
        "uuid": "9736a8c6-73a6-4636-b878-0900f58465a9",
        "type": "Service",
        "title": "OSCO",
        "description": "OSCO",
        "control-implementations": [
          {
            "uuid": "62f1eb5d-0560-4be9-8485-d3ca1254b97e",
            "source": "https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis-node.profile",
            "description": "OSCO implemented controls for CIS Red Hat OpenShift Container Platform 4 Benchmark.",
            "props": [
              {
                "name": "profile_name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                "value": "OCP4 CIS-benchmark v4",
                "class": "scc_profile_name"
              },
              {
                "name": "profile_mnemonic",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                "value": "ocp4-cis-node",
                "class": "scc_profile_mnemonic"
              },
              {
                "name": "profile_version",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
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
                "uuid": "7edf17a0-edc8-4c47-8ad8-7c2b865a3c81",
                "control-id": "CIS-1.1.1",
                "description": "Ensure that the API server pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Kubernetes API Server Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "211a585b-3f3c-407d-895b-f9bcae27eadf",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Kubernetes API Server Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "81c46b12-b464-4f02-8607-71015e9b4b91",
                "control-id": "CIS-1.1.2",
                "description": "Ensure that the API server pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_apiserver",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Kubernetes API Server Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "6060b442-8404-47ed-8149-7ccbb154553e",
                "control-id": "CIS-1.1.3",
                "description": "Ensure that the controller manager pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Kubernetes Controller Manager Pod Specificiation File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "b2e0ef87-3364-488f-8b75-f7a5dd05edf0",
                "control-id": "CIS-1.1.4",
                "description": "Ensure that the controller manager pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Kubernetes Controller Manager Pod Specificiation File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "7a36884d-ea73-43c4-8e7b-3e54a6f88c0d",
                "control-id": "CIS-1.1.4",
                "description": "Ensure that the controller manager pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_controller_manager",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Kubernetes Controller Manager Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "717546c5-92a0-4a43-8833-381ad7785b60",
                "control-id": "CIS-1.1.5",
                "description": "Ensure that the scheduler pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Kubernetes Scheduler Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "657e83d8-3df6-45cc-856d-d832a199e79b",
                "control-id": "CIS-1.1.6",
                "description": "Ensure that the scheduler pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kube_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Kubernetes Scheduler Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "a54189ef-996a-45b9-9c7c-c583e5beecbd",
                "control-id": "CIS-1.1.6",
                "description": "Ensure that the scheduler pod specification file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kube_scheduler",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Kubernetes Scheduler Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "83eed77c-9e53-48ea-bea9-89a5a781f531",
                "control-id": "CIS-1.1.7",
                "description": "Ensure that the etcd pod specification file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Etcd Member Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "3ebe76e2-747c-496c-a19b-f6d70c5931f5",
                "control-id": "CIS-1.1.8",
                "description": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Etcd Member Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "f1e0b6fe-5821-44d6-be78-a5dd71a9899e",
                "control-id": "CIS-1.1.8",
                "description": "Ensure that the etcd pod specification file ownership is set to root:root (Automated)",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_etcd_member",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The etcd Member Pod Specification File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "072e3d39-bca8-49a8-8428-5530d93978f8",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_cni_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the OpenShift Container Network Interface Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "4b2f2a3f-7cfb-470d-b3fe-b620cfb4b028",
                "control-id": "CIS-1.1.9",
                "description": "Ensure that the Container Network Interface file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_multus_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the OpenShift Multus Container Network Interface Plugin Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "74b43de9-56f4-44e5-835d-ca6a1b2449ff",
                "control-id": "CIS-1.1.10",
                "description": "Ensure that the Container Network Interface file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_cni_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The OpenShift Container Network Interface Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "49f05083-a405-4949-9ba0-cb0f322a8299",
                "control-id": "CIS-1.1.10",
                "description": "Ensure that the Container Network Interface file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_cni_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The OpenShift Container Network Interface Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "b998566d-d404-4a11-933f-37cbacccb7c3",
                "control-id": "CIS-1.1.10",
                "description": "Ensure that the Container Network Interface file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_multus_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The OpenShift Multus Container Network Interface Plugin Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "d187ad4b-7188-4c72-a5ed-9bf62b2857dc",
                "control-id": "CIS-1.1.10",
                "description": "Ensure that the Container Network Interface file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_multus_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The OpenShift Multus Container Network Interface Plugin Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "03c393f7-1de1-48f3-8e7e-40f11cf5c09b",
                "control-id": "CIS-1.1.11",
                "description": "Ensure that the etcd data directory permissions are set to 700 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_etcd_data_dir",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Etcd Database Directory"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "404bed52-fbab-4071-8f62-d5317cd3b146",
                "control-id": "CIS-1.1.11",
                "description": "Ensure that the etcd data directory permissions are set to 700 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_etcd_data_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Etcd Write-Ahead-Log Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "04490341-e89b-45b8-afc4-359e6325811f",
                "control-id": "CIS-1.1.12",
                "description": "Ensure that the etcd data directory ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_etcd_data_dir",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Etcd Database Directory"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "d78d2bba-1b4a-4585-afeb-7eaaf48e9247",
                "control-id": "CIS-1.1.12",
                "description": "Ensure that the etcd data directory ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_etcd_data_dir",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Etcd Database Directory"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "c62e0d7b-ec86-4cd0-84df-0721c70ff16b",
                "control-id": "CIS-1.1.12",
                "description": "Ensure that the etcd data directory ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_etcd_data_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Etcd Write-Ahead-Log Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "9c1abbdd-a714-4065-9767-a093c17d8400",
                "control-id": "CIS-1.1.12",
                "description": "Ensure that the etcd data directory ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_etcd_data_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Etcd Write-Ahead-Log Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "b85b87c7-e42a-4049-a53e-0557f53a04ed",
                "control-id": "CIS-1.1.13",
                "description": "Ensure that the admin.conf file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_master_admin_kubeconfigs",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the OpenShift Admin Kubeconfig Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "4568a3ec-e0db-4ac4-a80e-17216a508d2c",
                "control-id": "CIS-1.1.14",
                "description": "Ensure that the admin.conf file ownership is set to root:root ",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_master_admin_kubeconfigs",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The OpenShift Admin Kubeconfig Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "e24877c9-2732-49a2-bd95-e8e3bad3939d",
                "control-id": "CIS-1.1.14",
                "description": "Ensure that the admin.conf file ownership is set to root:root ",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_master_admin_kubeconfigs",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The OpenShift Admin Kubeconfig Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "029254cc-de79-4193-a957-9529a755670e",
                "control-id": "CIS-1.1.15",
                "description": "Ensure that the scheduler.conf file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_scheduler_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Kubernetes Scheduler Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "808410e7-e271-41d5-a5e0-31ff43a604c6",
                "control-id": "CIS-1.1.16",
                "description": "Ensure that the scheduler.conf file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_scheduler_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Kubernetes Scheduler Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "9a331490-feb9-4a1a-9789-331d55ef6e5d",
                "control-id": "CIS-1.1.16",
                "description": "Ensure that the scheduler.conf file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_scheduler_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Kubernetes Scheduler Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "763df124-4dde-4dae-9c69-71f8daf58ff0",
                "control-id": "CIS-1.1.17",
                "description": "Ensure that the controller-manager.conf file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_controller_manager_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the OpenShift Controller Manager Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "9b6dd566-c3ba-4ce9-a2c6-13fe0bdc2cdc",
                "control-id": "CIS-1.1.18",
                "description": "Ensure that the controller-manager.conf file ownership is set to root:root ",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_controller_manager_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The OpenShift Controller Manager Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "824580d2-9d20-4ca5-a81a-cb64731b6f09",
                "control-id": "CIS-1.1.18",
                "description": "Ensure that the controller-manager.conf file ownership is set to root:root ",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_controller_manager_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The OpenShift Controller Manager Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "4eb17715-062d-4f75-b4b2-64014ebd23bb",
                "control-id": "CIS-1.1.19",
                "description": "Ensure that the OpenShift PKI directory and file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_openshift_pki_key_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The OpenShift PKI Private Key Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "a9f4ad7d-95f2-4515-accb-178ce8ae7a09",
                "control-id": "CIS-1.1.19",
                "description": "Ensure that the OpenShift PKI directory and file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_openshift_pki_key_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The OpenShift PKI Private Key Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "a6a75dea-b98a-4e73-857b-c8b4a050efcb",
                "control-id": "CIS-1.1.19",
                "description": "Ensure that the OpenShift PKI directory and file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_openshift_pki_cert_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The OpenShift PKI Certificate Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "3b4f4f47-77dc-49f7-a842-7d32c00ec218",
                "control-id": "CIS-1.1.19",
                "description": "Ensure that the OpenShift PKI directory and file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_openshift_pki_cert_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The OpenShift PKI Certificate Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "2c98e4fe-e45d-4be9-90eb-74c6064d58d4",
                "control-id": "CIS-1.1.19",
                "description": "Ensure that the OpenShift PKI directory and file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_etcd_pki_cert_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Etcd PKI Certificate Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "95dc5f3f-98b5-42d7-9257-00853341f3cc",
                "control-id": "CIS-1.1.19",
                "description": "Ensure that the OpenShift PKI directory and file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_etcd_pki_cert_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Etcd PKI Certificate Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "893f481e-bd40-4818-a57b-b0d7b75f61fa",
                "control-id": "CIS-1.1.20",
                "description": "Ensure that the OpenShift PKI certificate file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_openshift_pki_cert_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the OpenShift PKI Certificate Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "03e45888-b680-46f4-9cc7-a77453fb720d",
                "control-id": "CIS-1.1.20",
                "description": "Ensure that the OpenShift PKI certificate file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_etcd_pki_cert_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Etcd PKI Certificate Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "369e863b-92ce-4f14-9577-3da1eb2632fc",
                "control-id": "CIS-1.1.21",
                "description": "Ensure that the OpenShift PKI key file permissions are set to 600 ",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_openshift_pki_key_files",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the OpenShift PKI Private Key Files"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "41a67b82-b4d5-429d-a861-bffa4f75f21d",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_memory_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionSoft: memory.available"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "676182d4-55ee-4db7-9d03-0430b117c742",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_nodefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionSoft: nodefs.available"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "dea2027f-0359-4e70-9a49-2035c741ed11",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_nodefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionSoft: nodefs.inodesFree"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "3baec849-eef1-4f7c-b807-9f68ed77af39",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_imagefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionSoft: imagefs.available"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "ef39ef95-e8e2-4ab2-974d-982f07b2a6d4",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_soft_imagefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionSoft: imagefs.inodesFree"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "1687e84f-4747-48e3-9c2f-b8fcca848b12",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_memory_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionHard: memory.available"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "7ca1031f-f8f1-48e8-a16d-28178bff5f41",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_nodefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionHard: nodefs.available"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "1a301190-38df-4111-9236-57bbf499fa04",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_nodefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionHard: nodefs.inodesFree"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "835650e3-85b0-49c0-84b0-ff9a2511eaaf",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_imagefs_available",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionHard: imagefs.available"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "2c58ea97-2491-467f-92bd-ea85ad203535",
                "control-id": "CIS-1.3.1",
                "description": "Ensure that garbage collection is configured as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_eviction_thresholds_set_hard_imagefs_inodesfree",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure Eviction threshold Settings Are Set - evictionHard: imagefs.inodesFree"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "544722fc-ca5d-4069-8666-cc1ddefc2dc0",
                "control-id": "CIS-2.7",
                "description": "Ensure that a unique Certificate Authority is used for etcd",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_etcd_unique_ca",
                    "class": "scc_goal_name_id",
                    "remarks": "Configure A Unique CA Certificate for etcd"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "6b8b0cdb-6a17-40e7-9b07-6cb7e4c51507",
                "control-id": "CIS-4.1.1",
                "description": "Ensure that the kubelet service file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_worker_service",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the OpenShift Node Service File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "25f49f5c-6654-473c-90ee-eeb22be80d97",
                "control-id": "CIS-4.1.2",
                "description": "Ensure that the kubelet service file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_worker_service",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The OpenShift Node Service File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "829db23f-acfa-44eb-96b4-a6e6fa94813f",
                "control-id": "CIS-4.1.2",
                "description": "Ensure that the kubelet service file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_worker_service",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The OpenShift Node Service File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "1f475b63-cb5a-4588-b6da-ea58ef56d30d",
                "control-id": "CIS-4.1.5",
                "description": "Ensure that the --kubeconfig kubelet.conf file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_kubelet_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on The Kubelet Configuration File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "ed3c05c2-96f1-4c87-8288-f9f11bdb4522",
                "control-id": "CIS-4.1.6",
                "description": "Ensure that the --kubeconfig kubelet.conf file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_kubelet_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Kubelet Configuration File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "b4861cc6-9ce6-41eb-ad38-8e00fa64474a",
                "control-id": "CIS-4.1.6",
                "description": "Ensure that the --kubeconfig kubelet.conf file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_kubelet_conf",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Kubelet Configuration File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "65b16f0f-c711-4c7e-bd32-0b0d36af104e",
                "control-id": "CIS-4.1.7",
                "description": "Ensure that the certificate authorities file permissions are set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_worker_ca",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Worker Certificate Authority File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "0043332d-b965-46fb-b720-f0f7f6d2ab70",
                "control-id": "CIS-4.1.8",
                "description": "Ensure that the client certificate authorities file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_worker_ca",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns the Worker Certificate Authority File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "30184fe4-6b04-406e-a2a0-a3e89de08a74",
                "control-id": "CIS-4.1.8",
                "description": "Ensure that the client certificate authorities file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_worker_ca",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns the Worker Certificate Authority File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "f22b350a-5f62-4d47-916f-75f6ac796f47",
                "control-id": "CIS-4.1.9",
                "description": "Ensure that the kubelet --config configuration file has permissions set to 644 or more restrictive",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_permissions_worker_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Permissions on the Worker Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "ea0cfa26-04a2-4ca2-876b-ef3cb3f44ebd",
                "control-id": "CIS-4.1.10",
                "description": "Ensure that the kubelet configuration file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_owner_worker_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify User Who Owns The Worker Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "21e487ee-b108-445f-b9f7-2ff1cd34f289",
                "control-id": "CIS-4.1.10",
                "description": "Ensure that the kubelet configuration file ownership is set to root:root",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_file_groupowner_worker_kubeconfig",
                    "class": "scc_goal_name_id",
                    "remarks": "Verify Group Who Owns The Worker Kubeconfig File"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "a92246cc-af13-4e39-94c7-d30227bade5a",
                "control-id": "CIS-4.2.1",
                "description": "Ensure that the --anonymous-auth argument is set to false",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_anonymous_auth",
                    "class": "scc_goal_name_id",
                    "remarks": "Disable Anonymous Authentication to the Kubelet"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "e2c4b9a3-9c5e-4c91-8395-0c034e3e8703",
                "control-id": "CIS-4.2.2",
                "description": "Ensure that the --authorization-mode argument is not set to AlwaysAllow",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_authorization_mode",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure authorization is set to Webhook"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "2ebd2e53-fba5-436c-b1c6-cf0b98e7a88f",
                "control-id": "CIS-4.2.3",
                "description": "Ensure that the --client-ca-file argument is set as appropriate",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_configure_client_ca",
                    "class": "scc_goal_name_id",
                    "remarks": "kubelet - Configure the Client CA Certificate"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "52783785-5c33-4bf1-8343-42b8620eacbe",
                "control-id": "CIS-4.2.5",
                "description": "Ensure that the --streaming-connection-idle-timeout argument is not set to 0",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_enable_streaming_connections",
                    "class": "scc_goal_name_id",
                    "remarks": "kubelet - Do Not Disable Streaming Timeouts"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "a2d9b638-368e-4cee-9b1f-4af7cff572e1",
                "control-id": "CIS-4.2.6",
                "description": "Ensure that the --protect-kernel-defaults argument is set to true",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_enable_protect_kernel_defaults",
                    "class": "scc_goal_name_id",
                    "remarks": "kubelet - Enable Protect Kernel Defaults"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "5b199323-5a53-4f2e-ad93-52ca8e7e1ba0",
                "control-id": "CIS-4.2.7",
                "description": "Ensure that the --make-iptables-util-chains argument is set to true",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_enable_iptables_util_chains",
                    "class": "scc_goal_name_id",
                    "remarks": "kubelet - Allow Automatic Firewall Configuration"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "ba4da2f9-735e-40dc-a419-1d16ee5de6c4",
                "control-id": "CIS-4.2.9",
                "description": "Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_configure_event_creation",
                    "class": "scc_goal_name_id",
                    "remarks": "Kubelet - Ensure Event Creation Is Configured"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "e8662a3e-b823-4327-90d7-c7777ee8bfe5",
                "control-id": "CIS-4.2.11",
                "description": "Ensure that the --rotate-certificates argument is not set to false",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_enable_client_cert_rotation",
                    "class": "scc_goal_name_id",
                    "remarks": "kubelet - Enable Client Certificate Rotation"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "ef753d9c-5257-4e0c-835b-76a28dfb8429",
                "control-id": "CIS-4.2.11",
                "description": "Ensure that the --rotate-certificates argument is not set to false",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_enable_cert_rotation",
                    "class": "scc_goal_name_id",
                    "remarks": "kubelet - Enable Certificate Rotation"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "b19aed9b-84e4-48d3-8113-8f0e7f18872c",
                "control-id": "CIS-4.2.12",
                "description": "Verify that the RotateKubeletServerCertificate argument is set to true",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_enable_server_cert_rotation",
                    "class": "scc_goal_name_id",
                    "remarks": "kubelet - Enable Server Certificate Rotation"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  }
                ]
              },
              {
                "uuid": "c9482835-17d3-44f6-9739-17010e59e4c6",
                "control-id": "CIS-4.2.13",
                "description": "Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers",
                "props": [
                  {
                    "name": "XCCDF_rule",
                    "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ibm-cloud",
                    "value": "xccdf_org.ssgproject.content_rule_kubelet_configure_tls_cipher_suites",
                    "class": "scc_goal_name_id",
                    "remarks": "Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers"
                  }
                ],
                "responsible-roles": [
                  {
                    "role-id": "prepared-by",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
                    ]
                  },
                  {
                    "role-id": "prepared-for",
                    "party-uuids": [
                      "0b2b904c-9fa6-46d6-963b-06ad66ffcd62",
                      "c96d2ad1-04a9-4323-ba2a-9f9794ac5724"
                    ]
                  },
                  {
                    "role-id": "content-approver",
                    "party-uuids": [
                      "9013501d-5788-4c00-822d-117969d239d6"
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
