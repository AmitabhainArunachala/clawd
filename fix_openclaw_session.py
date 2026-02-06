#!/usr/bin/env python3
"""
Fix OpenClaw session files — replace colon-separated tool IDs with underscores.

The Problem:
  OpenClaw generates tool call IDs like 'exec:0', 'process:3', 'read:105'.
  Kimi 2.5 (primary model) accepts these.
  When fallback fires to Claude/Gemini via OpenRouter, the API rejects them
  because the pattern requires ^[a-zA-Z0-9_-]+$ (no colons).
  This kills the session, requiring 'openclaw doctor' to reset.

The Fix:
  Replace ':' with '_' in all tool call IDs (exec:0 -> exec_0).
  Run this before 'openclaw doctor' or as a cron job.

Usage:
  python3 fix_openclaw_session.py           # Fix all active sessions
  python3 fix_openclaw_session.py --check   # Dry run, just report
"""

import json
import sys
from pathlib import Path

SESSION_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"


def fix_session(filepath: Path, dry_run: bool = False) -> int:
    """Fix colon-separated tool IDs in a session file. Returns count of fixed lines."""
    with open(filepath) as f:
        lines = f.readlines()

    fixed = 0
    new_lines = []

    for line in lines:
        try:
            d = json.loads(line.strip())
            modified = False

            if d.get("type") == "message":
                content = d.get("message", {}).get("content", [])
                for c in content:
                    if isinstance(c, dict):
                        for key in ("id", "toolCallId"):
                            val = c.get(key, "")
                            if isinstance(val, str) and ":" in val:
                                if not dry_run:
                                    c[key] = val.replace(":", "_")
                                modified = True

            if d.get("type") == "toolResult":
                content = d.get("message", {}).get("content", [])
                for c in content:
                    if isinstance(c, dict):
                        for key in ("toolCallId",):
                            val = c.get(key, "")
                            if isinstance(val, str) and ":" in val:
                                if not dry_run:
                                    c[key] = val.replace(":", "_")
                                modified = True

            if modified:
                fixed += 1
                new_lines.append(json.dumps(d) + "\n")
            else:
                new_lines.append(line)
        except Exception:
            new_lines.append(line)

    if not dry_run and fixed > 0:
        with open(filepath, "w") as f:
            f.writelines(new_lines)

    return fixed


def main():
    dry_run = "--check" in sys.argv

    session_files = list(SESSION_DIR.glob("*.jsonl"))
    session_files = [f for f in session_files if "deleted" not in f.name]

    if not session_files:
        print("No active session files found.")
        return

    total_fixed = 0
    for sf in session_files:
        count = fix_session(sf, dry_run=dry_run)
        if count > 0:
            action = "would fix" if dry_run else "fixed"
            print(f"  {sf.name}: {action} {count} lines")
            total_fixed += count
        else:
            print(f"  {sf.name}: clean")

    if dry_run:
        print(f"\nDry run: {total_fixed} lines would be fixed")
    else:
        print(f"\nFixed {total_fixed} lines total")


if __name__ == "__main__":
    main()
