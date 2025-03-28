---
title: IBM SCC assessment results integration
description: Description of how to use trestle to interchange results with IBM Cloud Security and Compliance Center
---

# Schema of Assessment Results for Interchange with IBM Cloud Security and Compliance Center, SCC

This document depicts the structure and guidelines for creating an OSCAL result object which would be generated by various transformers for different tools such as Tanium to OSCAL and OSCO to OSCAL. Policy Validation Points (PVPs) such as toolchain that directly generate OSCAL results for sending to SCC Exchange API should follow the structure and guidelines described below.

The overall object will be a *results* element of OSCAL Assessment Result schema wrapped in an outer json object as shown below.

```json
{
  "results": [
    {
      "result": "object"
    },
    {
      "result": "object"
    }
  ]
}
```

Each result object represents one assessment scan and should have the required properties as per OSCAL schema. The *start* and *end* represents the start and end datetime of evidence collection activity. The *end* is optional. In addition to these, the result object may contain details about inventory, list of observations (checks) for each inventory, and findings for profile level controls (such as NIST).

```json
{
  "uuid": "cd54e9bf-f4d3-45d6-ae3b-6e8255847dc2",
  "title": "Tanium",
  "description": "Tanium",
  "start": "2021-04-05T20:19:11.000+00:00",
  "end": "2021-04-05T20:19:11.000+00:00",
  "local-definitions": {},
  "reviewed-controls": {},
  "observations": {},
  "findings": {}
}
```

The inventory should be included in *local-definitions* if observations are being reported, but can be omitted if only *findings* are being reported. As *reviewed-controls* is required as per OSCAL schema, an empty object should be included if only observations are being reported. Optionally, the controls for which the status is being reported in *findings* can be captured here. The actual assessment checks being performed on different inventory items should be captured under *observations*. This can be omitted if only *findings* are being reported. As *findings* is required as per OSCAL schema, an empty object can be included if only observations are being reported and no profile controls are being assessed. Otherwise, findings should include the status of profile controls.

## General Guidance

1. All the properties in the source result (tool specific format) should be represented as properties of the right objects in OSCAL such as inventory-items, observations, etc. The properties should have a tool specific namespace to convey that the property names are exactly same as what is coming from specific tools.

1. Not everything from the non-OSCAL results are relevant (required) by SCC. The relevant properties MUST have SCC specific *class* such as scc_inventory_item_id, scc_result, etc. This will help SCC identify corresponding information from different tools and handle them appropriately. SCC MUST store the original property names so that when these are retrieved by tools later, they can get back the same name-value pairs as was there in the input data.

1. There must be a pre-defined set of properties (class values) from SCC for each result object component such as *inventory-items*, *components*, *observations*, etc.

1. A property value MUST be a string of appropriate format.

## Transforms

1. File *Unification SCC class for OSCO and Tanium to OSCAL.xlsx* contains the *SCC class* mapping from Tanium and OpenShift Compliance Operator results data to OSCAL. Although other
   properties are constructed during transformation, only items having *SCC class* are shown
   in the table.

<img src="../Unification-SCC-class-for-OSCO-and-Tanium-to-OSCAL.png"/>

## Inventory

1. Inventory is captured under *local-definitions* in result object. local-definitions can be used to represent inventory items, components, users, etc. For our purposes only components and inventory-items will be used. Components should be used to represent software, services, etc. whereas inventory-items represent specific machines, VMs, network devices, etc. The inventory items should be associated to a component through *implemented-components* as shown below.

   ```json
   {
     "local-definitions": {
       "components": {
         "b3e243a1-4660-4f5a-aa85-159b4b2d69ce": {
           "type": "Operating System",
           "title": "Windows 10",
           "description": "Windows 10",
           "status": {
             "state": "operational"
           }
         }
       },
       "inventory-items": [
         {
           "uuid": "c9fb63cf-d21e-4584-88f8-44d67ea33ba0",
           "description": "inventory",
           "props": [
             {
               "name": "Computer Name",
               "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
               "value": "cmp-wn-2106.demo.tanium.local"
             },
             {
               "name": "Tanium Client IP Address",
               "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
               "value": "192.168.0.120",
               "class": "scc_inventory_item_id"
             },
             {
               "name": "IP Address",
               "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
               "value": "['fe80::cd44:4154:61e8:53ae', '192.168.0.120']"
             },
             {
               "name": "Count",
               "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
               "value": "1"
             }
           ],
           "implemented-components": [
             {
               "component-uuid": "b3e243a1-4660-4f5a-aa85-159b4b2d69ce"
             }
           ]
         }
       ]
     }
   }
   ```

1. Inventory items have one required property with class *scc_inventory_item_id* as shown above. Similarly in some other tool's result the scc_inventory_item_id may be specified through some other property. It is the job of the transformation code to appropriately specify class values for required properties. As shown above, non-mandatory property such as *count* from native result does not have any class specified.

1. The *type* of the inventory item is specified by linking it to *component* via *implemented-components*.

## Observation

1. Loosely speaking, an *observation* object equates with results from a goal check, and the observation is uniquely identified by a uuid, e.g.,

   ```json
   {
     "uuid": "00000000-0000-4000-9999-000000000016",
     "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1_L1_Ensure_Enforce_password_history_is_set_to_24_or_more_passwords"
   }
   ```

1. A sample observation object generated from Tanium result looks like -

   ```json
   {
     "uuid": "74b605f8-7e8c-41b3-9514-2412692fbe01",
     "description": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled",
     "props": [
       {
         "name": "Check ID",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "CIS Red Hat Enterprise Linux 8 Benchmark;1.0.0-1;Level 1 - Server;1;xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled"
       },
       {
         "name": "Check ID Benchmark",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "CIS Red Hat Enterprise Linux 8 Benchmark",
         "class": "scc_predefined_profile"
       },
       {
         "name": "Check ID Version",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "1.0.0-1",
         "class": "scc_check_version"
       },
       {
         "name": "Check ID Version",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "1.0.0-1",
         "class": "scc_predefined_profile_version"
       },
       {
         "name": "Check ID Level",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "Level 1 - Server"
       },
       {
         "name": "Rule ID",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled",
         "class": "scc_goal_description"
       },
       {
         "name": "Rule ID",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "xccdf_org.cisecurity.benchmarks_rule_1.1.1.1_Ensure_mounting_of_cramfs_filesystems_is_disabled",
         "class": "scc_check_name_id"
       },
       {
         "name": "State",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "fail",
         "class": "scc_result"
       },
       {
         "name": "Timestamp",
         "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
         "value": "2021-05-11T22:34:03+00:00",
         "class": "scc_timestamp"
       }
     ],
     "methods": [
       "TEST-AUTOMATED"
     ],
     "subjects": [
       {
         "uuid-ref": "c8919d2b-3300-4f3f-98f6-15a7104c2e04",
         "type": "inventory-item"
       }
     ],
     "collected": "2021-05-11T22:34:03.000+00:00"
   }
   ```

1. An observation has five required properties -

   - *scc_predefined_profile* - identifies both Goal based Profiles (eg CIS-benchmarks, IBM BP etc) and Control/Regulation based Profiles (eg. NIST, FS Cloud etc). The way the integrators or customers will differentiate between the two types of profiles is by the OSCAL element used i.e., Goal based Profiles are defined in the *observation* element which carries the goal id (check id) and posture. Control/Regulation based Profiles  are defined in the *finding* element which carries the control posture, the custom profile name, and the mapping of the goal results to NIST controls
   - *scc_check_version, scc_predefined_profile_version* - gives the version of the goal/profile i.e., CIS benchmark version used for check.
   - *scc_goal_description, scc_check_name_id* - gives the specific goal check (rule) that was assessed from the scc_predefined_profile.
   - *scc_result* - gives the outcome of performing the check. Possible values are - "pass", "fail", "error" , "unknown", "notchecked", "notapplicable".
   - *scc_timestamp* - datetime for this observation. This can be date and time when this observation was performed or reported.

1. Targets such as systems or services MUST be a *subject* in the observation, which MUST be identified by a *uuid-ref* value pointing to the subject in local-definitions.

## Finding

1. A *finding* represents the assessment of a profile control such as NIST 800-53: AC-1 and the related observations. A sample finding object looks like -

   ```json
   {
     "uuid": "cde35fad-3922-4046-8ef8-830e77ffd75a",
     "title": "800-53: IA-5",
     "description": "800-53: IA-5",
     "target": {
       "type": "statement-id",
       "id-ref": "800-53: IA-5",
       "props": [
         {
           "name": "Profile",
           "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
           "value": "Windows 10 - NIST 800-53",
           "class": "scc_predefined_profile"
         },
         {
           "name": "Version",
           "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
           "value": "version: 1",
           "class": "scc_predefined_profile_version"
         },
         {
           "name": "Custom ID",
           "ns": "https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/tanium",
           "value": "800-53: IA-5"
         }
       ],
       "status": "not-satisfied"
     },
     "related-observations": [
       {
         "observation-uuid": "d8bd1785-b95f-45c9-9fa8-32a362845102"
       },
       {
         "observation-uuid": "d06c6f13-5006-4e2d-b3f3-5cdb577473b1"
       }
     ]
   }
   ```

1. A finding has two required property *scc_predefined_profile* that gives the name of the profile whose control is specified in "id-ref", and *scc_predefined_profile_version*.

1. If there is no finding associated with a PVP, a single finding will be created (to preserve valid OSCAL) where the UUID maps to a 'all zeros' UUID e.g.:

   ```json
   {
     "uuid": "00000000-0000-4000-8000-000000000000",
     "title": "No finding",
     "description": "No finding."
   }
   ```
