# Tutorial: Introduction to trestle workflow

Here are step-by-step instructions to manipulate a [NIST](https://www.nist.gov/) standard [OSCAL](https://pages.nist.gov/OSCAL/) catalog using the [compliance-trestle](https://ibm.github.io/compliance-trestle/) (`"trestle"`) tool.

## *Objective*

Learn how to split and merge an OSCAL catalog json file using trestle commands and its command line interface (CLI).  Trestle simplifies the manipulation and management of large OSCAL documents by allowing controlled deconstruction into smaller components, and later reconstruction after editing those components.  And all operations guarantee that the individual files conform to the corresponding OSCAL schema to maintain integrity of the document in the process.

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

## Step 2: Import a catalog from the trestle sample data directory into your trestle workspace

For this tutorial we will use a catalog file from NIST, but we first must `import` it into the trestle workspace.  This can be done either by first downloading the file locally and then importing it, or you can download it directly using its url address.

We will import the file directly from the [NIST OSCAL github site](https://github.com/usnistgov/OSCAL).  The specific catalog is [NIST_SP-800-53_rev5_catalog.json](https://raw.githubusercontent.com/usnistgov/oscal-content/master/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json)

Import the file from the url with the following command:

```bash
trestle import -f https://raw.githubusercontent.com/usnistgov/oscal-content/master/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json -o mycatalog
```

As a reminder, you could also have imported the file from a local directory on your file system, or an sftp:// address.  But the file must first be imported to the trestle workspace in order for it to be directly manipulated by trestle as in this tutorial.

The `import` command will also check the
validity of the file including the presence of any duplicate uuid's.  If the file is manually created
please be sure it conforms with the current OSCAL schema (OSCAL version 1.0.0) and has no defined uuid's that are duplicates.
If there are any errors the Import will fail and the file must be corrected.

<br>
<details>
<summary>Your initial workspace will look like this</summary>

```text
my_workspace
 ┣ .trestle
 ┃ ┣ .keep
 ┃ ┗ config.ini
 ┣ assessment-plans
 ┃ ┗ .keep
 ┣ assessment-results
 ┃ ┗ .keep
 ┣ catalogs
 ┃ ┣ mycatalog
 ┃ ┃ ┗ catalog.json
 ┃ ┗ .keep
 ┣ component-definitions
 ┃ ┗ .keep
 ┣ dist
 ┃ ┣ assessment-plans
 ┃ ┃ ┗ .keep
 ┃ ┣ assessment-results
 ┃ ┃ ┗ .keep
 ┃ ┣ catalogs
 ┃ ┃ ┗ .keep
 ┃ ┣ component-definitions
 ┃ ┃ ┗ .keep
 ┃ ┣ plan-of-action-and-milestones
 ┃ ┃ ┗ .keep
 ┃ ┣ profiles
 ┃ ┃ ┗ .keep
 ┃ ┣ system-security-plans
 ┃ ┃ ┗ .keep
 ┃ ┗ target-definitions
 ┃ ┃ ┗ .keep
 ┣ plan-of-action-and-milestones
 ┃ ┗ .keep
 ┣ profiles
 ┃ ┗ .keep
 ┣ system-security-plans
 ┃ ┗ .keep
 ┗ target-definitions
 ┃ ┗ .keep
```

</details>
<br>

You will see that the directory now shows your catalog file in `my_workspace/catalogs/mycatalog/catalog.json`.  Note that the `.keep` files are simply to make sure git does not remove the directories - and can be ignored.  Also note that the json file itself is *singular* (catalog) while the directory above is plural (catalogs).  This convention is used throughout trestle because a given model directory like catalogs may contain several individual models - each of which is singular.  The imported catalog file size may be larger than the original due to a change in formatting, but the contents should be the same.

From here on in this tutorial we will just focus on the catalogs directory since the others are not directly involved.

You have now populated your trestle workspace with an OSCAL catalog that you can manipulate.  Let's start.

## Step 3: Split the file into smaller parts

The OSCAL schema specifies that a catalog must contain metadata, groups, and back-matter - so this command will pull them out of the original file and place them in separate json files for additional manipulations.

To begin splitting the file, first cd to the directory where `catalog.json` has been placed.

```bash
cd catalogs/mycatalog
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'
```

Here the `-f` refers to the filename of the json catalog file, and `-e` refers to the comma-separated list of `elements` you would like to split from the file.  This list does not represent the full file contents of the source `catalog.json` file, so some contents will be left behind in a much smaller `catalog.json` file after the split.  The elements that were split off will be placed in separate json files next to the new and smaller `catalog.json` file.

<br>
<details>
<summary>Your new catalogs directory with json files split out</summary>

```text
catalogs
 ┗ mycatalog
 ┃ ┣ catalog
 ┃ ┃ ┣ back-matter.json
 ┃ ┃ ┣ groups.json
 ┃ ┃ ┗ metadata.json
 ┃ ┗ catalog.json
```

</details>
<br>

Note there still remains a catalog.json file, but it is much smaller since the bulk of its contents have been split off.

Any split step can be reversed by a corresponding `merge` operation.  In this case we can go backwards with:

```bash
trestle merge -e 'catalog.metadata,catalog.groups,catalog.back-matter'
```

or simply

```bash
trestle merge -e 'catalog.*'
```

You can go back and forth splitting and merging, but for the next step please start with the above files split so that `metadata.json` can be further split.

## Step 4: Split the metadata into constituent files

```bash
cd catalog
trestle split -f ./metadata.json -e 'metadata.roles,metadata.parties,metadata.responsible-parties'
```

<br>
<details>
<summary>The directory will now look like this, with metadata split into files</summary>

```text

catalogs
 ┗ mycatalog
 ┃ ┣ catalog
 ┃ ┃ ┣ metadata
 ┃ ┃ ┃ ┣ parties.json
 ┃ ┃ ┃ ┣ responsible-parties.json
 ┃ ┃ ┃ ┗ roles.json
 ┃ ┃ ┣ back-matter.json
 ┃ ┃ ┣ groups.json
 ┃ ┃ ┗ metadata.json
 ┃ ┗ catalog.json

```

</details>
<br>

Again there remains a metadata.json file but it is smaller than the original.

And this step can be reversed with the following:

```bash
trestle merge -e 'metadata.roles,metadata.parties,metadata.responsible-parties'
```

or simply

```bash
trestle merge -e 'metadata.*'
```

## Step 5: Split metadata further using wildcards

```bash
cd metadata
trestle split -f ./roles.json -e 'roles.*'
trestle split -f ./responsible-parties.json -e 'responsible-parties.*'
```

<br>
<details>
<summary>The directory now looks like this, with new subdirectories containing multiple roles and responsible-parties</summary>

```text

catalogs
 ┗ mycatalog
 ┃ ┣ catalog
 ┃ ┃ ┣ metadata
 ┃ ┃ ┃ ┣ responsible-parties
 ┃ ┃ ┃ ┃ ┣ contact__responsible-party.json
 ┃ ┃ ┃ ┃ ┗ creator__responsible-party.json
 ┃ ┃ ┃ ┣ roles
 ┃ ┃ ┃ ┃ ┣ 00000__role.json
 ┃ ┃ ┃ ┃ ┗ 00001__role.json
 ┃ ┃ ┃ ┗ parties.json
 ┃ ┃ ┣ back-matter.json
 ┃ ┃ ┣ groups.json
 ┃ ┃ ┗ metadata.json
 ┃ ┗ catalog.json

```

</details>
<br>

Note that the presence of wildcards caused new directories to be created containing the full lists of roles and responsible parties.  You can read the wildcard as *split off **all** roles* from `roles.json`.

This split can be reversed with

```bash
trestle merge -e 'roles.*,responsible-parties.*'
```

## Step 6: Split groups and controls with two wildcards

This single command will split off *all* controls in *all* groups.  To do it you need to go back up into the catalog directory where the `groups.json` file is found:

```bash
cd ..
trestle split -f ./groups.json -e 'groups.*.controls.*'
```

<br>
<details>
<summary>Your directory is now very large with that one command!</summary>

```text

catalogs
 ┗ mycatalog
 ┃ ┣ catalog
 ┃ ┃ ┣ groups
 ┃ ┃ ┃ ┣ 00000__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00013__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00014__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00015__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00016__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00017__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00018__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00019__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00020__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00021__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00022__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00023__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00024__control.json
 ┃ ┃ ┃ ┣ 00001__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00005__control.json
 ┃ ┃ ┃ ┣ 00002__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00013__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00014__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00015__control.json
 ┃ ┃ ┃ ┣ 00003__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00008__control.json
 ┃ ┃ ┃ ┣ 00004__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00013__control.json
 ┃ ┃ ┃ ┣ 00005__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00012__control.json
 ┃ ┃ ┃ ┣ 00006__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00011__control.json
 ┃ ┃ ┃ ┣ 00007__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00009__control.json
 ┃ ┃ ┃ ┣ 00008__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00006__control.json
 ┃ ┃ ┃ ┣ 00009__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00007__control.json
 ┃ ┃ ┃ ┣ 00010__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00013__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00014__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00015__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00016__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00017__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00018__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00019__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00020__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00021__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00022__control.json
 ┃ ┃ ┃ ┣ 00011__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00010__control.json
 ┃ ┃ ┃ ┣ 00012__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00013__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00014__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00015__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00016__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00017__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00018__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00019__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00020__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00021__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00022__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00023__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00024__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00025__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00026__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00027__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00028__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00029__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00030__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00031__control.json
 ┃ ┃ ┃ ┣ 00013__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00008__control.json
 ┃ ┃ ┃ ┣ 00014__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00007__control.json
 ┃ ┃ ┃ ┣ 00015__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00009__control.json
 ┃ ┃ ┃ ┣ 00016__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00013__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00014__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00015__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00016__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00017__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00018__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00019__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00020__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00021__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00022__control.json
 ┃ ┃ ┃ ┣ 00017__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00013__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00014__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00015__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00016__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00017__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00018__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00019__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00020__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00021__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00022__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00023__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00024__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00025__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00026__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00027__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00028__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00029__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00030__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00031__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00032__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00033__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00034__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00035__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00036__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00037__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00038__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00039__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00040__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00041__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00042__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00043__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00044__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00045__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00046__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00047__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00048__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00049__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00050__control.json
 ┃ ┃ ┃ ┣ 00018__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00011__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00012__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00013__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00014__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00015__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00016__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00017__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00018__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00019__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00020__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00021__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00022__control.json
 ┃ ┃ ┃ ┣ 00019__group
 ┃ ┃ ┃ ┃ ┗ controls
 ┃ ┃ ┃ ┃ ┃ ┣ 00000__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00001__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00002__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00003__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00004__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00005__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00006__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00007__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00008__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00009__control.json
 ┃ ┃ ┃ ┃ ┃ ┣ 00010__control.json
 ┃ ┃ ┃ ┃ ┃ ┗ 00011__control.json
 ┃ ┃ ┃ ┣ 00000__group.json
 ┃ ┃ ┃ ┣ 00001__group.json
 ┃ ┃ ┃ ┣ 00002__group.json
 ┃ ┃ ┃ ┣ 00003__group.json
 ┃ ┃ ┃ ┣ 00004__group.json
 ┃ ┃ ┃ ┣ 00005__group.json
 ┃ ┃ ┃ ┣ 00006__group.json
 ┃ ┃ ┃ ┣ 00007__group.json
 ┃ ┃ ┃ ┣ 00008__group.json
 ┃ ┃ ┃ ┣ 00009__group.json
 ┃ ┃ ┃ ┣ 00010__group.json
 ┃ ┃ ┃ ┣ 00011__group.json
 ┃ ┃ ┃ ┣ 00012__group.json
 ┃ ┃ ┃ ┣ 00013__group.json
 ┃ ┃ ┃ ┣ 00014__group.json
 ┃ ┃ ┃ ┣ 00015__group.json
 ┃ ┃ ┃ ┣ 00016__group.json
 ┃ ┃ ┃ ┣ 00017__group.json
 ┃ ┃ ┃ ┣ 00018__group.json
 ┃ ┃ ┃ ┗ 00019__group.json
 ┃ ┃ ┣ metadata
 ┃ ┃ ┃ ┣ responsible-parties
 ┃ ┃ ┃ ┃ ┣ contact__responsible-party.json
 ┃ ┃ ┃ ┃ ┗ creator__responsible-party.json
 ┃ ┃ ┃ ┣ roles
 ┃ ┃ ┃ ┃ ┣ 00000__role.json
 ┃ ┃ ┃ ┃ ┗ 00001__role.json
 ┃ ┃ ┃ ┗ parties.json
 ┃ ┃ ┣ back-matter.json
 ┃ ┃ ┗ metadata.json
 ┃ ┗ catalog.json

```

</details>
<br>

All 20 groups of controls have been split off, and each one has a corresponding directory with its full list of controls in it.

You can then reverse the split with

```bash
trestle merge -e 'groups.*'
```

## Step 7: Collapse the entire directory structure back into a single `catalog.json` file - possibly after modifying individual files

You can collapse everything back to a single `catalog.json` file after first going up one directory to the mycatalog directory

```bash
cd ..
trestle merge -e 'catalog.*'
```

<br>
<details>
<summary>After all that splitting and merging you are back to this directory structure</summary>

```text

catalogs
 ┗ mycatalog
 ┃ ┗ catalog.json

```

</details>
<br>

## Conclusion

This completes the tutorial on using `trestle` to split and merge an OSCAL catalog file.  Not shown here are modifications of the individual files that would be done in an actual use case, but note that if any changes are made that violate the OSCAL schema, `trestle` will notice them and flag them in the merge.  This way not only does `trestle` allow user-driven decomposition and aggregation of these large, complex files; it also does constant checks on the contents against the required schema to make sure no errors are introduced in the process.
