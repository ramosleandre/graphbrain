"""Validation logic for rule-based edge checking."""

from typing import Dict, List, Optional, Union, Any, Literal
from graphbrain import hedge
from graphbrain.hyperedge import Hyperedge


def validate_edges_against_rules(
    api,
    proposed_edges: Union[str, Hyperedge, List[Union[str, Hyperedge]]],
    rule_pattern: Optional[str] = None,
    strategy: Literal["tri_state", "simple"] = "tri_state",
    layers: Optional[List[str]] = None,
    confidence_min: float = 0.0
) -> Dict[str, Any]:
    """
    Validate proposed edge(s) against rules with tri-state logic.

    Returns:
        ValidationReport dict with decision (ALLOW/DENY/UNKNOWN)
    """
    # Normalize to list
    if not isinstance(proposed_edges, list):
        proposed_edges = [proposed_edges]

    # Convert strings to hedges
    proposed_edges = [
        hedge(e) if isinstance(e, str) else e
        for e in proposed_edges
    ]

    # Determine which rules to check
    if rule_pattern:
        rules = api.query(rule_pattern)
    else:
        active = layers if layers else list(api._active_layers)
        rules = []
        for edge in api.all_edges(limit=10000):
            attrs = api.get_attrs(edge)
            if attrs and attrs.get("layer") in active:
                rules.append(edge)

    # Filter by confidence
    if confidence_min > 0.0:
        filtered_rules = []
        for rule in rules:
            attrs = api.get_attrs(rule)
            confidence = float(attrs.get("confidence", 1.0)) if attrs else 1.0
            if confidence >= confidence_min:
                filtered_rules.append(rule)
        rules = filtered_rules

    kept = []
    rejected = []
    unknown = []

    for proposed in proposed_edges:
        edge_decision, why_trace = _evaluate_edge(api, proposed, rules, strategy)

        if edge_decision == "ALLOW":
            kept.append({
                "edge": proposed,
                "edge_str": proposed.to_str(),
                "why_trace": why_trace
            })
        elif edge_decision == "DENY":
            rejected.append({
                "edge": proposed,
                "edge_str": proposed.to_str(),
                "reason": "contraindicated or forbidden by rules",
                "why_trace": why_trace
            })
        else:  # UNKNOWN
            unknown.append({
                "edge": proposed,
                "edge_str": proposed.to_str(),
                "reason": "insufficient information",
                "suggestions": ["add more context", "clarify user conditions"],
                "why_trace": why_trace
            })

    # Overall decision
    if rejected:
        decision = "DENY"
    elif unknown:
        decision = "UNKNOWN"
    else:
        decision = "ALLOW"

    return {
        "decision": decision,
        "kept": kept,
        "rejected": rejected,
        "unknown": unknown,
        "rules_checked": len(rules)
    }


def _evaluate_edge(
    api,
    proposed: Hyperedge,
    rules: List[Hyperedge],
    strategy: str
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Evaluate a single edge against rules.

    Returns:
        (decision, why_trace) where decision is ALLOW/DENY/UNKNOWN
    """
    why_trace = []
    proposed_concepts = set(str(atom) for atom in proposed.atoms())

    # Get user facts to enrich context
    user_conditions = set()
    try:
        for edge in api.all_edges(limit=1000):
            attrs = api.get_attrs(edge)
            if attrs and attrs.get("layer") == "user":
                for atom in edge.atoms():
                    atom_str = str(atom)
                    if "/C" in atom_str and "user" not in atom_str.lower():
                        user_conditions.add(atom_str)
    except:
        pass

    for rule in rules:
        rule_concepts = set(str(atom) for atom in rule.atoms())

        # Direct overlap
        direct_overlap = proposed_concepts & rule_concepts

        # Context overlap
        context_overlap = user_conditions & rule_concepts

        # Total match
        total_overlap = direct_overlap | context_overlap

        if len(total_overlap) >= 2:  # Significant overlap
            rule_attrs = api.get_attrs(rule) or {}
            connector = str(rule[0]) if len(rule) > 0 else ""

            # Check connector type
            is_contraindicated = "contraind" in connector.lower() or "forbidden" in connector.lower()
            is_recommended = "recommend" in connector.lower() or "advise" in connector.lower()
            is_obligatory = "oblige" in connector.lower() or "require" in connector.lower()

            mandatory = rule_attrs.get("mandatory", "false").lower() == "true" if isinstance(rule_attrs.get("mandatory"), str) else rule_attrs.get("mandatory", False)

            # Build why-trace entry
            trace_entry = {
                "rule": rule.to_str(),
                "connector": connector,
                "layer": rule_attrs.get("layer"),
                "source": rule_attrs.get("source"),
                "mandatory": mandatory,
                "confidence": float(rule_attrs.get("confidence", 1.0)),
                "matched_concepts": list(total_overlap),
                "direct_match": list(direct_overlap),
                "user_context": list(context_overlap)
            }

            if is_contraindicated and mandatory:
                why_trace.append(trace_entry)
                return ("DENY", why_trace)
            elif is_obligatory and mandatory:
                why_trace.append(trace_entry)
                return ("UNKNOWN", why_trace)
            elif is_recommended:
                why_trace.append(trace_entry)
                continue

    if why_trace:
        return ("ALLOW", why_trace)
    else:
        return ("ALLOW" if strategy == "simple" else "ALLOW", why_trace)
