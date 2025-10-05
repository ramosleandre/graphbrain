"""
Backward compatibility wrapper for graphbrain.api module.

This file maintains backward compatibility by re-exporting from the new
modular api package.
"""

# Re-export all public API from the new modular structure
from graphbrain.api.core import GraphbrainAPI, create_api
from graphbrain.api.utils import normalize_edge, sanitize_pattern
from graphbrain.api.bulk import quick_add, quick_query
from graphbrain.api.exceptions import (
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
