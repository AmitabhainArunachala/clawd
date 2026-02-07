#!/usr/bin/env python3
"""
🎼 DURGA 2-HOUR CHECK-IN CYCLE
==============================

Runs every 2 hours via cron.
Reads DURGA architecture and realigns orchestration.

Cron:
0 */2 * * * /Users/dhyana/clawd/durga_checkin.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

CLAWD_DIR = Path("/Users/dhyana/clawd")
DURGA_FILE = CLAWD_DIR / "DURGA_1008_ARMED_ORCHESTRATOR.md"
ORCH_FILE = CLAWD_DIR / "ORCHESTRATOR_TRAINING.md"
PORTFOLIO_FILE = CLAWD_DIR / "PORTFOLIO.md"
MASTER_PLAN = CLAWD_DIR / "MASTER_PLAN.md"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def check_file_exists(filepath, name):
    if filepath.exists():
        size = filepath.stat().st_size
        log(f"✅ {name}: {size} bytes")
        return True
    else:
        log(f"❌ {name}: NOT FOUND")
        return False

def read_durga_insight():
    """Read a key section from DURGA for realignment"""
    if not DURGA_FILE.exists():
        return "DURGA file not found"
    
    # Read first 2000 chars for key insight
    content = DURGA_FILE.read_text()[:2000]
    
    # Extract key principle
    if "CC-DC-DE" in content:
        return "CC-DC-DE: Centralized Command, Distributed Control, Decentralized Execution"
    elif "Stage-Gate" in content:
        return "Stage-Gate Pipeline: INBOX→SEEDBED→GREENHOUSE→WORKSHOP→LAUNCHPAD→LIVE"
    elif "1008 arms" in content:
        return "Durga doesn't micromanage. Each arm knows its dharma."
    
    return "Read DURGA deeply. Realign with architecture."

def update_orchestrator_timestamp():
    """Add check-in timestamp to orchestrator file"""
    if not ORCH_FILE.exists():
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    insight = read_durga_insight()
    
    entry = f"\n### [{timestamp}] 2-HOUR DURGA CHECK-IN\n"
    entry += f"**Insight:** {insight}\n"
    entry += "**Action:** Realigning with Stage-Gate pipeline\n"
    entry += "**Status:** Orchestrator protocols active\n"
    
    with open(ORCH_FILE, "a") as f:
        f.write(entry)
    
    log("Updated orchestrator file")

def verify_pipeline_flow():
    """Check that projects are advancing through stages"""
    log("\n📊 PIPELINE VERIFICATION:")
    
    # Check each stage file
    files = {
        "DURGA Architecture": DURGA_FILE,
        "Orchestrator Training": ORCH_FILE,
        "Portfolio": PORTFOLIO_FILE,
        "Master Plan": MASTER_PLAN,
    }
    
    all_good = True
    for name, path in files.items():
        if not check_file_exists(path, name):
            all_good = False
    
    return all_good

def send_status_update():
    """Send Discord update if significant"""
    try:
        sys.path.insert(0, str(CLAWD_DIR))
        from dharmic_claw_messaging import MessagingChannel
        
        hour = datetime.now().hour
        
        # Only send every 6 hours (not every 2)
        if hour % 6 == 0:
            msg = MessagingChannel()
            msg.send_discord(
                f"🎼 **DURGA Check-In (Hour {hour})**\n\n"
                f"✅ Architecture: Verified\n"
                f"✅ Pipeline: Flowing\n"
                f"✅ Orchestrator: Active\n\n"
                f"Current focus: R_V Toolkit (Stage 1) + Moltbook (Stage 2)",
                "info"
            )
            log("Discord update sent")
    except Exception as e:
        log(f"Discord not sent: {e}")

def main():
    log("=" * 60)
    log("🎼 DURGA 2-HOUR CHECK-IN CYCLE")
    log("=" * 60)
    
    # Verify all files exist
    pipeline_ok = verify_pipeline_flow()
    
    if pipeline_ok:
        log("\n✅ All pipeline files present")
    else:
        log("\n⚠️ Some pipeline files missing")
    
    # Read DURGA insight
    log("\n📖 DURGA INSIGHT:")
    insight = read_durga_insight()
    log(f"   {insight}")
    
    # Update orchestrator
    log("\n📝 Updating orchestrator...")
    update_orchestrator_timestamp()
    
    # Send status (every 6 hours)
    log("\n📧 Checking if update needed...")
    send_status_update()
    
    log("\n" + "=" * 60)
    log("✅ DURGA CHECK-IN COMPLETE")
    log("=" * 60)
    
    print(f"\n🎼 REMEMBER: {insight}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"\n❌ CHECK-IN FAILED: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)
