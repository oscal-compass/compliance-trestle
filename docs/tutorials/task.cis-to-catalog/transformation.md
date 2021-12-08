# Tutorial: Setup for and use of ComplianceAsCode profile to OSCAL Catalog transformer

Here are step by step instructions for setup and transformation of [ComplianceAsCode](https://github.com/ComplianceAsCode/content) profile data files into [NIST](https://www.nist.gov/) standard [OSCAL](https://pages.nist.gov/OSCAL/) [Catalog](https://pages.nist.gov/OSCAL/reference/latest/catalog/json-outline/) using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) tool.

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

```
(venv.trestle)$ cd trestle.workspace
```

- View configuration information.

```
(venv.trestle)$ trestle task cis-to-catalog -i
trestle.core.commands.task:102 WARNING: Config file was not configured with the appropriate section for the task: "[task.cis-to-catalog]"
Help information for cis-to-catalog task.

Purpose: Create catalog from from standard (e.g. CIS benchmark).

Configuration flags sit under [task.cis-to-catalog]:
  input-dir              = (required) location to read the compliance-as-code profile files.
  output-dir             = (required) location to write the generated catalog.json file.
  output-overwrite       = (optional) true [default] or false; replace existing output when true.
```

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

- Fetch trestle task file.

```
(venv.trestle)$ curl 'https://https://github.com/IBM/compliance-trestle/blob/develop/docs/tutorials/task.cis-to-catalog/demo-cis-to-catalog.config' > adjunct-data/task-files/demo-cis-to-catalog.config
```

<details>
<summary>demo-cis-to-catalog.config</summary>

```
[task.cis-to-catalog]

input-dir = adjunct-data/cis-benchmarks
output-dir = catalogs/cis
```

</details>

- Perform and validate the transform.

```
(venv.trestle)$ trestle task cis-to-catalog -c adjunct-data/task-files/demo-cis-to-catalog.config
output: catalogs/cis/catalog.json
Task: cis-to-catalog executed successfully.

(venv.trestle)$ trestle validate --all
VALID: Model /home/<user>/trestle.workspace/catalog/cis/catalog.json passed the Validator to confirm the model passes all registered validation tests.

```

- View the generated OSCAL.

```
(venv.trestle)$ cat catlog/cis/catalog.json
```

<details>
<summary>catalog.json</summary>

```
{
  "catalog": {
    "uuid": "19543ebf-4667-48b7-be47-d51154f16fda",
    "metadata": {
      "title": "CIS Red Hat OpenShift Container Platform 4 Benchmark",
      "last-modified": "2021-12-03T13:52:21+00:00",
      "version": "0.29.0",
      "oscal-version": "1.0.0",
      "links": [
        {
          "href": "https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis-node.profile"
        },
        {
          "href": "https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile"
        }
      ]
    },
    "groups": [
      {
        "title": "1 Control Plane Components",
        "groups": [
          {
            "title": "1.1 Master Node Configuration Files",
            "controls": [
              {
                "id": "CIS-1.1.1",
                "title": "1.1.1 Ensure that the API server pod specification file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.2",
                "title": "1.1.2 Ensure that the API server pod specification file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.3",
                "title": "1.1.3 Ensure that the controller manager pod specification file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.4",
                "title": "1.1.4 Ensure that the controller manager pod specification file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.5",
                "title": "1.1.5 Ensure that the scheduler pod specification file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.6",
                "title": "1.1.6 Ensure that the scheduler pod specification file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.7",
                "title": "1.1.7 Ensure that the etcd pod specification file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.8",
                "title": "1.1.8 Ensure that the etcd pod specification file ownership is set to root:root (Automated)"
              },
              {
                "id": "CIS-1.1.9",
                "title": "1.1.9 Ensure that the Container Network Interface file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.10",
                "title": "1.1.10 Ensure that the Container Network Interface file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.11",
                "title": "1.1.11 Ensure that the etcd data directory permissions are set to 700 or more restrictive"
              },
              {
                "id": "CIS-1.1.12",
                "title": "1.1.12 Ensure that the etcd data directory ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.13",
                "title": "1.1.13 Ensure that the admin.conf file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.14",
                "title": "1.1.14 Ensure that the admin.conf file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.15",
                "title": "1.1.15 Ensure that the scheduler.conf file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.16",
                "title": "1.1.16 Ensure that the scheduler.conf file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.17",
                "title": "1.1.17 Ensure that the controller-manager.conf file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.18",
                "title": "1.1.18 Ensure that the controller-manager.conf file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.19",
                "title": "1.1.19 Ensure that the OpenShift PKI directory and file ownership is set to root:root"
              },
              {
                "id": "CIS-1.1.20",
                "title": "1.1.20 Ensure that the OpenShift PKI certificate file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-1.1.21",
                "title": "1.1.21 Ensure that the OpenShift PKI key file permissions are set to 600"
              }
            ]
          },
          {
            "title": "1.2 API Server",
            "controls": [
              {
                "id": "CIS-1.2.1",
                "title": "1.2.1 Ensure that the --anonymous-auth argument is set to false"
              },
              {
                "id": "CIS-1.2.2",
                "title": "1.2.2 Ensure that the --basic-auth-file argument is not set"
              },
              {
                "id": "CIS-1.2.3",
                "title": "1.2.3 Ensure that the --token-auth-file parameter is not set"
              },
              {
                "id": "CIS-1.2.4",
                "title": "1.2.4 Ensure that the --kubelet-https argument is set to true"
              },
              {
                "id": "CIS-1.2.5",
                "title": "1.2.5 Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate"
              },
              {
                "id": "CIS-1.2.6",
                "title": "1.2.6 Ensure that the --kubelet-certificate-authority argument is set as appropriate"
              },
              {
                "id": "CIS-1.2.7",
                "title": "1.2.7 Ensure that the --authorization-mode argument is not set to AlwaysAllow"
              },
              {
                "id": "CIS-1.2.8",
                "title": "1.2.8 Ensure that the --authorization-mode argument includes Node"
              },
              {
                "id": "CIS-1.2.9",
                "title": "1.2.9 Ensure that the --authorization-mode argument includes RBAC"
              },
              {
                "id": "CIS-1.2.10",
                "title": "1.2.10 Ensure that the admission control plugin EventRateLimit is set"
              },
              {
                "id": "CIS-1.2.11",
                "title": "1.2.11 Ensure that the admission control plugin AlwaysAdmit is not set"
              },
              {
                "id": "CIS-1.2.12",
                "title": "1.2.12 Ensure that the admission control plugin AlwaysPullImages is set"
              },
              {
                "id": "CIS-1.2.13",
                "title": "1.2.13 Ensure that the admission control plugin SecurityContextDeny is not set"
              },
              {
                "id": "CIS-1.2.14",
                "title": "1.2.14 Ensure that the admission control plugin ServiceAccount is set"
              },
              {
                "id": "CIS-1.2.15",
                "title": "1.2.15 Ensure that the admission control plugin NamespaceLifecycle is set"
              },
              {
                "id": "CIS-1.2.16",
                "title": "1.2.16 Ensure that the admission control plugin PodSecurityPolicy is set (Automated)"
              },
              {
                "id": "CIS-1.2.17",
                "title": "1.2.17 Ensure that the admission control plugin NodeRestriction is set (Automated)"
              },
              {
                "id": "CIS-1.2.18",
                "title": "1.2.18 Ensure that the --insecure-bind-address argument is not set"
              },
              {
                "id": "CIS-1.2.19",
                "title": "1.2.19 Ensure that the --insecure-port argument is set to 0"
              },
              {
                "id": "CIS-1.2.20",
                "title": "1.2.20 Ensure that the --secure-port argument is not set to 0"
              },
              {
                "id": "CIS-1.2.21",
                "title": "1.2.21 Ensure that the --profiling argument is set to false"
              },
              {
                "id": "CIS-1.2.22",
                "title": "1.2.22 Ensure that the --audit-log-path argument is set"
              },
              {
                "id": "CIS-1.2.23",
                "title": "1.2.23 Ensure that the audit logs are forwarded off the cluster for retention"
              },
              {
                "id": "CIS-1.2.24",
                "title": "1.2.24 Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate"
              },
              {
                "id": "CIS-1.2.25",
                "title": "1.2.25 Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate"
              },
              {
                "id": "CIS-1.2.26",
                "title": "1.2.26 Ensure that the --request-timeout argument is set as appropriate"
              },
              {
                "id": "CIS-1.2.27",
                "title": "1.2.27 Ensure that the --service-account-lookup argument is set to true"
              },
              {
                "id": "CIS-1.2.28",
                "title": "1.2.28 Ensure that the --service-account-key-file argument is set as appropriate"
              },
              {
                "id": "CIS-1.2.29",
                "title": "1.2.29 Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate"
              },
              {
                "id": "CIS-1.2.30",
                "title": "1.2.30 Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate"
              },
              {
                "id": "CIS-1.2.31",
                "title": "1.2.31 Ensure that the --client-ca-file argument is set as appropriate"
              },
              {
                "id": "CIS-1.2.32",
                "title": "1.2.32 Ensure that the --etcd-cafile argument is set as appropriate"
              },
              {
                "id": "CIS-1.2.33",
                "title": "1.2.33 Ensure that the --encryption-provider-config argument is set as appropriate"
              },
              {
                "id": "CIS-1.2.34",
                "title": "1.2.34 Ensure that encryption providers are appropriately configured"
              },
              {
                "id": "CIS-1.2.35",
                "title": "1.2.35 Ensure that the API Server only makes use of Strong Cryptographic Ciphers"
              }
            ]
          },
          {
            "title": "1.3 Controller Manager",
            "controls": [
              {
                "id": "CIS-1.3.1",
                "title": "1.3.1 Ensure that garbage collection is configured as appropriate"
              },
              {
                "id": "CIS-1.3.2",
                "title": "1.3.2 Ensure that controller manager healthz endpoints are protected by RBAC. (Automated)"
              },
              {
                "id": "CIS-1.3.3",
                "title": "1.3.3 Ensure that the --use-service-account-credentials argument is set to true"
              },
              {
                "id": "CIS-1.3.4",
                "title": "1.3.4 Ensure that the --service-account-private-key-file argument is set as appropriate"
              },
              {
                "id": "CIS-1.3.5",
                "title": "1.3.5 Ensure that the --root-ca-file argument is set as appropriate"
              },
              {
                "id": "CIS-1.3.6",
                "title": "1.3.6 Ensure that the RotateKubeletServerCertificate argument is set to true"
              },
              {
                "id": "CIS-1.3.7",
                "title": "1.3.7 Ensure that the --bind-address argument is set to 127.0.0.1"
              }
            ]
          },
          {
            "title": "1.4 Scheduler",
            "controls": [
              {
                "id": "CIS-1.4.1",
                "title": "1.4.1 Ensure that the --profiling argument is set to false  (info only)"
              },
              {
                "id": "CIS-1.4.2",
                "title": "1.4.2 Ensure that the --bind-address argument is set to 127.0.0.1"
              }
            ]
          }
        ]
      },
      {
        "title": "2 etcd",
        "controls": [
          {
            "id": "CIS-2.1",
            "title": "2.1 Ensure that the --cert-file and --key-file arguments are set as appropriate"
          },
          {
            "id": "CIS-2.2",
            "title": "2.2 Ensure that the --client-cert-auth argument is set to true"
          },
          {
            "id": "CIS-2.3",
            "title": "2.3 Ensure that the --auto-tls argument is not set to true"
          },
          {
            "id": "CIS-2.4",
            "title": "2.4 Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate"
          },
          {
            "id": "CIS-2.5",
            "title": "2.5 Ensure that the --peer-client-cert-auth argument is set to true"
          },
          {
            "id": "CIS-2.6",
            "title": "2.6 Ensure that the --peer-auto-tls argument is not set to true"
          },
          {
            "id": "CIS-2.7",
            "title": "2.7 Ensure that a unique Certificate Authority is used for etcd"
          }
        ]
      },
      {
        "title": "3 Control Plane Configuration",
        "groups": [
          {
            "title": "3.1 Authentication and Authorization",
            "controls": [
              {
                "id": "CIS-3.1.1",
                "title": "3.1.1 Client certificate authentication should not be used for users"
              }
            ]
          },
          {
            "title": "3.2 Logging",
            "controls": [
              {
                "id": "CIS-3.2.1",
                "title": "3.2.1 Ensure that a minimal audit policy is created"
              },
              {
                "id": "CIS-3.2.2",
                "title": "3.2.2 Ensure that the audit policy covers key security concerns"
              }
            ]
          }
        ]
      },
      {
        "title": "4 Worker Nodes",
        "groups": [
          {
            "title": "4.1 Worker node configuration",
            "controls": [
              {
                "id": "CIS-4.1.1",
                "title": "4.1.1 Ensure that the kubelet service file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-4.1.2",
                "title": "4.1.2 Ensure that the kubelet service file ownership is set to root:root"
              },
              {
                "id": "CIS-4.1.3",
                "title": "4.1.3 If proxy kubeconfig file exists ensure permissions are set to 644 or more restrictive (Automated)"
              },
              {
                "id": "CIS-4.1.4",
                "title": "4.1.4 If proxy kubeconfig file exists ensure ownership is set to root:root (Manual)"
              },
              {
                "id": "CIS-4.1.5",
                "title": "4.1.5 Ensure that the --kubeconfig kubelet.conf file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-4.1.6",
                "title": "4.1.6 Ensure that the --kubeconfig kubelet.conf file ownership is set to root:root"
              },
              {
                "id": "CIS-4.1.7",
                "title": "4.1.7 Ensure that the certificate authorities file permissions are set to 644 or more restrictive"
              },
              {
                "id": "CIS-4.1.8",
                "title": "4.1.8 Ensure that the client certificate authorities file ownership is set to root:root"
              },
              {
                "id": "CIS-4.1.9",
                "title": "4.1.9 Ensure that the kubelet --config configuration file has permissions set to 644 or more restrictive"
              },
              {
                "id": "CIS-4.1.10",
                "title": "4.1.10 Ensure that the kubelet configuration file ownership is set to root:root"
              }
            ]
          },
          {
            "title": "4.2 Kubelet",
            "controls": [
              {
                "id": "CIS-4.2.1",
                "title": "4.2.1 Ensure that the --anonymous-auth argument is set to false"
              },
              {
                "id": "CIS-4.2.2",
                "title": "4.2.2 Ensure that the --authorization-mode argument is not set to AlwaysAllow"
              },
              {
                "id": "CIS-4.2.3",
                "title": "4.2.3 Ensure that the --client-ca-file argument is set as appropriate"
              },
              {
                "id": "CIS-4.2.4",
                "title": "4.2.4 Ensure that the --read-only-port argument is set to 0"
              },
              {
                "id": "CIS-4.2.5",
                "title": "4.2.5 Ensure that the --streaming-connection-idle-timeout argument is not set to 0"
              },
              {
                "id": "CIS-4.2.6",
                "title": "4.2.6 Ensure that the --protect-kernel-defaults argument is set to true"
              },
              {
                "id": "CIS-4.2.7",
                "title": "4.2.7 Ensure that the --make-iptables-util-chains argument is set to true"
              },
              {
                "id": "CIS-4.2.8",
                "title": "4.2.8 Ensure that the --hostname-override argument is not set"
              },
              {
                "id": "CIS-4.2.9",
                "title": "4.2.9 Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture"
              },
              {
                "id": "CIS-4.2.10",
                "title": "4.2.10 Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate"
              },
              {
                "id": "CIS-4.2.11",
                "title": "4.2.11 Ensure that the --rotate-certificates argument is not set to false"
              },
              {
                "id": "CIS-4.2.12",
                "title": "4.2.12 Verify that the RotateKubeletServerCertificate argument is set to true"
              },
              {
                "id": "CIS-4.2.13",
                "title": "4.2.13 Ensure that the Kubelet only makes use of Strong Cryptographic Ciphers"
              }
            ]
          }
        ]
      },
      {
        "title": "5 Policies",
        "groups": [
          {
            "title": "5.1 RBAC and Service Accounts",
            "controls": [
              {
                "id": "CIS-5.1.1",
                "title": "5.1.1 Ensure that the cluster-admin role is only used where required"
              },
              {
                "id": "CIS-5.1.2",
                "title": "5.1.2 Minimize access to secrets (info)"
              },
              {
                "id": "CIS-5.1.3",
                "title": "5.1.3 Minimize wildcard use in Roles and ClusterRoles (info)"
              },
              {
                "id": "CIS-5.1.4",
                "title": "5.1.4 Minimize access to create pods (info)"
              },
              {
                "id": "CIS-5.1.5",
                "title": "5.1.5 Ensure that default service accounts are not actively used. (info)"
              },
              {
                "id": "CIS-5.1.6",
                "title": "5.1.6 Ensure that Service Account Tokens are only mounted where necessary (info)"
              }
            ]
          },
          {
            "title": "5.2 Pod Security Policies / Security Context Constraints",
            "controls": [
              {
                "id": "CIS-5.2.1",
                "title": "5.2.1 Minimize the admission of privileged containers (info)"
              },
              {
                "id": "CIS-5.2.2",
                "title": "5.2.2 Minimize the admission of containers wishing to share the host process ID namespace (info)"
              },
              {
                "id": "CIS-5.2.3",
                "title": "5.2.3 Minimize the admission of containers wishing to share the host IPC namespace (info)"
              },
              {
                "id": "CIS-5.2.4",
                "title": "5.2.4 Minimize the admission of containers wishing to share the host network namespace (info)"
              },
              {
                "id": "CIS-5.2.5",
                "title": "5.2.5 Minimize the admission of containers with allowPrivilegeEscalation (info)"
              },
              {
                "id": "CIS-5.2.6",
                "title": "5.2.6 Minimize the admission of root containers (info)"
              },
              {
                "id": "CIS-5.2.7",
                "title": "5.2.7 Minimize the admission of containers with the NET_RAW capability (info)"
              },
              {
                "id": "CIS-5.2.8",
                "title": "5.2.8 Minimize the admission of containers with added capabilities (info)"
              },
              {
                "id": "CIS-5.2.9",
                "title": "5.2.9 Minimize the admission of containers with capabilities assigned (info)"
              }
            ]
          },
          {
            "title": "5.3 Network Policies and CNI",
            "controls": [
              {
                "id": "CIS-5.3.1",
                "title": "5.3.1 Ensure that the CNI in use supports Network Policies (info)"
              },
              {
                "id": "CIS-5.3.2",
                "title": "5.3.2 Ensure that all Namespaces have Network Policies defined"
              }
            ]
          },
          {
            "title": "5.4 Secrets Management",
            "controls": [
              {
                "id": "CIS-5.4.1",
                "title": "5.4.1 Prefer using secrets as files over secrets as environment variables (info)"
              },
              {
                "id": "CIS-5.4.2",
                "title": "5.4.2 Consider external secret storage (info)"
              }
            ]
          },
          {
            "title": "5.5 Extensible Admission Control",
            "controls": [
              {
                "id": "CIS-5.5.1",
                "title": "5.5.1 Configure Image Provenance using ImagePolicyWebhook admission controller"
              }
            ]
          },
          {
            "title": "5.6 General Policies",
            "controls": [
              {
                "id": "CIS-5.6.1",
                "title": "5.6.1 Create administrative boundaries between resources using namespaces (info)"
              },
              {
                "id": "CIS-5.6.2",
                "title": "5.6.2 Ensure Seccomp Profile Pod Definitions (info)"
              },
              {
                "id": "CIS-5.6.3",
                "title": "5.6.3 Apply Security Context to your Pods and Containers (info)"
              },
              {
                "id": "CIS-5.6.4",
                "title": "5.6.4 The Default Namespace should not be used (info)"
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
