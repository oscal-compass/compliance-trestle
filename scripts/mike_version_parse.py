#!/usr/bin/env python
"""Parsing of tags for mike."""

import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError('Expected exactly one argument')
    revision = sys.argv[1]

    components = revision.split('/')
    if len(components) != 3:
        raise ValueError('Expected revision string with 3 components')
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
