# Tutorial: Setup for and use of Tanium to OSCAL transformer

Here are step by step instructions for setup and transformation of [Tanium](https://www.tanium.com/) compliance data files into [NIST](https://www.nist.gov/) standard [OSCAL](https://pages.nist.gov/OSCAL/) using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) tool.

## *Objective*

How to transform a `Tanium.results` compliance file into a standardized `OSCAL.json` file.

There are 2 short steps shown below.
The first is a one-time check/set-up of your environment.
The second is a one-command transformation from `Tanium.results` to `OSCAL.json`.

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

```bash
$ python -V
Python 3.8.3
```

- Setup a virtual environment.

```bash
$ cd
$ python -m venv venv.trestle
$ source venv.trestle/bin/activate
(venv.trestle)$

```

- Insure you have a modern [pip](https://pip.pypa.io/en/stable/installing/) (19.x or greater).

```bash
(venv.trestle)$ pip --version
pip 19.2.3 from /home...
```

- Install [compliance-trestle](https://ibm.github.io/compliance-trestle/).

```bash
(venv.trestle)$ pip install compliance-trestle
Looking in indexes: https://pypi.org/simple,...

```

- Check trestle viability (and view help).

```bash
(venv.trestle)$ trestle -h
usage: trestle [-h] {init,create,split,merge,replicate,add,remove,validate,import,task,assemble} ...

```

- Create trestle workspace.

```bash
(venv.trestle)$ mkdir trestle.workspace
(venv.trestle)$ cd trestle.workspace
(venv.trestle)$ trestle init
Initialized trestle project successfully in /home/<user>/trestle.workspace
```

## *Step 2: Transform sample*

- Create Tanium data folders.

```bash
(venv.trestle)$ mkdir -p tanium/tests/data/tasks/tanium/input
```

- Fetch sample Tanium data file. It is a "raw" Tanium report for which a transformation to OSCAL is desired.

```bash
(venv.trestle)$ curl 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/tasks/tanium/input-doc/Tanium.comply-nist-results' > tanium/tests/data/tasks/tanium/input/Tanium.doc-json
```

<details>
<summary>sample: Tanium.doc-json</summary>

```json
{
  "Computer Name": "RHEL8",
  "Tanium Client IP Address": "192.168.0.125",
  "IP Address": [
    "192.168.0.125",
    "192.168.122.1",
    "fe80::3c47:1aff:fe33:601"
  ],
  "Comply - Compliance Findings": [
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled",
      "State": "fail",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.1.3_Ensure_mounting_of_squashfs_filesystems_is_disabled",
      "State": "fail",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.3_Ensure_mounting_of_squashfs_filesystems_is_disabled"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.1.4_Ensure_mounting_of_udf_filesystems_is_disabled",
      "State": "fail",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.4_Ensure_mounting_of_udf_filesystems_is_disabled"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.10_Ensure_noexec_option_set_on_vartmp_partition",
      "State": "pass",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.10_Ensure_noexec_option_set_on_vartmp_partition"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.14_Ensure_nodev_option_set_on_home_partition",
      "State": "pass",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.14_Ensure_nodev_option_set_on_home_partition"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.15_Ensure_nodev_option_set_on_devshm_partition",
      "State": "pass",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.15_Ensure_nodev_option_set_on_devshm_partition"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.16_Ensure_nosuid_option_set_on_devshm_partition",
      "State": "pass",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.16_Ensure_nosuid_option_set_on_devshm_partition"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.17_Ensure_noexec_option_set_on_devshm_partition",
      "State": "fail",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.17_Ensure_noexec_option_set_on_devshm_partition"
    },
    {
      "Check ID": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.18_Ensure_nodev_option_set_on_removable_media_partitions",
      "State": "notchecked",
      "Rule ID": "xccdf_org.cisecurity.benchmarks_rule_1.1.18_Ensure_nodev_option_set_on_removable_media_partitions"
    }
  ],
  "Count": "1"
}
```

</details>

- Fetch sample trestle tanium-to-oscal config file. It informs the trestle command where to read input and write output.

```bash
(venv.trestle)$ curl 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/tasks/tanium/demo-tanium-to-oscal.config' > tanium/demo-tanium-to-oscal.config
```

<details>
<summary>sample: demo-tanium-to-oscal.config</summary>

```conf
[task.tanium-to-oscal]

input-dir =  tests/data/tasks/tanium/input
output-dir = tests/data/tasks/tanium/runtime

```

</details>

- Perform the transform.

```bash
(venv.trestle)$ cd tanium
(venv.trestle)$ trestle task tanium-to-oscal -c demo-tanium-to-oscal.config 
input: tests/data/tasks/tanium/input/Tanium.doc-json
output: tests/data/tasks/tanium/runtime/Tanium.oscal.json
inventory: 1
observations: 9
Task: tanium-to-oscal executed successfully.
```

- View the generated OSCAL.

```bash
(venv.trestle)$ cat tests/data/tasks/tanium/runtime/Tanium.oscal.json
```

<details>
<summary>sample:  Tanium.oscal.json</summary>

```json
{
  "results": [
    {
      "uuid": "f79add8e-488a-45f3-9024-72ecf95c7952",
      "title": "Tanium",
      "description": "Tanium",
      "start": "2021-05-12T13:46:46.000+00:00",
      "end": "2021-05-12T13:46:46.000+00:00",
      "local-definitions": {
        "components": {
          "1ea447fe-a2af-4110-baae-c70ed5223261": {
            "type": "Operating System",
            "title": "Red Hat Enterprise Linux 8",
            "description": "Red Hat Enterprise Linux 8",
            "status": {
              "state": "operational"
            }
          }
        },
        "inventory-items": [
          {
            "uuid": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "RHEL8"
              },
              {
                "name": "Tanium Client IP Address",
                "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "192.168.0.125",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "['192.168.0.125', '192.168.122.1', 'fe80::3c47:1aff:fe33:601']"
              },
              {
                "name": "Count",
                "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "1ea447fe-a2af-4110-baae-c70ed5223261"
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
          "uuid": "e67f5fd9-5b1f-4134-a67e-cebdc2e5735c",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "6cb81459-9c25-4a8b-bf3c-d8ff08ee728c",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.3_Ensure_mounting_of_squashfs_filesystems_is_disabled",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.1.3_Ensure_mounting_of_squashfs_filesystems_is_disabled"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.3_Ensure_mounting_of_squashfs_filesystems_is_disabled",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.3_Ensure_mounting_of_squashfs_filesystems_is_disabled",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "9453eaed-db41-4a20-b684-2887de2d9657",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.4_Ensure_mounting_of_udf_filesystems_is_disabled",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.1.4_Ensure_mounting_of_udf_filesystems_is_disabled"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.4_Ensure_mounting_of_udf_filesystems_is_disabled",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.4_Ensure_mounting_of_udf_filesystems_is_disabled",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "a37c2569-8695-4cfe-8b5c-bd8d6eaf9df7",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.10_Ensure_noexec_option_set_on_vartmp_partition",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.10_Ensure_noexec_option_set_on_vartmp_partition"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.10_Ensure_noexec_option_set_on_vartmp_partition",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.10_Ensure_noexec_option_set_on_vartmp_partition",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "b77e1b49-a818-4d43-adaf-69effcbd9219",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.14_Ensure_nodev_option_set_on_home_partition",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.14_Ensure_nodev_option_set_on_home_partition"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.14_Ensure_nodev_option_set_on_home_partition",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.14_Ensure_nodev_option_set_on_home_partition",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "ac25b329-7a4a-45f4-b42b-1cce470e237b",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.15_Ensure_nodev_option_set_on_devshm_partition",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.15_Ensure_nodev_option_set_on_devshm_partition"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.15_Ensure_nodev_option_set_on_devshm_partition",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.15_Ensure_nodev_option_set_on_devshm_partition",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "f9c0f033-f08b-431d-b411-fe1f63c2c98c",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.16_Ensure_nosuid_option_set_on_devshm_partition",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.16_Ensure_nosuid_option_set_on_devshm_partition"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.16_Ensure_nosuid_option_set_on_devshm_partition",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.16_Ensure_nosuid_option_set_on_devshm_partition",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "149a814e-7f80-4e6d-a613-54f027e0d663",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.17_Ensure_noexec_option_set_on_devshm_partition",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.17_Ensure_noexec_option_set_on_devshm_partition"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.17_Ensure_noexec_option_set_on_devshm_partition",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.17_Ensure_noexec_option_set_on_devshm_partition",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        },
        {
          "uuid": "a0e602b5-e587-41c5-846b-675b26cf3e18",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.18_Ensure_nodev_option_set_on_removable_media_partitions",
          "props": [
            {
              "name": "Check ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.18_Ensure_nodev_option_set_on_removable_media_partitions"
            },
            {
              "name": "Check ID Benchmark",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_check_version"
            },
            {
              "name": "Check ID Version",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.0.0-1",
              "class": "scc_predefined_profile_version"
            },
            {
              "name": "Check ID Level",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "Level 1 - Server"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.18_Ensure_nodev_option_set_on_removable_media_partitions",
              "class": "scc_goal_description"
            },
            {
              "name": "Rule ID",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.18_Ensure_nodev_option_set_on_removable_media_partitions",
              "class": "scc_check_name_id"
            },
            {
              "name": "State",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "notchecked",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-05-12T13:46:46+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "2d33d2b0-af5c-4c37-85b1-e4f414183de2",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-05-12T13:46:46.000+00:00"
        }
      ],
      "findings": [
        {
          "uuid": "00000000-0000-4000-8000-000000000000",
          "title": "No Finding.",
          "description": "No Finding."
        }
      ]
    }
  ]
}
```

</details>

<br>
<br>

<span style="color:green">
Congratulations! You have bridged Tanium data into an OSCAL Assessment Results Findings report using compliance-trestle.
</span>

<br>
<br>
<hr>

<small>Newtown, Victoria</small>

![Australia Scarsdale  Nimons Bridge](800px-Australia_scarsdale_nimons_bridge.jpg)
