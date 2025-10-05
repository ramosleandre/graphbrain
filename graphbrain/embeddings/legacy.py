"""
Legacy compatibility layer for old embeddings.py API.

This module provides backward compatibility for code using the old embeddings.py structure.
"""

from typing import List, Dict, Any, Optional
from graphbrain.hyperedge import Hyperedge
from graphbrain.embeddings.core import EdgeEmbedder, edge_to_text
from graphbrain.embeddings.stores.chroma import ChromaStore


class GraphbrainRAG:
    """
    Combined hypergraph + vector store for RAG applications (legacy compatibility).

    This is the original GraphbrainRAG from embeddings.py, kept for backward compatibility.
    New code should use graphbrain.rag.core.GraphbrainRAG instead.
    """

    def __init__(
        self,
        hg_locator: str,
        collection_name: str,
        embedder_provider: str = 'sentence-transformers',
        persist_directory: Optional[str] = None
    ):
        """
        Initialize RAG system.

        Args:
            hg_locator: Path to hypergraph database
            collection_name: ChromaDB collection name
            embedder_provider: Embedding provider
            persist_directory: Directory for ChromaDB persistence
        """
        from graphbrain.api import GraphbrainAPI

        self.api = GraphbrainAPI(hg_locator)
        self.embedder = EdgeEmbedder(provider=embedder_provider)
        self.vector_store = ChromaStore(collection_name, persist_directory)
        self.vector_store.set_embedder(self.embedder)

    def add_edge_with_embedding(
        self,
        connector: str,
        args: List[str],
        attrs: Optional[Dict[str, Any]] = None
    ) -> Hyperedge:
        """Add an edge to both hypergraph and vector store."""
        # Add to hypergraph
        edge = self.api.add_edge(connector, args, attrs)

        # Compute embedding and add to vector store
        embedding = self.embedder.embed_edge(edge)
        self.vector_store.add(edge, embedding, metadata=attrs)

        return edge

    def retrieve(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant edges for a query."""
        # Vector search
        vector_results = self.vector_store.search(query, k=k)

        # Enrich with hypergraph attributes
        enriched = []
        for edge, score, vector_metadata in vector_results:
            hg_attrs = self.api.get_attrs(edge)
            enriched.append({
                'edge': edge,
                'edge_str': edge.to_str(),
                'text': edge_to_text(edge),
                'score': score,
                'vector_metadata': vector_metadata,
                'hypergraph_attrs': hg_attrs
            })

        return enriched

    def validate_with_rag(
        self,
        proposed_action: str,
        rule_query: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """Validate a proposed action against rules using RAG."""
        # Retrieve relevant rules
        rules = self.retrieve(rule_query, k=k)

        # Simple check: look for keywords overlap
        action_lower = proposed_action.lower()
        violations = []

        for rule in rules:
            rule_text = rule['text'].lower()
            # Check if rule is relevant to action
            rule_words = set(rule_text.split())
            action_words = set(action_lower.split())
            overlap = rule_words & action_words

            if len(overlap) >= 2:  # Significant overlap
                violations.append({
                    'rule': rule['edge_str'],
                    'rule_text': rule['text'],
                    'score': rule['score'],
                    'matched_words': list(overlap),
                    'attrs': rule['hypergraph_attrs']
                })

        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'rules_checked': len(rules)
        }

    def close(self):
        """Close connections."""
        self.api.close()
