# trestle CLI for governance of authored documents

## Overview

The premise of trestle is to support managing compliance artifacts as code.
When this is considered, many organisations using `{github|gitlab|bitbucket}` rely on markdown documents for documentary artifacts that may either directly or indirectly support compliance efforts.

To support this trestle has the concept of 'governing' documents that are authored documents: Where structural conditions are enforced on the markdown documents to allow automation and to ensure business processes are met.

Living in the `GitOps` world this capability is anchored with `markdown` files as the core of the workflows. Currently `drawio` files are also supported for a subset of enforcement mechanisms.

### Why is this capability in trestle?

While trestle provides editing support for OSCAL there is an unfortunate truth that for some compliance workflows:

1. OSCAL does not cover the lower level operational workflows.
1. Some users will not be comfortable editing in json/yaml/xml formats

The markdown centric workflows allow transition path where capability is [being developed](https://github.com/IBM/compliance-trestle/issues/555)

## Governance mechanisms

### Markdown structural enforcement

In order for trestle to enforce structure an approach has been taken for how to template markdown documents. There are two mechanism that are enforced:

1. Enforcing a heading structure within the markdown document:
1. Enforcing a structured header within the markdown document either by using yaml headers or a designated heading.

For enforcing the heading structure the mechanism used is the following:

Markdown headings `As an example` are considered to be nested based on the heading level (e.g. ` heading` is below ` top level heading`).

For a document to contain the structural requirements it must contain all the headings provided in the template, however, can contain additional nested templates. Given this template:

```markdown
# Template heading 1

# Template heading 2
## Template sub heading
```

The following document is acceptable:

```markdown
# Template heading 1
Content for heading one
## Non-required sub header
Content for non-required sub header
# Template heading 2
Content for heading two
## Template sub heading
Content for template sub heading
### non required sub-sub heading
This sub-sub heading is okay
```

However, violations such as adding or removing a heading at a level that has been templated is not acceptable e.g.:

```markdown
# Template heading 1
Content for heading one
## Non-required sub header
Content for non-required sub header
# Template heading 2
Content for heading two
## Template sub heading
Content for template sub heading
## sub heading that violates template
This sub heading is NOT okay
# Top level heading that is not okay
```

For each of the headings - the text of the heading is enforced with one caveat:

- If the template heading text is wrapped in curly brackets `{}` then the name is not measured e.g. `# {Insert title here}`.

### Strict header / heading conformance mechanisms

Two mechanisms are provided to enforce metadata within markdown documents. The first is the yaml header, as used by technologies such as jekyll, the second is a markdown 'governed heading\` where templating of the content is enforced.
Use of the yaml header is strongly encouraged as a first preference.

```markdown
---
yaml:
    header:
        - with some 
        - structure
    more: information
---
# The rest of my document
```

The yaml header is structurally enforced my measuring whether the template key structure is reflected in the measured document. It does not measure values for yaml attributes. For the above markdown document the array value for `yaml.header` could be replaced with a single value or expanded. Enforcing the yaml header is enabled by `-hv` where available.

For enforcing a governed heading the structural enforcement mechanism assumes that the `key:value` structure simply takes the form that following that for each line of content under the chosen heading the template content is a subset of the measured document, in the order provided in the template. This is performed after removing formatting (such as bolding), and any HTML comments.

Given:

```markdown
# heading for strict enforcement
my_key:
**my_key_2:**
my_other key with strange stuff??
```

The following heading would be acceptable.

```markdown
# heading for strict enforcement
my_key: my value
my_key_2: my value
my_other key with strange stuff?? my value
```

This capability, where available, is activated by `--governed-heading` or `-gh`

### Drawio enforcement mechanisms

Drawio or [diagrams.net](https://app.diagrams.net/) is a diagramming platform which has significant use for architecture diagrams. In the context of governance of content trestle is supporting enforcement of metadata.

Drawio (or `mxgraph`) files have a set of data fields. In a drawio file this is available the edit menu as *edit data*. The diagram below shows how to access the (meta)data.

![Accessing the drawio data editor](assets/drawio_data_menu.png "Accessing the drawio data editor")

The data presents as a set of key-value pairs which can be edited (see below). The data is bound to each tab in a drawio file. The trestle CLI currently expects that metadata (whether from the template or file to be measured) is in the first tab when editing the draw io file.

![Editing drawio data](assets/drawio_editing_data.png "Editing drawio data")

## `trestle author governed-docs`

`author docs` is designed to support enforcing and generating templating markdown files within a single folder based on a task name. Currently `author docs` supports markdown files only.

`trestle author docs setup -tn my_task_name` Create the necessary directory structures for running governed docs validation.
A template file will be created in `TRESTLE_ROOT/.trestle/author/my_task_name/template.md` and be applied to all markdown files here: `TRESTLE_ROOT/my_task_name/*.md`.

`trestle author docs create-sample -tn my_task_name` Creates a sample file in `TRESTLE_ROOT/my_task_name/`

`trestle author docs template-validate -tn my_task_name` Ensures that the markdown is parseable. If `--governed-heading 'heading name'` is passed it ensures that the required heading exists.

`trestle author docs validate -tn my_task_name` validates the markdown, optionally with a `--governed-heading` or `-hv` yaml header based on this `TRESTLE_ROOT/.trestle/author/my_task_name/template.md` template to all markdown files here: `TRESTLE_ROOT/my_task_name/*.md`.

### Extra options

#### recursive (`-r`, `--recurse`)

By default `author docs` only indexes a flat directory. The recursive option allows the markdown files to be nested in sub-directories.

#### Header only validation (`-hov`, `--header-only-validate`)

Turns off the validation of the structure of the document and only validates the yaml header structure.

## `trestle author folders`

\`author folders is designed to allow the assembly of groups of templates where the folder assembly is the unique instance. Trestle author folders supports validation of both markdown and drawio files. Note that headers / metadata must be specified in each applicable template.

For example given the following template setup using `trestle author folders setup -tn my_task_2`

```
trestle_root
 ┣ .trestle
 ┃ ┣ author
 ┃ ┃ ┗ my_task_2
 ┃ ┃ ┃ ┣ a_template.md
 ┃ ┃ ┃ ┣ another_template.md
 ┃ ┃ ┃ ┗ template.drawio
 ┃ ┗ config.ini
```

Each task folder is required to meet template requirements for both `a_template.md`, `another_template.md`, and template.drawio.
The names, numbers, and nesting of folders is user specifiable, however, unlike `docs` the names must be carried over to each instances.

Following the similar structure of `docs`, measurement occurs in the `my_task_2` where this structure is enforced for every directory.

```
trestle_root
 ┣ .trestle
 ┣ my_task_2
 ┃ ┣ User_chosen_name
 ┃ ┃ ┣ a_template.md
 ┃ ┃ ┣ template.drawio
 ┃ ┃ ┗ another_template.md

 ┃ ┗ Second_user_chosen_name
 ┃ ┃ ┣ a_template.md
 ┃ ┃ ┣ template.drawio
 ┃ ┃ ┗ another_template.md
```

### Supported options

#### Header validate (`-hv`/`--header-validate`)

Validate the headers in markdown and metadata in drawio files.

#### Header only validation (`-hov`, `--header-only-validate`)

Turns off the validation of the structure of the document and only validates the yaml header structure and drawio files.

## `trestle author headers`

Trestle author headers supports a different usecase that of `docs` and `folders` above: Some content is governed, however, it the content is non-standardized.

The result: metadata but not content needs to be measured. `author headers` provides this functionality for drawio and markdown files.

`trestle author headers setup -tn my_task_name` Create the necessary directory structures for running header only validation. Per supported file type (e.g. drawio and md) a template file will be generated with the format of `template.{extension name}` e.g.

e.g.:
trestle_root
┣ .trestle
┃ ┣ md
┃ ┃ ┗ my_task_2
┃ ┃ ┃ ┣ template.md
┃ ┃ ┃ ┗ template.drawio
┃ ┗ config.ini

`trestle author headers template-validate -tn my_task_name` Ensures that the respective template files are parseable.

`trestle author headers validate -tn my_task_name` Will validate all files within the directory against the templates by matching the extensions.

### Supported options

#### Recursive (`-r`, `--recurse`)

By default `author headers` only indexes a flat directory. The recursive option allows the discovery of sub directories.

#### Global (`-g`, `--global`)

Allows a single set of templates defined in `.trestle/author/__global__` to be applied to mulitple directories in trestle.
If `--task-name` is not provided all folders in the repository will be measured.

## `trestle author ssp-generate`

The `ssp-generate` sub-command creates a partial SSP (System Security Plan) from a profile and optional yaml header file.  `ssp-assemble` (described below) can later assemble the markdown files into a single json SSP file.  The profile contains a list of imports that are either a direct reference to a catalog, or an indirect reference via a profile.
There may be multiple imports of either type, and referenced profiles may themselves import either catalogs or profiles.  Each profile involved may specify
the controls that should be imported, along with any modifications to those controls.  This command internally creates a resolved profile catalog and generates a
directory containing a set of markdown files, one for each control in the resolved catalog.  Each markdown file has the optional yaml header embedded
at the start of the file.

Example usage for creation of the markdown:

`trestle author ssp-generate -p my_prof -y /my_yaml_dir/header.yaml -s 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence' -o my_ssp`

In this example the profile has previously been imported into the trestle project directory.  The profile itself must be in the trestle directory, but the imported catalogs and profiles may be URI's with href's as described below.

The `-s --section` argument specifies the name of Parts in the control for which the corresponding prose should be included in the control's markdown file.  Each colon-separated pair refers to the actual part name first, followed by the form that should be used in the heading for that section.  This is done because the name itself may be abbreviated and lack needed spaces between words.

(Note that the single quotes are required on Unix-like systems, but on Windows they are only needed if the contained string includes spaces, in which case *double* quotes should be used.)

In the example above, the two sections loaded are `ImplGuidance` and `ExpectedEvidence` - and their aliases are provided with full spacing and
spelling so the section headers will have proper titles.  The output will be placed in the trestle subdirectory `my_ssp` with a subdirectory
for each control group.

If the imported catalogs or profiles are not at the URI pointed to by the Import href of the profile then the href should be changed using the `trestle href` command.

The optional yaml header file can be anywhere in the file system.

<br>
<details>
<summary>The resulting files look like this</summary>

```
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

## `trestle author ssp-assemble`

After manually edting the markdown and providing the responses for the control implementation requirements, the markdown can be assembled into a single json SSP file with:

`trestle author ssp-assemble -m my_ssp -o my_json_ssp`

This will assemble the markdown files in the my_ssp directory and create a json SSP with name my_json_ssp in the system-security-plans directory.

As indicated for `ssp-generate`, please do not alter any of the horizontal rule lines or lines indicating the part or control id, e.g. `### Part a.`.  You may run `ssp-generate` and `ssp-assemble` repeatedly for the same markdown directory, allowing a continuous editing and updating cycle.
