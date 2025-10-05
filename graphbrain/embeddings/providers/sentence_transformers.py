"""Sentence Transformers embedding provider (local, free)."""

from typing import List
from graphbrain.embeddings.providers.base import BaseEmbedder


class SentenceTransformersEmbedder(BaseEmbedder):
    """
    Sentence Transformers embedding provider (local, no API key needed).

    Uses HuggingFace sentence-transformers models.
    """

    def __init__(self, model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize Sentence Transformers embedder.

        Args:
            model: Model name (default: 'all-MiniLM-L6-v2')
                   Other options: 'all-mpnet-base-v2', 'paraphrase-multilingual-MiniLM-L12-v2'
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "Sentence Transformers not available. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model
        self._client = SentenceTransformer(model)

    def embed_text(self, text: str) -> List[float]:
        """Compute embedding for a single text."""
        embedding = self._client.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """Compute embeddings for multiple texts."""
        embeddings = self._client.encode(
            texts,
            batch_size=batch_size,
            convert_to_tensor=False,
            show_progress_bar=len(texts) > 100
        )
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._client.get_sentence_embedding_dimension()

    @property
    def name(self) -> str:
        """Return embedder name."""
        return f"sentence-transformers/{self.model_name}"
