### Contextual trestle command

trestle split -e metadata.title,metadata.last-modified,metadata.version,metadata.links,metadata.roles,metadata.parties,metadata.responsible-parties

# OR
trestle split -e metadata.title \
              -e metadata.last-modified \
              -e metadata.version \
              -e metadata.links \
              -e metadata.roles \
              -e metadata.parties \
              -e metadata.responsible-parties

# OR
trestle split -e metadata.title
trestle split -e metadata.last-modified
trestle split -e metadata.version
trestle split -e metadata.links
trestle split -e metadata.roles
trestle split -e metadata.parties
trestle split -e metadata.responsible-parties