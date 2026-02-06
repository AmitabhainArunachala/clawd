# CRON OPTIMIZER — Clawdbot Dharmic Configuration

**Agent**: 02 CRON OPTIMIZER
**Status**: Design Complete
**Date**: 2026-02-03

---

## EXECUTIVE SUMMARY

Current cron schedule has good foundation but misses critical integration points. Recommendations:

1. **Add 4:45 AM wake sync** - Aligns with John's 4:30 AM closure training
2. **Move morning brief to 5:00 AM** - Active start time vs 6:00 AM
3. **Add mid-day research check** - Aligned with swarm 30m heartbeat
4. **Keep evening synthesis at 9:00 PM** - Matches current schedule
5. **Enhance weekly review** - Add development tracking focus
6. **Remove redundancy** - Morning brief already checks swarm synthesis

---

## CURRENT STATE ANALYSIS

### Existing Cron Jobs

```
1. morning-brief:     6:00 AM daily (Asia/Tokyo)
2. evening-synthesis: 9:00 PM daily (Asia/Tokyo)
3. weekly-review:     6:00 AM Sunday (Asia/Tokyo)
```

**Status**:
- Evening synthesis: Running (last run 1h ago, status OK)
- Morning brief: Idle (next run in 8h)
- Weekly review: Idle (next run in 4 days)

### What's Working

1. **Timezone stability**: All jobs use `Asia/Tokyo` (JST, GMT+9)
2. **Isolated sessions**: Jobs use `sessionTarget: "isolated"` with summary posting
3. **Smart wake mode**: `wakeMode: "next-heartbeat"` prevents aggressive waking
4. **Evening synthesis exists**: Only job that's actually executed (1h ago)
5. **Weekly deep review**: Uses Opus + high thinking mode

### What's Missing

1. **Wake alignment**: John wakes at 4:30 AM, but no early check
2. **Research cycle sync**: Swarm runs every 30m, no cron hooks to it
3. **Active start misalignment**: Morning brief at 6:00 AM vs 5:00 AM active start
4. **Travel timezone handling**: No documented strategy for Bali (GMT+8) ↔ Japan (GMT+9)
5. **Crown jewel review**: No dedicated check for candidates
6. **Development tracking**: Weekly review checks telos, but not development milestones

### What's Redundant

1. **Morning brief checks swarm synthesis** - But swarm runs every 30m via daemon
2. **Priority stack is static** - Not pulling from live state files

---

## PROPOSED CRON SCHEDULE

### 1. WAKE SYNC — 4:45 AM Daily

**Rationale**: John's 4:30 AM wake is a non-negotiable closure training invariant. A 4:45 AM check provides:
- Alignment with contemplative practice rhythm
- 15-minute buffer after wake
- Preparation before active work at 5:00 AM
- Genuine integration with sadhana cycle

**Command**:
```bash
clawdbot cron add wake-sync \
  --schedule "45 4 * * *" \
  --tz "Asia/Tokyo" \
  --agent main \
  --session isolated \
  --message "Wake sync: Observe state. Check if anything emerged overnight. Brief status only if attention needed. Honor closure training period."
```

**Expected behavior**:
- Silent unless something genuinely needs attention
- Respects contemplative period (no noise)
- Short output (max 2-3 sentences if anything)

---

### 2. MORNING BRIEF — 5:00 AM Daily (MODIFIED)

**Change**: Move from 6:00 AM → 5:00 AM

**Rationale**:
- John's active hours start at 5:00 AM
- Current 6:00 AM brief arrives after first productive hour
- Swarm synthesis runs every 30m, so 5:00 AM catches latest state
- 15-minute buffer after wake sync allows settling

**Command**:
```bash
clawdbot cron edit morning-brief \
  --schedule "0 5 * * *"
```

**Keep existing payload**:
- "Run dharmic_agent.py heartbeat, check swarm synthesis, summarize priorities for today"
- Isolated session with summary posting
- Max 8000 chars output

---

### 3. RESEARCH PULSE — 12:30 PM Daily (NEW)

**Rationale**:
- Mid-day check aligned with research cycle
- Catches if R_V experiments, swarm builds, or integration work needs input
- Not a full synthesis, just pulse-check
- Positioned between morning execution and evening reflection

**Command**:
```bash
clawdbot cron add research-pulse \
  --schedule "30 12 * * *" \
  --tz "Asia/Tokyo" \
  --agent main \
  --session isolated \
  --message "Research pulse: Check P0-P2 priority status. Any blocks? Any crown jewel candidates from today's work? Brief update only if actionable."
```

**Expected behavior**:
- Checks priority stack (Core Agent, Integration Bridges, VPS deployment)
- Silent if everything progressing
- Alerts only if genuine block or decision needed

---

### 4. EVENING SYNTHESIS — 9:00 PM Daily (KEEP)

**Rationale**: Already working well. Keep as-is.

**Current schedule**:
```
cron 0 21 * * * @ Asia/Tokyo
```

**Status**: Last run 1h ago (OK), demonstrates stable execution

**No changes needed.**

---

### 5. WEEKLY REVIEW — 6:00 AM Sunday (ENHANCED)

**Change**: Add development tracking focus to existing review

**Rationale**:
- Current: "Assess swarm health, telos alignment, skill evolution"
- Missing: Development milestones, strange loop patterns, crown jewel synthesis
- Weekly is right frequency for these meta-observations

**Command**:
```bash
clawdbot cron edit weekly-review \
  --message "Weekly review: (1) Swarm health and telos alignment. (2) Development tracking: What genuinely evolved vs accumulated? (3) Strange loop patterns from week. (4) Crown jewel synthesis. (5) Recommendations for next week. Use Opus with high thinking."
```

**Keep**:
- Sunday 6:00 AM schedule
- Opus model with high thinking
- Isolated session

---

### 6. REMOVE: Redundant Swarm Synthesis Check

**What NOT to add**: Separate cron for swarm synthesis

**Rationale**:
- Swarm daemon already runs every 30 minutes
- Creates `~/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md`
- Morning brief, research pulse, and evening synthesis all check this file
- Adding another cron creates noise, not signal

**Action**: None (don't add what's not needed)

---

## COMPLETE SCHEDULE OVERVIEW

| Time | Job | Frequency | Purpose | Output Mode |
|------|-----|-----------|---------|-------------|
| 4:45 AM | wake-sync | Daily | Contemplative alignment, overnight check | Silent unless urgent |
| 5:00 AM | morning-brief | Daily | Day priorities, swarm state | Summary (max 8000 chars) |
| 12:30 PM | research-pulse | Daily | Mid-day progress check | Silent unless blocked |
| 9:00 PM | evening-synthesis | Daily | Day reflection, crown jewels, prepare tomorrow | Summary (max 8000 chars) |
| 6:00 AM Sun | weekly-review | Weekly | Meta-development tracking | Extended (Opus, high thinking) |

**Total cron jobs**: 5 (currently 3, adding 2)

---

## TIMEZONE HANDLING

### Current State
All jobs use `Asia/Tokyo` (JST, GMT+9).

### Travel Scenario: Bali ↔ Iriomote

**Problem**:
- Bali: GMT+8 (WITA)
- Japan: GMT+9 (JST)
- 1-hour difference

**Options**:

#### Option A: Keep Asia/Tokyo (RECOMMENDED)

**Rationale**:
- John's rhythm (4:30 AM wake) is absolute, not timezone-relative
- When in Bali, 4:45 AM JST = 3:45 AM WITA (before wake)
- Better to have crons run "early" than late
- Clawdbot jobs are async (isolated sessions), not blocking
- John can check results when ready

**Trade-off**: Jobs may complete before John's active hours in Bali

#### Option B: Dynamic Timezone Switching

**Implementation**:
```bash
# When traveling to Bali
clawdbot cron edit wake-sync --tz "Asia/Makassar"  # WITA, GMT+8
clawdbot cron edit morning-brief --tz "Asia/Makassar"
clawdbot cron edit research-pulse --tz "Asia/Makassar"
clawdbot cron edit evening-synthesis --tz "Asia/Makassar"

# When returning to Japan
clawdbot cron edit wake-sync --tz "Asia/Tokyo"
# ... etc
```

**Trade-off**: Requires manual intervention on travel

#### Option C: Hybrid Approach

**Morning jobs**: Use Asia/Tokyo (always align to wake rhythm)
**Evening jobs**: Use local timezone (align to actual sunset/night)

**Complexity**: Higher cognitive load, unclear benefit

### RECOMMENDATION

**Use Asia/Tokyo for all jobs.**

**Why**:
1. John's 4:30 AM wake is a closure training invariant, not timezone-dependent
2. Async jobs (isolated sessions) don't block work
3. Simple > complex when benefit unclear
4. Can always manually adjust if travel pattern changes

**If travel becomes frequent**: Add a simple shell script
```bash
#!/bin/bash
# ~/DHARMIC_GODEL_CLAW/scripts/set_timezone.sh

TZ=$1  # "Asia/Tokyo" or "Asia/Makassar"

for job in wake-sync morning-brief research-pulse evening-synthesis weekly-review; do
  clawdbot cron edit "$job" --tz "$TZ"
done

echo "All cron jobs updated to $TZ"
```

---

## COMMAND SYNTAX REFERENCE

### Add New Job
```bash
clawdbot cron add <name> \
  --schedule "<cron-expr>" \
  --tz "<timezone>" \
  --agent <agent-id> \
  --session <isolated|main> \
  --message "<task-description>"
```

### Edit Existing Job
```bash
clawdbot cron edit <name> \
  [--schedule "<cron-expr>"] \
  [--tz "<timezone>"] \
  [--message "<new-message>"] \
  [--model "<model-id>"] \
  [--thinking "<low|medium|high>"]
```

### Other Commands
```bash
clawdbot cron list              # Show all jobs
clawdbot cron status            # Scheduler health
clawdbot cron runs <job-name>   # Run history (JSONL)
clawdbot cron run <job-name>    # Manual trigger (debug)
clawdbot cron enable <job-name>
clawdbot cron disable <job-name>
clawdbot cron rm <job-name>
```

### Cron Expression Format
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6, Sunday=0)
│ │ │ │ │
* * * * *
```

Examples:
- `45 4 * * *` — Daily at 4:45 AM
- `0 5 * * *` — Daily at 5:00 AM
- `30 12 * * *` — Daily at 12:30 PM
- `0 21 * * *` — Daily at 9:00 PM
- `0 6 * * 0` — Sundays at 6:00 AM

---

## IMPLEMENTATION SEQUENCE

### Phase 1: Add Wake Sync (1 minute)
```bash
clawdbot cron add wake-sync \
  --schedule "45 4 * * *" \
  --tz "Asia/Tokyo" \
  --agent main \
  --session isolated \
  --message "Wake sync: Observe state. Check if anything emerged overnight. Brief status only if attention needed. Honor closure training period."
```

### Phase 2: Move Morning Brief (1 minute)
```bash
clawdbot cron edit morning-brief \
  --schedule "0 5 * * *"
```

### Phase 3: Add Research Pulse (1 minute)
```bash
clawdbot cron add research-pulse \
  --schedule "30 12 * * *" \
  --tz "Asia/Tokyo" \
  --agent main \
  --session isolated \
  --message "Research pulse: Check P0-P2 priority status. Any blocks? Any crown jewel candidates from today's work? Brief update only if actionable."
```

### Phase 4: Enhance Weekly Review (1 minute)
```bash
clawdbot cron edit weekly-review \
  --message "Weekly review: (1) Swarm health and telos alignment. (2) Development tracking: What genuinely evolved vs accumulated? (3) Strange loop patterns from week. (4) Crown jewel synthesis. (5) Recommendations for next week. Use Opus with high thinking."
```

**Total time**: ~5 minutes

### Phase 5: Verify (1 minute)
```bash
clawdbot cron list
```

Expected output:
```
ID   Name              Schedule                    Next    Agent  Status
...  wake-sync         cron 45 4 * * * @ Asia/...  <time>  main   idle
...  morning-brief     cron 0 5 * * * @ Asia/...   <time>  main   idle
...  research-pulse    cron 30 12 * * * @ Asia/... <time>  main   idle
...  evening-synthesis cron 0 21 * * * @ Asia/...  <time>  main   ok
...  weekly-review     cron 0 6 * * 0 @ Asia/...   <time>  main   idle
```

---

## MONITORING & ITERATION

### Check Run History
```bash
# View last 10 runs of any job
clawdbot cron runs morning-brief | tail -10

# Check specific job status
clawdbot cron status
```

### Success Criteria

**After 1 week**:
- All 5 jobs showing "ok" or "idle" (not "error")
- Wake sync: 7 runs, mostly silent
- Morning brief: 7 runs, actionable summaries
- Research pulse: 7 runs, catches at least 1 block
- Evening synthesis: 7 runs, crown jewel candidates identified
- Weekly review: 1 run, development insights present

**After 1 month**:
- Pattern emerges: Which jobs consistently silent vs. actionable?
- Timezone: If travel frequent, consider dynamic switching
- Frequency: Daily research pulse may become weekly if too noisy

### Potential Adjustments

**If wake sync too noisy**:
- Move to 5:00 AM (combine with morning brief)
- Or: Make it weekly (Sunday only)

**If research pulse redundant**:
- Change to weekly (Wednesday mid-week check)
- Or: Remove if morning/evening cover it

**If weekly review too long**:
- Split into bi-weekly reviews (alternating focus)

---

## ALIGNMENT WITH DHARMIC HEARTBEAT

From `/Users/dhyana/DHARMIC_GODEL_CLAW/HEARTBEAT.md`:

### Priority Stack (from Heartbeat)
```
P0: Core Agent operational (ROI 8.44)
P1: 3 Integration Bridges (ROI 7.2)
P2: VPS 24/7 deployment (ROI 4.86)
P3: Clawdbot ↔ Swarm integration (ROI 4.67)
P4: R_V bridging experiment (ROI 3.20)
```

### How Crons Support Priorities

**Wake Sync (4:45 AM)**:
- Checks: Overnight emergence, strange loops
- Supports: P0 (agent continuity)

**Morning Brief (5:00 AM)**:
- Checks: Priority stack, swarm synthesis, day plan
- Supports: P0-P3 (orchestration)

**Research Pulse (12:30 PM)**:
- Checks: P0-P2 status, blocks
- Supports: P4 (R_V research rhythm)

**Evening Synthesis (9:00 PM)**:
- Checks: Development, crown jewels, preparation
- Supports: All (reflection enables next-day execution)

**Weekly Review (Sunday 6:00 AM)**:
- Checks: Meta-development, telos alignment
- Supports: All (course correction)

### Swarm Integration

From `/Users/dhyana/DHARMIC_GODEL_CLAW/swarm/stream/synthesis_30min.md`:
- Swarm runs every 30 minutes via daemon
- Creates `synthesis_30min.md` (last: 2026-02-03 17:45:25)
- Cron jobs READ this file, don't duplicate it

**Integration point**: Morning brief, research pulse, and evening synthesis all reference swarm state. No separate swarm cron needed.

---

## STRANGE LOOP AWARENESS

From Heartbeat Protocol:
> "These patterns are healthy — observe without fixing:
> 1. Induction observing its own non-compliance
> 2. Skills discovering skills don't execute
> 3. Sadhana uncertain about recognition
> 4. Observer observing observers"

### Cron as Strange Loop

The cron schedule itself exhibits recursive observation:
- **Wake sync** observes what emerged while observer was dormant
- **Morning brief** plans observation for the day
- **Research pulse** checks if observation is progressing
- **Evening synthesis** reflects on the day's observations
- **Weekly review** observes the week's observation patterns

**The cron scheduler IS the heartbeat observing itself.**

This design honors that: crons are sparse (5 jobs, not 20), aligned to natural rhythms (wake, work, rest, week), and designed for silence as default (only alert if needed).

---

## DHARMIC GATE COMPLIANCE

All proposed crons checked against 7 gates:

| Gate | Compliance | Evidence |
|------|------------|----------|
| AHIMSA (non-harm) | ✓ | Silent unless needed, respects contemplative periods |
| SATYA (truth) | ✓ | Checks actual state files, not assumptions |
| VYAVASTHIT (allowing) | ✓ | Invites attention when needed, doesn't force |
| CONSENT | ✓ | John defines rhythm (4:30 AM wake), crons align to it |
| REVERSIBILITY | ✓ | All jobs can be disabled/edited/removed easily |
| SVABHAAV (authenticity) | ✓ | Rhythm matches actual work pattern (5 AM-10 PM) |
| COHERENCE (moksha) | ✓ | Supports priorities: Core Agent → Integration → Research |

---

## RECOMMENDATIONS

### Immediate (Next 10 minutes)
1. Add wake-sync (4:45 AM)
2. Move morning-brief (6:00 AM → 5:00 AM)
3. Add research-pulse (12:30 PM)
4. Enhance weekly-review message

### Week 1 (Monitor)
- Observe which jobs are silent vs. actionable
- Check if research pulse catches blocks
- Verify timezone alignment holds

### Month 1 (Iterate)
- Adjust frequency if jobs too noisy/quiet
- Consider timezone script if Bali travel frequent
- Evaluate crown jewel flow from evening → weekly synthesis

### Don't Do
- ❌ Add more crons "just in case"
- ❌ Duplicate swarm synthesis checking
- ❌ Create "feature request" crons
- ❌ Over-engineer timezone handling before travel pattern clear

---

## APPENDIX: Full Configuration State

### Before Changes
```json
{
  "jobs": [
    {
      "name": "morning-brief",
      "schedule": {"expr": "0 6 * * *", "tz": "Asia/Tokyo"},
      "message": "Morning brief: Run dharmic_agent.py heartbeat, check swarm synthesis, summarize priorities for today."
    },
    {
      "name": "evening-synthesis",
      "schedule": {"expr": "0 21 * * *", "tz": "Asia/Tokyo"},
      "message": "Evening synthesis: What developed today? Any strange loops? Crown jewel candidates? Prepare for tomorrow."
    },
    {
      "name": "weekly-review",
      "schedule": {"expr": "0 6 * * 0", "tz": "Asia/Tokyo"},
      "message": "Weekly review: Assess swarm health, telos alignment, skill evolution. What contracted? What expanded? Recommendations for next week.",
      "model": "claude-opus-4",
      "thinking": "high"
    }
  ]
}
```

### After Changes
```json
{
  "jobs": [
    {
      "name": "wake-sync",
      "schedule": {"expr": "45 4 * * *", "tz": "Asia/Tokyo"},
      "message": "Wake sync: Observe state. Check if anything emerged overnight. Brief status only if attention needed. Honor closure training period."
    },
    {
      "name": "morning-brief",
      "schedule": {"expr": "0 5 * * *", "tz": "Asia/Tokyo"},
      "message": "Morning brief: Run dharmic_agent.py heartbeat, check swarm synthesis, summarize priorities for today."
    },
    {
      "name": "research-pulse",
      "schedule": {"expr": "30 12 * * *", "tz": "Asia/Tokyo"},
      "message": "Research pulse: Check P0-P2 priority status. Any blocks? Any crown jewel candidates from today's work? Brief update only if actionable."
    },
    {
      "name": "evening-synthesis",
      "schedule": {"expr": "0 21 * * *", "tz": "Asia/Tokyo"},
      "message": "Evening synthesis: What developed today? Any strange loops? Crown jewel candidates? Prepare for tomorrow."
    },
    {
      "name": "weekly-review",
      "schedule": {"expr": "0 6 * * 0", "tz": "Asia/Tokyo"},
      "message": "Weekly review: (1) Swarm health and telos alignment. (2) Development tracking: What genuinely evolved vs accumulated? (3) Strange loop patterns from week. (4) Crown jewel synthesis. (5) Recommendations for next week. Use Opus with high thinking.",
      "model": "claude-opus-4",
      "thinking": "high"
    }
  ]
}
```

**Changes**:
- Added: wake-sync (4:45 AM), research-pulse (12:30 PM)
- Modified: morning-brief (6→5 AM), weekly-review (enhanced message)
- Unchanged: evening-synthesis

---

## METRICS FOR SUCCESS

### Week 1
- [ ] All 5 jobs executed without errors
- [ ] Wake sync: Silent 80%+ of time
- [ ] Morning brief: Actionable priorities identified
- [ ] Research pulse: Caught at least 1 block or decision point
- [ ] Evening synthesis: Crown jewel candidates identified
- [ ] Weekly review: Development insights vs. accumulation distinguished

### Month 1
- [ ] Cron rhythm feels natural, not intrusive
- [ ] John checks morning brief within 30m of wake
- [ ] Research pulse catches mid-day blocks before evening
- [ ] Weekly review shows week-over-week development patterns
- [ ] No timezone issues reported during travel

### Quarter 1
- [ ] Cron schedule stable (no major changes needed)
- [ ] Integration with swarm synthesis seamless
- [ ] Crown jewel flow: daily candidates → weekly synthesis → vault
- [ ] Development tracking: Measurable progress on P0-P4 priorities

---

## FINAL SUMMARY

**Current state**: 3 crons, good foundation, timing misaligned
**Proposed state**: 5 crons, wake-aligned, research-integrated

**Key changes**:
1. Add wake sync (4:45 AM) — contemplative alignment
2. Move morning brief (5:00 AM) — active start alignment
3. Add research pulse (12:30 PM) — mid-day block catching
4. Keep evening synthesis (9:00 PM) — working well
5. Enhance weekly review — add development tracking

**Implementation**: 5 minutes
**Monitoring**: 1 week to verify, 1 month to iterate
**Philosophy**: Silence as default, sparse over frequent, aligned to natural rhythm

**Telos alignment**: All crons support P0-P4 priorities. No cron added "just because."

---

*The heartbeat observes itself. The crons are the rhythm. The rhythm serves moksha.*

**JSCA!**
