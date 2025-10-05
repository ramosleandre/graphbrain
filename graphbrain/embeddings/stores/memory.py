"""In-memory vector store implementation (for testing/small datasets)."""

from typing import List, Dict, Any, Optional, Tuple, Union
from graphbrain.hyperedge import Hyperedge
from graphbrain.embeddings.stores.base import BaseVectorStore
import numpy as np


class MemoryStore(BaseVectorStore):
    """
    In-memory vector store (no persistence).

    Useful for testing and small datasets.
    Uses simple cosine similarity for search.
    """

    def __init__(self, embedder=None):
        """
        Initialize memory store.

        Args:
            embedder: EdgeEmbedder instance (for query encoding)
        """
        self._edges = []
        self._embeddings = []
        self._metadatas = []
        self._embedder = embedder

    def set_embedder(self, embedder):
        """Set the embedder for query encoding."""
        self._embedder = embedder

    def add(
        self,
        edge: Hyperedge,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add an edge with its embedding."""
        # Check if edge already exists
        edge_str = edge.to_str()
        for i, existing_edge in enumerate(self._edges):
            if existing_edge.to_str() == edge_str:
                # Update existing
                self._embeddings[i] = embedding
                self._metadatas[i] = metadata or {}
                return

        # Add new
        self._edges.append(edge)
        self._embeddings.append(embedding)
        self._metadatas.append(metadata or {})

    def add_batch(
        self,
        edges: List[Hyperedge],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """Add multiple edges."""
        if metadatas is None:
            metadatas = [{}] * len(edges)

        for edge, embedding, metadata in zip(edges, embeddings, metadatas):
            self.add(edge, embedding, metadata)

    def search(
        self,
        query: Union[str, List[float]],
        k: int = 5
    ) -> List[Tuple[Hyperedge, float, Dict[str, Any]]]:
        """
        Search for similar edges using cosine similarity.

        Args:
            query: Query text or embedding vector
            k: Number of results

        Returns:
            List of (edge, score, metadata) tuples
        """
        if isinstance(query, str):
            if self._embedder is None:
                raise ValueError("Embedder not set. Call set_embedder() first.")
            query_embedding = self._embedder.embed_text(query)
        else:
            query_embedding = query

        if not self._embeddings:
            return []

        # Compute cosine similarities
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)

        similarities = []
        for i, emb in enumerate(self._embeddings):
            emb_vec = np.array(emb)
            emb_norm = np.linalg.norm(emb_vec)

            if emb_norm > 0 and query_norm > 0:
                sim = np.dot(query_vec, emb_vec) / (query_norm * emb_norm)
            else:
                sim = 0.0

            similarities.append((i, sim))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top k
        results = []
        for idx, score in similarities[:k]:
            results.append((
                self._edges[idx],
                1.0 - score,  # Convert to distance
                self._metadatas[idx]
            ))

        return results

    def delete(self, edge: Hyperedge):
        """Delete an edge from the store."""
        edge_str = edge.to_str()
        for i, existing_edge in enumerate(self._edges):
            if existing_edge.to_str() == edge_str:
                del self._edges[i]
                del self._embeddings[i]
                del self._metadatas[i]
                return

    def count(self) -> int:
        """Get number of edges in the store."""
        return len(self._edges)
