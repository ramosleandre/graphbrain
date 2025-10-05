"""
Export hypergraphs to various visualization formats.

Supports: GraphML (yEd, Gephi), DOT (Graphviz), Cytoscape JSON
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from graphbrain.hyperedge import Hyperedge
from graphbrain.api import GraphbrainAPI


def to_graphml(
    api: GraphbrainAPI,
    output_path: str,
    edge_pattern: Optional[str] = None,
    color_by_layer: bool = True
) -> int:
    """
    Export hypergraph to GraphML format (compatible with yEd, Gephi).

    Args:
        api: GraphbrainAPI instance
        output_path: Path to output .graphml file
        edge_pattern: Optional pattern to filter edges
        color_by_layer: Color nodes by 'layer' attribute

    Returns:
        Number of edges exported

    Example:
        >>> api = GraphbrainAPI('kb.db')
        >>> count = to_graphml(api, 'graph.graphml', color_by_layer=True)
    """
    # Get edges
    if edge_pattern:
        edges = api.query(edge_pattern)
    else:
        edges = api.all_edges(limit=10000)

    # Color mapping
    layer_colors = {
        'foundation': '#FF6B6B',     # Red
        'user': '#4ECDC4',           # Teal
        'agent_rule': '#45B7D1',     # Blue
        'plan': '#FFA07A',           # Light orange
        'experimental': '#95E1D3',   # Light green
    }

    # Build graph
    nodes = {}
    graph_edges = []

    for edge in edges:
        attrs = api.get_attrs(edge) or {}
        layer = attrs.get('layer', 'default')
        color = layer_colors.get(layer, '#CCCCCC')

        # Add atoms as nodes
        for atom in edge.atoms():
            atom_str = str(atom)
            if atom_str not in nodes:
                nodes[atom_str] = {
                    'id': atom_str,
                    'label': atom.root() if hasattr(atom, 'root') else atom_str,
                    'color': color,
                    'layer': layer
                }

        # Add edge
        if len(edge) >= 2:
            connector = str(edge[0])
            for i in range(1, len(edge)):
                for j in range(i + 1, len(edge)):
                    source = str(edge[i])
                    target = str(edge[j])
                    graph_edges.append({
                        'source': source,
                        'target': target,
                        'label': connector,
                        'color': color
                    })

    # Write GraphML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\n')
        f.write('         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
        f.write('         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n')
        f.write('         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n')

        # Keys
        f.write('  <key id="label" for="node" attr.name="label" attr.type="string"/>\n')
        f.write('  <key id="color" for="node" attr.name="color" attr.type="string"/>\n')
        f.write('  <key id="layer" for="node" attr.name="layer" attr.type="string"/>\n')
        f.write('  <key id="edge_label" for="edge" attr.name="label" attr.type="string"/>\n')
        f.write('  <key id="edge_color" for="edge" attr.name="color" attr.type="string"/>\n')

        f.write('  <graph id="G" edgedefault="undirected">\n')

        # Nodes
        for node_id, node in nodes.items():
            f.write(f'    <node id="{_escape_xml(node_id)}">\n')
            f.write(f'      <data key="label">{_escape_xml(node["label"])}</data>\n')
            if color_by_layer:
                f.write(f'      <data key="color">{node["color"]}</data>\n')
            f.write(f'      <data key="layer">{node["layer"]}</data>\n')
            f.write('    </node>\n')

        # Edges
        edge_id = 0
        for edge in graph_edges:
            f.write(f'    <edge id="e{edge_id}" source="{_escape_xml(edge["source"])}" target="{_escape_xml(edge["target"])}">\n')
            f.write(f'      <data key="edge_label">{_escape_xml(edge["label"])}</data>\n')
            if color_by_layer:
                f.write(f'      <data key="edge_color">{edge["color"]}</data>\n')
            f.write('    </edge>\n')
            edge_id += 1

        f.write('  </graph>\n')
        f.write('</graphml>\n')

    return len(edges)


def to_dot(
    api: GraphbrainAPI,
    output_path: str,
    edge_pattern: Optional[str] = None,
    color_by_layer: bool = True
) -> int:
    """
    Export hypergraph to DOT format (Graphviz).

    Args:
        api: GraphbrainAPI instance
        output_path: Path to output .dot file
        edge_pattern: Optional pattern to filter edges
        color_by_layer: Color nodes by 'layer' attribute

    Returns:
        Number of edges exported

    Example:
        >>> api = GraphbrainAPI('kb.db')
        >>> count = to_dot(api, 'graph.dot')
        >>> # Then: dot -Tpng graph.dot -o graph.png
    """
    # Get edges
    if edge_pattern:
        edges = api.query(edge_pattern)
    else:
        edges = api.all_edges(limit=10000)

    # Color mapping
    layer_colors = {
        'foundation': 'red',
        'user': 'cyan',
        'agent_rule': 'blue',
        'plan': 'orange',
        'experimental': 'green',
    }

    # Build graph
    nodes = set()
    graph_edges = []

    for edge in edges:
        attrs = api.get_attrs(edge) or {}
        layer = attrs.get('layer', 'default')
        color = layer_colors.get(layer, 'gray')

        # Add atoms as nodes
        for atom in edge.atoms():
            nodes.add((str(atom), color))

        # Add edges
        if len(edge) >= 2:
            connector = str(edge[0])
            for i in range(1, len(edge)):
                for j in range(i + 1, len(edge)):
                    source = str(edge[i])
                    target = str(edge[j])
                    graph_edges.append((source, target, connector, color))

    # Write DOT
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('graph G {\n')
        f.write('  layout=fdp;\n')
        f.write('  overlap=false;\n')
        f.write('  splines=true;\n\n')

        # Nodes
        for node_id, color in nodes:
            safe_id = _safe_dot_id(node_id)
            label = node_id.split('/')[0] if '/' in node_id else node_id

            if color_by_layer:
                f.write(f'  "{safe_id}" [label="{label}", color={color}, style=filled, fillcolor={color}30];\n')
            else:
                f.write(f'  "{safe_id}" [label="{label}"];\n')

        f.write('\n')

        # Edges
        for source, target, label, color in graph_edges:
            safe_source = _safe_dot_id(source)
            safe_target = _safe_dot_id(target)

            if color_by_layer:
                f.write(f'  "{safe_source}" -- "{safe_target}" [label="{label}", color={color}];\n')
            else:
                f.write(f'  "{safe_source}" -- "{safe_target}" [label="{label}"];\n')

        f.write('}\n')

    return len(edges)


def to_cytoscape(
    api: GraphbrainAPI,
    edge_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """
    Export hypergraph to Cytoscape JSON format.

    Args:
        api: GraphbrainAPI instance
        edge_pattern: Optional pattern to filter edges

    Returns:
        Cytoscape-compatible dictionary

    Example:
        >>> api = GraphbrainAPI('kb.db')
        >>> cy_data = to_cytoscape(api)
        >>> import json
        >>> with open('graph.json', 'w') as f:
        ...     json.dump(cy_data, f)
    """
    # Get edges
    if edge_pattern:
        edges = api.query(edge_pattern)
    else:
        edges = api.all_edges(limit=10000)

    # Build graph
    nodes_dict = {}
    cy_edges = []

    edge_id = 0
    for edge in edges:
        attrs = api.get_attrs(edge) or {}

        # Add atoms as nodes
        for atom in edge.atoms():
            atom_str = str(atom)
            if atom_str not in nodes_dict:
                nodes_dict[atom_str] = {
                    'data': {
                        'id': atom_str,
                        'label': atom.root() if hasattr(atom, 'root') else atom_str,
                        'layer': attrs.get('layer', 'default')
                    }
                }

        # Add edges
        if len(edge) >= 2:
            connector = str(edge[0])
            for i in range(1, len(edge)):
                for j in range(i + 1, len(edge)):
                    source = str(edge[i])
                    target = str(edge[j])
                    cy_edges.append({
                        'data': {
                            'id': f'e{edge_id}',
                            'source': source,
                            'target': target,
                            'label': connector,
                            'layer': attrs.get('layer', 'default')
                        }
                    })
                    edge_id += 1

    # Format Cytoscape
    return {
        'elements': {
            'nodes': list(nodes_dict.values()),
            'edges': cy_edges
        }
    }


def _escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))


def _safe_dot_id(text: str) -> str:
    """Make text safe for DOT identifiers."""
    return text.replace('"', '\\"').replace('\n', ' ')
