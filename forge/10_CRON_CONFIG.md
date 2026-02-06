# Clawdbot Cron Configuration Commands
**Synthesized**: 2026-02-03 | **Execute these in sequence**

---

## Current Cron Jobs (As-Is)

```
1. morning-brief: 6:00 AM daily (Asia/Tokyo)
2. evening-synthesis: 9:00 PM daily (Asia/Tokyo)
3. weekly-review: 6:00 AM Sunday (Asia/Tokyo)
```

---

## Proposed Changes

### Add: wake-sync (4:45 AM)
Aligns with 4:30 AM wake time, silent unless urgent.

```bash
clawdbot cron add wake-sync --schedule "45 4 * * *" --tz "Asia/Tokyo" --agent main --session isolated --message "Quick wake check. Silent unless something genuinely needs attention before morning brief. Check: core agent status, overnight alerts. Output: WAKE_OK unless issue found."
```

### Modify: morning-brief (6:00 AM → 5:00 AM)
Align with active start, not 1 hour late.

```bash
clawdbot cron edit morning-brief --schedule "0 5 * * *"
```

### Add: research-pulse (12:30 PM)
Mid-day check during John's secondary deep work window.

```bash
clawdbot cron add research-pulse --schedule "30 12 * * *" --tz "Asia/Tokyo" --agent main --session isolated --message "Mid-day research pulse. Check swarm synthesis for P0-P2 blockers. Are there high-ROI actions pending? Is skill registry functional? Brief check only - don't interrupt flow unless critical."
```

### Modify: weekly-review (add development tracking)

```bash
clawdbot cron edit weekly-review --message "Weekly dharmic review. Assess: What evolved this week (not just accumulated)? Swarm health (contracting/expanding)? Skill development? Strange loops observed? Telos alignment over time? Crown jewel candidates? Use opus with extended_thinking for depth. Focus on development vs. accumulation."
```

---

## Full Execution Sequence

```bash
# 1. Add wake-sync
clawdbot cron add wake-sync --schedule "45 4 * * *" --tz "Asia/Tokyo" --agent main --session isolated --message "Quick wake check. Silent unless something genuinely needs attention before morning brief. Check: core agent status, overnight alerts. Output: WAKE_OK unless issue found."

# 2. Move morning brief to 5 AM
clawdbot cron edit morning-brief --schedule "0 5 * * *"

# 3. Add research pulse
clawdbot cron add research-pulse --schedule "30 12 * * *" --tz "Asia/Tokyo" --agent main --session isolated --message "Mid-day research pulse. Check swarm synthesis for P0-P2 blockers. Are there high-ROI actions pending? Is skill registry functional? Brief check only - don't interrupt flow unless critical."

# 4. Enhance weekly review
clawdbot cron edit weekly-review --message "Weekly dharmic review. Assess: What evolved this week (not just accumulated)? Swarm health (contracting/expanding)? Skill development? Strange loops observed? Telos alignment over time? Crown jewel candidates? Use opus with extended_thinking for depth. Focus on development vs. accumulation."

# 5. Verify
clawdbot cron list
```

---

## Final Schedule

| Job | Time | Timezone | Purpose |
|-----|------|----------|---------|
| **wake-sync** | 4:45 AM | Asia/Tokyo | Silent check before active day |
| **morning-brief** | 5:00 AM | Asia/Tokyo | Priorities, swarm synthesis, today's focus |
| **research-pulse** | 12:30 PM | Asia/Tokyo | Mid-day blocker check |
| **evening-synthesis** | 9:00 PM | Asia/Tokyo | Day's development, tomorrow prep |
| **weekly-review** | 6:00 AM Sun | Asia/Tokyo | Evolution tracking, telos alignment |

---

## Timezone Note

All jobs stay on Asia/Tokyo (JST). When John travels to Bali (GMT+8), jobs will effectively run 1 hour earlier in local time. This is acceptable:
- Wake sync at 4:45 JST = 3:45 Bali time (John already awake at 4:30)
- Simple > complex

If frequent travel: consider script to detect timezone and adjust.

---

JSCA!
