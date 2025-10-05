"""Demo 2: Foundation Pack - Bulk Load Medical Knowledge"""

from graphbrain.api import GraphbrainAPI

# Foundation pack: medical guidelines (LLM can generate this)
foundation_pack = [
    # Contraindications (mandatory - will DENY)
    {"s": "(contraindicated/P ibuprofen/C diabetes/C)",
     "attrs": {"layer": "foundation", "mandatory": True, "confidence": 0.98}},

    {"s": "(contraindicated/P aspirin/C pregnancy/C)",
     "attrs": {"layer": "foundation", "mandatory": True, "confidence": 0.99}},

    # Recommendations (non-mandatory - will inform)
    {"s": "(recommended/P metformin/C diabetes/C)",
     "attrs": {"layer": "foundation", "mandatory": False, "confidence": 0.95}},

    {"s": "(recommended/P walking/C diabetes/C)",
     "attrs": {"layer": "foundation", "mandatory": False, "confidence": 0.92}},
]

with GraphbrainAPI('medical_kb.hg') as api:
    # Bulk load foundation
    result = api.bulk_add(foundation_pack)
    print(f"✓ Loaded foundation pack:")
    print(f"  Inserted: {result['inserted']} rules")
    print(f"  Total edges: {api.count()}")
    print()

    # Add agent safety rules
    api.add_fact('any_drug', 'requires', 'medical_supervision',
                 attrs={'layer': 'agent_rule', 'mandatory': True})
    print(f"✓ Added agent rule: requires medical supervision")
    print()

    # Query by layer
    foundation_rules = [e for e in api.all_edges()
                        if api.get_attrs(e) and api.get_attrs(e).get('layer') == 'foundation']
    print(f"Foundation layer: {len(foundation_rules)} rules")
