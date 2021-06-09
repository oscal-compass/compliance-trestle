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

## `trestle author ssp`

The `ssp` sub-command creates a partial ssp from a catalog, profile and yaml header file.  It can also assemble the markdown files
into a single json SSP file.  The catalog consists of a number of controls with parameters, and the profile specifies a subset of
those controls along with corresponding parameter values.  This command merges the information from the two files and generates a
directory containing a set of markdown files, one for each control in the profile.  Each markdown file has the yaml header embedded
at the start of the file.

Example usage for creation of the markdown:

`trestle author ssp -f my_prof -yh /my_yaml_dir/header.yaml -s "ImplGuidance:Implied Guidance,ExpectedEvidence:Expected Evidence" -o my_ssp setup`

In this example the catalog and profile have previously been imported into the trestle project directory, making sure to import the
catalog using the name specified in the import href of the profile.  Note that the path in the href is ignored.  The yaml
header file can be anywhere in the file system.  In this case the two sections loaded are `ImplGuidance` and `ExpectedEvidence` -
and their aliases are provided with full spacing and spelling so the section headers will have proper titles.  The output will be
placed in the trestle subdirectory `my_ssp` with a subdirectory for each control group.

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


# ac-1 - AC Access Control Policy and Procedures
## Control Description

The organization:

a. Develops, documents, and disseminates to Assignment: organization-defined personnel or roles:

    1. An access control policy that addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance; and
    2. Procedures to facilitate the implementation of the access control policy and associated access controls; and

b. Reviews and updates the current:

    1. Access control policy at least annually; and
    2. Access control procedures at least annually.



## ac-1 What is the solution and how is it implemented?

---
### Part a.

Add control implementation description here.


---
### Part b.

Add control implementation description here.

---


## ac-1 Section Implied Guidance

Perform the needed tasks.

## ac-1 Section Expected Evidence

Provide detailed logs.
                       
```

</details>
<br>

Note that for each statement in the control description there is a corresponding response section in which to provide a detailed response for later inclusion in the final ssp as the control implementation.

Also note that the optional final sections are provided, and labeled using the alias given at the command line.

After manually edting the markdown and providing the responses for the control implementation requirements, the markdown can be assembled into a single json SSP file with:

`trestle author ssp -f my_ssp -o my_json_ssp assemble`

This will assemble the markdown files in the my_ssp directory and create a json SSP with name my_json_ssp in the system-security-plans directory.
