# task csv-to-oscal-cd

The below table represents the expectations of trestle task `csv-to-oscal-cd` for the contents of the input csv-file for synthesis of the output OSCAL Component Definition json-file.

`Column Name` is the name of the expected column in the input csv-file. Any additional columns not identified here, for example foobar, are also extracted and placed into the output json-file as component.control-implementation.prop["foobar"].

`Component Definition Locale` is the `path` within the output json-file into witch the value is stashed.

An example input [csv-file](ocp4-sample-input.csv).

An example output [json-file](component-definition.json).

<table>

<tr style="text-align:left;vertical-align:top">
<th>Column Name
<th>Value Type
<th>Specification
<th>Value Description
<th>Component Definition Locale
<th>Example Value

<tr style="text-align:left;vertical-align:top">
<td>Rule_Id
<td>String
<td>required
<td>A textual label that uniquely identifies a policy (desired state) that can be used to reference it elsewhere in this or other documents.
<td>component.control-implementation.prop["Rule_Id"]
<td>password_policy_min_length_characters

<tr style="text-align:left;vertical-align:top">
<td>Rule_Description
<td>String
<td>required
<td>A description of the policy (desired state) including information about its purpose and scope.
<td>component.control-implementation.prop["Rule_Description"]
<td>Ensure password policy requires minimum length of 12 characters

<tr style="text-align:left;vertical-align:top">
<td>Profile_Reference_URL
<td>String
<td>required
<td>A URL reference to the source catalog or profile for which this component is implementing controls for. A profile designates a selection and configuration of controls from one or more catalogs
<td>component.control-implementation.source
<td>https://github.com/usnistgov/oscal-content/blob/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_HIGH-baseline_profile.json

<tr style="text-align:left;vertical-align:top">
<td>Profile_Description
<td>String
<td>required
<td>A description of the profile.
<td>component.control-implementation.description
<td>NIST Special Publication 800-53 Revision 5 HIGH IMPACT BASELINE

<tr style="text-align:left;vertical-align:top">
<td>Component_Type
<td>String
<td>required
<td>A category describing the purpose of the component.
<td>component.type
<td>Validation

<tr style="text-align:left;vertical-align:top">
<td>Control_Mappings
<td>String List (blank separated)
<td>required
<td>A list of textual labels that uniquely identify the controls or statements that the component implements.
<td>component.control-implementation.implemented-requirement.statement.statement-id<br>*and*<br>component.control-implementation.implemented-requirement.control-id
<td>ia-5.1_smt.a ia-5.1

<tr style="text-align:left;vertical-align:top">
<td>Resource
<td>String
<td>required
<td>A human readable name for the component.
<td>component.title
<td>Compliance Center

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Id
<td>String
<td>optional
<td>A textual label that uniquely identifies the parameter associated with that policy (desired state) or controls implemented by the policy (desired state).	A description of the parameter including the purpose and use of the parameter.
<td>component.control-implementation.prop["Parameter_Id"]<br>*and*<br>component.control-implementation.set-parameter.param-id
<td>minimum_password_length

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Description
<td>String
<td>optional
<td>A description of the parameter including the purpose and use of the parameter.
<td>component.control-implementation.prop["Parameter_Description"]
<td>Minimum Password

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Default_Value
<td>String
<td>optional
<td>A value recommended in this profile for the parameter of the control or policy (desired state).
<td>12
<td>component.control-implementation.set-parameter.values

<tr style="text-align:left;vertical-align:top">
<td>Parameter_Value_Alternatives
<td>String List (blank separated)
<td>optional
<td>ONLY for the policy (desired state) parameters: A value or set of values the parameter can take.
<td>component.control-implementation.prop["Parameter_Value_Alternatives"]
<td>12 8

<tr style="text-align:left;vertical-align:top">
<td>Check_Id
<td>String
<td>optional
<td>A textual label that uniquely identifies a check of the policy (desired state) that can be used to reference it elsewhere in this or other documents.
<td>component.control-implementation.prop["Check_Id"]
<td>check_password_policy_min_length_characters

<tr style="text-align:left;vertical-align:top">
<td>Check_Description
<td>String
<td>optional
<td>A description of the check of the policy (desired state) including the method (interview or examine or test) and procedure details.
<td>component.control-implementation.prop["Check_Description"]
<td>Check whether password policy requires minimum length of 12 characters

<tr style="text-align:left;vertical-align:top">
<td>Fetcher
<td>String
<td>optional
<td>A textual label that uniquely identifies a collector of the actual state (evidence) associated with the policy (desired state) that can be used to reference it elsewhere in this or other documents.
<td>component.control-implementation.prop["Fetcher"]
<td>fetch_password_policy_min_length_characters

<tr style="text-align:left;vertical-align:top">
<td>Fetcher_Description
<td>String
<td>optional
<td>A description of the collector of the actual state (evidence) associated with the policy (desired state) including the method (interview or examine or API) and questionaire
<td>component.control-implementation.prop["Fetcher_Description"]
<td>Fetch whether password policy requires minimum length of 12 characters

<tr style="text-align:left;vertical-align:top">
<td>Resource_Instance_Type
<td>String
<td>optional
<td>not used
<td>
<td>

</table>
        