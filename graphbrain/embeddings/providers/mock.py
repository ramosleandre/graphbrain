"""Mock embedding provider for testing."""

import hashlib
from typing import List
from graphbrain.embeddings.providers.base import BaseEmbedder


class MockEmbedder(BaseEmbedder):
    """
    Mock embedder for testing (no external dependencies).

    Generates deterministic embeddings based on text hash.
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize mock embedder.

        Args:
            dimension: Embedding dimension (default: 384)
        """
        self._dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generate mock embedding for a single text."""
        # Use hash for deterministic embeddings
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)

        # Generate pseudo-random vector from hash
        embedding = []
        for i in range(self._dimension):
            # Simple pseudo-random based on hash and index
            val = ((hash_val + i * 7919) % 10000) / 10000.0 - 0.5
            embedding.append(val)

        # Normalize
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """Generate mock embeddings for multiple texts."""
        return [self.embed_text(text) for text in texts]

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    @property
    def name(self) -> str:
        """Return embedder name."""
        return "mock/deterministic"
