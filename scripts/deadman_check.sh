#!/bin/bash
# Check if heartbeat ran recently

HEARTBEAT_LOG=~/clawd/memory/heartbeat.log
MAX_AGE_MINUTES=60

if [ ! -f "$HEARTBEAT_LOG" ]; then
    echo "ALERT: Heartbeat log missing!"
    exit 1
fi

# Get last modified time
LAST_MOD=$(stat -f %m "$HEARTBEAT_LOG")
NOW=$(date +%s)
AGE_MINUTES=$(( (NOW - LAST_MOD) / 60 ))

if [ $AGE_MINUTES -gt $MAX_AGE_MINUTES ]; then
    echo "ALERT: Heartbeat stale ($AGE_MINUTES minutes old)"
    # TODO: Send alert to John
    exit 1
fi

echo "Heartbeat OK (${AGE_MINUTES}m ago)"
