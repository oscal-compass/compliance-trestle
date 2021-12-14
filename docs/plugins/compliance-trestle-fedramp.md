# compliance-trestle-fedramp plugin

This plugin provides functionality for validating an SSP for FedRAMP compliance. It provides both an API interface and a trestle command for performing this validation.

## `trestle fedramp-validate`

This command allow users to validate existing OSCAL SSP file (in JSON or YAML format) for FedRAMP complaince. For example, `trestle fedramp-validate -f /local_dir/ssp.json -o report/` will validate `ssp.json` file for fedramp complaince and store the validation reports in `report` folder.

The following options are supported:

- `-f or --file`: specifies the path of an existing OSCAL SSP file. It may be an absolute or relative path. The file must be in either JSON or YAML format. This is a required option.
- `-o or --output`: specifies the name of the output directory where the validation reports will be stored. It may be an absolute or relative path. The output directory should already exist. This is also a required option.

The validation reports are created in XML and HTML format and provide details on which part of the SSP are not complaint as per FedRAMP specification.
