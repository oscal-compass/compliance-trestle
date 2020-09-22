#! /usr/bin/env zsh -e
git submodule add https://github.com/usnistgov/OSCAL.git nist-source
git submodule update --init

OUTPUT_DIR=trestle/oscal
mkdir -p $OUTPUT_DIR
touch $OUTPUT_DIR/__init__.py

for i in `ls nist-source/json/schema| sed -e 's/oscal_\(.*\)_schema.json/\1/'`
do
  echo datamodel-codegen --input-file-type jsonschema --input nist-source/json/schema/oscal_${i}_schema.json --base-class trestle.core.base_model.OscalBaseModel --output $OUTPUT_DIR/$i:s/-/_/.py
  datamodel-codegen --input-file-type jsonschema --input nist-source/json/schema/oscal_${i}_schema.json --base-class trestle.core.base_model.OscalBaseModel --output $OUTPUT_DIR/$i:s/-/_/.py
  python scripts/fix_any.py $OUTPUT_DIR/$i:s/-/_/.py
done

# 3rd party schemas are explicilty codified rather than inferred.
echo datamodel-codegen --input-file-type jsonschema --input 3rd-party-schema-documents/IBM_target_schema.json --base-class trestle.core.base_model.OscalBaseModel --output $OUTPUT_DIR/target.py
datamodel-codegen --input-file-type jsonschema --input 3rd-party-schema-documents/IBM_target_schema.json --base-class trestle.core.base_model.OscalBaseModel --output $OUTPUT_DIR/target.py
python scripts/fix_any.py $OUTPUT_DIR/target.py