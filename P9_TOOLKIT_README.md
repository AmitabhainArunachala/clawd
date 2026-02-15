# P9 Standalone Toolkit

Three standalone scripts for deploying P9 indexer on any VPS (AGNI, RUSHABDEV, etc.)

## Files

| File | Purpose | Dependencies |
|------|---------|--------------|
| `p9_index.py` | Index workspace into SQLite + FTS5 | sqlite3 (stdlib) |
| `p9_search.py` | CLI query tool | sqlite3 (stdlib) |
| `p9_nats_bridge.py` | NATS service for remote search | nats-py (pip install) |

## Quick Start

### 1. Index Your Workspace

```bash
python3 p9_index.py /path/to/workspace --db unified_memory.db
```

**Output:**
- Creates `unified_memory.db` (SQLite with FTS5 full-text search)
- Indexes all `.md`, `.py`, `.js`, `.txt`, etc. files
- Incremental updates (only re-indexes changed files)

**Example:**
```bash
# On AGNI VPS
python3 p9_index.py /home/openclaw/workspace --db agni_memory.db

# Result
✓ Database initialized: agni_memory.db
🔍 Indexing: /home/openclaw/workspace
  ... 100 files processed
  ... 200 files processed
✓ Indexing complete:
  Total indexed: 20456
  Updated: 1523
  Database total: 20456 documents
```

### 2. Search Locally

```bash
python3 p9_search.py "your query" --db agni_memory.db
```

**Options:**
```bash
# Top 5 results
python3 p9_search.py "R_V Layer 27" --top-k 5

# No snippets (faster)
python3 p9_search.py "context" --no-snippets

# Database stats
python3 p9_search.py --stats
```

**Example Output:**
```
🔍 Searching: "R_V Layer 27"
📁 Database: agni_memory.db

================================================================================
Found 3 result(s)
================================================================================

1. [EXACT] R_V Causal Validation — Layer 27 Analysis
   Path: /home/openclaw/workspace/research/rv_l27.md
   Score: 0.52 | Size: 15234 bytes
   Snippet: ...the geometric signature of recursive self-observation at Layer 27 (84% depth) shows R_V contraction with Cohen's d = -5.57...

2. [HIGH] Mechanistic Interpretability Findings
   Path: /home/openclaw/workspace/mech_interp/findings.md
   Score: 2.15 | Size: 8932 bytes
   Snippet: ...comparing Layer 27 activations across architectures reveals consistent R_V patterns...
```

### 3. Run NATS Bridge

**Install dependency:**
```bash
pip install nats-py
```

**Run bridge:**
```bash
python3 p9_nats_bridge.py --db agni_memory.db --node-name agni
```

**Output:**
```
🚀 P9 NATS Bridge starting...
   Node: agni
   Database: agni_memory.db
   NATS: nats://localhost:4222

✓ Bridge operational. Waiting for requests...
   Example: nats request agni.memory.search '{"query": "test"}'
```

**Test from another node:**
```bash
# From Mac or RUSHABDEV
nats request agni.memory.search '{"query": "R_V", "top_k": 5}'
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Mac (DC)      │     │  AGNI (Factory) │     │ RUSHABDEV       │
│                 │     │                 │     │                 │
│  p9_index.py    │     │  p9_index.py    │     │  p9_index.py    │
│  ├─ PSMV        │     │  ├─ workspace/  │     │  ├─ SAB code    │
│  ├─ mech-interp │     │  └─ 20K files   │     │  └─ 2K files    │
│  └─ DGC         │     │                 │     │                 │
│                 │◄────┤  p9_nats_bridge │◄────┤                 │
│  UnifiedMemory  │     │  └─ NATS        │     │  (can query     │
│  class          │ NATS│                 │ NATS│   AGNI/Mac)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Integration with OpenClaw

**Extend OpenClaw's memory_search to use P9:**

```python
# In OpenClaw skill or agent
import subprocess
import json

def memory_search(query, node="all"):
    """Search across all P9 instances via NATS"""
    results = []
    
    # Query local P9
    if node in ["mac", "all"]:
        local = subprocess.run(
            ["python3", "p9_search.py", query, "--top-k", "10"],
            capture_output=True, text=True
        )
        results.extend(parse_results(local.stdout))
    
    # Query remote P9 via NATS
    if node in ["agni", "all"]:
        remote = subprocess.run(
            ["nats", "request", "agni.memory.search", 
             json.dumps({"query": query, "top_k": 10})],
            capture_output=True, text=True
        )
        results.extend(json.loads(remote.stdout)["results"])
    
    return merge_and_rank(results)
```

## Command Reference

### p9_index.py

```bash
# Basic usage
python3 p9_index.py /path/to/workspace

# Custom database
python3 p9_index.py /path/to/workspace --db /custom/path.db

# Re-index (incremental)
python3 p9_index.py /path/to/workspace --db existing.db
```

### p9_search.py

```bash
# Search
python3 p9_search.py "query"

# Options
--db PATH        # Database path
--top-k N        # Number of results (default: 10)
--no-snippets    # Faster, no text extraction
--stats          # Show database statistics
```

### p9_nats_bridge.py

```bash
# Run with NATS
python3 p9_nats_bridge.py --db agni_memory.db --node-name agni

# Environment variables
export NATS_URL="nats://localhost:4222"
export NODE_NAME="agni"
python3 p9_nats_bridge.py

# Test mode (no NATS)
python3 p9_nats_bridge.py --db agni_memory.db --test-mode
```

## Deployment Checklist (AGNI)

- [ ] Copy `p9_index.py`, `p9_search.py`, `p9_nats_bridge.py` to AGNI VPS
- [ ] Run: `python3 p9_index.py /home/openclaw/workspace --db agni_memory.db`
- [ ] Test: `python3 p9_search.py "test" --db agni_memory.db`
- [ ] Install: `pip install nats-py`
- [ ] Run bridge: `python3 p9_nats_bridge.py --db agni_memory.db --node-name agni`
- [ ] Test from Mac: `nats request agni.memory.search '{"query": "test"}'`

## Troubleshooting

**"Database not found"**
→ Run `p9_index.py` first to create the database

**"nats-py not installed"**
→ Run `pip install nats-py` or use `--test-mode`

**"NATS connection refused"**
→ Check NATS is running: `nats server check`
→ Verify URL: `--nats nats:// correct-host:4222`

**Slow indexing**
→ Normal for first run (20K files = ~5 minutes)
→ Incremental updates are fast (<1 minute)

## Performance

- **Indexing:** ~1000 files/minute (depends on file size)
- **Search:** <50ms for typical queries (FTS5)
- **Database size:** ~3MB per 1000 files (text only)
- **Memory:** ~50MB RAM for searcher

## License

Same as DHARMIC_GODEL_CLAW — ISC License

---

Built for AGNI VPS deployment | 2026-02-15
