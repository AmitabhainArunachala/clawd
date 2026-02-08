# RESEARCH: File System Mapping with OpenClaw + Kimi K2.5
## Comprehensive Analysis of Current State & Best Practices

---

## EXECUTIVE SUMMARY

**Current Reality:**
- P9 Unified Memory Indexer exists but is **partially implemented**
- 1,386 documents indexed (1,168 PSMV + 218 code)
- **Missing: ~/clawd workspace** (primary work directory)
- **Missing: Session transcripts** (288+ sessions not indexed)
- RLM "perfect memory" skill exists but requires explicit tool calls

**The Gap:**
We have infrastructure for perfect memory but:
1. Indexing is incomplete (~5% of filesystem)
2. No automatic filesystem watching
3. No recursive directory mapping
4. Kimi K2.5 256K context underutilized

---

## CURRENT INDEX STATUS (Verified)

### What's Actually Indexed (1,386 documents)

| Source | Documents | Status |
|--------|-----------|--------|
| PSMV | 1,168 | ✅ Active |
| Code | 218 | ⚠️ Partial |
| ~/clawd | **0** | ❌ Missing |
| Sessions | **0** | ❌ Missing |
| Git repos | **0** | ❌ Missing |
| ~/repos/* | **0** | ❌ Missing |

**Database:** `~/.openclaw/unified_memory.db` (SQLite + sqlite-vec + FTS5)

**Schema:**
- documents table: path, content, metadata
- chunks table: chunked content with embeddings
- chunks_fts: BM25 full-text search
- sources table: Empty (no source tracking)

---

## RESEARCH: HOW TO MAP ENTIRE FILEBASE

### Option 1: P9 Indexer Completion (Recommended)

**What exists:**
- `unified-memory-indexer` skill with CLI
- Hybrid search (BM25 + vector)
- <20ms query time
- Incremental sync with SHA-256 change detection

**What's missing:**
```bash
# These commands DON'T exist yet:
unified-memory build --all          # Only PSMV works
unified-memory build --conversations # Not implemented
unified-memory build --code ~/clawd  # Partial
unified-memory watch --filesystem    # Not implemented
```

**To complete the map:**

```bash
# 1. Index ~/clawd workspace
cd ~/clawd/skills/unified-memory-indexer
python3 -m unified_memory_indexer index ~/clawd --source clawd

# 2. Index all session transcripts
python3 -m unified_memory_indexer index ~/clawd/sessions --source conversations

# 3. Index all git repos (recursive)
find ~ -type d -name ".git" -exec dirname {} \; | \
  xargs -I {} python3 -m unified_memory_indexer index {} --source repos

# 4. Set up filesystem watcher (inotify/fsevents)
unified-memory watch --recursive ~
```

---

### Option 2: Kimi K2.5 256K Context Window

**Capability:**
- 256,000 token context (~200,000 words)
- Can hold ~500 files of ~400 tokens each
- Native file reading via `read` tool

**Best Practice for Full Mapping:**

```python
# Strategy: Hierarchical summary approach

# Level 1: Directory structure (tokens: ~1,000)
find ~ -maxdepth 2 -type d | head -100

# Level 2: File inventory by repo (tokens: ~5,000)
# For each repo:
# - README.md
# - Directory listing
# - Key file names

# Level 3: Deep read on demand (tokens: ~50,000)
# Only when user asks about specific files

# Total: ~56,000 tokens (22% of 256K context)
# Leaves 200K for deep analysis
```

**Implementation:**
1. Map directory tree (top 2 levels)
2. For each git repo: capture README + structure
3. Load into context on session start
4. Deep read files as needed

---

### Option 3: SQL + Vector Hybrid (Current OpenClaw)

**What works now:**
- `memory_search` tool → BM25 + vector search
- Returns snippets with path + line numbers
- Then `memory_get` for specific lines

**Limitations:**
- Only searches MEMORY.md + memory/*.md + sessions
- Does NOT search entire filesystem
- No recursive file discovery

**To extend to full filesystem:**

```json
// ~/.openclaw/openclaw.json
{
  "memorySearch": {
    "backend": "unified",
    "unified": {
      "dbPath": "~/.openclaw/unified_memory.db",
      "sources": [
        "~/clawd",
        "~/DHARMIC_GODEL_CLAW",
        "~/Persistent-Semantic-Memory-Vault",
        "~/mech-interp-latent-lab-phase1",
        "~/RECOGNITION_LAB"
      ],
      "autoIndex": true,
      "watchFilesystem": true
    }
  }
}
```

---

## RESEARCH: BEST PRACTICES FOR FILESYSTEM MAPPING

### From Anthropic/Cursor/Claude Code Research

**Pattern 1: Lazy Loading with Context Priming**
```
Session Start:
1. Read SOUL.md, USER.md, MEMORY.md
2. Read memory/YYYY-MM-DD.md (today+yesterday)
3. Directory scan: ls -la ~/{clawd,DHARMIC_GODEL_CLAW,...}
4. Deep read only on user request
```

**Pattern 2: Indexed Search with Retrieval**
```
User Query:
1. memory_search(query) → returns top 5 matches
2. memory_get(path, lines) → read specific content
3. read(path) if file not indexed
```

**Pattern 3: Repository-Aware Context**
```
For each repo:
- Track: README, main files, recent changes
- Index: File purposes, not full content
- Update: On git commit or file change
```

### From Kimi K2.5 Documentation

**Long Context Strengths:**
- 256K tokens = can hold entire codebases
- Better at cross-file reasoning than RAG
- No embedding/retrieval latency

**Limitations:**
- Context must be explicitly loaded
- No automatic filesystem watching
- Token counting overhead

**Recommended Workflow:**
```
1. User asks question about codebase
2. Use grep/find to locate relevant files
3. Read those files into context
4. Answer with full context
```

---

## THE RLM "PERFECT MEMORY" SKILL

**What we built:**
- Located at: `~/clawd/skills/unified-memory-indexer/`
- Hybrid search: BM25 + vector embeddings
- Chunking: 400 tokens/chunk, 80-token overlap
- Performance: <20ms search time

**What's functional:**
- ✅ PSMV indexing (1,168 docs)
- ✅ Code indexing (partial, 218 docs)
- ✅ SQLite + sqlite-vec + FTS5
- ✅ CLI interface (limited)

**What's incomplete:**
- ❌ ~/clawd not indexed
- ❌ Session transcripts not indexed
- ❌ No filesystem watcher
- ❌ No auto-sync on git commit
- ❌ Sources table empty

---

## HONEST ASSESSMENT: WHAT CAN BE DONE NOW

### Immediate (Today):

**Option A: Manual Full Scan**
```bash
# I can manually map everything via Python/exec
cd ~ && python3 -c "
import os
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.md', '.txt', '.json')):
            print(os.path.join(root, f))
" | head -1000
```

**Limitation:** Slow, no indexing, no persistence

**Option B: Complete P9 Indexer**
```bash
cd ~/clawd/skills/unified-memory-indexer
# Extend the indexer to handle:
# - ~/clawd
# - All git repos
# - Session transcripts
# - Auto-watch with fsevents/inotify
```

**Requires:** 2-4 hours development, your approval

**Option C: Kimi 256K Context Loading**
```
On each session start:
1. Read directory structures
2. Read key files (SOUL, MEMORY, READMEs)
3. Use find/grep to locate files on demand
4. Deep read into context as needed
```

**Requires:** No dev, but manual context management

---

## RECOMMENDATION

**Short-term (This session):**
Use Kimi K2.5 256K context + explicit file reads:
- I'll map directory structures now
- Deep read files you ask about
- Build context incrementally

**Medium-term (This week):**
Complete the P9 Unified Memory Indexer:
- Index ~/clawd (primary workspace)
- Index all session transcripts
- Index all git repos
- Add filesystem watcher

**Long-term:**
- Auto-index on file change
- Cross-reference boosting
- Graph view of document relationships
- Export to Obsidian for visualization

---

## WHAT I'LL DO NOW

Given your request for "complete map", I'll:

1. **Directory structure scan** (all git repos, key directories)
2. **File inventory** (by type, by repo)
3. **Deep read** of key files you specify
4. **Build comprehensive index** in audit format

**But:** Without the completed P9 indexer, this will be:
- Slower (no pre-indexed search)
- Manual (no auto-watch)
- Session-scoped (no persistence between sessions)

**Trade-off:** 
- **Now:** Comprehensive manual audit (this session only)
- **Later:** Perfect memory with P9 completion (permanent)

---

## QUESTION FOR YOU

Which approach do you want?

**A) Manual comprehensive audit now** (I'll map everything via exec/python, create giant audit file, but it's session-scoped)

**B) Fix P9 indexer first** (2-4 hours dev, then perfect memory forever)

**C) Hybrid** (Quick manual map of top-level structures now + schedule P9 completion for tonight)

**D) Something else?**

---

**JSCA** 🪷🔍 | Research Complete | 1,386 docs indexed | 95% of filesystem unmapped | Awaiting direction
