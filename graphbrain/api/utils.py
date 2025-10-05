"""Utility functions for API operations."""

import re
from .exceptions import GraphPatternError


def _canon_atom(s: str) -> str:
    """
    Canonicalize an atom string.

    - Strips whitespace
    - Converts spaces to underscores for multi-word concepts
    - Preserves case
    """
    s = s.strip()
    s = s.replace(" ", "_")
    return s


def _ensure_typed_concept(x: str) -> str:
    """Ensure atom has /C type, unless already typed."""
    return x if "/" in x else f"{_canon_atom(x)}/C"


def _ensure_typed_pred(x: str) -> str:
    """Ensure atom has /P type, unless already typed."""
    return x if "/" in x else f"{_canon_atom(x)}/P"


def _ensure_typed_modifier(x: str) -> str:
    """Ensure atom has /M type, unless already typed."""
    return x if "/" in x else f"{_canon_atom(x)}/M"


def _normalize_triplet(subject: str, predicate: str, object_: str) -> tuple:
    """
    Normalize a subject-predicate-object triplet with proper types.

    Returns:
        (typed_subject, typed_predicate, typed_object)
    """
    s = _ensure_typed_concept(subject)
    p = _ensure_typed_pred(predicate)
    o = _ensure_typed_concept(object_)
    return s, p, o


def normalize_edge(edge_str: str, remove_lang: bool = True, simplify_types: bool = True) -> str:
    """
    Normalize hyperedge representation for stable output.

    Args:
        edge_str: Hyperedge string to normalize
        remove_lang: Remove language tags (/en, /fr, etc.)
        simplify_types: Simplify morphological tags to base types

    Returns:
        Normalized edge string

    Example:
        >>> normalize_edge("(is/Pd.sc.|f--3s-/en graphbrain/Cc.s/en)")
        "(is/P graphbrain/C)"
    """
    # Remove language tags
    if remove_lang:
        edge_str = re.sub(r'/[a-z]{2}\b', '', edge_str)

    # Simplify type tags
    if simplify_types:
        edge_str = re.sub(r'/([PCMBADJRSTXW])[a-z\.\|\-\d]+', r'/\1', edge_str)

    # Remove builder operators
    edge_str = re.sub(r'\(\+/B[^\s]*\s+', '(', edge_str)

    # Clean up spaces
    edge_str = re.sub(r'\s+', ' ', edge_str)

    return edge_str.strip()


def sanitize_pattern(pattern: str, max_depth: int = 10) -> str:
    """
    Sanitize a query pattern to prevent malicious queries.

    Args:
        pattern: Pattern string to sanitize
        max_depth: Maximum nesting depth allowed

    Returns:
        Sanitized pattern string

    Raises:
        GraphPatternError: If pattern is invalid or potentially malicious
    """
    # Check balanced parentheses
    if pattern.count('(') != pattern.count(')'):
        raise GraphPatternError("Unbalanced parentheses in pattern")

    # Check depth
    current_depth = 0
    max_observed_depth = 0
    for char in pattern:
        if char == '(':
            current_depth += 1
            max_observed_depth = max(max_observed_depth, current_depth)
        elif char == ')':
            current_depth -= 1

    if max_observed_depth > max_depth:
        raise GraphPatternError(
            f"Pattern depth {max_observed_depth} exceeds maximum {max_depth}"
        )

    # Check for suspicious patterns
    suspicious_patterns = [
        r';.*DROP',
        r';.*DELETE',
        r';.*UPDATE',
        r'--\s',
    ]

    for suspicious in suspicious_patterns:
        if re.search(suspicious, pattern, re.IGNORECASE):
            raise GraphPatternError(
                f"Potentially malicious pattern detected"
            )

    return pattern
