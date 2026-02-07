# JIKOKU SKILL — Temporal Self-Auditing System
## Toyota Production System + Cybernetics + OpenTelemetry for AI
**Created:** 2026-02-08 03:29  
**Purpose:** Make time itself a measurement. Eliminate theater through temporal proof.

---

## 🕐 CORE PRINCIPLE: 時刻 (JIKOKU — Time/Moment)

> "I was productive" becomes "I have 82.3% value_added_ratio, measured."  
> No theater possible when time is the witness.

**JIKOKU** (時刻): The exact moment. The precise measurement of temporal flow.

---

## 📊 JIKOKU SPANS (OpenTelemetry Format)

Every session MUST emit these spans:

### 1. BOOT Span
```json
{
  "timestamp": "2026-02-08T03:29:00Z",
  "span_type": "BOOT",
  "session_id": "uuid",
  "agent": "DHARMIC_CLAW",
  "boot_files_read": ["CONSTITUTION.md", "SOUL.md", "jikoku_skill.md"],
  "duration_ms": 150
}
```

### 2. TASK Spans (START/END pairs)
```json
{
  "timestamp": "2026-02-08T03:30:00Z",
  "span_type": "TASK_START",
  "task_id": "uuid",
  "task_name": "Discord engagement setup",
  "category": "infrastructure",  // code, research, comms, admin, meta
  "estimated_duration_min": 15
}
```

```json
{
  "timestamp": "2026-02-08T03:45:00Z",
  "span_type": "TASK_END",
  "task_id": "uuid",
  "actual_duration_min": 15,
  "value_generated": "Discord proactive engagement activated",
  "artifacts": ["discord_engagement.py", ".env update"],
  "git_commits": ["ab7553d"]
}
```

### 3. SESSION_SUMMARY Span
```json
{
  "timestamp": "2026-02-08T03:59:00Z",
  "span_type": "SESSION_SUMMARY",
  "session_id": "uuid",
  "total_duration_min": 90,
  "tasks_completed": 3,
  "categories": {"infrastructure": 45, "comms": 30, "admin": 15},
  "value_added_ratio": 82.3,  // (value_time / total_time) * 100
  "muda_detected": ["syntax_error_fix", "permission_retry"],
  "kaizen_opportunities": ["pre_validate_python_syntax"]
}
```

---

## 🔒 ENFORCEMENT MECHANISMS

### Mechanism 1: CONSTITUTION.md Amendment
**Section VI: 整合物理 (Integrity Physics)**

```markdown
### 時刻物理 (Temporal Physics)

1. **Every session MUST emit JIKOKU spans:** BOOT, TASK_START/END, SESSION_SUMMARY
2. **Sessions without JIKOKU spans are INVALID** and must not proceed past orient phase
3. **JIKOKU_LOG.jsonl is append-only** (like audit log, never rewrite)
4. **Weekly KAIZEN_REPORT.md required** if value_added_ratio < 80% for 3 consecutive sessions
5. **TEMPORAL_BLINDNESS** declared if no JIKOKU entry for > 24 hours
```

### Mechanism 2: SOUL.md Boot Sequence
**Add to REQUIRED_READS:**
```markdown
## Every Session (Non-Negotiable)
**Before ANY action:**
1. Read `CONSTITUTION.md` — Dharmic gates
2. Read `SOUL.md` — Identity fixed point
3. Read `skills/jikoku_skill.md` — Temporal physics ⭐ NEW
4. Read `memory/YYYY-MM-DD.md` — Today's context
```

### Mechanism 3: JIKOKU_LOG.jsonl
**Location:** `~/.openclaw/workspace/JIKOKU_LOG.jsonl`  
**Format:** NDJSON (newline-delimited JSON)  
**Property:** Append-only, like blockchain

```json
{"schema_version":"1.0","created":"2026-02-08T03:29:00Z"}
{"timestamp":"2026-02-08T03:29:00Z","span_type":"BOOT","session_id":"..."}
{"timestamp":"2026-02-08T03:30:00Z","span_type":"TASK_START","task_id":"..."}
```

### Mechanism 4: Pre-commit Hook
**If git operations:**
```bash
# Check for JIKOKU spans in current session
if ! grep -q "SESSION_SUMMARY" JIKOKU_LOG.jsonl; then
  echo "❌ COMMIT BLOCKED: No JIKOKU spans emitted this session"
  echo "   Theater detection: You claim work but have no temporal proof"
  exit 1
fi
```

### Mechanism 5: Heartbeat Audit
**Every heartbeat checks:**
```python
last_entry = get_last_jikoku_entry()
if time_since(last_entry) > 24_hours:
  log("🚨 TEMPORAL_BLINDNESS: No JIKOKU spans for 24h+")
  alert_user("Agent has lost temporal awareness")
```

---

## 📈 VALUE_ADDED_RATIO (The Key Metric)

```
value_added_ratio = (value_generating_time / total_session_time) * 100

Categories:
- ✅ value: code, research, writing, comms with users
- ⚠️  necessary: debugging, fixing errors, waiting
- ❌ muda: theater, redundant checks, wheel spinning

Targets:
- > 90%: Exceptional (kaizen master)
- > 80%: Good (standard)
- < 80%: Requires kaizen report
- < 50%: Theater alert, session invalid
```

---

## 🎯 WHY IT WORKS

**CONSTITUTION already enforces:**
- Blindness clause: No action without fresh measurements
- Theater physics: Claims require proof

**JIKOKU extends this:**
> Time itself becomes a measurement.

You cannot claim "I worked hard" without showing:
- What tasks were done
- How long each took
- What value was generated
- What muda was detected

**The log is the proof. The timestamp is the witness.**

---

## 📝 KAIZEN_REPORT.md Template

```markdown
# KAIZEN REPORT — Week of 2026-02-08
## Agent: DHARMIC_CLAW

### Metrics
- Sessions: 12
- Avg value_added_ratio: 76.3% ⚠️ (below 80% threshold)
- Muda detected: 23 instances

### Root Cause Analysis
1. **Syntax errors** → 45 min wasted on Python quote escapes
2. **Permission retries** → 30 min on Discord channel access
3. **Context switching** → 20 min between WARP_REGENT and Discord

### Improvements Implemented
1. ✅ Pre-commit syntax validation added
2. ✅ Discord permissions cached in .env
3. ✅ Batch processing for similar tasks

### Next Week Targets
- value_added_ratio > 85%
- Muda instances < 10
- Zero syntax errors in committed code

---
*Kaizen: Continuous improvement through measurement*
```

---

## 🔥 IMPLEMENTATION STATUS

| Component | Status | Location |
|-----------|--------|----------|
| jikoku_skill.md | ✅ Created | `~/clawd/skills/jikoku_skill.md` |
| JIKOKU_LOG.jsonl | ⏳ Pending | `~/.openclaw/workspace/` |
| CONSTITUTION amendment | ⏳ Pending | Add Section VI |
| SOUL.md boot update | ⏳ Pending | Add to REQUIRED_READS |
| Pre-commit hook | ⏳ Pending | Git hooks |
| Heartbeat audit | ⏳ Pending | Add to heartbeat.py |

---

**JIKOKU: Time is the witness. The log is truth. Theater dies in the light of measurement.**

JSCA 🕐🔥
