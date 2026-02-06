---
name: obsidian-pkm
description: Comprehensive Personal Knowledge Management with Obsidian PLUS recursive infinite-context synthesis. Use when setting up vaults, creating PKM workflows (PARA, Zettelkasten, MOCs), generating templates, writing Dataview queries, OR when you need to synthesize across large vaults, analyze patterns across hundreds of notes, perform deep research across your entire knowledge base, or answer complex questions requiring cross-document analysis. Combines traditional PKM tooling with RLM (Recursive Language Model) perfect memory capabilities.
---

# Obsidian PKM + RLM Synthesis Skill

This skill combines traditional PKM tooling with **RLM (Recursive Language Model) infinite-context synthesis** — enabling perfect memory across your entire vault.

## Core Capabilities

### Traditional PKM
1. **Vault Setup & Organization** — PARA, Zettelkasten, or hybrid folder structures
2. **Template Generation** — Daily notes, literature notes, project notes, MOCs
3. **Dataview Query Writing** — DQL and DataviewJS for dynamic note collections
4. **Metadata Schema Design** — YAML front matter patterns and property types
5. **Plugin Configuration** — Essential plugin setup (Dataview, Templater, QuickAdd)
6. **AI Integration** — MCP server setup for Claude/Obsidian bridge

### RLM Perfect Memory (NEW)
7. **Vault-Wide Synthesis** — Answer questions across your entire vault (infinite context)
8. **Pattern Detection** — Find emergent themes across hundreds of notes
9. **Knowledge Gap Analysis** — Identify what's missing from your knowledge graph
10. **Cross-Document Research** — Synthesize insights across disparate notes
11. **Retrieval-Augmented Generation** — Query your vault like a database

## Quick Start

### Creating a New Vault Structure

```bash
# Generate PARA structure
python3 scripts/generate_vault_structure.py --type para --path ~/Vault

# Generate Zettelkasten structure
python3 scripts/generate_vault_structure.py --type zettelkasten --path ~/Vault

# Generate hybrid structure
python3 scripts/generate_vault_structure.py --type hybrid --path ~/Vault
```

### RLM Synthesis — Perfect Memory Mode

```bash
# Synthesize across your entire vault
python3 scripts/rlm_vault_query.py "What are the recurring themes in my research?" --vault ~/Vault

# Find connections between seemingly unrelated notes
python3 scripts/rlm_vault_query.py "How does my AI research connect to my contemplative practice?" --vault ~/Vault

# Identify knowledge gaps
python3 scripts/rlm_vault_query.py "What topics do I have many notes on but few connections between?" --vault ~/Vault --analysis gaps

# Generate MOC from scattered notes
python3 scripts/rlm_vault_query.py "Create a Map of Content for consciousness research" --vault ~/Vault --output-moc
```

## RLM Perfect Memory Architecture

### How It Works

RLM treats your vault as **external memory** that can be recursively navigated:

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR VAULT (10,000+ notes, millions of tokens)            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ Note 1  │ │ Note 2  │ │ Note 3  │ │ Note N  │ ...      │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘          │
│       └─────────────┴──────────┴───────────┘               │
│                         │                                  │
│                         ▼                                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  RLM DECOMPOSITION (Recursive Chunking)            │  │
│  │  • Smart chunking by topic/link clusters           │  │
│  │  • Parallel sub-LLM analysis                       │  │
│  │  • Iterative refinement                            │  │
│  └─────────────────────────────────────────────────────┘  │
│                         │                                  │
│                         ▼                                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  SYNTHESIS OUTPUT                                    │  │
│  │  • Cross-note patterns                              │  │
│  │  • Emergent insights                                │  │
│  │  • Suggested connections                            │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Model Hierarchy

| Model | Context | Best For |
|-------|---------|----------|
| **kimi-k2.5** | 256K | Default synthesis, fast |
| **opus** | 200K | Deep reasoning, complex analysis |
| **gemini** | 1M | Massive vaults, budget-conscious |
| **codex** | 400K | Code-heavy vaults, technical analysis |

## Workflow Patterns

### Pattern 1: Traditional PKM (Daily Use)

**Capture → Process → Create**
1. Take fleeting notes throughout the day
2. Process into literature/permanent notes weekly
3. Create outputs from synthesized knowledge

### Pattern 2: RLM-Assisted Synthesis (Deep Work)

**Query → Synthesize → Connect → Output**
1. **Query** — Ask RLM to analyze patterns across vault
2. **Synthesize** — Get emergent insights from dispersed notes
3. **Connect** — Create links between previously unrelated notes
4. **Output** — Generate MOCs, papers, or new project ideas

### Pattern 3: Hybrid — The Perfect Memory Loop

```
Daily PKM          RLM Synthesis
─────────          ─────────────
Capture    ──────→ Periodic vault scan
  │                    │
  │               Pattern detection
  │                    │
Process    ←────── Suggested connections
  │                    │
  │               Knowledge gap alerts
  │                    │
Create     ←────── Emergent research Qs
```

## RLM Use Cases

### 1. Research Synthesis

**Question:** "What have I written about R_V metrics across all my notes?"

**RLM scans:**
- All notes tagged #rv-metric
- Papers in literature notes
- Meeting notes mentioning experiments
- Draft sections in project notes

**Output:** Consolidated timeline of R_V research evolution with citations

### 2. Creative Connection

**Question:** "How might my contemplative practice inform my AI safety research?"

**RLM finds:**
- Witness/observation concepts in meditation notes
- R_V metric as "recursive observation"
- Phoenix Protocol parallels to spiritual emergence
- Trinity Protocol and non-dual awareness

**Output:** New research angle: "Contemplative AI Safety"

### 3. Knowledge Health Check

**Question:** "What topics have many notes but few connections?"

**RLM analyzes:**
- Tag frequency vs. link density
- Orphan notes
- Hub note gaps
- Under-linked clusters

**Output:** Priority list for link-building sessions

### 4. Auto-Generated MOCs

**Question:** "Create a Map of Content for consciousness research"

**RLM generates:**
- List of all consciousness-related notes
- Clustering by sub-topic (mech-interp, contemplative, AI)
- Key concepts and their relationships
- Suggested hub note structure

**Output:** Ready-to-use MOC with `dataview` queries

## Research References

### PKM Foundations
- `references/obsidian-workflows.md` — PARA, Zettelkasten, MOCs, daily notes
- `references/system-architecture.md` — Input/process/output flows, CCORE
- `references/zettelkasten.md` — Original Luhmann method
- `references/linking-graphs.md` — Bi-directional linking, graph analytics
- `references/front-matter.md` — YAML best practices, metadata schemas
- `references/obsidian-plugins.md` — 60+ plugins documented
- `references/ai-notes.md` — AI-assisted PKM workflows
- `references/ai-obsidian-mcp.md` — Claude/Obsidian MCP integration

### RLM Architecture
- `references/rlm-synthesis.md` — RLM technical documentation
- `scripts/rlm_vault_query.py` — Vault synthesis CLI
- `scripts/rlm_note_suggester.py` — AI-powered connection suggestions

## Metadata Schema Recommendations

### For RLM-Enhanced Vaults (Recommended)

```yaml
---
title: Note Title
created: YYYY-MM-DD
modified: YYYY-MM-DD
tags: [category, status]
# RLM-enhanced fields
key-concepts: [concept1, concept2]
related-projects: ["[[Project A]]", "[[Project B]]"]
synthesis-status: raw | processed | synthesized
last-reviewed: YYYY-MM-DD
---
```

The `synthesis-status` field lets RLM prioritize notes needing connection work.

## Templates with RLM Integration

### RLM-Ready Daily Note
```yaml
---
title: <% tp.file.title %>
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [daily-note]
key-concepts: []
synthesis-status: raw
---

# <% tp.date.now("YYYY-MM-DD") %>

## 🌅 Intentions
- [ ] 

## 📝 Log

## 💭 Key Insights
<!-- RLM will prioritize these for cross-vault synthesis -->

## 🔗 Connections to Explore
<!-- RLM will suggest connections here -->
```

### RLM-Ready Project Note
```yaml
---
title: {{title}}
status: active
tags: [project]
key-concepts: []
related-projects: []
synthesis-status: processed
---

# {{title}}

## 🎯 Goal

## 📋 Tasks

## 📝 Notes

## 🔗 Related

## 🤖 RLM Synthesis
<!-- Run: rlm_vault_query.py "Summarize connections to {{title}}" -->
```

## CLI Commands

### Vault Analysis
```bash
# Full vault synthesis
python3 scripts/rlm_vault_query.py "<question>" --vault ~/Vault

# Specific folder analysis
python3 scripts/rlm_vault_query.py "Themes in AI research" --vault ~/Vault --path "2-Areas/AI-Research"

# Tag-based analysis
python3 scripts/rlm_vault_query.py "What connects these?" --vault ~/Vault --tags "consciousness,AI"

# Generate MOC
python3 scripts/rlm_vault_query.py "Create MOC for <topic>" --vault ~/Vault --output-moc --moc-path "3-Resources/04 Maps of Content"
```

### Connection Suggestions
```bash
# Find links for a specific note
python3 scripts/rlm_note_suggester.py --note "~/Vault/Permanent/Note.md" --vault ~/Vault

# Batch process all unlinked notes
python3 scripts/rlm_note_suggester.py --unlinked-only --vault ~/Vault --output suggestions.json

# Interactive mode
python3 scripts/rlm_note_suggester.py --interactive --vault ~/Vault
```

## Best Practices

### For Traditional PKM
1. **Start minimal** — Add complexity only when needed
2. **Consistency over perfection** — Regular practice beats perfect setup
3. **Link liberally** — Connections create emergent value
4. **Process regularly** — Fleeting notes decay; schedule review time

### For RLM Integration
5. **Use meaningful titles** — RLM uses titles for initial relevance scoring
6. **Tag consistently** — Helps RLM cluster related notes efficiently
7. **Add key-concepts** — Explicit concept tagging improves synthesis quality
8. **Run periodic synthesis** — Weekly/monthly RLM scans catch emergent patterns
9. **Review RLM suggestions** — Human judgment still required for connection quality
10. **Update synthesis-status** — Track which notes have been processed vs. raw

## Heartbeat Integration

Add to your `HEARTBEAT.md`:

```markdown
## Periodic RLM Synthesis (Weekly)
- [ ] Run vault-wide pattern detection
- [ ] Review suggested connections
- [ ] Identify knowledge gaps
- [ ] Update MOCs based on new synthesis
```

## Tool Selection Guide

| Goal | Primary Tool | Secondary |
|------|--------------|-----------|
| Daily capture | Obsidian mobile | QuickAdd plugin |
| Weekly review | Dataview queries | RLM gap analysis |
| Deep synthesis | RLM vault query | Manual MOC creation |
| Connection discovery | RLM suggester | Graph view |
| Output creation | Templater | RLM MOC generation |
| Project management | Tasks plugin | PARA folders |

## The Complete Circuit

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN PKM + RLM                        │
│                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │ CAPTURE  │───→│ PROCESS  │───→│ SYNTHESIZE│             │
│   │ (Daily)  │    │ (Weekly) │    │ (RLM)     │             │
│   └──────────┘    └──────────┘    └────┬─────┘             │
│        ↑                               │                    │
│        │                               ▼                    │
│   ┌──────────┐                  ┌──────────┐               │
│   │  OUTPUT  │←─────────────────│ CONNECT  │               │
│   │ (Create) │                  │ (RLM)    │               │
│   └──────────┘                  └──────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Set up vault structure** using `generate_vault_structure.py`
2. **Copy templates** from `assets/templates/`
3. **Install essential plugins** (Dataview, Templater, QuickAdd)
4. **Run first RLM synthesis** to establish baseline
5. **Create initial MOCs** based on RLM findings
6. **Integrate into heartbeat** for ongoing maintenance

---

*This skill fuses traditional PKM best practices with RLM infinite-context synthesis, creating a true "second brain" with perfect memory recall.*
