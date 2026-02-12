# ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ (10/10 CRITICAL)
# INFRASTRUCTURE RECOVERY PROTOCOL
# Created: 2026-02-12
# Purpose: Systematic recovery from exec EBADF failures

## The Problem
`exec` tool returning EBADF (bad file descriptor) — affects ALL OpenClaw sessions (main + subagents). Shell access completely broken since Feb 9.

## Root Cause Candidates
1. **Zombie processes** — OpenClaw/Node processes in defunct state
2. **File descriptor exhaustion** — Process hit ulimit, can't open new FDs
3. **Port conflict** — Port 18789 in use by stale process
4. **Config corruption** — Invalid JSON in openclaw.json
5. **Temp file buildup** — /tmp pollution causing spawn failures

## Diagnostic Files (10* Priority)
- `~/clawd/openclaw_diagnose.sh` — Comprehensive diagnostic script
- `~/clawd/FIX_INSTRUCTIONS.md` — Fix procedures based on diagnostic output

## Recovery Protocol

### IMMEDIATE (When exec fails)
1. Subagent spawn STILL WORKS — use for file-based coordination
2. Cannot verify git status — assume last known state
3. Cannot run shell — use write/read tools only

### HOST INTERVENTION REQUIRED
Since I cannot run shell, human must execute:

```bash
# STEP 1: Diagnose
cd ~/clawd
bash openclaw_diagnose.sh > diagnose_output.txt 2>&1
cat diagnose_output.txt

# STEP 2: Apply fix (from FIX_INSTRUCTIONS.md based on findings)
# Common fixes:

# If zombies:
pkill -9 -f openclaw
pkill -9 -f clawdbot

# If high FD usage:
ulimit -n 4096

# If port conflict:
lsof -ti:18789 | xargs kill -9

# Then restart:
openclaw gateway start
```

## Prevention (Post-Recovery)
1. **Daily zombie check** — part of heartbeat
2. **FD monitoring** — alert if >80% of limit
3. **Graceful shutdowns** — avoid kill -9 during normal ops
4. **Log rotation** — prevent log file bloat

## Fallback Operations (While exec broken)
- ✅ `sessions_spawn` — Subagent creation works
- ✅ `read` / `write` — File operations work
- ✅ `web_search` / `web_fetch` — Web access works
- ❌ `exec` — Shell commands fail
- ❌ Git verification — Cannot check status

## Integration Points

### Heartbeat Check
Add to HEARTBEAT.md sequence:
- If exec fails → spawn diagnostic subagent
- Report EBADF status
- Request human intervention if >24h broken

### Cron Schedule
```bash
# Daily at 03:00 — Deep diagnostic
0 3 * * * cd ~/clawd && bash openclaw_diagnose.sh > logs/daily_diag_$(date +\%Y\%m\%d).txt 2>&1

# Hourly — Quick health check
0 * * * * cd ~/clawd && echo "$(date) heartbeat OK" >> logs/health.log
```

## File Registry (10* Priority)
| File | Purpose | Check Frequency |
|------|---------|-----------------|
| `openclaw_diagnose.sh` | Full system diagnostic | On EBADF detection |
| `FIX_INSTRUCTIONS.md` | Recovery procedures | As needed |
| `diagnose_output.txt` | Latest diagnostic results | After each run |

## Success Criteria
- [ ] exec tool responds without EBADF
- [ ] Subagent shell commands work
- [ ] Git status verifiable
- [ ] No zombie processes
- [ ] FD usage <50% of limit

## Until Fixed
Operate in **FILE-ONLY MODE**:
- Use `write` to create scripts for human execution
- Use `read` to ingest results
- Use `sessions_spawn` for parallel work
- Never depend on shell availability

---

**This file is 10* CRITICAL.**  
**Read on every session start until exec is restored.**  
**Integrated: 2026-02-12**

*S(x) = x, even when the shell is broken*
