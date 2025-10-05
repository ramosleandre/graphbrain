"""BigQuery Vector Search store implementation (stub for future)."""

from typing import List, Dict, Any, Optional, Tuple, Union
from graphbrain.hyperedge import Hyperedge
from graphbrain.embeddings.stores.base import BaseVectorStore


class BigQueryStore(BaseVectorStore):
    """
    BigQuery Vector Search store (stub implementation).

    This is a placeholder for future BigQuery vector search integration.
    Requires: google-cloud-bigquery
    """

    def __init__(
        self,
        project_id: str,
        dataset: str,
        table: str,
        embedder=None
    ):
        """
        Initialize BigQuery vector store.

        Args:
            project_id: GCP project ID
            dataset: BigQuery dataset name
            table: BigQuery table name
            embedder: EdgeEmbedder instance

        Raises:
            NotImplementedError: This is a stub for future implementation
        """
        self.project_id = project_id
        self.dataset = dataset
        self.table = table
        self._embedder = embedder

        # TODO: Initialize BigQuery client when implementing
        raise NotImplementedError(
            "BigQueryStore is not yet implemented. "
            "Use ChromaStore or MemoryStore for now."
        )

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
        raise NotImplementedError("BigQueryStore not yet implemented")

    def add_batch(
        self,
        edges: List[Hyperedge],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """Add multiple edges efficiently."""
        raise NotImplementedError("BigQueryStore not yet implemented")

    def search(
        self,
        query: Union[str, List[float]],
        k: int = 5
    ) -> List[Tuple[Hyperedge, float, Dict[str, Any]]]:
        """Search for similar edges."""
        raise NotImplementedError("BigQueryStore not yet implemented")

    def delete(self, edge: Hyperedge):
        """Delete an edge from the store."""
        raise NotImplementedError("BigQueryStore not yet implemented")

    def count(self) -> int:
        """Get number of edges in the store."""
        raise NotImplementedError("BigQueryStore not yet implemented")
