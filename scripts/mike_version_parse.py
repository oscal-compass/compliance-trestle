#!/usr/bin/env python
"""Parsing of tags for mike."""
import sys

if __name__ == '__main__':
    assert len(sys.argv) == 2
    revision = sys.argv[1]

    components = revision.split('/')
    assert len(components) == 3
    if components[1] == 'heads' and components[2] == 'develop':
        print('latest')  # noqa: T201
        sys.exit(0)
    elif components[1] == 'tags' and components[2][0] == 'v':
        versions = components[2][1:].split('.')
        if 'rc' in components[2][1:]:
            print(components[2][1:])  # noqa: T201
        else:
            print(f'{versions[0]}.{versions[1]}')  # noqa: T201
        sys.exit(0)

sys.exit(1)
