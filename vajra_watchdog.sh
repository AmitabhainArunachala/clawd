#!/usr/bin/env bash
# VAJRA Watchdog — Runs every 3 minutes via cron.
# Checks if OpenClaw gateway and agent are healthy. Restarts if stuck.

set -euo pipefail

LOG="/Users/dhyana/clawd/logs/watchdog.log"
mkdir -p "$(dirname "$LOG")"

GATEWAY_PORT=18789
GATEWAY_TOKEN="42efc5747188c6c61259a7342aad02d3cccc46eb6a13adb1"

ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }

log() { echo "[$(ts)] $1" >> "$LOG"; }

# 1. Check gateway process
if ! pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
    log "ALERT: Gateway process not running"
    # Could auto-restart here but safer to just log
    exit 1
fi

# 2. Check gateway responds
if ! curl -sf --max-time 5 \
    "http://127.0.0.1:${GATEWAY_PORT}/status" \
    -H "Authorization: Bearer ${GATEWAY_TOKEN}" > /dev/null 2>&1; then
    log "ALERT: Gateway not responding on port ${GATEWAY_PORT}"
    exit 1
fi

# 3. Check session freshness (warn if no activity for 30 min)
SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
ACTIVE=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | grep -v deleted | head -1)
if [ -n "$ACTIVE" ]; then
    MTIME=$(stat -f %m "$ACTIVE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    AGE=$(( (NOW - MTIME) / 60 ))
    if [ "$AGE" -gt 30 ]; then
        log "WARN: Active session stale (${AGE}m since last update)"
    fi
fi

# 4. Fix colon-separated tool IDs that crash fallback models
FIX_SCRIPT="/Users/dhyana/clawd/fix_openclaw_session.py"
if [ -f "$FIX_SCRIPT" ]; then
    FIXED=$(python3 "$FIX_SCRIPT" 2>/dev/null | grep "fixed" | grep -oE '[0-9]+' | head -1)
    if [ -n "$FIXED" ] && [ "$FIXED" -gt 0 ]; then
        log "FIX: Cleaned ${FIXED} lines with bad tool IDs (colon -> underscore)"
    fi
fi

# 5. CHAIWALA: Check message bus for sibling agent messages
CHAIWALA_CHECK="$HOME/.openclaw/workspace/check_chaiwala.py"
if [ -f "$CHAIWALA_CHECK" ]; then
    UNREAD=$(python3 "$CHAIWALA_CHECK" 2>/dev/null | grep -oE '[0-9]+ messages' | head -1 || echo "0 messages")
    if [ "$UNREAD" != "0 messages" ]; then
        log "CHAIWALA: $UNREAD waiting from sibling agents"
    fi
fi

log "OK: Gateway running, session active"
