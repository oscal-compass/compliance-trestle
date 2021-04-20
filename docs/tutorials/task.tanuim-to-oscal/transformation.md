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
      "uuid": "cea11208-69f7-4e10-bd71-6ecc391e1d52",
      "title": "Tanium",
      "description": "Tanium",
      "start": "2021-04-06T16:15:26.000+00:00",
      "local-definitions": {
        "inventory-items": [
          {
            "uuid": "d29fe7f7-62c0-4f66-ad5d-ef01bdde3f7d",
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
            "uuid": "30a5703b-14d5-4a96-ab36-df5e4f271d36",
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
          },
          {
            "uuid": "3f80f9b8-da53-4c8c-aa9f-d48a64ee737e",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2115.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "fe80::21f6:c36a:3f45:ac95",
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
            "uuid": "68936e40-6369-4079-8788-57a899afd984",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2115.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "10.8.68.218",
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
            "uuid": "3c4a6883-0583-46f2-b549-bf44c45b667d",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2105.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "fe80::186d:aba0:846b:f858",
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
            "uuid": "01c45e14-e97a-4498-b8e1-115fbcfc494b",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2105.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "10.8.69.7",
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
            "uuid": "f0b05734-daa9-4b19-a632-e432358ff461",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2108.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "fe80::fcb4:14fa:b62d:ad",
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
            "uuid": "ae21f8db-afb4-452b-8969-646c7c4f47a0",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2108.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "10.8.68.160",
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
            "uuid": "b568ce95-e63f-4a78-ae3a-650e6f4b9622",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2109.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "fe80::20cf:636b:5fe7:b0ff",
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
            "uuid": "9578e003-1c88-418a-8f9e-e890bca195a1",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2109.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "10.8.77.220",
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
            "uuid": "e4548b4e-9955-4e7f-a2f5-b2bf876d902d",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2107.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "fe80::2585:c75f:8e0:666c",
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
            "uuid": "761dec7b-7e45-444c-a374-c6ff63867211",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2107.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "10.8.68.184",
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
            "uuid": "1620aa52-b314-4c88-9b13-12ac1b1ef3a4",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2116.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "fe80::ed25:77c3:b611:eedc",
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
            "uuid": "308291b2-40ba-4b23-8be9-f6c59bc17b90",
            "description": "inventory",
            "props": [
              {
                "name": "computer-name",
                "ns": "dns://tanium",
                "value": "cmp-wn-2116.demo.tanium.local",
                "class": " inventory-item"
              },
              {
                "name": "computer-ip",
                "ns": "dns://tanium",
                "value": "10.8.68.219",
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
          "uuid": "94ba09f3-5deb-4660-98d9-ccf75678d388",
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
              "uuid-ref": "d29fe7f7-62c0-4f66-ad5d-ef01bdde3f7d",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "1d305783-7c30-4176-8b6d-a5a13002739b",
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
              "uuid-ref": "30a5703b-14d5-4a96-ab36-df5e4f271d36",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "2cf82258-89ac-4a97-ac0d-09ddfd05857e",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "value": "win_security_ps",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "30a5703b-14d5-4a96-ab36-df5e4f271d36",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "7a401d9a-3198-4816-833f-eb4d29516856",
          "description": "av_service",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "value": "av_service",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "value": "fail",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "30a5703b-14d5-4a96-ab36-df5e4f271d36",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "ed71ec37-5360-4784-b912-8f78474017e1",
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
              "uuid-ref": "3f80f9b8-da53-4c8c-aa9f-d48a64ee737e",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "5e9835d8-da19-4c44-b67f-0a6016b96e54",
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
              "uuid-ref": "68936e40-6369-4079-8788-57a899afd984",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "b65276ab-85b0-42c5-940c-0cd1692c2414",
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
              "uuid-ref": "68936e40-6369-4079-8788-57a899afd984",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "dabfc652-cb06-4562-9af0-50efc4881380",
          "description": "xccdf_org.cisecurity.benchmarks_rule_19.7.44.2.1_L2_Ensure_Prevent_Codec_Download_is_set_to_Enabled",
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
              "value": "xccdf_org.cisecurity.benchmarks_rule_19.7.44.2.1_L2_Ensure_Prevent_Codec_Download_is_set_to_Enabled",
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
              "uuid-ref": "68936e40-6369-4079-8788-57a899afd984",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "0b6f5682-54f0-4bf1-bd06-7c9735f06981",
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
              "uuid-ref": "3c4a6883-0583-46f2-b549-bf44c45b667d",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "18531286-1224-4669-9fe9-a9a84cf270de",
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
              "value": "skip",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "01c45e14-e97a-4498-b8e1-115fbcfc494b",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "17882708-817c-4421-87e2-120c69faffd0",
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
              "uuid-ref": "01c45e14-e97a-4498-b8e1-115fbcfc494b",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "58d87821-a847-463f-a946-66faf278dcc3",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "value": "win_security_ps",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "01c45e14-e97a-4498-b8e1-115fbcfc494b",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "ee109970-b914-46df-b62d-324e824e0446",
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
              "uuid-ref": "f0b05734-daa9-4b19-a632-e432358ff461",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "993580a5-a8f5-4d41-b2e3-b215cda41333",
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
              "uuid-ref": "ae21f8db-afb4-452b-8969-646c7c4f47a0",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "4ad5e138-8f2c-4e61-a264-fb62d378e0c1",
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
              "uuid-ref": "ae21f8db-afb4-452b-8969-646c7c4f47a0",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "5889f5a9-30eb-4bbc-8add-cb8b932cd5eb",
          "description": "av_service",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "value": "av_service",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "value": "fail",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "ae21f8db-afb4-452b-8969-646c7c4f47a0",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "2c1cf710-42bc-40b4-a82f-0628ea81c2fd",
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
              "uuid-ref": "b568ce95-e63f-4a78-ae3a-650e6f4b9622",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "acfdd4f4-f349-4244-8ea1-69d5398636c2",
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
              "uuid-ref": "9578e003-1c88-418a-8f9e-e890bca195a1",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "1b0ed8f2-d9d7-4b14-b8bf-6f094f27a788",
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
              "uuid-ref": "9578e003-1c88-418a-8f9e-e890bca195a1",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "1189e0a5-005a-433f-b60e-c379728c715f",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "value": "win_security_ps",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "9578e003-1c88-418a-8f9e-e890bca195a1",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "192313fb-27c3-436d-8dad-c177bfe42721",
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
              "uuid-ref": "e4548b4e-9955-4e7f-a2f5-b2bf876d902d",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "34ab6ba6-a5f6-4f78-b9aa-5d9407fd0aef",
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
              "uuid-ref": "761dec7b-7e45-444c-a374-c6ff63867211",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "ad2f95f1-b12a-4912-9a8e-b8b95d9f9b42",
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
              "uuid-ref": "761dec7b-7e45-444c-a374-c6ff63867211",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "04a56e7a-5c62-41ed-baad-f1e22e7620ff",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "value": "win_security_ps",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "761dec7b-7e45-444c-a374-c6ff63867211",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "5b20f5b2-493e-4f85-9d47-48aaffa465ef",
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
              "uuid-ref": "1620aa52-b314-4c88-9b13-12ac1b1ef3a4",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "afc8bb87-2cf1-4d2c-86e7-df04e7e46c2d",
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
              "uuid-ref": "308291b2-40ba-4b23-8be9-f6c59bc17b90",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "7837f2aa-b377-44cb-9956-53ed74e6e453",
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
              "uuid-ref": "308291b2-40ba-4b23-8be9-f6c59bc17b90",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        },
        {
          "uuid": "7e4c2e1f-c896-4c6b-8745-54988094c88f",
          "description": "win_security_ps",
          "props": [
            {
              "name": "benchmark",
              "ns": "dns://tanium",
              "value": "",
              "class": "source"
            },
            {
              "name": "rule",
              "ns": "dns://tanium",
              "value": "win_security_ps",
              "class": "id"
            },
            {
              "name": "result",
              "ns": "dns://tanium",
              "value": "pass",
              "class": "result"
            }
          ],
          "methods": [
            "TEST-AUTOMATED"
          ],
          "subjects": [
            {
              "uuid-ref": "308291b2-40ba-4b23-8be9-f6c59bc17b90",
              "type": "inventory-item"
            }
          ],
          "collected": "2021-04-06T16:15:26.000+00:00"
        }
      ],
      "findings": [
        {
          "uuid": "159d92d0-414e-4043-9e55-90e09c637197",
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
              "observation-uuid": "94ba09f3-5deb-4660-98d9-ccf75678d388"
            },
            {
              "observation-uuid": "ed71ec37-5360-4784-b912-8f78474017e1"
            },
            {
              "observation-uuid": "0b6f5682-54f0-4bf1-bd06-7c9735f06981"
            },
            {
              "observation-uuid": "ee109970-b914-46df-b62d-324e824e0446"
            },
            {
              "observation-uuid": "2c1cf710-42bc-40b4-a82f-0628ea81c2fd"
            },
            {
              "observation-uuid": "192313fb-27c3-436d-8dad-c177bfe42721"
            },
            {
              "observation-uuid": "5b20f5b2-493e-4f85-9d47-48aaffa465ef"
            },
            {
              "observation-uuid": "1d305783-7c30-4176-8b6d-a5a13002739b"
            },
            {
              "observation-uuid": "5e9835d8-da19-4c44-b67f-0a6016b96e54"
            },
            {
              "observation-uuid": "18531286-1224-4669-9fe9-a9a84cf270de"
            },
            {
              "observation-uuid": "993580a5-a8f5-4d41-b2e3-b215cda41333"
            },
            {
              "observation-uuid": "acfdd4f4-f349-4244-8ea1-69d5398636c2"
            },
            {
              "observation-uuid": "34ab6ba6-a5f6-4f78-b9aa-5d9407fd0aef"
            },
            {
              "observation-uuid": "afc8bb87-2cf1-4d2c-86e7-df04e7e46c2d"
            },
            {
              "observation-uuid": "b65276ab-85b0-42c5-940c-0cd1692c2414"
            },
            {
              "observation-uuid": "17882708-817c-4421-87e2-120c69faffd0"
            },
            {
              "observation-uuid": "4ad5e138-8f2c-4e61-a264-fb62d378e0c1"
            },
            {
              "observation-uuid": "1b0ed8f2-d9d7-4b14-b8bf-6f094f27a788"
            },
            {
              "observation-uuid": "ad2f95f1-b12a-4912-9a8e-b8b95d9f9b42"
            },
            {
              "observation-uuid": "7837f2aa-b377-44cb-9956-53ed74e6e453"
            }
          ]
        },
        {
          "uuid": "d05dce0c-8c62-49cc-9f68-f7dfd0a4670a",
          "title": "win_security_ps",
          "description": "win_security_ps",
          "target": {
            "type": "objective-id",
            "id-ref": "win_security_ps",
            "props": [
              {
                "name": "profile",
                "ns": "dns://tanium",
                "value": "N/A",
                "class": "source"
              },
              {
                "name": "id-ref",
                "ns": "dns://tanium",
                "value": "win_security_ps",
                "class": "source"
              },
              {
                "name": "result",
                "ns": "dns://xccdf",
                "value": "PASS",
                "class": "STRVALUE"
              }
            ],
            "status": "satisfied"
          },
          "related-observations": [
            {
              "observation-uuid": "2cf82258-89ac-4a97-ac0d-09ddfd05857e"
            },
            {
              "observation-uuid": "58d87821-a847-463f-a946-66faf278dcc3"
            },
            {
              "observation-uuid": "1189e0a5-005a-433f-b60e-c379728c715f"
            },
            {
              "observation-uuid": "04a56e7a-5c62-41ed-baad-f1e22e7620ff"
            },
            {
              "observation-uuid": "7e4c2e1f-c896-4c6b-8745-54988094c88f"
            }
          ]
        },
        {
          "uuid": "e60b9e6c-0001-4360-afe3-8f7ffcbebb34",
          "title": "av_service",
          "description": "av_service",
          "target": {
            "type": "objective-id",
            "id-ref": "av_service",
            "props": [
              {
                "name": "profile",
                "ns": "dns://tanium",
                "value": "N/A",
                "class": "source"
              },
              {
                "name": "id-ref",
                "ns": "dns://tanium",
                "value": "av_service",
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
              "observation-uuid": "7a401d9a-3198-4816-833f-eb4d29516856"
            },
            {
              "observation-uuid": "5889f5a9-30eb-4bbc-8add-cb8b932cd5eb"
            }
          ]
        },
        {
          "uuid": "f27da5da-1759-4fbb-9cee-e1a75a06d866",
          "title": "800-53: SC-18",
          "description": "800-53: SC-18",
          "target": {
            "type": "objective-id",
            "id-ref": "800-53: SC-18",
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
                "value": "800-53: SC-18",
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
              "observation-uuid": "dabfc652-cb06-4562-9af0-50efc4881380"
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
