"""Custom exceptions for Graphbrain API."""


class GraphbrainAPIError(Exception):
    """Base exception for Graphbrain API errors."""
    pass


class GraphPatternError(GraphbrainAPIError):
    """Raised when a graph pattern is invalid or malicious."""
    pass


class StoreError(GraphbrainAPIError):
    """Raised when there's an error with the underlying hypergraph store."""
    pass


class ValidationError(GraphbrainAPIError):
    """Raised during edge validation against rules."""
    pass
