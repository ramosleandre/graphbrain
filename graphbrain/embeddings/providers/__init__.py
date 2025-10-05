"""Embedding providers for Graphbrain."""

from graphbrain.embeddings.providers.base import BaseEmbedder
from graphbrain.embeddings.providers.sentence_transformers import SentenceTransformersEmbedder

# Optional providers
try:
    from graphbrain.embeddings.providers.vertex import VertexAIEmbedder
except ImportError:
    VertexAIEmbedder = None

try:
    from graphbrain.embeddings.providers.openai import OpenAIEmbedder
except ImportError:
    OpenAIEmbedder = None

from graphbrain.embeddings.providers.mock import MockEmbedder

__all__ = [
    'BaseEmbedder',
    'SentenceTransformersEmbedder',
    'VertexAIEmbedder',
    'OpenAIEmbedder',
    'MockEmbedder'
]
