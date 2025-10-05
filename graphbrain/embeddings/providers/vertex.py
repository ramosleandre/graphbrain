"""Vertex AI embedding provider (Google Cloud)."""

from typing import List
from graphbrain.embeddings.providers.base import BaseEmbedder


class VertexAIEmbedder(BaseEmbedder):
    """
    Vertex AI Text Embeddings provider (Google Cloud).

    Requires: google-cloud-aiplatform
    """

    def __init__(self, model: str = 'text-embedding-004', project_id: str = None):
        """
        Initialize Vertex AI embedder.

        Args:
            model: Model name (default: 'text-embedding-004')
            project_id: GCP project ID (optional, uses default from env)
        """
        try:
            from vertexai.language_models import TextEmbeddingModel
            import vertexai
        except ImportError:
            raise ImportError(
                "Vertex AI not available. "
                "Install with: pip install google-cloud-aiplatform"
            )

        if project_id:
            vertexai.init(project=project_id)

        self.model_name = model
        self._model = TextEmbeddingModel.from_pretrained(model)

    def embed_text(self, text: str) -> List[float]:
        """Compute embedding for a single text."""
        embeddings = self._model.get_embeddings([text])
        return embeddings[0].values

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """Compute embeddings for multiple texts (Vertex AI handles batching internally)."""
        # Vertex AI can handle up to 250 texts per request
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self._model.get_embeddings(batch)
            all_embeddings.extend([emb.values for emb in embeddings])

        return all_embeddings

    @property
    def dimension(self) -> int:
        """Return embedding dimension (768 for text-embedding-004)."""
        return 768  # text-embedding-004

    @property
    def name(self) -> str:
        """Return embedder name."""
        return f"vertex-ai/{self.model_name}"
