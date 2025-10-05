"""
High-level API for LLM integration with Graphbrain.

This module provides a simplified, stable interface for AI agents and LLMs
to interact with Graphbrain hypergraphs.
"""

from .core import GraphbrainAPI, create_api
from .utils import normalize_edge, sanitize_pattern
from .bulk import quick_add, quick_query
from .exceptions import (
    GraphbrainAPIError,
    GraphPatternError,
    StoreError,
    ValidationError
)

__all__ = [
    'GraphbrainAPI',
    'create_api',
    'normalize_edge',
    'sanitize_pattern',
    'quick_add',
    'quick_query',
    'GraphbrainAPIError',
    'GraphPatternError',
    'StoreError',
    'ValidationError'
]
