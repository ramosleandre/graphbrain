"""
Embeddings and vector search integration for Graphbrain.

This module provides functionality to compute embeddings for hyperedges
and integrate with vector databases for semantic search.

Refactored structure:
- providers/: Embedding providers (Vertex AI, OpenAI, Sentence Transformers, Mock)
- stores/: Vector stores (ChromaDB, BigQuery, Memory)
- core.py: Unified EdgeEmbedder and utilities
"""

from graphbrain.embeddings.core import EdgeEmbedder, edge_to_text
from graphbrain.embeddings.stores.chroma import ChromaStore
from graphbrain.embeddings.stores.memory import MemoryStore

# Backward compatibility: import old GraphbrainRAG if needed
try:
    from graphbrain.rag.core import GraphbrainRAG
except ImportError:
    # Fallback to old implementation if rag module not available
    from graphbrain.embeddings.legacy import GraphbrainRAG

__all__ = [
    'EdgeEmbedder',
    'edge_to_text',
    'ChromaStore',
    'MemoryStore',
    'GraphbrainRAG'
]
