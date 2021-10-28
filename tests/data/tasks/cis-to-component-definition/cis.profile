documentation_complete: true

title: 'CIS Red Hat OpenShift Container Platform 4 Benchmark'

platform: ocp4

metadata:
    SMEs:
        - JAORMX
        - mrogers950
        - jhrozek

description: |-
    This profile defines a baseline that aligns to the Center for Internet Security®
    Red Hat OpenShift Container Platform 4 Benchmark™, V0.3, currently unreleased.

    This profile includes Center for Internet Security®
    Red Hat OpenShift Container Platform 4 CIS Benchmarks™ content.

    Note that this part of the profile is meant to run on the Platform that
    Red Hat OpenShift Container Platform 4 runs on top of.

    This profile is applicable to OpenShift versions 4.6 and greater.
selections:
  ### 1 Control Plane Components
  ###
  #### 1.2 API Server
  # 1.2.1 Ensure that the --anonymous-auth argument is set to false
    - api_server_anonymous_auth
  # 1.2.2 Ensure that the --basic-auth-file argument is not set
    - api_server_basic_auth
  # 1.2.3 Ensure that the --token-auth-file parameter is not set
    - api_server_token_auth
  # 1.2.4 Ensure that the --kubelet-https argument is set to true
    - api_server_https_for_kubelet_conn
  # These rules make sure that the services of openshift-apiserver and openshift-oauth-apiserver
  # serve TLS
    - api_server_openshift_https_serving_cert
    - api_server_oauth_https_serving_cert
  # 1.2.5 Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set as appropriate
    - api_server_kubelet_client_cert
    - api_server_kubelet_client_key
  # 1.2.6 Ensure that the --kubelet-certificate-authority argument is set as appropriate
    - api_server_kubelet_certificate_authority
  # 1.2.7 Ensure that the --authorization-mode argument is not set to AlwaysAllow
    - api_server_auth_mode_no_aa
  # 1.2.8 Ensure that the --authorization-mode argument includes Node
    - api_server_auth_mode_node
  # 1.2.9 Ensure that the --authorization-mode argument includes RBAC
    - api_server_auth_mode_rbac
      #### 1.3 Controller Manager
  # 1.3.1 Ensure that garbage collection is configured as appropriate
    - kubelet_eviction_thresholds_set_soft_memory_available
    - kubelet_eviction_thresholds_set_soft_nodefs_available
    - kubelet_eviction_thresholds_set_soft_nodefs_inodesfree
    - kubelet_eviction_thresholds_set_soft_imagefs_available
    - kubelet_eviction_thresholds_set_soft_imagefs_inodesfree
    - kubelet_eviction_thresholds_set_hard_memory_available
    - kubelet_eviction_thresholds_set_hard_nodefs_available
    - kubelet_eviction_thresholds_set_hard_nodefs_inodesfree
    - kubelet_eviction_thresholds_set_hard_imagefs_available
    - kubelet_eviction_thresholds_set_hard_imagefs_inodesfree
