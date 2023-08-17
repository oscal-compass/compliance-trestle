---
authors:
  - Tim
  - Jane
  - Sally
owner: Joe
valid:
  from: 2020-01-01
  to: 2099-12-31
---

# Vulnerability Management (VULN) Defect Checks
## 0. Vulnerability Management Workflow
### 0.1 Data Sources
### 0.2 Fetchers
### 0.3 Data Store
### 0.4 Policy Engine
### 0.5 Ticketing System
## 1. Facts Data Model
### 1.1 Devices
#### Server
#### KubernetesCluster
#### ContainerImage
### 1.2 Vulnerabilities
#### ResourceScan
#### ResourceScanFinding
#### ResourceScanResult
### 1.3 Thresholds
#### CISOOverride
#### CISAKEV
### 1.4 Risks
#### VulnDeviations
### 1.5 Scanner Definition
#### ScannerConfiguration
## 2. Defect Checks
### Sub-capability: Reduce Software/ Firmware Vulnerabilities
#### Vulnerable Software/ Firmware
##### Purpose
##### Assessment Criteria
###### Inputs
###### Rules
####### vuln_prod_os_scan_duedate_check
######## Type
######## Rationale Statement
######## Impact Statement
######## Implementation Description
######## Audit Procedure(s)
######## Remediation Procedure(s)
######## Parameters
####### vuln_prod_os_scan_warning_duedate_check_warning
######## Type
######## Rationale Statement
######## Impact Statement
######## Implementation Description
######## Audit Procedure(s)
######## Remediation Procedure(s)
######## Parameters
###### Additional Outputs
##### Assessment Objectives
