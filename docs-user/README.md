# Graphbrain + LLM - Documentation

Welcome to the documentation for this Graphbrain fork with LLM integration.

## What is This?

A fork of [Graphbrain](http://graphbrain.net) that adds:

- ✅ **Simple API** - LLM-friendly functions for knowledge graphs
- ✅ **JSON/YAML Support** - Load knowledge from structured files (beta)
- ✅ **RAG Integration** - Vector embeddings + semantic search
- ✅ **Better Installation** - LevelDB recommended, SQLite as beta fallback

## Quick Links

### Getting Started (Start Here!)

1. **[Installation](installation.md)** ← Install LevelDB (recommended) or SQLite (beta)
2. **[Quick Start](quickstart.md)** ← Get started in 5 minutes
3. **[Run Examples](../examples/)** ← See it in action

### Documentation

- **[Features](features.md)** - What's new in this fork
- **[API Reference](api-reference.md)** - Complete API documentation

## Quick Example

```python
from graphbrain.api import GraphbrainAPI

# LevelDB (recommended)
with GraphbrainAPI('knowledge.hg') as api:
    # Add facts
    api.add_fact('Paris', 'capital_of', 'France')

    # Load from JSON (beta)
    api.load_foundation_pack('medical_rules.json')

    # Query (use exact type /P or wildcard *)
    results = api.query('(capital_of/P * *)')
```

## What We Added vs Original Graphbrain

| Feature | Original | This Fork |
|---------|----------|-----------|
| **Core hypergraph** | ✅ | ✅ Same |
| **NLP parsing** | ✅ | ✅ Same |
| **Simple API** | ❌ | ✅ New |
| **JSON/YAML** | ❌ | ✅ Beta |
| **RAG** | ❌ | ✅ New |
| **LevelDB setup** | Complex | ✅ Documented |
| **SQLite backend** | Basic | ✅ Beta |

## Documentation Structure

### For New Users

**Path:** Installation → Quick Start → Examples

1. [Installation](installation.md) - Setup LevelDB (15 min)
2. [Quick Start](quickstart.md) - Learn basics (5 min)
3. [Examples](../examples/) - Run working code (10 min)

### For LLM Developers

**Path:** Installation → Quick Start → API Reference

1. [Installation](installation.md) - Setup environment
2. [Quick Start](quickstart.md#1-basic-api-usage-2-minutes) - Basic API
3. [Features](features.md#1-simple-api-for-llms) - LLM integration

### Reference

- [Features](features.md) - Complete feature comparison
- [API Reference](api-reference.md) - All functions documented

## Installation (TL;DR)

**macOS M-series (recommended):**

```bash
brew tap-new <your-username>/leveldb
cd "$(brew --repo <your-username>/leveldb)"
wget https://raw.githubusercontent.com/Homebrew/homebrew-core/e2c833d326c45d9aaf4e26af6dd8b2f31564dc04/Formula/leveldb.rb -O Formula/leveldb.rb
brew install <your-username>/leveldb/leveldb
echo 'export LIBRARY_PATH="$LIBRARY_PATH:/opt/homebrew/lib"' >> ~/.zshrc
echo 'export CPATH="$CPATH:/opt/homebrew/include"' >> ~/.zshrc
source ~/.zshrc
pip install -e .
python -m spacy download en_core_web_lg
```

Replace `<your-username>` with your actual username!

**SQLite fallback (beta, for Windows or quick start):**

```bash
pip install -e .
python -m spacy download en_core_web_lg
# Use .db files instead of .hg
```

See [Installation Guide](installation.md) for details.

## Key Concepts

### 1. Backends

**LevelDB (Recommended):**
- Fast, production-ready
- Use `.hg` file extension
- See [Installation](installation.md) for setup

**SQLite (Beta):**
- Easy setup, slower performance
- Use `.db` file extension
- Beta stability - development use only

### 2. API Modules

```python
# High-level API (new)
from graphbrain.api import GraphbrainAPI

# RAG support (new)
from graphbrain.embeddings import GraphbrainRAG

# Core API (original, still works)
from graphbrain import hgraph, hedge
```

### 3. Knowledge Loading

**Code (original):**
```python
api.add_fact('subject', 'predicate', 'object')
```

**JSON (beta):**
```json
{
  "rules": [
    {"s": "(predicate/P subject/C object/C)", "attrs": {...}}
  ]
}
```

## Common Tasks

### Add Knowledge

```python
# Simple facts
api.add_fact('Paris', 'capital_of', 'France')

# With attributes
api.add_fact('drug', 'contraindicated', 'condition',
             attrs={'layer': 'foundation', 'mandatory': True})

# From JSON (beta)
api.load_foundation_pack('knowledge.json')
```

### Query Knowledge

```python
# Pattern matching (use exact type /P or wildcard *)
results = api.query('(capital_of/P * *)')

# By connector (automatically adds /P)
contras = api.edges_by_connector('contraindicated')

# Multi-hop reasoning
related = api.search_with_reasoning(query, hops=2)
```

### Validate Actions

```python
# Enable layers
api.toggle_layer('foundation', True)
api.toggle_layer('user', True)

# Validate
result = api.validate_against_rules(
    proposed_edges='(takes/P patient/C drug/C)',
    layers=['foundation', 'user']
)

print(result['decision'])  # ALLOW/DENY/UNKNOWN
```

## Troubleshooting

**LevelDB installation issues?**
→ See [Installation Guide - Troubleshooting](installation.md#troubleshooting)

**Can't install LevelDB?**
→ Use SQLite backend (beta): Change `.hg` to `.db`

**Import errors?**
→ Make sure you're in virtual environment and ran `pip install -e .`

**Need help?**
→ Check [Installation](installation.md) and [Quick Start](quickstart.md)

## Resources

### This Fork
- [Installation Guide](installation.md)
- [Quick Start](quickstart.md)
- [Features](features.md)
- [Examples](../examples/)

### Original Graphbrain
- [Official Docs](http://graphbrain.net)
- [Paper](https://graphbrain.net/overview.html#publications)

## What's Next?

**New users:**
1. ✅ [Install](installation.md) LevelDB
2. ✅ Try [Quick Start](quickstart.md)
3. ✅ Run [examples](../examples/)

**LLM developers:**
1. ✅ Read [Features](features.md#1-simple-api-for-llms)
2. ✅ Check [API Reference](api-reference.md)
3. ✅ See [example JSON](../examples/foundation_pack_example.json)

**Existing Graphbrain users:**
1. ✅ Read [Features](features.md#migration-guide)
2. ✅ Your code still works! (100% compatible)
3. ✅ Try new API when ready

## Contributing

Pull requests welcome. For major changes, open an issue first.

## Credits

- **Original Graphbrain:** Telmo Menezes et al.
- **This Fork:** LLM integration & installation improvements
- **Funding:** CNRS and ERC Socsemics (#772743)

## License

[MIT](https://choosealicense.com/licenses/mit/) - Same as original Graphbrain
