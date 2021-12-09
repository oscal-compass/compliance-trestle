# Tutorial: Work with template versions when authoring

Here are step-by-step instructions on how to work with template versions when
authoring content using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) (`"trestle"`) tool.

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
