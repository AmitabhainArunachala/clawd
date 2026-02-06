#!/bin/bash
# Ping healthchecks.io to confirm Clawdbot is alive
# Called at end of each heartbeat

HEALTHCHECK_URL="${HEALTHCHECK_URL:-https://hc-ping.com/YOUR-UUID-HERE}"

if curl -fsS -m 10 --retry 3 "$HEALTHCHECK_URL" > /dev/null 2>&1; then
    echo "Healthcheck ping OK"
else
    echo "Healthcheck ping FAILED"
fi
