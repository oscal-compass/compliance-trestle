# Tutorial: Setup for and use of Tanium to OSCAL transformer

Here are step by step instructions for setup and transformation of [Tanium](https://www.tanium.com/) compliance data files into [NIST](https://www.nist.gov/) standard [OSCAL](https://pages.nist.gov/OSCAL/) using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) tool.

## *Objective*

How to transform a `Tanium.results` compliance file into a standardized `OSCAL.json` file.

There are 2 short steps shown below.
The first is a one-time check/set-up of your enviroment.
The second is a one-command transformation form Tanium to OSCAL.

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
$ python -V</code>
Python 3.8.3</code>
```

- Setup a virtual environment.

```
$ cd
$ python -m venv venv.trestle
$ source venv.trestle/bin/activate
(venv.trestle)$

```

- Insure you have a modern [pip](https://pip.pypa.io/en/stable/installing/) (19.x or greater).

```
(venv.trestle)$ pip --version
pip 19.2.3 from /home...
```

- Install [compliance-trestle](https://ibm.github.io/compliance-trestle/).

```
(venv.trestle)$ pip install compliance-trestle
Looking in indexes: https://pypi.org/simple,...

```

- Check trestle viability (and view help).

```
(venv.trestle)$ trestle -h
usage: trestle [-h] {init,create,split,merge,replicate,add,remove,validate,import,task,assemble} ...

```

- Create trestle workspace.

```
(venv.trestle)$ mkdir trestle.workspace
(venv.trestle)$ cd trestle.workspace
(venv.trestle)$ trestle init
Initialized trestle project successfully in /home/<user>/trestle.workspace
```

## *Step 2: Transform sample*

- Create Tanium data folders.

```
(venv.trestle)$ mkdir -p tanium/tests/data/tasks/tanium/input
```

- Fetch sample Tanium data file. It is a "raw" Tanium report for which a transformation to OSCAL is desired.

```
(venv.trestle)$ curl 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/tasks/tanium/input/Tanium.comply-nist-results' > tanium/tests/data/tasks/tanium/input/Tanium.comply-nist-results
```

<details>
<summary>sample: Tanium.comply-nist-results</summary>

```
{"IP Address":"fe80::3cd5:564b:940e:49ab","Computer Name":"cmp-wn-2106.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.11","Computer Name":"","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.11","Computer Name":"cmp-wn-2106.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"","Benchmark Version":"","Profile":"","ID":"win_security_ps","Result":"pass","Custom ID":"","Version":""}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.11","Computer Name":"cmp-wn-2106.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"","Benchmark Version":"","Profile":"","ID":"av_service","Result":"fail","Custom ID":"","Version":""}],"Count":"1","Age":"600"}
{"IP Address":"fe80::21f6:c36a:3f45:ac95","Computer Name":"cmp-wn-2115.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.218","Computer Name":"cmp-wn-2115.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.218","Computer Name":"cmp-wn-2115.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days","Result":"fail","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.218","Computer Name":"cmp-wn-2115.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_19.7.44.2.1_L2_Ensure_Prevent_Codec_Download_is_set_to_Enabled","Result":"fail","Custom ID":"800-53: SC-18","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"fe80::186d:aba0:846b:f858","Computer Name":"cmp-wn-2105.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.7","Computer Name":"cmp-wn-2105.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"skip","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.7","Computer Name":"cmp-wn-2105.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days","Result":"fail","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.69.7","Computer Name":"cmp-wn-2105.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"","Benchmark Version":"","Profile":"","ID":"win_security_ps","Result":"pass","Custom ID":"","Version":""}],"Count":"1","Age":"600"}
{"IP Address":"fe80::fcb4:14fa:b62d:ad","Computer Name":"cmp-wn-2108.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.160","Computer Name":"cmp-wn-2108.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.160","Computer Name":"cmp-wn-2108.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days","Result":"fail","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.160","Computer Name":"cmp-wn-2108.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"","Benchmark Version":"","Profile":"","ID":"av_service","Result":"fail","Custom ID":"","Version":""}],"Count":"1","Age":"600"}
{"IP Address":"fe80::20cf:636b:5fe7:b0ff","Computer Name":"cmp-wn-2109.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.77.220","Computer Name":"cmp-wn-2109.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.77.220","Computer Name":"cmp-wn-2109.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days","Result":"fail","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.77.220","Computer Name":"cmp-wn-2109.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"","Benchmark Version":"","Profile":"","ID":"win_security_ps","Result":"pass","Custom ID":"","Version":""}],"Count":"1","Age":"600"}
{"IP Address":"fe80::2585:c75f:8e0:666c","Computer Name":"cmp-wn-2107.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.184","Computer Name":"cmp-wn-2107.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.184","Computer Name":"cmp-wn-2107.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days","Result":"fail","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.184","Computer Name":"cmp-wn-2107.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"","Benchmark Version":"","Profile":"","ID":"win_security_ps","Result":"pass","Custom ID":"","Version":""}],"Count":"1","Age":"600"}
{"IP Address":"fe80::ed25:77c3:b611:eedc","Computer Name":"cmp-wn-2116.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.219","Computer Name":"cmp-wn-2116.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0","Result":"pass","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.219","Computer Name":"cmp-wn-2116.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark","Benchmark Version":"1.5.0.1","Profile":"Windows 10 - NIST 800-53","ID":"xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days","Result":"fail","Custom ID":"800-53: IA-5","Version":"version: 1"}],"Count":"1","Age":"600"}
{"IP Address":"10.8.68.219","Computer Name":"cmp-wn-2116.demo.tanium.local","Comply - JovalCM Results[c2dc8749]":[{"Benchmark":"","Benchmark Version":"","Profile":"","ID":"win_security_ps","Result":"pass","Custom ID":"","Version":""}],"Count":"1","Age":"600"}
```

</details>

- Fetch sample trestle tanium-to-oscal config file. It informs the trestle command where to read input and write output.

```
(venv.trestle)$ curl 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/tasks/tanium/demo-tanium-to-oscal.config' > tanium/demo-tanium-to-oscal.config
```

<details>
<summary>sample: demo-tanium-to-oscal.config</summary>

```
[task.tanium-to-oscal]

input-dir =  tests/data/tasks/tanium/input
output-dir = tests/data/tasks/tanium/runtime

```

</details>

- Perform the transform.

```
(venv.trestle)$ cd tanium
(venv.trestle)$ trestle task tanium-to-oscal -c demo-tanium-to-oscal.config
create: tests/data/tasks/tanium/runtime/Tanium.oscal.json
Rules Analysis:
rules [dispatched]: 28
rules [unique]: 6
results: {'pass': 18, 'fail': 9, 'skip': 1}
Task: tanium-to-oscal executed successfully.

```

- View the generated OSCAL.

```
(venv.trestle)$ cat tests/data/tasks/tanium/runtime/Tanium.oscal.json
```

<details>
<summary>sample:  Tanium.oscal.json</summary>

```
{
  "results": [
    {
      "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
      "title": "Tanium",
      "description": "Tanium",
      "start": "2021-02-24T19:31:13.000+00:00",
      "end": "2021-02-24T19:31:13.000+00:00",
      "local-definitions": {
        "components": {
          "56666738-0f9a-4e38-9aac-c0fad00a5821": {
            "type": "Windows 10",
            "title": "Windows 10",
            "description": "Windows 10",
            "status": {
              "state": "operational"
            }
          }
        },
        "inventory-items": [
          {
            "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "cmp-wn-2106.demo.tanium.local",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "fe80::3cd5:564b:940e:49ab, 10.8.69.11"
              },
              {
                "name": "Count",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              },
              {
                "name": "Age",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "600"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
              }
            ]
          },
          {
            "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "cmp-wn-2115.demo.tanium.local",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "fe80::21f6:c36a:3f45:ac95, 10.8.68.218"
              },
              {
                "name": "Count",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              },
              {
                "name": "Age",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "600"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
              }
            ]
          },
          {
            "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "cmp-wn-2105.demo.tanium.local",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "fe80::186d:aba0:846b:f858, 10.8.69.7"
              },
              {
                "name": "Count",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              },
              {
                "name": "Age",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "600"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
              }
            ]
          },
          {
            "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "cmp-wn-2108.demo.tanium.local",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "fe80::fcb4:14fa:b62d:ad, 10.8.68.160"
              },
              {
                "name": "Count",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              },
              {
                "name": "Age",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "600"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
              }
            ]
          },
          {
            "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "cmp-wn-2109.demo.tanium.local",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "fe80::20cf:636b:5fe7:b0ff, 10.8.77.220"
              },
              {
                "name": "Count",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              },
              {
                "name": "Age",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "600"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
              }
            ]
          },
          {
            "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "cmp-wn-2107.demo.tanium.local",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "fe80::2585:c75f:8e0:666c, 10.8.68.184"
              },
              {
                "name": "Count",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              },
              {
                "name": "Age",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "600"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
              }
            ]
          },
          {
            "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
            "description": "inventory",
            "props": [
              {
                "name": "Computer Name",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "cmp-wn-2116.demo.tanium.local",
                "class": "scc_inventory_item_id"
              },
              {
                "name": "IP Address",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "fe80::ed25:77c3:b611:eedc, 10.8.68.219"
              },
              {
                "name": "Count",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "1"
              },
              {
                "name": "Age",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "600"
              }
            ],
            "implemented-components": [
              {
                "component-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
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
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "win_security_ps",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "win_security_ps",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "av_service",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "av_service",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_19.7.44.2.1_L2_Ensure_Prevent_Codec_Download_is_set_to_Enabled",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_19.7.44.2.1_L2_Ensure_Prevent_Codec_Download_is_set_to_Enabled",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "skip",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "win_security_ps",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "win_security_ps",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "av_service",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "av_service",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "win_security_ps",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "win_security_ps",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "win_security_ps",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "win_security_ps",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "1.5.0.1",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "fail",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "description": "win_security_ps",
          "props": [
            {
              "name": "Benchmark",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_predefined_profile"
            },
            {
              "name": "Benchmark Version",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "",
              "class": "scc_goal_version"
            },
            {
              "name": "ID",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "win_security_ps",
              "class": "scc_goal_name_id"
            },
            {
              "name": "Result",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "pass",
              "class": "scc_result"
            },
            {
              "name": "Timestamp",
              "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
              "value": "2021-02-24T19:31:13+00:00",
              "class": "scc_timestamp"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "56666738-0f9a-4e38-9aac-c0fad00a5821",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-02-24T19:31:13.000+00:00"
        }
      ],
      "findings": [
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "title": "800-53: IA-5",
          "description": "800-53: IA-5",
          "target": {
            "type": "statement-id",
            "id-ref": "800-53: IA-5",
            "props": [
              {
                "name": "Profile",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "Windows 10 - NIST 800-53",
                "class": "scc_predefined_profile"
              },
              {
                "name": "Custom ID",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "800-53: IA-5"
              },
              {
                "name": "Version",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "version: 1",
                "class": "scc_mapping_version"
              }
            ],
            "status": "not-satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            }
          ]
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "title": "win_security_ps",
          "description": "win_security_ps",
          "target": {
            "type": "statement-id",
            "id-ref": "win_security_ps",
            "props": [
              {
                "name": "Profile",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "",
                "class": "scc_predefined_profile"
              },
              {
                "name": "Custom ID",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "win_security_ps"
              },
              {
                "name": "Version",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "",
                "class": "scc_mapping_version"
              }
            ],
            "status": "satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            }
          ]
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "title": "av_service",
          "description": "av_service",
          "target": {
            "type": "statement-id",
            "id-ref": "av_service",
            "props": [
              {
                "name": "Profile",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "",
                "class": "scc_predefined_profile"
              },
              {
                "name": "Custom ID",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "av_service"
              },
              {
                "name": "Version",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "",
                "class": "scc_mapping_version"
              }
            ],
            "status": "not-satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            },
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            }
          ]
        },
        {
          "uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821",
          "title": "800-53: SC-18",
          "description": "800-53: SC-18",
          "target": {
            "type": "statement-id",
            "id-ref": "800-53: SC-18",
            "props": [
              {
                "name": "Profile",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "Windows 10 - NIST 800-53",
                "class": "scc_predefined_profile"
              },
              {
                "name": "Custom ID",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "800-53: SC-18"
              },
              {
                "name": "Version",
                "ns": "http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium",
                "value": "version: 1",
                "class": "scc_mapping_version"
              }
            ],
            "status": "not-satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "56666738-0f9a-4e38-9aac-c0fad00a5821"
            }
          ]
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
