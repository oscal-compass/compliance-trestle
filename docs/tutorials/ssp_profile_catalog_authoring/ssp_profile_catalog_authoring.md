# Tutorial: SSP, Profile and Catalog Authoring

## Introduction

Trestle has authoring tools that allow conversion of OSCAL documents to markdown for easy editing - and conversion back to OSCAL for validation and automation.  The author commands are:

1. `catalog-generate` converts a control Catalog to individual controls in markdown format for addition or editing of guidance prose and parameters, with parameters stored in a yaml header at the top of the markdown file.  `catalog-assemble` then gathers the prose and parameters and updates the controls in the Catalog to make a new OSCAL Catalog.
1. `profile-generate` takes a given Profile and converts the controls represented by its resolved profile catalog to individual controls in markdown format, with sections corresponding to the content that the Profile adds to the Catalog, along with both the current values of parameters in the resolved profile catalog - and the values that are being modified by the given profile's SetParameters.  The user may edit the content or add more, and `profile-assemble` then gathers the updated content and creates a new OSCAL Profile that includes those changes.
1. `ssp-generate` takes a given Profile and its resolved profile catalog, and represents the individual controls as markdown files with sections that prompt for prose regarding the implementation response for items in the statement of the control.  `ssp-assemble` then gathers the response sections and creates an OSCAL System Security Plan comprising the resolved profile catalog and the implementation responses.
1. `ssp-filter` takes a given ssp and filters its contents based on the controls included in a provided profile.

In summary, the `catalog` tools allow conversion of a Catalog to markdown for editing - and back again to a Catalog.  The `profile` tools similarly convert a Profile's resolved profile catalog to markdown and allow conversion to a new Profile with modified additions that get applied in resolving the profile catalog.  Finally, the `ssp` tools allow the addition of implementation prose to a resolved profile catalog, then combine that prose with the Catalog into an OSCAL System Security Plan.

If a yaml header has been added to any of the controls, it will be retained if catalog-generate is run with currently existing markdown for controls.  The yaml header can add parameters to the control's implemented requirements when an SSP is assembled from the markdown.

The authoring tools are designed to work well in a CI/CD environment where changes are made in a pipeline by people with different responsibilities and authority.  In this setting, changes to documents can trigger changes downstream, e.g. the editing of a control would cause an update in the catalog, which could then flow down to an updated SSP.  These changes can occur automatically via actions that restrict the potential changes to the generated documents.  Examples are the `--set-parameters` option on the `-assemble` tools, and both `--required-sections` and `allowed-sections` for `profile-assemble`.  If a document change triggers an assemble action, changes to parameters can only occur if the action has `--set-parameters` in the command.  Similarly, `profile-assemble` will fail if the sections do not meet the requirements specified in the command options.  Another feature of the `-assemble` tools is that they won't create a new OSCAL file if the output already exists and its content would not be changed.  This prevents undesired triggering of downstream actions when there is no actual change in content.

For a complete standalone demonstration of the SSP generation process with trestle, please see the [Trestle SSP Demo](https://github.com/IBM/compliance-trestle-ssp-demo).  It shows the complete flow from OSCAL json files to a finished Word .docx file.

## Background on underlying concepts

In order to understand the specific operations handled by these commands, it is helpful to clarify some of the underlying OSCAL structures and how they can be edited in markdown form.  This tutorial should be viewed in the context of the extensive documentation provided by [OSCAL](https://pages.nist.gov/OSCAL).

First, a *Catalog* is a collection of *Controls*, and a *Profile* imports controls and allows modification and additions to the controls, but it does not create new controls.  A Profile has one or more *Imports* that refer either to an actual Catalog, or another Profile that itself is importing from a Catalog or Profile.  The profiles can import controls selectively from each source and make additions or modifications to properties of the controls.  The final collection of selected and modified controls represents the profile's *resolved profile catalog*.

For clarity, here is a simple depicton of a catalog as a collection of controls:

![Simple catalog](simple_catalog.png)

Here is a profile pulling controls from a catalog to make a resolved profile catalog:

![Resolved profile catalog](resolved_profile_catalog.png)

And here is a more complex situation where a single profile pulls controls from catalogs and profiles:

![Complex resolved profile catalog](complex_resolved_profile_catalog.png)

From the diagram it's clear that the profile is performing many tasks under the covers.  This is shown in an expanded view of a profile:

![What a profile does](profile_does.png)

It's important to note that each profile is importing a selection of controls from each source, then making its own *suggested* modifications to parameters and other content in those controls.  They are suggested in the sense that downstream profiles may override those settings - with priority given to the later profiles in the pipeline.  The changes made by upstream profiles may be accepted, or overridden by better choices for a given need.  This way the catalogs themselves can remain relatively static, and individual use cases can effectively create a custom catalog based on the original controls plus modifications by  other static profiles, and/or the user's custom profile.  The authoring tools here provide ways to make those modifications, both to the catalog controls and to the profiles, and to enter the implementation responses that are needed in a System Security Plan.

The tools are designed to be used in a continuous `generate-edit-assemble` cycle, with previous edits retained in each cycle.  Each new edit phase can add or modify the current content, allowing a new `generate` of an OSCAL json document capturing those edits.

NOTE: We use `json` format for specifying OSCAL files in this tutorial, but it is equally applicable to `yaml` format also.

## `trestle author catalog-generate` and `trestle author catalog-assemble`

`catalog-generate` will take an existing json catalog and write it out as markdown files for each control in a user-specified directory.  That directory will contain subdirectories for each group in the catalog, and those directories may contain subdirectories for groups within groups.  But controls containing controls are always split out into a series of controls in the same directory - and each control markdown file corresponds to a single control.

We now look at the contents of a typical control markdown file.

A Control may contain many parts, but only one of them is a Statement, which describes the function of the control.  The statement itself is broken down into separate items, each of which may contain parameter id's in "moustache" (`{{}}`) brackets.  Below is an example of a control as generated in markdown form by the `catalog-generate` command.

```markdown
---
control-origination:
  - Service Provider Corporate
  - Service Provider System Specific
responsible-roles:
  - Customer
sort-id: ac-01
x-trestle-set-params:
  ac-1_prm_1:
    label: organization-defined personnel or roles
    values: new value
  new value
  ac-1_prm_2: 
    select:
      choice:
        - Organization-level 
        - Mission/business process-level
        - System-level
      how_many: one_or_more
    values:
      - Organization-level
      - System-level
  ac-1_prm_3:
    label: organization-defined official
---

# ac-1 - \[Access Control\] Policy and Procedures

## Control Statement

- \[a.\] Develop, document, and disseminate to {{ insert: param, ac-1_prm_1 }}:

  - \[1.\]  {{ insert: param, ac-1_prm_2 }} access control policy that:

    - \[(a)\] Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
    - \[(b)\] Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and

  - \[2.\] Procedures to facilitate the implementation of the access control policy and the associated access controls;

- \[b.\] Designate an {{ insert: param, ac-1_prm_3 }} to manage the development, documentation, and dissemination of the access control policy and procedures; and

- \[c.\] Review and update the current access control:

  - \[1.\] Policy {{ insert: param, ac-1_prm_4 }} and following {{ insert: param, ac-1_prm_5 }}; and
  - \[2.\] Procedures {{ insert: param, ac-1_prm_6 }} and following {{ insert: param, ac-1_prm_7 }}.
- \[d.\] My added item

## Control guidance

Access control policy and procedures address the controls in the AC family that are implemented within systems and organizations.

```

The control markdown files rely on brackets around key items that are important in defining the control's properties and structure.  `\[Access Control\]` at the top indicates the title of the group containing the control.  The name of the control is already known from the name of the markdown file (`ac-1.md`) and the name of the group is already known from the name of the directory containing the group's controls (`ac`) - but the group title must be indicated in the control in a special manner, hence the brackets.  The text following the group title is the title of the control itself.  All controls in a group should have the same group title or a warning will be indicated in certain trestle operations.

In addition, each part label corresponds to the label used in the OSCAL structure for the control statement, and so must be maintained in a special manner -  hence the need for brackets on `\[(a)\]`.

The items in moustaches (`{{}}`) correspond to the original prose from the control description.  The moustaches represent places to substitue parameter values, but no substitutions are ever made until the final SSP generation.  The authoring process provides multiple ways to set and change the final parameter values, as described below.

`catalog-generate` is run with the command `trestle author catalog-generate --name catalog_name --output markdown_dir`, where `catalog_name` is the name of a catalog already loaded into the trestle workspace, and `markdown_dir` is the directory into which the markdown files for the controls will be written.  A separate directory is created for each group in the catalog.

A user then may edit the control statement for the control and add or change the contents.  In this case an added item, `My added item` is shown as item `d`.  You can then assemble the edited controls into a new catalog with the command `trestle author catalog-assemble --markdown markdown_dir --output new_catalog`.  This will load the updated control statements for each control into a new json or yaml catalog named `new_catalog`.

As with profile and ssp generation described below, a yaml header may be provided with the `--yaml` option that is inserted into the top of each control file.  If a control file already exists, as is expected in a continuous cycle of generate-edit-assemble, then the provided header will be merged with the existing header in each control.  If a given item in the header is already present in the control, by default the values in the markdown header will be given priority, though this can be overridden by the `--overwrite-header-values` option, which will give priority to any values coming from the provided yaml header.  In all cases, values in the yaml header not already present in the markdown header will be inserted.

In the control markdown example above, the header contains some arbitrary values along with a special `x-trestle-set-params` section containing parameters for some of the parameters in the control.  Any parameters for the control in the catalog will appear in the markdown header automatically during `catalog-generate`.  These values may be changed and values for other parameters may be inserted into the markdown header for later use during `catalog-assemble`.

Parameters in the header are shown with a subset of their full OSCAL attributes in order to convey any values they may have along with descriptive text.  This amounts to the parameter id, its label if present, any values if present, and any select if present.  When a select is present the list of choices is provided along with the how-many option.  Note that values is a list in OSCAL, but in many cases it is a list of only one item.  As a result, for convenience the values: dictionary may either have one string value (on the same line with `values:`) or as an indented `-` list of multiple values underneath `values:`.  Multiple examples are evident in the sample above, including ac-1_prm_3, which only has a label and no values.

Another important item in the header is the sort-id for the control.  This specifies how the controls and their parameters are ordered in any aggregated list operation.  If it is not specified for a control, the control's id is used for sorting.

`catalog-assemble` is run with the command `catalog-assemble --markdown my_md --output my_new_catalog`.  This will read the markdown for each control and create a new catalog based on any edits to the markdown.  Note that you may optionally provide a `--name` option specifying an original json catalog into which the updated controls are inserted, and the resulting catalog can either replace the original one or output to a different json file.  New controls may be added and existing controls may be removed.  The main benefit is that the original metadata and other contents of the catalog json file will be retained.  You have the option to specify a new `--version` for the catalog, and an option to regenerate the uuid's in the catalog.  Finally, you have the option to use the parameters in the markdown header to update the values in the control.  Any parameters and their values present will be added to the control, and any not present will be removed.  The parameters themselves are still present but their values are removed.

In a typical `generate-edit-assemble` cycle, the cycle would start with an original json file containing source content and metadata and use that to generate an initial markdown directory of controls.  After editing the controls they would be assembled into into a new json file with a different name.  But once that new file exists, it can be used as the source for the next generation and the original source document is no longer needed or referred to.  For the `catalog-` editing cycle it would go as:

```
trestle author catalog-generate --name orig_catalog --output md_catalog
[user edits the markdown files]
trestle author catalog-assemble --name orig_catalog --markdown md_catalog --output assembled_catalog
[user makes additional markdown edits]
trestle author catalog-assemble --markdown md_catalog --output assembled_catalog
```

The key point here is that the first `-assemble` needs to use the original catalog for its metadata, backmatter and other items not captured in the markdown controls.  But once the output catalog has been created, by default it will be used as the "original" or "parent" catalog into which changes will be incorporated, unless a different source catalog is specified via `--name`.

Note that `catalog-assemble` can instantiate a catalog anew from a manually created directory of markdown controls in directories corresponding to groups, but the metadata in the assembled json catalog will contain many `REPLACE_ME` items that would need to be manually edited in the json file itself.  The trestle `split` and `merge` tools may help in that case.  Once the changes have been made they will be retained if a new `catalog-assemble` happens with that same output file as the target.

*Special Note about assemble*: In order to avoid triggering actions when a new file is created that has no actual changes in it, `catalog-assemble` and the other `-assemble` tools below will check to see if the output file already exists, and if so it will be examined for changes relative to the newly assembled one.  If there are no changes the file will not be written out.  Note that the check happens *before* any possible `--regeneration` of uuid's, and *after* any possible `--version` change.  This avoids the creation of a new file and new uuid's if there is no change to the version or other file contents relative to the existing output file, but if the specified `--version` is different from the one in the existing output file, or there is any other difference in the model, a new file will be written out.

## `trestle author profile-generate` and `trestle author profile-assemble`

The background text above conveys how a profile pulls controls from catalogs and makes modifications to them, and the `trestle profile` tools let you change the way those modifications are made.  In addition to selecting controls and setting parameters, a profile may add new parts to a control that provide additional guidance specific to a certain use case.  `profile-generate` is run with the command, `trestle author profile-generate --name profile_name --output markdown_dir`.  It will load the specified profile name from the trestle workspace (it must have been imported into the trestle workspace prior) and create its corresponding resolved profile catalog - but *without* applying any of its `Adds` of additonal guidance content or `SetParameters`.  It will make all other modifications, but the `Adds` and `SetParameters` are kept separate, as shown below:

```markdown
---
control-origination:
  - Service Provider Corporate
  - Service Provider System Specific
responsible-roles:
  - Customer
x-trestle-set-params:
  ac-1_prm_1:
    values: all personnel
    profile-values: new value from profile
  ac-1_prm_2:
    values: new value
  ac-1_prm_3:
    values: all meetings
    profile-values:
      - some meetings
      - most meetings
  ac-1_prm_4:
    values: monthly
x-trestle-sections:
  ImplGuidance: Implementation Guidance
  ExpectedEvidence: Expected Evidence
  my_guidance: My Guidance
  a_guidance: A Guidance
  b_guidance: B Guidance
  NeededExtra: Needed Extra

---

# ac-1 - \[Access Control\] Policy and Procedures

## Control Statement

- \[a\] Develop, document, and disseminate to {{ insert: param, ac-1_prm_1 }}:

  - \[1\]  {{ insert: param, ac-1_prm_2 }} access control policy that:

    - \[a\] Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
    - \[b\] Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and

  - \[2\] Procedures to facilitate the implementation of the access control policy and the associated access controls;

- \[b\] Designate an {{ insert: param, ac-1_prm_3 }} to manage the development, documentation, and dissemination of the access control policy and procedures; and

- \[c\] Review and update the current access control:

  - \[1\] Policy {{ insert: param, ac-1_prm_4 }} and following {{ insert: param, ac-1_prm_5 }}; and
  - \[2\] Procedures {{ insert: param, ac-1_prm_6 }} and following {{ insert: param, ac-1_prm_7 }}.

## Control guidance

Access control policy and procedures address the controls in the AC family that are implemented within systems and organizations.

# Editable Content

<!-- Make additions and edits below -->
<!-- The above represents the contents of the control as received by the profile, prior to additions. -->
<!-- If the profile makes additions to the control, they will appear below. -->
<!-- The above markdown may not be edited but you may edit the content below, and/or introduce new additions to be made by the profile. -->
<!-- If there is a yaml header at the top, parameters and values may be edited. Use --set-parameters to incorporate the changes during assembly. -->
<!-- The content here will then replace what is in the profile for this control, after running profile-assemble. -->
<!-- The added parts in the profile for this control are below.  You may edit them and/or add new ones. -->
<!-- Each addition must have a heading of the form ## Control my_addition_name -->
<!-- See https://ibm.github.io/compliance-trestle/tutorials/ssp_profile_catalog_authoring/ssp_profile_catalog_authoring for guidance. -->

## Control Implementation Guidance

Do it carefully.

## Control Expected Evidence

Detailed logs.

## Control Needed Extra

Add prose here for required Section: Needed Extra

## Control A Guidance

This is A Guidance.

## Control B Guidance

This is B Guidance.

```

In the above markdown example, the fixed, uneditable parts of the control are output first (after the header, which can be edited), followed by a separate section marked, `Editable Content`.  And below the editable content are the individual `Adds` that the profile makes, with each one marked by a header of the form, `## Control guidance_name`.  You may edit the editable content and you may add new Control guidance headers with your own new content. Please refer to Markdown Specifications for Editable Content section below to learn more on which headers are valid in Trestle. Then the command, `trestle author profile-assemble --name original_profile --markdown markdown_dir --output new_profile` will create a new OSCAL profile based on the original profile (specified) and the editable content in each control.

In a cyclic operation of `profile generate-edit-assemble` you would simply be re-writing from and to the same json profile, in which case the `--name` and `--output` are the same file.  For this reason the default value for `--name` is the given output file name specified by `--output` and you can just use `trestle author profile-assemble --markdown profile_md --output my_profile`.  This will assemble the markdown profile contents in directory `profile_md` into a json profile named `my_profile` but it will first use the existing `my_profile` json file as the parent profile and incorporate changes (due to user edits) in the markdown version of the profile.  Unlike `catalog-assemble` there must always be a parent json profile to reference during assemble, but like `catalog-assemble` an explicit value for `--name` is only needed if the parent file is different from the assembled output file.

It's important to note that these operations only apply to the `Adds` and `SetParameters` in the profile itself - and nothing upstream of the profile is affected.  Nor is anything else in the original profile lost or altered.  In the example above, the section, `## Control Implementation Guidance` was added by editing the generated control - and after `profile-assemble` it ended up as new guidance in the assembled profile.

As in the other commands, `profile-generate` allows specification of a yaml header with `--yaml`, and support of the `--overwrite-header-values` flag.   Also, during assembly with `profile-assemble` the `--set-parameters` flag will set parameters in the profile for the control based on the header in the control markdown file.  But unlike with `catalog-assemble`, only those parameter values marked `profile-values` will be part of the assembled profile's SetParams when you assemble with the `--set-parameters` flag.  For each parameter, the "incoming" values for the parameters prior to any changes made by the profile are listed as `values:` and any pending changes made by the profile are listed as `profile-values:`.  If you don't use the `--set-parameters` flag then all the original SetParameters in the profile will be retained in the new, assembled profile.  But if you do set that flag, then only the header parameters with `profile-values:` will be added as SetParameters.  This lets you see all the incoming values for parameters along with any changes made by the current profile, and you can modify, add, or remove parameter settings as desired in the new profile.

As with `catalog-assemble` described above, a new file is written out only if there are changes to the model relative to an existing output file.

## Use of Sections in `profile-generate` and `profile-assemble`

The addition of guidance sections in the `profile` tools requires special handling because the corresponding parts have both a name and a title, where the name is a short form used as an id in the json schema, while the title is the readable form intended for final presentation.  An example is `ImplGuidance` vs. `Implementation Guidance`.  The trestle authoring tools strive to make the markdown as readable as possible, therefore the headings for sections use the title - which means somehow there is a need for a mapping from the short name to the long title for each section.  This mapping is provided in several ways:  During `profile-generate` you may provide a `--sections "ImplGuidance:Implementation Guidance,ExpEvidence:Expected Evidence"` option that would provide title values for `ImplGuidance` and `ExpEvidence`.  This dictionary mapping is then inserted into the yaml header of each control's markdown.  You may also add this mapping directly to a yaml file that is passed in during `profile-generate`, which is preferable if the list of sections is long.  The sections should be entered in the yaml header in a section titled, `x-trestle-sections`.

There is also a `--required-sections` option during both `profile-generate` and `profile-assemble`.  This option expects a list of sections as *comma-separated short names*, e.g. `--required-sections "ImplGuidance,ExpEvidence"`.  During `profile-generate` any required sections will have in the markdown a prompt created for guidance prose to be entered.  And during `profile-assemble` if required sections are specified, those sections must have prose filled in or it will fail with error.

Finally, `profile-assemble` also has an `--allowed-sections` option that restricts any added guidance to only those allowed sections - and if disallowed sections are present it will fail with error.  If `--allowed-sections` is not specified then any sections found in the markdown will be added to the assembled profile.

Note that these section options are all optional and there isn't a need to provide this form of restriction and enforcement.  But in order to have such sections read properly and mapped to the intended part names, a mapping must be provided in one of the ways described above.  And for certain workflows, if the allowed and required sections are specified by a command that is run as an action outside the user's control, it allows restriction of what changes can or must be made to a profile in terms of added guidance.

(Note that the single quotes are required on Unix-like systems, but on Windows they are only needed if the contained string includes spaces, in which case *double* quotes should be used.)

## Markdown Specifications for Editable Content.

For the ease of editing markdown in Github, Trestle's markdown parser follows [Github Flavoured Markdown (GFM) specifications](https://github.github.com/gfm/) and therefore only certain Control headers will be parsed and added to the control.

A valid control header in Trestle is the header that is correctly displayed as such when reading or previewing the edited markdown on Github website.

In GFM, headers are considered to be any line of text that has any number of `#` symbols at the beginning. For example those are all valid headers and will be treated as such by Github:

```markdown
# Valid header
## Valid header 
##### Valid header
# Valid <ins> header </ins> 
# Valid header <!-- some comment here -->
```

The headers above are valid Control headers and will be added to the control. However, there are multiple exceptions where the header will not be displayed. The header will not be displayed correctly if it is:

1. Written in the HTML comments `<!-- # not a header -->` or tags `<ins> # not a header </ins>` as well as multi-line comments:
   ```markdown
   <!--
   # not a header
   -->
   ```
   or multi-line HTML blocks:
   ```markdown
   <dl> # not a header
   # not a header
     <dt># not a header</dt>
   </dl>
   ```
1. Written in the single-line `# not a header` and multi-line code blocks:
   ```markdown
   # not a header 
   ```
1. Written in the links `[# not a header](url)`
1. Trestle will also not support headers inside the blockquotes `> # not a header`

In all cases above Trestle markdown parser will skip such headers and it will be not added to the control.

## `trestle author ssp-generate` and `trestle author ssp-assemble`

The `ssp-generate` sub-command creates a partial SSP (System Security Plan) from a profile and optional yaml header file.  `ssp-assemble` (described below) can later assemble the markdown files into a single json SSP file.  The profile contains a list of imports that are either a direct reference to a catalog, or an indirect reference via a profile.
There may be multiple imports of either type, and referenced profiles may themselves import either catalogs or profiles.  Each profile involved may specify
the controls that should be imported, along with any modifications to those controls.  This command internally creates a resolved profile catalog and generates a
directory containing a set of markdown files, one for each control in the resolved catalog.  Each markdown file has the optional yaml header embedded
at the start of the file.

Example usage for creation of the markdown:

`trestle author ssp-generate --profile my_prof --yaml /my_yaml_dir/header.yaml --sections 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence' --output my_ssp`

In this example the profile has previously been imported into the trestle directory.  The profile itself must be in the trestle directory, but the imported catalogs and profiles may be URI's with href's as described below.

The `-s --sections` argument specifies the name of Parts in the control for which the corresponding prose should be included in the control's markdown file.  The concept is the same as above with `profile` tools in providing a mapping between all possible short names for guidance and their corresponding long versions that should appear in the markdown headings.  In addition, `ssp-generate` has an `--allowed-sections` option that specifies a list of section short names that will be included in the markdown.  This provides a means for filtering the guidance that appears in the markdown for the controls.  Note that unlike in `profile-assemble` there is no error if sections are present in the control that are not among the "allowed" sections.  For `ssp-generate` the allowed sections simply provide a means for filtering the guidance.  If you do not specify `--allowed-sections` then all sections present in the control will appear in the markdown.

The generated markdown output will be placed in the trestle subdirectory `my_ssp` with a subdirectory
for each control group.

If the imported catalogs or profiles are not at the URI pointed to by the Import href of the profile then the href should be changed using the `trestle href` command.

Similar to `catalog-generate`, the `--yaml` and `--overwrite-header-values` flag may be specified to let the input yaml header overwrite values already specified in the header of the control markdown file.

The resulting files look like this:

```markdown
---
control-origination:
  - Service Provider Corporate
  - Service Provider System Specific
responsible-roles:
  - Customer

x-trestle-sections:
  ImplGuidance: Implementation Guidance
  ExpectedEvidence: Expected Evidence
  guidance: Guidance
  statement: statement

---

# ac-1 - \[Access Control\] Policy and Procedures

## Control Statement

- \[a\] Develop, document, and disseminate to all personnel:

  - \[1\]  A thorough access control policy that:

    - \[a\] Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
    - \[b\] Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and

  - \[2\] Procedures to facilitate the implementation of the access control policy and the associated access controls;

- \[b\] Designate an officer to manage the development, documentation, and dissemination of the access control policy and procedures; and

- \[c\] Review and update the current access control:

  - \[1\] Policy weekly and following all meetings; and
  - \[2\] Procedures monthly and following organization-defined events.

## Control Implementation Guidance

Do it carefully.

## Control Expected Evidence

Detailed logs.

## Control Guidance

Access control policy and procedures address the controls in the AC family that are implemented within systems and organizations.

______________________________________________________________________

## What is the solution and how is it implemented?

<!-- Please leave this section blank and enter implementation details in the parts below. -->

______________________________________________________________________

## Implementation a.

Add control implementation description here for item ac-1_smt.a

______________________________________________________________________

## Implementation b.

Add control implementation description here for item ac-1_smt.b

### ACME Component

Do the ACME requirements

______________________________________________________________________

## Implementation c.

Add control implementation description here for item ac-1_smt.c

______________________________________________________________________
```

Each label in the ssp is wrapped in `\[ \]` to indicate it comes directly from the label in the control and is not generated by the markdown viewer.  Keep in mind that the actual label is the same but with the `\[ \]` removed.

Note that for each statement in the control description there is a corresponding response section in which to provide a detailed response for later inclusion in the final ssp as the control implementation.

Also note that the optional final sections are provided, and labeled using the title for the corresponding section.

In addition, this is the only control markdown where the moustache (`{{}}`) items have been replaced by the corresponding parameter values in the final resolved profile catalog, so that the prose corresponds to the final intended control and its implementation.

The markdown can have guidance per-component in the control, as shown by the line, `### ACME Component`.  Any prose directly under a `##` implementation section will apply to the overall system component, but sections in a sub-header of the form `###` will only apply to that particular component.

After generating the markdown for the resolved profile catalog you may then edit the files and provide text in the sections with `Add control implementation...` in them.  But do not remove the horizontal rule
lines or modify/remove the lines with `### ` in them, corresponding to system components.

If you edit the control markdown files you may run `ssp-generate` again and your edits will not be overwritten.  When writing out the markdown for a control, any existing markdown for that control will be read and the response text for each part will be re-inserted into the new markdown file.  If the new markdown has added parts the original responses will be placed correctly in the new file, but if any part is removed from the source control json file then any corresponding prose will be lost after the next `ssp-generate`.

## `trestle author ssp-assemble`

After manually edting the markdown and providing the responses for the control implementation requirements, the markdown can be assembled into a single json SSP file with:

`trestle author ssp-assemble --markdown my_ssp --output my_json_ssp`

This will assemble the markdown files in the my_ssp directory and create a json SSP with name my_json_ssp in the system-security-plans directory.

As indicated for `ssp-generate`, please do not alter any of the horizontal rule lines or lines indicating the part or control id, e.g. `### ACME Component`.  You may run `ssp-generate` and `ssp-assemble` repeatedly for the same markdown directory, allowing a continuous editing and updating cycle.

As with all the `assemble` tools, you may optionally specify a `--name` for a corresponding json file into which the updates will be inserted, thereby preserving metadata and other aspects of the model.  The result can overwrite the provided model or get directed to a new model.  And the version may be updated and the uuid's regenerated.  As with the other `-assemble` tools, if an output file already exists, a new one will only be written if there are changes to the model relative to the existing file.  See `catalog-assemble` for more details.

## `trestle author ssp-filter`

Once you have an SSP in the trestle directory you can filter its contents with a profile by using the command `trestle author ssp-filter`.  The SSP is assumed to contain a superset of the controls needed by the profile, and the filter operation will generate a new SSP with only those controls needed by the profile.  The filter command is invoked as:

`trestle author ssp-filter --name my_ssp --profile my_profile --output my_culled_ssp`

Both the SSP and profile must be present in the trestle directory.  This command will generate a new SSP in the directory.  If the profile makes reference to a control not in the SSP then the routine will fail with an error message.

## Summary of options used by the `catalog`, `profile` and `ssp` authoring tools.

The provided options for the generation and assembly of documents in the ssp workflow is rich and powerful, but can also be confusing.  To help see how they all relate please consult the following diagram showing the required and optional command line arguments for each command.  The checkboxes indicate required and the open circles represent optional.

The options shown are fairly consistent across the `-generate` and `-assemble` functions, but some clarification may be needed.  For `catalog-assemble` and `profile-assemble` you have the option to use an existing json file as a parent model into which new content is inserted - in memory - and the final model may either be written back into that same json file, or a different one - based on `--output`.  If you just want to keep editing and modifying the same original json file you can specify `--name` and `--output` to be the same, original json file.  But you could also direct it to a new json file while still using an original file as the "parent."  A key benefit of referencing an original json file is the resuse of metadata and backmatter - along with everything else separate from the controls.

`ssp-generate` is special because it starts with a profile rather than an ssp, whereas `catalog-generate` and `profile-generate` both start with a parent model of the same type.  Nonetheless, you still have an option during `ssp-assemble` to use a given json file as the template into which new content is inserted, and once again you may overwrite that original json file or direct it to a new one using `--output`.

![Table of authoring tool options](trestle_ssp_author_options.png)
