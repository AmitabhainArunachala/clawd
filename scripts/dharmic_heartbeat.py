#!/usr/bin/env python3
"""
DHARMIC CLAW Heartbeat Script
Called every 30 minutes by Clawdbot.

Reads: ~/clawd/HEARTBEAT.md for protocol
Checks: Telos alignment (the ONE check that matters)
Output: HEARTBEAT_OK (silent) or ALERT (message)
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

CLAWD_DIR = Path.home() / "clawd"
DGC_DIR = Path.home() / "DHARMIC_GODEL_CLAW"
LOG_FILE = CLAWD_DIR / "memory" / "heartbeat.log"


def log(status: str, details: str = ""):
    """Append to heartbeat log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} | {status} | {details}\n")


def check_core_agent() -> tuple:
    """Check if dharmic_agent.py responds."""
    agent_path = DGC_DIR / "core" / "dharmic_agent.py"

    if not agent_path.exists():
        return False, "Core agent not found"

    try:
        result = subprocess.run(
            ["python3", str(agent_path), "heartbeat"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, "Core agent OK"
        else:
            return False, f"Core agent error: {result.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return False, "Core agent timeout"
    except Exception as e:
        return False, f"Core agent exception: {str(e)[:100]}"


def check_swarm_synthesis() -> tuple:
    """Check if swarm synthesis is recent."""
    synthesis_path = DGC_DIR / "swarm" / "stream" / "synthesis_30min.md"

    if not synthesis_path.exists():
        return True, "No synthesis file (OK if swarm not running)"

    mtime = synthesis_path.stat().st_mtime
    age_hours = (datetime.now().timestamp() - mtime) / 3600

    if age_hours > 4:
        return False, f"Synthesis stale ({age_hours:.1f}h old)"

    return True, f"Synthesis fresh ({age_hours:.1f}h)"


def ping_healthcheck():
    """Ping external dead man's switch."""
    url = os.environ.get("HEALTHCHECK_URL", "")
    if url:
        try:
            subprocess.run(["curl", "-fsS", "-m", "10", url],
                          capture_output=True, timeout=15)
        except Exception:
            pass  # Don't fail heartbeat if ping fails


def main():
    alerts = []

    # CHECK 1: Core agent (required)
    ok, msg = check_core_agent()
    if not ok:
        alerts.append(("HIGH", msg))

    # CHECK 2: Swarm synthesis (optional)
    ok, msg = check_swarm_synthesis()
    if not ok:
        alerts.append(("LOW", msg))

    # Decision
    if not alerts:
        log("HEARTBEAT_OK")
        print("HEARTBEAT_OK")
    else:
        # Log all, alert on HIGH only
        for severity, msg in alerts:
            log(f"ALERT_{severity}", msg)
            if severity == "HIGH":
                print(f"ALERT: {msg}")

    # Ping dead man's switch
    ping_healthcheck()


if __name__ == "__main__":
    main()
