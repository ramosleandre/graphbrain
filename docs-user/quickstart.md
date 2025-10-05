# Quick Start Guide

Get started with Graphbrain in 5 minutes.

## Prerequisites

**First, complete the [Installation](installation.md)** to set up LevelDB 1.22.

## 1. Basic API Usage (2 minutes)

```python
from graphbrain.api import GraphbrainAPI

# Create hypergraph with LevelDB (.hg extension)
with GraphbrainAPI('my_graph.hg') as api:
    # Add a fact
    api.add_fact('Paris', 'capital_of', 'France')

    # Query - use exact type or wildcard
    results = api.query('(capital_of/P * *)')
    print(f"Found {len(results)} facts")
    for edge in results:
        print(edge.to_str())
```

**Output:**
```
Found 1 facts
(capital_of/P Paris/C France/C)
```

**Important:** Query patterns must match atom types:
- ✅ `(capital_of/P * *)` - matches `capital_of/P`
- ✅ `(* * *)` - matches anything
- ❌ `(capital_of/* * *)` - does NOT match `capital_of/P`

## 2. Load Knowledge from JSON (3 minutes)

Create a file `medical_rules.json`:

```json
{
  "rules": [
    {
      "s": "(contraindicated/P ibuprofen/C diabetes/C)",
      "attrs": {
        "layer": "foundation",
        "mandatory": true,
        "confidence": 0.98,
        "source": "Medical Guidelines 2025"
      }
    },
    {
      "s": "(recommended/P metformin/C diabetes/C)",
      "attrs": {
        "layer": "foundation",
        "mandatory": false,
        "confidence": 0.95
      }
    }
  ]
}
```

Load it:

```python
from graphbrain.api import GraphbrainAPI

with GraphbrainAPI('medical_kb.hg') as api:
    # Load foundation pack
    result = api.load_foundation_pack('medical_rules.json')
    print(f"Loaded {result['inserted']} rules")

    # Query contraindications
    contras = api.query('(contraindicated/P * *)')
    for edge in contras:
        print(edge.to_str())
```

**Output:**
```
Loaded 2 rules
(contraindicated/P ibuprofen/C diabetes/C)
```

You can also use YAML format. See [foundation_pack_example.json](../examples/foundation_pack_example.json) for more examples.

## 3. Validation with Layers (5 minutes)

```python
from graphbrain.api import GraphbrainAPI

with GraphbrainAPI('medical_kb.hg') as api:
    # Load foundation rules
    api.load_foundation_pack('medical_rules.json')

    # Add user facts
    api.add_user_fact('diabetes', session_id='patient-001')

    # Enable layers
    api.toggle_layer('foundation', True)
    api.toggle_layer('user', True)

    # Validate action
    result = api.validate_against_rules(
        proposed_edges='(takes/P patient/C ibuprofen/C)',
        layers=['foundation', 'user']
    )

    print(f"Decision: {result['decision']}")  # DENY
    if result['rejected']:
        print(f"Reason: {result['rejected'][0]['reason']}")
        print(f"Matched rule: {result['rejected'][0]['why_trace'][0]['rule']}")
```

**Output:**
```
Decision: DENY
Reason: contraindicated or forbidden by rules
Matched rule: (contraindicated/P ibuprofen/C diabetes/C)
```

## Core Concepts

### 1. Hyperedges

Semantic hypergraphs use hyperedges to represent knowledge:

```python
(contraindicated/P ibuprofen/C diabetes/C)
#  ↑ predicate     ↑ concept   ↑ concept

# Types: P=Predicate, C=Concept, M=Modifier
```

### 2. Query Patterns

**Important:** Patterns must match atom types exactly:

```python
# ✅ Correct patterns
api.query('(contraindicated/P * *)')       # Matches predicate type
api.query('(* ibuprofen/C *)')              # Matches any with ibuprofen
api.query('(* * *)')                         # Matches all 3-ary edges

# ❌ Incorrect patterns (won't match!)
api.query('(contraindicated/* * *)')       # Won't match contraindicated/P
api.query('(*/P * *)')                      # Won't match - wildcard in atom
```

**Rule:** Use full atom with type `/P`, `/C`, etc., or use `*` to match any atom.

### 3. Layers

Organize knowledge by source/purpose:

- **foundation**: Medical guidelines, rules (mandatory)
- **agent_rule**: Agent safety policies
- **user**: User session data (conditions, preferences)
- **plan**: Generated action plans

### 4. Validation States

- **ALLOW**: Action approved
- **DENY**: Blocked by mandatory contraindication
- **UNKNOWN**: Insufficient information

## 6 Essential API Functions

```python
# 1. Add fact (simple triple)
api.add_fact(subject, predicate, object, attrs=None)
# Creates: (predicate/P subject/C object/C)

# 2. Query (pattern matching)
api.query(pattern: str, limit=None)
# Use: '(predicate/P * *)' or '(* * *)'

# 3. Bulk add (load foundation packs)
api.bulk_add(edges: list[dict])

# 4. Load foundation pack (JSON/YAML)
api.load_foundation_pack(filepath)

# 5. Validate (tri-state with Why-Trace)
api.validate_against_rules(edges, layers, confidence_min=0.0)

# 6. Toggle layer (enable/disable)
api.toggle_layer(layer: str, enabled: bool)
```

## Common Query Patterns

```python
# Find all edges with specific predicate
api.query('(contraindicated/P * *)')

# Find all edges containing a concept
api.query('(* diabetes/C *)')
api.query('(* * diabetes/C)')

# Find all ternary edges
api.query('(* * *)')

# Use connector helper (adds /P automatically)
api.edges_by_connector('contraindicated')
```

## Next Steps

1. **Run examples**: See [examples](../examples/) directory
2. **Read features**: [features.md](features.md) - What's new in this fork
3. **API reference**: [api-reference.md](api-reference.md) - Complete API

## Using Different Backends

```python
# LevelDB (recommended) - use .hg extension
api = GraphbrainAPI('data.hg')

# SQLite (beta) - use .db extension
api = GraphbrainAPI('data.db')
```

**Note:** LevelDB 1.22 is recommended. See [Installation](installation.md) for setup.

## Troubleshooting

### Query returns empty results?

**Problem:**
```python
api.add_fact('Paris', 'capital_of', 'France')
results = api.query('(capital_of/* * *)')  # ❌ Returns []
```

**Solution:** Use exact type or wildcard:
```python
results = api.query('(capital_of/P * *)')  # ✅ Returns 1 result
# OR
results = api.query('(* * *)')              # ✅ Returns all edges
```

### LevelDB issues?

See [Installation Guide](installation.md) for LevelDB 1.22 setup on your platform.

### Need embeddings/RAG?

```bash
pip install sentence-transformers chromadb
# See examples for usage
```

---

**Ready?** Start with the [examples](../examples/) directory 🚀
