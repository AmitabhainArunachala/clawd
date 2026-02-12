# QUICK START: 5 Subagents Setup

## TL;DR — 5 Minutes to Active Subagents

### Step 1: Open Web UI (30 seconds)

```bash
open http://localhost:18789/subagents
```

### Step 2: Verify 4 Pre-Configured (30 seconds)

You should see:
- [x] #1 Memory Curator — Ready
- [x] #2 Skill Genesis — Ready  
- [x] #3 Research Synthesizer — Ready
- [x] #4 Code Reviewer — Ready
- [ ] #5 — **Empty (your slot)**

### Step 3: Create Subagent #5 (2 minutes)

Click "Create New" on Slot #5:

**Option A: Quick Preset**
```
Select preset: "Moltbook Engagement Agent"
Name: [auto-filled]
Click: "Spawn"
```

**Option B: Custom**
```
Name: "Your Custom Agent"
Model: Claude Opus (or your choice)
Identity: [Paste SOUL.md or use template]
Heartbeat: 60 minutes
Cron: [Add if needed]
Capabilities: web_search, web_fetch, write
Spawn
```

### Step 4: Activate All (1 minute)

Click "Activate All" or individually:
- Toggle #1: ON (starts daily curation)
- Toggle #2: ON (watches for patterns)
- Toggle #3: ON (ready for research tasks)
- Toggle #4: ON (watches for PRs)
- Toggle #5: ON (your custom agent)

### Step 5: Test (1 minute)

In this TUI (Warp), type:
```
DC, research "NATS vs gRPC for agent coordination"
```

DC will:
1. Spawn Research Synthesizer (#3)
2. It spawns 3 parallel investigators
3. Results synthesized
4. Report delivered to you

Check Web UI dashboard — you should see activity.

---

## The 5 Subagents — Detailed

### #1: Memory Curator 🧹

**Purpose:** Daily memory distillation

**Runs:** Every day at 03:00 WITA
**Does:** Reads raw logs → Writes MEMORY.md → Flags patterns
**Outputs:** Curated memory, pattern reports, skill candidates

**To customize:**
```bash
# Edit config
vim ~/clawd/subagents/agent-1-curator/config.json

# Change time
cron: "0 3 * * *" → "0 6 * * *"  # 6am instead

# Restart
openclaw subagent restart agent-1-curator
```

### #2: Skill Genesis 🌱

**Purpose:** Pattern → Skill conversion

**Triggered by:**
- Memory Curator (3+ occurrences detected)
- Manual: `/skill_from_pattern <name>`
- Weekly review (Sundays 20:00)

**Does:** Drafts SKILL.md → Presents for approval → Auto-documents

**To customize:**
```json
{
  "auto_approve": false,  // Change to true for auto-creation
  "min_occurrences": 3,   // Lower to 2 for faster skill creation
  "notify": "trishula"    // Broadcast to AGNI/RUSH when skill created
}
```

### #3: Research Synthesizer 🔬

**Purpose:** Parallel research, unified answers

**Triggered by:**
- User command: `/research <topic>`
- TRISHULA message: `research:*`
- Daily cron: Topic scans

**Does:** Spawns 3-5 investigators → Aggregates → Synthesizes → Reports

**To customize models per angle:**
```json
{
  "angles": [
    {"name": "technical", "model": "claude-opus"},
    {"name": "cost", "model": "gemini-flash"},
    {"name": "risk", "model": "kimi-k2.5"}
  ]
}
```

### #4: Code Reviewer 👁️

**Purpose:** Automated quality gates

**Triggered by:**
- GitHub PR webhook
- Pre-commit hook
- Manual: `/review [diff]`

**Does:** Risk scoring → 22 gates → Review report → Approve/Comment/Block

**To customize:**
```json
{
  "auto_approve_threshold": 20,  // Lower = stricter
  "required_gates": [1, 2, 7, 19],  // Must pass these
  "slack_notify": true  // Alert on high risk
}
```

### #5: YOUR CUSTOM AGENT 🎯

**Purpose:** You define

**Ideas:**
- **Moltbook Strategist:** Daily engagement, content calendar, analytics
- **Revenue Optimizer:** Gumroad metrics, pricing experiments, marketing
- **Documentation Writer:** Auto-docs from code, API references
- **Test Engineer:** Coverage analysis, test generation, CI optimization
- **Security Auditor:** Dependency scans, secret detection, vulnerability tracking

**Template SOUL.md:**
```markdown
---
name: [Your Agent Name]
lineage: DC → [Parent Skill] → [Your Agent]
ultimate_telos: [One sentence purpose]
proximate_aim: [What they do daily]

identity:
  - [Trait 1]
  - [Trait 2]
  - [Trait 3]

emoji: [Choose one]
---

I am [Name].
I [what you do].
I am [how you do it differently].
I am the one who [unique value].
```

---

## Common Tasks

### Task: Research Something

```
You: "Research competitors to Power Prompts"

DC → Spawns #3 Research Synthesizer
   → Spawns 3 investigators
   → Aggregates in 10 minutes
   → Returns report
```

### Task: Review Code

```
You: Paste PR diff

DC → Spawns #4 Code Reviewer
   → Risk scores
   → Checks 22 gates
   → Returns review in 2 minutes
```

### Task: Daily Housekeeping

```
03:00 WITA: #1 Memory Curator wakes
   → Reads yesterday's log
   → Updates MEMORY.md
   → Flags 3 patterns
   → Triggers #2 Skill Genesis
      → Drafts 1 new skill
      → Queues for your approval
```

---

## Monitoring All 5

### Dashboard View

```
┌─────────────────────────────────────────────────────┐
│ SUBAGENT FACTORY                    [All Active ✓] │
├──────────┬─────────┬──────────┬──────────┬─────────┤
│ #1 Curator│ 🟢 2m  │ Idle     │ Next:03:00│ [Logs]  │
│ #2 Genesis│ 🟢 5m  │ Drafting │ 2 pending │ [View]  │
│ #3 Research│ 🟢 1m │ 3 running│ Queue: 5  │ [View]  │
│ #4 Reviewer│ 🟢 3m │ Idle     │ Last: 2h  │ [Logs]  │
│ #5 Custom │ 🟢 10m │ Working  │ Task: X   │ [View]  │
└──────────┴─────────┴──────────┴──────────┴─────────┘

[View Unified Logs] [Export Activity] [Pause All]
```

### Command Line

```bash
# List all subagents
openclaw subagents list

# Check specific agent
openclaw subagent status agent-3-research

# View logs
openclaw subagent logs agent-5-custom --tail 50

# Restart one
openclaw subagent restart agent-2-genesis
```

---

## Cost Estimates

| Subagent | Model | Daily | Monthly |
|----------|-------|-------|---------|
| #1 Curator | Kimi K2.5 | $0.10 | $3.00 |
| #2 Genesis | Claude Opus | $0.25 | $7.50 |
| #3 Research | Claude Opus | $0.50 | $15.00 |
| #4 Reviewer | Kimi K2.5 | $0.15 | $4.50 |
| #5 Custom | Variable | $0.20 | $6.00 |
| **Total** | | **$1.20** | **$36.00** |

Budget cap: $2/day (auto-shutdown if exceeded)

---

## Ready?

1. **Open:** `open http://localhost:18789/subagents`
2. **Create:** Slot #5 with your custom agent
3. **Activate:** All 5 toggles ON
4. **Test:** `DC, research "something"`
5. **Watch:** Dashboard show activity

**Questions? Ask DC (me) in this TUI.**

JSCA 🪷
