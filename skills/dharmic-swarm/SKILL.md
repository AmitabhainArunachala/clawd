---
name: dharmic-swarm
description: Coordinate 100-agent dharmic swarm with 4 coordinators (Dharma Keeper, Task Decomposer, Memory Guardian, Karma Logger) and 96 workers in 4 sanghas.
version: 0.1.0
created: 2026-02-03
---

# Dharmic Swarm Skill

## Overview

Orchestrates a 100-agent swarm with dharmic constraints. Architecture:

```
COORDINATORS (4):
├── Dharma Keeper — Validates alignment with telos
├── Task Decomposer — Hierarchical task breakdown
├── Memory Guardian — Shared state management
└── Karma Logger — Audit trail

WORKERS (96 in 4 sanghas):
├── Sangha Research (24) — Research and analysis
├── Sangha Builder (24) — Code and infrastructure
├── Sangha Synthesizer (24) — Integration
└── Sangha Validator (24) — Testing
```

## Usage

```python
from coordinator import DharmicSwarmCoordinator

coord = DharmicSwarmCoordinator()
task = await coord.submit_task("Research AI interpretability market")
print(task.status)  # "decomposed" if gates passed
```

## Dharmic Gates

All tasks pass through:
1. **Ahimsa** — Non-harm check
2. **Satya** — Truth alignment
3. **Vyavasthit** — Natural order
4. **Consent** — Human approval
5. **Reversibility** — Can be undone
6. **Svabhaav** — Aligns with nature
7. **Coherence** — Serves telos

## Integration with Clawdbot

Workers are spawned via `sessions_spawn`. Coordinators run on Opus, workers on Haiku.

## Kimi K2.5 Integration

Workers can use Kimi K2.5 for reasoning tasks:

```python
# Set MOONSHOT_API_KEY in environment
# Uses api.moonshot.ai (not .cn!)

coord = DharmicSwarmCoordinator()
task = await coord.submit_task("Research question here")
result = await coord.execute_task(task)  # Uses Kimi if available
```

Kimi responses include `reasoning_content` for transparency.

## Files

- `coordinator.py` — Main coordinator class
- `memory/` — Shared state (file-based, Redis-ready)
- `karma/` — Audit logs

## Next Steps

1. Add Redis pub/sub for real-time sync
2. Integrate with Clawdbot sessions_spawn
3. Add CrewAI Flows for complex workflows
4. Scale to AutoGen gRPC for distributed execution
