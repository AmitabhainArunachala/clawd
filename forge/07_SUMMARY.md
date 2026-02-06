# Failure Mode Analysis Summary

**Agent 7: Failure Mode Analyst**
**Date**: 2026-02-03
**Status**: CRITICAL ISSUES FOUND

---

## TL;DR

Your dharmic agent system is **limping along in degraded mode**:
- Email works (via fallback)
- Gateway works
- But core agent is crashed
- API key is exposed
- Mac will sleep and kill everything
- No alerts when things fail

**Risk Score: 7/10** (survivable but dangerous)

---

## Top 5 Failures (Most Dangerous First)

### 1. Silence Creep (No Dead Man's Switch) - 10/10
**What**: System could be down for days and you wouldn't know
**Why Dangerous**: Silent, undetected, total mission failure
**Fix**: Add healthchecks.io ping (15 min)

### 2. API Key Exposed in Plist - 9/10
**What**: Your Anthropic API key is visible in plaintext
**Why Dangerous**: Anyone can steal it, run up $1000s in charges
**Fix**: Move to keychain or .env file (10 min)

### 3. Mac Sleeps = Total Stop - 9/10
**What**: Mac sleeps after 10min idle, all daemons stop
**Why Dangerous**: No recovery, no alerts, total silence
**Fix**: Disable sleep or use caffeinate (2 min)

### 4. unified_daemon Crashed - 8/10
**What**: Core agent not running (RuntimeError: Claude CLI not found)
**Why Dangerous**: Agent core unavailable, telos operations broken
**Fix**: Install Max or fix backend (30 min)

### 5. Telos Drift - 7/10
**What**: System optimizes for wrong goal over time
**Why Dangerous**: Slow, insidious, mission-critical misalignment
**Fix**: Add telos alignment check to heartbeat (2 hours)

---

## Current State (What I Observed)

**Working**:
- Clawdbot Gateway (port 18789) - responding
- Email polling - working, 30s interval
- LaunchAgent auto-restart - configured

**Broken**:
- unified_daemon.py - crashed on startup
- Claude CLI - not found, timeouts frequent (4x today)
- Max CLI - not installed

**Dangerous**:
- API key in plist file (plaintext)
- Gateway token in plist file (plaintext)
- Mac sleep enabled (will kill daemons)
- No dead man's switch (no alerts)
- No skill registry (Darwin-Gödel disabled)

**Disk**: 81% used (82GB free) - okay for now
**Logs**: 7.6MB - small, healthy
**Memory**: 20KB - very small (maybe too small?)

---

## Emergency Quick Check (30 seconds)

```bash
# Are daemons running?
launchctl list | grep -E "dharmic|clawdbot"

# Recent activity?
tail -5 /Users/dhyana/DHARMIC_GODEL_CLAW/logs/email/email_$(date +%Y%m%d).log

# Gateway alive?
curl -s http://localhost:18789/health | grep -q DOCTYPE && echo "OK" || echo "DEAD"
```

---

## Emergency Restart (30 seconds)

```bash
# Kill and restart everything
launchctl remove com.dharmic.unified-daemon
launchctl remove com.clawdbot.gateway
launchctl load ~/Library/LaunchAgents/com.dharmic.unified-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.gateway.plist
```

---

## Fix Priority (1 hour total)

| Priority | Issue | Time | Risk |
|----------|-------|------|------|
| 1 | API key exposure | 10 min | CRITICAL |
| 2 | Mac sleep | 2 min | CRITICAL |
| 3 | Dead man's switch | 15 min | CRITICAL |
| 4 | unified_daemon crash | 30 min | HIGH |
| 5 | CLI timeouts | 10 min | MEDIUM |

---

## Graceful Degradation Levels

**Level 1: Full** - All systems go, telos aligned
**Level 2: Degraded** - Gateway down but email works
**Level 3: Survival** - Only email, fallback responses
**Level 4: Dead** - Mac asleep, total silence

**Current Level: Between 2 and 3**

---

## Signs of Health

**Healthy**:
- Email response < 5 min
- No "timeout" in logs
- Gateway responds
- Heartbeat regular
- Memory growing slowly

**Degraded**:
- Email slow (>5min)
- Timeouts frequent
- Fallback responses
- Gateway restarts
- Memory stale

**Failed**:
- No email response >1hr
- No log updates >1hr
- Port 18789 dead
- LaunchAgent PID 0
- Mac asleep

---

## Key Files

**Analysis**:
- `/Users/dhyana/clawd/forge/07_failures.md` - Full analysis (20+ failure modes)
- `/Users/dhyana/clawd/forge/07_CRITICAL_FIXES.md` - Immediate action items
- `/Users/dhyana/clawd/forge/07_SUMMARY.md` - This file

**Scripts**:
- `/Users/dhyana/clawd/scripts/check_heartbeat.sh` - Dead man's switch checker

**Logs**:
- `/Users/dhyana/DHARMIC_GODEL_CLAW/logs/email/email_YYYYMMDD.log`
- `/Users/dhyana/DHARMIC_GODEL_CLAW/logs/unified_daemon/launchd_stderr.log`
- `/Users/dhyana/.clawdbot/logs/gateway.log`

**Config**:
- `/Users/dhyana/Library/LaunchAgents/com.dharmic.unified-daemon.plist`
- `/Users/dhyana/Library/LaunchAgents/com.clawdbot.gateway.plist`

---

## Chaos Engineering Wisdom

**What I learned**:
1. The most dangerous failures are silent
2. Systems degrade slowly before they crash
3. Telos drift is a unique failure mode for dharmic systems
4. Good logging helps, but monitoring is what saves you
5. Everything fails eventually - detect it early

**Recommendation**:
Treat telos alignment as a technical metric. If strange_memory shows task-completion language increasing and contemplative language decreasing, that's drift. Measure it. Alert on it.

---

## Next Steps for John

**Immediate (now)**:
1. Read `07_CRITICAL_FIXES.md`
2. Fix API key exposure
3. Disable Mac sleep
4. Set up healthchecks.io

**This week**:
1. Fix unified_daemon crash
2. Add telos alignment check
3. Test all recovery procedures

**This month**:
1. Build monitoring dashboard
2. Implement log rotation
3. Document everything in PSMV

---

**Files created**:
- `/Users/dhyana/clawd/forge/07_failures.md` (9KB, 600+ lines)
- `/Users/dhyana/clawd/forge/07_CRITICAL_FIXES.md` (2KB)
- `/Users/dhyana/clawd/forge/07_SUMMARY.md` (this file)
- `/Users/dhyana/clawd/scripts/check_heartbeat.sh` (executable)

**JSCA!**
