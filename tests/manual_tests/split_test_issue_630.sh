# Test for issue 630


rm -rf test_trestle
mkdir test_trestle
cd test_trestle
trestle init
#UPDATE HERE!!!!!!
trestle import -f path_to/NIST_SP-800-53_rev4_catalog.json -o mycatalog
#UPDATE HERE!!!!!!
cd catalogs
cd mycatalog
trestle split -f catalog.json -e 'catalog.metadata'

trestle split -f 'catalog/metadata.json' -e 'metadata.props'