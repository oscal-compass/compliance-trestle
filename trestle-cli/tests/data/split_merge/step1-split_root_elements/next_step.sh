cd $TRESTLE_BASEDIR/catalogs/mycatalog/catalog

# Splits the properties listed in the -e option that must exist in the file specified in the -f option.
trestle split -f ./metadata.json -e 'metadata.roles,metadata.parties,metadata.responsible-parties'

# In the near future, trestle split should be smart enough to figure out which json file contains the elemenets you want to split
# In that case, the -f option would be deprecated and the commands would look like:
trestle split -e 'metadata.roles,metadata.parties,metadata.responsible-parties'

# OR
trestle split -e 'metadata.roles' \
              -e 'metadata.parties' \
              -e 'metadata.responsible-parties'
# OR
trestle split -e 'metadata.roles'
trestle split -e 'metadata.parties'
trestle split -e 'metadata.responsible-parties'



REVERSE:
    trestle merge -e 'metadata.roles,metadata.parties,metadata.responsible-parties'
    or
    trestle merge -e 'metadata.*'

or

cd $TRESTLE_BASEDIR/catalogs/mycatalog
    trestle split -e 'catalog.metadata.roles,catalog.metadata.parties,catalog.metadata.responsible-parties'

    trestle merge -e 'catalog.metadata.roles,catalog.metadata.parties,catalog.metadata.responsible-parties'
    or
    trestle merge -e 'catalog.metadata.*'
which is different from:
    trestle merge -e 'catalog.metadata'
