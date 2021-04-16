# Known errors and limitations

## uft-8 encoding only

Trestle supports utf8 as a file text-encoding. If files are encountered without utf8 errors will be reported / thrown.
Trestle provides an script at `https://github.com/IBM/compliance-trestle/blob/develop/scripts/utf8me.py` which may be used.

WARNING: This script is potentially destructive and may remove / damage content. Ensure you have a backup before use.
