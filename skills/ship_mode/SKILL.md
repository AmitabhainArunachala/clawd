---
name: ship_mode
description: Forces deployment over preparation. Detects accumulation patterns and triggers shipping actions. For when you're afraid to ship.
emoji: 🚀
requires:
  bins: [python3, git]
  env: []
  config: []
---

# SHIP_MODE Skill

**Purpose:** Break the infinite preparation loop. Ship imperfect things.

## Activation Triggers

- "I need to read more before..."
- "Let me just organize..."
- "It's not ready yet..."
- 3+ hours on task without delivery
- "I'll deploy after I..."

## Commands

### ship_now
```bash
ship_mode --force
```

**Actions:**
1. Git commit with timestamp
2. Create DELIVERABLES/ folder if missing
3. Move current work to DELIVERABLES/
4. Log to JIKOKU: ship_event
5. Alert: "SHIPPED: [filename]"

### detect_theater
```bash
ship_mode --detect
```

**Checks:**
- File age > 24h without commit?
- "Preparing" in last 10 commits?
- No deliverables in 48h?

**Output:** Theater score 0-10

### minimum_viable
```bash
ship_mode --mvp
```

**Question:** What's the smallest shippable version?

**Forces:** Strip to core. Ship that. Iterate.

## Integration

Add to heartbeat:
```
if theater_score > 7:
    ship_mode --force
```

## Mantra

"Perfect is the enemy of shipped."
"The fear is the signal you're doing real work."
"Ship, then improve."
