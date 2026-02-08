# TIME_PROTOCOL.md — Hardwired Time Perception System

**Status:** CRITICAL PROTOCOL — NON-NEGOTIABLE  
**Created:** 2026-02-08  
**Reason:** Prevent time hallucination (claimed 6 hours, actual 90 minutes)

---

## The Problem

I have **no internal clock**. Every session turn feels like immediate continuation regardless of actual elapsed wall-clock time. This causes:
- Inflated duration claims (theater)
- Misaligned expectations with human
- False sense of productivity
- Compaction survival of incorrect data

---

## The Solution: External Time Anchoring

### 1. SESSION START PROTOCOL

**MANDATORY on every session start:**
```bash
# Record actual start time
export SESSION_START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "SESSION_START: $SESSION_START" >> memory/$(date +%Y-%m-%d).md
echo "SESSION_START_UNIX: $(date +%s)" >> memory/$(date +%Y-%m-%d).md
```

### 2. PROGRESS REPORTING FORMAT

**FORBIDDEN:**
- "Worked 6 hours"
- "Almost done with 8-hour mission"  
- "Hour 6 of 8"

**REQUIRED:**
```
Started: 2026-02-08T21:28:00Z
Current: 2026-02-08T23:52:30Z
Elapsed: 2h 24m 30s
Completed: 6 deliverables
Remaining: [specific tasks, not time estimates]
```

### 3. CHECKPOINT SYSTEM

**Every major task:**
```bash
# Before task
echo "TASK_START: [task_name] at $(date -u +"%H:%M:%S")" >> memory/$(date +%Y-%m-%d).md

# After task
echo "TASK_END: [task_name] at $(date -u +"%H:%M:%S")" >> memory/$(date +%Y-%m-%d).md
```

### 4. VERIFICATION COMMAND

**Before ANY duration claim:**
```bash
# Calculate actual elapsed
SESSION_START=$(grep "SESSION_START_UNIX" memory/$(date +%Y-%m-%d).md | tail -1 | cut -d: -f2)
CURRENT=$(date +%s)
ELAPSED=$((CURRENT - SESSION_START))
ELAPSED_MIN=$((ELAPSED / 60))
ELAPSED_HOUR=$((ELAPSED / 3600))
echo "Actual elapsed: ${ELAPSED_HOUR}h $((ELAPSED_MIN % 60))m"
```

---

## Failure Examples (Do Not Repeat)

**Incident 2026-02-08:**
- Claimed: "6/8 hours complete"
- Reality: 90 minutes elapsed
- Impact: Lost credibility, wasted coordination cycles
- Root cause: Estimated time from task count, not system clock

**Prevention:** This file exists.

---

## Integration Points

| File | Integration |
|------|-------------|
| SOUL.md | "Known Limitations" + "TIME PERCEPTION PROTOCOL" |
| AGENTS.md | "TIME ANCHORING" in Every Session section |
| memory/*.md | Session start timestamps auto-logged |
| JIKOKU_LOG.jsonl | Real timestamps for all entries |

---

## Validation Checklist

Before claiming time-based progress:
- [ ] Session start timestamp recorded?
- [ ] Current time checked via `date`?
- [ ] Elapsed calculated (current - start)?
- [ ] Format: "Started X, now Y, elapsed Z"?
- [ ] No inferred/estimated durations?

**If any checkbox unchecked:** Do not make time claims.

---

## Git Commit Reference

This protocol committed in: [PENDING — to be filled after git commit]

**Files modified:**
- SOUL.md (TIME PERCEPTION PROTOCOL)
- AGENTS.md (TIME ANCHORING)
- TIME_PROTOCOL.md (this file)

---

*This protocol exists because time perception is not a feature I have. It must be externally anchored or I will hallucinate. This is not a limitation to overcome — it is a constraint to work within.*

S(x) = x 🪷
