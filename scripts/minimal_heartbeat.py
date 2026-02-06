#!/usr/bin/env python3
"""
Minimal Heartbeat for DHARMIC CLAW

ONE check: Telos alignment.
Output: Silent unless drift detected.

Run every 30 minutes via cron.
"""

from pathlib import Path
from datetime import datetime
import yaml

CLAWD_DIR = Path.home() / "clawd"
TELOS_FILE = Path.home() / "DHARMIC_GODEL_CLAW/config/telos.yaml"
MEMORY_DIR = CLAWD_DIR / "memory"
LOG_FILE = MEMORY_DIR / "heartbeat.log"

def check_telos_alignment() -> tuple[bool, str]:
    """
    The ONE check that matters.

    Returns:
        (aligned: bool, reason: str)
    """

    # Read telos
    if not TELOS_FILE.exists():
        return True, "No telos file (probably okay)"

    with open(TELOS_FILE) as f:
        telos = yaml.safe_load(f)

    # Read last 5 actions from today's memory
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = MEMORY_DIR / f"{today}.md"

    if not memory_file.exists():
        return True, "No actions today"

    # Simple heuristic: Check for keywords that violate moksha
    # (Can be sophisticated later if needed)
    with open(memory_file) as f:
        content = f.read().lower()

    # Red flags (add as needed based on actual drift)
    red_flags = [
        "performance rather than presence",
        "complexity for complexity",
        "noise without signal",
        "forcing rather than allowing",
        "spam",
        "unnecessary alert",
    ]

    for flag in red_flags:
        if flag in content:
            return False, f"Telos drift: {flag}"

    return True, "Aligned"

def log_heartbeat(status: str, details: str = ""):
    """Append to heartbeat log (silent file write)."""
    timestamp = datetime.now().isoformat()
    LOG_FILE.parent.mkdir(exist_ok=True)

    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} | {status} | {details}\n")

def alert_john(message: str):
    """
    Alert John about telos drift.

    TODO: Implement actual notification (email/telegram)
    For now: just print and log
    """
    print(f"ALERT: {message}")
    log_heartbeat("ALERT_SENT", message)

    # Write to alert file that John can check
    alert_file = CLAWD_DIR / "ALERTS.txt"
    with open(alert_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {message}\n")

def main():
    """Run the minimal heartbeat check."""
    try:
        aligned, reason = check_telos_alignment()

        if aligned:
            # Silent success (95% of heartbeats)
            log_heartbeat("HEARTBEAT_OK", reason)
        else:
            # Telos drift detected (rare, should be < 1%)
            log_heartbeat("TELOS_DRIFT", reason)
            alert_john(f"Telos drift detected: {reason}")

    except Exception as e:
        # Log errors but don't crash
        log_heartbeat("ERROR", str(e))
        print(f"Heartbeat error: {e}")

if __name__ == "__main__":
    main()
