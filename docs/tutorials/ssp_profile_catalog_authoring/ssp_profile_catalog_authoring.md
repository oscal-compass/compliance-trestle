# Tutorial: SSP, Profile and Catalog Authoring

## Introduction

Trestle has authoring tools that allow conversion of OSCAL documents to markdown for easy editing - and conversion back to OSCAL for validation and automation.  The author commands are:

1. `catalog-generate` converts a control Catalog to individual controls in markdown format for addition or editing of guidance prose.  `catalog-assemble` then gathers the prose and adds it to the controls in the Catalog.
1. `profile-generate` takes a given Profile and converts the controls represented by its resolved profile catalog to individual controls in markdown format, with sections corresponding to the content that the Profile adds to the Catalog.  The user may edit that additional content or add more, and `profile-assemble` then gathers the updated additional content and creates a new OSCAL Profile that includes those edits.
1. `ssp-generate` takes a given Profile and its resolved profile catalog, and represents the individual controls as markdown files with sections that prompt for prose regarding the implementation response for items in the statement of the control.  `ssp-assemble` then gathers the response sections and creates an OSCAL System Security Plan comprising the resolved profile catalog and the implementation responses.

In summary, the `catalog` tools allow conversion of a Catalog to markdown for editing - and back again to a Catalog.  The `profile` tools similarly convert a Profile's resolved profile catalog to markdown and allow conversion to a new Profile with modified additions that get applied in resolving the profile catalog.  Finally, the `ssp` tools allow the addition of implementation prose to a resolved profile catalog, then combine that prose with the Catalog into an OSCAL System Security Plan.

If a yaml header has been added to any of the controls, it will be retained if catalog-generate is run with currently existing markdown for controls.  The yaml header can add parameters to the control's implemented requirements when an SSP is assembled from the markdown.

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

It's important to note that each profile is importing a selection of controls from each source, then making its own modifications to parameters and other content in those controls.  This way the catalogs themselves can remain relatively static, and individual use cases can effectively create a custom catalog based on the original controls plus modifications.  The authoring tools here provide ways to make those modifications, both to the controls and to the profile, and to enter the implementation responses that are needed in a System Security Plan.

## `trestle author catalog-generate` and `trestle author catalog-assemble`

A Control may contain many parts, but only one of them is a Statement, which describes the function of the control.  The statement itself is broken down into separate items, each of which may contain parameter id's in "moustache" (`{{}}`) brackets.  Below is an example of a control statement as generated in markdown form by the `catalog-generate` command.

```markdown
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

- \[d\] My added item

```

A profile can then provide values for the parameters so that the final resolved profile catalog is complete and all the parameters have been specified for the needs of a specific use case.  But `catalog-generate` lets you add or edit items in the control statement.

`catalog-generate` is run with the command `trestle author catalog-generate --name catalog_name --output markdown_dir`, where `catalog_name` is the name of a catalog already loaded into the trestle workspace, and `markdown_dir` is the directory into which the markdown files for the controls will be written.  A separate directory is created for each group in the catalog.

A user then may edit the control statement for the control and add or change the contents.  In this case an added item, `My added item` is shown as item `d`.  You can then assemble the edited controls into a new catalog with the command `trestle author catalog-assemble --markdown markdown_dir --output new_catalog`.  This will load the updated control statements for each control into a new json or yaml catalog named `new_catalog`.

## `trestle author profile-generate` and `trestle author profile-assemble`

The background text above conveys how a profile pulls controls from catalogs and makes modifications to them, and the `trestle profile` tools let you change the way those modifications are made.  In addition to selecting controls and setting parameters, a profile may add new parts to a control that provide additional guidance specific to a certain use case.  `profile-generate` is run with the command, `trestle author profile-generate --name profile_name --output markdown_dir`.  It will load the specified profile name from the trestle workspace (it must have been imported prior) and create its corresponding resolved profile catalog - but *without* applying any of its `Adds` of additonal guidance content.  It will make all other modifications, such as parameter settings, but the `Adds` are kept separate, as shown below:

```markdown
# ac-1 - \[Access Control\] Policy and Procedures

## Control Statement

- \[a\] Develop, document, and disseminate to all personell:

  - \[1\]  A thorough access control policy that:

    - \[a\] Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
    - \[b\] Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and

## Control guidance

Access control policy and procedures address the controls in the AC family that are implemented within systems and organizations.

# Editable Content

<!-- Make additions and edits below -->
<!-- The above represents the contents of the control as received by the profile, prior to additions. -->
<!-- If the profile makes additions to the control, they will appear below. -->
<!-- The above may not be edited but you may edit the content below, and/or introduce new additions to be made by the profile. -->
<!-- The content here will then replace what is in the profile for this control, after running profile-assemble. -->
<!-- The added parts in the profile for this control are below.  You may edit them and/or add new ones. -->
<!-- Each addition must have a heading of the form ## Control my_addition_name -->
<!-- See https://ibm.github.io/compliance-trestle/tutorials/ssp_profile_catalog_authoring/ssp_profile_catalog_authoring for guidance. -->

## Control ImplGuidance

Do it carefully.

## Control my_guidance

This is my_guidance.

## Control ExpectedEvidence

Detailed logs.
```

In the above markdown example, the fixed, uneditable parts of the control are output first, follwed by a separate section marked, `Editable Content`.  And below the editable content are the individual `Adds` that the profile makes, with each one marked by a header of the form, `## Control guidance_name`.  You may edit the editable content and you may add new Control guidance headers with your own new content. Please refer to Markdown Specifications for Editable Content section to learn more on which headers are valid in Trestle. Then the command, `trestle author profile-assemble --name original_profile --markdown markdown_dir --output new_profile` will create a new OSCAL profile based on the original profile (specified) and the editable content in each control.

It's important to note that these operations only apply to the `Adds` in the profile itself - and nothing upstream of the profile is affected.  Nor is anything else in the original profile lost or altered.  In the example above, the section, `## Control my_guidance` was added by editing the generated control - and after `profile-assemble` it ended up as new guidance in the assembled profile.

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

`trestle author ssp-generate -p my_prof -y /my_yaml_dir/header.yaml -s 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence' -o my_ssp`

In this example the profile has previously been imported into the trestle project directory.  The profile itself must be in the trestle directory, but the imported catalogs and profiles may be URI's with href's as described below.

The `-s --section` argument specifies the name of Parts in the control for which the corresponding prose should be included in the control's markdown file.  Each colon-separated pair refers to the actual part name first, followed by the form that should be used in the heading for that section.  This is done because the name itself may be abbreviated and lack needed spaces between words. If no section labels are provided all parts are included using the default 'name' as specified in the underlying OSCAL.

(Note that the single quotes are required on Unix-like systems, but on Windows they are only needed if the contained string includes spaces, in which case *double* quotes should be used.)

In the example above, the two sections loaded are `ImplGuidance` and `ExpectedEvidence` - and their aliases are provided with full spacing and
spelling so the section headers will have proper titles.  The output will be placed in the trestle subdirectory `my_ssp` with a subdirectory
for each control group.

If the imported catalogs or profiles are not at the URI pointed to by the Import href of the profile then the href should be changed using the `trestle href` command.

The optional yaml header file can be anywhere in the file system.

<br>
<details>
<summary>The resulting files look like this</summary>

```markdown
---
control-origination:
- Service Provider Corporate
- Service Provider System Specific
responsible-roles:
- Customer
---

# ac-1 - Access Control Policy and Procedures

## Control Description

- \[a.\] Develop, document, and disseminate to all personell:

  - \[1.\] A thorough access control policy that:

    - \[(a)\] Addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
    - \[(b)\] Is consistent with applicable laws, executive orders, directives, regulations, policies, standards, and guidelines; and

  - \[2.\] Procedures to facilitate the implementation of the access control policy and the associated access controls;

- \[b.\] Designate an officer to manage the development, documentation, and dissemination of the access control policy and procedures; and
- \[c.\] Review and update the current access control:

  - \[1.\] Policy weekly and following all meetings; and
  - \[2.\] Procedures monthly and following conferences.

_______________________________________________________________________________

## ac-1 Section Implementation Guidance

Do it carefully.

_______________________________________________________________________________

## ac-1 Section Expected Evidence

Detailed logs.
   
_______________________________________________________________________________

## ac-1 What is the solution and how is it implemented?

_______________________________________________________________________________


### Part a.

Add control implementation description here.

_______________________________________________________________________________


### Part b.

Add control implementation description here.

_______________________________________________________________________________


### Part c.

Add control implementation description here.

_______________________________________________________________________________



```

</details>
<br>

Each label in the ssp is wrapped in \\\[ \\\] to indicate it comes directly from the label in the control and is not generated by the markdown viewer.  Keep in mind that the actual label is the same but with the \\\[ \\\] removed.

Note that for each statement in the control description there is a corresponding response section in which to provide a detailed response for later inclusion in the final ssp as the control implementation.

Also note that the optional final sections are provided, and labeled using the alias given at the command line.

After generating the markdown for the resolved profile catalog you may then edit the files and provide text in the sections with `Add control implementation...` in them.  But do not remove the horizontal rule
lines or modify/remove the lines with `### Part` in them.  They are used to match the added prose to the corresponding control part description.

If you edit the control markdown files you may run `ssp-generate` again and your edits will not be overwritten.  When writing out the markdown for a control, any existing markdown for that control will be read and the response text for each part will be re-inserted into the new markdown file.  If the new markdown has added parts the original responses will be placed correctly in the new file, but if any part is removed from the control in the update then any corresponding prose will be lost.

There is special handling for the yaml header if 'ssp-generate' is run and markdown files for the controls already exist.  If a yaml header is not specified, then any header found in the controls will be retained in the newly generated control.  But if a yaml header is specified, then the contents of that header will be merged with any existing header in a control.  The merge is done in a way to retain any values in the original markdown and ignore new values from the provided header, but at the same time any new content not present in the original header that is in the new header will be added to the control markdown.  In other words, edited content in the markdown is never deleted.

## `trestle author ssp-assemble`

After manually edting the markdown and providing the responses for the control implementation requirements, the markdown can be assembled into a single json SSP file with:

`trestle author ssp-assemble -m my_ssp -o my_json_ssp`

This will assemble the markdown files in the my_ssp directory and create a json SSP with name my_json_ssp in the system-security-plans directory.

As indicated for `ssp-generate`, please do not alter any of the horizontal rule lines or lines indicating the part or control id, e.g. `### Part a.`.  You may run `ssp-generate` and `ssp-assemble` repeatedly for the same markdown directory, allowing a continuous editing and updating cycle.

## `trestle author ssp-filter`

Once you have an SSP in the trestle directory you can filter its contents with a profile by using the command `trestle author ssp-filter`.  The SSP is assumed to contain a superset of the controls needed by the profile, and the filter operation will generate a new SSP with only those controls needed by the profile.  The filter command is invoked as:

`trestle author ssp-filter --name my_ssp --profile my_profile --output my_culled_ssp`

Both the SSP and profile must be present in the trestle directory.  This command will generate a new SSP in the directory.  If the profile makes reference to a control not in the SSP then the routine will fail with an error message.
