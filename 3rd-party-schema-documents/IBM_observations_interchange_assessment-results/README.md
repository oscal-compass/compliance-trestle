# Schema of Assessment Results

This depicts the structure of the interchange object which consists of custom *observations* and OSCAL *metadata*:

```
interchange
|
+---- observations[] (required)
|        |
|        +---- [0] (custom observation)
|        |
|        +---- [1] (custom observation)
|        .
|        .
|        +---- [n] (custom observation)
|
+---- metadata
```

Unlike an OSCAL *result* that contains *observations*, the custom interchange object contains *observations* and *metadata*, the first customized, the second as defined in OSCAL. The interchange *observation* includes two custom properties, *remediation-group* and *parameter-settings*, each as defined by OSCAL.

```
observation (custom)
|
+---- uuid (required)
|
+---- title
|
+---- description (required)
|
+---- props[]
|
+---- annotations[]
|
+---- links[]
|
+---- methods[] (required)
|
+---- types[]
|
+---- assessors[]
|
+---- subjects[]
|
+---- origins[]
|
+---- relevant-evidence[]
|
+---- remarks
|
+---- remediation-group[] (required, custom)
|
+---- parameter-settings (custom)
```

1. The OSCAL *metadata* object MAY be included. An example of its purpose is to specify the schema if tools require or expect it in the actual interchange results.

1. An array called *remediation-group* containing [remediation](https://pages.nist.gov/OSCAL/documentation/schema/assessment-results-layer/assessment-results/json-schema/#remediation) objects, to accommodate test results that do not conform to OSCAL. This avoids having to use some "foreign key" property to associate remediations with an observation. In OSCAL [assessment-results](https://pages.nist.gov/OSCAL/documentation/schema/assessment-results-layer/assessment-results/json-schema/), this corresponds to the *remediations* array of [response or oscal-assessment-common-response](https://pages.nist.gov/OSCAL/documentation/schema/assessment-results-layer/assessment-results/json-schema/#global_oscal-assessment-common-response) objects. OSCAL defines *remediation* within a [risk](https://pages.nist.gov/OSCAL/documentation/schema/assessment-results-layer/assessment-results/json-schema/#global_risk).

   A sample is found in [toolchain_result_observation14.json](toolchain_result_observation14.json), e.g.,

   ```
    "remediation-group" : [
        {
            "uuid" : "00000000-0000-4000-9999-000000000019",
            "description" : "",
            "title" : "",
            "props" : [
                {
                    "ns" : "IBM",
                    "class" : "id",
                    "name" : "issue",
                    "value" : "https://acme.org/foo/123"
                },
                {
                    "ns" : "IBM",
                    "class" : "id",
                    "name" : "issue",
                    "value" : "https://acme.org/foo/125"
                }
            ]
        }
    ]
   ```

   The above references records of issues that describe the remediation in detail.

1. A *parameter-settings* object containing one or more [set-parameter](https://pages.nist.gov/OSCAL/documentation/schema/assessment-results-layer/assessment-results/json-schema/#global_set-parameter_h2) objects, which normally goes inside [modify](https://pages.nist.gov/OSCAL/documentation/schema/profile-layer/profile/json-schema/#global_modify_h2) in an OSCAL [profile](https://pages.nist.gov/OSCAL/documentation/schema/profile-layer/profile/json-schema/), or in an [implemented-requirement](https://pages.nist.gov/OSCAL/documentation/schema/implementation-layer/ssp/json-schema/#global_implemented-requirement) in OSCAL [SSPs](https://pages.nist.gov/OSCAL/documentation/schema/implementation-layer/ssp/json-schema/)

   A sample is found in the same [toolchain_result_observation14.json](toolchain_result_observation14.json), e.g.,

   ```
    "parameter-settings": {
        "reboot": {
            "values": [ "true" ]
        }
    }
   ```

   These are effectively labeled values which can be useful for, say, XCCDF results with *<xccdf:fix>* details.

## General Guidance

1. Loosely speaking, an *observation* object equates with results from a goal, and the observation is uniquely identified by a uuid, e.g.,

   ```
        {
            "uuid" : "00000000-0000-4000-9999-000000000016",
            "title" : "",
            "description" : "Detect Secret observation 2007-09-25",
             ..
         }
   ```

1. The rule for a given result MUST be identified in the observation's *properties* as a property with *"name":"rule"* and *"class":"id"*, e.g.,

   ```
            "props" : [
                {
                    "ns" : "IBM",
                    "class" : "id",
                    "name" : "rule",
                    "value" : "com.ibm.detect_secret"
                }
            ],
   ```

1. Not everything from the non-OSCAL results are relevant. The relevant pieces of information MUST be presented as properties in *subject*, *relevant-evidence*, or *remediation-group*, or as set parameters in *parameter-settings*, if applicable. Less relevant pieces, if included, MUST be presented in annotations. Note that properties of a [subject-reference](https://pages.nist.gov/OSCAL/documentation/schema/assessment-results-layer/assessment-results/json-schema/#global_oscal-assessment-common-subject-reference) go into a *props* array.

1. For properties as above, the *class* key MUST indicate one of these:

   - *id* - a string identifier
   - *link* - a string containing some link or href
   - *result* - a string enumeration indicating one of *PASS*, *FAIL*, *SKIP*, *WARNING*, *ERROR*, or *PARTIAL-PASS*. Note that the original result may format this in other ways, e.g., in lowercase, or as a verb in the past tense, or using some synonym.
   - *timestamp* - as per OSCAL *dateTime-with-timezone*, although some results will need format adjustments, e.g., IBM S&CC collector scans.
   - *info* - some relevant piece of information string that does not fit in the other classes
     In the interest of consistency, all classes are named in singular form, and values given should be singular as well, e.g., if multiple links are to be specified, they should be given as individual link-class properties.

1. All properties MUST be of *ns* (namespace) "IBM". If a different namespace is given, e.g. "SCC", then the property MAY be ignored.

1. A property value MUST be a string of appropriate format.

1. A property's name SHOULD indicate the result source type, such as prefixing with *"xccdf"*, and MAY include hierarchy data, e.g., *"xccdf:TestResult.id"* to name this property as the *id* attribute of the XCCDF *xccdf:TestResult* element. This may be particularly important if the source naming terminology overlaps with OSCAL terminology when they mean different things. For example,

   ```
            {
                "ns": "IBM",
                "class": "id",
                "name": "xccdf:TestResult.id",
                "value": "xccdf_org.example_testresult_ios-test5"
            },
   ```

1. Non-identifying system, component or resource properties, e.g., MAC address or hardware data, MUST be of property class *info*, and MUST NOT be *id*.

1. Targets such as systems or accounts MUST be a *subject-reference*, which MUST be identified by a *uuid-ref* value.

1. All IBM Cloud resources MUST be identified with valid *crn* values. In the property that specifies such a resource, the property class is *id* and the property name is *crn*.

1. An IBM Service ID appearing in a *subject-reference* MUST be presented with valid uuid values, with property class *id* and the property name MUST correspond with the IBM Cloud identifier type, e.g., "pipeline_id" or "pipeline_run_id". ???

1. A result MUST be rendered unique by aggregating, where applicable, the rule-specific identifiers in the OSCAL *observation* properties, in the specific result in the *relevant-evidence*, and subject-specific identifiers in *subject-reference* properties.

1. Less relevant information MUST appear as annotations, either of a *relevant-evidence* or of the relevant *observation*, and MUST NOT be presented in properties. Naming SHOULD be descriptive, such as indicating the source as a prefix, e.g.,

   ```
            {
                "ns": "IBM",
                "name": "xccdf:href",
                "value": "ios-sample-12.4.xccdf.xml"
            },
            {
                "ns": "IBM",
                "name": "xccdf:remark",
                "value": "Test run by Bob on Sept 25, 2007"
            },
   ```

1. Every *PASS* or *FAIL* result MUST be specified as a property of a *relevant-evidence*, with *"class":"result"* and *"name":"result"*, with the actual result in the *"value"* key.

1. Fixes and similar data, if applicable, MUST be supplied as remediations in the *remediation-group*. Such a remediation MUST be supplied with *uuid*, *title* and *description* strings, which are required by OSCAL. The remediation *type* MAY be defined appropriately, e.g., *"issue"* if the remediation just points to a github issue or service request link where details can be found. Otherwise, the details MAY be given in the description instead.

   ```
        "remediation-group" : [
            {
                "uuid" : "00000000-0000-4000-9999-000000000003",
                "title" : "Sample remediation group",
                "description" : "Sample remediation group",
                "props" : [
                    {
                        "ns": "IBM",
                        "class":"info",
                        "name": "xccdf:fix.system",
                        "value": "urn:xccdf:fix:commands"
                    },
               ..
   ```

1. Parameter settings, if applicable, MUST be supplied under *"parameter-settings"* inside the observation. Parameter settings contain labeled *set-parameter* objects. For example,

   ```
        "parameter-settings": {
            "reboot": {
                "values": [ "true" ]
            }
        }
   ```

1. Multi-line strings MUST be broken by the newline escape sequence `\n` inside one string. For example, this property in a remediation:

   ```
                    {
                        "ns": "IBM",
                        "class":"info",
                        "name": "xccdf:fix",
                        "value": "line console\nexec-timeout 10 0\n"
                    }
   ```

1. All values in properties are strings, and there MUST NOT be attempts to provide json values in properties.

## Draft: from Toolchain OPA test results

1. One OPA test result document roughly corresponds with an OSCAL *observation*. Uniqueness of one result document is a combination of the *pipeline_id*, *pipeline_run_id*, *toolchain_crn* and *date*.

1. The IBM toolchain identifier MUST be an *id* class property with *"name":"crn"* of a given *subject-reference*.

1. The IBM toolchain UUID value SHOULD be further identified as a *subject-reference* property with *"class":"id"* and *"name":"pipeline_id*.

   ```
        "subjects" : [
            {
                "uuid-ref" : "00000000-0000-4000-9999-000000000018",
                "type" : "inventory-item",
                "title" : "Toolchain",
                "props" : [
                    {
                        "ns" : "IBM",
                        "class" : "id",
                        "name" : "crn",
                        "value" : "crn:v1:bluemix:public:is:au-syd:a/00000000000000000000000000000000::key:00000000-0000-0000-0000-000000000000"
                    },
                    {
                        "ns" : "IBM",
                        "class" : "id",
                        "name" : "pipeline_id",
                        "value" : "00000000-0000-4000-9999-000000000017"
                    }
                ]
            }
        ],
   ```

1. The toolchain's *pipeline_id* must be defined as a property of a *relevant-evidence* exactly as already defined in the corresponding *subject-reference*, in order to maintain the reference.

1. The instance/run identifier MUST be defined as another property, e.g., *"class":"id"* and *"name":"pipeline_run_id"*.

   ```
        "relevant-evidence" : [
            {
                "href" : "",
                "description" : "",
                "props" : [
                    {
                        "ns" : "IBM",
                        "class" : "id",
                        "name" : "pipeline_id",
                        "value" : "00000000-0000-4000-9999-000000000017"
                    },
                    {
                        "ns" : "IBM",
                        "class" : "id",
                        "name" : "pipeline_run_id",
                        "value" : "12345"
                    },
   ```

1. Likewise, the run timestamp MUST also become a property, with *"class":"timestamp"* and *"name":"time"* with the actual timestamp in the *"value"* key, e.g.,

   ```
   {
       "ns" : "IBM",
       "class" : "timestamp",
       "name" : "time",
       "value" : "2020-05-06T12:00:00-00:00"
   }
   ```

1. If toolchain parameter settings are to be specified, they MUST go under *"parameter-settings"* inside the observation.

1. Other bits of relevant evidence SHOULD appear under annotations of the relevant-evidence.

An example observation for Toolchain OPA results can be found here: [toolchain_result_observation14.json](toolchain_result_observation14.json).

## Draft: from XCCDF TestResult

1. An *xccdf:TestResult* may contain multiple *xccdf:rule-result* elements up to one *xccdf:Benchmark* element.

1. The rule identifier appears in XCCDF as the *idref* attribute value for a given *xccdf:rule-result*.

1. The benchmark is identified in XCCDF as the *id* attribute of the *xccdf:benchmark* element.

1. One particular *xccdf:rule-result* element MUST correspond with one OSCAL *observation*, even if multiple *xccdf:rule-result* elements come in from the same *xccdf:TestResult*.

1. The *xccdf:TestResult* attribute, *id*, MUST be a property of the observation with *"class":"id"* and *"name":TestResult-id"*. This is specified as the unique identifier for the *xccdf:TestResult* element. On the other hand, the *observation* itself MUST be uniquely identified with its *uuid* value.

   ```
   {
       "ns": "IBM",
       "class": "id",
       "name": "TestResult-id",
       "value": "xccdf_org.example_testresult_ios-test5"
   }
   ```

1. The *xccdf:Benchmark* MUST be identified in the OSCAL observation as a property with *"name":"benchmark-id"* and *"class":"id"*, e.g.,

   ```
   {
       "ns": "IBM",
       "class": "id",
       "name": "benchmark-id",
       "value": "xccdf_org.example_benchmark_ios-test-benchmark"
   }
   ```

1. The *xccdf:TestResult* *start-time* and *end-time* attributes, if provided, MUST each be an annotation of the observation with either *"name":"xccdf:start-time"* or *"name":"xccdf:end-time"*, as appropriate.

1. The *xccdf:target* element MUST be defined in the *subject-reference* in its *"title"* , e.g., *"title":"host.example.net"*. This SHOULD be the target system's Fully Qualified Domain Name, and SHOULD be unique to the source *xccdf:TestResult*. NB XCCDF also allows a name or description for this element, but does not require uniqueness beyond the context of the test that ran on it.

1. Whereas the *xccdf:target* is not specified to be unique, its specification as a *subject-reference* MUST include a unique *uuid-ref* as the target's identifier.

1. Each *xccdf:target-address* element becomes a *subject-reference* property, with *"class":"info"* and *"name":"target-address"*, and the given address in the prop's *"value"*. NB An IP address is not necessarily unique, e.g., different systems in different private networks may be given the same private address of *192.168.0.1*, for example.

1. Each *xccdf:fact* MAY be included in the *props* for this *subject-reference*, using *"class":"info"*, filling in appropriate values for keys *"name"* and *"value"*, e.g., `<xccdf:target-address>192.168.248.1</xccdf:target-address>` becomes

   ```
   "props":[
       {
           "ns": "IBM",
           "class": "info",
           "name": "xccdf:target-address",
           "value": "192.168.248.1"
       },
   ```

1. XCCDF results go into the OSCAL *relevant-evidence* array. The identifying *xccdf:rule-result* attribute *idref* goes into an evidence property with *"class":"id"* and *"name":"rule"*, with the actual identifier in the *"value"* key, e.g., `<xccdf:rule-result idref="xccdf_org.example_rule_ios12-no-finger-service"` becomes

   ```
   {
       "ns": "IBM",
       "class": "id",
       "name": "rule",
       "value": "xccdf_org.example_rule_ios12-no-finger-service"
   },
   ```

1. The *xccdf:rule-result* attribute, *time*, goes into the evidence property with  *"class":"timestamp"* and *"name":"time"*, with the actual timestamp in the *"value"* key, e.g., `<xccdf:rule-result idref="xccdf_org.example_rule_ios12-no-finger-service" time="2007-09-25T13:45:00-04:00">` becomes

   ```
   {
       "ns": "IBM",
       "class": "timestamp",
       "name": "time",
       "value": "2007-09-25T13:45:00-04:00"
   }
   ```

1. Other XCCDF rule-result data MAY be included in the *annotations* of the *relevant-evidence*.

An example observation for XCCDF TestResults can be found here: [benchmark_xccdf_observation14.json](benchmark_xccdf_observation14.json).

## Draft: IBM Cloud Compliance and Security Centre (Spanugo) scan results

1. The scan's profile, i.e., benchmark, MUST be indicated in a property of the OSCAL assessment-result *observation* with *"class":"id"* and *"name":"scan"*.

1. The scan's *IT_resource* MUST be indicated as  a *subject-reference* property where *"class":"id"* and *"name":"IT-resource"* (see below).

1. The scan's *Control Target* MUST be indicated as another *subject-reference* property with *"class":"id"* and *"name":"control-target"*. For example, this *subject-reference*:

   ```
            {
                "uuid-ref": "00000000-0000-4000-9999-000000000013",
                "type": "component",
                "title": "192.168.122.4",
                "props":[
                    {
                        "ns": "IBM",
                        "class": "id",
                        "name": "IT-resource",
                        "value": "192.168.122.4"
                    },
                    {
                        "ns": "IBM",
                        "class": "id",
                        "name": "control-target",
                        "value": "centos"
                    }
                ]
            }
   ```

   or this:

   ```
            {
                "uuid-ref": "00000000-0000-4000-9999-000000000006",
                "type": "component",
                "title": "PasswordPolicy",
                "props":[
                    {
                        "ns": "IBM",
                        "class": "id",
                        "name": "account",
                        "value": "2"
                    },
                    {
                        "ns": "IBM",
                        "class": "id",
                        "name": "IT-resource",
                        "value": "PasswordPolicy"
                    },
                    {
                        "ns": "IBM",
                        "class": "id",
                        "name": "control-target",
                        "value": "Identity and Access Management"
                    }
                ]
            }
   ```

1. The scan result's *Status* is the *PASS* or *FAIL* result that goes into the *relevant-evidence*.

1. The scan result's *Actual Value* MUST be indicated as another *relevant-evidence* property with *"class":"info"* and *"name":"actual-value"*.

1. The scan result's *Expected Value* MUST be indicated as another *relevant-evidence* property with *"class":"info"* and *"name":"expected-value"*.

1. The scan result's *detail* string MUST be indicated as another *relevant-evidence* property with *"class":"info"* and *"name":"detail"*.

1. For scan results, a control number that exists for a profile or benchmark MUST be specified in the observation *props* with *"name":"control-number"* and *"class":"id"*. For example,

   ```
            {
                "ns": "IBM",
                "class": "id",
                "name": "control-number",
                "value": "1.1.1.1"
            }
   ```

An example observation from the scan results in IBM Security and Compliance Center can be found in [collector_system_multi-observations_OSCAL.json](collector_system_multi-observations_OSCAL.json).

## Notes:

- Currently supporting **OSCAL 1.0.0-rc1**
