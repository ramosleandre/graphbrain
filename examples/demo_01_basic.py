"""Demo 1: Basic API Usage - LevelDB + Auto-Typing"""

from graphbrain.api import GraphbrainAPI

# Create knowledge base (LevelDB backend - .hg extension)
with GraphbrainAPI('medical_kb.hg') as api:
    # Simple input → Auto-typed storage
    edge = api.add_fact('ibuprofen', 'contraindicated', 'diabetes',
                        attrs={'layer': 'foundation', 'mandatory': True})

    print(f"Created: {edge}")
    print(f"Storage: typed with /P (predicate) and /C (concepts)")
    print()

    # Query with type
    results = api.query('(contraindicated/P * *)')
    print(f"Query '(contraindicated/P * *)' → {len(results)} result(s)")
    print(f"  - {results[0]}")
    print()

    # Attributes
    attrs = api.get_attrs(edge)
    print(f"Attributes: layer={attrs['layer']}, mandatory={attrs['mandatory']}")
