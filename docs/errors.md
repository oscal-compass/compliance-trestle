# Known errors and limitations

## utf-8 encoding only

Trestle supports only utf8 as a file text-encoding. If non-utf8 files are encountered, errors will be reported / thrown.
Trestle provides a [script](https://github.com/IBM/compliance-trestle/blob/develop/scripts/utf8me.py) that may be used to convert files to utf8 in a destructive manner that may change the file contents.

WARNING: This script is potentially destructive and may remove / damage content. Ensure you have a backup before use.
