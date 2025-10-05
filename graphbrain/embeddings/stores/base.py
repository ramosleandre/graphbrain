"""Base class for vector stores."""

from typing import List, Dict, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod
from graphbrain.hyperedge import Hyperedge


class BaseVectorStore(ABC):
    """Base interface for vector storage backends."""

    @abstractmethod
    def add(
        self,
        edge: Hyperedge,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add an edge and its embedding to the store.

        Args:
            edge: Hyperedge to store
            embedding: Embedding vector
            metadata: Optional metadata
        """
        pass

    @abstractmethod
    def add_batch(
        self,
        edges: List[Hyperedge],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Add multiple edges efficiently.

        Args:
            edges: List of hyperedges
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
        """
        pass

    @abstractmethod
    def search(
        self,
        query: Union[str, List[float]],
        k: int = 5
    ) -> List[Tuple[Hyperedge, float, Dict[str, Any]]]:
        """
        Search for similar edges.

        Args:
            query: Query text or embedding vector
            k: Number of results

        Returns:
            List of (edge, score, metadata) tuples
        """
        pass

    @abstractmethod
    def delete(self, edge: Hyperedge):
        """
        Delete an edge from the store.

        Args:
            edge: Hyperedge to delete
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get number of edges in the store.

        Returns:
            Number of stored edges
        """
        pass
