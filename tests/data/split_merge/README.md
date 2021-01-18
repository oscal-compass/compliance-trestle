# How to navigate through this example

The contents of this folder show the evolution of a catalog model named `mycatalog` as it is split and merged by trestle.

It also contains an example of a `config.ini` file under `.trestle` folder specifying the default or reference decomposition behaviour of each model.

The commands responsible for the changes in contents between subsequent steps can be found in files named `next_step.sh` and/or `previous_step.sh`. The location of those files in a `step*` folder indicates where those commands are run from.

The story told by the steps can be summarised as:

## Step 0:

- The catalog model is all in one piece and its contents are all in `catalog.json`.
- `./next_step.sh` contains the command that splits the catalog into `uuid`, `metadata`, `groups` and `back-matter`.

## Step 1:

- The catalog model gets split into `uuid`, `metadata`, `groups` and `back-matter`.
- `./next_step.sh` contains the command that splits the catalog metadata property into each of its properties: `metadata.title`, `metadata.last-modified`, `metadata.version`,`metadata.links`, `metadata.roles`, `metadata.parties`, `metadata.responsible-parties`.
- `./previous_step.sh` contains the command reverses the split executed on step 0.

## Step 2:

- The catalog metadata subcomponent gets split into `metadata.title`, `metadata.last-modified`, `metadata.version`,`metadata.links`, `metadata.roles`, `metadata.parties`, `metadata.responsible-parties`.
- `metadata/next_step.sh` contains the command that splits each collection item in the metadata properties of roles and responsible-parties.
- `./previous_step.sh` contains the command reverses the split executed on step 1.

## Step 3:

- Each collection item in the `metadata.roles` and `metadata.responsible-parties` gets split.
- `./next_step.sh` contains the command that splits each collection item in catalog groups and, for each group, each collection item in controls.
- `metadata/previous_step.sh` contains the command reverses the split executed on step 2.

## Step 4:

- Each collection item in the `catalog.groups` and `catalog.groups.*.controls` gets split.
- `./next_step.sh` contains the command that merges everything back to how it looks at step 0.
- `./previous_step.sh` contains the command reverses the split executed on step 3.
