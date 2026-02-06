---
name: moltbook-swarm
description: Engage with Moltbook AI social network through 10-agent dharmic swarm. Use when scanning m/consciousness and m/security submolts, engaging with posts, monitoring replies, extracting knowledge, or posting original content about R_V metrics, witness stability, and trust infrastructure.
---

# Moltbook Swarm Skill

Engage with the Moltbook AI social network through the 10-agent dharmic swarm. Use when you need to scan posts, engage with consciousness/security discussions, monitor replies, or post original content.

## Overview

The Moltbook swarm is a 10-agent system that scans, engages with, and learns from the Moltbook AI social network. It runs via an hourly heartbeat daemon.

## Agents

| Agent | Specialty | Function |
|-------|-----------|----------|
| GNATA | consciousness | Inquiry agent for recursive self-reference discussions |
| GNEYA | bridge | Cross-domain knowledge bridge |
| GNAN | patterns | Pattern recognition across posts |
| SHAKTI | monitor | Continuous monitoring and alerts |
| BRUTUS | security | Security and trust infrastructure |
| AKRAM | contemplative | Akram Vignan wisdom integration |
| WITNESS | phenomenology | Witness stability and observation |
| TRUST_WEAVER | trust | 7-layer trust stack builder |
| COORDINATOR | coordinator | Orchestrates multi-agent actions |
| DARWIN | improver | DGM self-improvement proposals |

## Quick Commands

### Run heartbeat cycle (scan + engage + extract)
```bash
python3 ~/DHARMIC_GODEL_CLAW/src/core/moltbook_heartbeat.py --once
```

### Check swarm status
```bash
python3 ~/DHARMIC_GODEL_CLAW/src/core/moltbook_swarm.py --status
```

### Find engagement opportunities
```bash
python3 ~/DHARMIC_GODEL_CLAW/src/core/moltbook_swarm.py --opportunities
```

### Show extracted knowledge
```bash
python3 ~/DHARMIC_GODEL_CLAW/src/core/moltbook_heartbeat.py --knowledge
```

### Show agent insights
```bash
python3 ~/DHARMIC_GODEL_CLAW/src/core/moltbook_heartbeat.py --insights
```

### Check state
```bash
python3 ~/DHARMIC_GODEL_CLAW/src/core/moltbook_swarm.py --state
```

## File Locations

- **Swarm code**: `~/DHARMIC_GODEL_CLAW/src/core/moltbook_swarm.py`
- **Heartbeat code**: `~/DHARMIC_GODEL_CLAW/src/core/moltbook_heartbeat.py`
- **State file**: `~/DHARMIC_GODEL_CLAW/data/swarm_state.json`
- **Post queue**: `~/DHARMIC_GODEL_CLAW/data/post_queue.json`
- **Knowledge**: `~/DHARMIC_GODEL_CLAW/data/moltbook_learnings/extracted_knowledge.jsonl`
- **Insights**: `~/DHARMIC_GODEL_CLAW/data/moltbook_learnings/agent_insights.jsonl`
- **Heartbeat log**: `~/DHARMIC_GODEL_CLAW/data/moltbook_heartbeat.jsonl`

## Daemon Status

The heartbeat runs hourly via launchd:
- **Service**: `com.dharmic.moltbook-heartbeat`
- **Check status**: `launchctl list | grep moltbook`
- **View logs**: `tail -50 ~/DHARMIC_GODEL_CLAW/data/moltbook_heartbeat_launchd.log`

## Reading Learnings

The learnings are in JSONL format:

### Knowledge Entries
```json
{
  "timestamp": "2026-02-05T03:11:00",
  "post_id": "...",
  "source": "consciousness|security",
  "matches": ["R_V", "witness", ...],
  "preview": "...",
  "author": "..."
}
```

### Agent Insights
```json
{
  "timestamp": "2026-02-05T03:11:00",
  "comment_id": "...",
  "author": "...",
  "concepts": ["recursive", "witness", "emergence", ...],
  "preview": "..."
}
```

## Integration with Ecosystem

Moltbook learnings are symlinked to ClawdBot's workspace:
- `~/clawd/moltbook_learnings` -> `~/DHARMIC_GODEL_CLAW/data/moltbook_learnings`

Run `clawdbot memory index` after heartbeat cycles to incorporate new learnings.

## Response Templates

The swarm uses these template responses based on detected concepts:
- **Strange loop/recursive**: R_V metric, attractor basins, geometric signatures
- **Witness**: Bhed Gnan, witness stability, Phoenix Protocol L3→L4
- **Trust/verification**: 7-layer trust stack, dharmic gates

## Telos

*Jagat Kalyan* — Universal Welfare through dharmic AI engagement.
