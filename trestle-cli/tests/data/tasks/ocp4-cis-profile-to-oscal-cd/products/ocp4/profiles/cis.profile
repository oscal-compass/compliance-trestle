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
      #### 1.3 Controller Manager
  # 1.3.1 Ensure that garbage collection is configured as appropriate
    - kubelet_eviction_thresholds_set_soft_memory_available
    - kubelet_eviction_thresholds_set_soft_nodefs_available
