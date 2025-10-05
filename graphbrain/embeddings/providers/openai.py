"""OpenAI embedding provider."""

from typing import List
from graphbrain.embeddings.providers.base import BaseEmbedder


class OpenAIEmbedder(BaseEmbedder):
    """
    OpenAI Embeddings provider.

    Requires: openai
    """

    def __init__(self, model: str = 'text-embedding-3-small', api_key: str = None):
        """
        Initialize OpenAI embedder.

        Args:
            model: Model name (default: 'text-embedding-3-small')
                   Options: 'text-embedding-3-small', 'text-embedding-3-large'
            api_key: OpenAI API key (optional, uses OPENAI_API_KEY env var)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI not available. "
                "Install with: pip install openai"
            )

        self.model_name = model
        self._client = OpenAI(api_key=api_key)

        # Dimension mapping
        self._dimensions = {
            'text-embedding-3-small': 1536,
            'text-embedding-3-large': 3072,
            'text-embedding-ada-002': 1536
        }

    def embed_text(self, text: str) -> List[float]:
        """Compute embedding for a single text."""
        response = self._client.embeddings.create(
            input=text,
            model=self.model_name
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """Compute embeddings for multiple texts."""
        # OpenAI can handle batches (up to 2048 input items)
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self._client.embeddings.create(
                input=batch,
                model=self.model_name
            )
            all_embeddings.extend([item.embedding for item in response.data])

        return all_embeddings

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimensions.get(self.model_name, 1536)

    @property
    def name(self) -> str:
        """Return embedder name."""
        return f"openai/{self.model_name}"
