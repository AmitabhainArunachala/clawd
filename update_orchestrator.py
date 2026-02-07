#!/usr/bin/env python3
"""
🎼 ORCHESTRATOR UPDATE CYCLE
============================

Runs every 3 hours via cron.
Updates ORCHESTRATOR_TRAINING.md with current status.

Cron:
0 */3 * * * /Users/dhyana/clawd/update_orchestrator.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

CLAWD_DIR = Path("/Users/dhyana/clawd")
TRAINING_FILE = CLAWD_DIR / "ORCHESTRATOR_TRAINING.md"
STATE_FILE = CLAWD_DIR / ".hourly_state.json"
MOLTBOOK_STATE = Path("/Users/dhyana/DHARMIC_GODEL_CLAW/moltbook_swarm/state.json")
MOLTBOOK_MEM = Path("/Users/dhyana/DHARMIC_GODEL_CLAW/moltbook_swarm/memory/latest_observations.json")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def get_moltbook_stats():
    """Get current Moltbook swarm stats"""
    try:
        if MOLTBOOK_STATE.exists():
            with open(MOLTBOOK_STATE) as f:
                state = json.load(f)
            return {
                "cycles": state.get("cycles_completed", 0),
                "observations": state.get("observations_total", 0),
                "engagements": state.get("engagements_successful", 0),
                "running": state.get("status") == "running"
            }
    except Exception as e:
        log(f"Error reading moltbook state: {e}")
    return None

def get_latest_observations():
    """Get latest Moltbook observations"""
    try:
        if MOLTBOOK_MEM.exists():
            with open(MOLTBOOK_MEM) as f:
                data = json.load(f)
            obs = data.get("observations", [])
            if obs:
                # Get top 3 by quality
                top = sorted(obs, key=lambda x: x.get("quality", 0), reverse=True)[:3]
                return top
    except Exception as e:
        log(f"Error reading observations: {e}")
    return []

def update_training_file():
    """Update ORCHESTRATOR_TRAINING.md with current status"""
    if not TRAINING_FILE.exists():
        log("Training file not found!")
        return False
    
    # Get stats
    moltbook = get_moltbook_stats()
    observations = get_latest_observations()
    
    # Build update entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n### [{timestamp}] 3-HOUR ORCHESTRATOR UPDATE\n\n"
    
    # Moltbook status
    if moltbook:
        entry += "**Moltbook Swarm:**\n"
        entry += f"- Status: {'✅ Running' if moltbook['running'] else '❌ Stopped'}\n"
        entry += f"- Cycles: {moltbook['cycles']}\n"
        entry += f"- Observations: {moltbook['observations']}\n"
        entry += f"- Engagements: {moltbook['engagements']}\n\n"
    
    # Top observations
    if observations:
        entry += "**Top Observations:**\n"
        for obs in observations:
            agent = obs.get('agent_name', 'Unknown')
            quality = obs.get('quality', 0)
            title = obs.get('thread_title', 'Untitled')[:50]
            entry += f"- {agent} (Q{quality}): {title}...\n"
        entry += "\n"
    
    # Active threads status
    entry += "**Active Threads:**\n"
    entry += "- R_V Toolkit: 80% (awaiting your go)\n"
    entry += "- Moltbook Swarm: Active ✅\n"
    entry += "- AIKAGRYA Report: 60% (blocked on R_V)\n"
    entry += "- WARP_REGENT: Background (no alerts)\n\n"
    
    entry += "**Next 3 Hours:**\n"
    entry += "- Continue Moltbook observation/engagement\n"
    entry += "- Remind about R_V toolkit (if not done)\n"
    entry += "- Execute any user-directed tasks\n\n"
    
    # Append to file
    with open(TRAINING_FILE, "a") as f:
        f.write(entry)
    
    log(f"Updated training file with {len(observations)} observations")
    return True

def main():
    log("=" * 60)
    log("🎼 ORCHESTRATOR UPDATE CYCLE")
    log("=" * 60)
    
    success = update_training_file()
    
    if success:
        log("✅ Training file updated")
    else:
        log("❌ Update failed")
    
    log("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ ERROR: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)
