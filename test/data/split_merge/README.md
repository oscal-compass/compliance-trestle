# Example of usage of `trestle split` and `trestle merge`

The contents of this folder contains an example of a catalog being split and merge by trestle.

We envision two different modes of running `trestle split/merge` subcommands:
- `Contextual mode`: it takes into account the directory the subcommand is running from to determine the path of the subcomponents that are being split or merged.
- `Non-contextual mode`: it uses the base folder of the trestle model (catalag, profile, target-definition, etc) as the root for determining the path of the subcomponents that are being split or merged. It requires the `-i` option to be specified in order to identify the model instance that will be affected. For example, `-i catalogs/mycatalog`

The changes to the `mycatalog` model used in this example can be performed using either of those two modes.

## Splitting and Merging `mycatalog` using Contextual mode

1. `cd $BASE_FOLDER/catalogs/mycatalog`
    
    In this example, the inital state of `mycatalog` in this example can be found in `step0-merged_catalog/catalogs/mycatalog`
   
2. `cd $BASE_FOLDER/catalogs/mycatalog`

   `trestle split -e uuid,metadata,groups,back-matter`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step1-split_root_elements/catalogs/mycatalog`

3. `cd $BASE_FOLDER/catalogs/mycatalog`
   
   `trestle split -e metadata.title,metadata.last-modified,metadata.version,metadata.links,metadata.roles,metadata.parties,metadata.responsible-parties`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step2-split_metadata_elements/catalogs/mycatalog`

4. `cd $BASE_FOLDER/catalogs/mycatalog/metadata`

   `trestle split -e roles[],responsible-parties{}`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step3-split_metadata_array_additionalproperties_elements/catalogs/mycatalog`

5. `cd $BASE_FOLDER/catalogs/mycatalog`

   `trestle split -e groups[].controls`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step4_split_groups_array/catalogs/mycatalog`

6. `cd $BASE_FOLDER/catalogs/mycatalog`
     
   `trestle merge -e uuid,metadata,groups,back-matter`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step0-merged_catalog/catalogs/mycatalog`


## Splitting and Merging `mycatalog` using Non-contextual mode

1. `cd $BASE_FOLDER`
    
    In this example, the inital state of `mycatalog` in this example can be found in `step0-merged_catalog/catalogs/mycatalog`
   
2. `trestle split -i catalogs/mycatalog -e uuid,metadata,groups,back-matter`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step1-split_root_elements/catalogs/mycatalog`

3. `trestle split -e metadata.title,metadata.last-modified,metadata.version,metadata.links,metadata.roles,metadata.parties,metadata.responsible-parties`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step2-split_metadata_elements/catalogs/mycatalog`

4. `trestle split -e metadata.roles[],metadata.responsible-parties{}`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step3-split_metadata_array_additionalproperties_elements/catalogs/mycatalog`

5. `trestle split -e groups[].controls`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step4_split_groups_array/catalogs/mycatalog`

6. `trestle merge -e uuid,metadata,groups,back-matter`

    In this example, the result state of `mycatalog` in this example for this step can be found in `step0-merged_catalog/catalogs/mycatalog`