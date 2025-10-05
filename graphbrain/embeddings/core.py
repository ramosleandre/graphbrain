"""
Core embeddings functionality for Graphbrain.

Provides unified EdgeEmbedder that wraps different providers
and utilities for edge-to-text conversion.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Union, Optional
from graphbrain.hyperedge import Hyperedge, hedge


def edge_to_text(edge: Hyperedge) -> str:
    """
    Convert a hyperedge to natural language text for embedding.

    Args:
        edge: Hyperedge to convert

    Returns:
        Text representation of the edge

    Example:
        >>> edge = hedge("(is/Pd graphbrain/C awesome/C)")
        >>> edge_to_text(edge)
        "graphbrain is awesome"
    """
    if edge.atom:
        # For atoms, return the concept without type
        return edge.root()

    # For non-atoms, extract relation and arguments
    connector = str(edge[0].root()) if edge[0].atom else str(edge[0])
    args = [edge_to_text(arg) if isinstance(arg, Hyperedge) else str(arg)
            for arg in edge[1:]]

    # Format as natural sentence
    if connector in ['is', 'are']:
        return f"{args[0]} {connector} {' '.join(args[1:])}"
    elif connector in ['has', 'have']:
        return f"{args[0]} {connector} {' '.join(args[1:])}"
    elif connector in ['contraindicated', 'contreindique']:
        return f"{args[0]} contraindicated for {' '.join(args[1:])}"
    elif connector in ['recommande', 'recommend']:
        return f"{args[0]} recommended for {' '.join(args[1:])}"
    else:
        # Generic format
        return f"{connector} {' '.join(args)}"


class EdgeEmbedder:
    """
    Unified embedder for hyperedges with caching support.

    Wraps different embedding providers and provides caching.
    """

    def __init__(
        self,
        provider: str = 'sentence-transformers',
        model: Optional[str] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        enable_cache: bool = True,
        **kwargs
    ):
        """
        Initialize edge embedder.

        Args:
            provider: 'sentence-transformers', 'vertex-ai', 'openai', 'mock'
            model: Model name (provider-specific, optional)
            cache_dir: Directory for caching embeddings
            enable_cache: Enable file-based caching
            **kwargs: Additional provider-specific arguments
        """
        self.provider_name = provider.lower()
        self.enable_cache = enable_cache

        # Setup cache
        if enable_cache:
            if cache_dir is None:
                cache_dir = Path.home() / ".cache" / "graphbrain" / "embeddings"
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

        # Initialize provider
        self._embedder = self._create_provider(provider, model, **kwargs)

    def _create_provider(self, provider: str, model: Optional[str], **kwargs):
        """Create the appropriate provider instance."""
        if provider == 'sentence-transformers':
            from graphbrain.embeddings.providers.sentence_transformers import SentenceTransformersEmbedder
            return SentenceTransformersEmbedder(model=model or 'all-MiniLM-L6-v2')

        elif provider == 'vertex-ai':
            from graphbrain.embeddings.providers.vertex import VertexAIEmbedder
            return VertexAIEmbedder(model=model or 'text-embedding-004', **kwargs)

        elif provider == 'openai':
            from graphbrain.embeddings.providers.openai import OpenAIEmbedder
            return OpenAIEmbedder(model=model or 'text-embedding-3-small', **kwargs)

        elif provider == 'mock':
            from graphbrain.embeddings.providers.mock import MockEmbedder
            return MockEmbedder(dimension=int(kwargs.get('dimension', 384)))

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        content = f"{self._embedder.name}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """Load embedding from cache if exists."""
        if not self.enable_cache or not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return data['embedding']
            except:
                return None
        return None

    def _save_to_cache(self, cache_key: str, embedding: List[float]):
        """Save embedding to cache."""
        if not self.enable_cache or not self.cache_dir:
            return

        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'embedding': embedding,
                    'provider': self._embedder.name
                }, f)
        except:
            pass  # Fail silently on cache errors

    def embed_text(self, text: str) -> List[float]:
        """
        Compute embedding for text (with caching).

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Try cache first
        cache_key = self._get_cache_key(text)
        cached = self._load_from_cache(cache_key)
        if cached is not None:
            return cached

        # Compute embedding
        embedding = self._embedder.embed_text(text)

        # Save to cache
        self._save_to_cache(cache_key, embedding)

        return embedding

    def embed_edge(self, edge: Union[str, Hyperedge]) -> List[float]:
        """
        Compute embedding for a hyperedge.

        Args:
            edge: Hyperedge (as object or string)

        Returns:
            Embedding vector
        """
        if isinstance(edge, str):
            edge = hedge(edge)

        text = edge_to_text(edge)
        return self.embed_text(text)

    def embed_batch(
        self,
        edges: List[Union[str, Hyperedge]],
        batch_size: int = 64
    ) -> List[List[float]]:
        """
        Compute embeddings for multiple edges efficiently.

        Args:
            edges: List of hyperedges
            batch_size: Batch size for provider

        Returns:
            List of embedding vectors
        """
        # Convert edges to text
        texts = []
        for edge in edges:
            if isinstance(edge, str):
                edge = hedge(edge)
            texts.append(edge_to_text(edge))

        # Check cache for all texts
        embeddings = []
        uncached_indices = []
        uncached_texts = []

        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            cached = self._load_from_cache(cache_key)
            if cached is not None:
                embeddings.append(cached)
            else:
                embeddings.append(None)  # Placeholder
                uncached_indices.append(i)
                uncached_texts.append(text)

        # Compute uncached embeddings in batch
        if uncached_texts:
            new_embeddings = self._embedder.embed_batch(uncached_texts, batch_size)

            # Fill in results and cache
            for idx, embedding in zip(uncached_indices, new_embeddings):
                embeddings[idx] = embedding
                cache_key = self._get_cache_key(texts[idx])
                self._save_to_cache(cache_key, embedding)

        return embeddings

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._embedder.dimension

    @property
    def name(self) -> str:
        """Return embedder name."""
        return self._embedder.name
