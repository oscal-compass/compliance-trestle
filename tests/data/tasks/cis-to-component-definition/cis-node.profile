documentation_complete: true

title: 'CIS Red Hat OpenShift Container Platform 4 Benchmark'

platform: ocp4-node

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

    Note that this part of the profile is meant to run on the Operating System that
    Red Hat OpenShift Container Platform 4 runs on top of.

    This profile is applicable to OpenShift versions 4.6 and greater.
selections:
  ### 1. Control Plane Components
  ###
  #### 1.1 Master Node Configuration Files
  # 1.1.1 Ensure that the API server pod specification file permissions are set to 644 or more restrictive
    - file_permissions_kube_apiserver
  # 1.1.2 Ensure that the API server pod specification file ownership is set to root:root
    - file_owner_kube_apiserver
    - file_groupowner_kube_apiserver
  # 1.1.3 Ensure that the controller manager pod specification file permissions are set to 644 or more restrictive
    - file_permissions_kube_controller_manager
  # 1.1.4 Ensure that the controller manager pod specification file ownership is set to root:root
    - file_owner_kube_controller_manager
    - file_groupowner_kube_controller_manager
  # 1.1.5 Ensure that the scheduler pod specification file permissions are set to 644 or more restrictive
    - file_permissions_scheduler
  # 1.1.6 Ensure that the scheduler pod specification file ownership is set to root:root
    - file_owner_kube_scheduler
    - file_groupowner_kube_scheduler
  # 1.1.7 Ensure that the etcd pod specification file permissions are set to 644 or more restrictive
    - file_permissions_etcd_member
  # 1.1.8 Ensure that the etcd pod specification file ownership is set to root:root (Automated)
    - file_owner_etcd_member
    - file_groupowner_etcd_member
  # 1.1.9 Ensure that the Container Network Interface file permissions are set to 644 or more restrictive
    - file_permissions_cni_conf
    - file_permissions_multus_conf
  # 1.1.10 Ensure that the Container Network Interface file ownership is set to root:root
    - file_owner_cni_conf
    - file_groupowner_cni_conf
