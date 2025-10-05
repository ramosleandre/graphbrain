"""Core GraphbrainAPI implementation."""

import logging
from typing import Dict, List, Optional, Any, Union, Literal
from graphbrain import hgraph, hedge
from graphbrain.hyperedge import Hyperedge

from .exceptions import StoreError, GraphPatternError
from .utils import (
    _ensure_typed_pred,
    _ensure_typed_concept,
    _normalize_triplet,
    sanitize_pattern
)
from .validation import validate_edges_against_rules
from .foundation import load_foundation_pack_file
from .graph_ops import (
    search_with_reasoning,
    find_neighbors,
    edges_by_connector,
    atoms_by_prefix,
    plan_to_edges
)

logger = logging.getLogger(__name__)


class GraphbrainAPI:
    """
    High-level API wrapper for LLM integration.

    Example:
        >>> api = GraphbrainAPI('my_graph.db')
        >>> api.add_edge('is', ['graphbrain', 'awesome'])
        >>> results = api.query('(is/* * *)')
        >>> api.close()
    """

    def __init__(self, locator_string: str):
        """
        Initialize the API with a hypergraph.

        Args:
            locator_string: Path to the hypergraph database.
                          Use .db extension for SQLite, .hg for LevelDB.
        """
        try:
            self.hg = hgraph(locator_string)
        except Exception as e:
            raise StoreError(f"Failed to open hypergraph at {locator_string}: {e}")

        self.locator = locator_string
        self._active_layers = set()

    def add_edge(
        self,
        connector: str,
        args: List[Union[str, Hyperedge]],
        attrs: Optional[Dict[str, Any]] = None,
        auto_type: bool = True
    ) -> Hyperedge:
        """
        Add a hyperedge to the graph.

        Args:
            connector: The connector/relation (e.g., 'is', 'has', 'can')
            args: List of arguments (concepts or other edges)
            attrs: Optional attributes dictionary
            auto_type: Automatically add /P and /C types (default: True)

        Returns:
            The created hyperedge
        """
        if attrs is None:
            attrs = {}

        if auto_type:
            connector = _ensure_typed_pred(connector)

        formatted_args = []
        for arg in args:
            if isinstance(arg, str):
                if auto_type:
                    arg = _ensure_typed_concept(arg)
                formatted_args.append(arg)
            elif isinstance(arg, Hyperedge):
                formatted_args.append(arg.to_str())
            else:
                formatted_args.append(str(arg))

        edge_str = f"({connector} {' '.join(formatted_args)})"
        edge = hedge(edge_str)

        if attrs:
            self.hg.add(edge, primary=True)
            for key, value in attrs.items():
                self.hg.set_attribute(edge, key, str(value))
        else:
            self.hg.add(edge, primary=True)

        return edge

    def add_edge_from_string(
        self,
        edge_str: str,
        attrs: Optional[Dict[str, Any]] = None
    ) -> Hyperedge:
        """Add a hyperedge from its string representation."""
        edge = hedge(edge_str)
        self.hg.add(edge, primary=True)
        if attrs:
            for key, value in attrs.items():
                self.hg.set_attribute(edge, key, str(value))
        return edge

    def query(
        self,
        pattern: Union[str, Hyperedge],
        limit: Optional[int] = None,
        sanitize: bool = True
    ) -> List[Hyperedge]:
        """
        Search for hyperedges matching a pattern.

        Args:
            pattern: Search pattern in SH notation (e.g., "(is/* * *)")
            limit: Maximum number of results to return
            sanitize: Whether to sanitize the pattern (default: True)

        Returns:
            List of matching hyperedges
        """
        if isinstance(pattern, str):
            if sanitize:
                pattern = sanitize_pattern(pattern)
            pattern = hedge(pattern)

        try:
            results = list(self.hg.search(pattern))
        except Exception as e:
            raise StoreError(f"Query failed: {e}")

        if limit:
            return results[:limit]
        return results

    def set_attrs(self, edge: Union[str, Hyperedge], attrs: Dict[str, Any]) -> None:
        """Set attributes for a hyperedge."""
        if isinstance(edge, str):
            edge = hedge(edge)
        for key, value in attrs.items():
            self.hg.set_attribute(edge, key, str(value))

    def get_attrs(self, edge: Union[str, Hyperedge]) -> Optional[Dict[str, Any]]:
        """Get attributes of a hyperedge."""
        if isinstance(edge, str):
            edge = hedge(edge)
        return self.hg.get_attributes(edge)

    def exists(self, edge: Union[str, Hyperedge]) -> bool:
        """Check if a hyperedge exists in the graph."""
        if isinstance(edge, str):
            edge = hedge(edge)
        return self.hg.exists(edge)

    def remove(self, edge: Union[str, Hyperedge]) -> None:
        """Remove a hyperedge from the graph."""
        if isinstance(edge, str):
            edge = hedge(edge)
        self.hg.remove(edge, deep=True)

    def add_fact(
        self,
        subject: str,
        predicate: str,
        object_: str,
        attrs: Optional[Dict[str, Any]] = None
    ) -> Hyperedge:
        """
        Add a simple fact (subject-predicate-object) to the graph.

        Example:
            >>> api.add_fact('ibuprofen', 'contraindicated', 'diabetes')
            (contraindicated/P ibuprofen/C diabetes/C)
        """
        s, p, o = _normalize_triplet(subject, predicate, object_)
        edge = hedge(f'({p} {s} {o})')
        self.hg.add(edge, primary=True)

        if attrs:
            for key, value in attrs.items():
                self.hg.set_attribute(edge, key, str(value))

        return edge

    def add_rule(
        self,
        rule_text: str,
        attrs: Optional[Dict[str, Any]] = None
    ) -> Hyperedge:
        """Add a rule to the graph from natural language text."""
        return self.add_edge_from_string(rule_text, attrs)

    def validate_against_rules(
        self,
        proposed_edges: Union[str, Hyperedge, List[Union[str, Hyperedge]]],
        rule_pattern: Optional[str] = None,
        strategy: Literal["tri_state", "simple"] = "tri_state",
        layers: Optional[List[str]] = None,
        confidence_min: float = 0.0
    ) -> Dict[str, Any]:
        """
        Validate proposed edge(s) against rules with tri-state logic.

        Args:
            proposed_edges: Edge(s) to validate
            rule_pattern: Pattern to match rules
            strategy: "tri_state" or "simple"
            layers: Filter rules by layers
            confidence_min: Minimum confidence threshold

        Returns:
            ValidationReport dict
        """
        return validate_edges_against_rules(
            self, proposed_edges, rule_pattern, strategy, layers, confidence_min
        )

    def all_edges(self, limit: Optional[int] = None) -> List[Hyperedge]:
        """Get all edges in the graph."""
        edges = list(self.hg.all())
        if limit:
            return edges[:limit]
        return edges

    def count(self) -> int:
        """Count total number of edges in the graph."""
        return len(list(self.hg.all()))

    def bulk_add(self, edges: List[Dict[str, Any]], upsert: bool = True) -> Dict[str, Any]:
        """
        Add multiple edges efficiently with upsert support.

        Args:
            edges: List of edge dictionaries
            upsert: If True, update existing edges

        Returns:
            BulkResult dict
        """
        inserted = 0
        updated = 0
        skipped = 0
        errors = []

        for edge_dict in edges:
            try:
                edge_str = edge_dict.get("s")
                attrs = edge_dict.get("attrs", {})

                if not edge_str:
                    errors.append({"edge": edge_dict, "error": "Missing 's' field"})
                    continue

                edge = hedge(edge_str)
                exists = self.hg.exists(edge)

                if exists and not upsert:
                    skipped += 1
                    continue

                self.hg.add(edge, primary=True)

                if attrs:
                    for key, value in attrs.items():
                        self.hg.set_attribute(edge, key, str(value))

                if exists:
                    updated += 1
                else:
                    inserted += 1

            except Exception as e:
                errors.append({"edge": edge_dict, "error": str(e)})
                logger.error(f"Error adding edge {edge_dict}: {e}")

        return {
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "errors": errors
        }

    def toggle_layer(self, layer: str, enabled: bool) -> None:
        """Enable or disable a layer for filtering."""
        if enabled:
            self._active_layers.add(layer)
            logger.info(f"Layer '{layer}' enabled")
        else:
            self._active_layers.discard(layer)
            logger.info(f"Layer '{layer}' disabled")

    def get_active_layers(self) -> set:
        """Get the set of currently active layers."""
        return self._active_layers.copy()

    def add_user_fact(
        self,
        text: str,
        attrs: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Hyperedge:
        """Add a simple user fact from natural language."""
        concept = text.lower().strip().replace(" ", "-")

        attrs = attrs or {}
        attrs["layer"] = "user"
        if session_id:
            attrs["session_id"] = session_id

        return self.add_edge("a", ["user", concept], attrs=attrs)

    def plan_to_edges(self, steps: List[str], user: str = "user") -> List[Dict[str, Any]]:
        """Convert plan steps to hyperedge dictionaries."""
        return plan_to_edges(steps, user)

    def search_with_reasoning(
        self,
        query: Union[str, Hyperedge],
        hops: int = 2,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Multi-hop reasoning search (BFS on patterns)."""
        return search_with_reasoning(self, query, hops, limit)

    def load_foundation_pack(self, filepath: str, format: str = "auto") -> Dict[str, Any]:
        """Load a foundation pack from YAML or JSON file."""
        return load_foundation_pack_file(self, filepath, format)

    def neighbors(
        self,
        node: Union[str, Hyperedge],
        max_degree: int = 2,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find neighboring edges (connected by shared atoms)."""
        return find_neighbors(self, node, max_degree, limit)

    def edges_by_connector(
        self,
        connector: str,
        limit: Optional[int] = None
    ) -> List[Hyperedge]:
        """Find all edges with a specific connector."""
        return edges_by_connector(self, connector, limit)

    def atoms_by_prefix(self, prefix: str, limit: int = 100) -> List[str]:
        """Find atoms matching a prefix pattern."""
        return atoms_by_prefix(self, prefix, limit)

    def close(self):
        """Close the hypergraph connection."""
        self.hg.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()


def create_api(locator_string: str) -> GraphbrainAPI:
    """Create a GraphbrainAPI instance."""
    return GraphbrainAPI(locator_string)
