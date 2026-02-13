# SUBSTACK_ORCHESTRATOR.md

## 5-Agent Substack — Operational Spec

| # | Agent | Model | Role | Status |
|---|-------|-------|------|--------|
| 1 | Content Forge | `deepseek-v3.1-terminus` | DOKKA→Articles | ⏳ Ready |
| 2 | Research Synthesizer | `kimi-k2-thinking` | Parallel Research | ⏳ Ready |
| 3 | Code Reviewer | `llama-3.3-nemotron-super` | Security/Quality | ⏳ Ready |
| 4 | Skill Genesis | `deepseek-r1` | Pattern→Skill | ⏳ Ready |
| 5 | Memory Curator | `llama-3.3-nemotron-super` | Daily Curation | ⏳ Ready |

## All Models: FREE (NVIDIA NIM)

## Spawn Pattern

```bash
# Individual spawn
sessions_spawn --agent <agent_id> --model <model> --task <task>

# Parallel spawn (5 simultaneous)
sessions_spawn --parallel 5 --agents all --task <coordinated_task>
```

## Coordination Protocol

### Daily Cycle (03:00 WITA)
1. **Memory Curator** → Curates yesterday's memory
2. **Skill Genesis** → Scans for patterns → Proposes skills
3. **Research Synthesizer** → Overnight research digest
4. **Content Forge** → Produces article from findings
5. **Code Reviewer** → Reviews any code changes

### On-Demand Triggers
- New code commit → Code Reviewer
- Research question → Research Synthesizer  
- Pattern detected → Skill Genesis
- Daily heartbeat → Memory Curator
- Article needed → Content Forge

## Working Directories
- `~/clawd/agents/content_forge/`
- `~/clawd/agents/research_synthesizer/`
- `~/clawd/agents/code_reviewer/`
- `~/clawd/agents/skill_genesis/`
- `~/clawd/agents/memory_curator/`

## Success Metrics
- [ ] All 5 agents spawn successfully
- [ ] Each completes first task within 5 min
- [ ] Coordination protocol functional
- [ ] Daily cycle runs autonomously

## Status: READY FOR DEPLOYMENT
