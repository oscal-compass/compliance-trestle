#!/usr/bin/env python3
"""
Download OSCAL release schemas and metaschemas.

This script downloads OSCAL JSON schemas and metaschemas from the official
NIST OSCAL GitHub releases. By default, it downloads the latest release,
but you can specify a specific version.

Usage:
    python3 scripts/download_oscal.py [--version VERSION]

Examples:
    python3 scripts/download_oscal.py                    # Download latest
    python3 scripts/download_oscal.py --version 1.2.1    # Download v1.2.1
    python3 scripts/download_oscal.py --version 1.1.2    # Download v1.1.2
"""

import argparse
import json
import shutil
import sys
import tempfile
import urllib.request
import urllib.error
import zipfile
from pathlib import Path


def get_latest_version():
    """Get the latest OSCAL release version from GitHub API."""
    api_url = 'https://api.github.com/repos/usnistgov/OSCAL/releases/latest'

    try:
        with urllib.request.urlopen(api_url) as response:  # noqa: S310
            data = json.loads(response.read().decode())
            tag_name = data.get('tag_name', '')
            # Remove 'v' prefix if present
            version = tag_name.lstrip('v')
            return version
    except Exception as e:
        print(f'Error fetching latest version: {e}')
        sys.exit(1)


def download_oscal(version, output_dir=None):
    """
    Download OSCAL release for the specified version.

    Args:
        version: OSCAL version to download (e.g., '1.2.2', '1.1.2')
        output_dir: Optional output directory (defaults to project root)
    """
    # Setup directories
    if output_dir is None:
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent
    else:
        output_dir = Path(output_dir)

    schemas_dir = output_dir / 'release-schemas'
    metaschemas_dir = output_dir / 'release-metaschemas'

    # Create directories if they don't exist
    schemas_dir.mkdir(exist_ok=True)
    metaschemas_dir.mkdir(exist_ok=True)

    # Download URL
    download_url = f'https://github.com/usnistgov/OSCAL/releases/download/v{version}/oscal-{version}.zip'

    # Use secure temporary files
    temp_dir = Path(tempfile.gettempdir())
    zip_path = temp_dir / f'oscal-{version}.zip'
    extract_path = temp_dir / f'oscal-extract-{version}'

    print(f'Downloading OSCAL v{version}...')
    print(f'  URL: {download_url}')

    try:
        # Download the zip file
        with urllib.request.urlopen(download_url) as response, open(zip_path, 'wb') as out_file:  # noqa: S310
            shutil.copyfileobj(response, out_file)

        print(f'  Downloaded: {zip_path}')

        # Extract the zip file
        print('Extracting schemas and metaschemas...')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # Copy JSON schemas
        json_schema_src = extract_path / 'json' / 'schema'
        if json_schema_src.exists():
            schema_files = list(json_schema_src.glob('*.json'))
            for schema_file in schema_files:
                shutil.copy2(schema_file, schemas_dir / schema_file.name)
            print(f'  Copied {len(schema_files)} JSON schemas to {schemas_dir}')
        else:
            print(f'  Warning: JSON schema directory not found: {json_schema_src}')

        # Copy metaschemas
        metaschema_src = extract_path / 'metaschema'
        if metaschema_src.exists():
            metaschema_files = list(metaschema_src.glob('*_RESOLVED.xml'))
            for metaschema_file in metaschema_files:
                shutil.copy2(metaschema_file, metaschemas_dir / metaschema_file.name)
            print(f'  Copied {len(metaschema_files)} metaschemas to {metaschemas_dir}')
        else:
            print(f'  Warning: Metaschema directory not found: {metaschema_src}')

        # Cleanup
        zip_path.unlink()
        shutil.rmtree(extract_path)

        print(f'\nSuccessfully downloaded OSCAL v{version}')
        print(f'  Schemas: {schemas_dir}/ ({len(list(schemas_dir.glob("*.json")))} files)')
        print(f'  Metaschemas: {metaschemas_dir}/ ({len(list(metaschemas_dir.glob("*_RESOLVED.xml")))} files)')

    except urllib.error.HTTPError as e:
        print(f'\nError: Failed to download OSCAL v{version}')
        print(f'  HTTP Error {e.code}: {e.reason}')
        print(f'  URL: {download_url}')
        print('\nPlease check that the version exists at:')
        print('  https://github.com/usnistgov/OSCAL/releases')
        sys.exit(1)
    except Exception as e:
        print(f'\nError: {e}')
        # Cleanup on error
        if zip_path.exists():
            zip_path.unlink()
        if extract_path.exists():
            shutil.rmtree(extract_path)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="""Download OSCAL release schemas and metaschemas.

This script automatically:
  1. Downloads the OSCAL release zip file from GitHub
  2. Extracts schemas and metaschemas
  3. Copies JSON schemas to release-schemas/
  4. Copies metaschemas to release-metaschemas/
  5. Cleans up temporary files
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Download latest release
  %(prog)s --version 1.2.2    # Download specific version
  %(prog)s --version 1.1.2    # Download older version
  %(prog)s -v 1.2.1           # Short form

Output directories:
  - JSON schemas: release-schemas/
  - Metaschemas: release-metaschemas/

Available versions can be found at:
  https://github.com/usnistgov/OSCAL/releases
        """,
    )

    parser.add_argument(
        '--version', '-v', help='OSCAL version to download (e.g., 1.2.2). If not specified, downloads latest.'
    )

    parser.add_argument('--output-dir', '-o', help='Output directory (defaults to project root)')

    args = parser.parse_args()

    # Determine version to download
    if args.version:
        version = args.version.lstrip('v')  # Remove 'v' prefix if present
        print(f'Downloading OSCAL v{version} (specified version)')
    else:
        print('Fetching latest OSCAL release version...')
        version = get_latest_version()
        print(f'Latest version: {version}')

    # Download OSCAL
    download_oscal(version, args.output_dir)


if __name__ == '__main__':
    main()

# Made with Bob
