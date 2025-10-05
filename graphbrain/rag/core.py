"""
Core RAG functionality for Graphbrain.

Provides unified RAG interface combining hypergraph and vector search.
"""

from typing import List, Dict, Any, Optional, Union
from graphbrain.hyperedge import Hyperedge
from graphbrain.api import GraphbrainAPI
from graphbrain.embeddings.core import EdgeEmbedder, edge_to_text
from graphbrain.embeddings.stores.chroma import ChromaStore


def index_edges(
    api: GraphbrainAPI,
    embedder: EdgeEmbedder,
    vector_store,
    edge_pattern: Optional[str] = None,
    batch_size: int = 64
) -> int:
    """
    Index all edges from hypergraph into vector store.

    Args:
        api: GraphbrainAPI instance
        embedder: EdgeEmbedder instance
        vector_store: Vector store instance
        edge_pattern: Optional pattern to filter edges (default: all edges)
        batch_size: Batch size for embedding

    Returns:
        Number of edges indexed

    Example:
        >>> api = GraphbrainAPI('kb.db')
        >>> embedder = EdgeEmbedder()
        >>> store = ChromaStore('kb_vectors')
        >>> count = index_edges(api, embedder, store)
    """
    # Get edges to index
    if edge_pattern:
        edges = api.query(edge_pattern, limit=None)
    else:
        edges = api.all_edges(limit=None)

    if not edges:
        return 0

    # Batch embed and store
    total = 0
    for i in range(0, len(edges), batch_size):
        batch = edges[i:i + batch_size]

        # Get embeddings
        embeddings = embedder.embed_batch(batch, batch_size=batch_size)

        # Get metadatas
        metadatas = []
        for edge in batch:
            attrs = api.get_attrs(edge) or {}
            attrs['indexed'] = True
            metadatas.append(attrs)

        # Add to vector store
        vector_store.add_batch(batch, embeddings, metadatas)

        total += len(batch)

    return total


def retrieve_similar(
    embedder: EdgeEmbedder,
    vector_store,
    query: str,
    k: int = 5,
    with_text: bool = True
) -> List[Dict[str, Any]]:
    """
    Retrieve similar edges from vector store.

    Args:
        embedder: EdgeEmbedder instance
        vector_store: Vector store instance
        query: Query text
        k: Number of results
        with_text: Include natural language text in results

    Returns:
        List of result dicts with edge, score, metadata, text

    Example:
        >>> results = retrieve_similar(embedder, store, "diabetes medication", k=5)
    """
    # Search
    results = vector_store.search(query, k=k)

    # Format results
    formatted = []
    for edge, score, metadata in results:
        result = {
            'edge': edge,
            'edge_str': edge.to_str(),
            'score': score,
            'metadata': metadata
        }

        if with_text:
            result['text'] = edge_to_text(edge)

        formatted.append(result)

    return formatted


class GraphbrainRAG:
    """
    Unified RAG system combining hypergraph + vector store.

    This is the new, improved GraphbrainRAG with better separation of concerns.
    """

    def __init__(
        self,
        hg_locator: str,
        collection_name: str,
        embedder_provider: str = 'sentence-transformers',
        embedder_model: Optional[str] = None,
        persist_directory: Optional[str] = None,
        enable_cache: bool = True
    ):
        """
        Initialize RAG system.

        Args:
            hg_locator: Path to hypergraph database
            collection_name: Vector store collection name
            embedder_provider: Embedding provider ('sentence-transformers', 'vertex-ai', 'openai', 'mock')
            embedder_model: Optional model name
            persist_directory: Directory for vector store persistence
            enable_cache: Enable embedding caching
        """
        self.api = GraphbrainAPI(hg_locator)
        self.embedder = EdgeEmbedder(
            provider=embedder_provider,
            model=embedder_model,
            enable_cache=enable_cache
        )
        self.vector_store = ChromaStore(collection_name, persist_directory)
        self.vector_store.set_embedder(self.embedder)

    def add_edge_with_embedding(
        self,
        connector: str,
        args: List[str],
        attrs: Optional[Dict[str, Any]] = None
    ) -> Hyperedge:
        """
        Add an edge to both hypergraph and vector store.

        Args:
            connector: Relation connector
            args: Arguments
            attrs: Optional attributes

        Returns:
            Created hyperedge
        """
        # Add to hypergraph
        edge = self.api.add_edge(connector, args, attrs)

        # Compute embedding and add to vector store
        embedding = self.embedder.embed_edge(edge)
        self.vector_store.add(edge, embedding, metadata=attrs)

        return edge

    def index_all(self, edge_pattern: Optional[str] = None, batch_size: int = 64) -> int:
        """
        Index all edges from hypergraph into vector store.

        Args:
            edge_pattern: Optional pattern to filter edges
            batch_size: Batch size for embedding

        Returns:
            Number of edges indexed
        """
        return index_edges(
            self.api,
            self.embedder,
            self.vector_store,
            edge_pattern=edge_pattern,
            batch_size=batch_size
        )

    def retrieve(
        self,
        query: str,
        k: int = 5,
        with_hg_attrs: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant edges for a query.

        Args:
            query: Query text
            k: Number of results
            with_hg_attrs: Include hypergraph attributes

        Returns:
            List of results
        """
        # Vector search
        results = retrieve_similar(
            self.embedder,
            self.vector_store,
            query,
            k=k,
            with_text=True
        )

        # Optionally enrich with hypergraph attributes
        if with_hg_attrs:
            for result in results:
                hg_attrs = self.api.get_attrs(result['edge'])
                result['hypergraph_attrs'] = hg_attrs

        return results

    def validate_with_rag(
        self,
        proposed_action: str,
        rule_query: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Validate a proposed action against rules using RAG.

        Args:
            proposed_action: Action to validate (natural language)
            rule_query: Query to find relevant rules
            k: Number of rules to retrieve

        Returns:
            Validation result
        """
        # Retrieve relevant rules
        rules = self.retrieve(rule_query, k=k)

        # Simple keyword matching (future: use LLM)
        action_lower = proposed_action.lower()
        violations = []

        for rule in rules:
            rule_text = rule['text'].lower()
            rule_words = set(rule_text.split())
            action_words = set(action_lower.split())
            overlap = rule_words & action_words

            if len(overlap) >= 2:
                violations.append({
                    'rule': rule['edge_str'],
                    'rule_text': rule['text'],
                    'score': rule['score'],
                    'matched_words': list(overlap),
                    'attrs': rule.get('hypergraph_attrs', {})
                })

        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'rules_checked': len(rules)
        }

    def close(self):
        """Close all connections."""
        self.api.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()
