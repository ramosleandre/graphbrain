"""ChromaDB vector store implementation."""

from typing import List, Dict, Any, Optional, Tuple, Union
from graphbrain.hyperedge import Hyperedge, hedge
from graphbrain.embeddings.stores.base import BaseVectorStore


class ChromaStore(BaseVectorStore):
    """
    ChromaDB vector store for hyperedges.

    Example:
        >>> store = ChromaStore('medical_rules')
        >>> store.add(edge, embedding, metadata={'category': 'contraindication'})
        >>> results = store.search("diabetes medication", k=5)
    """

    def __init__(
        self,
        collection_name: str,
        persist_directory: Optional[str] = None,
        embedder=None
    ):
        """
        Initialize ChromaDB store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory for persistent storage
            embedder: EdgeEmbedder instance (for query encoding)
        """
        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "ChromaDB not available. "
                "Install with: pip install chromadb"
            )

        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Graphbrain hyperedges"}
        )
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
        edge_id = edge.to_str()
        metadata = metadata or {}
        metadata['edge_str'] = edge_id

        self.collection.add(
            ids=[edge_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def add_batch(
        self,
        edges: List[Hyperedge],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """Add multiple edges efficiently."""
        ids = [edge.to_str() for edge in edges]
        if metadatas is None:
            metadatas = [{}] * len(edges)

        for i, edge in enumerate(edges):
            metadatas[i]['edge_str'] = edge.to_str()

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

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
        if isinstance(query, str):
            if self._embedder is None:
                raise ValueError("Embedder not set. Call set_embedder() first.")
            query_embedding = self._embedder.embed_text(query)
        else:
            query_embedding = query

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        output = []
        for i, edge_str in enumerate(results['ids'][0]):
            edge = hedge(edge_str)
            score = results['distances'][0][i]
            metadata = results['metadatas'][0][i]
            output.append((edge, score, metadata))

        return output

    def delete(self, edge: Hyperedge):
        """Delete an edge from the store."""
        self.collection.delete(ids=[edge.to_str()])

    def count(self) -> int:
        """Get number of edges in the store."""
        return self.collection.count()
