# API Reference - New Features

Complete reference for new features added to Graphbrain.

## Table of Contents
- [GraphbrainAPI Class](#graphbrainapi-class)
- [Bulk Operations](#bulk-operations)
- [Layer Management](#layer-management)
- [Validation](#validation)
- [Multi-hop Reasoning](#multi-hop-reasoning)
- [Embeddings](#embeddings)
- [RAG](#rag)
- [Visualization](#visualization)
- [Configuration](#configuration)

---

## GraphbrainAPI Class

High-level API for LLM integration.

### Import

```python
from graphbrain.api import GraphbrainAPI
```

### Basic Usage

```python
# Context manager (recommended)
with GraphbrainAPI('kb.db') as api:
    edge = api.add_edge('is', ['graphbrain', 'awesome'])
    results = api.query('(is/* * *)')

# Manual management
api = GraphbrainAPI('kb.db')
try:
    # ... operations ...
finally:
    api.close()
```

---

## Bulk Operations

### `bulk_add(edges, upsert=True)`

Add multiple edges efficiently.

**Parameters:**
- `edges`: `List[Dict[str, Any]]` - List of edge dictionaries
  - Each dict: `{"s": "edge_string", "attrs": {...}}`
- `upsert`: `bool` - If `True`, update existing; if `False`, skip duplicates

**Returns:** `Dict[str, Any]`
```python
{
    "inserted": int,      # Number of new edges
    "updated": int,       # Number of updated edges
    "skipped": int,       # Number skipped (upsert=False)
    "errors": [           # List of errors
        {"edge": {...}, "error": "message"}
    ]
}
```

**Example:**
```python
edges = [
    {"s": "(has/P user/C diabetes/C)",
     "attrs": {"layer": "user", "session": "s1"}},
    {"s": "(contraindicated/P ibuprofen/C diabetes/C)",
     "attrs": {"layer": "foundation", "mandatory": True}}
]

result = api.bulk_add(edges)
print(f"Inserted: {result['inserted']}, Errors: {len(result['errors'])}")
```

---

## Layer Management

### `toggle_layer(layer, enabled)`

Enable or disable a layer for validation.

**Parameters:**
- `layer`: `str` - Layer name (`'foundation'`, `'user'`, `'agent_rule'`, `'plan'`, etc.)
- `enabled`: `bool` - `True` to enable, `False` to disable

**Example:**
```python
api.toggle_layer("foundation", True)
api.toggle_layer("experimental", False)
```

### `get_active_layers()`

Get currently active layers.

**Returns:** `set` - Set of active layer names

**Example:**
```python
active = api.get_active_layers()
print(f"Active layers: {active}")
# Output: {'foundation', 'user', 'agent_rule'}
```

### `add_user_fact(text, attrs=None, session_id=None)`

Add a user fact from natural language.

**Parameters:**
- `text`: `str` - Fact in natural language (e.g., "diabetic")
- `attrs`: `Optional[Dict]` - Additional attributes
- `session_id`: `Optional[str]` - Session identifier

**Returns:** `Hyperedge` - Created edge

**Example:**
```python
edge = api.add_user_fact("diabetic", session_id="session-001")
# Creates: (a/P user/C diabetic/C) with layer=user
```

### `plan_to_edges(steps, user="user")`

Convert plan steps to hyperedge dictionaries.

**Parameters:**
- `steps`: `List[str]` - List of action descriptions
- `user`: `str` - Subject performing actions (default: `"user"`)

**Returns:** `List[Dict[str, Any]]` - List of edge dictionaries

**Example:**
```python
steps = ["Take ibuprofen", "Walk 30 minutes"]
edges = api.plan_to_edges(steps)
# Returns: [
#   {"s": "(take/P user/C ibuprofen/C)", "attrs": {"layer": "plan", ...}},
#   {"s": "(walk/P user/C 30-minutes/C)", "attrs": {"layer": "plan", ...}}
# ]
```

---

## Validation

### `validate_against_rules(proposed_edges, ...)`

Validate edges against rules with tri-state logic and Why-Trace.

**Parameters:**
- `proposed_edges`: `Union[str, Hyperedge, List]` - Edge(s) to validate
- `rule_pattern`: `Optional[str]` - Pattern to match rules (default: uses active layers)
- `strategy`: `Literal["tri_state", "simple"]` - Validation strategy (default: `"tri_state"`)
- `layers`: `Optional[List[str]]` - Filter rules by layers (default: active layers)
- `confidence_min`: `float` - Minimum confidence threshold 0.0-1.0 (default: `0.0`)

**Returns:** `Dict[str, Any]` - Validation report

```python
{
    "decision": "ALLOW" | "DENY" | "UNKNOWN",
    "kept": [                          # Approved edges
        {
            "edge": Hyperedge,
            "edge_str": str,
            "why_trace": [...]         # Supporting rules
        }
    ],
    "rejected": [                      # Rejected edges
        {
            "edge": Hyperedge,
            "edge_str": str,
            "reason": str,
            "why_trace": [...]         # Blocking rules
        }
    ],
    "unknown": [                       # Uncertain edges
        {
            "edge": Hyperedge,
            "edge_str": str,
            "reason": str,
            "suggestions": [...]
        }
    ],
    "rules_checked": int
}
```

**Why-Trace Format:**
```python
{
    "rule": str,                # Rule edge string
    "connector": str,           # Rule connector
    "layer": str,               # Rule layer
    "source": str,              # Rule source
    "mandatory": bool,          # Is mandatory
    "confidence": float,        # Confidence score
    "matched_concepts": [str]   # Matched concepts
}
```

**Example:**
```python
result = api.validate_against_rules(
    proposed_edges=["(take/P user/C ibuprofen/C)"],
    layers=["foundation", "user"],
    strategy="tri_state",
    confidence_min=0.8
)

if result['decision'] == 'DENY':
    for item in result['rejected']:
        print(f"Rejected: {item['edge_str']}")
        print(f"Reason: {item['reason']}")
        for trace in item['why_trace']:
            print(f"  Rule: {trace['rule']}")
            print(f"  Source: {trace['source']}")
```

---

## Multi-hop Reasoning

### `search_with_reasoning(query, hops=2, limit=100)`

Multi-hop BFS search for reasoning chains.

**Parameters:**
- `query`: `Union[str, Hyperedge]` - Starting edge or pattern
- `hops`: `int` - Number of hops to traverse (default: `2`)
- `limit`: `int` - Maximum results (default: `100`)

**Returns:** `List[Dict[str, Any]]`

```python
[
    {
        "edge": Hyperedge,
        "edge_str": str,
        "distance": int,          # Hops from start
        "path": [str],            # Reasoning path
        "attrs": Dict             # Edge attributes
    }
]
```

**Example:**
```python
results = api.search_with_reasoning(
    "(has/P user/C diabetes/C)",
    hops=2,
    limit=20
)

for result in results:
    print(f"Distance {result['distance']}: {result['edge_str']}")
    print(f"  Path: {' → '.join(result['path'])}")
```

---

## Embeddings

### EdgeEmbedder

Unified embedder with caching.

```python
from graphbrain.embeddings import EdgeEmbedder

embedder = EdgeEmbedder(
    provider='sentence-transformers',  # or 'vertex-ai', 'openai', 'mock'
    model='all-MiniLM-L6-v2',         # Optional model name
    enable_cache=True,                 # Enable file caching
    cache_dir='~/.cache/graphbrain/embeddings'
)

# Embed single edge
embedding = embedder.embed_edge(edge)

# Batch embed
embeddings = embedder.embed_batch(edges, batch_size=64)

# Properties
print(embedder.dimension)  # Embedding dimension
print(embedder.name)       # Provider name
```

**Supported Providers:**
- `'sentence-transformers'` - Local, free (default)
- `'vertex-ai'` - Google Cloud Vertex AI
- `'openai'` - OpenAI embeddings
- `'mock'` - Deterministic mock (testing)

### Vector Stores

#### ChromaStore

```python
from graphbrain.embeddings.stores import ChromaStore

store = ChromaStore(
    collection_name='my_collection',
    persist_directory='./chroma_data'  # Optional
)

store.set_embedder(embedder)

# Add
store.add(edge, embedding, metadata={'layer': 'foundation'})

# Search
results = store.search("diabetes medication", k=5)
for edge, score, metadata in results:
    print(f"{edge} (score: {score})")

# Count
print(f"Store size: {store.count()}")
```

#### MemoryStore

```python
from graphbrain.embeddings.stores import MemoryStore

store = MemoryStore(embedder=embedder)
# Same API as ChromaStore, but in-memory only
```

---

## RAG

### GraphbrainRAG

Combined hypergraph + vector store.

```python
from graphbrain.rag import GraphbrainRAG

rag = GraphbrainRAG(
    hg_locator='kb.db',
    collection_name='vectors',
    embedder_provider='sentence-transformers',
    embedder_model='all-MiniLM-L6-v2',    # Optional
    persist_directory='./chroma_data',     # Optional
    enable_cache=True
)

# Add with embedding
edge = rag.add_edge_with_embedding(
    'contraindicated',
    ['ibuprofen', 'diabetes'],
    attrs={'severity': 'high'}
)

# Index all existing edges
count = rag.index_all(edge_pattern='(*/P * *)', batch_size=64)

# Retrieve
results = rag.retrieve("diabetes medications", k=5)
for result in results:
    print(result['edge_str'])
    print(result['text'])
    print(result['score'])

# Validate with RAG
validation = rag.validate_with_rag(
    "Prescribe ibuprofen to diabetic",
    "diabetes contraindications",
    k=5
)
```

### Utility Functions

```python
from graphbrain.rag import index_edges, retrieve_similar

# Index edges manually
count = index_edges(api, embedder, vector_store, edge_pattern=None)

# Retrieve similar
results = retrieve_similar(embedder, vector_store, "query", k=5)
```

---

## Visualization

Export graphs to various formats.

```python
from graphbrain.viz import to_graphml, to_dot, to_cytoscape
```

### `to_graphml(api, output_path, edge_pattern=None, color_by_layer=True)`

Export to GraphML (yEd, Gephi).

**Returns:** `int` - Number of edges exported

```python
count = to_graphml(api, 'graph.graphml', color_by_layer=True)
```

### `to_dot(api, output_path, edge_pattern=None, color_by_layer=True)`

Export to DOT (Graphviz).

```python
count = to_dot(api, 'graph.dot')
# Then: dot -Tpng graph.dot -o graph.png
```

### `to_cytoscape(api, edge_pattern=None)`

Export to Cytoscape JSON.

**Returns:** `Dict[str, Any]` - Cytoscape-compatible dict

```python
import json

cy_data = to_cytoscape(api)
with open('graph.json', 'w') as f:
    json.dump(cy_data, f, indent=2)
```

**Layer Colors:**
- Foundation: Red (`#FF6B6B`)
- User: Teal (`#4ECDC4`)
- Agent Rule: Blue (`#45B7D1`)
- Plan: Orange (`#FFA07A`)
- Experimental: Green (`#95E1D3`)

---

## Configuration

### GraphbrainConfig

```python
from graphbrain.config import get_config, validate_api_key

# Get configuration
config = get_config()

print(config.default_backend)        # 'sqlite'
print(config.default_embedder)       # 'sentence-transformers'
print(config.google_api_key)         # From .env
print(config.embedding_cache_enabled) # True
print(config.log_level)              # 'INFO'

# Validate API key
key = validate_api_key('google')  # Raises ValueError if not set

# Reload configuration
config = get_config(reload=True)
```

**Environment Variables** (see `.env.example`):
- `GOOGLE_API_KEY` - Google Cloud / Vertex AI
- `OPENAI_API_KEY` - OpenAI
- `GRAPHBRAIN_BACKEND` - `'sqlite'` or `'leveldb'`
- `GRAPHBRAIN_EMBEDDER` - Default embedder provider
- `GRAPHBRAIN_EMBEDDING_CACHE` - Enable caching
- `GRAPHBRAIN_LOG_LEVEL` - Log level
- And many more...

---

## Security

### `sanitize_pattern(pattern, max_depth=10)`

Sanitize query patterns to prevent malicious queries.

```python
from graphbrain.api import sanitize_pattern, GraphPatternError

try:
    safe = sanitize_pattern("(is/* * *)")  # OK
    safe = sanitize_pattern("(" * 100)      # Raises GraphPatternError
except GraphPatternError as e:
    print(f"Invalid pattern: {e}")
```

**Checks:**
- Balanced parentheses
- Maximum nesting depth
- SQL injection patterns

---

## Exceptions

```python
from graphbrain.api import (
    GraphbrainAPIError,      # Base exception
    GraphPatternError,       # Invalid pattern
    StoreError,              # Database error
    ValidationError          # Validation error
)

try:
    result = api.validate_against_rules(...)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

## Complete Example

```python
from graphbrain.api import GraphbrainAPI
from graphbrain.rag import GraphbrainRAG
from graphbrain.viz import to_graphml

# 1. API
with GraphbrainAPI('kb.db') as api:
    # Add rules
    api.bulk_add([
        {"s": "(contraindicated/P drug-A/C condition-X/C)",
         "attrs": {"layer": "foundation", "mandatory": True}}
    ])

    # Add user fact
    api.add_user_fact("has condition-X", session_id="s1")

    # Activate layers
    api.toggle_layer("foundation", True)
    api.toggle_layer("user", True)

    # Create and validate plan
    plan = api.plan_to_edges(["Take drug-A"])
    result = api.validate_against_rules(
        [hedge(e['s']) for e in plan],
        layers=["foundation", "user"],
        strategy="tri_state"
    )

    # Export
    to_graphml(api, 'output.graphml')

# 2. RAG
with GraphbrainRAG('kb.db', 'vectors') as rag:
    rag.add_edge_with_embedding('is', ['graphbrain', 'awesome'])
    results = rag.retrieve("knowledge graphs", k=5)
```

---

## See Also

- [Examples](../examples/) - Complete working examples
- [Tutorials](tutorials/) - Step-by-step guides
- [Features](features.md) - What's new
- [Installation](installation.md) - Setup instructions
