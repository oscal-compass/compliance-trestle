cd $TRESTLE_BASEDIR/catalogs/mycatalog

# Splits the properties listed in the -e option that must exist in the file specified in the -f option.
trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'

# In the near future, trestle split should be smart enough to figure out which json file contains the elemenets you want to split
# In that case, the -f option would be deprecated and the commands would look like:
trestle split -e 'catalog.metadata,catalog.groups,catalog.back-matter'


REVERSE: 
    trestle merge -e 'catalog.metadata,catalog.groups,catalog.back-matter'
    or
    trestle merge -e 'catalog.*'