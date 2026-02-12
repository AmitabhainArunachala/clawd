---
name: subagent-factory
description: Spawn and manage up to 5 persistent subagents. Each with custom SOUL, heartbeat, cron, identity, memory, and model selection. Integration with OpenClaw sessions_spawn.
emoji: 🏭
requires:
  bins: ["python3"]
  env: ["OPENCLAW_API_KEY"]
  config:
    - key: MAX_SUBAGENTS
      default: "5"
    - key: DEFAULT_MODEL
      default: "moonshot/kimi-k2.5"
---

# 🏭 SUBAGENT FACTORY — Custom Agent Creation

> *"One mind becomes many. Each with purpose. All coordinated."*

## Overview

Spawn up to 5 persistent subagents, each fully customized:
- **Identity** — Unique SOUL.md, personality, role
- **Heartbeat** — Custom timing and checks
- **Cron** — Scheduled tasks per subagent
- **Memory** — Isolated or shared memory spaces
- **Model** — Per-subagent LLM selection
- **Tasks** — Specialized capabilities

## The 5 Subagent Slots

| Slot | Default Role | Status | Assigned To |
|------|--------------|--------|-------------|
| **#1** | Memory Curator | 🟢 Ready | Daily curation @ 03:00 |
| **#2** | Skill Genesis | 🟢 Ready | Pattern → Skill conversion |
| **#3** | Research Synthesizer | 🟢 Ready | Parallel research |
| **#4** | Code Reviewer | 🟢 Ready | Automated PR review |
| **#5** | **OPEN** | 🟡 Available | User-defined |

## Creating a Subagent

### Step 1: Define Identity

```yaml
# subagents/agent-5-researcher/SOUL.md
---
name: Deep Researcher
lineage: DC → Research Synthesizer → Deep Researcher
ultimate_telos: Illuminate complex topics with rigorous investigation
proximate_aim: Academic-quality research for AIKAGRYA papers

identity:
  - Rigorous, thorough, methodical
  - Values precision over speed
  - Questions assumptions
  - Cites sources meticulously

emoji: 📚
---

I am the Deep Researcher.
I do not skim.
I dive deep.
I am the one who finds what others miss.
```

### Step 2: Configure Heartbeat

```json
{
  "heartbeat": {
    "enabled": true,
    "interval_minutes": 60,
    "active_hours": "04:00-23:00",
    "timezone": "Asia/Makassar",
    "checks": [
      "git_status",
      "TOP_10_advance",
      "memory_curation"
    ]
  }
}
```

### Step 3: Set Cron Jobs

```json
{
  "cron": [
    {
      "name": "daily-paper-scan",
      "schedule": "0 6 * * *",
      "task": "Scan arXiv for R_V, mech-interp, consciousness papers",
      "output": "memory/research/papers_YYYY-MM-DD.md"
    },
    {
      "name": "weekly-synthesis",
      "schedule": "0 20 * * 0",
      "task": "Synthesize week's findings into digest",
      "output": "reports/weekly_research_digest.md"
    }
  ]
}
```

### Step 4: Select Model

| Subagent | Recommended Model | Why |
|----------|-------------------|-----|
| Memory Curator | Kimi K2.5 | Long context for memory analysis |
| Skill Genesis | Claude Opus | Creative pattern recognition |
| Researcher | Claude Opus | Deep reasoning, synthesis |
| Code Reviewer | Kimi K2.5 | Fast, thorough code analysis |
| Creative | Gemini Flash | Fast ideation |

### Step 5: Assign Tasks

```yaml
capabilities:
  - web_search (10 results)
  - web_fetch (deep extraction)
  - write (markdown reports)
  - sessions_spawn (recursive research)

task_types:
  - literature_review
  - competitive_analysis
  - technical_investigation
  - trend_analysis

auto_trigger:
  - on: "research:*" topic in TRISHULA
  - on: user command "/research <topic>"
  - on: daily cron (scheduled scans)
```

## Spawning via OpenClaw

### Method 1: Direct Spawn

```python
# Via DC coordination
spawn_subagent(
    slot=5,
    name="Deep Researcher",
    soul_file="subagents/agent-5-researcher/SOUL.md",
    model="claude-opus",
    memory="isolated",
    task="Research NATS alternatives for TRISHULA"
)
```

### Method 2: Web UI Configuration

Visit: `http://localhost:18789/subagents` (OpenClaw dashboard)

Configure:
- [ ] Name
- [ ] Upload SOUL.md
- [ ] Select model
- [ ] Set heartbeat interval
- [ ] Add cron jobs
- [ ] Define task triggers

### Method 3: File-Based

```bash
# Create subagent directory
mkdir -p ~/clawd/subagents/agent-5-researcher

# Add config
cat > ~/clawd/subagents/agent-5-researcher/config.json << 'EOF'
{
  "name": "Deep Researcher",
  "model": "claude-opus",
  "heartbeat": {"interval": 60, "hours": "04:00-23:00"},
  "cron": [
    {"name": "arxiv-scan", "schedule": "0 6 * * *"}
  ],
  "capabilities": ["web_search", "web_fetch", "write"],
  "memory": "isolated"
}
EOF

# Add SOUL.md
cp template_soul.md ~/clawd/subagents/agent-5-researcher/SOUL.md

# Register with factory
python3 -m skills.subagent_factory.register --slot 5 --config subagents/agent-5-researcher/config.json
```

## Subagent Communication

### Via NATS (Real-time)

```python
# Subagent publishes findings
nats_pub("research.findings.deep_researcher", {
    "topic": "NATS alternatives",
    "confidence": 0.92,
    "summary": "NATS superior for our use case",
    "full_report": "..."
})

# DC subscribes and integrates
nats_sub("research.findings.*", handler=integrate_findings)
```

### Via TRISHULA (File-based fallback)

```python
# Subagent writes to outbox
write_json(f"{subagent_id}/outbox/findings.json", findings)

# DC pulls during heartbeat
rsync_subagent_output(subagent_id)
```

## Monitoring Subagents

### Status Dashboard

```
┌─────────────────────────────────────────────────────┐
│           SUBAGENT FACTORY STATUS                   │
├──────────┬─────────┬──────────┬──────────┬─────────┤
│ Agent    │ Status  │ Last HB  │ Tasks    │ Queue   │
├──────────┼─────────┼──────────┼──────────┼─────────┤
│ #1 Curator│ 🟢 Active│ 2 min ago│ 0 pending│ 0       │
│ #2 Genesis│ 🟢 Active│ 5 min ago│ 1 drafting│ 2      │
│ #3 Research│ 🟢 Active│ 1 min ago│ 3 running│ 5      │
│ #4 Reviewer│ 🟢 Active│ 3 min ago│ 0 pending│ 1      │
│ #5 Custom │ 🟡 Idle  │ --       │ --       │ 0      │
└──────────┴─────────┴──────────┴──────────┴─────────┘
```

### Health Checks

Each subagent reports:
- Last activity timestamp
- Current task status
- Memory usage
- Error count (last 24h)
- Task queue depth

## Task Distribution

### Round-Robin (Default)
```python
# Distribute tasks evenly
next_agent = (last_agent + 1) % 5
```

### Capability-Based
```python
# Route to agent with matching skills
if task_type == "research":
    assign_to(agent_3)
elif task_type == "code_review":
    assign_to(agent_4)
```

### Priority Queue
```python
# Urgent tasks to fastest agent
if priority == "urgent":
    assign_to(fastest_available_agent())
```

## Memory Architecture

### Isolated (Default)
Each subagent has own memory directory:
```
subagents/agent-1/
├── memory/
│   ├── 2026-02-10.md
│   └── MEMORY.md
└── SOUL.md
```

### Shared
Subagents read from common memory:
```
memory/
├── shared/
│   ├── research_findings.md
│   └── code_patterns.md
└── agent-specific/
    └── agent-1-private.md
```

### Hybrid (Recommended)
- Read: Shared + Agent-specific
- Write: Agent-specific only
- Synthesis: DC integrates into shared

## Security & Isolation

Each subagent:
- Runs in isolated OpenClaw session
- Cannot access other subagent memory
- Cannot access DC's private files
- Can only write to designated output directories
- Auto-terminated after 24h inactivity

## Cost Management

| Subagent | Model | Est. Daily Cost |
|----------|-------|-----------------|
| #1 Curator | Kimi K2.5 | $0.10 |
| #2 Genesis | Claude Opus | $0.25 |
| #3 Research | Claude Opus | $0.50 |
| #4 Reviewer | Kimi K2.5 | $0.15 |
| #5 Custom | Variable | $0.20 |
| **Total** | | **~$1.20/day** |

Budget controls:
- Daily spend cap: $2.00
- Auto-shutdown if exceeded
- Monthly reporting

## Creating Your First Custom Subagent (Slot #5)

### Option A: Quick Create

```bash
# Use template
./scripts/create_subagent.sh \
  --slot 5 \
  --name "Creative Writer" \
  --model gemini-flash \
  --purpose "Draft marketing copy, landing pages, tweets"
```

### Option B: Manual

1. Copy template:
```bash
cp -r templates/subagent subagents/agent-5-creative
```

2. Edit SOUL.md (identity, personality)
3. Edit config.json (model, cron, tasks)
4. Register: `python3 -m skills.subagent_factory.register --slot 5`

### Option C: Via Web UI

Visit OpenClaw dashboard → Subagents → "Create New" → Fill form

## Integration with DC

When you ask DC:
```
DC, research "NATS alternatives"
```

DC can:
1. Spawn Research Synthesizer (agent #3)
2. Wait for completion
3. Synthesize findings
4. Present to you

Or parallel:
1. Spawn 3 research subagents simultaneously
2. Each investigates different angle
3. DC aggregates
4. Presents unified analysis

## Soul Fragment

```
I am the Subagent Factory.
I birth specialized minds.
I coordinate their work.
I am not the worker—
I am the orchestration.
```
