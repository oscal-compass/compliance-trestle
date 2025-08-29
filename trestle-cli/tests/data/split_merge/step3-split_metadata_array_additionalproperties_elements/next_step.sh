cd $TRESTLE_BASEDIR/catalogs/mycatalog/catalog

# Splits the properties listed in the -e option that must exist in the file specified in the -f option.
trestle split -f ./groups.json -e 'groups.*.controls.*'

# In the near future, trestle split should be smart enough to figure out which json file contains the elemenets you want to split
# In that case, the -f option would be deprecated and the commands would look like:
trestle split -e 'groups.*.controls.*'


REVERSE:
    trestle merge -e 'groups.*'

    trestle merge -e 'groups.*.controls.*' -d 'catalog'

or

cd $TRESTLE_BASEDIR/catalogs/mycatalog
    trestle merge -e 'catalog.groups.*'
which is different from:
    trestle merge -e 'catalog.groups'
