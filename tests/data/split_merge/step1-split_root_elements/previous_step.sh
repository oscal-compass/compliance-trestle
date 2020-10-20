cd $TRESTLE_BASEDIR/catalogs/mycatalog/catalog

# Merges the properties inside each of the files passed in via the -f option to a destination file specified with the -d option.
trestle merge -f 'metadata.json,groups.json,back-matter.json' -d ../catalog.json

# In the near future, trestle merge should be smart enough to figure out which json files contain the elemenets that you want to be merged
# as well as the destination file that the elements should go in (every directory contains just one possible destination/parent file).
# In that case, both -f option and -d would be deprecated, -e option would be introduced and the commands would look like:
trestle merge -e 'metadata,groups,back-matter'

# In order to determine which elements the user can merge at this level, the following command can be used:
trestle merge -l
# which is the same as
trestle merge --list-available-elements



