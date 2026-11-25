#!/usr/bin/env python3
"""
Query OSCAL namespace for valid values.

This script queries the oscal_namespace.yaml file to retrieve allowed values
for a given OSCAL path and optionally an attribute.

Usage:
    python3 scripts/get_oscal_values.py <path> [attribute]

Examples:
    # Attribute constraints:
    python3 scripts/get_oscal_values.py catalog.part.prop name
    python3 scripts/get_oscal_values.py component.prop name
    python3 scripts/get_oscal_values.py prop value --condition name=type

    # Field value constraints:
    python3 scripts/get_oscal_values.py mapping-collection.mappings.maps.relationship
    python3 scripts/get_oscal_values.py relationship
"""

import yaml
import sys
import argparse
from pathlib import Path

NAMESPACE_YAML_PATH = Path('trestle/resources/oscal_namespace.yaml')


def load_namespace_data(yaml_file):
    """Load the OSCAL namespace YAML file."""
    if not yaml_file.exists():
        print(f'Error: {yaml_file} not found.')
        print("Please run 'python3 scripts/extract_oscal_namespace.py' first.")
        sys.exit(1)

    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def normalize_path(path):
    """
    Normalize a path to extract document type and element.

    Supports:
    - Full metaschema names: oscal-catalog, oscal-mapping-common
    - Short metaschema names: catalog, mapping-common (adds oscal- prefix)
    - User-friendly aliases: mapping, mapping-collection -> oscal-mapping-common

    Examples:
        'catalog.metadata.prop' -> ('oscal-catalog', 'prop')
        'mapping.relationship' -> ('oscal-mapping-common', 'relationship')
        'mapping-collection.relationship' -> ('oscal-mapping-common', 'relationship')

    Returns:
        Tuple of (document_type, element)
        - document_type: Full oscal- prefixed metaschema name or None
        - element: The final element name
    """
    parts = path.split('.')

    if len(parts) > 1:
        first_part = parts[0]

        # User-friendly aliases that map to actual metaschema document types
        # These handle cases where the user-facing name differs from internal organization
        aliases = {
            'mapping': 'oscal-mapping-common',
            'mapping-collection': 'oscal-mapping-common',
            'oscal-mapping': 'oscal-mapping-common',
            'component': 'oscal-component-definition',
            'oscal-component': 'oscal-component-definition',
        }

        if first_part in aliases:
            document_type = aliases[first_part]
        elif first_part.startswith('oscal-'):
            # Already has oscal- prefix, use as-is
            document_type = first_part
        else:
            # Add oscal- prefix
            document_type = f'oscal-{first_part}'

        element = parts[-1]
    else:
        document_type = None
        element = parts[-1]

    return document_type, element


def get_included_document_types(document_type):
    """
    Get list of document types that should be included when querying a specific document type.
    This includes the document type itself plus any common modules it imports.

    Args:
        document_type: The main document type (e.g., 'oscal-catalog')

    Returns:
        List of document types to search (e.g., ['oscal-catalog', 'oscal-control-common', 'oscal-metadata'])
    """
    if not document_type:
        return None

    # Mapping of main document types to their included common modules
    # Based on actual metaschema import statements
    includes = {
        'oscal-catalog': ['oscal-catalog', 'oscal-control-common', 'oscal-metadata'],
        'oscal-profile': ['oscal-profile', 'oscal-metadata', 'oscal-control-common'],
        'oscal-component-definition': ['oscal-component-definition', 'oscal-implementation-common'],
        'oscal-ssp': ['oscal-ssp', 'oscal-metadata', 'oscal-implementation-common'],
        'oscal-ap': ['oscal-ap', 'oscal-metadata', 'oscal-assessment-common'],
        'oscal-ar': ['oscal-ar', 'oscal-metadata', 'oscal-assessment-common'],
        'oscal-poam': ['oscal-poam', 'oscal-metadata', 'oscal-implementation-common', 'oscal-assessment-common'],
        'oscal-mapping-common': ['oscal-mapping-common', 'oscal-metadata'],
        # Common modules can be queried directly
        'oscal-control-common': ['oscal-control-common'],
        'oscal-implementation-common': ['oscal-implementation-common'],
        'oscal-assessment-common': ['oscal-assessment-common'],
        'oscal-metadata': ['oscal-metadata'],
    }

    return includes.get(document_type, [document_type])


def find_matching_constraints(
    namespace_data, element, attribute, namespace_uri=None, conditions=None, document_type=None, constraint_key=None
):
    """
    Find constraints matching the given element and attribute.

    Args:
        namespace_data: Loaded YAML data
        element: Element name (e.g., 'prop', 'part', 'relationship')
        attribute: Attribute name (e.g., 'name', 'value') or empty string for field value constraints
        namespace_uri: Optional namespace URI to filter by
        conditions: Optional dict of conditions (e.g., {'name': 'type'})
        document_type: Optional document type to filter by (e.g., 'oscal-catalog', 'oscal-ssp')
        constraint_key: Optional exact constraint key to match (e.g., 'metadata/prop[@name]')
                       When provided, only returns exact matches for this constraint

    Returns:
        List of matching constraints with their allowed values
    """
    namespaces = namespace_data['oscal_namespace']['namespaces']

    # Default to OSCAL namespace if not specified
    if namespace_uri is None:
        namespace_uri = 'http://csrc.nist.gov/ns/oscal'

    if namespace_uri not in namespaces:
        return []

    ns_data = namespaces[namespace_uri]
    matches = []

    # Get list of document types to search (includes common modules)
    doc_types_to_search = get_included_document_types(document_type) if document_type else None

    # Iterate through document types
    for doc_type, doc_data in ns_data.items():
        # Filter by document type if specified
        if doc_types_to_search and doc_type not in doc_types_to_search:
            continue

        # Search through all elements in this document type
        for elem_key, elem_data in doc_data.items():
            # If exact constraint_key is specified, we need to match the full elem_key
            if constraint_key:
                # Extract the element path from constraint_key (e.g., 'metadata/prop' from 'metadata/prop[@name]')
                # The elem_key in the YAML is the hierarchical path (e.g., 'metadata/prop')
                if '[@' in constraint_key:
                    expected_elem_key = constraint_key.split('[@')[0]
                else:
                    expected_elem_key = constraint_key

                # Skip if elem_key doesn't match
                if elem_key != expected_elem_key:
                    continue
            else:
                # No exact constraint_key specified, use fuzzy matching
                # elem_key could be 'prop', 'part', 'metadata/prop', 'relationship', etc.
                if element not in elem_key:
                    continue

            # Search through constraints for this element
            for ck, constraint_data in elem_data.items():
                # ck format examples:
                # - "prop[@name]"
                # - "prop[@value] where name=type"
                # - "relationship" (field value constraint, no attribute)

                # If exact constraint_key is specified, only match that exact constraint
                if constraint_key and ck != constraint_key:
                    continue

                # Check if this is a field value constraint (no attribute)
                if not attribute or attribute == 'value':
                    # For field value constraints, the ck could be:
                    # - Just the element name (e.g., 'relationship')
                    # - A hierarchical path (e.g., 'map/relationship')
                    # Match if ck equals element OR if ck ends with element
                    if ck == element or (ck == elem_key and elem_key.endswith('/' + element)):
                        matches.append(
                            {
                                'element_key': elem_key,
                                'constraint_key': ck,
                                'allowed_values': constraint_data['allowed_values'],
                                'allow_other': constraint_data['allow_other'],
                                'definitions': constraint_data['definitions'],
                                'source_files': constraint_data['source_files'],
                                'document_type': doc_type,
                            }
                        )
                        continue

                # Check if attribute matches (for attribute constraints)
                if attribute and f'[@{attribute}]' not in ck:
                    continue

                # Check conditions if specified
                if conditions:
                    # Parse conditions from ck
                    if 'where' in ck:
                        constraint_conditions = constraint_data.get('conditions', {})
                        if not all(constraint_conditions.get(k) == v for k, v in conditions.items()):
                            continue
                    else:
                        # Conditions specified but constraint has none
                        continue
                else:
                    # No conditions specified, prefer constraints without conditions
                    if 'where' in ck:
                        continue

                matches.append(
                    {
                        'element_key': elem_key,
                        'constraint_key': ck,
                        'allowed_values': constraint_data['allowed_values'],
                        'allow_other': constraint_data['allow_other'],
                        'definitions': constraint_data['definitions'],
                        'source_files': constraint_data['source_files'],
                        'document_type': doc_type,
                    }
                )

    return matches


def format_output(matches, verbose=False):
    """Format the output for display."""
    if not matches:
        return 'No matching constraints found.'

    output = []

    for i, match in enumerate(matches):
        if len(matches) > 1:
            doc_type = match.get('document_type', 'unknown')
            output.append(f'\n=== Match {i + 1}: {match["constraint_key"]} (Document: {doc_type}) ===')

        output.append(f'Allowed values ({len(match["allowed_values"])}):')
        for value in match['allowed_values']:
            output.append(f'  - {value}')

        if match['allow_other']:
            output.append('  (other values are also allowed)')

        if verbose:
            output.append('\nSource files:')
            for source in match['source_files']:
                output.append(f'  - {source}')

            output.append('\nDefinitions:')
            for defn in match['definitions']:
                deprecated = f' [DEPRECATED: {defn["deprecated"]}]' if 'deprecated' in defn else ''
                output.append(f'  - {defn["value"]}{deprecated}')
                if defn['description']:
                    # Wrap long descriptions
                    desc = defn['description'].replace('\n', ' ').strip()
                    if len(desc) > 80:
                        desc = desc[:77] + '...'
                    output.append(f'    {desc}')

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Query OSCAL namespace for valid values',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s catalog.part.prop name
  %(prog)s component.prop name
  %(prog)s prop value --condition name=type
  %(prog)s prop name --verbose
  %(prog)s catalog.parameter.prop name --document-type catalog
  %(prog)s mapping-collection.mappings.maps.relationship

Available Document Types:
  Main OSCAL Models:
    catalog, profile, component, ssp, ap, ar, poam, oscal-mapping, mapping, mapping-collection
    (or with oscal- prefix: oscal-catalog, oscal-profile, etc.)

  Common Modules:
    oscal-control-common, oscal-implementation-common, oscal-assessment-common, oscal-metadata

Note: When specifying a document type, constraints from imported common
      modules (control-common, implementation-common, assessment-common,
      metadata) are automatically included.
        """,
    )

    parser.add_argument('path', help='OSCAL path (e.g., catalog.part.prop, relationship)')
    parser.add_argument(
        'attribute', nargs='?', default='', help='Attribute name (e.g., name, value). Omit for field value constraints.'
    )
    parser.add_argument(
        '--condition', '-c', action='append', help='Condition in format key=value (can be specified multiple times)'
    )
    parser.add_argument(
        '--namespace', '-n', default='http://csrc.nist.gov/ns/oscal', help='Namespace URI (default: OSCAL namespace)'
    )
    parser.add_argument('--document-type', '-d', help='Filter by document type (includes imported common modules)')
    parser.add_argument('--constraint-key', '-k', help='Exact constraint key to match (e.g., metadata/prop[@name])')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information including descriptions')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    # Parse conditions
    conditions = {}
    if args.condition:
        for cond in args.condition:
            if '=' not in cond:
                print(f"Error: Invalid condition format '{cond}'. Use key=value")
                sys.exit(1)
            key, value = cond.split('=', 1)
            conditions[key.strip()] = value.strip()

    # Load namespace data
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    yaml_file = project_root / NAMESPACE_YAML_PATH

    namespace_data = load_namespace_data(yaml_file)

    # Normalize path to get document type and element
    document_type, element = normalize_path(args.path)

    # Override document_type if explicitly provided
    if args.document_type:
        document_type = args.document_type

    # Find matching constraints
    matches = find_matching_constraints(
        namespace_data,
        element,
        args.attribute,
        args.namespace,
        conditions if conditions else None,
        document_type,
        args.constraint_key,
    )

    # Output results
    if args.json:
        import json

        result = {
            'path': args.path,
            'element': element,
            'attribute': args.attribute,
            'namespace': args.namespace,
            'conditions': conditions if conditions else None,
            'matches': matches,
        }
        print(json.dumps(result, indent=2))
    else:
        print(f'Query: {args.path} [@{args.attribute}]')
        if document_type:
            print(f'Document Type: {document_type}')
        if conditions:
            print(f'Conditions: {conditions}')
        print(f'Namespace: {args.namespace}')
        print()
        print(format_output(matches, args.verbose))


if __name__ == '__main__':
    main()

# Made with Bob
