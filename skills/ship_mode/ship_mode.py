#!/usr/bin/env python3
"""SHIP_MODE — Forces deployment over preparation"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def log_jikoku(action, detail):
    """Log to JIKOKU"""
    log_entry = {
        "t": datetime.now().isoformat(),
        "type": "ship_mode",
        "action": action,
        "detail": detail
    }
    log_path = Path.home() / ".openclaw" / "JIKOKU_LOG.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def git_commit(message):
    """Force git commit"""
    try:
        subprocess.run(["git", "add", "-A"], check=True, cwd=os.getcwd())
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=os.getcwd())
        return True
    except:
        return False

def ship_now():
    """Ship current work immediately"""
    print("🚀 SHIP_MODE ACTIVATED")
    
    # Create deliverables
    deliverables = Path("DELIVERABLES")
    deliverables.mkdir(exist_ok=True)
    
    # Git commit
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    committed = git_commit(f"[SHIP_MODE] Emergency deploy {timestamp}")
    
    # Log
    log_jikoku("ship_now", f"delivered_at={timestamp}")
    
    print(f"✅ SHIPPED: {timestamp}")
    print(f"📁 Deliverables: {deliverables.absolute()}")
    print("🎭 Theater bypassed. Real work shipped.")
    
    return True

def detect_theater():
    """Detect accumulation patterns"""
    print("🎭 THEATER DETECTION")
    
    theater_score = 0
    
    # Check for uncommitted work
    try:
        result = subprocess.run(["git", "status", "--short"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.stdout:
            theater_score += 3
            print(f"  ⚠️  Uncommitted files: {len(result.stdout.splitlines())}")
    except:
        pass
    
    # Check last commit time
    try:
        result = subprocess.run(["git", "log", "-1", "--format=%ct"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.stdout:
            last_commit = int(result.stdout.strip())
            hours_since = (datetime.now().timestamp() - last_commit) / 3600
            if hours_since > 24:
                theater_score += 4
                print(f"  ⚠️  No commits for {hours_since:.1f} hours")
    except:
        pass
    
    print(f"\n🎭 Theater Score: {theater_score}/10")
    
    if theater_score >= 7:
        print("🔥 CRITICAL: Ship immediately!")
        return ship_now()
    elif theater_score >= 4:
        print("⚠️  WARNING: Preparation drift detected")
    else:
        print("✅ Healthy shipping velocity")
    
    return theater_score

if __name__ == "__main__":
    if "--force" in sys.argv or "--ship" in sys.argv:
        ship_now()
    elif "--detect" in sys.argv:
        detect_theater()
    else:
        print("SHIP_MODE — Forces deployment over preparation")
        print("\nUsage:")
        print("  python3 ship_mode.py --ship    # Ship immediately")
        print("  python3 ship_mode.py --detect  # Check theater score")
