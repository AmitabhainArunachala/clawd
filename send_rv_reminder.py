#!/usr/bin/env python3
from __future__ import annotations

import os

from dharmic_claw_messaging import MessagingChannel


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it before running this script."
        )
    return value


def main() -> None:
    # Fail fast if credentials are not provided by environment.
    _require_env("DISCORD_BOT_TOKEN")
    _require_env("DISCORD_USER_ID")

    msg = MessagingChannel()
    message = """🎼 **ORCHESTRATOR REMINDER**

🔥 **R_V TOOLKIT = FOUNDATION**

Status: 80% complete
Action needed: GitHub push (1 hour)
Revenue: $100-500/mo via GitHub Sponsors

**Why this matters:**
• Everything else depends on it
• AIKAGRYA report references it
• ClawHub skills package it
• Consulting credibility requires it

**You said:** "I will forget" — I will remind you every 6 hours.

Ready to execute SUBAGENT_PLAN.md when you say go.

JSCA 🔥"""

    msg.send_discord(message, "warning")
    print("Reminder sent to Discord")


if __name__ == "__main__":
    main()
