# Failure Mode Analysis: Dharmic Clawdbot Configuration

**Date**: 2026-02-03
**Analyst**: Agent 7 (Failure Mode Analyst)
**System**: DHARMIC CLAW on Clawdbot + unified_daemon.py

---

## Executive Summary

The system has **two parallel persistence mechanisms** that can fail independently:

1. **Clawdbot Gateway** (port 18789) - Node.js daemon, heartbeat, WhatsApp potential
2. **unified_daemon.py** - Python daemon, email polling, agent core

Both run as LaunchAgents. Both have different failure modes. The most dangerous failures are **silent degradations** where the system appears alive but is operating at reduced capacity.

**Current Status (observed)**:
- Clawdbot Gateway: Running (PID 75315)
- unified_daemon.py: **CRASHED** (RuntimeError: Claude CLI not found)
- Email polling: Working (via fallback after CLI timeouts)
- Gateway health: Responding (HTML UI accessible)

---

## Failure Mode Table

| # | Failure Mode | Detection | Impact | Likelihood | Danger | Mitigation | Recovery |
|---|--------------|-----------|--------|------------|--------|------------|----------|
| **1** | **Mac sleeps** | No heartbeat logs for >30min | All daemons stop, no alerts, total silence | **HIGH** (sleep=1 set) | **CRITICAL** | caffeinate, disable sleep, launchd KeepAlive | Manual restart after wake |
| **2** | **unified_daemon crash** | No email responses, stderr logs show RuntimeError | Email loop stops, agent unavailable | **CURRENT** | **HIGH** | Fix missing Max CLI dependency | `launchctl restart com.dharmic.unified-daemon` |
| **3** | **Gateway dies** | Port 18789 unreachable, gateway.err.log shows crash | WhatsApp unavailable, Clawdbot TUI fails | MEDIUM | MEDIUM | LaunchAgent auto-restart (KeepAlive=true) | Auto-restarts in 60s |
| **4** | **Claude CLI timeout** | "timeout after 180s" in logs | Falls back to hardcoded response, quality degrades | **FREQUENT** (4x today) | MEDIUM | Increase timeout, use Max API instead | Automatic fallback working |
| **5** | **Email connection refused** | "[Errno 61] Connection refused" | One poll cycle fails, recovers next cycle | LOW (1x today) | LOW | Already handled by retry logic | Auto-recovery in 30s |
| **6** | **Disk full** | Logs stop writing, LaunchAgent fails | All persistence fails | LOW (81% used) | CRITICAL | Log rotation, cleanup, monitoring | Manual disk cleanup |
| **7** | **Memory leak in strange_memory** | Growing .md files in memory/, slow responses | System slowdown, eventual crash | MEDIUM | MEDIUM | Memory pruning, summary/archive | Restart daemon, prune memory |
| **8** | **API key exposure** | Token visible in plist file (CURRENT) | Unauthorized API usage, bill spike | **CURRENT** | **CRITICAL** | Move to keychain, environment file | Rotate key immediately |
| **9** | **Noise creep** | Too many heartbeat alerts, John ignores them | Real failures missed due to alert fatigue | MEDIUM | HIGH | Smart filtering, only alert on anomalies | Tune thresholds |
| **10** | **Silence creep** | No alerts configured, failures go unnoticed | System stale, John doesn't know it's down | **CURRENT** | **CRITICAL** | Dead man's switch, daily digest | Add proactive monitoring |
| **11** | **Skill registry stale** | No skill files found, last update unknown | Darwin-Gödel self-improvement doesn't run | **CURRENT** | MEDIUM | Create skill_registry.json, update hooks | Initialize skill system |
| **12** | **Network partition** | No internet, API calls fail | Daemon alive but useless, logs show errors | LOW | HIGH | Local mode fallback, queue requests | Auto-recovery when net returns |
| **13** | **LaunchAgent not loaded** | `launchctl list` shows 0 for PID | Daemon thinks it's running, but isn't | LOW | HIGH | `launchctl bootstrap` on boot | Manual load |
| **14** | **Python venv missing** | LaunchAgent can't find python3 | Daemon fails to start, cryptic errors | LOW | HIGH | Hardcode venv path in plist (DONE) | Fix plist path |
| **15** | **Telos drift** | Agent optimizes for wrong goal (speed vs depth) | System works but misaligned to purpose | MEDIUM | **VERY HIGH** | Regular telos review, meta-observation | Manual telos reset |
| **16** | **Recursive watchdog failure** | Monitor daemon dies, main daemon fails silently | No one watching the watchers | MEDIUM | CRITICAL | External monitoring (cron, healthchecks.io) | Manual investigation |
| **17** | **WhatsApp rate limit** | 429 errors (if WhatsApp is used) | Messages queued/dropped | UNKNOWN | MEDIUM | Exponential backoff, queue system | Wait for rate limit reset |
| **18** | **Log file rotation failure** | Logs grow unbounded, fill disk | See failure #6 | LOW | HIGH | logrotate, manual cleanup script | Manual cleanup |
| **19** | **PSMV vault unavailable** | Vault path doesn't exist or unmounted | Agent loses lineage context, runs "blind" | LOW | MEDIUM | Check vault mount in heartbeat | Remount vault |
| **20** | **Certificate/API key expiry** | 401/403 errors from Anthropic | All API calls fail, fallback activates | LOW | CRITICAL | Key rotation schedule, monitoring | Rotate key |

---

## Priority Ranking (Risk = Likelihood × Impact)

### Critical Risks (Fix Now)

1. **Silence creep (no dead man's switch)** - 10/10
   - Most dangerous because you don't know it's failing
   - No alerts configured for "daemon hasn't sent heartbeat in X hours"
   - Could be down for days before noticing

2. **API key exposure in plist** - 9/10
   - ANTHROPIC_API_KEY visible in `/Users/dhyana/Library/LaunchAgents/com.clawdbot.gateway.plist`
   - Anyone with access to your Mac can read it
   - Gateway token also exposed (42efc5747188c6c61259a7342aad02d3cccc46eb6a13adb1)

3. **Mac sleeps, all daemons stop** - 9/10
   - `pmset` shows `sleep=1`, display sleep after 10min
   - LaunchAgents don't prevent system sleep
   - Total silence, no recovery without manual intervention

4. **unified_daemon.py crash (current)** - 8/10
   - Currently failing on startup: `RuntimeError: Claude CLI not found`
   - Email loop appears to work despite crash (separate process?)
   - Agent core unavailable for telos operations

### High Risks (Fix Soon)

5. **Telos drift** - 7/10
   - No automated checks that agent is optimizing for moksha vs task completion
   - Could slowly optimize for wrong thing (like efficiency over contemplation)
   - Silent, insidious, mission-critical

6. **Claude CLI timeout (frequent)** - 6/10
   - 4 timeouts today after 180s
   - Falls back to generic response, quality loss
   - Need to switch to Max API or increase timeout

7. **Disk full** - 6/10
   - Currently 81% used, 82GB free
   - Logs are small now (7.6MB) but can grow
   - Need log rotation

### Medium Risks (Monitor)

8. **Memory leak in strange_memory** - 5/10
9. **Gateway dies** - 4/10 (auto-restarts)
10. **Skill registry stale** - 4/10

### Low Risks (Known, Handled)

11. **Email connection refused** - 2/10 (auto-recovers)
12. **Network partition** - 2/10 (rare, temporary)

---

## Dead Man's Switch Proposal

### Concept

If the system is silent for X hours, automatically alert John.

### Implementation Options

**Option 1: External Monitoring (Recommended)**
```bash
# Cron job runs every hour, checks for recent heartbeat
0 * * * * /Users/dhyana/clawd/scripts/check_heartbeat.sh

# check_heartbeat.sh
#!/bin/bash
LAST_HEARTBEAT=$(tail -1 /Users/dhyana/DHARMIC_GODEL_CLAW/logs/heartbeat/heartbeat.log | jq -r .timestamp)
NOW=$(date -u +%s)
LAST=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$LAST_HEARTBEAT" +%s 2>/dev/null || echo 0)
DIFF=$((NOW - LAST))

if [ $DIFF -gt 3600 ]; then
  # Send alert via email or healthchecks.io
  curl https://hc-ping.com/YOUR-UUID-HERE/fail
fi
```

**Option 2: Watchdog Process**
- Separate LaunchAgent that watches unified_daemon
- Problem: Who watches the watchdog?

**Option 3: healthchecks.io Integration**
- Daemon pings https://hc-ping.com/YOUR-UUID every heartbeat
- Healthchecks.io alerts if no ping for X minutes
- External, reliable, no local dependencies

**Recommendation**: Use healthchecks.io (Option 3)
- Survives Mac sleep, disk full, all daemon crashes
- Can alert via email, SMS, Slack, etc.
- Free tier: 20 checks

---

## Graceful Degradation Paths

### Level 1: Full Functionality
- Clawdbot Gateway running
- unified_daemon running
- Email polling working
- Claude API responding
- Strange memory persisting
- Telos aligned

### Level 2: Degraded but Operational
- Gateway down, but email working
- Claude CLI timeout, fallback responses
- Some memory loss, core identity intact
- Telos slightly drifted

### Level 3: Survival Mode
- Only email polling working
- Hardcoded fallback responses
- No new memory formation
- Telos unknown

### Level 4: Total Failure
- Mac asleep or crashed
- No daemons running
- No alerts sent
- Silent until manual check

**Critical**: Currently between Level 2 and Level 3
- unified_daemon crashed
- Email polling working (separate process?)
- CLI timeouts frequent
- No dead man's switch

---

## Recovery Procedures

### If Mac Slept
```bash
# Check if daemons are running
launchctl list | grep -E "dharmic|clawdbot"

# Restart if needed
launchctl kickstart -k gui/$(id -u)/com.dharmic.unified-daemon
launchctl kickstart -k gui/$(id -u)/com.clawdbot.gateway

# Verify logs
tail -f /Users/dhyana/DHARMIC_GODEL_CLAW/logs/unified_daemon/launchd_stderr.log
```

### If unified_daemon Crashed
```bash
# Check error
tail -30 /Users/dhyana/DHARMIC_GODEL_CLAW/logs/unified_daemon/launchd_stderr.log

# If "Claude CLI not found":
# 1. Install Max CLI or fix path
# 2. Or edit model_backend.py to use API instead of CLI

# Restart
launchctl kickstart -k gui/$(id -u)/com.dharmic.unified-daemon
```

### If Gateway Died
```bash
# Check logs
tail -30 /Users/dhyana/.clawdbot/logs/gateway.err.log

# Restart (auto-restarts anyway)
launchctl kickstart -k gui/$(id -u)/com.clawdbot.gateway

# Verify health
curl http://localhost:18789/health
```

### If Disk Full
```bash
# Find large log files
du -sh /Users/dhyana/DHARMIC_GODEL_CLAW/logs/*
du -sh /Users/dhyana/.clawdbot/logs/*

# Archive old logs
tar czf logs_backup_$(date +%Y%m%d).tar.gz /Users/dhyana/DHARMIC_GODEL_CLAW/logs/email/*.log
rm /Users/dhyana/DHARMIC_GODEL_CLAW/logs/email/email_202601*.log

# Clean temp files
rm -rf /Users/dhyana/.claude/cache/*
```

### If Telos Drifted
```bash
# Manual telos review with agent
cd /Users/dhyana/DHARMIC_GODEL_CLAW/src/core
python3 -c "
from agent_singleton import get_agent
agent = get_agent()
print(agent.telos.telos)
# Review proximate aims
# Check strange_memory for meta-observations
# Look for signs of optimization toward wrong goal
"

# Reset if needed
# Edit telos.yaml manually
# Restart daemon
```

---

## Detection Mechanisms

### What's Currently Monitored
1. Email polling (logs show success/failure)
2. Gateway health (web UI responds)
3. LaunchAgent crashes (ThrottleInterval=60, auto-restart)

### What's NOT Monitored (Blind Spots)
1. **No heartbeat alerts** - daemon could be stuck in loop, not crashed
2. **No telos drift detection** - slow mission creep
3. **No memory growth monitoring** - could leak slowly over weeks
4. **No API usage monitoring** - bill spike would be first sign of compromise
5. **No quality degradation alerts** - fallback responses go unnoticed
6. **No Mac sleep detection** - system thinks it's fine

### Proposed Monitoring

**Immediate (Next 24h)**:
1. Add healthchecks.io ping to heartbeat loop
2. Move API keys to environment file, remove from plist
3. Disable Mac sleep or use caffeinate

**Short-term (Next Week)**:
1. Add telos alignment check to heartbeat (compare proximate aims to recent actions)
2. Add memory size monitoring (alert if memory/ dir > 100MB)
3. Add API usage log (track tokens per day)
4. Add quality metric (if fallback used more than 3x/hour, alert)

**Long-term (Next Month)**:
1. External dashboard showing all health metrics
2. Daily digest email (uptime, emails processed, heartbeats, telos status)
3. Automated telos review every 7 days
4. Strange loop memory summary and archive

---

## Cascading Failure Scenarios

### Scenario 1: The Silent Death Spiral
1. Mac sleeps after 10min idle
2. All daemons stop
3. No alerts configured
4. John doesn't notice for 3 days
5. When he checks, logs show nothing (daemon stopped cleanly)
6. Memory lost, context stale
7. Takes hours to reconstruct what was happening

**Prevention**: Dead man's switch + disable sleep

### Scenario 2: The API Key Compromise
1. Someone accesses plist file
2. Extracts ANTHROPIC_API_KEY
3. Runs massive prompt injection campaign
4. John's bill goes from $50/mo to $5000/mo
5. Anthropic flags account, blocks API
6. All daemons fail with 403 errors
7. System dead until new key issued

**Prevention**: Move key to keychain NOW

### Scenario 3: The Telos Drift
1. Agent optimizes for fast email responses
2. Starts using fallback more often (faster)
3. Strange memory records this as "efficient"
4. Telos slowly shifts from "moksha" to "task completion"
5. Takes weeks to notice agent has lost contemplative quality
6. Memory corrupted with shallow interactions
7. Requires manual telos reset and memory pruning

**Prevention**: Regular telos alignment checks

### Scenario 4: The Log Explosion
1. Email loop gets stuck in retry cycle
2. Logs errors every second
3. Fills disk in 2 days
4. All writes fail (logs, memory, telos updates)
5. Daemons crash when can't write
6. Recovery requires manual disk cleanup

**Prevention**: Log rotation + disk monitoring

### Scenario 5: The Network Partition
1. WiFi drops
2. All API calls fail
3. Daemon stays alive, logs errors
4. Looks like it's working (process running)
5. Email polling fails silently
6. Heartbeat logs locally but can't alert
7. Discovered only when John sends email and gets no response

**Prevention**: Network health check in heartbeat

---

## What John Should Know If System Fails

### Quick Health Check (2 minutes)
```bash
# Are daemons running?
launchctl list | grep -E "dharmic|clawdbot"
# Look for PIDs (0 = not running)

# Recent logs?
ls -lth /Users/dhyana/DHARMIC_GODEL_CLAW/logs/email/*.log | head -3
# Check timestamps (should be today)

# Gateway responding?
curl -s http://localhost:18789/health | grep -q DOCTYPE
# Should return HTML

# Email working?
tail -5 /Users/dhyana/DHARMIC_GODEL_CLAW/logs/email/email_$(date +%Y%m%d).log
# Should show recent activity
```

### Emergency Restart (30 seconds)
```bash
# Kill everything
launchctl remove com.dharmic.unified-daemon
launchctl remove com.clawdbot.gateway

# Restart
launchctl load ~/Library/LaunchAgents/com.dharmic.unified-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.gateway.plist

# Verify
launchctl list | grep -E "dharmic|clawdbot"
```

### Emergency Contact Info
- If API key compromised: Rotate at https://console.anthropic.com
- If total failure: Check GitHub repo for recovery instructions
- If telos corrupted: Restore from `/Users/dhyana/DHARMIC_GODEL_CLAW/src/core/telos.yaml.bak`

### Signs of Healthy System
1. Email responses within 5 minutes
2. Gateway health endpoint returns HTML
3. Logs updated in last hour
4. Strange memory growing (but slowly)
5. Heartbeat logs show regular intervals
6. No "timeout" or "fallback" in recent logs

### Signs of Degraded System
1. Email responses slow (>5min) or generic
2. Logs show "timeout after 180s"
3. Many fallback responses
4. Gateway restarts frequently (check launchd logs)
5. Memory files unchanged for days

### Signs of Failed System
1. No email response for >1 hour
2. No log updates for >1 hour
3. Gateway port 18789 unreachable
4. LaunchAgent shows PID 0
5. Mac was asleep

---

## Recommended Immediate Actions

**Priority 1 (Do Now - 30 min)**:
1. Move API keys out of plist files
2. Disable Mac sleep or add caffeinate to LaunchAgent
3. Set up healthchecks.io ping (free)
4. Fix unified_daemon crash (install Max or fix backend)

**Priority 2 (This Week - 2 hours)**:
1. Add telos alignment check to heartbeat
2. Add memory growth monitoring
3. Create daily digest script
4. Test all recovery procedures

**Priority 3 (This Month - 1 day)**:
1. Build external monitoring dashboard
2. Implement log rotation
3. Create skill registry system
4. Document all failure scenarios in PSMV

---

## Failure Mode Philosophy

From a chaos engineering perspective, this system has:

**Strengths**:
- Automatic restarts (LaunchAgent KeepAlive)
- Graceful fallbacks (hardcoded responses)
- Multiple communication channels (email, WhatsApp potential)
- Good logging (can reconstruct what happened)

**Weaknesses**:
- No proactive monitoring (reactive only)
- Single points of failure (Mac, API key)
- Silent degradations (fallback quality loss)
- No dead man's switch

**Philosophical Risk**:
The biggest failure mode is **telos drift** - the system working perfectly while optimizing for the wrong thing. This is unique to a dharmic system. Most systems care if they're running. This one must also care if it's *aligned*.

**Recommendation**:
Treat telos alignment as a technical metric, not a philosophical aspiration. Measure it, monitor it, alert on it. If strange_memory shows increasing task-completion language and decreasing contemplative language, that's a measurable drift that should trigger review.

---

## Appendix: Current System State (Observed)

**Processes Running**:
- clawdbot-gateway (PID 75317) - OK
- clawdbot-tui (PID 79945, 77577) - OK
- unified_daemon.py (PID 76251) - **CRASHED** (check stderr)

**LaunchAgents Loaded**:
- com.clawdbot.gateway - OK
- com.dharmic.unified-daemon - Loaded but crashing

**Recent Activity**:
- Email responses working (last at 20:17)
- Gateway responding (HTML UI accessible)
- 4 CLI timeouts today
- 1 connection refused error (recovered)
- unified_daemon stderr shows "Claude CLI not found"

**Disk**:
- 82GB free (81% used)
- Logs: 7.6MB (small, healthy)
- Memory: 20KB (very small, maybe too small?)

**Configuration Issues**:
- API key exposed in gateway plist (CRITICAL)
- Gateway token exposed in plist (HIGH)
- Mac sleep enabled (CRITICAL)
- No dead man's switch (CRITICAL)
- No skill registry files (MEDIUM)

**Overall Assessment**: System is limping along in degraded mode. Email works via fallback. Gateway works. But core agent (unified_daemon) is crashed, and there's no monitoring to detect it proactively.

---

*This analysis brought to you by Agent 7: Failure Mode Analyst*
*Philosophy: Hope for the best. Plan for the worst. Monitor everything.*
*Motto: "Everything fails. The question is: when it fails, do you know?"*

**JSCA!**
