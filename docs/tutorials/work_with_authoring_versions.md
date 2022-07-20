# Tutorial: Work with template versions when authoring

Here are step-by-step instructions on how to work with template versions when
authoring content using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) (`"trestle"`) tool.

## Step 1: Create a trestle workspace if you don't have one already

This will initialize Trestle workspace that would contain all your templates and governed documents.

```bash
mkdir my_workspace
cd my_workspace
trestle init
>>> Initialized trestle project successfully in [user_path]/my_workspace
```

The templates will be located in the `/my_workspace/.trestle/author/`. Please note that if you use MacOS or Linux distribution, by default `.trestle` will be hidden. You will need to reconfigure your system to show hidden folders.

## Step 2: Setup or create a new template version

Say you would like to have a collection of governed decisions. This step will create a new template of version `0.0.2` for such documents.
Please note that `0.0.1` is restricted for backward compatibility and should not be used.

```bash
cd my_workspace 
trestle author docs setup -tn decisions -tv 0.0.2
>>> Set template version to 0.0.2.
>>> Template file setup for task decisions at .trestle/author/decisions/0.0.2/template.md
>>> Task directory is decisions
```

Note: version 0.0.1 is reserved for unversioned documents.

## Step 3: Create a new document using a particular template version

Now that we have a template, we would like to create an instance of this template that would actually have content in it.
This steps will create a complete copy of the template of version `0.0.2` that you can fill in with custom content.

```bash
cd my_workspace 
trestle author docs create-sample -tn decisions -tv 0.0.2
>>> Set template version to 0.0.2.
```

## Step 4: Validate documents against a particular template version

After filling the decision document with content, you can validate it against the template to make sure that all required fields in the header are present and all the required headings are present.
This mechanism allows authors to ensure that all required content is present and in the correct format.

```bash
cd my_workspace 
trestle author docs validate -tn decisions
>>> Instances will be validated against template version specified in their headers.
>>> VALID: decisions/decision_000.md
```
