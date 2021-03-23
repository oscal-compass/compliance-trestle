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

* Insure you have a modern [Python](https://www.python.org/downloads/) (3.7, 3.8, 3.9).

```
$ python -V</code>
Python 3.8.3</code>
```

* Setup a virtual environment.

```
$ cd
$ python -m venv venv.trestle
$ source venv.trestle/bin/activate
(venv.trestle)$

```
* Insure you have a modern [pip](https://pip.pypa.io/en/stable/installing/) (19.x or greater).

```
(venv.trestle)$ pip --version
pip 19.2.3 from /home...
```
* Install [compliance-trestle](https://ibm.github.io/compliance-trestle/).

```
(venv.trestle)$ pip install compliance-trestle
Looking in indexes: https://pypi.org/simple,...

```

* Check trestle viability (and view help).

```
(venv.trestle)$ trestle -h
usage: trestle [-h] {init,create,split,merge,replicate,add,remove,validate,import,task,assemble} ...

```
* Create trestle workspace.

```
(venv.trestle)$ mkdir trestle.workspace
(venv.trestle)$ cd trestle.workspace
(venv.trestle)$ trestle init
Initialized trestle project successfully in /home/<user>/trestle.workspace
```


## *Step 2: Transform sample*

* Create Tanium data folders.

```
(venv.trestle)$ mkdir -p tanium/tests/data/tasks/tanium/input
```


* Fetch sample Tanium data file. It is a "raw" Tanium report for which a transformation to OSCAL is desired.

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

* Fetch sample trestle tanium-to-oscal config file. It informs the trestle command where to read input and write output.

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

* Perform the transform.

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

* View the generated OSCAL.

```
(venv.trestle)$ cat tests/data/tasks/tanium/runtime/Tanium.oscal.json
```


<details>
<summary>sample:  Tanium.oscal.json</summary>

```
{
  "results": [
    {
      "uuid": "6b035143-6fcb-46f8-ae62-1aa42d06356d",
      "title": "Tanium",
      "description": "Tanium",
      "start": "2021-03-13T15:15:55.000+00:00",
      "local-definitions": {
        "inventory-items": [
          {
            "uuid": "92c0992e-c37a-4863-8682-de62666012de",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2106.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "fe80::3cd5:564b:940e:49ab"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "794fdc22-ed15-4abf-bf5f-48bebacef2f6",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": ""
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "10.8.69.11"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "e8642e4e-6cc7-4466-900f-b6d9116810fc",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2115.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "fe80::21f6:c36a:3f45:ac95"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "75f579b6-ff78-4c2d-af04-802a1712295f",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2115.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "10.8.68.218"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "beb2b8fb-0d30-4501-b762-ecbcf22dc0c3",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2105.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "fe80::186d:aba0:846b:f858"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "cfe46a99-6b1d-43cf-9996-18713eca66bf",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2105.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "10.8.69.7"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "aaed9c5e-8b67-478f-a2d3-bead5a747333",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2108.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "fe80::fcb4:14fa:b62d:ad"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "9593c80e-678f-4e67-9306-b84ec1c6e1a5",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2108.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "10.8.68.160"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "dcfb719f-7990-4e30-99c5-c6bfc5ae431e",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2109.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "fe80::20cf:636b:5fe7:b0ff"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "eaec04d2-3283-41a7-91df-26724f360342",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2109.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "10.8.77.220"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "18162697-08ee-40b9-8cc6-ee72fb09f75b",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2107.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "fe80::2585:c75f:8e0:666c"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "f6e60268-1f07-4066-8f4e-a146492f8d0e",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2107.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "10.8.68.184"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "1c9206ba-613e-4471-b256-3e1a83b8a417",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2116.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "fe80::ed25:77c3:b611:eedc"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
              }
            ]
          },
          {
            "uuid": "70e3f8b2-150c-41f6-b0a0-c4dfe6174c03",
            "description": "inventory-item",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "cmp-wn-2116.demo.tanium.local"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "10.8.68.219"
              },
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": " inventory-item",
                "value": "Windows 10"
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
          "uuid": "372d97c9-0c47-4776-890f-316856eebb2c",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "92c0992e-c37a-4863-8682-de62666012de",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "1dbfecb0-0434-42b6-b49e-3699e3373233",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "794fdc22-ed15-4abf-bf5f-48bebacef2f6",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "b420c818-bb03-4570-8731-dd29cfc9a0eb",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": ""
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "class": "id",
              "value": "win_security_ps"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://tanium",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "794fdc22-ed15-4abf-bf5f-48bebacef2f6",
              "type": "inventory-item",
              "title": "N/A"
            }
          ]
        },
        {
          "uuid": "9e5a7882-7a06-495a-8135-606eaecaa631",
          "description": "av_service",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": ""
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "class": "id",
              "value": "av_service"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://tanium",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "794fdc22-ed15-4abf-bf5f-48bebacef2f6",
              "type": "inventory-item",
              "title": "N/A"
            }
          ]
        },
        {
          "uuid": "6800d9cd-7d26-4898-b7a7-56d03a528c96",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "e8642e4e-6cc7-4466-900f-b6d9116810fc",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "ae23c09e-24ac-4bc9-ae9e-d0d9efe3a86f",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "75f579b6-ff78-4c2d-af04-802a1712295f",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "0f7ee272-0dc5-4374-bd79-4ae101d18407",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "75f579b6-ff78-4c2d-af04-802a1712295f",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "9970018e-ba1d-4374-8be7-d20ae6b4c08f",
          "description": "xccdf_org.cisecurity.benchmarks_rule_19.7.44.2.1_L2_Ensure_Prevent_Codec_Download_is_set_to_Enabled",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_19.7.44.2.1_L2_Ensure_Prevent_Codec_Download_is_set_to_Enabled"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "75f579b6-ff78-4c2d-af04-802a1712295f",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "f5618e4f-54be-4780-89c6-207a2bf2e178",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "beb2b8fb-0d30-4501-b762-ecbcf22dc0c3",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "1301229a-3957-4d56-886e-888594450bd8",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "skip"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "cfe46a99-6b1d-43cf-9996-18713eca66bf",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "c8611cbb-ada0-40ae-870a-3a08ebd53dc1",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "cfe46a99-6b1d-43cf-9996-18713eca66bf",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "761f1d9f-a0f1-4ab1-9147-95ff4efa6373",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": ""
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "class": "id",
              "value": "win_security_ps"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://tanium",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "cfe46a99-6b1d-43cf-9996-18713eca66bf",
              "type": "inventory-item",
              "title": "N/A"
            }
          ]
        },
        {
          "uuid": "23a6a47f-3f39-4707-8f36-5a8730079e60",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "aaed9c5e-8b67-478f-a2d3-bead5a747333",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "a2f3ecc7-0f9a-4f86-b2ac-1e44d49d399c",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "9593c80e-678f-4e67-9306-b84ec1c6e1a5",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "7cb083e8-a734-4387-9712-225484c88066",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "9593c80e-678f-4e67-9306-b84ec1c6e1a5",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "5886df1f-8e9a-48d6-874c-aefa352dbf9c",
          "description": "av_service",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": ""
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "class": "id",
              "value": "av_service"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://tanium",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "9593c80e-678f-4e67-9306-b84ec1c6e1a5",
              "type": "inventory-item",
              "title": "N/A"
            }
          ]
        },
        {
          "uuid": "8f755919-6188-4c59-a260-4124f756caea",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "dcfb719f-7990-4e30-99c5-c6bfc5ae431e",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "aa0a1d88-ed97-4fc0-b8c0-381628ade77e",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "eaec04d2-3283-41a7-91df-26724f360342",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "ac97b33c-e8a0-417b-b281-4c8b980ae510",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "eaec04d2-3283-41a7-91df-26724f360342",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "e7a04b3f-3b93-459a-953b-2b1882b8cba9",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": ""
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "class": "id",
              "value": "win_security_ps"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://tanium",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "eaec04d2-3283-41a7-91df-26724f360342",
              "type": "inventory-item",
              "title": "N/A"
            }
          ]
        },
        {
          "uuid": "37c94def-a074-47c4-949f-a502b948f08e",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "18162697-08ee-40b9-8cc6-ee72fb09f75b",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "7a6b1fe2-3033-46d4-9aea-64f5e69eb9af",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "f6e60268-1f07-4066-8f4e-a146492f8d0e",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "969e384a-3bc1-4f16-8348-c3648e63d697",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "f6e60268-1f07-4066-8f4e-a146492f8d0e",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "0197b9f7-dd74-4bc1-8fa7-4d79b5f1cf70",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": ""
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "class": "id",
              "value": "win_security_ps"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://tanium",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "f6e60268-1f07-4066-8f4e-a146492f8d0e",
              "type": "inventory-item",
              "title": "N/A"
            }
          ]
        },
        {
          "uuid": "92f90125-debf-4563-9002-523618255cfc",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "1c9206ba-613e-4471-b256-3e1a83b8a417",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "854633cb-e2d5-434e-905e-7fbe7291d3aa",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.2_L1_Ensure_Maximum_password_age_is_set_to_60_or_fewer_days_but_not_0"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "70e3f8b2-150c-41f6-b0a0-c4dfe6174c03",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "697b07a2-82d4-4d0e-9f8c-bbd4a247c677",
          "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": "CIS Microsoft Windows 10 Enterprise Release 1803 Benchmark"
            },
            {
              "name": "rule",
              "ns": "dns://xccdf",
              "class": "id",
              "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.3_L1_Ensure_Minimum_password_age_is_set_to_1_or_more_days"
            },
            {
              "name": "result",
              "ns": "dns://xccdf",
              "class": "result",
              "value": "fail"
            },
            {
              "name": "time",
              "ns": "dns://xccdf",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "70e3f8b2-150c-41f6-b0a0-c4dfe6174c03",
              "type": "inventory-item",
              "title": "Windows 10"
            }
          ]
        },
        {
          "uuid": "58c1ac67-0464-4d30-b5e3-37579c7f9330",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "class": "source",
              "value": ""
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "class": "id",
              "value": "win_security_ps"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "class": "result",
              "value": "pass"
            },
            {
              "name": "time",
              "ns": "dns://tanium",
              "class": "timestamp",
              "value": "2021-03-13T15:15:55+00:00"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "f5d3493b-94e2-4d23-a8bb-f3078fe8c8dc",
              "type": "component",
              "title": "Windows OS"
            },
            {
              "uuid-ref": "70e3f8b2-150c-41f6-b0a0-c4dfe6174c03",
              "type": "inventory-item",
              "title": "N/A"
            }
          ]
        }
      ],
      "findings": [
        {
          "uuid": "9afdeaf0-55b9-4f4a-a741-d7bd4b1f3562",
          "title": "800-53: IA-5",
          "description": "800-53: IA-5",
          "collected": "2021-03-13T15:15:55.000+00:00",
          "objective-status": {
            "props": [
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": "source",
                "value": "NIST 800-53"
              },
              {
                "name": "id-ref",
                "ns": "dns://tanium",
                "class": "source",
                "value": "IA-5"
              },
              {
                "name": "result",
                "ns": "dns://xccdf",
                "class": "STRVALUE",
                "value": "FAIL"
              }
            ],
            "status": "not-satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "372d97c9-0c47-4776-890f-316856eebb2c"
            },
            {
              "observation-uuid": "6800d9cd-7d26-4898-b7a7-56d03a528c96"
            },
            {
              "observation-uuid": "f5618e4f-54be-4780-89c6-207a2bf2e178"
            },
            {
              "observation-uuid": "23a6a47f-3f39-4707-8f36-5a8730079e60"
            },
            {
              "observation-uuid": "8f755919-6188-4c59-a260-4124f756caea"
            },
            {
              "observation-uuid": "37c94def-a074-47c4-949f-a502b948f08e"
            },
            {
              "observation-uuid": "92f90125-debf-4563-9002-523618255cfc"
            },
            {
              "observation-uuid": "1dbfecb0-0434-42b6-b49e-3699e3373233"
            },
            {
              "observation-uuid": "ae23c09e-24ac-4bc9-ae9e-d0d9efe3a86f"
            },
            {
              "observation-uuid": "1301229a-3957-4d56-886e-888594450bd8"
            },
            {
              "observation-uuid": "a2f3ecc7-0f9a-4f86-b2ac-1e44d49d399c"
            },
            {
              "observation-uuid": "aa0a1d88-ed97-4fc0-b8c0-381628ade77e"
            },
            {
              "observation-uuid": "7a6b1fe2-3033-46d4-9aea-64f5e69eb9af"
            },
            {
              "observation-uuid": "854633cb-e2d5-434e-905e-7fbe7291d3aa"
            },
            {
              "observation-uuid": "0f7ee272-0dc5-4374-bd79-4ae101d18407"
            },
            {
              "observation-uuid": "c8611cbb-ada0-40ae-870a-3a08ebd53dc1"
            },
            {
              "observation-uuid": "7cb083e8-a734-4387-9712-225484c88066"
            },
            {
              "observation-uuid": "ac97b33c-e8a0-417b-b281-4c8b980ae510"
            },
            {
              "observation-uuid": "969e384a-3bc1-4f16-8348-c3648e63d697"
            },
            {
              "observation-uuid": "697b07a2-82d4-4d0e-9f8c-bbd4a247c677"
            }
          ]
        },
        {
          "uuid": "b6a75770-c64b-4d43-b658-01cf4f740458",
          "title": "win_security_ps",
          "description": "win_security_ps",
          "collected": "2021-03-13T15:15:55.000+00:00",
          "objective-status": {
            "props": [
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": "source",
                "value": "N/A"
              },
              {
                "name": "id-ref",
                "ns": "dns://tanium",
                "class": "source",
                "value": "win_security_ps"
              },
              {
                "name": "result",
                "ns": "dns://xccdf",
                "class": "STRVALUE",
                "value": "PASS"
              }
            ],
            "status": "satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "b420c818-bb03-4570-8731-dd29cfc9a0eb"
            },
            {
              "observation-uuid": "761f1d9f-a0f1-4ab1-9147-95ff4efa6373"
            },
            {
              "observation-uuid": "e7a04b3f-3b93-459a-953b-2b1882b8cba9"
            },
            {
              "observation-uuid": "0197b9f7-dd74-4bc1-8fa7-4d79b5f1cf70"
            },
            {
              "observation-uuid": "58c1ac67-0464-4d30-b5e3-37579c7f9330"
            }
          ]
        },
        {
          "uuid": "d0d1b223-e9c8-487b-a57b-3a3f5419d996",
          "title": "av_service",
          "description": "av_service",
          "collected": "2021-03-13T15:15:55.000+00:00",
          "objective-status": {
            "props": [
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": "source",
                "value": "N/A"
              },
              {
                "name": "id-ref",
                "ns": "dns://tanium",
                "class": "source",
                "value": "av_service"
              },
              {
                "name": "result",
                "ns": "dns://xccdf",
                "class": "STRVALUE",
                "value": "FAIL"
              }
            ],
            "status": "not-satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "9e5a7882-7a06-495a-8135-606eaecaa631"
            },
            {
              "observation-uuid": "5886df1f-8e9a-48d6-874c-aefa352dbf9c"
            }
          ]
        },
        {
          "uuid": "b2e3daff-7544-429c-be9f-0cccd9f805d9",
          "title": "800-53: SC-18",
          "description": "800-53: SC-18",
          "collected": "2021-03-13T15:15:55.000+00:00",
          "objective-status": {
            "props": [
              {
                "name": "profile",
                "ns": "dns://tanium",
                "class": "source",
                "value": "NIST 800-53"
              },
              {
                "name": "id-ref",
                "ns": "dns://tanium",
                "class": "source",
                "value": "SC-18"
              },
              {
                "name": "result",
                "ns": "dns://xccdf",
                "class": "STRVALUE",
                "value": "FAIL"
              }
            ],
            "status": "not-satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "9970018e-ba1d-4374-8be7-d20ae6b4c08f"
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

