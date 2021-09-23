# run 1

rm -rf test_trestle
mkdir test_trestle
cd test_trestle
trestle init
trestle import -f path_to/NIST_SP-800-53_rev4_catalog.json -o mycatalog

#trestle split -f catalogs/mycatalog/catalog.json -e 'catalog.groups'
cd catalogs
cd mycatalog
trestle split -f catalog.json -e 'catalog.groups.*.controls.*'
cd ../../
trestle validate -a












