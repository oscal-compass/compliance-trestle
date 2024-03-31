##### gen_oscal.py

Notes moving to OSCAL `1.1.2` from `1.0.4`

- Modify (by hand edit) the location of `"oscal-component-definition-oscal-metadata:metadata"` in file `oscal_component_schema.json` to be commensurate with the other models so that file `trestle/oscal/common.py` is properly generated.

- Update `pyproject.toml` to include `line_length = 200` to fix problem of class bodies not matching due to extra left and right parens to some but not all statements by datamodel-codegen tool.

- Update to modify (automated) the location of `"oscal-component-definition-oscal-metadata:metadata"` in file `oscal_component_schema.json` to be commensurate with the other models so that file `trestle/oscal/common.py` is properly generated. This includes creation of a new folder `release-...-fixup` that has both the changed and unchanged schemas for comparison with the originals and use by the normalization code.

- Update to automate parse of meta-schema for OSCAL version and set OSCAL_VERSION in oscal/__init__.py.