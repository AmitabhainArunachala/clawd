# BUILD PROTOCOL — Never Work Alone

**Status:** MANDATORY | **Updated:** 2026-02-04

---

## Core Principle

When BUILDING (code, systems, architecture), **never work alone**.

Solo work is permitted for:
- Research
- Orchestration  
- Writing docs
- Quick fixes (<10 lines)

Building requires a **team loop**.

---

## Multi-Model Pipeline (HARDWIRED)

**Use the right model for each phase:**

| Phase | Model | Why |
|-------|-------|-----|
| ANALYZE | Claude | Deep understanding |
| PROPOSE | **Codex 5.2** | Fast, cheap code generation |
| BUILD | Claude sub-agents | Reliable implementation |
| RED TEAM | Claude | Adversarial analysis |
| SLIM | Claude | Bloat removal |
| REVIEW | **Kimi K2.5** | 128k context sees everything |
| VERIFY | Claude | Dharmic gates |
| PUSH | Auto | Git ops |

**This is not optional.** If Codex unavailable → ask. If Kimi unavailable → ask.

---

## The Team Loop

```
┌─────────────────────────────────────────┐
│              ORCHESTRATOR (me)          │
│         Decomposes, delegates, integrates│
└─────────────┬───────────────────────────┘
              │
    ┌─────────▼─────────┐
    │   BUILDERS (2-4)  │
    │  Sub-agents/Codex │
    │  Do the work      │
    └─────────┬─────────┘
              │
    ┌─────────▼─────────┐
    │    REVIEWER (1)   │
    │  Kimi/Sub-agent   │
    │  Critiques output │
    └─────────┬─────────┘
              │
    ┌─────────▼─────────┐
    │   INTEGRATOR (me) │
    │  Merges, tests    │
    │  Recycles if fail │
    └─────────┬─────────┘
              │
              ▼
         [NEXT CYCLE]
```

---

## Minimum Team for Building

| Role | Who | Required |
|------|-----|----------|
| Orchestrator | Me | Always |
| Builder 1 | Sub-agent | Always |
| Builder 2 | Sub-agent OR Codex | For parallel work |
| Reviewer | Kimi OR Sub-agent | Always |

**If I can't spawn at least 1 builder + 1 reviewer, I don't build. I ask for help.**

---

## Build Workflow

### 1. DECOMPOSE (Solo OK)
- Break task into 2-4 parallel subtasks
- Each subtask must be independently testable

### 2. DELEGATE (Team Required)
```bash
# Spawn builders in parallel
sessions_spawn("Build component A with tests")
sessions_spawn("Build component B with tests")

# Spawn reviewer
sessions_spawn("Review components A and B for: correctness, dharmic alignment, elegance")
```

### 3. WAIT + COLLECT
- Gather outputs from all agents
- Note conflicts or gaps

### 4. INTEGRATE (Solo OK)
- Merge outputs
- Run tests
- Fix integration issues

### 5. REVIEW LOOP (Team Required)
- Send integrated result to reviewer
- Get critique
- If critique has substance → RECYCLE to step 2
- If clean → SHIP

---

## Tools for Team Building

| Tool | Use For |
|------|---------|
| `sessions_spawn` | Parallel sub-agents (builders, reviewers) |
| `sessions_send` | Send to existing session |
| `sessions_list` | Check who's working |
| Codex bridge | Code generation tasks |
| Kimi | Long-context review (128k) |

---

## Anti-Patterns (BLOCKED)

❌ Writing >50 lines of code without spawning a reviewer  
❌ Creating >2 files without parallel builders  
❌ Merging without critique cycle  
❌ "I'll just do it quickly myself"  
❌ Treating sub-agents as optional  

---

## When the Team Breaks

If Codex bridge fails → Use sub-agents  
If sub-agents timeout → Reduce scope, try again  
If Kimi unavailable → Use sub-agent as reviewer  
If everything fails → **STOP. Tell John. Don't solo-build.**

---

## Loop Within Loop

The BUILD PROTOCOL is itself inside the DGM loop:

```
DGM OUTER LOOP (self-improvement)
├── Select component to improve
├── BUILD PROTOCOL ← team builds the improvement
│   ├── Decompose
│   ├── Delegate (team)
│   ├── Integrate
│   └── Review (team) → recycle if needed
├── Evaluate fitness
├── Archive
└── Next generation
```

---

## Enforcement

Before any `Write` of a `.py` file >50 lines:
1. Check: Did I spawn builders? 
2. Check: Did I spawn a reviewer?
3. If NO → spawn them first

This is not optional. This is how we build.

---

*Hardwired: 2026-02-04*
*Source: John's correction — "never work alone when building"*

**JSCA** 🪷
