# Features - What's New

What this fork adds to [Graphbrain](http://graphbrain.net).

## Overview

This fork extends Graphbrain with **LLM integration capabilities** while maintaining 100% backward compatibility.

## New Features

### 1. Simple API for LLMs

**Problem:** Original Graphbrain API is low-level and verbose for AI agents.

**Solution:** New high-level `graphbrain.api` module with 6 essential functions:

```python
from graphbrain.api import GraphbrainAPI

with GraphbrainAPI('knowledge.hg') as api:
    # Simple fact addition
    api.add_fact('Paris', 'capital_of', 'France')

    # Pattern queries (use exact type /P or wildcard *)
    results = api.query('(capital_of/P * *)')

    # Bulk operations
    api.bulk_add(edges_list)

    # Foundation packs
    api.load_foundation_pack('rules.json')

    # Validation
    api.validate_against_rules(edges, layers=['foundation'])

    # Layer management
    api.toggle_layer('foundation', True)
```

**Benefits:**
- ✅ LLM function calling ready
- ✅ Context manager support
- ✅ Consistent interface
- ✅ Clear error messages

### 2. JSON/YAML Knowledge Loading (Beta)

**Problem:** Writing hyperedge notation is verbose.

**Solution:** Load structured knowledge from JSON/YAML files:

```json
{
  "rules": [
    {
      "s": "(contraindicated/P ibuprofen/C diabetes/C)",
      "attrs": {
        "layer": "foundation",
        "mandatory": true,
        "confidence": 0.98
      }
    }
  ]
}
```

```python
api.load_foundation_pack('medical_rules.json')
```

**Status:** Beta - JSON/YAML loading is functional but experimental.

**Benefits:**
- ✅ LLMs can generate knowledge packs
- ✅ Human-readable format
- ✅ Version control friendly
- ✅ Easy validation

### 3. RAG Integration

**Problem:** No semantic search in original Graphbrain.

**Solution:** Vector embeddings + hybrid retrieval:

```python
from graphbrain.embeddings import GraphbrainRAG

rag = GraphbrainRAG('kb.hg', 'vectors')

# Add with automatic embedding
rag.add_edge_with_embedding('is', ['graphbrain', 'awesome'])

# Semantic search
results = rag.retrieve('knowledge graph library', k=5)
```

**Features:**
- Multiple embedding providers (Sentence Transformers, Vertex AI, OpenAI)
- Hybrid search (symbolic + semantic)
- ChromaDB integration

### 4. Better Installation

**Problem:** Original Graphbrain required complex LevelDB setup.

**Solution:**
- **LevelDB (Recommended):** Clear instructions for macOS M-series
- **SQLite (Beta):** Zero-dependency fallback

**Installation improvements:**
- ✅ Works on macOS M1/M2/M3/M4 (tested method)
- ✅ SQLite as beta alternative
- ✅ Clear troubleshooting docs
- ✅ Environment variables automated

**Backend comparison:**

| Feature | LevelDB | SQLite (Beta) |
|---------|---------|---------------|
| Performance | Fast | Moderate |
| Installation | Medium | Easy |
| Stability | Production | Beta |
| Best for | All users | Development fallback |

**Recommendation:** Use LevelDB for all scenarios. SQLite is beta.

## What's the Same

**100% backward compatible** with original Graphbrain:

```python
# Old API still works
from graphbrain import hgraph, hedge

hg = hgraph('data.hg')
hg.add(hedge('(is/P graphbrain/C awesome/C)'))
results = list(hg.search(hedge('(is/* * *)')))
hg.close()
```

**Core features unchanged:**
- Hypergraph operations
- NLP parsing (spaCy)
- Semantic hyperedge notation
- Pattern matching

## Migration Guide

### For Existing Users

**No changes needed!** Your code still works:

```python
# This still works exactly the same
from graphbrain import hgraph, hedge

hg = hgraph('data.hg')
hg.add(hedge('(is/P graphbrain/C awesome/C)'))
```

### To Use New Features

Opt-in to new API:

```python
# Old way (still works)
from graphbrain import hgraph
hg = hgraph('data.hg')
# ... manual operations ...
hg.close()

# New way (recommended for new code)
from graphbrain.api import GraphbrainAPI
with GraphbrainAPI('data.hg') as api:
    api.add_fact('subject', 'predicate', 'object')
```

## Use Cases

### 1. LLM Agents

```python
# LLM function calling
def add_knowledge(subject, predicate, object):
    with GraphbrainAPI('kb.hg') as api:
        return api.add_fact(subject, predicate, object)

def query_knowledge(pattern):
    with GraphbrainAPI('kb.hg') as api:
        return api.query(pattern)
```

### 2. Knowledge Validation

```python
# Validate AI-generated plans
api.validate_against_rules(
    proposed_edges=plan_edges,
    layers=['foundation', 'user'],
    confidence_min=0.8
)
```

### 3. RAG Systems

```python
# Hybrid retrieval
rag = GraphbrainRAG('kb.hg', 'vectors')
relevant_facts = rag.retrieve(user_question, k=5)
llm_answer = generate_answer(relevant_facts, user_question)
```

## Performance

### Backend Performance

| Metric | LevelDB | SQLite (Beta) |
|--------|---------|---------------|
| Read speed | 100k-1M edges/s | 10k-100k edges/s |
| Write speed | 50k-500k edges/s | 5k-50k edges/s |
| Best for | Production | Development |

**Recommendation:** Use LevelDB for optimal performance.

### When to Use Each Backend

**LevelDB (Recommended for all):**
- Production use
- Any graph size
- Optimal performance needed
- Stable, tested solution

**SQLite (Beta - fallback only):**
- Windows without LevelDB
- Quick prototyping
- Small graphs (< 100k edges)
- Development/testing

## Roadmap

**Completed:**
- ✅ LLM-friendly API
- ✅ JSON/YAML loading (beta)
- ✅ RAG integration
- ✅ Better installation docs
- ✅ LevelDB for macOS M-series

**In Progress:**
- ⚠️ SQLite backend stabilization
- ⚠️ JSON/YAML format finalization

**Future:**
- 🔜 More embedding providers
- 🔜 Enhanced validation logic
- 🔜 Graph visualization
- 🔜 Multi-language support

## Summary

**What we added:**
- ✅ Simple API (`graphbrain.api`)
- ✅ JSON/YAML support (beta)
- ✅ RAG integration
- ✅ Better installation (LevelDB recommended)

**What's the same:**
- ✅ All core Graphbrain features
- ✅ 100% backward compatible
- ✅ Same hypergraph model

**Philosophy:**
> "Make LLM integration easy without sacrificing Graphbrain's power"

## Next Steps

1. **Install:** Follow [Installation Guide](installation.md)
2. **Learn:** Try [Quick Start](quickstart.md)
3. **Build:** Run [examples](../examples/)

## Resources

- [Installation Guide](installation.md) - Setup LevelDB
- [Quick Start](quickstart.md) - Get started fast
- [API Reference](api-reference.md) - Complete API docs
- [Original Graphbrain](http://graphbrain.net) - Core project
