#!/usr/bin/env python3
"""
Query and test OSCAL namespace constraints.

This script reads the oscal_namespace.yaml file and tests all OSCAL namespace
constraints, displaying the results to the console. It can test all constraints
or filter by document type.

Usage:
    python scripts/oscal_namespace_query.py [--document-type TYPE]
    
Examples:
    python scripts/oscal_namespace_query.py
    python scripts/oscal_namespace_query.py --document-type catalog
    python scripts/oscal_namespace_query.py --document-type component
"""

import yaml
import subprocess
import sys
import argparse
from pathlib import Path
from collections import defaultdict

NAMESPACE_YAML_PATH = Path('trestle/resources/oscal_namespace.yaml')


def load_namespace_data(yaml_file):
    """Load the OSCAL namespace YAML file."""
    if not yaml_file.exists():
        print(f"Error: {yaml_file} not found.")
        print("Please run 'python3 scripts/extract_oscal_namespace.py' first.")
        sys.exit(1)
    
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def get_included_document_types(document_type):
    """
    Get list of document types that should be included when testing a specific document type.
    This includes the document type itself plus any common modules it imports.
    """
    if not document_type:
        return None
    
    includes = {
        'oscal-catalog': ['oscal-catalog', 'oscal-control-common', 'oscal-metadata'],
        'oscal-profile': ['oscal-profile', 'oscal-metadata', 'oscal-control-common'],
        'oscal-component-definition': ['oscal-component-definition', 'oscal-implementation-common'],
        'oscal-ssp': ['oscal-ssp', 'oscal-metadata', 'oscal-implementation-common'],
        'oscal-ap': ['oscal-ap', 'oscal-metadata', 'oscal-assessment-common'],
        'oscal-ar': ['oscal-ar', 'oscal-metadata', 'oscal-assessment-common'],
        'oscal-poam': ['oscal-poam', 'oscal-metadata', 'oscal-implementation-common', 'oscal-assessment-common'],
        'oscal-mapping-common': ['oscal-mapping-common', 'oscal-metadata'],
        'oscal-control-common': ['oscal-control-common'],
        'oscal-implementation-common': ['oscal-implementation-common'],
        'oscal-assessment-common': ['oscal-assessment-common'],
        'oscal-metadata': ['oscal-metadata'],
    }
    
    return includes.get(document_type, [document_type])


def extract_queries(namespace_data, filter_document_type=None):
    """
    Extract all possible queries from the namespace data.
    
    Args:
        namespace_data: Loaded YAML data
        filter_document_type: Optional document type to filter by (e.g., 'oscal-catalog')
                             When specified, includes constraints from imported common modules
    
    Returns:
        List of query dictionaries
    """
    queries = []
    namespaces = namespace_data['oscal_namespace']['namespaces']
    
    # Get list of document types to include (main type + common modules)
    doc_types_to_include = get_included_document_types(filter_document_type) if filter_document_type else None
    
    for namespace_uri, ns_data in namespaces.items():
        for document_type, doc_data in ns_data.items():
            # Filter by document type if specified (includes common modules)
            if doc_types_to_include and document_type not in doc_types_to_include:
                continue
                
            for element, elem_data in doc_data.items():
                for constraint_key, constraint_data in elem_data.items():
                    # Parse the constraint_key to extract element, attribute, and conditions
                    # Examples:
                    # - "prop[@name]"
                    # - "prop[@value] where name=type"
                    # - "relationship" (field value constraint)
                    
                    if '[@' in constraint_key:
                        # Attribute constraint
                        parts = constraint_key.split('[@')
                        elem = parts[0].strip()
                        rest = parts[1]
                        
                        if ']' in rest:
                            attr = rest.split(']')[0]
                            
                            # Check for conditions
                            conditions = []
                            if 'where' in constraint_key:
                                cond_part = constraint_key.split('where')[1].strip()
                                # Parse conditions like "name=type, class=value"
                                for cond in cond_part.split(','):
                                    cond = cond.strip()
                                    if '=' in cond:
                                        conditions.append(cond)
                            
                            queries.append({
                                'namespace': namespace_uri,
                                'document_type': document_type,
                                'element': elem,
                                'attribute': attr,
                                'conditions': conditions,
                                'constraint_key': constraint_key,
                                'num_values': len(constraint_data['allowed_values']),
                                'allow_other': constraint_data['allow_other']
                            })
                    else:
                        # Field value constraint (no attribute)
                        queries.append({
                            'namespace': namespace_uri,
                            'document_type': document_type,
                            'element': constraint_key,
                            'attribute': '',
                            'conditions': [],
                            'constraint_key': constraint_key,
                            'num_values': len(constraint_data['allowed_values']),
                            'allow_other': constraint_data['allow_other']
                        })
    
    return queries


def run_query(script_path, element, attribute='', conditions=None, namespace=None, document_type=None, constraint_key=None):
    """
    Run the get_oscal_values.py script with the given parameters.
    
    Args:
        script_path: Path to get_oscal_values.py
        element: Element name (e.g., 'prop')
        attribute: Attribute name (e.g., 'name')
        conditions: List of condition strings (e.g., ['name=type'])
        namespace: Namespace URI
        document_type: Document type (e.g., 'oscal-catalog')
        constraint_key: Full constraint key for exact matching (e.g., 'metadata/prop[@name]')
    
    Returns:
        Tuple of (success, output)
    """
    cmd = ['python3', str(script_path), element]
    
    if attribute:
        cmd.append(attribute)
    
    if conditions:
        for cond in conditions:
            cmd.extend(['--condition', cond])
    
    if namespace:
        cmd.extend(['--namespace', namespace])
    
    if document_type:
        cmd.extend(['--document-type', document_type])
    
    if constraint_key:
        cmd.extend(['--constraint-key', constraint_key])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return (result.returncode == 0, result.stdout)
    except subprocess.TimeoutExpired:
        return (False, "Query timed out")
    except Exception as e:
        return (False, f"Error: {str(e)}")


def main():
    """Main test driver function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Query and test OSCAL namespace constraints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --document-type oscal-catalog
  %(prog)s --document-type catalog
  %(prog)s --document-type component

Available Document Types:
  Main OSCAL Models:
    oscal-catalog, catalog
    oscal-profile, profile
    oscal-component-definition, component
    oscal-ssp, ssp
    oscal-ap, ap
    oscal-ar, ar
    oscal-poam, poam
    oscal-mapping, mapping, mapping-collection

  Common Modules (automatically included in main models):
    oscal-control-common
    oscal-implementation-common
    oscal-assessment-common
    oscal-metadata

Note: When querying a main model, constraints from its imported common
      modules are automatically included.
        """
    )
    parser.add_argument('--document-type', '-d',
                       help='Filter tests by document type')
    
    args = parser.parse_args()
    
    # Normalize document type with aliases
    document_type = args.document_type
    if document_type:
        aliases = {
            'mapping': 'oscal-mapping-common',
            'mapping-collection': 'oscal-mapping-common',
            'component': 'oscal-component-definition',
        }
        if document_type in aliases:
            document_type = aliases[document_type]
        elif not document_type.startswith('oscal-'):
            document_type = f'oscal-{document_type}'
    
    # Setup paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    yaml_file = project_root / NAMESPACE_YAML_PATH
    get_values_script = script_dir / 'get_oscal_values.py'
    
    if not get_values_script.exists():
        print(f"Error: {get_values_script} not found.")
        sys.exit(1)
    
    # Load namespace data
    namespace_data = load_namespace_data(yaml_file)
    
    # Extract all queries (optionally filtered by document type)
    queries = extract_queries(namespace_data, document_type)
    
    # Group queries by namespace
    queries_by_ns = defaultdict(list)
    for query in queries:
        queries_by_ns[query['namespace']].append(query)
    
    # Run tests
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for namespace_uri, ns_queries in sorted(queries_by_ns.items()):
        print(f"\n{'=' * 80}")
        print(f"Namespace: {namespace_uri}")
        print(f"{'=' * 80}\n")
        
        for i, query in enumerate(sorted(ns_queries, key=lambda x: x['constraint_key']), 1):
            total_tests += 1
            
            # Use the full constraint_key which includes hierarchical context
            # This shows exactly which constraint is being tested (e.g., 'metadata/prop[@name]')
            query_desc = query['constraint_key']
            
            # Add document type to description
            doc_type_desc = f" ({query['document_type']})" if query.get('document_type') else ""
            
            print(f"\n[{i}/{len(ns_queries)}] {query_desc}{doc_type_desc}")
            print(f"    Values: {query['num_values']}, allow_other={query['allow_other']}")
            
            # Run the query with full constraint_key for exact matching
            success, output = run_query(
                get_values_script,
                query['element'],
                query['attribute'],
                query['conditions'] if query['conditions'] else None,
                namespace_uri,
                query.get('document_type'),
                query['constraint_key']
            )
            
            if success:
                passed_tests += 1
                
                # Extract and display the values from output
                lines = output.strip().split('\n')
                for line in lines:
                    if line.strip().startswith('- '):
                        print(f"      {line.strip()}")
            else:
                failed_tests += 1
                print(f"    ERROR:")
                for line in output.split('\n')[:5]:  # Show first 5 lines of error
                    print(f"      {line}")
    
    # Exit with error code if any tests failed
    if failed_tests > 0:
        sys.exit(1)
        sys.exit(0)


if __name__ == '__main__':
    main()

# Made with Bob