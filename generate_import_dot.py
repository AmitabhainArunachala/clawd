#!/usr/bin/env python3
"""
Generate a DOT graph file for visualization with Graphviz.
Usage: python3 generate_import_dot.py | dot -Tpng -o imports.png
"""

import json

def generate_dot():
    with open('/Users/dhyana/clawd/import_graph_analysis.json', 'r') as f:
        data = json.load(f)
    
    lines = ['digraph ImportGraph {']
    lines.append('    rankdir=TB;')
    lines.append('    node [shape=box, style=rounded];')
    lines.append('')
    
    # Define node styles by type
    lines.append('    // Node styles')
    lines.append('    node [color=blue, fillcolor=lightblue] // Internal modules')
    
    # Group nodes by package
    packages = {}
    for node in data['nodes']:
        node_id = node['id']
        if node['type'] == 'internal':
            pkg = node_id.split('.')[0] if '.' in node_id else node_id
            if pkg not in packages:
                packages[pkg] = []
            packages[pkg].append(node_id)
    
    # Add subgraphs for packages
    colors = {
        'skills': 'lightgreen',
        'oacp': 'lightyellow',
        'tests': 'lightpink',
        'scripts': 'lightgrey',
        'DHARMIC_GODEL_CLAW': 'lightcoral',
        'dgc': 'lightsalmon',
        'agno': 'plum',
        'dharmic': 'wheat',
        'unified': 'palegreen',
        'witness': 'mistyrose',
        'night': 'lavender'
    }
    
    for pkg, nodes in sorted(packages.items()):
        if len(nodes) > 1:
            lines.append(f'    subgraph cluster_{pkg} {{')
            lines.append(f'        label="{pkg}";')
            lines.append(f'        style=filled;')
            lines.append(f'        color={colors.get(pkg, "white")};')
            for node in sorted(nodes):
                safe_id = node.replace('.', '_').replace('-', '_')
                display = node.split('.')[-1] if '.' in node else node
                lines.append(f'        {safe_id} [label="{display}"];')
            lines.append('    }')
            lines.append('')
    
    # Add remaining internal nodes not in clusters
    for node in data['nodes']:
        if node['type'] == 'internal':
            pkg = node['id'].split('.')[0] if '.' in node['id'] else node['id']
            if pkg not in packages or len(packages.get(pkg, [])) <= 1:
                safe_id = node['id'].replace('.', '_').replace('-', '_')
                lines.append(f'    {safe_id} [label="{node["id"]}"];')
    
    lines.append('')
    
    # Add external nodes
    lines.append('    // External dependencies')
    lines.append('    node [color=red, fillcolor=pink, shape=ellipse];')
    external_added = set()
    for node in data['nodes']:
        if node['type'] == 'external':
            pkg = node['id'].split('.')[0]
            if pkg not in external_added:
                safe_id = pkg.replace('.', '_').replace('-', '_')
                lines.append(f'    {safe_id} [label="{pkg}"];')
                external_added.add(pkg)
    
    lines.append('')
    
    # Add edges (grouped by source package)
    lines.append('    // Internal dependencies')
    edges_by_source = {}
    for edge in data['edges']:
        source = edge['source']
        target = edge['target']
        source_pkg = source.split('.')[0] if '.' in source else source
        target_pkg = target.split('.')[0] if '.' in target else target
        
        # Only show internal-to-internal and internal-to-external
        source_internal = any(n['id'] == source and n['type'] == 'internal' for n in data['nodes'])
        
        if source_internal:
            if source not in edges_by_source:
                edges_by_source[source] = []
            edges_by_source[source].append((target, target_pkg))
    
    # Write edges
    for source, targets in sorted(edges_by_source.items()):
        source_id = source.replace('.', '_').replace('-', '_')
        seen_targets = set()
        for target, target_pkg in targets:
            if target in seen_targets:
                continue
            seen_targets.add(target)
            
            # Check if target is external
            is_external = any(n['id'] == target and n['type'] == 'external' for n in data['nodes'])
            
            if is_external:
                target_id = target_pkg.replace('.', '_').replace('-', '_')
                lines.append(f'    {source_id} -> {target_id} [color=red, style=dashed];')
            else:
                target_id = target.replace('.', '_').replace('-', '_')
                lines.append(f'    {source_id} -> {target_id};')
    
    lines.append('}')
    
    return '\n'.join(lines)

if __name__ == '__main__':
    print(generate_dot())
