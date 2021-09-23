# run 1

rm -rf test_trestle
mkdir test_trestle
cd test_trestle
trestle init
trestle import -f path_to_NIST_SP-800-53_rev5_catalog.json -o mycatalog
cd catalogs/mycatalog
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'

trestle merge -e 'catalog.metadata,catalog.groups,catalog.back-matter'
trestle merge -e 'catalog.*'
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'
trestle merge -e 'catalog.*'
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'
cd catalog
trestle split -f ./metadata.json -e 'metadata.roles,metadata.parties,metadata.responsible-parties'
cd metadata
trestle split -f ./roles.json -e 'roles.*'
trestle merge -e 'roles.*'

