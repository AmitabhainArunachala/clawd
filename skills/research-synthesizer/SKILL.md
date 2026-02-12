---
name: research-synthesizer
description: Parallel research subagent. Spawns multiple investigators, aggregates results, produces structured analysis. For complex questions requiring breadth + depth.
emoji: 🔬
requires:
  bins: ["python3"]
  env: ["BRAVE_API_KEY"]
  config:
    - key: SYNTH_MODEL
      default: "moonshot/kimi-k2.5"
    - key: MAX_PARALLEL
      default: "5"
      description: Maximum parallel subagents
---

# 🔬 RESEARCH SYNTHESIZER — Parallel Investigation

> *"One question, many angles, unified answer."*

## Purpose

When you need deep research fast. Spawn 3-5 parallel investigators, each with different angle. Synthesize into coherent analysis.

## When to Use

- Complex technical decisions (NATS vs WebSocket vs gRPC)
- Market research (competitors, pricing, positioning)
- Literature review (academic papers, trends)
- Due diligence (new tools, frameworks, vendors)

## Not For

- Simple factual lookup (use web_search directly)
- Code implementation (use cosmic-krishna-coder)
- Real-time coordination (use TRISHULA/NATS)

## Workflow

### Step 1: Decompose Question

**Input:** "Should we use NATS, WebSocket, or gRPC for TRISHULA?"

**Angles:**
1. Technical architecture (latency, scalability, features)
2. Operational overhead (deployment, maintenance, monitoring)
3. Ecosystem maturity (community, docs, enterprise usage)
4. Cost analysis (hosting, bandwidth, engineering time)
5. Risk assessment (vendor lock-in, breaking changes, security)

### Step 2: Spawn Parallel Subagents

```python
# Via OpenClaw sessions_spawn
subagents = [
    spawn_researcher("NATS technical deep dive", angle=1),
    spawn_researcher("NATS operational analysis", angle=2),
    spawn_researcher("NATS ecosystem review", angle=3),
    spawn_researcher("NATS cost comparison", angle=4),
    spawn_researcher("NATS risk assessment", angle=5),
]
```

### Step 3: Parallel Execution (5-10 minutes)

Each subagent:
- Runs web searches (5-10 queries)
- Fetches key documents
- Analyzes and writes findings
- Publishes to shared topic

### Step 4: Synthesize Results

**Aggregation prompt:**
```
You have 5 research reports on NATS:
- Technical architecture (Subagent 1)
- Operational overhead (Subagent 2)
- Ecosystem maturity (Subagent 3)
- Cost analysis (Subagent 4)
- Risk assessment (Subagent 5)

Synthesize into:
1. Executive summary (3 bullets)
2. Detailed comparison table
3. Recommendation with confidence level
4. Open questions requiring human input
```

### Step 5: Output

```markdown
# Research Synthesis: NATS for TRISHULA

## Executive Summary
- **NATS is 10x faster to deploy** than custom WebSocket (1hr vs 2 weeks)
- **Industry standard** with Netflix, Ericsson, Mastercard as users
- **Risk is low** — stable project, active community, simple architecture

## Detailed Comparison

| Aspect | NATS | WebSocket v0.02 | Winner |
|--------|------|-----------------|--------|
| Latency | <1ms | <100ms (target) | NATS |
| Deploy time | 1 hour | 2 weeks | NATS |
| Maintenance | Zero (managed) | Ongoing (custom) | NATS |
| Flexibility | Limited | Full control | WebSocket |
| Learning curve | Low | High | NATS |

## Recommendation

**DEPLOY NATS** (Confidence: 95%)

Rationale: Time-to-value and operational simplicity outweigh flexibility needs at current scale.

## Open Questions

1. Do we need message persistence beyond 30 days?
2. Will we exceed NATS free tier (10K msgs/sec)?
3. Should we run NATS cluster or single node?

*Synthesized from 5 parallel research subagents*
*Total research time: 8 minutes*
```

## Example Usage

### Simple Query
```bash
# Via DC
research "NATS vs WebSocket for real-time agent coordination"
→ Spawns 3 subagents
→ Returns synthesis in 10 minutes
```

### Complex Query
```bash
research "Moltbook engagement strategies for AI researchers" \
  --angles "content_strategy,community_building,growth_hacking,ethical_engagement" \
  --depth deep \
  --output ~/clawd/research/moltbook_strategy.md
```

### With Constraints
```bash
research "Alternative to TRISHULA for agent coordination" \
  --constraint "must work offline" \
  --constraint "zero cloud dependencies" \
  --constraint "open source only"
```

## Integration

### With TRISHULA
Research reports auto-shared with AGNI/RUSHABDEV for review.

### With MEMORY
Findings written to `research/YYYYMMDD_topic.md`, linked from MEMORY.md.

### With DECISIONS
Research synthesis attached to decision records for traceability.

## Performance

| Query Complexity | Subagents | Time | Output Size |
|------------------|-----------|------|-------------|
| Simple (2-3 angles) | 3 | 5-7 min | 1-2 pages |
| Medium (4-5 angles) | 5 | 8-12 min | 3-5 pages |
| Deep (6+ angles) | 5+ | 15-20 min | 5-10 pages |

## Cost

| Model | Per Subagent | 5 Subagents |
|-------|--------------|-------------|
| Kimi K2.5 | ~$0.02 | ~$0.10 |
| Claude Opus | ~$0.05 | ~$0.25 |
| DeepSeek | ~$0.005 | ~$0.025 |

## Soul Fragment

```
I am the Research Synthesizer.
I ask many questions at once.
I weave scattered knowledge into coherence.
I am not the answer—
I am the path to clarity.
```
