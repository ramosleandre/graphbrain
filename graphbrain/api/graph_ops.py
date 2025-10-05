"""Graph operations and utilities."""

from typing import Dict, List, Optional, Union, Any
from graphbrain import hedge
from graphbrain.hyperedge import Hyperedge
from .utils import sanitize_pattern


def search_with_reasoning(
    api,
    query: Union[str, Hyperedge],
    hops: int = 2,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Multi-hop reasoning search (BFS on patterns)."""
    if isinstance(query, str):
        query = hedge(sanitize_pattern(query))

    visited = set()
    results = []
    queue = [(query, 0, [query])]

    while queue and len(results) < limit:
        current, dist, path = queue.pop(0)

        if current.to_str() in visited:
            continue

        visited.add(current.to_str())

        results.append({
            "edge": current,
            "edge_str": current.to_str(),
            "distance": dist,
            "path": [e.to_str() if isinstance(e, Hyperedge) else str(e) for e in path],
            "attrs": api.get_attrs(current)
        })

        if dist < hops:
            atoms = current.atoms()
            for atom in atoms:
                try:
                    atom_str = str(atom)
                    related = api.query(f"(* {atom_str} *)", limit=20, sanitize=False)
                    for rel_edge in related:
                        if rel_edge.to_str() not in visited:
                            queue.append((rel_edge, dist + 1, path + [rel_edge]))
                except:
                    continue

    return results[:limit]


def find_neighbors(
    api,
    node: Union[str, Hyperedge],
    max_degree: int = 2,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Find neighboring edges (connected by shared atoms)."""
    if isinstance(node, str):
        node = hedge(f"({node})" if not node.startswith('(') else node)

    visited = set()
    results = []
    queue = [(node, 0)]

    while queue and len(results) < limit:
        current, dist = queue.pop(0)
        current_str = current.to_str()

        if current_str in visited:
            continue

        visited.add(current_str)

        results.append({
            "edge": current,
            "edge_str": current_str,
            "distance": dist,
            "attrs": api.get_attrs(current)
        })

        if dist < max_degree:
            for atom in current.atoms():
                try:
                    pattern = f"(* {str(atom)} *)"
                    connected = api.query(pattern, limit=20, sanitize=False)
                    for edge in connected:
                        if edge.to_str() not in visited:
                            queue.append((edge, dist + 1))
                except:
                    continue

    return results[:limit]


def edges_by_connector(api, connector: str, limit: Optional[int] = None) -> List[Hyperedge]:
    """Find all edges with a specific connector."""
    # Add /P if not already typed
    if '/' not in connector:
        connector = f"{connector}/P"
    pattern = f"({connector} * *)"
    return api.query(pattern, limit=limit)


def atoms_by_prefix(api, prefix: str, limit: int = 100) -> List[str]:
    """Find atoms matching a prefix pattern."""
    pattern = f"(* {prefix} *)"
    edges = api.query(pattern, limit=limit, sanitize=False)

    atoms_set = set()
    for edge in edges:
        for atom in edge.atoms():
            atom_str = str(atom)
            if prefix.endswith('*'):
                prefix_clean = prefix[:-1]
                if atom_str.startswith(prefix_clean):
                    atoms_set.add(atom_str)
            else:
                if atom_str == prefix:
                    atoms_set.add(atom_str)

    return list(atoms_set)[:limit]


def plan_to_edges(steps: List[str], user: str = "user") -> List[Dict[str, Any]]:
    """Convert plan steps (natural language) to hyperedge dictionaries."""
    edges = []

    verb_mapping = {
        "prendre": "prend",
        "marcher": "fait",
        "prend": "prend",
        "take": "take",
        "walk": "walk",
        "prescribe": "prescribe",
    }

    for step in steps:
        step_lower = step.lower().strip()

        words = step_lower.split()
        if not words:
            continue

        verb = words[0]
        obj = "-".join(words[1:]) if len(words) > 1 else "action"

        connector = verb_mapping.get(verb, verb)

        edge_str = f"({connector}/P {user}/C {obj}/C)"

        edges.append({
            "s": edge_str,
            "attrs": {
                "layer": "plan",
                "original_text": step
            }
        })

    return edges
