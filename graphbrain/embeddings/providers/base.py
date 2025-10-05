"""Base class for embedding providers."""

from typing import List
from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    """Base class for all embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Compute embedding for a text string.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """
        Compute embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the embedder name."""
        pass
