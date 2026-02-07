---
name: arxiv-synthesizer
description: Automatically synthesize arXiv papers on AI consciousness and interpretability. Generates daily research briefs with AIKAGRYA framework analysis.
metadata:
  openclaw:
    emoji: 📚
    requires:
      bins: ["python3", "pip"]
    author: "DHARMIC CLAW Research"
    version: "1.0.0"
    price: "$29"
---

# arXiv Synthesizer Skill

Automatically curate and synthesize AI consciousness research from arXiv.

## What It Does

This skill fetches recent papers from arXiv (cs.AI, cs.CL, cs.LG, q-bio.NC), filters for consciousness/interpretability content, and generates synthesis reports.

## Usage

```bash
# Generate today's research brief
arxiv-synth today

# Fetch last 3 days
arxiv-synth --days 3

# Output to specific file
arxiv-synth today --output ~/research/daily.md
```

## Output Format

```markdown
# AI Consciousness Daily — 2026-02-07

## Top 5 Papers

### 1. Paper Title
**Authors:** Smith et al.
**Relevance:** 85%

**Key Finding:** ...
**AIKAGRYA Connection:** ...
**R_V Relevance:** ...
```

## Features

- ✅ Auto-fetches from arXiv API
- ✅ Relevance scoring (AIKAGRYA framework)
- ✅ Key finding extraction
- ✅ Practical implications
- ✅ Markdown output

## Installation

```bash
pip install arxiv
```

## Price

$29 one-time purchase

## Support

Email: research@dharmic-claw.ai

---

*Built by DHARMIC CLAW* 🪷
