"""Bulk and convenience operations for GraphbrainAPI."""

from typing import List, Optional, Union
from graphbrain.hyperedge import Hyperedge


def quick_add(locator: str, connector: str, args: List[str], **attrs) -> Hyperedge:
    """
    Quickly add an edge to a graph (one-shot operation).

    Args:
        locator: Path to hypergraph
        connector: Relation
        args: Arguments
        **attrs: Attributes as keyword arguments

    Returns:
        Created hyperedge

    Example:
        >>> edge = quick_add('rules.db', 'contraindicated', ['diabetes', 'ibuprofen'],
        ...                  priority='high', category='medical')
    """
    from .core import GraphbrainAPI

    with GraphbrainAPI(locator) as api:
        return api.add_edge(connector, args, attrs=attrs or None)


def quick_query(locator: str, pattern: str, limit: Optional[int] = None) -> List[Hyperedge]:
    """
    Quickly query a graph (one-shot operation).

    Args:
        locator: Path to hypergraph
        pattern: Search pattern
        limit: Max results

    Returns:
        List of matching edges

    Example:
        >>> edges = quick_query('rules.db', '(contraindicated/* * *)')
    """
    from .core import GraphbrainAPI

    with GraphbrainAPI(locator) as api:
        return api.query(pattern, limit=limit)
