#!/usr/bin/env python3
"""
TAKT MASTER — The Heartbeat of OpenClaw TPS

This is the master takt pulse that coordinates all work cells.
It emits a CASCADE_START signal every 60 seconds that triggers
downstream processes in a staggered, collision-free sequence.

Philosophy: Like the andon cord in a Toyota factory, this is the
central timing mechanism that keeps all cells synchronized.

Author: Integration Architect
Version: 1.0
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import fcntl

# Configuration
TAKT_FILE = Path("/Users/dhyana/clawd/coordination/state/takt_state.json")
CASCADE_FILE = Path("/Users/dhyana/clawd/coordination/state/cascade_signal.json")
LOG_FILE = Path("/Users/dhyana/clawd/logs/takt.log")
STATE_DIR = Path("/Users/dhyana/clawd/coordination/state")

# Ensure state directory exists
STATE_DIR.mkdir(parents=True, exist_ok=True)


class TaktMaster:
    """
    The master timing controller for the OpenClaw factory floor.
    
    Emits a takt pulse every 60 seconds that downstream cells
    use to synchronize their operations.
    """
    
    TAKT_INTERVAL = 60  # seconds
    
    # 4 Shakti mode time blocks (WITA timezone)
    SHAKTI_SCHEDULE = {
        (6, 9): "Maheshwari",      # Morning - Vision/Planning
        (9, 12): "Mahakali",       # Morning - Cutting/Focus
        (12, 14): "transition",    # Lunch break
        (14, 17): "Mahalakshmi",   # Afternoon - Harmony/Integration
        (17, 19): "transition",    # Evening transition
        (19, 22): "Mahasaraswati", # Evening - Completion
    }
    
    def __init__(self):
        self.takt_count = 0
        self.start_time = datetime.now(timezone.utc)
        self.current_shakti = self._get_current_shakti()
        
    def _get_current_shakti(self) -> str:
        """Determine current Shakti mode based on WITA time."""
        # WITA = UTC+8
        wita_hour = (datetime.now(timezone.utc).hour + 8) % 24
        
        for (start, end), mode in self.SHAKTI_SCHEDULE.items():
            if start <= wita_hour < end:
                return mode
        return "rest"  # Outside working hours
    
    def _load_state(self) -> Dict[str, Any]:
        """Load the current takt state."""
        if TAKT_FILE.exists():
            try:
                with open(TAKT_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "takt_count": 0,
            "last_beat": None,
            "cascade_active": False,
            "cell_status": {}
        }
    
    def _save_state(self, state: Dict[str, Any]):
        """Save the current takt state atomically."""
        temp_file = TAKT_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        temp_file.rename(TAKT_FILE)
    
    def _emit_cascade(self, state: Dict[str, Any]):
        """
        Emit the cascade signal that triggers downstream processes.
        
        This is the core coordination mechanism. All cells watch
        for this signal to synchronize their work.
        """
        now = datetime.now(timezone.utc)
        
        cascade = {
            "takt_id": state["takt_count"],
            "timestamp": now.isoformat(),
            "shakti_mode": self.current_shakti,
            "cascade_start": now.timestamp(),
            "expected_responses": {
                "mmk": 30,      # 30 second SLA
                "trishula": 20,  # 20 second SLA
                "openclaw": 15,  # 15 second SLA
            },
            "cell_states": state.get("cell_status", {})
        }
        
        # Atomic write
        temp_file = CASCADE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(cascade, f, indent=2, default=str)
        temp_file.rename(CASCADE_FILE)
        
        return cascade
    
    def _check_cell_health(self) -> Dict[str, Any]:
        """
        Quick health check of all work cells.
        
        Returns status for each cell that downstream processes
        can use to coordinate.
        """
        cells = {
            "research": {"wip": 0, "limit": 3, "last_output": None},
            "build": {"wip": 0, "limit": 5, "last_output": None},
            "ship": {"wip": 0, "limit": 2, "last_output": None},
            "monitor": {"wip": 0, "limit": 0, "last_output": None},
        }
        
        # Check cell status files
        for cell in cells:
            cell_file = STATE_DIR / f"{cell}_status.json"
            if cell_file.exists():
                try:
                    with open(cell_file, 'r') as f:
                        data = json.load(f)
                        cells[cell].update(data)
                except (json.JSONDecodeError, IOError):
                    pass
        
        return cells
    
    def _log_beat(self, cascade: Dict[str, Any]):
        """Log the takt beat for monitoring."""
        now = datetime.now(timezone.utc)
        log_entry = f"[{now.isoformat()}] TAKT #{cascade['takt_id']} | {cascade['shakti_mode']} | cascade emitted\n"
        
        with open(LOG_FILE, 'a') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(log_entry)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def beat(self) -> Dict[str, Any]:
        """
        Execute a single takt beat.
        
        This is called every minute by cron. It:
        1. Loads current state
        2. Checks cell health
        3. Emits cascade signal
        4. Updates state
        5. Logs the beat
        """
        # Load current state
        state = self._load_state()
        
        # Update Shakti mode
        self.current_shakti = self._get_current_shakti()
        
        # Increment takt count
        state["takt_count"] = state.get("takt_count", 0) + 1
        state["last_beat"] = datetime.now(timezone.utc).isoformat()
        
        # Check cell health
        state["cell_status"] = self._check_cell_health()
        
        # Emit cascade signal
        cascade = self._emit_cascade(state)
        state["cascade_active"] = True
        
        # Save state
        self._save_state(state)
        
        # Log
        self._log_beat(cascade)
        
        return cascade
    
    def run_daemon(self):
        """
        Run as a continuous daemon (alternative to cron).
        
        Not used by default - cron handles the 1-minute trigger.
        But available for future event-driven architecture.
        """
        while True:
            self.beat()
            time.sleep(self.TAKT_INTERVAL)


def main():
    """Main entry point - called by cron every minute."""
    try:
        master = TaktMaster()
        cascade = master.beat()
        
        # Output for cron logging
        print(f"TAKT #{cascade['takt_id']} emitted at {cascade['timestamp']}")
        print(f"Shakti mode: {cascade['shakti_mode']}")
        print(f"Cell states: {len(cascade['cell_states'])} cells active")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Takt master failed: {e}", file=sys.stderr)
        
        # Attempt to alert
        try:
            alert_file = STATE_DIR / "takt_failure.alert"
            with open(alert_file, 'w') as f:
                f.write(f"Takt failure at {datetime.now(timezone.utc).isoformat()}: {e}\n")
        except:
            pass
            
        return 1


if __name__ == "__main__":
    sys.exit(main())
