cd $TRESTLE_BASEDIR/catalogs/mycatalog/catalog/metadata

# Splits the properties listed in the -e option that must exist in the file specified in the -f option.
trestle split -f ./roles.json -e 'roles.*'
trestle split -f ./responsible-parties.json -e 'responsible-parties.*'

# In the near future, trestle split should be smart enough to figure out which json file contains the elemenets you want to split
# In that case, the -f option would be deprecated and the commands would look like:
trestle split -e 'roles.*,responsible-parties.*'

# OR
trestle split -e 'roles.*' -e 'esponsible-parties.*'

# OR
trestle split -e 'roles.*'
trestle split -e 'responsible-parties.*'


REVERSE:
    trestle merge -e 'roles.*,responsible-parties.*'

or

cd $TRESTLE_BASEDIR/catalogs/mycatalog/catalog
    trestle merge -e 'metadata.roles.*,metadata.responsible-parties.*'
which is different from:
    trestle merge -e 'metadata.roles,metadata.responsible-parties'

or

cd $TRESTLE_BASEDIR/catalogs/mycatalog
    trestle merge -e 'catalog.metadata.roles.*,catalog.metadata.responsible-parties.*'
which is different from:
    trestle merge -e 'catalog.metadata.roles,catalog.metadata.responsible-parties'
