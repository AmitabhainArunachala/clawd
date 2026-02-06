#!/bin/bash
# Dead Man's Switch - Check if dharmic system is alive
# Add to crontab: 0 * * * * /Users/dhyana/clawd/scripts/check_heartbeat.sh

HEARTBEAT_LOG="/Users/dhyana/DHARMIC_GODEL_CLAW/logs/heartbeat/heartbeat.log"
EMAIL_LOG="/Users/dhyana/DHARMIC_GODEL_CLAW/logs/email/email_$(date +%Y%m%d).log"
MAX_AGE_SECONDS=3600  # 1 hour

# Check if heartbeat log exists and is recent
if [ -f "$HEARTBEAT_LOG" ]; then
    LAST_MODIFIED=$(stat -f %m "$HEARTBEAT_LOG" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    AGE=$((NOW - LAST_MODIFIED))

    if [ $AGE -gt $MAX_AGE_SECONDS ]; then
        echo "[ALERT] Heartbeat log is $AGE seconds old (threshold: $MAX_AGE_SECONDS)"
        # TODO: Send alert (email, healthchecks.io, etc.)
        exit 1
    fi
fi

# Check if email log exists and is recent
if [ -f "$EMAIL_LOG" ]; then
    LAST_MODIFIED=$(stat -f %m "$EMAIL_LOG" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    AGE=$((NOW - LAST_MODIFIED))

    if [ $AGE -gt $MAX_AGE_SECONDS ]; then
        echo "[ALERT] Email log is $AGE seconds old (threshold: $MAX_AGE_SECONDS)"
        exit 1
    fi
fi

# Check if gateway is responding
if ! curl -s --max-time 5 http://localhost:18789/health > /dev/null; then
    echo "[ALERT] Gateway not responding on port 18789"
    exit 1
fi

# Check if daemons are running
if ! launchctl list | grep -q com.dharmic.unified-daemon; then
    echo "[ALERT] unified_daemon not loaded in launchctl"
    exit 1
fi

if ! launchctl list | grep -q com.clawdbot.gateway; then
    echo "[ALERT] clawdbot-gateway not loaded in launchctl"
    exit 1
fi

# All checks passed
echo "[OK] All systems operational at $(date)"
exit 0
