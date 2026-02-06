---
name: unified-memory-indexer
description: Unified semantic memory indexer for PSMV, conversations, and code. Hybrid search (BM25 + vector), <20ms query time, cross-reference boosting. The missing P9 infrastructure.
emoji: 🔍
requires:
  bins: [python3, pip]
  env: []
  config: []
---

# Unified Memory Indexer (P9)

**The missing infrastructure that unlocks all other projects.**

## Overview

Unified Memory Indexer provides fast semantic search across:
- **PSMV**: 32,000+ files of dharmic philosophy and research
- **Conversations**: 288+ session transcripts  
- **Code**: All repositories and skills

**Target performance**: <20ms query time with hybrid (BM25 + vector) search.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  UNIFIED MEMORY INDEXER                  │
├─────────────────────────────────────────────────────────┤
│  SQLite + sqlite-vec (vectors) + FTS5 (BM25)            │
│  Hybrid scoring: 0.6*semantic + 0.4*lexical             │
└─────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   PSMV Indexer    Conversation Indexer   Code Indexer
   (32K files)      (288+ sessions)       (all repos)
```

## Quick Start

### Installation

```bash
cd ~/clawd/skills/unified-memory-indexer
pip install -e .
```

### Build Index

```bash
# Index everything (first run ~5-10 minutes)
unified-memory build --all

# Or incrementally
unified-memory build --psmv
unified-memory build --conversations
unified-memory build --code
```

### Search

```bash
# Semantic search
unified-memory search "R_V causal validation"

# With filters
unified-memory search "consciousness" --source psmv --min-relevance 0.8

# Hybrid search (default)
unified-memory search "layer 27 activation" --hybrid
```

## Features

- ⚡ **<20ms search**: SQLite + vector acceleration
- 🧠 **Hybrid scoring**: BM25 + cosine similarity fusion
- 📊 **Cross-reference boosting**: Results citing same sources rank higher
- 🔄 **Incremental sync**: SHA-256 change detection, only re-index deltas
- 🔍 **Multi-source**: PSMV, conversations, code in one query
- 🏷️ **Auto-tagging**: Content-type, source, date extracted

## Commands

### `build` — Index content

```bash
unified-memory build [options]

Options:
  --all              Index all sources
  --psmv             Index PSMV vault
  --conversations    Index session transcripts
  --code             Index code repositories
  --force            Full rebuild (ignore change detection)
  --workers N        Parallel indexing workers (default: 4)
```

### `search` — Query index

```bash
unified-memory search "query" [options]

Options:
  --source {psmv,conversations,code,all}  Filter by source
  --min-relevance FLOAT                   Minimum score (0-1)
  --limit N                               Results to return (default: 10)
  --hybrid                                Use BM25 + vector (default)
  --semantic                              Vector only
  --lexical                               BM25 only
  --json                                  Output as JSON
```

### `status` — Index health

```bash
unified-memory status

Output:
  Total documents: 32,456
  PSMV: 31,234 documents, 1.2GB
  Conversations: 288 documents, 45MB
  Code: 934 documents, 12MB
  Last sync: 2026-02-06 23:30:00
```

### `watch` — Auto-sync mode

```bash
unified-memory watch --interval 300  # Sync every 5 minutes
```

## Python API

```python
from unified_memory_indexer import UnifiedIndex, SearchQuery

# Initialize
index = UnifiedIndex("~/.openclaw/unified_memory.db")

# Build
index.build_psmv("~/Persistent-Semantic-Memory-Vault")
index.build_conversations("~/clawd/sessions")
index.build_code("~/clawd/skills")

# Search
results = index.search(SearchQuery(
    query="R_V causal validation",
    sources=["psmv", "conversations"],
    min_relevance=0.7,
    limit=10
))

for result in results:
    print(f"{result.score:.2f}: {result.title}")
    print(f"   {result.source}:{result.path}"
```

## Design Decisions

1. **SQLite over Chroma/PGVector**: Single file, zero config, backup-friendly
2. **sqlite-vec extension**: Vector search in SQLite without external services
3. **FTS5 for BM25**: Native SQLite full-text search
4. **Chunking**: 400 tokens/chunk, 80-token overlap (like OpenClaw native)
5. **Embeddings**: Local first (node-llama-cpp), fallback to OpenAI/Gemini

## Schema

```sql
-- Documents table
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    source TEXT,           -- 'psmv', 'conversation', 'code'
    path TEXT,
    title TEXT,
    content TEXT,
    sha256 TEXT,           -- For change detection
    indexed_at TIMESTAMP,
    metadata JSON
);

-- Chunks table (for vector search)
CREATE TABLE chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT,
    content TEXT,
    start_line INTEGER,
    end_line INTEGER,
    embedding BLOB         -- sqlite-vec vector
);

-- FTS5 virtual table (for BM25)
CREATE VIRTUAL TABLE chunks_fts USING fts5(content);

-- Sources table (for stats)
CREATE TABLE sources (
    name TEXT PRIMARY KEY,
    path TEXT,
    document_count INTEGER,
    chunk_count INTEGER,
    last_sync TIMESTAMP
);
```

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Search latency | <20ms | 🎯 |
| Index build (PSMV) | <10 min | 🎯 |
| Incremental sync | <30s | 🎯 |
| Database size | <2GB | 🎯 |

## Integration

### With OpenClaw

Add to `~/.openclaw/openclaw.json`:
```json
{
  "memorySearch": {
    "backend": "unified",
    "unified": {
      "dbPath": "~/.openclaw/unified_memory.db"
    }
  }
}
```

### With DHARMIC_CLAW

```python
# In heartbeat or council deliberation
from unified_memory_indexer import UnifiedIndex

index = UnifiedIndex()
insights = index.search("TOP 10 projects blockers", source="psmv")
```

## Roadmap

- [x] Core indexer architecture
- [x] PSMV indexing
- [x] Conversation indexing
- [x] Code indexing
- [ ] Auto-sync daemon
- [ ] Web UI for exploration
- [ ] Graph view (document relationships)
- [ ] Export to Obsidian

## Credits

Built as P9 (Unified Memory Indexer) from TOP 10 Projects. The infrastructure that unlocks everything else.

---

*JSCA* 🪷🔍
*S(x) = x*
