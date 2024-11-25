---
title: FedRAMP plugin
description: Description of the compliance-trestle FedRAMP plugin for validating an SSP against the extended requirements for FedRAMP
---

# compliance-trestle-fedramp plugin

This plugin provides functionality for validating an SSP for FedRAMP compliance. It provides both an API interface and a trestle command for performing this validation.

## `trestle fedramp-validate`

This command allows users to validate existing OSCAL SSP file (in JSON or YAML format) for FedRAMP compliance. For example, `trestle fedramp-validate -f /local_dir/ssp.json -o report/` will validate `ssp.json` file for fedramp compliance and store the validation reports in `report` folder.

The following options are supported:

- `-f or --file`: specifies the path of an existing OSCAL SSP file. It may be an absolute or relative path. The file must be in either JSON or YAML format. This is a required option.
- `-o or --output`: specifies the name of the output directory where the validation reports will be stored. It may be an absolute or relative path. The output directory should already exist. This is also a required option.

The validation reports are created in XML and HTML format and provide details on which part of the SSP are not complaint as per FedRAMP specification.

## `trestle fedramp-transform`

This command allows users to extract information from an OSCAL SSP and transform it into a Word document based on the FedRAMP SSP Appendix A Template. The templates for the High, Moderate, and Low baseline security control requirements were retrieved from this [location](https://www.fedramp.gov/documents-templates/) and are bundled with the application. The `Control Summary Information` tables are populated for each control based on the OSCAL SSP.

For example, `trestle fedramp-transform -n ssp-name -l 'high' -o my_ssp.docx` will transform the OSCAL SSP file `ssp-name` into a Word document `my_ssp.docx` based on the SSP Appendix A - High FedRAMP Security Controls template.

The following options are supported:

- `-n or --ssp-name`: The name of the OSCAL SSP imported into trestle workspace. This is a required option.
- `-l or --level`: The baseline level corresponding to the template. This is high, moderate, low. This is a required option.
- `-o or --output-file`: The output location for the populated Word document. This is also a required option.
