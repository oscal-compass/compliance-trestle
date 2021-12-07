# Tutorial: Work with template versions when authoring

Here are step-by-step instructions on how to work with template versions when
authoring content using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) (`"trestle"`) tool.

## *Objective*

Learn how to setup, create, and validate authored documents using mulitple template versions.

This tutorial assumes you have installed Python and installed trestle in a virtual environment per the directions found [here](../python_trestle_setup.md).

The examples shown will work for linux and mac, but Windows will require the following modifications:

<ul>
<li>use backslashes `\` for file paths (this is optional in most cases)
<li>use copy instead of cp (unless you have cp installed)
<li>use md instead of mkdir (unless you have mkdir installed)
<li>quotes (') are often not needed unless the text includes spaces, but if quotes are needed they should be double quotes (")
</ul>

Commands are shown without prompts so they are easy to cut and paste, and responses by trestle are shown with >>> at the start of the line.  In actual usage the >>> would not appear.

Be sure to include the quotes (' ') as shown in the examples, e.g. `merge -e 'catalog.*'` \[On windows you should probably use double quotes (") as needed.\]

In this tutorial you will see sections that contain dropdown that is revealed when you click on them.  Below is an example ("Like this").  Be sure to click on those sections to see their contents - and then close them if you like.

<br>
<details>
<summary>Like this</summary>

```text

more
information
in
here

```

</details>
<br>

## Step 1: Create a trestle workspace if you don't have one already

```bash
mkdir my_workspace
cd my_workspace
trestle init
>>> Initialized trestle project successfully in [user_path]/my_workspace
```

## Step 2: Setup or create a new template version

```bash
cd my_workspce 
trestle author docs setup -tn version_test -tv 0.0.2
>>> Set template version to 0.0.2.
>>> Template file setup for task version_test at .trestle/author/version_test/0.0.2/template.md
>>> Task directory is version_test
```

Note: version 0.0.1 is reserved for unversioned documents.

## Step 3: Create a new document using a particular template version

```bash
cd my_workspce 
trestle author docs create-sample -tn version_test -tv 0.0.2
>>> Set template version to 0.0.2.
```

## Step 4: Validate documents against a particular template version

```bash
cd my_workspce 
trestle author docs validate -tn version_test
>>> Instances will be validated against template version specified in their headers.
>>> VALID: version_test/version_test_000.md
```
