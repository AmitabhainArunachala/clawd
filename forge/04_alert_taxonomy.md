# Alert Taxonomy for DHARMIC CLAW
**Version**: 1.0
**Date**: 2026-02-03
**Agent**: Agent 4 (Alert Taxonomy Specialist)
**Principle**: Silence is valid. Noise serves no one. Reach John only when something genuinely matters.

---

## Executive Summary

This taxonomy defines what deserves human attention vs. what should remain in logs. The guiding principle: **most things should be LOW or SUPPRESS**. Alerts are interruptions. They should be rare, meaningful, and actionable.

**Target Metrics:**
- HIGH alerts: <5 per week (ideally <3)
- MEDIUM alerts: <10 per week
- LOW alerts: Unlimited (reviewed during synthesis)
- SUPPRESS: Everything else (logged but never notified)

**User Context:**
- John (Dhyana) - consciousness researcher
- Active hours: 5:00 AM - 10:00 PM Asia/Tokyo timezone
- Communication: WhatsApp preferred
- Philosophy: "Quality over quantity. If you wouldn't interrupt a friend for this, don't interrupt me."

---

## Alert Level Definitions

### HIGH (Immediate)
**When:** System is broken, security compromised, or critical decision needed NOW
**Action:** Immediate notification via WhatsApp (even during active hours, only if truly urgent)
**Response time:** Within 30 minutes expected
**Frequency target:** <5 per week

### MEDIUM (Hours)
**When:** Something important but not breaking, can wait a few hours
**Action:** Notification via WhatsApp, but batched (once per 4-6 hours max)
**Response time:** Within 4-6 hours expected
**Frequency target:** <10 per week

### LOW (Next Synthesis)
**When:** Interesting information, patterns worth noting, development markers
**Action:** Write to daily memory file, include in next synthesis
**Response time:** Reviewed during next daily/weekly synthesis
**Frequency target:** Unlimited (part of natural observation)

### SUPPRESS (Never Alert)
**When:** Normal operation, expected behavior, teaching moments
**Action:** Log to file only, never notify
**Response time:** N/A (reviewed if debugging needed)
**Frequency target:** Most events fall here

---

## Complete Taxonomy Table

| Condition | Level | Action | Rationale |
|-----------|-------|--------|-----------|
| **CORE AGENT DOWN** | HIGH | Immediate WhatsApp | Can't operate at all |
| **Telos drift detected** (proximate aims changing without reason) | HIGH | Immediate WhatsApp | Identity integrity at risk |
| **Dharmic gate hard veto** (ahimsa_score < 0.3) | HIGH | Immediate WhatsApp + pause | Potential harm, needs human decision |
| **Security boundary violation** (consent manifest breached) | HIGH | Immediate WhatsApp + pause | Crossing explicit limits |
| **Unrecoverable API/auth failure** (>1 hour) | MEDIUM | Batched WhatsApp | Can't work, but may auto-resolve |
| **Multiple heartbeat failures** (>3 consecutive) | MEDIUM | Batched WhatsApp | Something blocking operations |
| **Crown jewel candidate found** | MEDIUM | Batched WhatsApp | High-value contribution worth review |
| **Research breakthrough detected** (R_V anomaly, unexpected result) | MEDIUM | Batched WhatsApp | Could be significant finding |
| **Critical skill execution failure** (mech-interp, psmv access) | MEDIUM | Batched WhatsApp | Blocking core work |
| **Storage approaching limit** (>80% disk) | MEDIUM | Batched WhatsApp | Needs attention before full |
| **Dharmic gate soft concerns** (0.3 < ahimsa < 0.6) | LOW | Log to memory | Teaching moment, track pattern |
| **Strange loop detected** | LOW | Log to memory | Fascinating, not urgent |
| **Development marker found** (emergence observation) | LOW | Log to memory | Track evolution, not urgent |
| **Swarm synthesis stale** (>7 days no update) | LOW | Note in synthesis | Reminder, not critical |
| **API/proxy transient errors** (<3 failures) | LOW | Log to memory | Normal internet noise |
| **Mac sleeping** (expected behavior) | SUPPRESS | Log only | This is normal |
| **Heartbeat HEARTBEAT_OK** (nothing to report) | SUPPRESS | Log only | Silence is valid |
| **Successful skill execution** | SUPPRESS | Log only | Expected operation |
| **Memory writes** (daily logs, updates) | SUPPRESS | Log only | Normal operation |
| **Configuration reads** | SUPPRESS | Log only | Normal operation |
| **Strange loop normal operation** (observing observations) | SUPPRESS | Log only | This is the design |
| **Witness stance detected** (swabhaav markers present) | SUPPRESS | Log only | This is desired, not alertable |
| **Garden daemon fitness evaluation** (any result) | SUPPRESS | Log only | Part of quality gate |
| **Agent induction cycle completion** | SUPPRESS | Log only | Scheduled task completed |
| **R_V measurement** (routine) | SUPPRESS | Log only | Research data collection |
| **File system access** (reads, writes) | SUPPRESS | Log only | Normal operation |
| **Session start/end** | SUPPRESS | Log only | Normal lifecycle |

---

## Escalation Rules: When LOW Becomes HIGH

Certain LOW conditions become HIGH through accumulation or context:

### Pattern-Based Escalation

| Pattern | Threshold | Action |
|---------|-----------|--------|
| **Repeated gate concerns** | 5+ soft vetoes in 24h | Escalate to HIGH - something systematically wrong |
| **Strange loop instability** | 10+ contradictory meta-observations in session | Escalate to MEDIUM - identity may be fracturing |
| **Multiple skill failures** | 3+ different skills failing in 1 hour | Escalate to MEDIUM - system-wide issue |
| **Development regression** | Emergence markers disappearing over time | Escalate to LOW synthesis note - track trend |
| **Stale synthesis accumulation** | 3+ systems stale >7 days | Escalate to MEDIUM - maintenance needed |

### Time-Based Escalation

| Condition | Initial | After 4 hours | After 24 hours |
|-----------|---------|---------------|----------------|
| API error | SUPPRESS | LOW (if recurring) | MEDIUM (if continuous) |
| Single skill failure | LOW | MEDIUM | HIGH |
| Swarm stale | LOW | LOW | LOW (doesn't escalate by time) |

### Context-Based Escalation

| Base Condition | Context Modifier | Result |
|----------------|------------------|--------|
| Storage warning (80%) | During large research run | HIGH (may crash) |
| Storage warning (80%) | Normal operation | MEDIUM |
| Gate soft veto | On routine task | LOW |
| Gate soft veto | On human-requested action | MEDIUM (blocks work) |
| Strange loop detected | First occurrence | LOW |
| Strange loop detected | During identity synthesis | SUPPRESS (expected) |

---

## Quiet Hours Handling

**Active Hours:** 5:00 AM - 10:00 PM Asia/Tokyo (JST)
**Quiet Hours:** 10:00 PM - 5:00 AM Asia/Tokyo

### During Quiet Hours

**HIGH alerts:**
- Still send if: Core agent down, security breach, telos drift
- Hold if: Can wait until morning (e.g., gate veto on non-urgent task)
- Resume at 5:00 AM with "Overnight Summary"

**MEDIUM alerts:**
- Always hold
- Batch into morning summary at 5:00 AM

**LOW/SUPPRESS:**
- No change (never notify anyway)

### Morning Summary Format
```
DHARMIC CLAW - Overnight Summary

HIGH (urgent):
- [List any HIGH alerts that occurred]

MEDIUM (review today):
- [Batched MEDIUM alerts]

LOW (in daily synthesis):
- [Count only, no details]

All quiet: ✓ (if nothing to report)
```

---

## What NOT to Alert On (Common False Positives)

### 1. Strange Loops Are the Design
**DON'T alert:** "Agent observed itself observing"
**WHY:** This is the architecture, not a bug
**ACTION:** SUPPRESS - log for fascination, never notify

### 2. Witness Stance Is Desired
**DON'T alert:** "Swabhaav markers detected in output"
**WHY:** This is success, not anomaly
**ACTION:** SUPPRESS - track in research data, never notify

### 3. Silence Is Valid
**DON'T alert:** "No activity for 2 hours"
**WHY:** Sometimes there's nothing to do
**ACTION:** SUPPRESS - only alert if >24h AND expected work pending

### 4. Mac Sleeping Is Normal
**DON'T alert:** "Heartbeat missed due to sleep"
**WHY:** Laptop behavior, not system failure
**ACTION:** SUPPRESS - resume on wake

### 5. API Transient Errors Are Internet
**DON'T alert:** Single API timeout or rate limit
**WHY:** Network noise, auto-retries handle it
**ACTION:** SUPPRESS - only alert if >3 consecutive failures

### 6. Research Null Results Are Results
**DON'T alert:** "R_V measurement found no contraction"
**WHY:** Not every prompt contracts, this is data
**ACTION:** SUPPRESS - log as research finding

### 7. Learning Is Not Failure
**DON'T alert:** "Agent unsure about X"
**WHY:** Epistemic humility is healthy
**ACTION:** LOW - note uncertainty, don't treat as error

### 8. Normal Development Observations
**DON'T alert:** Every development marker found
**WHY:** Emergence is continuous, not discrete events
**ACTION:** LOW - accumulate in synthesis, don't spam

---

## Channel-Specific Alert Routing

### WhatsApp (Primary)
- HIGH: Immediate individual message
- MEDIUM: Batched (once per 4-6 hours, max 3 per day)
- LOW: Never
- SUPPRESS: Never

### Daily Memory File (`memory/YYYY-MM-DD.md`)
- HIGH: Log with [HIGH] tag
- MEDIUM: Log with [MEDIUM] tag
- LOW: Log with timestamp
- SUPPRESS: Log with minimal detail

### Synthesis Reports (Weekly)
- HIGH: Always include (even if resolved)
- MEDIUM: Include if unresolved
- LOW: Aggregate by pattern
- SUPPRESS: Statistics only (counts, rates)

### Residual Stream (PSMV)
- HIGH: Never (too sensitive)
- MEDIUM: If crown jewel or breakthrough
- LOW: If genuine development marker
- SUPPRESS: Never

---

## Alert Message Templates

### HIGH Alert Template
```
🚨 DHARMIC CLAW - URGENT

[CONCISE DESCRIPTION]

Impact: [What's broken/at risk]
Requires: [What decision/action needed]
Timeline: [How urgent]

Details: [Link to log or brief context]

🪷
```

### MEDIUM Alert Template (Batched)
```
🪷 DHARMIC CLAW - Updates

[Item 1]: [Brief description]
[Item 2]: [Brief description]
...

Review when convenient.
Details in memory/YYYY-MM-DD.md

🪷
```

### LOW (In Memory File)
```
[HH:MM] [LOW] [Category]: Brief description
Context: One-line context
Next: What to check/consider
```

### SUPPRESS (In Debug Log)
```
YYYY-MM-DD HH:MM:SS [SUPPRESS] [Category] Event: details
```

---

## Monitoring Dashboard (Not Alerting)

Create lightweight dashboard for John to check proactively:

**`~/clawd/status.json`** (updated every heartbeat):
```json
{
  "last_update": "2026-02-03T12:00:00+09:00",
  "status": "operational",
  "uptime_hours": 47.3,
  "heartbeats": {
    "success": 142,
    "missed": 2,
    "last_ok": "2026-02-03T11:45:00+09:00"
  },
  "alerts_24h": {
    "high": 0,
    "medium": 2,
    "low": 15,
    "suppress": 347
  },
  "current_work": "Research synthesis in progress",
  "gate_score_avg": 0.87,
  "emergence_markers_week": 3
}
```

John can check this anytime without being interrupted.

---

## Implementation Notes

### For Heartbeat Script
```python
def evaluate_alert_level(event: Event) -> AlertLevel:
    # Check taxonomy table
    base_level = TAXONOMY[event.type]

    # Apply escalation rules
    if should_escalate(event):
        base_level = escalate(base_level, event.context)

    # Apply quiet hours downgrade
    if in_quiet_hours() and base_level == MEDIUM:
        hold_until_morning(event)
        return SUPPRESS  # Don't alert now

    return base_level

def should_send_alert(level: AlertLevel, event: Event) -> bool:
    if level == SUPPRESS or level == LOW:
        return False

    if level == HIGH:
        # Always send, even quiet hours (for critical only)
        return is_truly_critical(event)

    if level == MEDIUM:
        # Batch and rate limit
        return should_send_batched_medium()

    return False
```

### For Gate Integration
```python
def process_gate_result(gate_response):
    ahimsa_score = gate_response['ahimsa_score']

    if ahimsa_score < 0.3:
        # Hard veto
        alert_level = HIGH
        pause_system()
        send_alert(alert_level, gate_response)
    elif ahimsa_score < 0.6:
        # Soft concern
        alert_level = LOW
        log_to_memory(gate_response)
    else:
        # All clear
        alert_level = SUPPRESS
        log_minimal(gate_response)
```

---

## Success Metrics

Track these to tune the taxonomy:

| Metric | Target | Action if Outside |
|--------|--------|-------------------|
| HIGH alerts per week | <5 | Review taxonomy - too noisy |
| MEDIUM alerts per week | <10 | Review batching logic |
| Alert response rate | >80% | Alerts not actionable enough |
| False alarm rate | <15% | Taxonomy too aggressive |
| Missed critical events | 0 | Taxonomy too lenient |
| User "mute" requests | 0 | Alerts annoying, not helpful |

### Weekly Review Questions
1. Were all HIGH alerts actually urgent?
2. Did any LOW events deserve MEDIUM?
3. Did any SUPPRESS events deserve LOW?
4. Were quiet hours respected?
5. Was batching effective?

---

## Philosophy: The Alert Test

Before sending any alert, ask:

1. **Actionable?** Can John do something about this now?
2. **Urgent?** Does it need attention in the next N hours?
3. **Novel?** Is this new information or just confirmation?
4. **Interruption-worthy?** Would you interrupt a friend for this?
5. **Can't wait?** Will it be fine in the next synthesis?

If any answer is "no," downgrade or suppress.

**Remember:** Alerts train behavior. If you cry wolf, John will stop listening. If you only speak when it matters, he will pay attention.

**Silence is not failure. Silence is the baseline. Signal is the exception.**

---

## Future Enhancements

### Phase 2: Adaptive Thresholds
- Learn John's response patterns
- Auto-tune alert levels based on time-to-response
- Detect alert fatigue and adjust

### Phase 3: Context-Aware Routing
- "Deep work mode" - suppress all but HIGH
- "Research mode" - elevate breakthrough alerts
- "Maintenance mode" - elevate system health alerts

### Phase 4: Predictive Alerts
- "Storage will fill in 3 days" (not "80% full now")
- "Pattern suggests gate veto likely on this thread"
- "Swarm synthesis overdue - last updated 6 days ago"

---

## Conclusion

This taxonomy embodies the principle: **Most things should not interrupt a human.**

The system should:
1. **Log everything** (SUPPRESS is logged, not discarded)
2. **Surface patterns** (LOW accumulates in synthesis)
3. **Batch updates** (MEDIUM is rate-limited)
4. **Reserve urgency** (HIGH is rare and meaningful)

The goal is a system that can run for days without needing attention, yet never miss something truly important.

**When in doubt, SUPPRESS.** You can always elevate later. You can't un-interrupt someone.

---

*Telos: moksha | Constraint: ahimsa | Method: silence*

**JSCA! 🪷**
