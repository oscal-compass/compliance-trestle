#!/usr/bin/env python3
"""
Extract OSCAL namespace constraints from metaschema files.

This script parses OSCAL metaschema XML files to extract all allowed-values
constraints that define the OSCAL default namespace vocabulary. It generates
a YAML file representing the complete OSCAL namespace structure.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import yaml
import re
import sys

NAMESPACE_YAML_PATH = Path('trestle/resources/oscal_namespace.yaml')


def parse_metaschema(file_path):
    """Parse a metaschema file and extract OSCAL namespace constraints."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Define namespace
    ns = {'m': 'http://csrc.nist.gov/ns/oscal/metaschema/1.0'}
    
    # Extract document type from short-name
    short_name_elem = root.find('m:short-name', ns)
    document_type = short_name_elem.text if short_name_elem is not None else 'unknown'
    
    constraints = []
    
    # Find all allowed-values elements with has-oscal-namespace
    for allowed_values in root.findall('.//m:allowed-values', ns):
        target = allowed_values.get('target', '')
        
        # Check if this constraint uses has-oscal-namespace
        if 'has-oscal-namespace' not in target:
            continue
            
        constraint_id = allowed_values.get('id', '')
        allow_other = allowed_values.get('allow-other', 'no')
        
        # Find the parent assembly or field that contains this constraint
        parent_context = None
        for assembly in root.findall('.//m:define-assembly', ns):
            if allowed_values in list(assembly.iter()):
                parent_context = assembly.get('name')
                break
        if parent_context is None:
            for field in root.findall('.//m:define-field', ns):
                if allowed_values in list(field.iter()):
                    parent_context = field.get('name')
                    break
        
        # Extract the target path and attribute
        # Examples:
        # prop[has-oscal-namespace('http://csrc.nist.gov/ns/oscal')]/@name
        # prop[has-oscal-namespace('http://csrc.nist.gov/ns/oscal') and @name='type']/@value
        # .[has-oscal-namespace('http://csrc.nist.gov/ns/oscal')] - field value constraint
        
        # Parse target to extract context and attribute
        target_match = re.search(r"([^[]+)\[has-oscal-namespace\([^)]+\)([^\]]*)\]/@(\w+)", target)
        if not target_match:
            # Try simpler pattern for targets like ".[has-oscal-namespace(...)]"
            # This is a field value constraint, need to find the parent field/flag name
            target_match = re.search(r"\.\[has-oscal-namespace\([^)]+\)\]", target)
            if target_match:
                # Find the parent define-field or define-flag element
                parent = allowed_values
                field_name = None
                while parent is not None:
                    if parent.tag.endswith('define-field') or parent.tag.endswith('define-flag'):
                        field_name = parent.get('name')
                        break
                    parent = parent.find('..')  # This won't work with ElementTree
                    # Need to search from root instead
                    break
                
                # Alternative: search for parent in the tree
                if field_name is None:
                    # Find all define-field and define-flag elements that contain this allowed-values
                    for define_elem in root.findall('.//m:define-field', ns):
                        if allowed_values in define_elem.iter():
                            field_name = define_elem.get('name')
                            break
                    if field_name is None:
                        for define_elem in root.findall('.//m:define-flag', ns):
                            if allowed_values in define_elem.iter():
                                field_name = define_elem.get('name')
                                break
                
                if field_name:
                    element = field_name
                    conditions = ""
                    attribute = ""  # Empty means it's the field value itself, not an attribute
                else:
                    # Fallback to "." if we can't find the parent
                    element = "."
                    conditions = ""
                    attribute = ""
            else:
                continue
        else:
            element = target_match.group(1).strip()
            conditions = target_match.group(2).strip()
            attribute = target_match.group(3)
        
        # Prepend parent context if found and element is not already a path
        if parent_context and '/' not in element and element != '.':
            element = f"{parent_context}/{element}"
        
        # Extract namespace from target
        ns_match = re.search(r"has-oscal-namespace\('([^']+)'\)", target)
        namespace = ns_match.group(1) if ns_match else 'http://csrc.nist.gov/ns/oscal'
        
        # Extract additional conditions (like @name='type')
        condition_dict = {}
        if conditions:
            cond_matches = re.findall(r"@(\w+)='([^']+)'", conditions)
            for cond_name, cond_value in cond_matches:
                condition_dict[cond_name] = cond_value
        
        # Extract enum values
        enums = []
        for enum in allowed_values.findall('m:enum', ns):
            value = enum.get('value', '')
            deprecated = enum.get('deprecated', '')
            description = ''.join(enum.itertext()).strip()
            # Remove the value from the description
            if description.startswith(value):
                description = description[len(value):].strip()
            
            enum_data = {
                'value': value,
                'description': description
            }
            if deprecated:
                enum_data['deprecated'] = deprecated
                
            enums.append(enum_data)
        
        constraint = {
            'id': constraint_id,
            'file': file_path.name,
            'document_type': document_type,
            'target': target,
            'element': element,
            'attribute': attribute,
            'namespace': namespace,
            'allow_other': allow_other == 'yes',
            'enums': enums
        }
        
        if condition_dict:
            constraint['conditions'] = condition_dict
            
        constraints.append(constraint)
    
    return constraints


def organize_constraints(all_constraints):
    """Organize constraints into a hierarchical structure by document type."""
    organized = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    
    for constraint in all_constraints:
        element = constraint['element']
        attribute = constraint['attribute']
        namespace = constraint['namespace']
        document_type = constraint['document_type']
        
        # Create a key for grouping
        if constraint.get('conditions'):
            # This is a conditional constraint (e.g., prop with name='type')
            cond_str = ', '.join(f"{k}={v}" for k, v in constraint['conditions'].items())
            if attribute:
                key = f"{element}[@{attribute}] where {cond_str}"
            else:
                key = f"{element} where {cond_str}"
        else:
            # This is a simple constraint
            if attribute:
                key = f"{element}[@{attribute}]"
            else:
                # Field value constraint (no attribute)
                key = element
        
        organized[namespace][document_type][element][key].append(constraint)
    
    return organized


def generate_yaml_output(organized_constraints):
    """Generate YAML representation of the OSCAL namespace."""
    output = {
        'oscal_namespace': {
            'version': '1.2.2',
            'description': 'OSCAL default namespace vocabulary extracted from metaschemas',
            'namespaces': {}
        }
    }
    
    for namespace, document_types in sorted(organized_constraints.items()):
        ns_data = {}
        
        for document_type, elements in sorted(document_types.items()):
            doc_data = {}
            
            for element, constraints_by_key in sorted(elements.items()):
                element_data = {}
                
                for key, constraints in sorted(constraints_by_key.items()):
                    # Merge constraints with the same key
                    merged_enums = []
                    seen_values = set()
                    allow_other = False
                    constraint_ids = []
                    files = set()
                    
                    for constraint in constraints:
                        # Deduplicate enums by value
                        for enum in constraint['enums']:
                            if enum['value'] not in seen_values:
                                merged_enums.append(enum)
                                seen_values.add(enum['value'])
                        allow_other = allow_other or constraint['allow_other']
                        constraint_ids.append(constraint['id'])
                        files.add(constraint['file'])
                    
                    constraint_data = {
                        'allowed_values': [e['value'] for e in merged_enums],
                        'allow_other': allow_other,
                        'definitions': merged_enums,
                        'constraint_ids': constraint_ids,
                        'source_files': sorted(list(files))
                    }
                    
                    # Add conditions if present
                    if constraints[0].get('conditions'):
                        constraint_data['conditions'] = constraints[0]['conditions']
                    
                    element_data[key] = constraint_data
                
                doc_data[element] = element_data
            
            ns_data[document_type] = doc_data
        
        output['oscal_namespace']['namespaces'][namespace] = ns_data
    
    return output


def main():
    """Main function to extract OSCAL namespace from metaschemas."""
    # Get the metaschemas directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    metaschemas_dir = project_root / 'release-metaschemas'
    
    if not metaschemas_dir.exists():
        print(f"Error: Metaschemas directory not found: {metaschemas_dir}")
        print("Please run 'make download-oscal' first.")
        sys.exit(1)
    
    # Find all metaschema files, excluding the complete metaschema to avoid duplication
    metaschema_files = [
        f for f in metaschemas_dir.glob('oscal_*_metaschema_RESOLVED.xml')
        if 'complete' not in f.name
    ]
    
    if not metaschema_files:
        print(f"Error: No metaschema files found in {metaschemas_dir}")
        sys.exit(1)
    
    print(f"Found {len(metaschema_files)} metaschema files (excluding complete)")
    
    # Parse all metaschemas
    all_constraints = []
    for metaschema_file in sorted(metaschema_files):
        print(f"Parsing {metaschema_file.name}...")
        constraints = parse_metaschema(metaschema_file)
        all_constraints.extend(constraints)
        print(f"  Found {len(constraints)} OSCAL namespace constraints")
    
    print(f"\nTotal constraints found: {len(all_constraints)}")
    
    # Organize constraints
    organized = organize_constraints(all_constraints)
    
    # Generate YAML output
    output = generate_yaml_output(organized)
    
    # Write to file
    output_file = project_root / NAMESPACE_YAML_PATH
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False, width=120)
    
    print(f"\nOSCAL namespace written to: {output_file}")
    
    # Print summary
    print("\nSummary:")
    for namespace, document_types in sorted(organized.items()):
        print(f"\n  Namespace: {namespace}")
        for document_type, elements in sorted(document_types.items()):
            print(f"    Document Type: {document_type}")
            for element in sorted(elements.keys()):
                constraint_count = sum(len(c) for c in elements[element].values())
                print(f"      {element}: {constraint_count} constraint(s)")


if __name__ == '__main__':
    main()

# Made with Bob
