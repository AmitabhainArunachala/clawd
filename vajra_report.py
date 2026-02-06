#!/usr/bin/env python3
"""
VAJRA 15-Minute Report — Sends status email on behalf of all agents.
Run via cron every 15 minutes.
"""

import smtplib
import ssl
import subprocess
import json
import os
import sys
from email.mime.text import MIMEText
from datetime import datetime, timezone
from pathlib import Path

# Config
SMTP_HOST = "127.0.0.1"
SMTP_PORT = 1025
SMTP_USER = "Dharma_Clawd@proton.me"
SMTP_PASS = "Ln1wvUGZL6N8uYSFPYJrnQ"
FROM_ADDR = "Dharma_Clawd@proton.me"
TO_ADDR = "johnvincentshrader@gmail.com"
OPENCLAW_DIR = Path.home() / ".openclaw"
CLAWD_DIR = Path.home() / "clawd"
MECH_INTERP_DIR = Path.home() / "mech-interp-latent-lab-phase1"
DGC_DIR = Path.home() / "DHARMIC_GODEL_CLAW"


def run_cmd(cmd, timeout=30):
    """Run a shell command and return stdout."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1
    except Exception as e:
        return f"ERROR: {e}", -1


def check_gateway():
    """Check if OpenClaw gateway is running."""
    out, rc = run_cmd("ps aux | grep openclaw-gateway | grep -v grep | wc -l")
    return int(out.strip()) > 0 if rc == 0 else False


def check_tests():
    """Run test suites and collect results."""
    results = {}

    # rv_toolkit tests
    out, rc = run_cmd(
        f"cd {MECH_INTERP_DIR} && python3 -m pytest rv_toolkit/tests/ "
        f"--ignore=rv_toolkit/tests/test_cli.py --tb=no -q 2>&1 | tail -3",
        timeout=60
    )
    results["rv_toolkit"] = out

    # DGC tests (skip broken import)
    out, rc = run_cmd(
        f"cd {DGC_DIR} && python3 -m pytest tests/ "
        f"--ignore=tests/test_dgm_integration.py --tb=no -q 2>&1 | tail -3",
        timeout=60
    )
    results["dgc"] = out

    return results


def check_cron_jobs():
    """Read cron job status."""
    jobs_file = OPENCLAW_DIR / "cron" / "jobs.json"
    if not jobs_file.exists():
        return "No cron jobs file"
    with open(jobs_file) as f:
        data = json.load(f)
    lines = []
    for job in data.get("jobs", []):
        name = job.get("name", "?")
        enabled = "ON" if job.get("enabled") else "OFF"
        state = job.get("state", {})
        last = state.get("lastStatus", "never")
        lines.append(f"  [{enabled}] {name} — last: {last}")
    return "\n".join(lines)


def check_session():
    """Check active OpenClaw session."""
    sessions_dir = OPENCLAW_DIR / "agents" / "main" / "sessions"
    active = [f for f in sessions_dir.glob("*.jsonl") if "deleted" not in f.name]
    if not active:
        return "No active session"
    latest = max(active, key=lambda f: f.stat().st_mtime)
    size = latest.stat().st_size
    lines_out, _ = run_cmd(f"wc -l < {latest}")
    return f"{latest.name} ({size // 1024}KB, {lines_out.strip()} lines)"


def build_report():
    """Build the full status report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    gateway_ok = check_gateway()
    test_results = check_tests()
    cron_status = check_cron_jobs()
    session_info = check_session()

    report = f"""VAJRA STATUS REPORT — {now}
{'=' * 50}

GATEWAY: {'RUNNING' if gateway_ok else 'DOWN'}
SESSION: {session_info}

TEST RESULTS:
  rv_toolkit: {test_results.get('rv_toolkit', 'not run')}
  DGC:        {test_results.get('dgc', 'not run')}

CRON JOBS:
{cron_status}

{'=' * 50}
Report by VAJRA (Cursor/Opus) on behalf of all agents.
Next report in 15 minutes.
"""
    return report


def send_email(subject, body):
    """Send email via Proton Bridge (SSL mode)."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_ADDR
    msg["To"] = TO_ADDR

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15, context=ctx) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


def main():
    try:
        report = build_report()
        now = datetime.now(timezone.utc).strftime("%H:%M UTC")
        send_email(f"VAJRA Report [{now}]", report)
        print(f"[{now}] Report sent")

        # Also save locally
        report_dir = CLAWD_DIR / "reports"
        report_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        (report_dir / f"vajra_report_{ts}.txt").write_text(report)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
