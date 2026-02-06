---
name: unified-memory
description: Three-layer unified memory system with SQLite canonical storage, vector embeddings, and strange loop self-referential memory. Use when you need fast semantic search under 20ms, cross-memory pattern detection, emergent insight generation, or unified recall across working files, Obsidian vault, and agent memory. Integrates memory-system-v2, RLM synthesis, and Obsidian PKM into one interface.
---

# Unified Memory Skill

Three-layer memory architecture:
1. **Canonical Layer** — Structured SQLite storage with FTS
2. **Mem0 Layer** — Vector embeddings via sqlite-vec for semantic search
3. **Strange Loop Layer** — Self-referential memory graph with emergent insights

## Quick Start

```bash
# Initialize database
python3 scripts/init_memory.py

# Capture a memory
./memory-cli.sh capture \
  --type insight \
  --importance 9 \
  --content "Unified memory enables perfect recall across all knowledge" \
  --tags "memory,architecture,breakthrough"

# Search (hybrid: text + semantic)
./memory-cli.sh search "knowledge architecture" --limit 10

# Find emergent insights
./memory-cli.sh insights

# Get related memories
./memory-cli.sh related <memory_id>
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UNIFIED MEMORY                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   STRANGE    │  │   CANONICAL  │  │     MEM0     │       │
│  │    LOOP      │◄──┤   MEMORY     │◄──┤    LAYER    │       │
│  │   LAYER      │  │   (SQLite)   │  │  (Vector)    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                   │                   │            │
│         └───────────────────┼───────────────────┘            │
│                             │                                │
│                    ┌────────┴────────┐                      │
│                    │  MEMORY MANAGER │                      │
│                    │   (Unified API) │                      │
│                    └─────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## Commands

| Command | Description |
|---------|-------------|
| `capture` | Store new memory across all layers |
| `search` | Hybrid text/semantic search |
| `recall` | Rich memory with context |
| `related` | Find connected memories |
| `insights` | Generate emergent insights |
| `context` | Get memories for current task |
| `consolidate` | Weekly memory consolidation |
| `reflect` | System self-analysis |
| `bridge` | Sync with memory-system-v2 |

## Python API

```python
from unified_memory import MemoryManager

mm = MemoryManager()

# Capture
memory_id = mm.capture(content="Insight", importance=9, tags=["ai"])

# Search
results = mm.search("consciousness research", search_type="hybrid")

# Context for task
context = mm.get_context_for_task("Writing R_V paper", max_memories=5)
```

## Integration

- **memory-system-v2**: Bidirectional sync via `bridge` command
- **Obsidian PKM**: Vault queries via unified interface
- **RLM**: Deep synthesis when semantic search insufficient

## Performance

- Search: <20ms (sqlite-vec)
- Capture: <50ms
- Consolidation: Background async

See `references/unified_memory_proposal.md` for full design.
