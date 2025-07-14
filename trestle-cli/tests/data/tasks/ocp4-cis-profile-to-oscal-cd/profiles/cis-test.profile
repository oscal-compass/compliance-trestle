  ### 1. Control Plane Components
  ###
  #### 1.1 Master Node Configuration Files
  # 1.1.9 Ensure that the Container Network Interface file permissions are set to 644 or more restrictive
    - var_kubelet_evictionsoft_nodefs_available
  # 1.1.10 Ensure that the Container Network Interface file ownership is set to root:root
    - var_kubelet_evictionsoft_nodefs_inodesfree
